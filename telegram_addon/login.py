"""Accesso a Telegram da dentro Lumi (al posto di configura_telegram.bat).

API ID, API hash e numero si scrivono nella finestra; il codice che Telegram
manda (e l'eventuale password in due passaggi) si inseriscono in un pop-up.
Credenziali e sessione vengono salvate cifrate con DPAPI di Windows, come prima
(telegram_security.save_credentials). Nessun messaggio viene inviato.
"""
from __future__ import annotations

import asyncio
import threading
import tkinter as tk
import webbrowser
from tkinter import ttk

from configura_telegram import clean_api_hash, normalize_phone, parse_api_id, valid_api_hash

API_PAGE = "https://my.telegram.org/apps"


class _Ask:
    """Pop-up mascherato chiesto dal thread di accesso e atteso fino a 5 minuti."""

    def __init__(self, window):
        self.window = window

    def __call__(self, title, text, secret=True):
        holder = {"value": None}
        ready = threading.Event()

        def show():
            dialog = tk.Toplevel(self.window)
            dialog.title(title)
            dialog.transient(self.window)
            dialog.grab_set()
            body = ttk.Frame(dialog, padding=12)
            body.pack(fill="both", expand=True)
            ttk.Label(body, text=text, wraplength=360).pack(anchor="w")
            value = tk.StringVar()
            entry = ttk.Entry(body, textvariable=value, show="*" if secret else "", width=32)
            entry.pack(fill="x", pady=8)
            entry.focus_set()

            def finish(result):
                holder["value"] = result
                dialog.destroy()
                ready.set()
            entry.bind("<Return>", lambda _e: finish(value.get()))
            row = ttk.Frame(body)
            row.pack(fill="x")
            ttk.Button(row, text="Conferma", command=lambda: finish(value.get())).pack(side="left")
            ttk.Button(row, text="Annulla", command=lambda: finish(None)).pack(side="right")
            dialog.protocol("WM_DELETE_WINDOW", lambda: finish(None))
        self.window.after(0, show)
        ready.wait(300)
        return holder["value"]


async def _login(api_id, api_hash, phone, ask, say):
    try:
        from telethon import TelegramClient
        from telethon.errors import SessionPasswordNeededError
        from telethon.sessions import StringSession
    except ImportError as exc:
        raise RuntimeError("Manca Telethon: premi «Installa» accanto a Telethon qui sopra.") from exc
    client = TelegramClient(StringSession(), api_id, api_hash)
    say("Collegamento a Telegram…")
    await client.connect()
    try:
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            say("Telegram ti ha mandato un codice (nell'app Telegram o via SMS).")
            code = ask("Codice Telegram", "Scrivi il codice ricevuto da Telegram.", secret=False)
            if not code:
                return "Accesso annullato: nessuna sessione salvata."
            try:
                await client.sign_in(phone, code.strip())
            except SessionPasswordNeededError:
                password = ask("Verifica in due passaggi",
                               "Il tuo account ha la verifica in due passaggi: scrivi la password.")
                if not password:
                    return "Accesso annullato: nessuna sessione salvata."
                await client.sign_in(password=password)
        if not await client.is_user_authorized():
            raise RuntimeError("Accesso Telegram non autorizzato.")
        from telegram_security import load_credentials, save_credentials
        save_credentials(api_id, api_hash, client.session.save())
        load_credentials()                      # rilettura: Lumi potrà usarle
        return "Accesso salvato (cifrato con Windows). Contatti e impostazioni restano come prima."
    finally:
        await client.disconnect()


class TelegramLoginWindow:
    def __init__(self, parent, on_done=None):
        self.on_done = on_done or (lambda: None)
        self.window = tk.Toplevel(parent)
        self.window.title("LUMI // Account Telegram")
        self.window.geometry("520x380")
        frame = ttk.Frame(self.window, padding=12)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, wraplength=490, text=(
            "API ID e API hash sono gratuiti: si creano su my.telegram.org con il tuo numero "
            "(F1 > Chiavi API spiega i passaggi). Non condividerli con nessuno.")).pack(anchor="w")
        ttk.Button(frame, text="Apri my.telegram.org", command=lambda: webbrowser.open(API_PAGE)
                   ).pack(anchor="w", pady=(4, 8))
        grid = ttk.Frame(frame)
        grid.pack(fill="x")
        self.api_id = tk.StringVar()
        self.api_hash = tk.StringVar()
        self.phone = tk.StringVar()
        for row, (label, var, secret) in enumerate((
                ("API ID (numero)", self.api_id, False),
                ("API hash (32 caratteri)", self.api_hash, True),
                ("Numero Telegram", self.phone, False))):
            ttk.Label(grid, text=label, width=24).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Entry(grid, textvariable=var, width=34, show="*" if secret else "").grid(
                row=row, column=1, sticky="w")
        ttk.Label(frame, text="Esempio numero: +39 333 1234567").pack(anchor="w", pady=(2, 8))
        row = ttk.Frame(frame)
        row.pack(fill="x")
        self.button = ttk.Button(row, text="Collegati", command=self.start)
        self.button.pack(side="left")
        ttk.Button(row, text="Chiudi", command=self.window.destroy).pack(side="right")
        self.status = tk.StringVar()
        ttk.Label(frame, textvariable=self.status, wraplength=490).pack(anchor="w", pady=(10, 0))

    def say(self, text):
        self.window.after(0, lambda: self.status.set(text))

    def start(self):
        api_id = parse_api_id(self.api_id.get())
        api_hash = clean_api_hash(self.api_hash.get())
        phone = normalize_phone(self.phone.get())
        if api_id is None:
            self.status.set("API ID non valido: copia il numero «App api_id» da my.telegram.org.")
            return
        if not valid_api_hash(api_hash):
            self.status.set(f"API hash non valido ({len(api_hash)} caratteri): servono 32 "
                            "caratteri tra 0-9 e a-f, la riga «App api_hash».")
            return
        if phone is None:
            self.status.set("Numero non valido: scrivilo con il prefisso, es. +39 333 1234567.")
            return
        self.button.state(["disabled"])
        ask = _Ask(self.window)

        def worker():
            try:
                message = asyncio.run(_login(api_id, api_hash, phone, ask, self.say))
                ok = message.startswith("Accesso salvato")
            except Exception as exc:                      # errore visibile, mai crash
                message, ok = "Accesso non riuscito: " + str(exc)[:200], False

            def finish():
                try:
                    self.status.set(message)
                    self.button.state(["!disabled"])
                except tk.TclError:
                    pass
                if ok:
                    self.on_done()
            self.window.after(0, finish)
        threading.Thread(target=worker, daemon=True, name="lumi-telegram-login").start()
