"""One-time account login; contacts selected later inside Lumi.

Requires optional free Telethon. Stores API hash + user StringSession sealed
using Windows DPAPI, and stores only the selected private contact's numeric
peer ID + display name in settings.json. Automatic answering stays OFF.
"""
from __future__ import annotations

import asyncio
import re
import os
import sys

from telegram_security import save_credentials
from telegram_secret_dialog import prompt_masked_secret


def valid_api_hash(value: str) -> bool:
    """Telegram api_hash is an exact 32-character hexadecimal string."""
    return isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{32}", value) is not None


def clean_api_hash(value) -> str:
    """Toglie spazi, a capo e virgolette copiati per sbaglio insieme all'hash."""
    if not isinstance(value, str):
        return ""
    return re.sub(r"[\s'\"`]+", "", value)


def parse_api_id(value) -> int | None:
    digits = re.sub(r"\s+", "", str(value or ""))
    return int(digits) if digits.isdigit() and 0 < int(digits) < 2**31 else None


def normalize_phone(value) -> str | None:
    """+39 333 1234567, 0039..., 3331234567 (Italia) -> +393331234567."""
    raw = re.sub(r"[\s\-./()]+", "", str(value or ""))
    if raw.startswith("00"):
        raw = "+" + raw[2:]
    if not raw.startswith("+") and raw.isdigit() and len(raw) == 10 and raw.startswith("3"):
        raw = "+39" + raw
    return raw if re.fullmatch(r"\+\d{8,15}", raw) else None


def _ask(prompt, parse, error, attempts=3):
    for _ in range(attempts):
        value = parse(input(prompt))
        if value is not None:
            return value
        print(error)
    raise ValueError(error)


async def configure():
    if os.name!="nt":
        raise RuntimeError("Configurazione Telegram supportata sul Pavilion Windows.")
    try:
        from telethon import TelegramClient
        from telethon.errors import SessionPasswordNeededError
        from telethon.sessions import StringSession
    except ImportError as exc:
        raise RuntimeError("Esegui installa_telegram.bat prima della configurazione.") from exc
    print("Configurazione sicura LUMI / Telegram")
    print("Occorrono API ID e API hash gratuiti del proprio account da my.telegram.org.")
    print("Non condividere codice Telegram, API hash o sessione.")
    api_id=_ask("API ID (solo numeri): ",parse_api_id,
                "API ID non valido: copia il numero «App api_id» da my.telegram.org.")
    print("Si aprirà una finestra protetta per l'API hash.")
    print("Incolla con Ctrl+V o con il pulsante Incolla; vedrai degli asterischi.")
    api_hash=None
    for _ in range(3):
        typed=prompt_masked_secret(
            "LUMI / Telegram - API hash",
            "Incolla l'API hash di 32 caratteri ottenuto da my.telegram.org. "
            "Il contenuto è nascosto. Usa Ctrl+V oppure il pulsante Incolla.",
            min_length=32,max_length=80)
        if typed is None:
            print("Configurazione annullata. Telegram resta come prima.")
            return
        candidate=clean_api_hash(typed)
        if valid_api_hash(candidate):
            api_hash=candidate
            break
        print("API hash non valido ("+str(len(candidate))+" caratteri): servono "
              "32 caratteri tra 0-9 e a-f, la riga «App api_hash» di my.telegram.org. Riprova.")
    if api_hash is None:
        raise ValueError("API hash non valido dopo 3 tentativi.")
    phone=_ask("Numero Telegram (es. +39 333 1234567): ",normalize_phone,
               "Numero non valido: scrivi il numero con il prefisso, per esempio +39 333 1234567.")
    client=TelegramClient(StringSession(),api_id,api_hash)
    await client.connect()
    try:
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            code=prompt_masked_secret(
                "LUMI / Telegram - Codice di accesso",
                "Inserisci il codice ricevuto da Telegram. "
                "Puoi incollarlo con Ctrl+V oppure con Incolla.",
                min_length=4,max_length=32)
            if code is None:
                print("Accesso annullato. Nessuna sessione salvata.")
                return
            try:
                await client.sign_in(phone,code.strip())
            except SessionPasswordNeededError:
                password=prompt_masked_secret(
                    "LUMI / Telegram - Verifica in due passaggi",
                    "Inserisci la password in due passaggi di Telegram. "
                    "Usa Ctrl+V o Incolla se la conservi in un gestore password.",
                    min_length=1,max_length=256)
                if password is None:
                    print("Accesso annullato. Nessuna sessione salvata.")
                    return
                await client.sign_in(password=password)
        if not await client.is_user_authorized():
            raise RuntimeError("Accesso Telegram non autorizzato.")
        # Contatti e stato NON vengono cancellati: prima ogni nuova
        # configurazione azzerava i contatti spuntati e spegneva Telegram, e i
        # messaggi non arrivavano più. È sicuro mantenerli: all'avvio Lumi
        # accetta solo ID presenti nelle chat/rubrica di QUESTO account.
        save_credentials(api_id,api_hash,client.session.save())
        from telegram_security import credential_path, load_credentials
        load_credentials()          # rilettura: conferma che Lumi potrà usarle
        print("\nAccesso Telegram salvato con cifratura Windows DPAPI.")
        print("File: "+str(credential_path()))
        print("In Lumi premi «Rileggi configurazione Telegram».")
        print("Contatti spuntati e impostazioni Telegram restano come prima;")
        print("se è un account diverso, ricarica e spunta i contatti.")
        print("Nessun messaggio inviato.")
    finally:
        await client.disconnect()


def main():
    try:
        asyncio.run(configure())
    except (OSError,RuntimeError,ValueError,KeyboardInterrupt) as exc:
        print("Configurazione non completata: "+str(exc)[:200])
        sys.exit(1)


if __name__=="__main__":
    main()
