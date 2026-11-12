"""Parte di interfaccia Telegram di Lumi, spostata da jarvis.py (piano di divisione, passo 2a).

Stesso codice di prima: le variabili di main() che usa arrivano da `d` (lumi_contesto.Vivo),
che restituisce sempre il valore attuale. Restano in jarvis.py, per ora, le funzioni che
cambiano lo stato condiviso (nonlocal) e quelle provate dai test direttamente su jarvis.py.
"""
from __future__ import annotations

import os
import sqlite3
import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox, simpledialog, ttk

from addon_manager import AddonError
from settings import TELEGRAM_PROFILE_LIMIT, save_settings
from telegram_directory import list_telegram_contacts
from telegram_security import credentials_present
from telegram_ui import edit_telegram_context, show_telegram_manual_send
from workspace_memory import WorkspaceError

NOMI = ('telegram_activity_window', 'queue_telegram_note', 'leave_telegram_note_dialog', 'selected_telegram_contacts', 'load_telegram_contacts_for_ui', 'open_telegram_history', 'clear_telegram_history', 'edit_telegram_contact_profile', 'open_telegram_manual_send', 'telegram_addon_enabled', 'telegram_open_setup', 'build_telegram_section')


def installa(d):
    """Crea le funzioni legate a questa esecuzione di Lumi; restituisce {nome: funzione}."""
    def telegram_activity_window(peer_id:int=0) -> None:
        allowed={c["id"]:c["name"] for c in selected_telegram_contacts()}
        if d.workspace is None or peer_id not in allowed:
            return
        win=tk.Toplevel(d.root)
        win.title("LUMI // Telegram — "+allowed[peer_id])
        win.geometry("640x420")
        log=tk.Text(win,wrap="word",bg="#031522",fg="#d7f6ff",
                    padx=12,pady=8)
        log.pack(fill="both",expand=True)
        try:
            records=d.workspace.telegram_activity(peer_id,limit=50)
            for item in reversed(records):
                direction=("RICEVUTO" if item["direction"]=="incoming"
                           else "LUMI HA RISPOSTO")
                log.insert("end",item["when"]+"  "+direction
                           +" ["+item["kind"]+"]\n"
                           +item["text"]+"\n\n")
            displayed_ids=[item["message_id"] for item in records
                           if item["direction"]=="incoming"]
            d.workspace.mark_telegram_read(peer_id, displayed_ids)
            d.refresh_orbit_nodes(reschedule=False)
        except (OSError,sqlite3.Error,WorkspaceError) as exc:
            log.insert("end","Archivio Telegram non leggibile: "+str(exc)[:100])
        log.configure(state="disabled")
    def queue_telegram_note(message:str) -> bool:
        chosen=selected_telegram_contacts()
        if len(chosen)!=1 or d.workspace is None:
            d.write_line("TELEGRAM > Il vecchio promemoria usa un solo destinatario. "
                       "Per scegliere tra più contatti usa 'Invia messaggio vocale'.")
            return False
        peer_id=chosen[0]["id"]
        try:
            d.workspace.note_for_contact(peer_id,message)
        except (OSError,sqlite3.Error,WorkspaceError) as exc:
            d.write_line("LUMI > Non posso salvare il messaggio: "+str(exc)[:100])
            return False
        d.write_line("LUMI > Messaggio memorizzato per "
                   +chosen[0]["name"]
                   +". Lo riferirò al prossimo contatto, se Telegram è attivo.")
        return True
    def leave_telegram_note_dialog() -> None:
        if not d.settings.get("telegram_peer_id"):
            d.telegram_status.set("Configura prima il contatto autorizzato.")
            return
        message=simpledialog.askstring(
            "LUMI / Telegram",
            "Che cosa devo riferire al contatto autorizzato?",
            parent=d.root)
        if message:
            queue_telegram_note(message)
    def selected_telegram_contacts() -> list[dict]:
        return [c for c in d.settings.get("telegram_contacts", [])
                if c.get("enabled") is True]
    def load_telegram_contacts_for_ui() -> None:
        """Read real Telegram private users on a worker, never on Tk."""
        if not credentials_present():
            d.output_queue.put(("telegram_contacts_error",
                              "Prima configura l'account Telegram."))
            return
        def worker() -> None:
            try:
                rows=list_telegram_contacts()
                d.output_queue.put(("telegram_contacts_loaded",rows))
            except Exception as exc:
                d.output_queue.put(("telegram_contacts_error",type(exc).__name__))
        threading.Thread(target=worker,daemon=True,
                         name="jarvis-telegram-contact-list").start()
    def open_telegram_history(peer_id:int) -> None:
        allowed={c["id"]:c["name"] for c in selected_telegram_contacts()}
        if d.workspace is None or peer_id not in allowed:
            messagebox.showwarning("Telegram","Contatto non autorizzato.",
                                   parent=d.root)
            return
        try:
            path=d.workspace.telegram_export_history(peer_id,allowed[peer_id])
            if os.name=="nt":
                os.startfile(str(path))
            else:
                webbrowser.open(path.as_uri())
        except (OSError,sqlite3.Error,WorkspaceError) as exc:
            messagebox.showerror("Telegram",
                "Non posso aprire la conversazione: "+str(exc)[:150],parent=d.root)
    def clear_telegram_history(peer_id:int) -> None:
        allowed={c["id"]:c["name"] for c in selected_telegram_contacts()}
        if d.workspace is None or peer_id not in allowed:
            messagebox.showwarning("Telegram","Contatto non autorizzato.",
                                   parent=d.root)
            return
        if not messagebox.askyesno(
                "Telegram — cancella cronologia",
                "Cancellare i messaggi Telegram salvati di "+
                allowed[peer_id]+"?\n\n"
                "Non verranno cancellati contatto, autorizzazioni, "
                "messaggi in attesa né lo stato della presentazione. "
                "Le risposte automatiche saranno disattivate prima della pulizia, "
                "se attive. Un invio già partito potrebbe ancora arrivare. "
                "I messaggi eliminati non potranno essere recuperati "
                "dall'archivio attivo.",
                parent=d.root,default="no"):
            return
        # Never delete a peer's active events while the listener is still
        # handling that contact. User explicitly approved disabling Telegram.
        if d.telegram_bridge and d.telegram_bridge.is_enabled():
            d.telegram_auto.set(False)
            d.toggle_telegram_automatic()
        try:
            d.workspace.telegram_clear_history(peer_id)
        except (OSError,sqlite3.Error,WorkspaceError) as exc:
            messagebox.showerror("Telegram",
                "Non posso cancellare la cronologia: "+str(exc)[:150],
                parent=d.root)
            return
        messagebox.showinfo("Telegram",
                            "Cronologia locale cancellata per "+
                            allowed[peer_id]+".",parent=d.root)
    def edit_telegram_contact_profile(parent, peer_id: int) -> None:
        contact = next((row for row in selected_telegram_contacts()
                        if row["id"] == peer_id), None)
        if contact is None:
            messagebox.showwarning("Telegram", "Contatto non autorizzato.", parent=parent)
            return
        key = str(peer_id)
        profiles = d.settings.get("telegram_contact_profiles", {}).copy()
        profile = edit_telegram_context(
            parent, contact["name"], profiles.get(key, ""), TELEGRAM_PROFILE_LIMIT)
        if profile is None:
            return
        profile = profile.strip()
        if len(profile) > TELEGRAM_PROFILE_LIMIT:
            messagebox.showwarning("Telegram", "Contesto troppo lungo. Nessuna modifica salvata.",
                                   parent=parent)
            return
        if profile:
            profiles[key] = profile
        else:
            profiles.pop(key, None)
        try:
            save_settings({**d.settings, "telegram_contact_profiles": profiles})
        except (OSError, ValueError):
            messagebox.showerror("Telegram", "Impossibile salvare il contesto.", parent=parent)
            return
        d.settings["telegram_contact_profiles"] = profiles
    def open_telegram_manual_send() -> None:
        show_telegram_manual_send(d.root,selected_telegram_contacts(),
                                  d.send_owner_telegram_voice)
    def telegram_addon_enabled() -> bool:
        if d.addon_manager is None:
            return True                 # archivio add-on guasto: comportamento di prima
        try:
            return any(item["id"] == "telegram" and item["enabled"]
                       for item in d.addon_manager.list_installed())
        except (AddonError, OSError, ValueError):
            return True
    def telegram_open_setup():
        # Accesso dentro Lumi (niente configura_telegram.bat): campi per
        # API ID, hash e numero; il codice di Telegram arriva in un pop-up.
        try:
            from telegram_addon.login import TelegramLoginWindow
            TelegramLoginWindow(d.root, on_done=d.telegram_reconfigure)
            d.telegram_status.set("Inserisci API ID, API hash e numero, poi «Collegati».")
        except (ImportError, OSError, tk.TclError) as exc:
            d.telegram_status.set("Configurazione non avviata: "+str(exc)[:100])
    def build_telegram_section(parent):
        telegram_panel=ttk.LabelFrame(
            parent,text="Telegram — contatti selezionati e messaggi vocali",padding=8)
        telegram_panel.pack(fill="x",pady=(3,10))
        telegram_toggle=ttk.Checkbutton(
            telegram_panel,text="Risposte vocali automatiche ON / OFF",
            variable=d.telegram_auto)
        telegram_toggle.pack(anchor="w")
        telegram_consent_row=ttk.Frame(telegram_panel)
        telegram_consent_row.pack(fill="x",pady=(4,0))
        ttk.Label(telegram_consent_row,text="Consenso GPT online").pack(side="left",padx=(0,8))
        ttk.Radiobutton(telegram_consent_row,text="Chiedi ogni volta",
                        variable=d.telegram_gpt_session_choice,value=False,
                        command=lambda: d.set_telegram_gpt_session(False)).pack(side="left")
        ttk.Radiobutton(telegram_consent_row,text="Consenti per questa sessione",
                        variable=d.telegram_gpt_session_choice,value=True,
                        command=lambda: d.set_telegram_gpt_session(True)).pack(side="left",padx=(8,0))
        ttk.Label(telegram_panel,wraplength=690,
                  text="Il consenso per questa sessione permette di inviare a GPT online "
                       "i messaggi e il contesto recente delle chat Telegram dei contatti "
                       "spuntati. Si azzera quando spegni o disconnetti GPT o chiudi Lumi."
                  ).pack(anchor="w",pady=(2,0))
        telegram_row=ttk.Frame(telegram_panel)
        telegram_row.pack(fill="x",pady=(4,3))
        telegram_configure_button=ttk.Button(
            telegram_row,text="Configura account (ID, hash, numero)...")
        telegram_configure_button.pack(side="left",padx=(0,8))
        telegram_reload_button=ttk.Button(
            telegram_row,text="Rileggi configurazione Telegram")
        telegram_reload_button.pack(side="left",padx=(0,8))
        telegram_note_button=ttk.Button(
            telegram_row,text="Messaggio da riferire (legacy)")
        telegram_note_button.pack(side="left")
        telegram_actions=ttk.Frame(telegram_panel)
        telegram_actions.pack(fill="x",pady=(4,3))
        telegram_contacts_button=ttk.Button(
            telegram_actions,text="Gestisci contatti Telegram (spunta)")
        telegram_contacts_button.pack(side="left",padx=(0,8))
        telegram_send_button=ttk.Button(
            telegram_actions,text="Invia messaggio vocale")
        telegram_send_button.pack(side="left")
        ttk.Label(
            telegram_panel,textvariable=d.telegram_status,wraplength=690
        ).pack(anchor="w",pady=(3,0))
        ttk.Label(
            telegram_panel,
            text="I contatti si scelgono dall'elenco Telegram con una spunta. "
                 "Le risposte automatiche si attivano separatamente dall'invio "
                 "manuale, che richiede conferma. I vocali usano Windows SAPI "
                 "e OGG/Opus, senza GPT per trasformare il testo in audio.",
            wraplength=690).pack(anchor="w",pady=(3,0))

        telegram_toggle.configure(command=d.toggle_telegram_automatic)
        telegram_configure_button.configure(command=telegram_open_setup)
        telegram_reload_button.configure(command=d.telegram_reconfigure)
        telegram_note_button.configure(command=leave_telegram_note_dialog)
        telegram_contacts_button.configure(command=d.open_telegram_contact_list)
        telegram_send_button.configure(command=open_telegram_manual_send)
        return telegram_panel

    return {nome: locals()[nome] for nome in NOMI}
