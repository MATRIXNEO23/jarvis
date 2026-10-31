"""One-time interactive Telegram account setup; NEVER sends a message.

Requires optional free Telethon. Stores API hash + user StringSession sealed
using Windows DPAPI, and stores only the selected private contact's numeric
peer ID + display name in settings.json. Automatic answering stays OFF.
"""
from __future__ import annotations

import asyncio
import re
import os
import sys

from settings import load_settings,save_settings
from telegram_security import save_credentials
from telegram_secret_dialog import prompt_masked_secret


def valid_api_hash(value: str) -> bool:
    """Telegram api_hash is an exact 32-character hexadecimal string."""
    return isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{32}", value) is not None


async def configure():
    if os.name!="nt":
        raise RuntimeError("Configurazione Telegram supportata sul Pavilion Windows.")
    try:
        from telethon import TelegramClient
        from telethon.errors import SessionPasswordNeededError
        from telethon.sessions import StringSession
    except ImportError as exc:
        raise RuntimeError("Esegui installa_telegram.bat prima della configurazione.") from exc
    print("Configurazione sicura JARVIS / Telegram")
    print("Occorrono API ID e API hash gratuiti del proprio account da my.telegram.org.")
    print("Non condividere codice Telegram, API hash o sessione.")
    api_id=int(input("API ID: ").strip())
    print("Si aprirà una finestra protetta per l'API hash.")
    print("Incolla con Ctrl+V o con il pulsante Incolla; vedrai degli asterischi.")
    api_hash=prompt_masked_secret(
        "JARVIS / Telegram - API hash",
        "Incolla l'API hash di 32 caratteri ottenuto da my.telegram.org. "
        "Il contenuto è nascosto. Usa Ctrl+V oppure il pulsante Incolla.",
        min_length=32,max_length=80)
    if api_hash is None:
        print("Configurazione annullata. Telegram resta disattivato.")
        return
    api_hash=api_hash.strip()
    if not valid_api_hash(api_hash):
        raise ValueError("API hash non valido: devono esserci 32 caratteri esadecimali.")
    phone=input("Numero Telegram con prefisso internazionale: ").strip()
    if api_id<=0 or not phone.startswith("+"):
        raise ValueError("Dati Telegram non validi.")
    client=TelegramClient(StringSession(),api_id,api_hash)
    await client.connect()
    try:
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            code=prompt_masked_secret(
                "JARVIS / Telegram - Codice di accesso",
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
                    "JARVIS / Telegram - Verifica in due passaggi",
                    "Inserisci la password in due passaggi di Telegram. "
                    "Usa Ctrl+V o Incolla se la conservi in un gestore password.",
                    min_length=1,max_length=256)
                if password is None:
                    print("Accesso annullato. Nessuna sessione salvata.")
                    return
                await client.sign_in(password=password)
        if not await client.is_user_authorized():
            raise RuntimeError("Accesso Telegram non autorizzato.")
        dialogs=await client.get_dialogs(limit=200)
        contacts=[
            d for d in dialogs
            if d.is_user and not getattr(d.entity,"bot",False)
            and not getattr(d.entity,"is_self",False)
        ]
        if not contacts:
            raise RuntimeError(
                "Non risultano chat private. Apri prima una conversazione Telegram.")
        print("\nSeleziona UN contatto, senza gruppi o bot:")
        for i,d in enumerate(contacts,1):
            print(f"{i:3d}. {str(d.name)[:54]}  [ID: {d.entity.id}]")
        selection=input("Numero del contatto autorizzato (INVIO per annullare): ").strip()
        if not selection:
            print("Nessun contatto scelto. Configurazione annullata.")
            return
        n=int(selection)
        if not 1<=n<=len(contacts):
            raise ValueError("Numero di contatto non valido.")
        contact=contacts[n-1]
        confirm=input(
            "Autorizzare SOLO "+str(contact.name)[:55]
            +" (ID "+str(contact.entity.id)+")? Scrivi SI: ").strip()
        if confirm!="SI":
            print("Nessuna modifica: autorizzazione annullata.")
            return
        # Commit credentials first; no message is sent in any phase.
        save_credentials(api_id,api_hash,client.session.save())
        settings=load_settings()
        settings["telegram_peer_id"]=int(contact.entity.id)
        settings["telegram_contact_name"]=str(contact.name)[:90]
        settings["telegram_enabled"]=False
        save_settings(settings)
        print("\nCollegamento salvato cifrato via DPAPI.")
        print("Le risposte automatiche sono SPENTE. Attivale dal menu ⚙ di Jarvis.")
        print("La tua amica deve sapere che l'assistente può rispondere al posto tuo.")
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
