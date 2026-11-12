"""Interfaccia: impostazioni, chat, comandi su Lumi

Spostato da jarvis.py con il codice invariato (docs/PIANO-DIVISIONE-JARVIS.md):
i nomi di main() arrivano da `d` (lumi_contesto.Vivo), sempre col valore attuale.
"""
from __future__ import annotations

import os
import queue
import subprocess
import sys
import shutil
from collections import deque
from concurrent.futures import Future
import json
import re
import sqlite3
import time
from conversation_memory import ConversationMemory
from workspace_memory import WorkspaceMemory, WorkspaceError
from workspace_gui import ProjectManagerWindow
from project_voice import (parse_project_voice, safe_project_name,
                           find_existing_project, project_delete_response)
from dialogue_focus import (focus_hint, PendingProjectReference,
                            normalized_utterance,is_ambiguous_short_reply)
from project_documents import parse_simple_save, project_save_destination
from self_diagnostics import diagnostic_request, inspect_jarvis, format_audit
from diagnostic_session import DiagnosticSession
from runtime_diagnostics import (RuntimeEventCounters,
                                 collect_runtime_evidence,
                                 format_runtime_evidence)
from diagnostic_handoff import (build_external_review_prompt,
                                is_external_review_request, wants_external_advice,
                                summarize_operation_outcomes)
from settings import default_path
from telegram_commands import explicit_telegram_note
from telegram_directory import (list_telegram_contacts, send_telegram_voice)
from telegram_ui import (TelegramContactsWindow, edit_telegram_context,
                         show_telegram_manual_send)
from telegram_outbound_flow import (
    VoiceSendDialog, parse_telegram_send_intent, resolve_selected_recipient,
)
from telegram_bridge import (TelegramBridge, telegram_assistant_prompt, telegram_local_messages,
                             telegram_local_prompt)
from live_capabilities import (LiveCapabilityRegistry, snapshot_capabilities,
                               capability_status_prompt)
from addon_manager import AddonManager, AddonError
from addon_ui import AddonSettingsWindow
from telegram_security import credentials_present
from telegram_voice import missing_voice_dependencies
from jarvis_persona import build_chat_prompt
from startup_greeting import startup_greeting
from adaptive_voice import SpeechCorrections, SpeechCorrectionError
from second_brain import SecondBrain, BrainError
from memory_boundaries import (PreferenceStore, OperationJournal, MemoryBoundaryError,
                               observed_local_result, observed_saved_file)
from preference_voice import parse_preference_intent
from foreground_power import ForegroundPower
from animated_hud import JarvisHUD, BG, PANEL, CYAN, MUTED, WHITE, GREEN, AMBER
from desktop_dictation import DesktopDictation, dictation_voice_action
from conversation_router import (
    ConversationRejected, build_conversation_prompt, parse_conversation_intent,
)
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import webbrowser
from document_execution import run_document_worker
from document_dialog import DocumentDialog
from document_language import classify_document_choice
from document_store import destination_from_voice
from managed_documents import ManagedDocuments
from document_recovery import release_closed_document
from gpt_client import GPTClient, GPTUnavailable
from local_engine import LocalEngine, TaskResult
from offline_tts import OfflineSpeaker, installed_voices
from planner_ui import open_planner
from settings import (load_settings, save_settings, normalize_telegram_contacts,
                      TELEGRAM_PROFILE_LIMIT)
from jarvis_timer import TimerPopup, SOUNDS, parse_timer_command, preview_sound
from sveglia.service import Alarm, parse_command as parse_alarm_clock_command
from voice_control import (VoiceController, WakeWordGate, STANDBY, PUSH_TO_TALK, CONTINUOUS,
                           GPT_CONVERSATION, speech_to_local_command)

NOMI = ('settings_page', 'save_keep_awake', 'open_online_permissions', 'show_settings', 'save_timer_preferences', 'preview_timer_sound', 'orbit_open', 'active_addon_actions', 'addon_changed', 'refresh_buttons', 'save_dock_settings', 'run_understood_command', 'understood_catalog', 'understanding_output', 'chat_navigation_possible', 'on_chat_tab_change', 'selected_chat_target', 'schedule_style_save', 'close_with_goodbye', 'initial_launch', 'lumi_restart', 'lumi_shutdown_pc', 'lumi_cancel_shutdown', 'lumi_say', 'lumi_minimize', 'lumi_hide', 'lumi_wake', 'first_run_components')


