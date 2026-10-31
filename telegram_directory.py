"""User-controlled Telegram directory and direct OGG/Opus outbound notes.

Uses the already encrypted StringSession. The owner may send without an
external GPT reply and without enabling automatic answering. No test messages.
Do not log or export account credentials, full contact lists, or message text.
"""
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from telegram_security import load_credentials
from telegram_voice import make_telegram_voice


class TelegramDirectoryError(RuntimeError):
    pass


def _safe_user(entity) -> bool:
    return (type(getattr(entity, "id", None)) is int
            and entity.id > 0
            and not getattr(entity, "bot", False)
            and not getattr(entity, "is_self", False)
            and not getattr(entity, "deleted", False))


def _display_name(user, fallback="") -> str:
    value = " ".join(str(v).strip() for v in (
        getattr(user, "first_name", None),
        getattr(user, "last_name", None)) if v)
    return (value or str(fallback or getattr(user, "username", "") or "")).strip()[:90]


async def verified_contact_entities(client) -> dict[int, tuple[str, object]]:
    """Resolve actual user entities by numeric ID: Telegram contacts + private chats."""
    found = {}
    try:
        from telethon.tl.functions.contacts import GetContactsRequest
        result = await client(GetContactsRequest(hash=0))
        for user in getattr(result, "users", ()):
            if _safe_user(user):
                name = _display_name(user)
                if name:
                    found[user.id] = (name, user)
    except (ImportError, OSError, RuntimeError):
        # Private dialogs are still usable when contacts sync fails.
        pass
    dialogs = await client.get_dialogs(limit=200)
    for dialog in dialogs:
        entity = getattr(dialog, "entity", None)
        if getattr(dialog, "is_user", False) and _safe_user(entity):
            name = _display_name(entity, getattr(dialog, "name", ""))
            if name:
                found[entity.id] = (name, entity)
    return found


async def _authenticated_client():
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
    except ImportError as exc:
        raise TelegramDirectoryError(
            "Telethon non installato: esegui installa_telegram.bat.") from exc
    creds = load_credentials()
    client = TelegramClient(StringSession(creds["session"]),
                            creds["api_id"], creds["api_hash"],
                            receive_updates=False, connection_retries=2)
    await client.connect()
    if not await client.is_user_authorized():
        await client.disconnect()
        raise TelegramDirectoryError("Sessione Telegram scaduta: riconfigura l'account.")
    return client


async def _list_telegram_contacts():
    client = await _authenticated_client()
    try:
        entities = await verified_contact_entities(client)
        return [{"id": peer_id, "name": entry[0]} for peer_id, entry
                in sorted(entities.items(), key=lambda p: (
                    p[1][0].casefold(), p[0]))][:250]
    finally:
        await client.disconnect()


def list_telegram_contacts() -> list[dict]:
    """Run only in a non-GUI thread; does not send messages."""
    return asyncio.run(_list_telegram_contacts())


async def _send_telegram_voice(peer_id: int, text: str, voice_name: str):
    if type(peer_id) is not int or peer_id <= 0:
        raise TelegramDirectoryError("Destinatario non valido.")
    if not isinstance(text, str) or not 1 <= len(text.strip()) <= 480:
        raise TelegramDirectoryError("Messaggio vuoto o troppo lungo (480 caratteri).")
    client = await _authenticated_client()
    try:
        peers = await verified_contact_entities(client)
        if peer_id not in peers:
            raise TelegramDirectoryError(
                "Destinatario non trovato nella rubrica o nelle chat Telegram.")
        # Generate only after the real Telegram account has resolved the ID.
        with tempfile.TemporaryDirectory(prefix="jarvis-tg-owner-") as folder:
            audio = await asyncio.to_thread(
                make_telegram_voice, text.strip(), Path(folder), voice_name)
            try:
                result = await client.send_file(peers[peer_id][1], str(audio),
                                                voice_note=True)
            except Exception as exc:
                # A timeout may happen *after* Telegram accepts the audio.
                # Never retry automatically, or duplicate voice messages.
                raise TelegramDirectoryError(
                    "Invio Telegram incerto: controlla la chat prima di riprovare."
                ) from exc
            if not result or type(getattr(result, "id", None)) is not int:
                raise TelegramDirectoryError(
                    "Telegram non ha restituito la ricevuta: esito incerto.")
            return result.id
    finally:
        await client.disconnect()


def send_telegram_voice(peer_id: int, text: str, voice_name: str = "") -> int:
    """One explicit owner action, not a text fallback, never sent by GPT."""
    return asyncio.run(_send_telegram_voice(peer_id, text, voice_name))
