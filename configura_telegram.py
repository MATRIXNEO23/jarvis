"""One-time interactive Telegram account setup; NEVER sends a message.

Requires optional free Telethon. Stores API hash + user StringSession sealed
using Windows DPAPI, and stores only the selected private contact's numeric
peer ID + display name in settings.json. Automatic answering stays OFF.
"""
from __future__ import annotations

import asyncio
import getpass
import os
import sys

from settings import load_settings,save_settings
from telegram_security import save_credentials


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
    api_hash=getpass.getpass("API hash (non viene mostrato): ").strip()
    phone=input("Numero Telegram con prefisso internazionale: ").strip()
    if api_id<=0 or len(api_hash)<16 or not phone.startswith("+"):
        raise ValueError("Dati Telegram non validi.")
    client=TelegramClient(StringSession(),api_id,api_hash)
    await client.connect()
    try:
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            code=input("Codice ricevuto direttamente in Telegram: ").strip()
            try:
                await client.sign_in(phone,code)
            except SessionPasswordNeededError:
                password=getpass.getpass("Password Telegram in due passaggi: ")
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