def installa(d):
    """Crea le funzioni per questa esecuzione di Lumi; restituisce {nome: funzione}."""
    def settings_page(title: str) -> ttk.Frame:
        host = ttk.Frame(d.settings_tabs)
        d.settings_tabs.add(host, text=title)
        canvas = tk.Canvas(host, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(host, orient="vertical", command=canvas.yview)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scroll.set)
        inner = ttk.Frame(canvas, padding=15)
        item = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda event: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(
            item, width=event.width))
        return inner
    def save_keep_awake():
        previous = d.settings["keep_awake_fullscreen"]
        d.settings["keep_awake_fullscreen"] = d.keep_awake.get()
        try:
            save_settings(d.settings)
        except (OSError, ValueError) as exc:
            d.settings["keep_awake_fullscreen"] = previous
            d.keep_awake.set(previous)
            messagebox.showerror("Impostazioni", str(exc), parent=d.settings_window)
    def open_online_permissions():
        try:
            from local_model.online_permissions_ui import OnlinePermissionsWindow
            OnlinePermissionsWindow(d.settings_window)
        except (OSError, ValueError, RuntimeError, ImportError) as exc:
            messagebox.showerror("Lumi / Permessi GPT", str(exc), parent=d.settings_window)
    def show_settings() -> None:
        d.settings_window.deiconify()
        d.settings_window.lift()
        d.settings_window.focus_set()
    def save_timer_preferences() -> None:
        old = {key: d.settings[key] for key in
               ("timer_sound", "timer_volume", "timer_repeat", "timer_audio_mode")}
        selected = next((key for key, name in SOUNDS.items()
                         if name == d.timer_sound_label.get()), "digital")
        d.settings.update(timer_sound=selected,
                        timer_volume=int(round(d.timer_volume.get())),
                        timer_repeat=bool(d.timer_repeat.get()),
                        timer_audio_mode="beep" if d.timer_audio_beep.get() else "auto")
        try:
            save_settings(d.settings)
        except (OSError, ValueError) as exc:
            d.settings.update(old)
            d.timer_sound_label.set(SOUNDS[old["timer_sound"]])
            d.timer_volume.set(old["timer_volume"])
            d.timer_repeat.set(old["timer_repeat"])
            d.timer_audio_beep.set(old["timer_audio_mode"] == "beep")
            messagebox.showerror("Impostazioni timer", str(exc), parent=d.settings_window)
    def preview_timer_sound(force_beep: bool = False) -> None:
        chosen = next((key for key, name in SOUNDS.items()
                       if name == d.timer_sound_label.get()), "digital")
        mode = ("beep" if force_beep else
                ("beep" if d.timer_audio_beep.get() else "auto"))
        d.timer_audio_status.set("Invio del suono a Windows...")
        def audio_result(success: bool, message: str) -> None:
            try:
                d.root.after(0, lambda: d.timer_audio_status.set(
                    ("Audio: " if success else "Errore: ") + message))
            except (RuntimeError, tk.TclError):
                pass
        preview_sound(chosen, int(round(d.timer_volume.get())),
                      mode=mode, on_status=audio_result)
    def orbit_open(identifier:str) -> None:
        if identifier.startswith("telegram:"):
            parts=identifier.split(":")
            if len(parts)==3 and parts[1]=="pending":
                d.write_line("TELEGRAM > Messaggi da riferire ancora in attesa.")
            try:
                peer_id=int(parts[-1])
            except ValueError:
                return
            d.telegram_activity_window(peer_id)
        elif identifier=="projects:more":
            d.open_project_manager()
        else:
            d.switch_context(identifier)
    def active_addon_actions() -> tuple[dict,...]:
        if d.addon_manager is None:
            return ()
        try:
            return d.addon_manager.active_actions()
        except (AddonError,OSError,ValueError,ImportError):
            # Never let a broken or modified add-on directory break GPT chat.
            for item in d.addon_capability_registry.available_addons():
                d.addon_capability_registry.unregister(item["id"])
            return ()
    def addon_changed() -> None:
        d.write_line("ADD-ON > Registro aggiornato. Le capacità attive saranno "
                   "comunicate al GPT alla prossima richiesta.")
        # Add-on Telegram spento: si fermano anche le risposte automatiche.
        if not d.telegram_addon_enabled() and d.telegram_auto.get():
            d.telegram_auto.set(False)
            d.toggle_telegram_automatic()
    def refresh_buttons() -> None:
        can_gpt = d.gpt_enabled.get() and not d.busy_gpt and not d.closing
        d.connect.configure(state="normal" if can_gpt else "disabled")
        d.disconnect.configure(state="normal" if can_gpt and d.active_gpt else "disabled")
        d.ask_button.configure(state="normal" if can_gpt and d.active_gpt else "disabled")
        d.plan_button.configure(state="normal" if can_gpt and d.active_gpt else "disabled")
        d.local_button.configure(state="disabled" if d.busy_local or d.closing else "normal")
    def save_dock_settings() -> None:
        from lumi_avatar import _dock_file, save_dock_options
        try:
            seconds=int(d.dock_idle_var.get())
        except (tk.TclError,ValueError):
            seconds=30
        save_dock_options(_dock_file(),d.dock_show_var.get(),seconds)
        d.write_line("IMPOSTAZIONI > Mini avatar: "+("visibile" if d.dock_show_var.get() else "nascosto")
                   +(f", trasparente dopo {seconds} s di mouse fermo." if seconds else
                     ", sempre visibile anche col mouse fermo."))
    def run_understood_command(text: str) -> None:
        # Comando capito dal motore interno: stessi gestori dei comandi diretti.
        from voice_control import model_switch_target
        if model_switch_target(text) is not None and d.try_model_switch(text):
            return
        if d.try_file_command(text) or d.try_program_command(text) or d.try_timer_command(text):
            return
        command = speech_to_local_command(text)
        if command == "apri blocco note":
            d.document_operation("open", source_utterance=text)
            return
        d.submit_local(message_override=command or text, source_utterance=text)
    def understood_catalog() -> list:
        import command_aliases
        return [c for items in command_aliases.catalog(d.engine).values() for c in items]
    def understanding_output(line: str) -> None:
        # Le domande «Intendevi…?» si sentono anche a voce (uso senza mani).
        d.write_line(line)
        if line.startswith("LUMI > "):
            d.speak_result(line[7:])
    def chat_navigation_possible():
        return not (
            d.closing or d.busy_gpt or d.busy_local or d.gemma_trial_busy[0]
            or d.document_busy or d.save_only_waiting
            or d.doc_dialog.phase.startswith("awaiting_")
            or d.pending_project_name or d.pending_project_rename_id is not None
            or d.pending_project_trash_id is not None
            or bool(d.pending_conversation))
    def on_chat_tab_change(_event=None):
        if d.changing_chat_tab[0]:
            return
        selected = d.chat_notebook.select()
        if selected == d.previous_chat_tab[0]:
            return
        if not chat_navigation_possible():
            d.changing_chat_tab[0] = True
            d.chat_notebook.select(d.previous_chat_tab[0])
            d.changing_chat_tab[0] = False
            d.write_line("CHAT > Termina la richiesta corrente prima di cambiare vista.")
            return
        if selected == str(d.chat_local_tab):
            if not d.chat_sessions_panel.activate():
                d.changing_chat_tab[0] = True
                d.chat_notebook.select(d.chat_console_tab)
                d.changing_chat_tab[0] = False
                return
        else:
            d.chat_selection_changed(None, None)
        d.previous_chat_tab[0] = selected
    def selected_chat_target():
        if d.chat_notebook.select() != str(d.chat_local_tab):
            return None
        target = d.chat_sessions_panel.current_target()
        if target is None or target[1] != d.active_project_id:
            return None
        return target
    def schedule_style_save(*_args) -> None:
        if d.style_save_job[0] is not None:
            try:
                d.root.after_cancel(d.style_save_job[0])
            except tk.TclError:
                pass
        d.style_save_job[0] = d.root.after(700, d.save_speech_preferences)
    def close_with_goodbye() -> None:
        # Saluto alla chiusura (frasi variabili); con la voce attiva aspetta che lo dica.
        if d.closing or d.goodbye_started[0]:
            return
        d.goodbye_started[0] = True
        from datetime import datetime
        from frasi_lumi import greeting as lumi_greeting
        text = lumi_greeting("chiusura", datetime.now().hour)
        d.write_line("LUMI > " + text)
        if d.spoken_enabled.get():
            d.speak_result(text)
            d.root.after(2300, d.close)
        else:
            d.close()
    def initial_launch() -> None:
        """App-only autostart: never adds Windows login/run-at-boot entries."""
        if d.closing:
            return
        for warning in d.settings_load_warnings:
            d.write_line("IMPOSTAZIONI > " + warning)
        d.settings_load_warnings.clear()
        if d.auto_listen_enabled.get():
            d.voice_mode.set(GPT_CONVERSATION)
            d.change_voice_mode()
        # The local SAPI voice is suppressed from Vosk input by
        # ignore_audio=speaker.is_audible, also during the cooldown.
        greeting = startup_greeting()
        d.write_line("LUMI > " + greeting)
        d.speak_result(greeting)
    def lumi_restart() -> None:
        from frasi_lumi import say
        text = say("riavvio")
        d.write_line("LUMI > " + text)
        d.speak_result(text)
        # Un piccolo processo separato riapre Lumi quando questa si è chiusa.
        subprocess.Popen(
            [sys.executable, "-c",
             "import subprocess,sys,time;time.sleep(5);subprocess.Popen(sys.argv[1:])",
             sys.executable, *sys.argv], cwd=os.getcwd(),
            creationflags=getattr(subprocess, "DETACHED_PROCESS", 0))
        d.goodbye_started[0] = True
        # Chiude solo dopo aver detto il messaggio per intero (stima dalla lunghezza,
        # minimo 2,5 s), così la voce non viene tagliata.
        d.root.after(max(2500, int(len(text) * 80) + 1200) if d.spoken_enabled.get() else 600, d.close)
    def lumi_shutdown_pc() -> None:
        subprocess.run(["shutdown", "/s", "/t", "20"], check=False,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        message = ("Spengo il computer tra 20 secondi. Per fermarlo di' "
                   "«annulla lo spegnimento».")
        d.write_line("LUMI > " + message)
        d.speak_result(message)
    def lumi_cancel_shutdown() -> None:
        subprocess.run(["shutdown", "/a"], check=False,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        d.write_line("LUMI > Spegnimento annullato.")
        d.speak_result("Spegnimento annullato.")
    def lumi_say(key: str) -> None:
        from frasi_lumi import say
        text = say(key)
        d.write_line("LUMI > " + text)
        d.speak_result(text)
    def lumi_minimize() -> None:
        lumi_say("minimizzo")
        d.root.iconify()
    def lumi_hide() -> None:
        lumi_say("nascondo")
        d.avatar_dock.hide_by_user()
        if d.root.state() != "iconic":
            d.root.iconify()
    def lumi_wake() -> None:
        d.avatar_dock.unhide()
        d.root.deiconify()
        try:
            d.root.state("zoomed")
        except tk.TclError:
            pass
        d.root.lift()
        try:
            d.root.focus_force()
        except tk.TclError:
            pass
        lumi_say("sveglia")
    def first_run_components() -> None:
        # Primo avvio: finestra per installare i componenti facoltativi da dentro
        # Lumi (niente .bat). Dopo la chiusura non ricompare: si riapre da
        # Gestisci add-on > «Installa componenti...».
        try:
            from componenti import catalog as components_catalog
            if not components_catalog.load_state()["wizard_shown"]:
                from componenti.ui import ComponentsWindow
                ComponentsWindow(d.root)
        except (ImportError, OSError, tk.TclError) as exc:
            d.write_line("COMPONENTI > Finestra non disponibile: " + str(exc)[:120])
    funzioni = locals()
    return {nome: funzioni[nome] for nome in NOMI}
