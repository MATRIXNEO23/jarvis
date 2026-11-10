"""Lumi alpha — local commands, GPT conversation and offline voice.

App startup may automatically enable the locally configured Vosk microphone.
A visible settings switch can disable auto-listening for future launches; all
modes, including Standby, remain manually selectable at any time.
GPT requires the official SDK and an explicit account sign-in.
"""
from __future__ import annotations

import os
import queue
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


def main() -> None:
    settings_load_warnings = []
    settings = load_settings(warnings=settings_load_warnings)
    root = tk.Tk()
    from window_chrome import install_window_chrome
    install_window_chrome(root)
    root.title("LUMI // Interfaccia")
    root.geometry("1200x670")
    root.minsize(940, 580)
    root.configure(bg=BG)
    # The classic Windows ttk theme ignores colors; clam permits a coherent
    # dark HUD without adding any UI toolkit or graphics dependency.
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=WHITE)
    style.configure("TLabelframe", background=BG, foreground=WHITE)
    style.configure("TLabelframe.Label", background=BG, foreground=CYAN)
    style.configure("TCheckbutton", background=BG, foreground=WHITE)
    style.map("TCheckbutton", background=[("active", BG)])
    style.configure("TRadiobutton", background=BG, foreground=WHITE)
    style.map("TRadiobutton", background=[("active", BG)])
    style.configure("TButton", background=PANEL, foreground=CYAN,
                    bordercolor="#0b4a6b", padding=(8, 5))
    style.map("TButton",
              foreground=[("disabled", "#486579"), ("active", WHITE)],
              background=[("active", "#0b3950")])
    style.configure("TEntry", fieldbackground=PANEL, foreground=WHITE,
                    insertcolor=CYAN)
    style.configure("TCombobox", fieldbackground=PANEL, foreground=WHITE)
    style.configure("Vertical.TScrollbar", background=PANEL,
                    troughcolor=BG)
    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=PANEL, foreground=CYAN,
                    padding=(13, 8))
    style.map("TNotebook.Tab",
              background=[("selected", "#124058"), ("active", "#0b344a")],
              foreground=[("selected", WHITE)])

    # Every existing setting remains available without crowding the main HUD.
    # The settings window is created once, hidden until the user presses ⚙.
    settings_window = tk.Toplevel(root)
    settings_window.title("LUMI // Impostazioni")
    settings_window.geometry("820x650")
    settings_window.minsize(650, 480)
    settings_window.withdraw()
    settings_window.protocol("WM_DELETE_WINDOW", settings_window.withdraw)
    # Reorganize only the existing gear-opened window: no control is removed.
    # Each existing section has its own independently scrollable category.
    settings_tabs = ttk.Notebook(settings_window)
    settings_tabs.pack(fill="both", expand=True, padx=8, pady=8)

    def settings_page(title: str) -> ttk.Frame:
        host = ttk.Frame(settings_tabs)
        settings_tabs.add(host, text=title)
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

    frame = settings_page("Voce")
    assistant_settings_frame = settings_page("GPT e memoria")
    integrations_settings_frame = settings_page("Progetti e servizi")
    timer_settings_frame = settings_page("Timer e allarmi")
    interface_settings_frame = settings_page("Interfaccia")
    keep_awake = tk.BooleanVar(value=settings["keep_awake_fullscreen"])
    power = ForegroundPower(root, keep_awake.get)

    def save_keep_awake():
        previous = settings["keep_awake_fullscreen"]
        settings["keep_awake_fullscreen"] = keep_awake.get()
        try:
            save_settings(settings)
        except (OSError, ValueError) as exc:
            settings["keep_awake_fullscreen"] = previous
            keep_awake.set(previous)
            messagebox.showerror("Impostazioni", str(exc), parent=settings_window)

    ttk.Checkbutton(interface_settings_frame,
                    text="Tieni acceso il PC con Lumi massimizzato in primo piano",
                    variable=keep_awake, command=save_keep_awake).pack(anchor="w")
    ttk.Label(interface_settings_frame, wraplength=540,
              text="Sospende lo standby automatico e lo spegnimento dello schermo "
                   "finché la finestra principale di Lumi è massimizzata e in primo piano."
              ).pack(anchor="w", pady=(6, 0))

    # Optional native settings editor. No model initialization or provider switch.
    def open_native_model_settings():
        try:
            from local_model.native_ui import NativeSettingsWindow
            NativeSettingsWindow(settings_window, get_session=get_gemma_session)
        except (OSError, ValueError, RuntimeError, ImportError) as exc:
            messagebox.showerror("Lumi / Gemma", str(exc), parent=settings_window)

    native_settings_box = ttk.LabelFrame(assistant_settings_frame,
                                         text="Modello locale Gemma (sperimentale)")
    native_settings_box.pack(fill="x", padx=8, pady=8)
    ttk.Label(native_settings_box,
              text="Configurazione separata; non attiva il modello e non cambia GPT.",
              wraplength=540).pack(anchor="w", padx=8, pady=5)
    ttk.Button(native_settings_box, text="Configura Gemma locale...",
               command=open_native_model_settings).pack(anchor="w", padx=8, pady=6)

    # F5 experimental preview: deliberately NOT connected to the active model.
    def open_multimodel_f5_preview():
        try:
            from local_model.multimodel_ui_f5 import MultiModelSettingsF5Window
            MultiModelSettingsF5Window(settings_window)
        except (OSError, ValueError, RuntimeError, ImportError) as exc:
            messagebox.showerror("Lumi / Multimodello F5", str(exc),
                                 parent=settings_window)

    ttk.Button(native_settings_box, text="Anteprima multimodello Gemma / Qwen...",
               command=open_multimodel_f5_preview).pack(anchor="w", padx=8, pady=6)

    def open_memory_preferences():
        try:
            from local_model.memory_ui import MemoryPreferencesWindow
            MemoryPreferencesWindow(settings_window, get_session=get_gemma_session)
        except (OSError, ValueError, RuntimeError, ImportError) as exc:
            messagebox.showerror("Lumi / Memoria", str(exc), parent=settings_window)

    ttk.Button(native_settings_box, text="Configura memoria e inattivita...",
               command=open_memory_preferences).pack(anchor="w", padx=8, pady=6)

    def open_online_permissions():
        try:
            from local_model.online_permissions_ui import OnlinePermissionsWindow
            OnlinePermissionsWindow(settings_window)
        except (OSError, ValueError, RuntimeError, ImportError) as exc:
            messagebox.showerror("Lumi / Permessi GPT", str(exc), parent=settings_window)

    ttk.Button(native_settings_box, text="Autorizzazioni GPT per funzione...",
               command=open_online_permissions).pack(anchor="w", padx=8, pady=6)


    def show_settings() -> None:
        settings_window.deiconify()
        settings_window.lift()
        settings_window.focus_set()

    hud = JarvisHUD(root, show_settings)
    timer = TimerPopup(root, lambda: settings)
    workspace_status=tk.StringVar(value="Progetti: inizializzazione.")
    telegram_status=tk.StringVar(value="Telegram: disattivato.")
    active_context_label=tk.StringVar(value="Contesto: GENERALE")
    active_project_id=None
    chat_sessions_panel=None
    workspace=None
    try:
        workspace=WorkspaceMemory()
        recovered=workspace.current_project()
        if recovered is not None:
            restored=workspace.project(recovered)
            active_project_id=recovered
            active_context_label.set("Contesto: "+restored["name"][:35])
        workspace_status.set(
            "Memoria progetti: "+str(len(workspace.projects()))+" progetti locali."
            + (" Ripreso: "+restored["name"][:40] if recovered else ""))
    except (OSError,sqlite3.Error,WorkspaceError) as exc:
        workspace_status.set("Memoria progetti non disponibile: "+str(exc)[:120])
    telegram_bridge=None
    telegram_gpt_ready=threading.Event()
    telegram_gpt_session_token=None
    telegram_gpt_session_choice=tk.BooleanVar(value=False)
    telegram_auto=tk.BooleanVar(value=settings["telegram_enabled"])
    telegram_contacts_dialog=None
    telegram_contacts_frame=None
    telegram_contacts_status=None
    telegram_contact_vars={}
    telegram_available_contacts=[]
    telegram_voice_dialog=VoiceSendDialog()
    addon_capability_registry=LiveCapabilityRegistry()
    addon_manager=None
    addon_setup_error=""
    try:
        addon_manager=AddonManager(addon_capability_registry)
        if not any(item["id"]=="accesso_file" for item in addon_manager.list_installed()):
            bundled=Path(__file__).parent/"file_access"/"AccessoFile.jaddon"
            if bundled.is_file():
                addon_manager.install(bundled)  # Descriptive only, remains OFF.
        if not any(item['id']=='programmi_app' for item in addon_manager.list_installed()):
            bundled=Path(__file__).parent/'program_apps'/'ProgrammiApp.jaddon'
            if bundled.is_file():
                addon_manager.install(bundled)  # No application is enabled by installation.

        if not any(item["id"] == "sveglia" for item in addon_manager.list_installed()):
            bundled = Path(__file__).parent / "sveglia" / "Sveglia.jaddon"
            if bundled.is_file():
                addon_manager.install(bundled)
        if not any(item["id"] == "musica" for item in addon_manager.list_installed()):
            bundled = Path(__file__).parent / "musica" / "Musica.jaddon"
            if bundled.is_file():
                addon_manager.install(bundled)  # Installed OFF: nothing changes until enabled.

    except (AddonError,OSError,ValueError) as exc:
        addon_setup_error=str(exc)[:150]
    alarm_status = tk.StringVar(value="Nessuna sveglia impostata.")
    alarm = Alarm(root, lambda: bool(addon_manager and any(
        item["id"] == "sveglia" and item["enabled"]
        for item in addon_manager.list_installed())),
        lambda: settings, alarm_status,
        lambda text: (write_line("SVEGLIA > " + text), speak_result(text)),
        hud.set_alarm_active)
    hud.alarm_stop_button.configure(command=alarm.stop)
    # Add-on Musica (cartella musica / YouTube nel browser), solo se attivo.
    music_service = None
    music_bar = None
    try:
        from musica.service import MusicService
        music_service = MusicService(
            lambda: bool(addon_manager and any(
                item["id"] == "musica" and item["enabled"]
                for item in addon_manager.list_installed())),
            notify=lambda text: output_queue.put(("music_status", text)))
        if addon_manager is not None:
            addon_manager.music_service = music_service
        from musica.bar import MusicBar
        music_bar = MusicBar(hud.core_canvas, music_service,
                             on_message=lambda text: write_line("MUSICA > " + text))
    except (ImportError, OSError, ValueError, tk.TclError, AttributeError) as exc:
        addon_setup_error = (addon_setup_error or "") + " Musica: " + str(exc)[:80]
        music_service = None
        music_bar = None
    addon_settings_window=None
    telegram_owner_busy=False
    orbit_nodes_cache=()

    ttk.Label(frame, text="Voce e ascolto",
              font=("Segoe UI", 17, "bold")).pack(anchor="w")
    mic_status = tk.StringVar(value=(
        "Microfono: avvio dell'ascolto continuo in preparazione..."
        if settings["auto_listen"] else "Microfono: SPENTO all'avvio"))
    ttk.Label(frame, textvariable=mic_status, wraplength=710).pack(anchor="w", pady=(2, 6))
    voice_mode = tk.StringVar(value=STANDBY)
    audio_controls = ttk.LabelFrame(
        frame, text="Voce offline — ascolto e modalità selezionabili", padding=8)
    audio_controls.pack(fill="x", pady=(0, 9))
    mode_buttons = []
    mode_row = ttk.Frame(audio_controls)
    mode_row.pack(fill="x")
    mode_row.columnconfigure(0, weight=1)
    mode_row.columnconfigure(1, weight=1)
    for index, (label, mode) in enumerate((
            ("Standby (spento)", STANDBY),
            ("Premi per parlare", PUSH_TO_TALK),
            ("Ascolto continuo", CONTINUOUS),
            ("Hey Lumi", GPT_CONVERSATION))):
        button = ttk.Radiobutton(mode_row, text=label, variable=voice_mode, value=mode)
        button.grid(row=index // 2, column=index % 2, sticky="w", padx=(0, 12), pady=3)
        mode_buttons.append(button)
    auto_listen_enabled = tk.BooleanVar(value=settings["auto_listen"])
    auto_listen_switch = ttk.Checkbutton(
        audio_controls,
        text="Avvia Lumi con microfono attivo (richiede Lumi prima di ogni comando)",
        variable=auto_listen_enabled)
    auto_listen_switch.pack(anchor="w", pady=(5, 1))
    ttk.Label(
        audio_controls,
        text="Il microfono resta acceso fino a quando scegli Standby. "
             "La voce non viene salvata: Vosk trascrive in locale; "
             "solo le richieste precedute da Lumi vengono elaborate; "
             "la conversazione usa Gemma locale, senza invio automatico a GPT.",
        wraplength=710).pack(anchor="w", pady=(0, 4))
    ptt_button = ttk.Button(audio_controls, text="Tieni premuto per parlare", state="disabled")
    ptt_button.pack(anchor="w", pady=(5, 0))
    dictation_row = ttk.Frame(audio_controls)
    dictation_row.pack(fill="x", pady=(6, 0))
    dictation_button = ttk.Button(dictation_row, text="Attiva dettatura", state="disabled")
    dictation_button.pack(side="left", padx=(0, 9))
    dictation_status = tk.StringVar(value="Dettatura: disattivata.")
    ttk.Label(dictation_row, textvariable=dictation_status, wraplength=500).pack(
        side="left", fill="x", expand=True)


    # Built-in Windows voices are optional: no network and no new model.
    spoken_enabled = tk.BooleanVar(value=settings["tts_enabled"])
    DEFAULT_VOICE_LABEL = "Predefinita di Windows"
    spoken_voice = tk.StringVar(value=settings["tts_voice"] or DEFAULT_VOICE_LABEL)
    speech_controls = ttk.LabelFrame(frame, text="Risposte vocali offline — voci di Windows", padding=8)
    speech_controls.pack(fill="x", pady=(0, 8))
    spoken_switch = ttk.Checkbutton(
        speech_controls, text="Lumi risponde a voce", variable=spoken_enabled)
    spoken_switch.pack(anchor="w")
    speech_row = ttk.Frame(speech_controls)
    speech_row.pack(fill="x", pady=(4, 0))
    ttk.Label(speech_row, text="Voce:").pack(side="left", padx=(0, 6))
    spoken_picker = ttk.Combobox(
        speech_row, textvariable=spoken_voice, state="readonly",
        values=[DEFAULT_VOICE_LABEL], width=36)
    spoken_picker.pack(side="left", padx=(0, 6))
    refresh_voices_button = ttk.Button(speech_row, text="Aggiorna voci")
    refresh_voices_button.pack(side="left", padx=(0, 6))
    test_voice_button = ttk.Button(speech_row, text="Prova voce")
    test_voice_button.pack(side="left")
    # Natural voices (Piper) from the repository + digital effect (9/11).
    natural_row = ttk.Frame(speech_controls)
    natural_row.pack(fill="x", pady=(6, 0))
    ttk.Label(natural_row, text="Voci naturali:").pack(side="left", padx=(0, 6))
    download_paola_button = ttk.Button(natural_row, text="Scarica Paola")
    download_paola_button.pack(side="left", padx=(0, 6))
    download_serena_button = ttk.Button(natural_row, text="Scarica Serena")
    download_serena_button.pack(side="left", padx=(0, 12))
    ttk.Label(natural_row, text="Effetto digitale:").pack(side="left", padx=(0, 4))
    spoken_effect = tk.IntVar(value=settings.get("tts_effect", 25))
    ttk.Scale(natural_row, from_=0, to=100, variable=spoken_effect, length=140,
              command=lambda _v: spoken_effect.set(int(float(_v)))).pack(side="left")
    ttk.Label(natural_row, textvariable=spoken_effect, width=4).pack(side="left", padx=(4, 0))
    # Velocità, tonalità e volume: valgono per tutte le voci e per Telegram.
    style_row = ttk.Frame(speech_controls)
    style_row.pack(fill="x", pady=(6, 0))
    spoken_rate = tk.IntVar(value=settings.get("tts_rate", 0))
    spoken_pitch = tk.IntVar(value=settings.get("tts_pitch", 0))
    spoken_volume = tk.IntVar(value=settings.get("tts_volume", 100))
    for label, variable, low, high in (("Velocità:", spoken_rate, -50, 50),
                                       ("Tonalità:", spoken_pitch, -50, 50),
                                       ("Volume:", spoken_volume, 10, 100)):
        ttk.Label(style_row, text=label).pack(side="left", padx=(0, 4))
        ttk.Scale(style_row, from_=low, to=high, variable=variable, length=110,
                  command=lambda _v, var=variable: var.set(int(float(_v)))).pack(side="left")
        ttk.Label(style_row, textvariable=variable, width=4).pack(side="left", padx=(2, 10))
    ttk.Label(speech_controls, wraplength=680, foreground="#5f8aa3", text=(
        "Paola e Serena sono voci Piper scaricate dal repository Lumi con verifica. "
        "Serena: it_IT-serena-high by Marco Baccarani (Committa), CC BY 4.0. "
        "Il motore voce è già incluso in Lumi (cartella voce_engine): basta scaricare la voce. "
        "Se non funziona su questo PC si usa la voce di Windows. "
        "Voci Edge (Isabella, Elsa, Diego, Giuseppe): gratuite ma ONLINE, il testo va al "
        "servizio Microsoft; si attivano con installa_voce_edge.bat.")
              ).pack(anchor="w", pady=(4, 0))
    spoken_status = tk.StringVar(value="Voci locali: da rilevare.")
    ttk.Label(speech_controls, textvariable=spoken_status, wraplength=680).pack(anchor="w")

    # A compact popup keeps the existing Pavilion main window usable.
    last_voice_sample = tk.StringVar(value="Nessuna frase ancora riconosciuta.")
    voice_correction_button = ttk.Button(
        dictation_row, text="Correggi voce...")
    voice_correction_button.pack(side="right", padx=(6, 0))

    # Timer tone selection is part of the ORIGINAL gear settings dialog.
    ttk.Label(timer_settings_frame, text="Timer e allarmi",
              font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(0, 10))
    timer_box = ttk.LabelFrame(timer_settings_frame,
                               text="Suoneria alla scadenza", padding=12)
    timer_box.pack(fill="x", pady=(0, 10))
    timer_sound_label = tk.StringVar(
        value=SOUNDS.get(settings.get("timer_sound", "digital"), SOUNDS["digital"]))
    timer_volume = tk.DoubleVar(value=float(settings.get("timer_volume", 80)))
    timer_volume_label = tk.StringVar(value=str(settings.get("timer_volume", 80)) + "%")
    timer_repeat = tk.BooleanVar(value=settings.get("timer_repeat", True))
    timer_audio_beep = tk.BooleanVar(
        value=settings.get("timer_audio_mode", "auto") == "beep")
    timer_audio_status = tk.StringVar(value="Premi Prova per verificare l'audio.")
    sound_row = ttk.Frame(timer_box)
    sound_row.pack(fill="x", pady=5)
    ttk.Label(sound_row, text="Suono:").pack(side="left", padx=(0, 8))
    timer_picker = ttk.Combobox(sound_row, state="readonly",
                                textvariable=timer_sound_label,
                                values=list(SOUNDS.values()), width=25)
    timer_picker.pack(side="left", padx=(0, 9))

    def save_timer_preferences() -> None:
        old = {key: settings[key] for key in
               ("timer_sound", "timer_volume", "timer_repeat", "timer_audio_mode")}
        selected = next((key for key, name in SOUNDS.items()
                         if name == timer_sound_label.get()), "digital")
        settings.update(timer_sound=selected,
                        timer_volume=int(round(timer_volume.get())),
                        timer_repeat=bool(timer_repeat.get()),
                        timer_audio_mode="beep" if timer_audio_beep.get() else "auto")
        try:
            save_settings(settings)
        except (OSError, ValueError) as exc:
            settings.update(old)
            timer_sound_label.set(SOUNDS[old["timer_sound"]])
            timer_volume.set(old["timer_volume"])
            timer_repeat.set(old["timer_repeat"])
            timer_audio_beep.set(old["timer_audio_mode"] == "beep")
            messagebox.showerror("Impostazioni timer", str(exc), parent=settings_window)

    timer_picker.bind("<<ComboboxSelected>>",
                      lambda event: save_timer_preferences())
    def preview_timer_sound(force_beep: bool = False) -> None:
        chosen = next((key for key, name in SOUNDS.items()
                       if name == timer_sound_label.get()), "digital")
        mode = ("beep" if force_beep else
                ("beep" if timer_audio_beep.get() else "auto"))
        timer_audio_status.set("Invio del suono a Windows...")
        def audio_result(success: bool, message: str) -> None:
            try:
                root.after(0, lambda: timer_audio_status.set(
                    ("Audio: " if success else "Errore: ") + message))
            except (RuntimeError, tk.TclError):
                pass
        preview_sound(chosen, int(round(timer_volume.get())),
                      mode=mode, on_status=audio_result)

    ttk.Button(sound_row, text="▶ Prova",
               command=preview_timer_sound).pack(side="left")
    ttk.Button(sound_row, text="▶ Bip alternativo",
               command=lambda: preview_timer_sound(True)).pack(side="left", padx=5)
    ttk.Label(timer_box, textvariable=timer_audio_status,
              wraplength=590).pack(anchor="w", pady=(5, 3))
    ttk.Checkbutton(timer_box,
                    text="Usa bip alternativo Windows per l'allarme",
                    variable=timer_audio_beep,
                    command=save_timer_preferences).pack(anchor="w", pady=(5, 0))
    ttk.Label(timer_box,
              text="Il bip alternativo usa il volume di Windows, "
                   "non il cursore Lumi.", wraplength=590).pack(anchor="w")
    volume_row = ttk.Frame(timer_box)
    volume_row.pack(fill="x", pady=(12, 5))
    ttk.Label(volume_row, text="Volume").pack(side="left", padx=(0, 8))
    timer_volume_slider = ttk.Scale(volume_row, from_=0, to=100,
                                     variable=timer_volume,
                                     command=lambda value:
                                     timer_volume_label.set(str(int(round(float(value)))) + "%"))
    timer_volume_slider.pack(side="left", fill="x", expand=True)
    ttk.Label(volume_row, textvariable=timer_volume_label, width=5).pack(side="left")
    timer_volume_slider.bind("<ButtonRelease-1>",
                             lambda event: save_timer_preferences())
    timer_volume_slider.bind("<KeyRelease>",
                             lambda event: save_timer_preferences())
    ttk.Checkbutton(timer_box, text="Ripeti l'allarme finché non lo fermo",
                    variable=timer_repeat, command=save_timer_preferences).pack(
                        anchor="w", pady=(8, 2))
    ttk.Label(timer_settings_frame,
              text="Il timer si apre in una finestra indipendente. "
                   "Puoi impostarlo a voce con 'timer 10 minuti', "
                   "oppure modificare ore, minuti e secondi manualmente.",
              wraplength=630).pack(anchor="w", pady=(3, 10))
    ttk.Button(timer_settings_frame, text="Apri timer",
               command=timer.show).pack(anchor="w", pady=(0, 10))
    alarm_box = ttk.LabelFrame(timer_settings_frame, text="Sveglia")
    alarm_box.pack(fill="x", pady=(0, 10))
    alarm_input = ttk.Entry(alarm_box, width=8)
    alarm_input.insert(0, "07:30")
    alarm_input.pack(side="left", padx=6, pady=6)
    ttk.Button(alarm_box, text="Imposta",
               command=lambda: alarm_status.set(alarm.arm(alarm_input.get()))).pack(side="left")
    ttk.Button(alarm_box, text="Ferma", command=alarm.stop).pack(side="left", padx=6)
    ttk.Label(timer_settings_frame, textvariable=alarm_status).pack(anchor="w")


    document_controls = ttk.Frame(frame)
    document_controls.pack(fill="x", pady=(0, 6))
    document_status = tk.StringVar(value="Documenti: nessuno aperto da Lumi.")
    ttk.Label(document_controls, textvariable=document_status, wraplength=530).pack(
        side="left", fill="x", expand=True)
    choose_save_button = ttk.Button(document_controls, text="Scegli dove salvare",
                                    state="disabled")
    choose_save_button.pack(side="right", padx=(6, 0))
    # Saving a document is an action, not a setting: show its choices beside
    # the conversation. Hidden when no confirmation is pending.
    # Visible even when the secondary '...' toolbar is collapsed.
    diagnostic_status = tk.StringVar(value="Autodiagnosi: pronta")
    diagnostic_percent = tk.IntVar(value=0)
    # Completely hidden until an audit really starts. The old permanent
    # white ttk progress bar and large "Annulla" button overwhelmed the chat.
    diagnostic_row = tk.Frame(hud.command_host,bg="#03111d",height=21)
    tk.Label(diagnostic_row,textvariable=diagnostic_status,
             bg="#03111d",fg="#7baec6",anchor="w",
             font=("Consolas",8)).pack(side="left",fill="x",expand=True)
    diagnostic_cancel_button = tk.Button(
        diagnostic_row,text="×",state="disabled",width=2,
        bg="#03111d",fg="#8eb6c7",disabledforeground="#355466",
        activebackground="#0b3049",activeforeground="#d9f5ff",
        font=("Segoe UI",11),bd=0,relief="flat",cursor="hand2")
    diagnostic_cancel_button.pack(side="right",padx=(3,0))
    diagnostic_meter=tk.Canvas(
        diagnostic_row,width=58,height=4,bg="#092438",bd=0,
        highlightthickness=0)
    diagnostic_meter.pack(side="right",padx=(6,3))
    def draw_diagnostic_meter(_event=None):
        diagnostic_meter.delete("progress")
        w=max(1,diagnostic_meter.winfo_width())
        h=max(1,diagnostic_meter.winfo_height())
        progress=max(0,min(100,diagnostic_percent.get()))
        diagnostic_meter.create_rectangle(
            0,0,w*progress/100,h,fill="#17b8e5",outline="",
            tags="progress")
    diagnostic_meter.bind("<Configure>",draw_diagnostic_meter)
    doc_choices = ttk.Frame(hud.command_host)
    doc_choices.pack(fill="x", pady=(0, 5))
    doc_choices.pack_forget()
    hud_save_file_button = ttk.Button(
        doc_choices, text="Scegli file...", state="disabled")
    hud_save_file_button.pack(side="left", padx=(0, 6))
    doc_save_button = ttk.Button(doc_choices, text="Salva e chiudi", state="disabled")
    doc_save_button.pack(side="left", padx=(0, 6))
    doc_discard_button = ttk.Button(doc_choices, text="Esci senza salvare", state="disabled")
    doc_discard_button.pack(side="left", padx=(0, 6))
    doc_cancel_button = ttk.Button(doc_choices, text="Annulla chiusura", state="disabled")
    doc_cancel_button.pack(side="left")

    service = GPTClient()
    # Native inference is not enabled until a separate explicit model-selection
    # control is implemented and approved. Account actions remain on GPTClient.
    from local_model.chat_transport import ChatTransport
    class _UnavailableNative:
        def call(self, action, **arguments):
            raise RuntimeError("Gemma locale non ancora attivato.")
    chat_transport = ChatTransport(service, _UnavailableNative())
    output_queue: queue.Queue[tuple] = queue.Queue()
    gpt_enabled = tk.BooleanVar(value=settings["gpt_enabled"])
    gpt_status = tk.StringVar(value="GPT: inizializzazione" if gpt_enabled.get() else "GPT: disattivato")
    busy_local = False
    busy_gpt = False
    online_consent_pending = False
    gpt_conversation_session_grant = None
    gpt_request_action = ""
    local_execution_lock = threading.Lock()
    planner_abort_event = threading.Event()
    closing = False
    active_gpt = False
    conversation_epoch = 0
    document_busy = False
    documents = ManagedDocuments()
    doc_dialog = DocumentDialog()
    document_topic = ""
    document_owner_project_id = None
    pending_project_name = False
    pending_project_rename_id = None
    pending_project_trash_id = None
    pending_project_reference = PendingProjectReference()
    diagnostic_busy = False
    diagnostic_session = DiagnosticSession()
    diagnostic_threads = []
    last_diagnostic_audit = None
    last_runtime_evidence = None
    runtime_events = RuntimeEventCounters()
    pending_external_review = False
    save_only_waiting = False
    conversation_memory = ConversationMemory()
    pending_preference = None
    local_operation_id = None
    document_operation_id = None
    last_notepad_probe = 0.0
    preference_store = None
    operation_ledger = None
    # Up to three follow-ups may arrive while the model is still responding.
    # Never silently discard an earlier phrase or replay after mode changes.
    pending_conversation = deque()
    last_user_for_action = ""
    last_user_for_document = ""
    project_local_ticket = None
    project_document_ticket = None
    memory_enabled = tk.BooleanVar(value=settings["memory_enabled"])
    memory_status = tk.StringVar(value="Second Brain: inizializzazione.")
    durable_brain: SecondBrain | None = None
    gemma_memory_revision = 0
    speech_lexicon: SpeechCorrections | None = None
    # Preferences and operation history never share project/chat partitions.
    try:
        preference_store = PreferenceStore()
        operation_ledger = OperationJournal()
    except (OSError, sqlite3.Error, MemoryBoundaryError) as exc:
        memory_status.set("Archivio memoria separata non disponibile: "+str(exc)[:85])
    if memory_enabled.get():
        try:
            durable_brain = SecondBrain()
            speech_lexicon = SpeechCorrections(durable_brain.path)
            memory_status.set("Second Brain: attivo (memoria locale sul PC).")
        except (OSError, sqlite3.Error, SpeechCorrectionError, ValueError) as exc:
            durable_brain = None
            speech_lexicon = None
            memory_enabled.set(False)
            memory_status.set("Second Brain non disponibile: " + str(exc)[:90])
    else:
        memory_status.set("Second Brain: disattivato, conversazione breve solo in RAM.")

    def write_line(text: str) -> None:
        # The reference design uses a conversational timeline, not raw logs.
        # All actions and errors remain visible, with timestamp and source.
        label = str(text).strip()
        if not label:
            return
        low = label.casefold()
        role = ("utente" if low.startswith((
                    "utente >", "tu >", "domanda a gpt >", "comando locale >"))
                else "azione" if low.startswith((
                    "documento >", "[completed]", "correzione voce >"))
                else "jarvis" if low.startswith((
                    "jarvis >", "gpt >", "lia >", "lumi >"))
                else "errore" if (
                    "[failed]" in low or "[rejected]" in low
                    or low.startswith(("errore", "gpt: impossibile")))
                else "sistema")
        identity = {"utente":"●  TU",
                    "jarvis":"◉  LUMI",
                    "azione":"✓  OPERAZIONE",
                    "errore":"!  ERRORE",
                    "sistema":"·  SISTEMA"}[role]
        # Strip repeated provider prefixes without hiding the actual result.
        prefixes = ("utente >", "tu >", "domanda a gpt >", "comando locale >",
                    "jarvis >", "gpt >", "lia >", "lumi >", "documento >",
                    "correzione voce >")
        body = label
        for prefix in prefixes:
            if low.startswith(prefix):
                body = label[len(prefix):].strip()
                break
        output.configure(state="normal")
        output.insert(
            "end", identity + "         " +
            datetime.now().strftime("%H:%M:%S") + "\n",
            (role, "message_head"))
        output.insert("end", body + "\n\n", role)
        # Keep the UI responsive even during long voice conversations.
        # Drop only old visible console messages, never task/memory records.
        if int(output.index("end-1c").split(".")[0]) > 2200:
            output.delete("1.0", "200.0")
        output.see("end")
        output.configure(state="disabled")

    def memory_status_refresh(note: str = "") -> None:
        if durable_brain is None or not memory_enabled.get():
            memory_status.set(note or
                "Second Brain: solo memoria breve in RAM; archivio locale non attivo.")
            return
        try:
            turns, completed = durable_brain.stats()
            memory_status.set(
                f"Second Brain locale attivo: {turns} scambi, {completed} operazioni verificate."
                + (" " + note if note else ""))
        except (OSError, sqlite3.Error, ValueError) as exc:
            memory_status.set("Second Brain: errore di lettura: " + str(exc)[:85])

    def remember_exchange(user: str, reply: str, kind: str = "chat") -> bool | None:
        if re.search(r"\b(password|passphrase|token|pin|codice otp)\b",
                     user + " " + reply, re.I):
            return False
        conversation_memory.remember(user, reply, kind)
        # Explicitly created project memory advances independently from
        # the general-chat Second Brain opt-in switch.
        if active_project_id is not None:
            if workspace is not None:
                try:
                    return workspace.add_turn("project",active_project_id,
                                              user,reply,kind)
                except (OSError,sqlite3.Error,WorkspaceError) as exc:
                    workspace_status.set("Memoria progetto: "+str(exc)[:90])
            return False
        if not memory_enabled.get():
            return
        if durable_brain is not None:
            try:
                saved = durable_brain.remember_turn(user, reply, kind)
                memory_status_refresh()
                return saved
            except (OSError, sqlite3.Error, BrainError) as exc:
                memory_status.set("Memoria locale non scritta: " + str(exc)[:95])
        return False

    def remember_completed_action(action_id: str, application: str,
                                  summary: str, receipt_id: str,
                                  *, filename: str = "", folder: str = "",
                                  observed: bool = False) -> None:
        if (observed is not True or durable_brain is None or not memory_enabled.get()
                or active_project_id is not None):
            return
        metadata = {}
        if filename:
            metadata["file_name"] = filename[:140]
        if folder:
            metadata["folder"] = folder[:140]
        try:
            durable_brain.record_completed_action(
                action_id, application, summary,
                receipt_id=receipt_id, metadata=metadata, verified=True,
                proof_kind="local_observation")
            memory_status_refresh()
        except (OSError, sqlite3.Error, BrainError) as exc:
            memory_status.set("Ricevuta non registrata: " + str(exc)[:90])

    def begin_project_work(title: str, source: str = "local",
                           *, project_id: str | None = None,
                           planned: bool = False):
        """Persist a work ticket BEFORE executing a project operation."""
        ident=project_id if project_id is not None else active_project_id
        if ident is None:
            return None
        if workspace is None:
            workspace_status.set("Memoria progetto non disponibile: azione bloccata.")
            return False
        try:
            return (ident,workspace.begin_step(
                ident,title[:240],source=source,planned=planned))
        except (OSError,sqlite3.Error,WorkspaceError) as exc:
            workspace_status.set("Checkpoint non scritto: "+str(exc)[:110])
            return False

    def finish_project_work(ticket, status: str, detail: str,
                            *, receipt: str = "", observed: bool = False) -> bool:
        if not ticket or ticket is False or workspace is None:
            return False
        try:
            return bool(workspace.finish_step(
                ticket[0],ticket[1],status,detail,
                receipt=receipt,verified=observed))
        except (OSError,sqlite3.Error,WorkspaceError) as exc:
            # Planner callbacks may execute off the Tk thread.
            output_queue.put(("project_journal_error",str(exc)[:100]))
            return False

    def recent_memory_for_gpt(spoken: str) -> str:
        """Bounded recall with the *real* active project and latest question."""
        short=conversation_memory.context(max_chars=860)
        question=conversation_memory.last_question()

        def attach(raw,*,project_name=""):
            hint=focus_hint(spoken,active_project_name=project_name,
                            last_question=question)
            try:
                parsed=json.loads(raw)
            except (ValueError,TypeError):
                return raw
            if isinstance(parsed,list):
                parsed={"breve":parsed}
            if not isinstance(parsed,dict):
                return raw
            if (addon_manager is not None and getattr(addon_manager,'_program_service',None) is not None
                    and addon_manager.programs_enabled()):
                program_hint=addon_manager.program_service.context_hint()
                if program_hint:
                    hint['program_request']=program_hint
            if (addon_manager is not None and addon_manager._file_service is not None
                    and addon_manager.files_enabled()):
                file_hint=addon_manager.file_service.context_hint()
                if file_hint:
                    hint["file_results"]=file_hint
            if hint:
                parsed["focus"]=hint
            if preference_store is not None:
                try:
                    parsed["preferences"]=list(preference_store.context())
                except (OSError,sqlite3.Error,MemoryBoundaryError):
                    pass
            return json.dumps(parsed,ensure_ascii=False)

        if active_project_id is not None:
            if workspace is None:
                return attach(short)
            try:
                project=workspace.project(active_project_id)
                saved=json.loads(workspace.prompt_context(
                    "project",active_project_id,spoken,budget=620))
                evidence=saved.get("evidence",[])
                if project and project["summary"]:
                    evidence.insert(0,{"source":"conversation",
                        "when":project["updated_utc"],
                        "fact":"Stato progetto fornito dall'utente: "
                                +project["summary"][:260]})
                history=workspace.recent("project",active_project_id,3)
                earlier=[{"utente":item["utente"],"lia":item["jarvis"],
                          "tipo":item["tipo"]} for item in history]
                progress=[{"title":step["title"][:95],
                           "status":step["status"],
                           "detail":step["detail"][:110],
                           "verified":bool(step["verified"])}
                          for step in workspace.project_steps(active_project_id,limit=4)]
                return attach(json.dumps({
                    "breve":earlier+json.loads(short),
                    "progress":progress,
                    "permanente":{"related":evidence},
                },ensure_ascii=False),
                project_name=project["name"] if project else "")
            except (OSError,sqlite3.Error,WorkspaceError,ValueError) as exc:
                workspace_status.set("Ricerca progetto: "+str(exc)[:90])
                return attach(short)
        if not memory_enabled.get() or durable_brain is None:
            return attach(short)
        try:
            long=durable_brain.prompt_context(spoken,budget=530)
        except (OSError,sqlite3.Error,BrainError) as exc:
            memory_status.set("Ricerca memoria: "+str(exc)[:90])
            return attach(short)
        return attach(json.dumps({
            "breve":json.loads(short),
            "permanente":json.loads(long)},ensure_ascii=False))

    project_dialog=None

    def refresh_orbit_nodes(*, reschedule=True) -> None:
        nonlocal orbit_nodes_cache
        if closing:
            return
        items=[]
        if workspace is not None:
            try:
                projects=list(workspace.projects(active_only=True,limit=60))
                visible=projects[:33] if len(projects)>34 else projects
                items.extend({"id":p["id"],"name":p["name"],
                              "kind":"project"} for p in visible)
                if len(projects)>34:
                    items.append({"id":"projects:more","kind":"project",
                                  "name":"Altri progetti: "
                                         +str(len(projects)-33)})
                unread_items=[]
                for contact in selected_telegram_contacts()[:12]:
                    peer_id=contact["id"]
                    counts=workspace.telegram_counts(peer_id)
                    if counts["received"] or counts["replied"]:
                        unread=counts["unread"]
                        target=unread_items if unread else items
                        target.append({
                            "id":"telegram:"+str(peer_id),
                            "kind":"telegram_unread" if unread else "telegram",
                            "name":contact["name"]+
                                   " · ricevuti "+str(counts["received"])+
                                   " / risposti "+str(counts["replied"])+
                                   " / nuovi "+str(counts["unread"])})
                    notes=workspace.pending_for_contact(peer_id)
                    if notes:
                        items.append({"id":"telegram:pending:"+str(peer_id),
                                      "kind":"pending",
                                      "name":contact["name"]+
                                      " · da riferire: "+str(len(notes))})
                orbit_nodes_cache=tuple((unread_items+items)[:36])
                workspace_status.set(
                    "Progetti: "+str(len(projects))+" attivi. "
                    +"Archivi separati sul disco.")
            except (OSError,sqlite3.Error,WorkspaceError) as exc:
                workspace_status.set("Memoria progetti: "+str(exc)[:95])
        if reschedule:
            root.after(2600,refresh_orbit_nodes)

    def switch_context(project_id=None) -> bool:
        nonlocal active_project_id,conversation_epoch,pending_preference
        try:
            local_chat_active = chat_notebook.select() == str(chat_local_tab)
        except NameError:
            local_chat_active = False  # Legacy project routing remains unchanged.
        # Do not reject the existing Console->progetto change while Gemma is
        # busy; its epoch check already revokes the old reply. Only F2 local
        # chat switching is blocked during generation.
        if (busy_gpt or busy_local or document_busy
                or (local_chat_active and gemma_trial_busy[0])):
            write_line("LUMI > Finisco questa operazione prima di cambiare progetto.")
            return False
        if documents.current is not None or doc_dialog.phase != "idle":
            write_line("LUMI > Chiudi il documento di Blocco note prima di cambiare progetto.")
            speak_result("Chiudi prima il documento aperto, per non confondere i progetti.")
            return False
        if project_id is not None:
            if (workspace is None or not workspace.project(project_id)
                    or workspace.project(project_id)["trashed"]):
                write_line("LUMI > Progetto non trovato o nel cestino.")
                return False
            project=workspace.project(project_id)
        if workspace is not None:
            try:
                workspace.select_project(project_id)
            except (OSError,sqlite3.Error,WorkspaceError) as exc:
                workspace_status.set("Contesto non salvato: "+str(exc)[:100])
                return False
        active_context_label.set(
            "Contesto: "+project["name"][:35] if project_id else "Contesto: GENERALE")
        active_project_id=project_id
        # Existing project memory persists; only the opted-in chat pane
        # switches to its separate, project-scoped conversation.
        try:
            chat_view_available = (chat_sessions_panel is not None
                                   and chat_notebook.select() == str(chat_local_tab))
        except NameError:
            chat_view_available = False  # Standalone legacy route/unit harness.
        if chat_view_available:
            if not chat_sessions_panel.scope_changed():
                write_line("CHAT > Nuovo contesto non disponibile; apri Console.")
                chat_notebook.select(chat_console_tab)
        if addon_manager is not None and addon_manager._file_service is not None:
            addon_manager.file_service.reset(project_id)
        if addon_manager is not None and getattr(addon_manager,'_program_service',None) is not None:
            addon_manager.program_service.reset(project_id)
        conversation_epoch+=1
        conversation_memory.clear()
        pending_conversation.clear()
        pending_project_reference.reset()
        pending_preference=None
        write_line(
            "LUMI > "+("Progetto aperto: "+project["name"]+"."
                        if project_id else "Conversazione generale ripristinata."))
        return True

    def project_voice_command(spoken: str) -> bool:
        """Voice and typed project actions, never routed through untrusted GPT."""
        nonlocal pending_project_name, pending_project_rename_id
        nonlocal pending_project_trash_id
        if workspace is None:
            # Do not imply that an unavailable database contains zero projects.
            try:
                command = parse_project_voice(spoken)
            except ValueError:
                return False
            if command is not None:
                message = "Non riesco a leggere la memoria dei progetti. Non significa che siano spariti."
                write_line("LUMI > "+message)
                speak_result(message)
                return True
            return False

        def can_modify() -> bool:
            return (not busy_gpt and not busy_local and not document_busy
                    and documents.current is None and doc_dialog.phase=="idle")

        def acknowledge(message: str) -> bool:
            write_line("LUMI > "+message)
            speak_result(message)
            return True

        if pending_project_trash_id is not None:
            decision=project_delete_response(spoken)
            ident=pending_project_trash_id
            pending_project_trash_id=None
            if decision != "confirm":
                return acknowledge("Eliminazione annullata. Il progetto è rimasto intatto.")
            if not can_modify():
                return acknowledge("C'è un'operazione aperta: non elimino il progetto.")
            try:
                name=workspace.project(ident)["name"]
                workspace.trash_project(ident)
                if active_project_id==ident:
                    switch_context(None)
                if project_dialog is not None:
                    project_dialog.refresh()
                return acknowledge("Progetto "+name+
                    " spostato nel cestino interno. I suoi file e la memoria restano recuperabili.")
            except (OSError,sqlite3.Error,WorkspaceError,TypeError) as exc:
                return acknowledge("Non riesco a spostare il progetto nel cestino: "+str(exc)[:100])

        if pending_project_rename_id is not None:
            ident=pending_project_rename_id
            pending_project_rename_id=None
            if spoken.casefold().strip(" ,.!?") in ("annulla","lascia stare","niente"):
                return acknowledge("Rinomina annullata.")
            try:
                name=safe_project_name(re.sub(
                    r"^(?:(?:ehi|hey|ok)\s+)?jarvis[\s,.:;-]+","",
                    spoken.strip(),flags=re.I))
                command_action="rename"
                target_ident=ident
            except ValueError:
                pending_project_rename_id=ident
                return acknowledge("Quale nome preciso vuoi dare a questo progetto?")
        elif pending_project_name:
            pending_project_name = False
            if spoken.casefold().strip(" ,.!?") in ("annulla","lascia stare","niente"):
                return acknowledge("Creazione del progetto annullata.")
            try:
                name=safe_project_name(re.sub(
                    r"^(?:(?:ehi|hey|ok)\s+)?jarvis[\s,.:;-]+","",
                    spoken.strip(),flags=re.I))
                command_action="create"
                target_ident=None
            except ValueError:
                pending_project_name=True
                return acknowledge("Quale nome preciso vuoi dare al nuovo progetto?")
        else:
            try:
                command=parse_project_voice(spoken)
            except ValueError as exc:
                return acknowledge(str(exc))
            if command is None:
                return False
            pending_project_reference.reset()
            command_action=command.action
            name=command.name
            target_ident=None

        if command_action=="list":
            try:
                projects=workspace.projects(limit=200)
                if projects:
                    names=", ".join(p["name"] for p in projects[:12])
                    remaining=len(projects)-min(len(projects),12)
                    message="Progetti salvati: "+names+(
                        ". E altri "+str(remaining)+" nell'elenco." if remaining else ".")
                else:
                    message="Nel database attuale non risultano progetti. Controlla la cartella dati di Lumi."
            except (OSError,sqlite3.Error,WorkspaceError):
                message="Non riesco a consultare l'archivio dei progetti; non vuol dire che siano cancellati."
        elif command_action=="list_trash":
            projects=workspace.trashed_projects(limit=200)
            message=("Nel cestino ci sono: "+", ".join(x["name"] for x in projects[:12])
                     if projects else "Il cestino dei progetti è vuoto.")
        elif command_action=="create":
            if not name:
                pending_project_name=True
                message="Come vuoi chiamare il nuovo progetto?"
            elif not can_modify():
                message="Finisci prima l'operazione o chiudi il documento aperto."
            else:
                try:
                    existing=find_existing_project(workspace.projects(limit=200),name)
                    if existing:
                        message="Il progetto "+existing["name"]+" esiste già. Dimmi di aprirlo."
                    else:
                        ident=workspace.create_project(name)
                        if switch_context(ident):
                            message="Creato e aperto il progetto "+name+". Memoria e cartella pronte."
                        else:
                            message="Progetto creato; non riesco ad aprirlo ora."
                except (OSError,sqlite3.Error,WorkspaceError,ValueError) as exc:
                    message="Impossibile creare il progetto: "+str(exc)[:110]
        elif command_action=="rename":
            if not can_modify():
                message="Finisci prima l'operazione o chiudi il documento aperto."
            else:
                try:
                    if target_ident is None:
                        target_ident=active_project_id
                        if command.target:
                            target=find_existing_project(workspace.projects(limit=200),
                                                         command.target)
                            target_ident=target["id"] if target else None
                    project=workspace.project(target_ident) if target_ident else None
                    if project is None or project["trashed"]:
                        message=("Non trovo quel progetto. Dimmi 'elenca i progetti' "
                                 "o selezionalo dal gestore.")
                    elif not name:
                        pending_project_rename_id=project["id"]
                        message="Qual è il nuovo nome del progetto "+project["name"]+"?"
                    else:
                        old_name=project["name"]
                        workspace.rename_project(project["id"],name)
                        if active_project_id==project["id"]:
                            active_context_label.set("Contesto: "+name[:35])
                        if project_dialog is not None:
                            project_dialog.refresh()
                        message=("Progetto rinominato da "+old_name+" a "+name+
                                 ". Cartella e memoria sono rimaste le stesse.")
                except (OSError,sqlite3.Error,WorkspaceError,ValueError) as exc:
                    message="Rinomina non riuscita: "+str(exc)[:110]
        elif command_action=="trash":
            if not can_modify():
                message="Finisci prima l'operazione o chiudi il documento aperto."
            else:
                try:
                    selected=(find_existing_project(workspace.projects(limit=200),name)
                              if name else workspace.project(active_project_id)
                              if active_project_id else None)
                    if selected is None or selected["trashed"]:
                        message="Non trovo il progetto. Chiedimi di elencare quelli salvati."
                    else:
                        pending_project_trash_id=selected["id"]
                        message=("Vuoi eliminare il progetto "+selected["name"]+
                                 " dall'elenco? La memoria e i documenti resteranno "
                                 "nel cestino recuperabile. Di' 'confermo' oppure 'annulla'.")
                except (OSError,sqlite3.Error,WorkspaceError,ValueError) as exc:
                    message="Non riesco a preparare l'eliminazione: "+str(exc)[:110]
        elif command_action=="restore":
            if not can_modify():
                message="Finisci prima l'operazione o chiudi il documento aperto."
            else:
                try:
                    selected=find_existing_project(workspace.trashed_projects(limit=200),name)
                    if selected:
                        workspace.restore_project(selected["id"])
                        if project_dialog is not None:
                            project_dialog.refresh()
                        message="Ripristinato il progetto "+selected["name"]+". Memoria e file conservati."
                    else:
                        message="Non trovo il progetto "+name+" nel cestino."
                except (OSError,sqlite3.Error,WorkspaceError,ValueError) as exc:
                    message="Ripristino non riuscito: "+str(exc)[:110]
        elif command_action=="open":
            try:
                selected=find_existing_project(workspace.projects(limit=200),name)
                if selected and switch_context(selected["id"]):
                    message="Ripreso il progetto "+selected["name"]+"."
                elif selected:
                    message="Non posso cambiare progetto durante un'operazione."
                else:
                    message="Non trovo "+name+" tra i progetti salvati. Prova 'elenca i progetti'."
            except (OSError,sqlite3.Error,WorkspaceError,ValueError) as exc:
                message="Impossibile aprire il progetto: "+str(exc)[:105]
        elif command_action=="general":
            message=("Sono tornato alla conversazione generale."
                     if switch_context(None) else
                     "Non posso cambiare contesto finché il documento è aperto.")
        elif command_action=="folder":
            if active_project_id is None:
                message="Apri un progetto prima di chiedermi la sua cartella."
            else:
                try:
                    folder=workspace.project_directory(active_project_id)
                    if os.name=="nt":
                        os.startfile(str(folder))
                        message="Ho aperto la cartella del progetto."
                    else:
                        message="Cartella del progetto: "+str(folder)
                except (OSError,WorkspaceError) as exc:
                    message="Non riesco ad aprire la cartella: "+str(exc)[:100]
        else:
            return False
        return acknowledge(message)

    def handle_project_reference(spoken: str) -> bool:
        """Resolve 'questo progetto' only from selected scope or one answer."""
        if workspace is None:
            return False
        waiting=pending_project_reference.question
        if waiting:
            cleaned=normalized_utterance(spoken)
            if cleaned.casefold() in ("annulla","niente","lascia stare","no"):
                pending_project_reference.reset()
                write_line("LUMI > Chiarimento annullato.")
                speak_result("Chiarimento annullato.")
                return True
            # A fresh full command supersedes the old question; never replay it.
            try:
                if parse_project_voice(spoken) is not None:
                    pending_project_reference.reset()
                    return False
            except ValueError:
                pending_project_reference.reset()
                return False
            name=pending_project_reference.parse_answer(spoken)
            if name is None:
                pending_project_reference.reset()
                return False
            try:
                name=re.sub(r"^(?:il\s+)?progetto\s+","",name,flags=re.I)
                match=find_existing_project(workspace.projects(limit=200),name)
                if match is None:
                    message=("Non trovo un progetto salvato con quel nome. "
                             "Quale progetto esistente intendi?")
                    write_line("LUMI > "+message)
                    speak_result(message)
                    return True
                # The answer explicitly chooses the target requested by Jarvis.
                original=waiting
                if not switch_context(match["id"]):
                    pending_project_reference.reset()
                    return True
                write_line("LUMI > Riferimento risolto: progetto "+match["name"]+".")
                if gpt_enabled.get() and active_gpt and not busy_gpt:
                    # Resume the previous READ-ONLY question in *chat* mode,
                    # never via the executor or an old capability intent.
                    try:
                        prompt=build_chat_prompt(
                            original,memory_context=recent_memory_for_gpt(original))
                        if run_gpt("ask",prompt=prompt,source=original,
                                   consent_detail="La domanda precedente e il contesto del progetto selezionato."):
                            return True
                    except ValueError:
                        pass
                steps=workspace.project_steps(match["id"],limit=1)
                last=(" Ultima attività: "+steps[0]["title"]+
                      ", stato "+steps[0]["status"]+".") if steps else (
                      " Nessuna attività ancora registrata.")
                message="Progetto "+match["name"]+" selezionato."+last
                write_line("LUMI > "+message)
                speak_result(message)
                return True
            except (OSError,sqlite3.Error,WorkspaceError,ValueError) as exc:
                pending_project_reference.reset()
                message="Non riesco a consultare il progetto: "+str(exc)[:100]
                write_line("LUMI > "+message)
                speak_result(message)
                return True
        if pending_project_reference.start_if_needed(
                spoken,selected=active_project_id is not None):
            message="Quale progetto salvato vuoi aprire per risponderti?"
            write_line("LUMI > "+message)
            speak_result(message)
            return True
        return False

    def handle_unanchored_short_reply(spoken: str) -> bool:
        """Never pretend an isolated yes/no confirms a stale action."""
        if try_gemma_app_followup(spoken):
            return True
        if (not is_ambiguous_short_reply(spoken)
                or conversation_memory.last_question()):
            return False
        message="A quale domanda ti riferisci?"
        write_line("LUMI > "+message)
        speak_result(message)
        remember_exchange(spoken,message,"clarify")
        return True

    def preference_command(spoken: str) -> bool:
        """Only an explicitly confirmed request can change preference records."""
        nonlocal pending_preference
        if pending_preference is not None:
            answer=normalized_utterance(spoken).casefold()
            intent=pending_preference
            pending_preference=None
            if answer=="confermo":
                if preference_store is None:
                    message="Preferenze non disponibili; nessuna modifica."
                else:
                    try:
                        if intent.kind=="remove":
                            preference_store.remove(intent.key,user_confirmed=True)
                            message="Preferenza rimossa."
                        else:
                            preference_store.set(intent.key,intent.value,
                                                 user_confirmed=True)
                            message="Preferenza confermata e salvata."
                    except (OSError,sqlite3.Error,MemoryBoundaryError) as exc:
                        message="Preferenza non salvata: "+str(exc)[:90]
                write_line("LUMI > "+message)
                speak_result(message)
                return True
            if answer in ("annulla","no","lascia stare","non salvare"):
                write_line("LUMI > Preferenza non salvata.")
                speak_result("Preferenza non salvata.")
                return True
            # A new topic cancels stale pending consent.
        intent=parse_preference_intent(spoken)
        if intent is None:
            return False
        if preference_store is None:
            message="Archivio preferenze non disponibile."
        elif intent.kind=="list":
            try:
                rows=preference_store.all()
                message=("Preferenze confermate: "+
                         ", ".join(p["key"]+"="+p["value"] for p in rows)
                         if rows else "Nessuna preferenza confermata.")
            except (OSError,sqlite3.Error):
                message="Impossibile leggere le preferenze."
        elif intent.kind=="unsupported":
            message="Posso ricordare solo preferenze su risposte, lingua o interazione."
        else:
            pending_preference=intent
            message=("Vuoi "+("rimuovere" if intent.kind=="remove" else "salvare")+
                     " la preferenza "+intent.key+
                     ("="+intent.value if intent.value else "")+
                     "? Di' confermo oppure annulla.")
        write_line("LUMI > "+message)
        speak_result(message)
        return True

    def snapshot_runtime_evidence():
        """Sample actual local objects without making a GPT call or opening a mic.

        Runs only on Tk main thread after the source audit has completed.
        Source inspection stays on its existing isolated worker.
        """
        return collect_runtime_evidence(
            gpt_enabled=bool(gpt_enabled.get()),
            gpt_connected=bool(active_gpt),
            sdk_installed=service.installed_sdk().is_file(),
            node_available=bool(shutil.which("node")),
            bridge_file_present=(Path(__file__).resolve().parent
                                 / "gpt_bridge.mjs").is_file(),
            bridge_running=service.bridge_running(),
            voice_present=voice is not None,
            voice_mode=voice_mode.get(),
            voice_listening=voice.is_listening() if voice is not None else False,
            voice_model_present=(voice.model_dir.is_dir()
                                 if voice is not None else False),
            local_engine_present=engine is not None,
            local_store_present=(engine.db_path.is_file()
                                 if engine is not None else False),
            workspace_present=workspace is not None,
            workspace_store_present=(workspace.path.is_file()
                                     if workspace is not None else False),
            counters=runtime_events,
        )

    def snapshot_services_report():
        from runtime_diagnostics import format_service_report, RuntimeEvidence
        import importlib.util
        import shutil
        try:
            evidence = snapshot_runtime_evidence()
        except Exception:
            # One unavailable observation must not hide Telegram's journal.
            evidence = RuntimeEvidence((), ())
        current = gemma_session[0]
        try:
            state = "non_loaded" if current is None else "busy" if current.is_busy else "ready"
        except (RuntimeError, AttributeError):
            state = "unavailable"
        bridge = telegram_bridge
        try:
            telegram = bridge.diagnostic_snapshot() if bridge is not None else None
        except (RuntimeError, AttributeError):
            telegram = None
        try:
            telethon = importlib.util.find_spec("telethon") is not None
        except (ImportError, ValueError):
            telethon = None
        report = format_service_report(evidence, telegram=telegram,
            automatic=bool(telegram_auto.get()), credentials=credentials_present(),
            contacts=len(selected_telegram_contacts()),
            selected="GPT" if gpt_enabled.get() else "Gemma", gemma=state,
            memory=bool(memory_enabled.get()),
            telethon=telethon,
            ffmpeg=shutil.which("ffmpeg") is not None)
        if not evidence.checks:
            report += "\nStato generale parzialmente non disponibile; registro Telegram separato."
        return report

    def open_service_diagnostics():
        from runtime_diagnostics_ui import ServiceDiagnosticsWindow
        current = getattr(root, "_jarvis_services_diagnostic", None)
        if current is not None and current.window.winfo_exists():
            current.refresh()
            current.window.deiconify()
            current.window.lift()
            return
        root._jarvis_services_diagnostic = ServiceDiagnosticsWindow(
            settings_window, get_report=snapshot_services_report)

    def offer_external_diagnostic_review() -> bool:
        """Explicitly confirm sending *redacted findings*, not local files."""
        if last_diagnostic_audit is None:
            write_line("DIAGNOSTICA > Prima esegui l'autodiagnosi locale.")
            speak_result("Prima devo eseguire l'autodiagnosi locale.")
            return True
        if not gpt_enabled.get() or not active_gpt:
            write_line("DIAGNOSTICA > Rapporto locale disponibile. "
                       "Per la valutazione esterna devi collegare GPT.")
            speak_result("Il rapporto locale è pronto, ma GPT non è collegato.")
            return True
        if busy_gpt:
            write_line("DIAGNOSTICA > GPT sta già rispondendo; "
                       "non ho inviato nessun dato.")
            return True
        consent_epoch = conversation_epoch
        from local_model.online_permissions import authorize_online_request
        def confirm_review():
            return messagebox.askyesno(
                "LUMI — valutazione esterna",
                "Vuoi inviare al GPT collegato soltanto un rapporto tecnico "
                "ridotto dell'autodiagnosi?\n\n"
                "Contiene: file sorgenti RELATIVI, righe, segnali statici, "
                "stati osservati dei componenti e CONTEGGI ANONIMI delle operazioni.\n"
                "NON contiene codice completo, credenziali, documenti, "
                "log di sistema, percorsi personali né dati dei progetti.\n"\
                "Gli errori contati riguardano solo questa istanza.\n\n"
                "È un'analisi di possibili miglioramenti, NON una verifica "
                "del corretto funzionamento e non autorizza modifiche.",
                parent=root, default="no")
        permission = authorize_online_request("diagnostics.review", confirm=confirm_review)
        approved = permission is not None
        approved = approved and consent_epoch == conversation_epoch
        if not approved:
            write_line("DIAGNOSTICA > Invio al modello esterno annullato. "
                       "Il rapporto locale è conservato.")
            return True
        try:
            snapshot={
                "gpt_bridge":"available" if active_gpt else "not_tested",
                "voice_engine":"available" if voice is not None else "not_tested",
                "local_engine":"available" if engine is not None else "not_tested",
                "projects":"available" if workspace is not None else "not_tested",
            }
            try:
                history=(operation_ledger.recent(limit=20)
                         if operation_ledger is not None else ())
                outcomes=summarize_operation_outcomes(history)
            except (OSError,sqlite3.Error,MemoryBoundaryError):
                outcomes=summarize_operation_outcomes(())
            prompt=build_external_review_prompt(
                last_diagnostic_audit,snapshot,outcomes,last_runtime_evidence)
        except (ValueError,TypeError) as exc:
            write_line("DIAGNOSTICA > Non posso preparare il rapporto: "
                       +str(exc)[:140])
            return True
        write_line("DIAGNOSTICA > Consenso ricevuto. Invio SOLO metadati "
                   "della diagnosi locale al GPT esterno per suggerimenti.")
        run_gpt("ask",prompt=prompt,source="",
                capability="diagnostics.review",permission=permission)
        return True

    def update_diagnostic_ui() -> None:
        """Only show understated progress while the actual audit is active."""
        snapshot=diagnostic_session.snapshot()
        diagnostic_percent.set(snapshot.progress_percent)
        if snapshot.active:
            amount=(f"{snapshot.completed}/{snapshot.total}"
                    if snapshot.total else "preparazione")
            diagnostic_status.set(
                f"DIAGNOSI · {snapshot.phase[:16]} {amount}")
            if not diagnostic_row.winfo_manager():
                # Always stay above the input, never cover chat or actions.
                diagnostic_row.pack(fill="x",pady=(0,3),before=input_row)
        else:
            diagnostic_status.set("Autodiagnosi: "+snapshot.phase)
            if diagnostic_row.winfo_manager():
                diagnostic_row.pack_forget()
        draw_diagnostic_meter()
        diagnostic_cancel_button.configure(
            state="normal" if snapshot.active else "disabled")

    def cancel_diagnostic() -> None:
        """Stop waiting, revoke external consent and reject late results."""
        nonlocal diagnostic_busy,pending_external_review,last_runtime_evidence
        old_run=diagnostic_session.cancel()
        if old_run is None:
            return
        diagnostic_busy=False
        pending_external_review=False
        last_runtime_evidence=None
        update_diagnostic_ui()
        write_line("DIAGNOSTICA > Richiesta #"+str(old_run)+
                   " annullata nell'interfaccia. Il worker potrebbe "
                   "terminare dopo; i suoi risultati saranno ignorati.")
        speak_result("Ho annullato l'attesa della diagnosi. "
                     "Nessun file è stato modificato.")

    def try_self_diagnostic(spoken: str) -> bool:
        """Local bounded audit, visible progress and recoverable worker errors."""
        nonlocal diagnostic_busy,pending_external_review,last_diagnostic_audit,last_runtime_evidence
        if is_external_review_request(spoken):
            return offer_external_diagnostic_review()
        request_kind=diagnostic_request(spoken)
        if request_kind is None:
            return False
        mode,module=request_kind
        if mode=="services":
            open_service_diagnostics()
            return True
        if mode=="paths":
            source=Path(__file__).resolve().parent
            data=(workspace.path.parent if workspace is not None
                  else default_path().parent)
            message=("Programma: "+str(source)+
                     ". Archivio dei dati: "+str(data)+
                     ". I file personali e le credenziali non vengono analizzati.")
            write_line("DIAGNOSTICA > "+message)
            speak_result("Conosco le cartelle del mio programma e dei dati. Le ho mostrate nel registro.")
            return True
        if diagnostic_session.active:
            snapshot=diagnostic_session.snapshot()
            message=("La diagnosi locale è nella fase "+snapshot.phase+
                     " ("+str(snapshot.completed)+"/"+str(snapshot.total)+
                     " file, "+str(snapshot.elapsed_seconds)+
                     " secondi). Lo stato è visibile sotto la console.")
            write_line("DIAGNOSTICA > "+message)
            speak_result(message)
            return True
        # A previous timed-out worker may still be alive; never spawn an
        # unlimited number of workers against the same install directory.
        diagnostic_threads[:]=[t for t in diagnostic_threads if t.is_alive()]
        if len(diagnostic_threads)>=2:
            message=("Due analisi precedenti non rispondono ancora. "
                     "Non avvio altri controlli; chiudi e riapri Lumi.")
            diagnostic_status.set("Autodiagnosi: processi non responsivi")
            write_line("DIAGNOSTICA > "+message)
            speak_result(message)
            return True
        run_id=diagnostic_session.start()
        if run_id is None:
            return True
        # A new attempt invalidates the previous report; GPT must never
        # review outdated findings as though they belonged to this run.
        last_diagnostic_audit=None
        last_runtime_evidence=None
        diagnostic_busy=True
        pending_external_review=(mode=="review" and wants_external_advice(spoken))
        write_line("DIAGNOSTICA > Avvio controllo locale #"+str(run_id)+
                   ": inventario, verifica sintattica, consigli AST.")
        update_diagnostic_ui()

        def worker() -> None:
            def report(phase: str, completed: int, total: int) -> None:
                output_queue.put(("self_audit_progress",
                                  run_id,phase,completed,total))
            try:
                data=(workspace.path.parent if workspace is not None
                      else default_path().parent)
                audit=inspect_jarvis(
                    source_root=Path(__file__).resolve().parent,
                    data_root=data,module=module if mode=="module" else "",
                    progress=report)
            except Exception as exc:
                # Unexpected TypeError/IndexError/PermissionError must also
                # end the diagnostic rather than leave 'busy' stuck forever.
                # Exception type is enough for debugging, no path/secret leak.
                output_queue.put(("self_audit_error",run_id,
                                  exc.__class__.__name__))
            else:
                output_queue.put(("self_audit",run_id,audit))
        thread=threading.Thread(target=worker,daemon=True,
                                name="jarvis-static-audit-"+str(run_id))
        try:
            thread.start()
        except RuntimeError as exc:
            diagnostic_session.finish(run_id,succeeded=False)
            diagnostic_busy=False
            pending_external_review=False
            write_line("DIAGNOSTICA > Impossibile avviare il controllo: "
                       +exc.__class__.__name__)
            update_diagnostic_ui()
            return True
        diagnostic_threads.append(thread)
        return True

    def open_project_manager():
        nonlocal project_dialog
        if workspace is None:
            messagebox.showwarning(
                "Progetti","Memoria progetti non disponibile.",parent=root)
            return
        if project_dialog is None:
            def renamed_project(ident,name):
                if active_project_id==ident:
                    active_context_label.set("Contesto: "+name[:35])
            def trashed_project(ident):
                if active_project_id==ident:
                    switch_context(None)
            project_dialog=ProjectManagerWindow(
                root,workspace,switch_context,
                lambda:switch_context(None),lambda:None,
                can_modify=lambda:(not busy_gpt and not busy_local and
                                   not document_busy and documents.current is None
                                   and doc_dialog.phase=="idle"),
                on_renamed=renamed_project,on_trashed=trashed_project)
        project_dialog.show()

    def telegram_activity_window(peer_id:int=0) -> None:
        allowed={c["id"]:c["name"] for c in selected_telegram_contacts()}
        if workspace is None or peer_id not in allowed:
            return
        win=tk.Toplevel(root)
        win.title("LUMI // Telegram — "+allowed[peer_id])
        win.geometry("640x420")
        log=tk.Text(win,wrap="word",bg="#031522",fg="#d7f6ff",
                    padx=12,pady=8)
        log.pack(fill="both",expand=True)
        try:
            records=workspace.telegram_activity(peer_id,limit=50)
            for item in reversed(records):
                direction=("RICEVUTO" if item["direction"]=="incoming"
                           else "LUMI HA RISPOSTO")
                log.insert("end",item["when"]+"  "+direction
                           +" ["+item["kind"]+"]\n"
                           +item["text"]+"\n\n")
            displayed_ids=[item["message_id"] for item in records
                           if item["direction"]=="incoming"]
            workspace.mark_telegram_read(peer_id, displayed_ids)
            refresh_orbit_nodes(reschedule=False)
        except (OSError,sqlite3.Error,WorkspaceError) as exc:
            log.insert("end","Archivio Telegram non leggibile: "+str(exc)[:100])
        log.configure(state="disabled")

    def orbit_open(identifier:str) -> None:
        if identifier.startswith("telegram:"):
            parts=identifier.split(":")
            if len(parts)==3 and parts[1]=="pending":
                write_line("TELEGRAM > Messaggi da riferire ancora in attesa.")
            try:
                peer_id=int(parts[-1])
            except ValueError:
                return
            telegram_activity_window(peer_id)
        elif identifier=="projects:more":
            open_project_manager()
        else:
            switch_context(identifier)

    def queue_telegram_note(message:str) -> bool:
        chosen=selected_telegram_contacts()
        if len(chosen)!=1 or workspace is None:
            write_line("TELEGRAM > Il vecchio promemoria usa un solo destinatario. "
                       "Per scegliere tra più contatti usa 'Invia messaggio vocale'.")
            return False
        peer_id=chosen[0]["id"]
        try:
            workspace.note_for_contact(peer_id,message)
        except (OSError,sqlite3.Error,WorkspaceError) as exc:
            write_line("LUMI > Non posso salvare il messaggio: "+str(exc)[:100])
            return False
        write_line("LUMI > Messaggio memorizzato per "
                   +chosen[0]["name"]
                   +". Lo riferirò al prossimo contatto, se Telegram è attivo.")
        return True

    def leave_telegram_note_dialog() -> None:
        if not settings.get("telegram_peer_id"):
            telegram_status.set("Configura prima il contatto autorizzato.")
            return
        message=simpledialog.askstring(
            "LUMI / Telegram",
            "Che cosa devo riferire al contatto autorizzato?",
            parent=root)
        if message:
            queue_telegram_note(message)

    def maybe_queue_telegram_note(message:str) -> bool:
        chosen=selected_telegram_contacts()
        if len(chosen)!=1:
            return False
        parsed=explicit_telegram_note(message,chosen[0]["name"])
        if parsed is None:
            return False
        queue_telegram_note(parsed)
        return True

    def selected_telegram_contacts() -> list[dict]:
        return [c for c in settings.get("telegram_contacts", [])
                if c.get("enabled") is True]

    def current_capability_snapshot(has_document:bool=False) -> dict:
        """Re-evaluate runtime permissions on every external GPT request."""
        if addon_manager is not None:
            try:
                addon_manager.refresh()
            except (AddonError,OSError,ValueError):
                # Fail closed: do not claim stale addon actions are available.
                for binding in addon_capability_registry.available_addons():
                    addon_capability_registry.unregister(binding["id"])
        try:
            stream=voice.is_listening()
        except (AttributeError,RuntimeError,OSError):
            stream=False
        return snapshot_capabilities(
            settings=settings,
            has_document=has_document,
            telegram_credentials=credentials_present(),
            telegram_voice_dependencies=(not missing_voice_dependencies()),
            voice_stream_open=stream,
            registry=addon_capability_registry)

    def open_addon_settings() -> None:
        nonlocal addon_settings_window
        if addon_manager is None:
            messagebox.showerror(
                "Add-on Lumi",
                "Archivio add-on non disponibile: "+addon_setup_error,parent=root)
            return
        if (addon_settings_window is not None
                and addon_settings_window.exists()):
            addon_settings_window.focus()
            return
        addon_settings_window=AddonSettingsWindow(
            root,addon_manager,
            on_change=lambda: write_line(
                "ADD-ON > Registro aggiornato. Le capacità attive saranno "
                "comunicate al GPT alla prossima richiesta."))

    def active_addon_actions() -> tuple[dict,...]:
        if addon_manager is None:
            return ()
        try:
            return addon_manager.active_actions()
        except (AddonError,OSError,ValueError,ImportError):
            # Never let a broken or modified add-on directory break GPT chat.
            for item in addon_capability_registry.available_addons():
                addon_capability_registry.unregister(item["id"])
            return ()

    def load_telegram_contacts_for_ui() -> None:
        """Read real Telegram private users on a worker, never on Tk."""
        if not credentials_present():
            output_queue.put(("telegram_contacts_error",
                              "Prima configura l'account Telegram."))
            return
        def worker() -> None:
            try:
                rows=list_telegram_contacts()
                output_queue.put(("telegram_contacts_loaded",rows))
            except Exception as exc:
                output_queue.put(("telegram_contacts_error",type(exc).__name__))
        threading.Thread(target=worker,daemon=True,
                         name="jarvis-telegram-contact-list").start()

    def save_telegram_contact_selection(rows:list[dict]) -> bool:
        """Explicit checklist save; disable old auto listener before switching."""
        nonlocal telegram_bridge
        if normalize_telegram_contacts(rows) != rows:
            messagebox.showwarning("Telegram","Selezione non valida.",parent=root)
            return False
        previous=settings.copy()
        chosen=[c for c in rows if c["enabled"]]
        settings["telegram_contacts"]=rows
        settings["telegram_peer_id"]=(chosen[0]["id"] if len(chosen)==1 else 0)
        settings["telegram_contact_name"]=(chosen[0]["name"] if len(chosen)==1 else "")
        settings["telegram_enabled"]=False
        try:
            save_settings(settings)
        except (OSError,ValueError) as exc:
            settings.update(previous)
            messagebox.showerror("Telegram","Non posso salvare la selezione: "
                                 +str(exc)[:120],parent=root)
            return False
        if telegram_bridge:
            telegram_bridge.stop()
            telegram_bridge=None
        telegram_auto.set(False)
        telegram_voice_dialog.reset()
        telegram_status.set(
            f"Telegram: {len(chosen)} contatti autorizzati. "
            "Risposte automatiche spente; riattivale se vuoi.")
        write_line("TELEGRAM > Selezione contatti aggiornata; "
                   "risposte automatiche disattivate per sicurezza.")
        return True

    def open_telegram_history(peer_id:int) -> None:
        allowed={c["id"]:c["name"] for c in selected_telegram_contacts()}
        if workspace is None or peer_id not in allowed:
            messagebox.showwarning("Telegram","Contatto non autorizzato.",
                                   parent=root)
            return
        try:
            path=workspace.telegram_export_history(peer_id,allowed[peer_id])
            if os.name=="nt":
                os.startfile(str(path))
            else:
                webbrowser.open(path.as_uri())
        except (OSError,sqlite3.Error,WorkspaceError) as exc:
            messagebox.showerror("Telegram",
                "Non posso aprire la conversazione: "+str(exc)[:150],parent=root)

    def clear_telegram_history(peer_id:int) -> None:
        allowed={c["id"]:c["name"] for c in selected_telegram_contacts()}
        if workspace is None or peer_id not in allowed:
            messagebox.showwarning("Telegram","Contatto non autorizzato.",
                                   parent=root)
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
                parent=root,default="no"):
            return
        # Never delete a peer's active events while the listener is still
        # handling that contact. User explicitly approved disabling Telegram.
        if telegram_bridge and telegram_bridge.is_enabled():
            telegram_auto.set(False)
            toggle_telegram_automatic()
        try:
            workspace.telegram_clear_history(peer_id)
        except (OSError,sqlite3.Error,WorkspaceError) as exc:
            messagebox.showerror("Telegram",
                "Non posso cancellare la cronologia: "+str(exc)[:150],
                parent=root)
            return
        messagebox.showinfo("Telegram",
                            "Cronologia locale cancellata per "+
                            allowed[peer_id]+".",parent=root)

    def edit_telegram_contact_profile(parent, peer_id: int) -> None:
        contact = next((row for row in selected_telegram_contacts()
                        if row["id"] == peer_id), None)
        if contact is None:
            messagebox.showwarning("Telegram", "Contatto non autorizzato.", parent=parent)
            return
        key = str(peer_id)
        profiles = settings.get("telegram_contact_profiles", {}).copy()
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
            save_settings({**settings, "telegram_contact_profiles": profiles})
        except (OSError, ValueError):
            messagebox.showerror("Telegram", "Impossibile salvare il contesto.", parent=parent)
            return
        settings["telegram_contact_profiles"] = profiles

    def open_telegram_contact_list() -> None:
        nonlocal telegram_contacts_dialog
        if (telegram_contacts_dialog is not None
                and telegram_contacts_dialog.exists()):
            telegram_contacts_dialog.focus()
            return
        telegram_contacts_dialog=TelegramContactsWindow(
            root,settings.get("telegram_contacts",[]),
            load_telegram_contacts_for_ui,save_telegram_contact_selection,
            on_open_history=open_telegram_history,
            on_clear_history=clear_telegram_history,
            on_edit_context=edit_telegram_contact_profile)

    def send_owner_telegram_voice(peer_id:int,name:str,message:str) -> bool:
        """Explicit owner-initiated, one-shot OGG/Opus send; no GPT needed."""
        nonlocal telegram_owner_busy
        if closing or telegram_owner_busy:
            write_line("TELEGRAM > Invio già in corso oppure Lumi in chiusura.")
            speak_result("Invio Telegram già in corso.")
            return False
        contact=next((c for c in selected_telegram_contacts()
                      if c["id"]==peer_id),None)
        if contact is None or not credentials_present():
            write_line("TELEGRAM > Contatto non selezionato o account non configurato.")
            speak_result("Questo contatto non è autorizzato o Telegram non è collegato.")
            return False
        if not isinstance(message,str) or not 1<=len(message.strip())<=480:
            write_line("TELEGRAM > Messaggio non valido: massimo 480 caratteri.")
            return False
        missing=missing_voice_dependencies()
        if missing:
            write_line("TELEGRAM > Mancano "+", ".join(missing)+". Nessun invio.")
            return False
        telegram_owner_busy=True
        voice_snapshot=selected_voice()
        written=message.strip()
        def worker() -> None:
            try:
                msg_id=send_telegram_voice(
                    peer_id,written,voice_snapshot,
                    still_authorized=lambda: (
                        not closing and any(
                            c.get("id")==peer_id and c.get("enabled") is True
                            for c in settings.get("telegram_contacts",[]))))
                output_queue.put(("telegram_owner_sent",peer_id,name,msg_id,written))
            except Exception as exc:
                # Never auto-retry: a network timeout may follow acceptance.
                output_queue.put(("telegram_owner_error",type(exc).__name__,
                                  str(exc)[:160]))
        threading.Thread(target=worker,daemon=True,
                         name="jarvis-telegram-owner-send").start()
        write_line("TELEGRAM > Invio vocale richiesto per "+name+
                   "; attendo la ricevuta effettiva.")
        return True

    def open_telegram_manual_send() -> None:
        show_telegram_manual_send(root,selected_telegram_contacts(),
                                  send_owner_telegram_voice)

    def try_telegram_voice_send(spoken:str) -> bool:
        """Owner-only, local two-turn command; Telegram incoming never reaches here."""
        requested=parse_telegram_send_intent(spoken)
        if telegram_voice_dialog.pending:
            action=telegram_voice_dialog.receive(
                spoken,settings.get("telegram_contacts",[]))
        elif requested is not None:
            status,contact=resolve_selected_recipient(
                requested,settings.get("telegram_contacts",[]))
            if status!="ok":
                message=("Trovo più contatti con questo nome. "
                         "Usa il nome completo nelle impostazioni."
                         if status=="ambiguous" else
                         "Non trovo un contatto Telegram selezionato con quel nome.")
                write_line("TELEGRAM > "+message)
                speak_result(message)
                return True
            action=telegram_voice_dialog.begin(contact)
        else:
            return False
        if action.kind=="ask_message":
            message="Che messaggio vuoi mandare a "+action.name+"?"
            write_line("LUMI > "+message)
            speak_result(message)
        elif action.kind=="ask_confirm":
            write_line("TELEGRAM > Bozza per "+action.name+": "+action.message)
            speak_result("Ho preparato il messaggio per "+action.name+
                         ". Vuoi inviarlo come vocale? Di' confermo o annulla.")
        elif action.kind=="send":
            send_owner_telegram_voice(action.peer_id,action.name,action.message)
        elif action.kind in ("cancelled","expired","revoked"):
            write_line("TELEGRAM > Invio annullato: "+action.kind+".")
            speak_result("Messaggio Telegram non inviato.")
        elif action.kind=="invalid_message":
            speak_result("Il messaggio deve avere da uno a 480 caratteri. Riprova.")
        return True

    def set_telegram_gpt_session(enabled: bool) -> None:
        nonlocal telegram_gpt_session_token
        telegram_gpt_session_token = object() if enabled and gpt_enabled.get() else None
        telegram_gpt_session_choice.set(telegram_gpt_session_token is not None)

    def ask_telegram_gpt(prompt: str, bridge: TelegramBridge) -> str:
        # The worker reads only runtime state. Tk is used on the UI thread.
        approved_epoch = conversation_epoch
        session_token = telegram_gpt_session_token
        if not telegram_gpt_ready.is_set() or not bridge.is_enabled():
            return ""
        from local_model.online_permissions import authorize_online_request

        def request_consent():
            nonlocal approved_epoch
            approval = Future()
            output_queue.put(("telegram_gpt_consent", bridge, approval))
            try:
                approved_epoch = approval.result(timeout=30)
            except TimeoutError:
                approval.cancel()
                return False
            return approved_epoch is not None

        permission = authorize_online_request(
            "telegram.compose", confirmed=session_token is not None,
            confirm=request_consent)
        if permission is None:
            return ""

        def authorized():
            return (permission() and approved_epoch == conversation_epoch and telegram_gpt_ready.is_set()
                    and bridge.is_enabled()
                    and (session_token is None or session_token is telegram_gpt_session_token))
        if not authorized():
            return ""
        try:
            result = service.call("ask", prompt=prompt, timeout=120,
                                  authorize_send=authorized)
            return str(result.get("text", "")) if authorized() else ""
        except (GPTUnavailable, OSError, RuntimeError):
            return ""

    def ask_telegram_reply(message, context, bridge, peer_id=None):
        if not bridge.is_enabled():
            return ""
        if settings["gpt_enabled"]:
            if not telegram_gpt_ready.is_set():
                output_queue.put(("telegram_status",
                                  "Telegram: GPT selezionato ma non connesso. Nessuna risposta locale sostitutiva."))
                return ""
            return ask_telegram_gpt(telegram_assistant_prompt(message, context), bridge)
        local_epoch = conversation_epoch
        try:
            session = get_gemma_session()
            profile = (settings.get("telegram_contact_profiles", {}).get(str(peer_id), "")
                       if peer_id is not None else "")
            # 9/11: last 3 exchanges as real turns, short replies.
            answer = session.ask_isolated_messages(
                lambda pairs: telegram_local_messages(message, context, profile, pairs))
            return answer if (bridge.is_enabled() and not settings["gpt_enabled"]
                              and local_epoch == conversation_epoch) else ""
        except (OSError, ValueError, RuntimeError) as exc:
            if bridge.is_enabled():
                # Show the real cause (short, no prompt or private data).
                reason = " ".join(str(exc).split())[:160] or type(exc).__name__
                output_queue.put(("telegram_status",
                                  "Telegram: risposta locale non disponibile ("
                                  + type(exc).__name__ + ": " + reason + ")."))
            return ""

    def resolve_telegram_gpt_consent(bridge, approval) -> None:
        if not approval.set_running_or_notify_cancel():
            return
        approved_epoch = None
        try:
            if (bridge is telegram_bridge and bridge.is_enabled() and telegram_gpt_ready.is_set()
                    and confirm_gpt_inference(
                        "Il messaggio Telegram ricevuto e i messaggi recenti della stessa chat.")):
                approved_epoch = conversation_epoch
        finally:
            approval.set_result(approved_epoch)

    def toggle_telegram_automatic() -> None:
        nonlocal telegram_bridge
        enabled=telegram_auto.get()
        if not enabled:
            if telegram_bridge:
                telegram_bridge.stop()
                telegram_bridge=None
            settings["telegram_enabled"]=False
            telegram_status.set("Telegram: risposte automatiche disattivate.")
        else:
            chosen=selected_telegram_contacts()
            if not chosen or not credentials_present() or workspace is None:
                telegram_auto.set(False)
                telegram_status.set(
                    "Telegram: configura l'account e spunta almeno un contatto.")
                return
            missing=missing_voice_dependencies()
            if missing:
                telegram_auto.set(False)
                settings["telegram_enabled"]=False
                telegram_status.set(
                    "Telegram: manca "+", ".join(missing)
                    +". Nessun invio verrà effettuato.")
                return
            if telegram_bridge:
                telegram_bridge.stop()
            bridge = TelegramBridge(
                workspace, chosen[0]["id"], chosen[0]["name"],
                None, output_queue.put, voice_name=selected_voice(),
                allowed_contacts=chosen,
                reply_with_context=lambda message, context, peer_id:
                    ask_telegram_reply(message, context, bridge, peer_id))
            telegram_bridge = bridge
            if bridge.start():
                settings["telegram_enabled"]=True
                telegram_status.set("Telegram: collegamento in corso per "+
                                    str(len(chosen))+" contatti autorizzati.")
        try:
            save_settings(settings)
        except (OSError,ValueError) as exc:
            telegram_status.set("Impossibile salvare Telegram: "+str(exc)[:100])
            if telegram_bridge:
                telegram_bridge.stop()
            telegram_auto.set(False)
            settings["telegram_enabled"]=False

    def telegram_reconfigure():
        nonlocal telegram_bridge
        if telegram_bridge:
            telegram_bridge.stop()
            telegram_bridge=None
        current=load_settings()
        for key in ("telegram_peer_id","telegram_contact_name","telegram_contacts"):
            settings[key]=current[key]
        settings["telegram_enabled"]=False
        telegram_auto.set(False)
        telegram_voice_dialog.reset()
        telegram_status.set(
            "Contatti selezionati: "+str(len(selected_telegram_contacts()))+
            "; risposte automatiche spente.")
        try:
            save_settings(settings)
        except (OSError, ValueError) as exc:
            telegram_status.set("Impossibile salvare Telegram: " + str(exc)[:130])

    def telegram_open_setup():
        if os.name!="nt":
            telegram_status.set("Configurazione disponibile solo su Windows.")
            return
        script=Path(__file__).resolve().parent/"configura_telegram.bat"
        try:
            os.startfile(str(script))
            telegram_status.set(
                "Completa la configurazione nella finestra aperta, "
                "poi premi Rileggi contatto autorizzato.")
        except OSError as exc:
            telegram_status.set("Configurazione non avviata: "+str(exc)[:100])

    def display_status(state: dict) -> None:
        nonlocal active_gpt, conversation_epoch
        connected = state.get("status") == "connected" and state.get("sharing") is True
        active_gpt = connected
        if connected and gpt_enabled.get():
            telegram_gpt_ready.set()
        else:
            telegram_gpt_ready.clear()
        if not connected:
            conversation_epoch += 1
            pending_conversation.clear()
            doc_dialog.revoke_pending()
            planner_abort_event.set()
        if not gpt_enabled.get():
            gpt_status.set("GPT: disattivato manualmente")
        elif connected:
            label = state.get("profileLabel") or "account ChatGPT"
            gpt_status.set(f"GPT: connesso ({str(label)[:50]})")
        elif state.get("status") == "reauth_required":
            gpt_status.set("GPT: autenticazione scaduta. Effettua nuovamente il login.")
        else:
            gpt_status.set("GPT: non connesso. Premi 'Connetti ChatGPT' per accedere.")
        refresh_buttons()

    def refresh_buttons() -> None:
        can_gpt = gpt_enabled.get() and not busy_gpt and not closing
        connect.configure(state="normal" if can_gpt else "disabled")
        disconnect.configure(state="normal" if can_gpt and active_gpt else "disabled")
        ask_button.configure(state="normal" if can_gpt and active_gpt else "disabled")
        plan_button.configure(state="normal" if can_gpt and active_gpt else "disabled")
        local_button.configure(state="disabled" if busy_local or closing else "normal")

    def confirm_gpt_inference(detail: str) -> bool:
        nonlocal online_consent_pending
        if online_consent_pending or closing or busy_gpt or not gpt_enabled.get() or not active_gpt:
            return False
        epoch = conversation_epoch
        online_consent_pending = True
        try:
            approved = messagebox.askyesno(
                "Conferma GPT online",
                "Inviare a GPT online per questa richiesta?\n\n" + detail,
                parent=root, default="no")
        finally:
            online_consent_pending = False
        return (approved and epoch == conversation_epoch and not closing
                and gpt_enabled.get() and active_gpt and not busy_gpt)

    def run_gpt(action: str, *, consent_granted=False,
                capability="chat.conversation", permission=None,
                consent_detail="La richiesta e il contesto disponibile.", **params) -> bool:
        nonlocal busy_gpt, gpt_request_action, active_gpt, conversation_epoch
        nonlocal gpt_conversation_session_grant
        if busy_gpt or not gpt_enabled.get() or closing:
            return False
        if action in ("ask", "conversation", "typed_conversation"):
            if not active_gpt:
                return False
            from local_model.online_permissions import authorize_online_request
            if capability == "chat.conversation":
                if (gpt_conversation_session_grant is not None
                        and not gpt_conversation_session_grant()):
                    gpt_conversation_session_grant = None
                permission = permission or gpt_conversation_session_grant
                if permission is None:
                    # Check saved denial before asking. Even saved 'allowed'
                    # requires this app-session's explicit conversational consent.
                    candidate = authorize_online_request(capability, confirmed=True)
                    if candidate is not None and (consent_granted or confirm_gpt_inference(
                            "Conversazione GPT per questa sessione, da voce e chat. "
                            "Il consenso termina scegliendo Gemma o chiudendo Lumi.\n\n"
                            + consent_detail)):
                        permission = candidate
            else:
                permission = permission or authorize_online_request(
                    capability, confirmed=consent_granted,
                    confirm=lambda: confirm_gpt_inference(consent_detail))
            if (permission is None or permission.capability != capability
                    or not permission()):
                write_line("GPT > Invio non autorizzato. Controlla Autorizzazioni GPT per funzione.")
                return False
            if capability == "chat.conversation":
                gpt_conversation_session_grant = permission
        if action == "disconnect":
            gpt_conversation_session_grant = None
            set_telegram_gpt_session(False)
            conversation_epoch += 1
            active_gpt = False
            telegram_gpt_ready.clear()
            planner_abort_event.set()
        gpt_request_action = action
        busy_gpt = True
        refresh_buttons()
        if action == "sign_in":
            gpt_status.set("GPT: in attesa del login nel browser...")
        elif action in ("ask", "conversation","typed_conversation"):
            gpt_status.set("GPT: elaborazione richiesta...")
        elif action == "disconnect":
            gpt_status.set("GPT: scollegamento...")
        else:
            gpt_status.set("GPT: verifica connessione...")

        consent_epoch = conversation_epoch

        def worker() -> None:
            structured = action in ("conversation","typed_conversation")
            epoch = params.get("epoch") if structured else None
            doc_snapshot = params.get("document_id") if structured else None
            user_utterance = params.get("utterance", "") if structured else ""
            typed_question = params.get("source", "") if action == "ask" else ""
            try:
                timeout = 600 if action == "sign_in" else 180 if action in ("ask", "conversation", "typed_conversation") else 40
                sdk_action = "ask" if structured else action
                sdk_params = {key: value for key, value in params.items()
                              if key not in ("epoch", "document_id", "utterance", "source", "file_refinement")}
                if sdk_action == "ask":
                    def authorized():
                        return (not closing and consent_epoch == conversation_epoch
                                and permission())
                    if not authorized():
                        raise PermissionError("Autorizzazione GPT revocata.")
                    sdk_params["authorize_send"] = authorized
                result = chat_transport.call(sdk_action, timeout=timeout, **sdk_params)
                if structured:
                    output_queue.put(("conversation_ok", epoch, doc_snapshot,
                                      user_utterance, result, action, params.get("file_refinement")))
                else:
                    output_queue.put(("gpt_ok", action, result, typed_question, consent_epoch))
            except Exception as exc:
                if structured:
                    output_queue.put(("conversation_error", epoch, user_utterance,
                                      str(exc)[:220], action, params.get("file_refinement")))
                else:
                    output_queue.put(("gpt_error", action, str(exc)[:400], consent_epoch))
        threading.Thread(target=worker, daemon=True, name="jarvis-gpt-worker").start()
        return True

    def start_conversation_gpt(spoken: str) -> None:
        """Use the owner's selected model; connection failure never selects Gemma."""
        if closing or voice_mode.get() not in (GPT_CONVERSATION, CONTINUOUS, PUSH_TO_TALK):
            return
        if try_self_diagnostic(spoken):
            return
        try:
            chat_is_visible = chat_notebook.select() == str(chat_local_tab)
        except NameError:
            chat_is_visible = False
        if chat_is_visible and gpt_enabled.get():
            chat_sessions_panel.report_error(
                "GPT online non è collegato alle chat isolate F2. Disattiva GPT.")
            write_line("CHAT > Non ho inviato il messaggio a GPT: istanza locale isolata.")
            return
        if not gpt_enabled.get():
            submit_gemma_voice(spoken)
            return
        if not active_gpt:
            write_line("GPT > GPT selezionato ma non connesso. Connetti ChatGPT nelle impostazioni.")
            speak_result("GPT non è connesso. La scelta del modello resta GPT.")
            return
        if busy_gpt:
            write_line("GPT > Sto già elaborando. Attendi la risposta.")
            return
        snapshot = documents.current.ident if documents.current else None
        try:
            live = current_capability_snapshot(snapshot is not None)
            prompt = build_conversation_prompt(
                spoken, has_document=snapshot is not None,
                memory_context=recent_memory_for_gpt(spoken),
                telegram_send_ready=live["telegram_voice_send"],
                runtime_info=capability_status_prompt(live),
                addon_actions=active_addon_actions())
        except (ValueError, ConversationRejected) as exc:
            write_line("GPT > " + str(exc))
            return
        run_gpt("conversation", prompt=prompt, epoch=conversation_epoch,
                document_id=snapshot, utterance=spoken)

    def toggle_gpt() -> None:
        nonlocal active_gpt, conversation_epoch, gpt_conversation_session_grant
        previous = settings["gpt_enabled"]
        try:
            settings["gpt_enabled"] = bool(gpt_enabled.get())
            save_settings(settings)
        except (OSError, ValueError) as exc:
            settings["gpt_enabled"] = previous
            gpt_enabled.set(previous)
            messagebox.showerror("Impossibile salvare", str(exc), parent=root)
            return
        # Revoke queued replies from the previous selected model on either switch.
        conversation_epoch += 1
        pending_conversation.clear()
        if gpt_enabled.get():
            gpt_status.set("GPT: attivo nelle impostazioni; controllo collegamento...")
            run_gpt("status")
        else:
            gpt_conversation_session_grant = None
            set_telegram_gpt_session(False)
            doc_dialog.revoke_pending()
            planner_abort_event.set()
            active_gpt = False
            telegram_gpt_ready.clear()
            gpt_status.set("GPT: disattivato manualmente")
            threading.Thread(target=service.stop, daemon=True).start()
            refresh_buttons()

    def try_model_switch(spoken: str) -> bool:
        from voice_control import model_switch_target
        selected = model_switch_target(spoken)
        if (selected is None or closing or document_busy or save_only_waiting
                or doc_dialog.phase.startswith("awaiting_")
                or doc_dialog.phase == "executing" or pending_project_name
                or pending_project_rename_id is not None
                or pending_project_trash_id is not None
                or telegram_voice_dialog.pending):
            return False
        if bool(gpt_enabled.get()) != selected:
            gpt_enabled.set(selected)
            toggle_gpt()
        # toggle_gpt restores the old setting if persistence fails.
        model = "GPT" if gpt_enabled.get() else "Gemma"
        message = "Modello selezionato: " + model + "."
        write_line("LUMI > " + message)
        speak_result(message)
        return True

    def toggle_memory() -> None:
        nonlocal durable_brain, speech_lexicon
        desired = bool(memory_enabled.get())
        previous = bool(settings["memory_enabled"])
        candidate = durable_brain
        candidate_lexicon = speech_lexicon
        if desired:
            try:
                if candidate is None:
                    candidate = SecondBrain()
                if candidate_lexicon is None:
                    candidate_lexicon = SpeechCorrections(candidate.path)
            except (OSError, sqlite3.Error, ValueError, SpeechCorrectionError) as exc:
                memory_enabled.set(previous)
                memory_status_refresh("Impossibile attivare: " + str(exc)[:90])
                return
        settings["memory_enabled"] = desired
        try:
            save_settings(settings)
        except (OSError, ValueError) as exc:
            settings["memory_enabled"] = previous
            memory_enabled.set(previous)
            memory_status_refresh("Impossibile salvare l'opzione: " + str(exc)[:90])
            return
        durable_brain = candidate if desired else None
        speech_lexicon = candidate_lexicon if desired else None
        memory_status_refresh(
            "La memoria già salvata resta sul PC fino a cancellazione esplicita."
            if not desired else "Memoria attiva anche dopo il prossimo riavvio.")

    def clear_saved_memory() -> None:
        nonlocal gemma_memory_revision
        if not messagebox.askyesno(
            "Cancella il Second Brain",
            "Eliminare scambi, operazioni e correzioni vocali archiviate da Lia? "
            "Questa operazione non può essere annullata. "
            "La cronologia delle attività del motore locale resta separata.",
            parent=root,
        ):
            return
        try:
            # A post-commit cleanup (e.g. VACUUM) can fail after DELETE. Revoke
            # pending turns/RAM on confirmation, before any fallible disk I/O.
            gemma_memory_revision += 1
            conversation_memory.clear()
            if gemma_session[0] is not None:
                gemma_session[0].forget_context(None)
            target = durable_brain if durable_brain is not None else SecondBrain()
            target.clear_all()
            if speech_lexicon is not None:
                speech_lexicon.reload()
            memory_status_refresh("Memoria e correzioni vocali eliminate su richiesta.")
        except (OSError, sqlite3.Error, ValueError) as exc:
            memory_status.set("Cancellazione memoria non riuscita: " + str(exc)[:100])

    def show_voice_corrections() -> None:
        """User must explicitly review both sentences before saving a rule."""
        if speech_lexicon is None or not memory_enabled.get():
            messagebox.showinfo(
                "Vocabolario vocale di Lia",
                "Attiva prima Second Brain locale per conservare "
                "le correzioni vocali tra un avvio e l'altro.",
                parent=root)
            return
        popup = tk.Toplevel(root)
        popup.title("Correggi il riconoscimento di Lia")
        popup.geometry("630x270")
        popup.minsize(550, 240)
        popup.transient(root)
        body = ttk.Frame(popup, padding=12)
        body.pack(fill="both", expand=True)
        ttk.Label(
            body, text="Quando Vosk sbaglia una frase, correggila qui. "
                       "Lia impara soltanto le parole cambiate, "
                       "non i comandi e le conferme.",
            wraplength=595).pack(anchor="w", pady=(0, 6))
        heard = tk.StringVar(value=last_voice_sample.get())
        intended = tk.StringVar()
        ttk.Label(body, text="Frase riconosciuta da Vosk:").pack(anchor="w")
        ttk.Entry(body, textvariable=heard, width=80).pack(
            fill="x", pady=(0, 6))
        ttk.Label(body, text="Frase che avevi pronunciato:").pack(anchor="w")
        entry = ttk.Entry(body, textvariable=intended, width=80)
        entry.pack(fill="x", pady=(0, 6))
        result = tk.StringVar(
            value=f"Correzioni personali: {speech_lexicon.count()} / 80. "
                  "Esempio: 'apri blocco moto' → 'apri blocco note'.")
        ttk.Label(body, textvariable=result, wraplength=600).pack(
            anchor="w", pady=(0, 7))
        actions = ttk.Frame(body)
        actions.pack(fill="x")

        def learn() -> None:
            if speech_lexicon is None or not memory_enabled.get():
                result.set("Second Brain è disattivato: non salvo correzioni.")
                return
            try:
                before, after = speech_lexicon.learn_phrase(
                    heard.get(), intended.get(), user_confirmed=True)
            except (SpeechCorrectionError, OSError, sqlite3.Error) as exc:
                result.set("Correzione non salvata: " + str(exc)[:160])
                return
            result.set(
                f"Imparato: {before} → {after}. "
                "Sarà applicato alle prossime frasi riconosciute.")
            write_line(f"CORREZIONE VOCE > {before} → {after}")
            heard.set("")
            intended.set("")

        def reset_personal_words() -> None:
            if speech_lexicon is None or not memory_enabled.get():
                result.set("Second Brain disattivato.")
                return
            if not messagebox.askyesno(
                    "Azzera correzioni vocali",
                    "Cancellare soltanto le correzioni del riconoscimento "
                    "vocale, lasciando intatti gli altri ricordi di Lia?",
                    parent=popup):
                return
            try:
                speech_lexicon.clear()
                result.set("Dizionario di correzioni vocali azzerato.")
            except (OSError, sqlite3.Error) as exc:
                result.set("Cancellazione non riuscita: " + str(exc)[:120])

        ttk.Button(actions, text="Conferma correzione", command=learn).pack(
            side="left")
        ttk.Button(actions, text="Azzera correzioni",
                   command=reset_personal_words).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Chiudi", command=popup.destroy).pack(
            side="right")
        entry.focus_set()

    gpt_panel = ttk.LabelFrame(assistant_settings_frame,
                                text="Connessione ChatGPT", padding=12)
    gpt_panel.pack(fill="x", pady=(0, 10))
    gpt_toggle = ttk.Checkbutton(
        gpt_panel, text="Abilita collegamento ChatGPT (attivo di default, spegnimento manuale)",
        variable=gpt_enabled, command=toggle_gpt
    )
    gpt_toggle.pack(anchor="w")
    ttk.Label(gpt_panel, textvariable=gpt_status, wraplength=630).pack(anchor="w", pady=(5, 6))

    gpt_buttons = ttk.Frame(gpt_panel)
    gpt_buttons.pack(fill="x", pady=(0, 7))
    connect = ttk.Button(gpt_buttons, text="Connetti ChatGPT", command=lambda: run_gpt("sign_in"))
    connect.pack(side="left", padx=(0, 8))
    disconnect = ttk.Button(gpt_buttons, text="Scollega account", command=lambda: run_gpt("disconnect"))
    disconnect.pack(side="left")
    ttk.Label(gpt_panel, text="Il login usa il browser ufficiale; nessuna chiave API e nessuna fatturazione a consumo.", wraplength=630).pack(anchor="w")

    brain_controls = ttk.LabelFrame(assistant_settings_frame, text="Memoria generale", padding=12)
    brain_controls.pack(fill="x", pady=(5, 3))
    memory_toggle = ttk.Checkbutton(
        brain_controls, text="Second Brain locale (ricorda conversazioni e attività)",
        variable=memory_enabled, command=toggle_memory)
    memory_toggle.pack(side="left", padx=(0, 10))
    memory_clear_button = ttk.Button(
        brain_controls, text="Cancella memoria generale (non progetti)", command=clear_saved_memory)
    memory_clear_button.pack(side="right")
    ttk.Label(assistant_settings_frame, textvariable=memory_status, wraplength=630).pack(
        anchor="w", pady=(0, 2))
    ttk.Label(
        assistant_settings_frame,
        text="I ricordi restano sul PC. Se usi ChatGPT, gli estratti pertinenti "
             "vengono inviati al modello per comprendere il contesto; "
             "non vengono salvati i corpi completi delle email.",
        wraplength=710
    ).pack(anchor="w", pady=(0, 4))

    workspace_panel=ttk.LabelFrame(
        integrations_settings_frame,text="Progetti — contesto indipendente e continuità",padding=8)
    workspace_panel.pack(fill="x",pady=(6,8))
    ttk.Label(workspace_panel,
        text="Memoria progetti automatica: chat e risultati verificati vengono "
             "salvati nel progetto senza premere Salva. Il Second Brain ON/OFF "
             "controlla soltanto la memoria della conversazione generale.",
        wraplength=700).pack(anchor="w",pady=(0,5))
    workspace_button=ttk.Button(
        workspace_panel,text="Gestisci progetti / apri continuità")
    workspace_button.pack(side="left",padx=(0,12))
    ttk.Label(workspace_panel,textvariable=workspace_status,
              wraplength=420).pack(side="left",fill="x",expand=True)

    telegram_panel=ttk.LabelFrame(
        integrations_settings_frame,text="Telegram — contatti selezionati e messaggi vocali",padding=8)
    telegram_panel.pack(fill="x",pady=(3,10))
    telegram_toggle=ttk.Checkbutton(
        telegram_panel,text="Risposte vocali automatiche ON / OFF",
        variable=telegram_auto)
    telegram_toggle.pack(anchor="w")
    telegram_consent_row=ttk.Frame(telegram_panel)
    telegram_consent_row.pack(fill="x",pady=(4,0))
    ttk.Label(telegram_consent_row,text="Consenso GPT online").pack(side="left",padx=(0,8))
    ttk.Radiobutton(telegram_consent_row,text="Chiedi ogni volta",
                    variable=telegram_gpt_session_choice,value=False,
                    command=lambda: set_telegram_gpt_session(False)).pack(side="left")
    ttk.Radiobutton(telegram_consent_row,text="Consenti per questa sessione",
                    variable=telegram_gpt_session_choice,value=True,
                    command=lambda: set_telegram_gpt_session(True)).pack(side="left",padx=(8,0))
    ttk.Label(telegram_panel,wraplength=690,
              text="Il consenso per questa sessione permette di inviare a GPT online "
                   "i messaggi e il contesto recente delle chat Telegram dei contatti "
                   "spuntati. Si azzera quando spegni o disconnetti GPT o chiudi Lumi."
              ).pack(anchor="w",pady=(2,0))
    telegram_row=ttk.Frame(telegram_panel)
    telegram_row.pack(fill="x",pady=(4,3))
    telegram_configure_button=ttk.Button(
        telegram_row,text="Configura Telegram (accesso sicuro)")
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
        telegram_panel,textvariable=telegram_status,wraplength=690
    ).pack(anchor="w",pady=(3,0))
    ttk.Label(
        telegram_panel,
        text="I contatti si scelgono dall'elenco Telegram con una spunta. "
             "Le risposte automatiche si attivano separatamente dall'invio "
             "manuale, che richiede conferma. I vocali usano Windows SAPI "
             "e OGG/Opus, senza GPT per trasformare il testo in audio.",
        wraplength=690).pack(anchor="w",pady=(3,0))

    addon_panel=ttk.LabelFrame(
        integrations_settings_frame,text="Add-on — installazione locale e permessi",padding=8)
    addon_panel.pack(fill="x",pady=(3,9))
    addon_settings_button=ttk.Button(
        addon_panel,text="Gestisci add-on (installa, attiva, aggiorna, rimuovi)")
    addon_settings_button.pack(side="left",padx=(0,10))
    ttk.Label(addon_panel,
              text="Solo pacchetti .jaddon descrittivi; nessun codice esterno "
                   "viene eseguito automaticamente.",
              wraplength=455).pack(side="left",fill="x",expand=True)

    # Conversation is always visible at the left of the animated HUD.
    # The console composer follows the supplied reference: a circular mic,
    # one conversation field and a send arrow. The previous explicit tools
    # remain available behind the small menu (never silently removed).
    scope_row=ttk.Frame(hud.command_host)
    scope_row.pack(fill="x",pady=(0,5))
    ttk.Label(scope_row,textvariable=active_context_label,
              font=("Consolas",8)).pack(side="left",fill="x",expand=True)
    scope_button=ttk.Button(scope_row,text="Progetti")
    scope_button.pack(side="right")
    input_row = tk.Frame(hud.command_host, bg=PANEL)
    input_row.pack(fill="x")
    request = tk.StringVar()
    hud_mic_button = tk.Button(
        input_row, text="●", width=2,
        font=("Segoe UI", 13, "bold"),
        bg="#092d47", fg=CYAN,
        activebackground="#124766", activeforeground=WHITE,
        bd=1, relief="flat", cursor="hand2")
    hud_mic_button.pack(side="left", padx=(0, 6), ipady=3)
    input_box = ttk.Entry(
        input_row, textvariable=request, font=("Segoe UI", 10))
    input_box.pack(side="left", fill="x", expand=True, padx=(0, 5),
                   ipady=6)
    hud_send_button = tk.Button(
        input_row, text="➤", width=2,
        font=("Segoe UI Symbol", 15),
        bg="#072c44", fg=CYAN,
        activebackground="#0c4968", activeforeground=WHITE,
        bd=0, relief="flat", cursor="hand2")
    hud_send_button.pack(side="left", padx=(0, 3), ipady=1)
    tools_button = tk.Button(
        input_row, text="⋯", width=2, font=("Segoe UI", 14),
        bg=PANEL, fg="#76b9d1",
        activebackground="#0b344b", activeforeground=WHITE,
        bd=0, relief="flat", cursor="hand2")
    tools_button.pack(side="left")
    help_button = tk.Button(
        input_row, text="?", width=2, font=("Segoe UI", 14),
        bg=PANEL, fg=CYAN, activebackground="#0b344b",
        activeforeground=WHITE, bd=0, relief="flat", cursor="hand2")
    help_button.pack(side="left", padx=(3, 0))
    buttons_row = ttk.Frame(hud.command_host)
    # Hidden until the user clicks ⋯, like secondary controls in the concept.
    local_button = ttk.Button(buttons_row, text="Esegui locale")
    local_button.pack(side="left", padx=(0, 4))
    ask_button = ttk.Button(buttons_row, text="Chiedi a GPT")
    ask_button.pack(side="left", padx=(0, 4))
    gemma_button = ttk.Button(buttons_row, text="Prova Gemma locale")
    gemma_button.pack(side="left", padx=(0, 4))
    plan_button = ttk.Button(buttons_row, text="Pianifica attività")
    plan_button.pack(side="left", padx=(0, 4))
    diagnostic_button = ttk.Button(buttons_row, text="Autodiagnosi Lumi")
    diagnostic_button.pack(side="left")

    # Native Tk text with a dark ttk scrollbar matches the concept's
    # streamlined chat panel without third-party UI or web technologies.
    # The original action/log console is retained as-is. Local chat instances
    # live in a separate tab and never steal its existing output sink.
    chat_notebook = ttk.Notebook(hud.console_host)
    chat_notebook.pack(fill="both", expand=True)
    chat_local_tab = ttk.Frame(chat_notebook)
    chat_console_tab = ttk.Frame(chat_notebook)
    chat_notebook.add(chat_local_tab, text="Chat locali")
    chat_notebook.add(chat_console_tab, text="Console")
    chat_notebook.select(chat_console_tab)
    chat_panel = ttk.Frame(chat_console_tab)
    chat_panel.pack(fill="both", expand=True)
    output = tk.Text(
        chat_panel, height=12, wrap="word", state="disabled",
        font=("Segoe UI", 10), bg="#020d17", fg=WHITE,
        insertbackground=CYAN, relief="flat",
        borderwidth=0, padx=12, pady=9,
        selectbackground="#136488", selectforeground=WHITE)
    chat_scroll = ttk.Scrollbar(
        chat_panel, orient="vertical", command=output.yview)
    output.configure(yscrollcommand=chat_scroll.set)
    chat_scroll.pack(side="right", fill="y")
    output.pack(side="left", fill="both", expand=True)
    output.tag_configure("utente", foreground="#caeaff", spacing3=9)
    output.tag_configure("jarvis", foreground="#46ccfa", spacing3=9)
    output.tag_configure("azione", foreground=GREEN, spacing3=9)
    output.tag_configure("errore", foreground=AMBER, spacing3=9)
    output.tag_configure("sistema", foreground="#83a8ba", spacing3=9)
    output.tag_configure("message_head",
                         font=("Segoe UI", 10, "bold"),
                         spacing1=9)
    hud.attach_console(output)
    from local_model.chat_ui import ChatSessionsPanel
    chat_sessions_panel = ChatSessionsPanel(
        chat_local_tab,
        store_path=default_path().with_name("jarvis_chat_sessions.sqlite3"),
        get_project_id=lambda: active_project_id,
        can_change=lambda: chat_navigation_possible(),
        on_change=lambda old, new: chat_selection_changed(old, new),
        on_settings=open_native_model_settings)
    chat_sessions_panel.frame.pack(fill="both", expand=True)
    write_line("Lumi locale pronto. Scrivi 'aiuto' o premi F1 per la guida e i comandi.")

    try:
        engine = LocalEngine()
        if addon_manager is not None:
            try:
                engine.program_apps = addon_manager.program_service
            except (ImportError,OSError,ValueError) as exc:
                write_line('PROGRAMMI > Componente incompleto: '+str(exc)+
                           '. Reinstalla la cartella program_apps dal pacchetto completo.')
            try:
                engine.file_access = addon_manager.file_service
                engine.file_access.progress=lambda snapshot:output_queue.put(('file_progress',snapshot))
            except (ImportError,OSError,ValueError) as exc:
                engine.file_access_blocked = True
                write_line("ACCESSO FILE > Componente incompleto: "+str(exc)+
                           ". Reinstalla il pacchetto completo (cartella file_access), poi riavvia Lumi.")
    except (OSError, ValueError) as exc:
        messagebox.showerror("Motore locale non disponibile", str(exc), parent=root)
        root.destroy()
        return

    speaker = OfflineSpeaker(notify_error=lambda reason: output_queue.put(("tts_error", reason)))
    speaker.effect = settings.get("tts_effect", 25) / 100
    import voice_style
    voice_style.update(rate=settings.get("tts_rate", 0), pitch=settings.get("tts_pitch", 0),
                       volume=settings.get("tts_volume", 100))
    # Avatar LUMI: lip sync dalla curva del volume della voce naturale e
    # mini avatar in basso a destra quando la finestra e' ridotta a icona.
    from lumi_avatar import LIPSYNC, PLAYBACK_LATENCY, AvatarDock
    speaker.on_envelope = lambda envelope: LIPSYNC.push(envelope, delay=PLAYBACK_LATENCY, grace=0.8)
    import audio_player
    audio_player.POSITION_LISTENER = LIPSYNC.update_position
    avatar_dock = AvatarDock(root, lambda: getattr(hud, "_last_mode", "idle"))
    voice = VoiceController(output_queue.put, ignore_audio=speaker.is_audible)
    wake_gate = WakeWordGate()
    dictation = DesktopDictation()

    def selected_voice() -> str:
        choice = spoken_voice.get()
        return "" if choice == DEFAULT_VOICE_LABEL else choice

    def save_speech_preferences() -> None:
        settings["tts_enabled"] = bool(spoken_enabled.get())
        settings["tts_voice"] = selected_voice()
        settings["tts_effect"] = max(0, min(100, int(spoken_effect.get())))
        speaker.effect = settings["tts_effect"] / 100
        import voice_style
        style = voice_style.update(rate=spoken_rate.get(), pitch=spoken_pitch.get(),
                                   volume=spoken_volume.get())
        settings["tts_rate"], settings["tts_pitch"], settings["tts_volume"] = (
            style["rate"], style["pitch"], style["volume"])
        try:
            save_settings(settings)
            spoken_status.set("Risposte vocali salvate; nessun servizio a pagamento.")
        except (OSError, ValueError) as exc:
            spoken_status.set("Impossibile salvare le preferenze vocali: " + str(exc)[:130])

    def refresh_voices() -> None:
        spoken_status.set("Rilevamento delle voci già installate in Windows...")
        refresh_voices_button.configure(state="disabled")

        def worker() -> None:
            try:
                output_queue.put(("tts_voices", installed_voices()))
            except (OSError, ValueError, TimeoutError) as exc:
                output_queue.put(("tts_error", str(exc)[:140]))

        threading.Thread(target=worker, daemon=True, name="jarvis-voices-list").start()

    def download_natural_voice(key: str) -> None:
        from piper_voice import LABELS, PiperVoiceError, download_voice
        spoken_status.set("Download della voce " + LABELS[key] + " dal repository...")
        for button in (download_paola_button, download_serena_button):
            button.configure(state="disabled")

        def worker() -> None:
            try:
                download_voice(key)
                output_queue.put(("tts_status", "Voce " + LABELS[key]
                                  + " scaricata e verificata. Selezionala nel menu Voce."))
                output_queue.put(("tts_voices", installed_voices()))
            except Exception as exc:   # ogni errore arriva all'interfaccia
                output_queue.put(("tts_error", "Download voce non riuscito: "
                                  + (str(exc) or type(exc).__name__)[:140]))
            finally:
                output_queue.put(("tts_download_done", None))

        threading.Thread(target=worker, daemon=True, name="lumi-voice-download").start()

    def test_speech() -> None:
        speaker.effect = max(0, min(100, int(spoken_effect.get()))) / 100
        import voice_style
        voice_style.update(rate=spoken_rate.get(), pitch=spoken_pitch.get(),
                           volume=spoken_volume.get())
        if not speaker.speak("Pronto. Questa è la mia voce.", selected_voice()):
            spoken_status.set("Sintesi vocale occupata: riprova.")

    def speak_result(message: str) -> None:
        if spoken_enabled.get() and message:
            speaker.speak(message, selected_voice())

    def update_document_buttons() -> None:
        pending = (doc_dialog.phase.startswith("awaiting_") or save_only_waiting) and not document_busy
        can_choose = doc_dialog.phase == "awaiting_close_choice" and not document_busy
        doc_save_button.configure(state="normal" if can_choose else "disabled")
        doc_discard_button.configure(
            state="normal" if can_choose else "disabled")
        doc_cancel_button.configure(state="normal" if pending else "disabled")
        destination_ready = (
            (doc_dialog.phase == "awaiting_save_destination" or save_only_waiting)
            and not document_busy)
        choose_save_button.configure(
            state="normal" if destination_ready else "disabled")
        hud_save_file_button.configure(
            state="normal" if destination_ready else "disabled")
        if pending and not doc_choices.winfo_manager():
            doc_choices.pack(fill="x", pady=(0, 5), before=input_row)
        elif not pending and doc_choices.winfo_manager():
            doc_choices.pack_forget()

    def reconcile_document_session(*, force: bool = False) -> bool:
        """Reconcile a manually closed owned Notepad with the UI state.

        Only a definitely terminated original process/HWND can release the
        document. A temporarily inaccessible but still-live window is kept.
        This runs on Tk's UI thread, never while a document worker is active.
        """
        nonlocal save_only_waiting,document_topic,document_owner_project_id
        nonlocal last_notepad_probe,conversation_epoch
        if document_busy or documents.current is None:
            return False
        now=time.monotonic()
        if not force and now-last_notepad_probe<1.5:
            return False
        last_notepad_probe=now
        try:
            closed=release_closed_document(documents,doc_dialog)
        except (OSError,ValueError,AttributeError):
            # An inconclusive Windows probe must never discard unsaved text.
            return False
        if not closed:
            return False
        save_only_waiting=False
        document_topic=""
        document_owner_project_id=None
        # An old in-flight GPT reply cannot act on a document just closed.
        conversation_epoch+=1
        pending_conversation.clear()
        update_document_buttons()
        message=("Il precedente Blocco note è stato chiuso manualmente. "
                 "Puoi aprire un nuovo documento.")
        document_status.set(message)
        write_line("DOCUMENTO > "+message)
        return True

    def announce_document(message: str) -> None:
        update_document_buttons()
        document_status.set(message)
        write_line("DOCUMENTO > " + message)
        speak_result(message)

    def document_operation(operation: str, *, content: str = "",
                           target: str = "", document_id: str = "",
                           path: Path | None = None,
                           close_after: bool = False,
                           source_utterance: str = "") -> None:
        nonlocal document_busy, last_user_for_document, project_document_ticket
        nonlocal document_topic,document_owner_project_id,document_operation_id
        if document_busy or closing:
            announce_document("Sto già lavorando sul documento: attendi.")
            return
        reconcile_document_session(force=True)
        project_document_ticket = begin_project_work(
            source_utterance or operation,source="document")
        if project_document_ticket is False:
            announce_document("Checkpoint progetto non disponibile: azione non eseguita.")
            return
        if operation_ledger is None:
            finish_project_work(project_document_ticket,"interrupted",
                                "Registro operativo non disponibile.")
            project_document_ticket=None
            announce_document("Registro operativo non disponibile: operazione bloccata.")
            return
        try:
            document_operation_id=operation_ledger.begin(
                "notepad."+operation,origin="document",
                project_id=document_owner_project_id or active_project_id or "")
            operation_ledger.running(document_operation_id)
        except (OSError,sqlite3.Error,MemoryBoundaryError) as exc:
            finish_project_work(project_document_ticket,"interrupted",
                                "Registro operativo non disponibile.")
            project_document_ticket=None
            announce_document("Impossibile registrare l'azione: "+str(exc)[:95])
            return
        document_busy = True
        if operation == "open" or (operation=="compose" and target=="new_notepad"):
            document_owner_project_id=active_project_id
            document_topic=source_utterance if operation=="compose" else ""
        elif operation=="compose" and source_utterance and not document_topic:
            document_topic=source_utterance
        last_user_for_document = source_utterance or last_user_for_document or operation
        update_document_buttons()
        document_status.set("Operazione in corso su Blocco note...")

        def worker() -> None:
            output_queue.put(run_document_worker(
                documents, operation, content=content, target=target,
                document_id=document_id, path=path, close_after=close_after))

        # A started save must finish even when the Jarvis UI closes.
        try:
            threading.Thread(target=worker, daemon=False,
                             name="jarvis-document-worker").start()
        except RuntimeError as exc:
            output_queue.put(("document_error",operation,
                              "Impossibile avviare la scrittura: "+
                              type(exc).__name__))

    def ask_to_close_document(source_utterance: str = "") -> None:
        if document_busy:
            announce_document("Attendi la fine della scrittura prima di chiudere.")
            return
        if doc_dialog.phase != "editing" or doc_dialog.document_id is None:
            announce_document("Non ho un documento Blocco note gestito da Lumi da chiudere.")
            return
        decision = doc_dialog.request_close()
        if decision.kind == "close_clean":
            # The user could have manually edited the text in the meantime.
            # Never discard an apparently clean document without asking.
            doc_dialog.phase = "awaiting_close_choice"
            doc_dialog.dirty = True
            question = "Vuoi salvare e chiudere, chiudere senza salvare oppure annullare?"
            announce_document(question)
            if source_utterance:
                remember_exchange(source_utterance, question, "clarify")
        else:
            announce_document(decision.message)
            if source_utterance:
                remember_exchange(source_utterance, decision.message, "clarify")

    def automatic_document_destination(*, explicit_name: str = "") -> Path | None:
        """Use this document's original project, never a newly selected one."""
        if workspace is None or document_owner_project_id is None:
            return None
        return project_save_destination(
            workspace,document_owner_project_id,document_topic,
            explicit_name=explicit_name)

    def save_document_now(spoken: str, *, explicit_name: str = "") -> None:
        nonlocal save_only_waiting
        if document_busy or doc_dialog.phase!="editing" or documents.current is None:
            announce_document("Non ho un documento pronto da salvare.")
            return
        # Explicit user-chosen desktop/documents/downloads takes priority.
        explicit_path=destination_from_voice(spoken)
        if explicit_path is not None:
            path=explicit_path
        else:
            try:
                path=automatic_document_destination(explicit_name=explicit_name)
            except (OSError,ValueError,WorkspaceError) as exc:
                announce_document("Nome o cartella del documento non validi: "+str(exc)[:100])
                return
        if path is None:
            save_only_waiting=True
            announce_document("Dove vuoi salvare? Per esempio: sul desktop come appunti.")
            return
        save_only_waiting=False
        document_operation("save_only",document_id=doc_dialog.document_id,
                           path=path,source_utterance=spoken)

    def receive_save_only_destination(spoken: str) -> None:
        nonlocal save_only_waiting
        if spoken.casefold().strip(" ,.!?") in ("annulla","lascia stare"):
            save_only_waiting=False
            announce_document("Salvataggio annullato. Documento aperto.")
            return
        path=destination_from_voice(spoken)
        if path is None:
            announce_document("Indicami una cartella e un nome, per esempio "
                              "sul desktop come appunti, oppure scegli la cartella.")
            return
        save_only_waiting=False
        document_operation("save_only",document_id=doc_dialog.document_id,
                           path=path,source_utterance=spoken)

    def execute_document_choice(decision, *, path: Path | None = None) -> None:
        if decision.kind == "ask_destination":
            try:
                path=automatic_document_destination()
            except (OSError,ValueError,WorkspaceError) as exc:
                announce_document("Cartella progetto non disponibile: "+str(exc)[:100])
                return
            if path is not None:
                selected=doc_dialog.provide_destination(str(path))
                execute_document_choice(selected,path=path)
                return
        if decision.kind in ("save_then_close", "save_as_then_close"):
            destination = path if path is not None else (
                Path(doc_dialog.saved_path) if doc_dialog.saved_path else None)
            if (path is None and doc_dialog.saved_path and
                    document_owner_project_id is not None):
                # Fresh version if the editor changed since the last save.
                # ManagedDocuments will reuse the old file if unchanged.
                try:
                    destination=automatic_document_destination()
                except (OSError,ValueError,WorkspaceError) as exc:
                    announce_document("Cartella progetto non disponibile: "+str(exc)[:100])
                    return
            if destination is None:
                try:
                    destination=automatic_document_destination()
                except (OSError,ValueError,WorkspaceError) as exc:
                    announce_document("Cartella progetto non disponibile: "+str(exc)[:100])
                    return
                if destination is None:
                    doc_dialog.phase = "awaiting_save_destination"
                    announce_document("Dove vuoi salvare? Per esempio: "
                                      "sul desktop come storia di Venezia.")
                    choose_save_button.configure(state="normal")
                    return
                if doc_dialog.phase=="awaiting_save_destination":
                    doc_dialog.provide_destination(str(destination))
            choose_save_button.configure(state="disabled")
            document_operation("save", document_id=decision.document_id,
                               path=destination)
        elif decision.kind == "discard_then_close":
            choose_save_button.configure(state="disabled")
            document_operation("discard", document_id=decision.document_id)
        else:
            announce_document(decision.message)
            choose_save_button.configure(
                state="normal" if doc_dialog.phase == "awaiting_save_destination"
                else "disabled")

    def handle_document_confirmation(spoken: str) -> None:
        nonlocal last_user_for_document
        if save_only_waiting:
            receive_save_only_destination(spoken)
            return
        last_user_for_document = spoken
        if document_busy:
            announce_document("Operazione documento in corso; attendi.")
            return
        if doc_dialog.phase == "awaiting_save_destination":
            path = destination_from_voice(spoken)
            if path is not None:
                decision = doc_dialog.provide_destination(str(path))
                execute_document_choice(decision, path=path)
                return
        execute_document_choice(doc_dialog.reply(spoken))

    def press_discard_button() -> None:
        if doc_dialog.phase == "awaiting_close_choice":
            # The named button itself is an explicit decision after Jarvis
            # requested a choice; no extra spoken magic phrase.
            handle_document_confirmation("chiudi senza salvare")

    def choose_save_destination() -> None:
        nonlocal save_only_waiting
        if ((doc_dialog.phase!="awaiting_save_destination" and not save_only_waiting)
                or document_busy):
            return
        selected = filedialog.asksaveasfilename(
            parent=root, title="Dove vuoi salvare il nuovo file?",
            defaultextension=".txt", filetypes=[("File di testo", "*.txt")])
        if selected:
            if save_only_waiting:
                save_only_waiting=False
                document_operation("save_only",document_id=doc_dialog.document_id,
                                   path=Path(selected),source_utterance="salva documento")
            else:
                decision = doc_dialog.provide_destination(selected)
                execute_document_choice(decision, path=Path(selected))

    def sync_dictation_ui(message: str) -> None:
        dictation_status.set(message)
        dictation_button.configure(text="Disattiva dettatura" if dictation.enabled
                                  else "Attiva dettatura")
        if not closing:
            write_line(message)

    def toggle_dictation() -> None:
        if dictation.enabled:
            sync_dictation_ui(dictation.disable())
        elif voice_mode.get() == CONTINUOUS:
            sync_dictation_ui(dictation.enable())
        else:
            sync_dictation_ui("Seleziona prima Ascolto continuo per dettare.")



    def save_auto_listen_preference() -> None:
        """Only changes NEXT app launch, never the current listening mode."""
        desired = bool(auto_listen_enabled.get())
        previous = settings["auto_listen"]
        settings["auto_listen"] = desired
        try:
            save_settings(settings)
        except (OSError, ValueError) as exc:
            settings["auto_listen"] = previous
            auto_listen_enabled.set(previous)
            messagebox.showerror(
                "Impossibile salvare l'avvio automatico",
                str(exc)[:160], parent=root)
            return
        write_line(
            "SISTEMA > Al prossimo avvio microfono "
            + ("in conversazione locale con hotword Lumi." if desired
               else "in standby, come selezionato nelle impostazioni."))

    def change_voice_mode() -> None:
        nonlocal conversation_epoch
        selected = voice_mode.get()
        conversation_epoch += 1
        pending_conversation.clear()
        doc_dialog.revoke_pending()
        choose_save_button.configure(state="disabled")
        wake_gate.reset()
        voice.set_mode(selected)
        hud_mic_button.configure(
            text="●" if selected == STANDBY else "◉",
            fg="#67899c" if selected == STANDBY else CYAN)
        if selected != CONTINUOUS and dictation.enabled:
            sync_dictation_ui(dictation.disable())
        dictation_button.configure(state="normal" if selected == CONTINUOUS else "disabled")
        ptt_button.configure(state="normal" if selected == PUSH_TO_TALK else "disabled")
        if selected == STANDBY:
            mic_status.set("Microfono: SPENTO (standby)")
        elif selected == PUSH_TO_TALK:
            mic_status.set("Premi per parlare: microfono spento finché non tieni premuto.")
        elif selected == GPT_CONVERSATION:
            mic_status.set("Microfono attivo: inizia ogni richiesta con Lumi, "
                           "per esempio ‘Lumi, apri Netflix’. Il resto viene ignorato.")
            if not spoken_enabled.get():
                spoken_enabled.set(True)
                save_speech_preferences()
            write_line("Modalità Hey Lumi. Inizia ogni richiesta con Lumi.")
        else:
            mic_status.set("Ascolto continuo: parla direttamente. "
                           "La dettatura richiede l’attivazione manuale.")

    def ptt_press(event=None) -> None:
        if voice.press():
            mic_status.set("Premi per parlare: attivazione del microfono...")

    def ptt_release(event=None) -> None:
        voice.release()

    def journal_plan_approved(plan):
        """Capture the project identity before the plan's worker starts."""
        if active_project_id is None:
            return None
        tickets=[]
        project_id=active_project_id
        for step in plan.steps:
            ticket=begin_project_work(step.description,"planner",
                                      project_id=project_id,planned=True)
            if ticket is False:
                for prior in tickets:
                    finish_project_work(prior,"interrupted","Avvio piano non riuscito.")
                raise WorkspaceError("Impossibile memorizzare i passi: nessuna esecuzione.")
            tickets.append(ticket)
        return tuple(tickets)

    def journal_plan_step(tickets,index,status,message,receipt):
        if not tickets:
            return
        if not 1 <= index <= len(tickets):
            raise WorkspaceError("Indice passo fuori piano.")
        result=finish_project_work(
            tickets[index-1],
            "completed" if status=="completed" else "failed",
            message,receipt=receipt if status=="completed" else "")
        if not result:
            raise WorkspaceError("Esito del piano non registrato.")

    def journal_plan_finished(tickets,reason):
        if not tickets:
            return
        for ticket in tickets:
            # Completed steps are immutable; remaining planned steps are
            # interrupted. Nothing will be silently replayed on restart.
            finish_project_work(ticket,"interrupted","Piano terminato: "+reason)

    def submit_plan() -> None:
        if not gpt_enabled.get() or not active_gpt or busy_gpt or closing:
            return
        from local_model.online_permissions import authorize_online_request
        open_planner(
            root, service, engine,
            lambda: bool(gpt_enabled.get() and active_gpt and not busy_gpt and not closing),
            local_execution_lock, planner_abort_event,
            on_approved=journal_plan_approved,
            on_step=journal_plan_step,
            on_finished=journal_plan_finished,
            confirm_inference=lambda detail: authorize_online_request(
                "planner.create", confirm=lambda: confirm_gpt_inference(detail)),
            consent_generation=lambda: conversation_epoch,
        )

    def try_music_command(spoken: str) -> bool:
        if music_service is None or not music_service.is_enabled():
            return False
        from musica.commands import parse_command as parse_music_command
        request = parse_music_command(spoken)
        if request is None:
            return False
        # Una frase che Programmi e app riconosce (es. «metti Netflix» come
        # comando personalizzato) resta a Programmi e app.
        provider = getattr(engine, "program_apps", None)
        if request[0] == "play" and provider is not None:
            try:
                if provider.parse_command(spoken) is not None:
                    return False
            except Exception:
                pass
        message = music_service.handle(*request)
        if message:
            write_line("MUSICA > " + message)
            if request[0] == "play" and music_service.mode == "browser":
                speak_result(message)
        return True

    def try_timer_command(spoken: str) -> bool:
        alarm_request = parse_alarm_clock_command(spoken)
        if alarm_request:
            action, value = alarm_request
            if action == "clock":
                from datetime import datetime
                now = datetime.now()
                message = f"Sono le {now.hour:02d}:{now.minute:02d}."
            elif action == "stop":
                alarm.stop()
                message = "Sveglia fermata."
            else:
                message = alarm.arm(value)
            write_line("OROLOGIO > " + message)
            speak_result(message)
            return True
        parsed = parse_timer_command(spoken)
        if parsed is None:
            # Stesso punto d'ingresso dei comandi locali: la musica viene
            # provata solo dopo timer e sveglia, e solo con l'add-on attivo.
            return try_music_command(spoken)
        action = parsed.action
        if action == "start":
            if timer.start(parsed.seconds):
                write_line("TIMER > Avviato: " + timer.remaining_text())
            else:
                write_line("TIMER > Durata non valida.")
        elif action == "open":
            timer.show()
            write_line("TIMER > Aperto: modifica ore, minuti e secondi.")
        elif action == "pause":
            timer.pause()
            write_line("TIMER > In pausa.")
        elif action == "resume":
            timer.resume()
            write_line("TIMER > Ripreso.")
        elif action == "stop":
            timer.stop()
            write_line("TIMER > Fermato; allarme spento.")
        elif action == "reset":
            timer.reset()
            write_line("TIMER > Ripristinato.")
        elif action == "remaining":
            write_line("TIMER > Tempo rimasto: " + timer.remaining_text())
        return True

    def start_file_refinement(token, original, *, answer='') -> bool:
        """One model interpretation of an unresolved, locally scoped request."""
        if (closing or busy_gpt or not gpt_enabled.get() or not active_gpt
                or addon_manager is None or not addon_manager.files_enabled()):
            write_line("FILE > Nessun risultato utile; raffinamento GPT non disponibile. Puoi precisare la ricerca.")
            return False
        provider=addon_manager.file_service
        if not provider.refinement_live(token):
            return False
        from local_model.online_permissions import authorize_online_request
        permission = authorize_online_request(
            "files.search", confirm=lambda: confirm_gpt_inference(
                "La richiesta di ricerca e gli indizi sul nome del file o della cartella."))
        if permission is None:
            write_line("FILE > Richiesta GPT annullata. Puoi precisare la ricerca localmente.")
            return False
        feedback=provider.refinement_context(token,original,answer=answer)
        if feedback is None:
            return False
        original=feedback.pop('original')
        snapshot=documents.current.ident if documents.current else None
        try:
            live=current_capability_snapshot(snapshot is not None)
            prompt=build_conversation_prompt(original,has_document=snapshot is not None,
                runtime_info=capability_status_prompt(live),
                addon_actions=active_addon_actions(),file_feedback=feedback)
        except (ValueError,ConversationRejected) as exc:
            write_line("FILE > Raffinamento non avviato: "+str(exc))
            return False
        write_line("FILE > Chiedo al modello di precisare la stessa ricerca.")
        return run_gpt("typed_conversation",prompt=prompt,epoch=conversation_epoch,
                       document_id=snapshot,utterance=original,file_refinement=token,
                       capability="files.search", permission=permission)

    def accept_file_refinement(token, intent) -> bool:
        provider=addon_manager.file_service if addon_manager is not None and addon_manager.files_enabled() else None
        if provider is None or not provider.refinement_live(token):
            write_line("FILE > Risposta ignorata: ricerca cambiata, scaduta o revocata.")
            return False
        if intent.kind=='chat' or intent.kind=='clarify':
            if intent.kind=='clarify':
                provider.refinement_question(token,intent.reply)
            return True
        cap=intent.capability
        try:
            if intent.kind!='capability' or cap is None or cap.handler!='file_access':
                raise ValueError('Il modello non ha proposto la stessa ricerca file.')
            provider.refinement_arguments(token,cap.file_operation,dict(cap.file_arguments))
        except ValueError as exc:
            write_line("FILE > "+str(exc))
            return False
        return True

    def try_program_command(message: str) -> bool:
        provider=getattr(engine,'program_apps',None)
        if provider is None or not provider.available():
            return False
        # Document/project decisions retain their original routing and context.
        if (save_only_waiting or document_busy or doc_dialog.phase.startswith('awaiting_')
                or doc_dialog.phase=='executing' or pending_project_name
                or pending_project_rename_id is not None or pending_project_trash_id is not None):
            provider.reset(active_project_id)
            return False
        if provider._context != active_project_id:
            provider.reset(active_project_id)
        parsed=provider.parse_command(message)
        if parsed is None:
            return False
        if busy_local:
            write_line('PROGRAMMI > Operazione in corso: riprova fra poco.')
            return True
        if addon_manager is not None and addon_manager._file_service is not None:
            addon_manager.file_service.reset(active_project_id)
        submit_local(message_override=message,source_utterance=message,
                     addon_action_id='addon.programmi_app.avvia',program_call=parsed)
        return True

    def try_file_command(message: str) -> bool:
        if getattr(engine,'program_apps',None) is not None and try_program_command(message):
            return True
        if addon_manager is None or not addon_manager.files_enabled():
            return False
        try:
            provider=addon_manager.file_service
        except (ImportError,OSError,ValueError) as exc:
            write_line("ACCESSO FILE > Componente non disponibile: "+str(exc)+
                       ". Reinstalla la cartella file_access dal pacchetto completo e riavvia.")
            return True
        if provider._context != active_project_id:
            provider.reset(active_project_id)
        parsed=provider.parse_command(message)
        if parsed is None:
            pending=provider.pending_clarification()
            if pending is not None:
                # Parser failure is not evidence of a new task. Keep the live
                # local question available to the model without executing it.
                mode,token=pending
                if mode=="refinement":
                    start_file_refinement(token,message,answer=message)
                    return True
                return False
            # Without a live question, revoke an old unrelated selection.
            if getattr(provider,'_refinement',None) is not None or not any(word in message.casefold() for word in
                       ("file","cartella","quello","questo","aprilo","leggilo")):
                provider.reset(active_project_id)
            return False
        operation,args=parsed
        if operation=="refinement_answer":
            start_file_refinement(args['token'],message,answer=args['answer'])
            return True
        if operation=="cancel":
            provider.reset(active_project_id)
            write_line("FILE > Interruzione richiesta; attendo la chiusura della chiamata Windows.")
            return True
        if busy_local:
            write_line("FILE > Ricerca/operazione in corso. Puoi dire ‘annulla ricerca’.")
            return True
        submit_local(message_override=message,source_utterance=message,file_call=parsed)
        return True

    def submit_local(event=None, message_override: str | None = None,
                     source_utterance: str = "",
                     addon_action_id: str = "",
                     file_call=None, program_call=None) -> None:
        nonlocal busy_local, last_user_for_action, project_local_ticket
        nonlocal local_operation_id
        if closing:
            return
        if not addon_action_id:
            proposed = message_override if message_override is not None else request.get()
            if try_timer_command(proposed):
                if message_override is None:
                    request.set("")
                return
        if busy_local:
            return
        if addon_action_id and (addon_manager is None or not
                                addon_manager.is_active(addon_action_id)):
            write_line("ADD-ON > Comando rifiutato: add-on non più autorizzato.")
            return
        message = (message_override if message_override is not None else request.get()).strip()
        if not message:
            return
        if message_override is None:
            request.set("")
        write_line("COMANDO LOCALE > " + message)
        last_user_for_action = source_utterance or message
        project_local_ticket = begin_project_work(last_user_for_action,"local")
        if project_local_ticket is False:
            write_line("LUMI > Impossibile salvare il checkpoint: comando non eseguito.")
            return
        if operation_ledger is None:
            finish_project_work(project_local_ticket,"interrupted",
                                "Registro operativo non disponibile.")
            project_local_ticket=None
            write_line("LUMI > Registro operativo non disponibile: non eseguo.")
            return
        try:
            local_operation_id=operation_ledger.begin(
                "local_request",origin="local",project_id=active_project_id or "")
            operation_ledger.running(local_operation_id)
        except (OSError,sqlite3.Error,MemoryBoundaryError) as exc:
            finish_project_work(project_local_ticket,"interrupted",
                                "Impossibile registrare l'operazione.")
            project_local_ticket=None
            write_line("LUMI > Operazione bloccata: "+str(exc)[:95])
            return
        busy_local = True
        refresh_buttons()

        def worker() -> None:
            try:
                with local_execution_lock:
                    if addon_action_id and (
                            addon_manager is None or not
                            addon_manager.is_active(addon_action_id)):
                        result=TaskResult("-","addon","rejected",
                                          "Add-on disattivato prima dell'esecuzione.")
                    else:
                        result = (engine.execute_program(*program_call) if program_call is not None
                                  else engine.execute_file(*file_call) if file_call is not None
                                  else engine.execute(message))
                output_queue.put(("local", result))
            except Exception as exc:
                output_queue.put(("local", TaskResult("-", "internal", "failed",
                    "Errore locale ("+type(exc).__name__+"): operazione non completata.")))
        threading.Thread(target=worker, daemon=True).start()

    def dispatch_model_capability(cap, original_phrase, doc_snapshot, refinement_token=None):
        """Shared validated capability dispatch for online and native replies."""
        current_id = (documents.current.ident
                      if documents.current else None)
        if cap is None:
            announce_document("Azione non disponibile.")
        elif cap.handler == 'program_apps':
            from program_apps.service import blocked, protected
            if (blocked(original_phrase) or protected(original_phrase)
                    or save_only_waiting or document_busy
                    or doc_dialog.phase.startswith('awaiting_')
                    or doc_dialog.phase=='executing'):
                speak_result('Nessuna app avviata: richiesta negata o altro dialogo in corso.')
            elif addon_manager is None or not addon_manager.is_active(cap.action_id):
                speak_result('Programmi e app non è più attivo.')
            elif not busy_local:
                submit_local(message_override=original_phrase,
                    source_utterance=original_phrase,addon_action_id=cap.action_id,
                    program_call=('launch',{'query':cap.target}))
            else:
                speak_result('Operazione locale in corso, riprova.')
        elif cap.handler == "file_access":
            if (addon_manager is None or not addon_manager.is_active(cap.action_id)):
                speak_result("Accesso file non è più attivo.")
            elif not busy_local:
                submit_local(message_override=original_phrase,
                    source_utterance=original_phrase,addon_action_id=cap.action_id,
                    file_call=(cap.file_operation,
                        addon_manager.file_service.arguments_for_utterance(
                            cap.file_operation,dict(cap.file_arguments),original_phrase),
                        refinement_token) if refinement_token else (cap.file_operation,
                        addon_manager.file_service.arguments_for_utterance(
                            cap.file_operation,dict(cap.file_arguments),original_phrase)))
            else:
                speak_result("Operazione file già in corso.")
        elif cap.handler == "local" and cap.plan is not None:
            # A GPT proposal cannot retain permission after
            # a local add-on is disabled or uninstalled.
            if (cap.action_id.startswith("addon.") and
                    (addon_manager is None or not
                     addon_manager.is_active(cap.action_id))):
                speak_result("L'add-on non è più attivo.")
            elif not busy_local:
                submit_local(
                    message_override=cap.plan.steps[0].command,
                    source_utterance=original_phrase,
                    addon_action_id=(cap.action_id if
                        cap.action_id.startswith("addon.")
                        else ""))
            else:
                speak_result("Operazione in corso, riprova.")
        elif cap.handler == "telegram_voice_dialog":
            # GPT proposes a name, it never authorizes
            # a contact or sends audio. Local selection
            # and two-step owner confirmation are final.
            try_telegram_voice_send(
                "manda un messaggio a "+cap.recipient)
        elif cap.handler == "document_open":
            if current_id is None:
                document_operation(
                    "open", source_utterance=original_phrase)
            else:
                announce_document(
                    "C'è già un Blocco note gestito da Lumi. "
                    "Dimmi cosa vuoi scriverci.")
        elif cap.handler == "document_close":
            if (doc_snapshot is not None
                    and current_id == doc_snapshot):
                ask_to_close_document(original_phrase)
            else:
                announce_document(
                    "Il documento è cambiato; non chiudo nulla.")
        elif cap.handler == "document_write":
            if cap.target == "selected_document" and (
                    doc_snapshot is None
                    or current_id != doc_snapshot):
                announce_document(
                    "La finestra è cambiata: nessun testo inserito.")
            elif cap.target == "new_notepad" and current_id:
                announce_document(
                    "C'è già un documento aperto. "
                    "Vuoi aggiungere il testo a quello?")
            else:
                document_operation(
                    "compose", content=cap.content,
                    target=cap.target,
                    close_after=cap.close_after,
                    source_utterance=original_phrase)
        else:
            announce_document("Azione del catalogo non attiva.")

    def submit_gpt() -> None:
        if closing:
            return
        try:
            chat_is_visible = chat_notebook.select() == str(chat_local_tab)
        except NameError:
            chat_is_visible = False
        if chat_is_visible:
            write_line("CHAT > Invio GPT bloccato: questa istanza è solo locale.")
            chat_sessions_panel.report_error(
                "F2: seleziona Console per inviare a GPT online.")
            return
        message = request.get().strip()
        if not message:
            return
        if try_file_command(message):
            request.set("")
            return
        # Timer commands are local, independent of GPT connectivity.
        if try_timer_command(message):
            request.set("")
            return
        # The "Chiedi a GPT" control must not bypass local diagnostics.
        # This stays usable offline and avoids a misleading GPT refusal.
        if try_self_diagnostic(message):
            request.set("")
            return
        if not gpt_enabled.get() or not active_gpt or busy_gpt:
            return
        reconcile_document_session(force=True)
        if project_voice_command(message):
            request.set("")
            return
        if preference_command(message):
            request.set("")
            return
        if handle_project_reference(message):
            request.set("")
            return
        if handle_unanchored_short_reply(message):
            request.set("")
            return
        if len(message) > 5000:
            messagebox.showwarning("Testo troppo lungo", "Massimo 5000 caratteri.", parent=root)
            return
        document_snapshot=(documents.current.ident if documents.current else None)
        try:
            live=current_capability_snapshot(document_snapshot is not None)
            if len(message)<=450:
                # Typed commands must use the SAME reviewed capability contract
                # as voice, not a text-only model that falsely says it cannot act.
                prompt=build_conversation_prompt(
                    message,has_document=document_snapshot is not None,
                    memory_context=recent_memory_for_gpt(message),
                    telegram_send_ready=live["telegram_voice_send"],
                    runtime_info=capability_status_prompt(live),
                    addon_actions=active_addon_actions())
                if run_gpt("typed_conversation",prompt=prompt,
                           epoch=conversation_epoch,
                           document_id=document_snapshot,utterance=message):
                    request.set("")
                    write_line("DOMANDA A GPT > " + message)
                return
            # Longer free-form questions are conversational only; never
            # interpret a 5000-character document as an executable action.
            prompt = build_chat_prompt(
                message, memory_context=recent_memory_for_gpt(message),
                runtime_info=capability_status_prompt(live))
        except (ValueError,ConversationRejected) as exc:
            request.set(message)
            write_line("LUMI > " + str(exc))
            return
        if run_gpt("ask", prompt=prompt, source=message):
            request.set("")
            write_line("DOMANDA A GPT > " + message)

    def diagnostic_heartbeat() -> None:
        """Independent watchdog: runs even if another event handler fails."""
        nonlocal diagnostic_busy,pending_external_review,last_runtime_evidence
        if closing:
            return
        root.after(800,diagnostic_heartbeat)
        check=diagnostic_session.check()
        if check=="timeout":
            diagnostic_busy=False
            pending_external_review=False
            last_runtime_evidence=None
            runtime_events.record("diagnostic_failure")
            update_diagnostic_ui()
            write_line("DIAGNOSTICA > Tempo massimo superato (120 s). "
                       "Ho sbloccato l'interfaccia; il vecchio controllo "
                       "potrebbe ancora essere attivo. Risultati tardivi ignorati.")
            speak_result("La diagnosi non risponde. "
                         "Ho sbloccato i comandi, senza modificare file.")
        elif check=="stalled":
            update_diagnostic_ui()
            write_line("DIAGNOSTICA > Nessun avanzamento da 12 secondi. "
                       "Il controllo è ancora attivo; scadrà dopo 120 secondi.")
        elif diagnostic_session.active:
            update_diagnostic_ui()

    def poll() -> None:
        """Always schedule another UI tick before consuming potentially bad events."""
        nonlocal busy_local, busy_gpt, active_gpt, conversation_epoch, document_busy
        nonlocal local_operation_id, document_operation_id
        nonlocal diagnostic_busy,last_diagnostic_audit,last_runtime_evidence,pending_external_review
        nonlocal telegram_owner_busy
        nonlocal last_user_for_action, last_user_for_document
        nonlocal project_local_ticket, project_document_ticket
        nonlocal document_topic,document_owner_project_id,save_only_waiting
        if closing:
            return
        # A malformed or unexpected event must not permanently kill the
        # event pump and strand an in-progress diagnostic forever.
        root.after(120, poll)
        try:
            reconcile_document_session()
        except (OSError,ValueError,TypeError,RuntimeError) as exc:
            runtime_events.record("document_failure")
            write_line("DOCUMENTI > Controllo sessione non riuscito: "+
                       type(exc).__name__)
        try:
            # Never starve Tk on a burst of voice, GPT or diagnostic events.
            # Remaining events are processed during the next 120 ms tick.
            for _ in range(80):
                kind, *data = output_queue.get_nowait()
                # Mode changes revoke voice events already in the shared queue.
                # Check before status, logging, dictation or command/model work;
                # other producers keep their existing event contracts.
                if kind in ("voice_text", "voice_status") and (
                        len(data) != 2 or not isinstance(data[0], str)
                        or not voice.accepts_event(data[1])):
                    continue
                if kind == "self_audit_progress":
                    run_id,phase,completed,total=data
                    if diagnostic_session.progress(
                            run_id,phase,completed,total):
                        update_diagnostic_ui()
                        if completed==0 or phase=="inventario":
                            write_line("DIAGNOSTICA > "+phase+
                                       ": "+str(completed)+"/"+str(total)+
                                       " file.")
                elif kind == "self_audit":
                    run_id,audit=data
                    if not diagnostic_session.finish(run_id,succeeded=True):
                        # Late result of a timed-out run: NEVER replace
                        # a newer diagnosis or send it to GPT.
                        continue
                    diagnostic_busy=False
                    update_diagnostic_ui()
                    write_line("DIAGNOSTICA > Verifica locale terminata.")
                    last_diagnostic_audit=audit
                    # Real, read-only component observations from this instance.
                    # Never claim these are end-to-end tests or Windows logs.
                    try:
                        last_runtime_evidence=snapshot_runtime_evidence()
                        write_line("DIAGNOSTICA > "+
                                   format_runtime_evidence(last_runtime_evidence))
                    except (OSError,ValueError,TypeError,AttributeError):
                        last_runtime_evidence=None
                        write_line("DIAGNOSTICA > Stato runtime non rilevabile; "
                                   "rimane disponibile la sola verifica statica.")
                    write_line("DIAGNOSTICA > "+format_audit(audit))
                    write_line("DIAGNOSTICA > Se vuoi un parere del modello "
                               "esterno, puoi chiedere: "
                               "'Lumi, valuta la diagnosi con GPT'. "
                               "Prima di inviare dati chiederò il consenso.")
                    if audit.recommendations:
                        first=audit.recommendations[0]
                        message=(str(len(audit.recommendations))+
                                 " possibili miglioramenti da verificare. "
                                 "Il primo riguarda "+first.file+
                                 ": "+first.suggestion+
                                 " Ho scritto le motivazioni e i controlli nel registro.")
                    else:
                        message=("Non ho trovato problemi evidenti da questi "
                                 "controlli statici. Non significa che tutte "
                                 "le funzioni siano state provate. "
                                 "Trovi il resoconto nel registro.")
                    speak_result(message)
                    if pending_external_review:
                        pending_external_review=False
                        offer_external_diagnostic_review()
                elif kind == "self_audit_error":
                    run_id,error_type=data
                    if not diagnostic_session.finish(run_id,succeeded=False):
                        continue
                    diagnostic_busy=False
                    pending_external_review=False
                    last_runtime_evidence=None
                    runtime_events.record("diagnostic_failure")
                    update_diagnostic_ui()
                    write_line("DIAGNOSTICA > Analisi non completata. "
                               "Errore locale: "+str(error_type)[:90]+
                               ". Puoi riprovare con il pulsante.")
                    speak_result("La diagnosi non è riuscita. "
                                 "Ho scritto il tipo di errore nella console.")
                elif kind == "project_journal_error":
                    runtime_events.record("project_journal_failure")
                    workspace_status.set("Esito progetto non registrato: "+str(data[0])[:100])
                elif kind == "telegram_contacts_loaded":
                    if (telegram_contacts_dialog is not None
                            and telegram_contacts_dialog.exists()):
                        telegram_contacts_dialog.loaded(data[0])
                    else:
                        write_line("TELEGRAM > Elenco contatti caricato; "
                                   "riapri Gestisci contatti.")
                elif kind == "telegram_contacts_error":
                    if (telegram_contacts_dialog is not None
                            and telegram_contacts_dialog.exists()):
                        telegram_contacts_dialog.failed(data[0])
                    telegram_status.set("Telegram: impossibile caricare contatti "
                                        +str(data[0])[:90])
                elif kind == "telegram_owner_sent":
                    telegram_owner_busy=False
                    peer_id,display_name,msg_id,written=data
                    # Telegram returned a message ID; record separately by peer.
                    if workspace is not None:
                        try:
                            workspace.telegram_event(
                                peer_id,"outgoing",msg_id,"voice",written)
                        except (OSError,sqlite3.Error,WorkspaceError):
                            write_line("TELEGRAM > Vocale inviato, "
                                       "ma archivio locale non aggiornato.")
                    write_line("TELEGRAM > Messaggio vocale inviato a "+
                               str(display_name)[:90]+" (ricevuta Telegram).")
                    speak_result("Messaggio vocale inviato a "+str(display_name)[:90]+".")
                elif kind == "telegram_owner_error":
                    telegram_owner_busy=False
                    error_type,reason=data
                    write_line("TELEGRAM > Invio non confermato ("+
                               str(error_type)[:50]+"): "+str(reason)[:150])
                    speak_result("Non posso confermare l'invio Telegram. "
                                 "Controlla la chat prima di riprovare.")
                elif kind == "telegram_gpt_consent":
                    resolve_telegram_gpt_consent(*data)
                elif kind == "telegram_status":
                    telegram_status.set(str(data[0])[:220])
                    write_line("TELEGRAM > "+str(data[0])[:170])
                elif kind == "telegram_received":
                    who,format_type=data
                    write_line("TELEGRAM > Ricevuto da "
                               +str(who)[:55]+" ("+str(format_type)+").")
                elif kind == "telegram_sent":
                    write_line("TELEGRAM > Risposta vocale inviata a "
                               +str(data[0])[:55]+".")
                elif kind == "telegram_stopped":
                    if telegram_bridge and data and data[0] != id(telegram_bridge):
                        continue
                    if telegram_auto.get():
                        runtime_events.record("telegram_disconnected")
                        telegram_auto.set(False)
                        settings["telegram_enabled"]=False
                        try:
                            save_settings(settings)
                        except (OSError,ValueError):
                            pass
                        telegram_status.set("Telegram: collegamento terminato.")
                elif kind == "voice_status":
                    if str(data[0]).startswith(("Microfono spento", "Voce non disponibile")):
                        runtime_events.record("voice_unavailable")
                    if voice_mode.get() != STANDBY:
                        mic_status.set(data[0])
                        if str(data[0]).startswith("Voce non disponibile"):
                            write_line("MICROFONO > " + str(data[0]))
                    if (dictation.enabled and
                            (str(data[0]).startswith("Microfono spento") or
                             str(data[0]).startswith("Voce non disponibile"))):
                        sync_dictation_ui(dictation.disable())
                elif kind == "voice_text":
                    raw_spoken = str(data[0]).strip()
                    spoken = raw_spoken
                    route_type = "command"  # Push-to-talk is already intentional.
                    if (voice_mode.get() == GPT_CONVERSATION
                            or voice_mode.get() == CONTINUOUS):
                        if not raw_spoken or speaker.is_audible():
                            continue
                        # Check the RAW local transcript before learned
                        # corrections, logging, local actions or GPT queuing.
                        route_type, spoken = wake_gate.route(
                            raw_spoken, require_name=True,
                            dictation_active=(voice_mode.get() != GPT_CONVERSATION
                                              and dictation.enabled))
                        if (route_type == "ignored" and voice_mode.get() == CONTINUOUS
                                and not dictation.enabled):
                            route_type, spoken = "command", raw_spoken
                        if route_type == "dictation" and dictation_voice_action(raw_spoken) == "stop":
                            route_type = "command"
                        if route_type == "wake":
                            if voice_mode.get() == GPT_CONVERSATION:
                                mic_status.set("Dì Lumi seguito dalla richiesta nella stessa frase.")
                        if route_type not in ("command", "dictation"):
                            continue
                    if raw_spoken and voice_mode.get() != STANDBY:
                        # No new acoustic model or background training:
                        # correct approved app names in a single cached pass.
                        last_voice_sample.set(raw_spoken)
                        if speech_lexicon is not None and memory_enabled.get():
                            uncorrected = spoken
                            spoken = speech_lexicon.correct(uncorrected)
                            if spoken != uncorrected:
                                write_line("VOCABOLARIO LIA > " + spoken)
                    if voice_mode.get() != STANDBY and spoken and not speaker.is_audible():
                        if route_type == "dictation":
                            sync_dictation_ui(dictation.insert(spoken))
                            continue
                        from voice_control import model_switch_target
                        if model_switch_target(spoken) is not None and try_model_switch(spoken):
                            continue
                        if voice_mode.get() in (GPT_CONVERSATION, CONTINUOUS, PUSH_TO_TALK):
                            write_line("TU > " + spoken)
                            if try_file_command(spoken):
                                continue
                            if try_timer_command(spoken):
                                continue
                            # Safe local diagnostics must not wait for a GPT
                            # response or a stale Notepad confirmation.
                            if try_self_diagnostic(spoken):
                                continue
                            if try_telegram_voice_send(spoken):
                                continue
                            # Pending save/close decisions are handled locally.
                            if save_only_waiting:
                                receive_save_only_destination(spoken)
                                continue
                            if doc_dialog.phase.startswith("awaiting_"):
                                handle_document_confirmation(spoken)
                                continue
                            if doc_dialog.phase == "executing" or document_busy:
                                write_line("Blocco note: operazione in corso, attendi.")
                                continue
                            # "Salva" writes a file but leaves Notepad open;
                            # only "salva e chiudi" closes the owned document.
                            explicit_name=parse_simple_save(spoken)
                            if (doc_dialog.phase=="editing" and
                                    explicit_name is not None):
                                save_document_now(spoken,explicit_name=explicit_name)
                                continue
                            # An explicit natural phrase to discard changes
                            # is a single authorization: do not ask twice.
                            direct_choice = classify_document_choice(
                                spoken, pending=False)
                            if (doc_dialog.phase == "editing" and
                                    direct_choice in ("save", "discard")):
                                decision = doc_dialog.request_close_with_choice(spoken)
                                last_user_for_document = spoken
                                execute_document_choice(decision)
                                continue
                            normalized = " ".join(spoken.casefold().strip(" ,.!?").split())
                            if normalized in (
                                "chiudi blocco note", "chiudi il blocco note",
                                "chiudi il documento", "chiudi documento",
                                "chiudi il file", "chiudi file", "chiudilo",
                            ):
                                ask_to_close_document(spoken)
                                continue
                            if voice_mode.get() == CONTINUOUS:
                                dictation_action = dictation_voice_action(spoken)
                                if dictation_action == "stop":
                                    sync_dictation_ui(dictation.disable())
                                    continue
                                if dictation_action == "start":
                                    sync_dictation_ui(dictation.enable())
                                    continue
                            if project_voice_command(spoken):
                                continue
                            if preference_command(spoken):
                                continue
                            if handle_project_reference(spoken):
                                continue
                            if handle_unanchored_short_reply(spoken):
                                continue
                            if try_self_diagnostic(spoken):
                                continue
                            if maybe_queue_telegram_note(spoken):
                                continue
                            # Fixed local actions do not require an online model.
                            command = speech_to_local_command(spoken)
                            if command == "apri blocco note":
                                document_operation("open", source_utterance=spoken)
                            elif command:
                                if not busy_local:
                                    submit_local(message_override=command,
                                                 source_utterance=spoken)
                                else:
                                    write_line("Motore locale occupato: riprova.")
                            else:
                                if not gpt_enabled.get() and gemma_trial_busy[0]:
                                    write_line("LUMI > Sto ancora elaborando. "
                                               "Ripeti la frase al termine.")
                                else:
                                    start_conversation_gpt(spoken)
                            continue
                        # Log commands that passed the wake/press gate.
                        # Do not record free dictation or phrases ignored by wake.
                        write_line("TU > " + spoken)
                        if try_file_command(spoken):
                            continue

                        if try_timer_command(spoken):
                            continue
                        if try_self_diagnostic(spoken):
                            continue
                        if try_telegram_voice_send(spoken):
                            continue
                        dictation_action = dictation_voice_action(spoken)
                        if dictation_action == "stop":
                            sync_dictation_ui(dictation.disable())
                        elif dictation_action == "start":
                            if voice_mode.get() == CONTINUOUS:
                                sync_dictation_ui(dictation.enable())
                            else:
                                sync_dictation_ui(
                                    "Per dettare in altre finestre seleziona Ascolto continuo.")
                        elif save_only_waiting:
                            receive_save_only_destination(spoken)
                        elif project_voice_command(spoken):
                            pass
                        elif preference_command(spoken):
                            pass
                        elif handle_project_reference(spoken):
                            pass
                        elif handle_unanchored_short_reply(spoken):
                            pass
                        elif try_self_diagnostic(spoken):
                            pass
                        elif doc_dialog.phase=="editing" and parse_simple_save(spoken) is not None:
                            save_document_now(spoken,explicit_name=parse_simple_save(spoken))
                        else:
                            command = speech_to_local_command(spoken)
                            if command and not busy_local:
                                submit_local(message_override=command,
                                             source_utterance=spoken)
                            elif command:
                                write_line("Motore occupato; comando non eseguito.")
                            elif not dictation.enabled and not request.get().strip():
                                request.set(spoken)
                                write_line("Testo inserito: controllalo prima di eseguirlo.")
                            elif not dictation.enabled:
                                write_line("Testo non eseguito: il campo contiene già una richiesta.")
                            else:
                                write_line("Comando non riconosciuto; dettatura invariata.")
                elif kind == "file_progress":
                    if (addon_manager is not None and addon_manager.files_enabled()
                            and addon_manager.file_service.accepts_progress(data[0])):
                        try:
                            from file_access.ui import show_result_progress
                            show_result_progress(root,data[0])
                        except (ImportError,OSError,ValueError,tk.TclError) as exc:
                            write_line("ACCESSO FILE > Avanzamento visuale non disponibile: "+str(exc)[:120])
                elif kind == "local":
                    result = data[0]
                    if result.status in ("failed", "rejected"):
                        runtime_events.record("local_failure")
                    busy_local = False
                    if getattr(result,'program_listing',None) is not None:
                        try:
                            from program_apps.ui import show_choices
                            show_choices(root,result.program_listing,
                                lambda number,token:submit_local(
                                    message_override='Avvia programma scelto',
                                    source_utterance='Programma scelto nella finestra risultati',
                                    addon_action_id='addon.programmi_app.avvia',
                                    program_call=('select',{'query':number,'token':token})))
                        except (ImportError,OSError,ValueError,tk.TclError) as exc:
                            write_line('PROGRAMMI > Finestra scelte non disponibile: '+str(exc)[:150])
                    if result.action.startswith('files_') and result.file_listing is None:
                        try:
                            from file_access.ui import finish_result_progress
                            finish_result_progress(root,result.message)
                        except (ImportError,OSError,ValueError,tk.TclError) as exc:
                            write_line("ACCESSO FILE > Stato ricerca non aggiornato: "+str(exc)[:120])
                    if result.file_listing is not None:
                        from dataclasses import replace
                        listing=result.file_listing
                        result=replace(result,message=listing['summary'])
                        try:
                            from file_access.ui import show_results
                            show_results(root,listing,
                                on_open=lambda number,token:submit_local(
                                    message_override='Apri risultato '+str(number),
                                    source_utterance='Risultato scelto nella finestra file',
                                    file_call=('select',{'target':str(number),'selection_id':token,'open':True})),
                                on_select=lambda number,token,hwnd:addon_manager.file_service.mark_view_selection(number,token,hwnd))
                        except (ImportError,OSError,ValueError,tk.TclError) as exc:
                            write_line("ACCESSO FILE > Finestra risultati non disponibile: "+str(exc)[:140]+
                                       ". Reinstalla file_access/ui.py dal pacchetto completo.")
                    elif result.action=='files_select' and result.status=='completed':
                        try:
                            from file_access.ui import sync_result_selection
                            sync_result_selection(root,addon_manager.file_service)
                        except (ImportError,OSError,ValueError,tk.TclError) as exc:
                            write_line("ACCESSO FILE > Selezione visuale non aggiornata: "+str(exc)[:140])
                    write_line(f"[{result.status}] {result.message}")
                    if result.preview_path:
                        try:
                            from file_access.ui import show_preview
                            show_preview(root,result.preview_path,result.preview)
                        except (ImportError,OSError,ValueError) as exc:
                            write_line("ACCESSO FILE > Vista non disponibile: "+str(exc)+
                                       ". Reinstalla file_access/ui.py dal pacchetto completo.")
                        if result.explain:
                            if gpt_enabled.get() and active_gpt and not busy_gpt:
                                from file_access.service import explanation_prompt
                                run_gpt("ask",prompt=explanation_prompt(result.preview),
                                        source="Spiega il file letto su mia richiesta",
                                        capability="files.explain",
                                        consent_detail="Il testo mostrato nell’anteprima del file.")
                            else:
                                write_line("FILE > Testo letto. Per spiegarlo collega GPT e ripeti ‘spiega file …’.")
                    source = last_user_for_action or result.action
                    last_user_for_action = ""
                    # A successful subprocess launch is only reported, not
                    # proof that the requested window became usable.
                    observed=observed_local_result(result)
                    if operation_ledger is not None and local_operation_id:
                        try:
                            operation_ledger.finish(
                                local_operation_id,
                                ("verified" if observed else "reported"
                                 if result.status=="completed" else "failed"),
                                receipt=result.task_id if observed else "",
                                observed=observed,action=result.action
                                if result.action!="internal" else "local_error")
                        except (OSError,sqlite3.Error,MemoryBoundaryError) as exc:
                            write_line("LUMI > Registro operazioni: "+str(exc)[:90])
                    local_operation_id=None
                    finish_project_work(project_local_ticket,
                        "completed" if result.status=="completed" else "failed",
                        result.message,receipt=result.task_id if result.status=="completed" else "",
                        observed=observed)
                    project_local_ticket = None
                    remember_exchange(
                        source, result.message,
                        "action" if result.status == "completed" else "error")
                    if result.status == "completed":
                        remember_completed_action(
                            result.action, result.action.split("_")[0],
                            result.message, result.task_id,observed=observed)
                        spoken=(result.message if result.spoken_message is None
                                else result.spoken_message)
                        if spoken:
                            speak_result(spoken)
                    if result.file_listing is not None and result.file_listing.get('refinement'):
                        start_file_refinement(result.file_listing['refinement'],source)
                elif kind == "document_ok":
                    document_busy = False
                    operation, result, close_after = data
                    if result.kind in ("opened", "created"):
                        if doc_dialog.document_id not in (None, result.document_id):
                            # Earlier controlled window was closed manually.
                            doc_dialog.reset()
                        if doc_dialog.phase == "idle":
                            doc_dialog.begin(
                                result.document_id, "Nuovo Blocco note",
                                dirty=True, saved_path=None)
                    elif result.kind == "appended":
                        if doc_dialog.phase == "editing":
                            doc_dialog.mark_dirty()
                    elif result.kind in ("saved_and_closed", "closed_without_saving",
                                         "closed"):
                        if doc_dialog.phase == "executing":
                            doc_dialog.operation_completed(
                                result.document_id, succeeded=True)
                        choose_save_button.configure(state="disabled")
                    elif result.kind in ("saved_but_open","saved_open"):
                        if doc_dialog.phase == "executing":
                            doc_dialog.operation_completed(
                                result.document_id, succeeded=False)
                        if result.saved_path is not None:
                            doc_dialog.saved_path = str(result.saved_path)
                        choose_save_button.configure(state="disabled")
                    if result.kind in ("saved_and_closed","closed_without_saving","closed"):
                        document_topic=""
                        document_owner_project_id=None
                        save_only_waiting=False
                    announce_document(result.message)
                    source = last_user_for_document or operation
                    last_user_for_document = ""
                    # File presente sul disco: prova di salvataggio. Una finestra
                    # lanciata o modificata non è invece osservata indipendentemente.
                    saved_file=getattr(result,"saved_path",None)
                    observed_file=observed_saved_file(result)
                    if operation_ledger is not None and document_operation_id:
                        try:
                            operation_ledger.finish(
                                document_operation_id,
                                "verified" if observed_file else "reported",
                                receipt="file:"+str(result.document_id)[:65]
                                if observed_file else "",observed=observed_file,
                                action="notepad."+operation)
                        except (OSError,sqlite3.Error,MemoryBoundaryError) as exc:
                            write_line("LUMI > Registro documento: "+str(exc)[:90])
                    document_operation_id=None
                    finish_project_work(project_document_ticket,"completed",result.message,
                                        receipt=str(result.document_id)+":"+result.kind,
                                        observed=observed_file)
                    if (project_document_ticket and workspace is not None
                            and getattr(result,"saved_path",None) is not None):
                        try:
                            workspace.record_artifact(project_document_ticket[0],result.saved_path)
                        except (OSError,sqlite3.Error,WorkspaceError,ValueError) as exc:
                            workspace_status.set("File non registrato: "+str(exc)[:110])
                    project_document_ticket = None
                    remember_exchange(source, result.message, "action")
                    if result.kind in ("opened", "created", "appended",
                                       "saved_and_closed", "closed_without_saving",
                                       "saved_but_open", "saved_open", "closed"):
                        from uuid import uuid4
                        action_name = ("notepad.open" if result.kind == "opened"
                                       else "notepad.write" if result.kind in (
                                           "created", "appended")
                                       else "notepad.save" if result.kind in ("saved_but_open","saved_open")
                                       else "notepad.close")
                        filename = (result.saved_path.name
                                    if result.saved_path is not None else "")
                        folder = (result.saved_path.parent.name
                                  if result.saved_path is not None else "")
                        remember_completed_action(
                            action_name, "Blocco note", result.message,
                            "jarvis:" + uuid4().hex,
                            filename=filename, folder=folder,observed=observed_file)
                    if close_after and result.kind in ("created", "appended"):
                        ask_to_close_document(source)
                elif kind == "document_error":
                    runtime_events.record("document_failure")
                    document_busy = False
                    operation, reason = data
                    if doc_dialog.phase == "executing" and doc_dialog.document_id:
                        doc_dialog.operation_completed(
                            doc_dialog.document_id, succeeded=False)
                    if documents.current is None and doc_dialog.phase == "editing":
                        doc_dialog.reset()
                    if operation in ("open", "compose") and (
                            doc_dialog.phase == "idle" and documents.current is not None):
                        # The window may have opened before insertion failed.
                        # Keep control of it; never lose the ability to close it.
                        doc_dialog.begin(documents.current.ident,
                                         "Nuovo Blocco note", dirty=True)
                    choose_save_button.configure(state="disabled")
                    error_message = "Operazione non riuscita; nessun documento chiuso: " + reason
                    announce_document(error_message)
                    if operation_ledger is not None and document_operation_id:
                        try:
                            operation_ledger.finish(document_operation_id,"failed",
                                                    action="notepad."+operation)
                        except (OSError,sqlite3.Error,MemoryBoundaryError) as exc:
                            write_line("LUMI > Registro documento: "+str(exc)[:90])
                    document_operation_id=None
                    finish_project_work(project_document_ticket,"failed",error_message)
                    project_document_ticket = None
                    remember_exchange(last_user_for_document or operation,
                                      error_message, "error")
                    last_user_for_document = ""
                elif kind == "conversation_ok":
                    busy_gpt = False
                    epoch, doc_snapshot, original_phrase, result, *channels = data
                    channel=channels[0] if channels else "conversation"
                    refinement_token=channels[1] if len(channels)>1 else None
                    if (epoch == conversation_epoch and
                            (channel=="typed_conversation" or
                             voice_mode.get() in (GPT_CONVERSATION, CONTINUOUS, PUSH_TO_TALK)) and
                            gpt_enabled.get() and active_gpt):
                        try:
                            latest=current_capability_snapshot(documents.current is not None)
                            intent = parse_conversation_intent(
                                result.get("text", ""),
                                utterance=original_phrase,
                                has_document=doc_snapshot is not None,
                                telegram_send_ready=latest["telegram_voice_send"],
                                addon_resolver=(addon_manager.resolve
                                                if addon_manager is not None
                                                else None))
                        except ConversationRejected as exc:
                            write_line("GPT: impossibile interpretare la risposta: " + str(exc))
                            speak_result("Non ho capito con sicurezza. Puoi ripetere?")
                            remember_exchange(
                                original_phrase, "Non ho capito con sicurezza. Puoi ripetere?",
                                "clarify")
                        else:
                            if refinement_token and not accept_file_refinement(refinement_token,intent):
                                continue
                            if (is_ambiguous_short_reply(original_phrase)
                                    and intent.kind not in ("chat","clarify")):
                                message=("Per eseguire un'azione, dimmi "
                                         "esplicitamente cosa vuoi fare.")
                                write_line("LUMI > "+message)
                                speak_result(message)
                                remember_exchange(original_phrase,message,"clarify")
                                continue
                            if intent.kind in ("chat", "clarify"):
                                if (not refinement_token and intent.kind=="clarify" and addon_manager is not None
                                        and addon_manager.files_enabled()):
                                    addon_manager.file_service.remember_file_clarification(original_phrase)
                                write_line("LUMI > " + intent.reply)
                                speak_result(intent.reply)
                                remember_exchange(original_phrase, intent.reply,
                                                  intent.kind)
                            elif intent.kind == "capability":
                                dispatch_model_capability(
                                    intent.capability, original_phrase, doc_snapshot, refinement_token)
                            elif intent.kind == "tool":
                                if intent.plan is None or busy_local:
                                    speak_result("Sono occupato, riprova.")
                                elif intent.plan.steps[0].command == "apri blocco note":
                                    document_operation(
                                        "open", source_utterance=original_phrase)
                                else:
                                    submit_local(message_override=intent.plan.steps[0].command,
                                                 source_utterance=original_phrase)
                            elif intent.kind == "compose_document":
                                current_id = (documents.current.ident
                                              if documents.current else None)
                                if intent.target == "selected_document" and (
                                        current_id is None or current_id != doc_snapshot):
                                    announce_document(
                                        "Il documento selezionato è cambiato o non è gestito "
                                        "da Lumi. Non ho inserito il testo.")
                                elif current_id is not None and intent.target == "new_notepad":
                                    announce_document(
                                        "C'è già un documento aperto da Lumi. "
                                        "Per aggiungere testo a quello, chiedimi di scriverci.")
                                else:
                                    document_operation(
                                        "compose", content=intent.content,
                                        target=intent.target,
                                        close_after=intent.close_after,
                                        source_utterance=original_phrase)
                            elif intent.kind == "close_document":
                                current_id = (documents.current.ident
                                              if documents.current else None)
                                if doc_snapshot is not None and current_id == doc_snapshot:
                                    ask_to_close_document(original_phrase)
                                else:
                                    announce_document(
                                        "Non ho un documento identificato da chiudere.")
                elif kind == "conversation_error":
                    runtime_events.record("gpt_failure")
                    busy_gpt = False
                    epoch, original_phrase, reason, *channels = data
                    channel=channels[0] if channels else "conversation"
                    failed_refinement=channels[1] if len(channels)>1 else None
                    if failed_refinement and (addon_manager is None or
                            not addon_manager.files_enabled() or
                            not addon_manager.file_service.refinement_live(failed_refinement)):
                        continue
                    if (epoch == conversation_epoch and (
                            channel=="typed_conversation" or
                            voice_mode.get() in (GPT_CONVERSATION, CONTINUOUS, PUSH_TO_TALK))):
                        write_line("Conversazione GPT: " + reason)
                        speak_result("GPT non è disponibile. Puoi riprovare.")
                        remember_exchange(original_phrase, "GPT non disponibile, riprova.",
                                          "error")
                elif kind == "gpt_ok":
                    action, result, *rest = data
                    busy_gpt = False
                    if action == "ask" and len(rest) > 1 and rest[1] != conversation_epoch:
                        continue
                    if gpt_enabled.get():
                        if action == "ask":
                            write_line("GPT > " + result.get("text", "(nessuna risposta)"))
                            speak_result(result.get("text", ""))
                            if rest and rest[0]:
                                answer=result.get("text", "")
                                kind=("clarify" if isinstance(answer,str)
                                      and answer.strip().endswith("?")
                                      and answer.count("?")==1 else "chat")
                                remember_exchange(rest[0],answer,kind)
                            gpt_status.set("GPT: connesso")
                            active_gpt = True
                        elif action == "disconnect":
                            display_status({"status": "disconnected", "sharing": False})
                            write_line("Account scollegato da Lumi.")
                        else:
                            display_status(result)
                    else:
                        active_gpt = False
                elif kind == "tts_voices":
                    names = data[0]
                    spoken_picker.configure(values=[DEFAULT_VOICE_LABEL, *names])
                    if selected_voice() not in names:
                        spoken_voice.set(DEFAULT_VOICE_LABEL)
                        save_speech_preferences()
                    spoken_status.set(f"Voci offline disponibili: {len(names)}.")
                    refresh_voices_button.configure(state="normal")
                elif kind == "tts_error":
                    message = str(data[0])
                    spoken_status.set(message if message.startswith(("Voce naturale", "Download voce"))
                                      else "Voci Windows non disponibili: " + message)
                    refresh_voices_button.configure(state="normal")
                elif kind == "tts_status":
                    spoken_status.set(str(data[0]))
                elif kind == "music_status":
                    write_line("MUSICA > " + str(data[0])[:160])
                elif kind == "tts_download_done":
                    for button in (download_paola_button, download_serena_button):
                        button.configure(state="normal")
                elif kind == "gpt_error":
                    runtime_events.record("gpt_failure")
                    action, reason, *request_epoch = data
                    busy_gpt = False
                    if action == "ask" and request_epoch and request_epoch[0] != conversation_epoch:
                        continue
                    active_gpt = False if action != "ask" else active_gpt
                    if gpt_enabled.get():
                        gpt_status.set("GPT: collegamento non disponibile o richiesta fallita.")
                        write_line("GPT: " + str(reason))
                refresh_buttons()
        except queue.Empty:
            pass

        try:
            for _ in range(30):
                event = service.events.get_nowait()
                if event.get("event") == "open_browser":
                    url = event.get("url", "")
                    # Do not open arbitrary URLs coming from the child.
                    from urllib.parse import urlsplit
                    parsed = urlsplit(url)
                    if parsed.scheme == "https" and parsed.netloc == "auth.openai.com":
                        webbrowser.open(url)
                    else:
                        write_line("URL di autenticazione inatteso: apertura bloccata.")
                elif event.get("event") == "fatal":
                    runtime_events.record("gpt_failure")
                    conversation_epoch += 1
                    active_gpt = False
                    telegram_gpt_ready.clear()
                    planner_abort_event.set()
                    if gpt_enabled.get():
                        gpt_status.set("GPT: modulo non pronto.")
                        write_line("GPT: " + str(event.get("error", "errore")))
                elif event.get("event") == "stopped" and gpt_enabled.get() and not busy_gpt:
                    conversation_epoch += 1
                    planner_abort_event.set()
                    active_gpt = False
                    telegram_gpt_ready.clear()
                    gpt_status.set("GPT: servizio arrestato.")
                refresh_buttons()
        except queue.Empty:
            pass
        # A small bounded speech queue avoids dropping the next sentence
        # while GPT is processing. Do not forward it after mode/logout changes,
        # and never process it during a pending document-save decision.
        if (voice_mode.get() != GPT_CONVERSATION or not active_gpt
                or not gpt_enabled.get()):
            pending_conversation.clear()
        elif (pending_conversation and not busy_gpt and not busy_local
              and not document_busy
              and not doc_dialog.phase.startswith("awaiting_")
              and doc_dialog.phase != "executing"):
            epoch, follow_up = pending_conversation.popleft()
            if epoch == conversation_epoch:
                start_conversation_gpt(follow_up)

    def toggle_hud_microphone() -> None:
        # A real manual on/off action, not a decorative toggle.
        voice_mode.set(
            STANDBY if voice_mode.get() != STANDBY else GPT_CONVERSATION)
        change_voice_mode()

    def show_help(event=None):
        from local_help import open_help
        open_help(root, engine)
        return "break"

    def focus_command_box(event=None):
        root.lift()
        root.focus_force()
        input_box.focus_set()
        return "break"

    def send_console_input(event=None) -> None:
        message=request.get().strip()
        if not message:
            return
        try:
            chat_is_visible = chat_notebook.select() == str(chat_local_tab)
        except NameError:
            chat_is_visible = False  # Standalone legacy router tests.
        if " ".join(message.casefold().strip(" .!?").split()) in (
                "aiuto", "help", "comandi", "cosa puoi fare", "cosa sai fare"):
            show_help()
            request.set("")
            return "break"
        from voice_control import model_switch_target
        if model_switch_target(message) is not None and try_model_switch(message):
            request.set("")
            return
        reconcile_document_session(force=True)
        if try_telegram_voice_send(message):
            request.set("")
            return
        if save_only_waiting:
            request.set("")
            receive_save_only_destination(message)
            return
        if doc_dialog.phase.startswith("awaiting_"):
            request.set("")
            handle_document_confirmation(message)
            return
        requested_name=parse_simple_save(message)
        if doc_dialog.phase=="editing" and requested_name is not None:
            request.set("")
            save_document_now(message,explicit_name=requested_name)
            return
        if doc_dialog.phase=="editing":
            direct_choice=classify_document_choice(message,pending=False)
            if direct_choice in ("save","discard"):
                request.set("")
                decision=doc_dialog.request_close_with_choice(message)
                execute_document_choice(decision)
                return
        if (not (pending_project_name or pending_project_rename_id is not None
                 or pending_project_trash_id is not None) and try_file_command(message)):
            request.set("")
            return
        if (not (pending_project_name or pending_project_rename_id is not None
                 or pending_project_trash_id is not None) and try_timer_command(message)):
            request.set("")
            return
        if not (pending_project_name or pending_project_rename_id is not None
                or pending_project_trash_id is not None):
            # Same trusted recognition as voice, before the generic app guard
            # and before either model. Execution retains the existing owner.
            command = speech_to_local_command(message)
            if command:
                if handle_project_reference(message):
                    request.set("")
                    return
                if command == "apri blocco note":
                    document_operation("open", source_utterance=message)
                elif busy_local:
                    write_line("Motore locale occupato: riprova.")
                else:
                    submit_local(message_override=command, source_utterance=message)
                request.set("")
                return
        # Explicit application launches must never become pretend Gemma replies.
        # Only the trusted, user-enabled Programmi e app add-on can launch them.
        if not (pending_project_name or pending_project_rename_id is not None
                or pending_project_trash_id is not None):
            from program_apps.service import launch_query, blocked
            query = launch_query(message)
            if query and not blocked(message) and not re.search(r'\bprogett[oi]\b', query):
                request.set("")
                explanation = ("Non ho avviato il programma. Attiva Programmi e app, "
                               "seleziona l'applicazione e aggiorna l'elenco se necessario.")
                write_line("PROGRAMMI > " + explanation)
                speak_result(explanation)
                return
        if project_voice_command(message):
            request.set("")
            return
        if preference_command(message):
            request.set("")
            return
        if handle_project_reference(message):
            request.set("")
            return
        if not chat_is_visible and handle_unanchored_short_reply(message):
            request.set("")
            return
        if try_self_diagnostic(message):
            request.set("")
            return
        if maybe_queue_telegram_note(message):
            request.set("")
            return
        # F2 chat instances are Gemma-only. Never transmit their private
        # message to GPT silently; other existing console routes stay intact.
        if chat_is_visible and gpt_enabled.get():
            chat_sessions_panel.report_error(
                "Chat isolate F2: disattiva GPT per usare Gemma locale.")
            write_line("CHAT > Chat isolate: disattiva GPT per parlare con Gemma.")
            return
        # Selection is distinct from connection and local model configuration.
        if gpt_enabled.get():
            if not active_gpt:
                write_line("GPT > GPT selezionato ma non connesso. Connetti ChatGPT nelle impostazioni.")
            elif busy_gpt:
                write_line("GPT > Sto già elaborando. Attendi la risposta.")
            else:
                submit_gpt()
            return
        # GPT is explicitly off: use the configured local model.
        from local_model.native_config import NativeModelConfig
        from local_model.native_settings import default_native_settings_path
        native_path = default_native_settings_path()
        if native_path.is_file():
            try:
                native_cfg = NativeModelConfig.load(native_path)
                if native_cfg.model and Path(native_cfg.model).is_file():
                    submit_gemma_trial()
                    return
            except (OSError, ValueError) as exc:
                write_line("GEMMA / CONFIGURAZIONE > " + str(exc))
                return
        if chat_is_visible:
            chat_sessions_panel.report_error(
                "Nessun GGUF locale pronto. Configura Gemma nelle impostazioni.")
            write_line("CHAT > Nessun modello locale configurato.")
            return
        if gpt_enabled.get() and active_gpt:
            if busy_gpt:
                write_line("LUMI > Sto già elaborando. Attendi la risposta.")
                return
            submit_gpt()
        else:
            submit_local()

    def toggle_console_tools() -> None:
        if buttons_row.winfo_manager():
            buttons_row.pack_forget()
        else:
            buttons_row.pack(fill="x", pady=(6, 0))

    workspace_button.configure(command=open_project_manager)
    scope_button.configure(command=open_project_manager)
    telegram_toggle.configure(command=toggle_telegram_automatic)
    telegram_configure_button.configure(command=telegram_open_setup)
    telegram_reload_button.configure(command=telegram_reconfigure)
    telegram_note_button.configure(command=leave_telegram_note_dialog)
    telegram_contacts_button.configure(command=open_telegram_contact_list)
    telegram_send_button.configure(command=open_telegram_manual_send)
    addon_settings_button.configure(command=open_addon_settings)
    hud.set_orbit_open_handler(orbit_open)
    hud_send_button.configure(command=send_console_input)
    help_button.configure(command=show_help)
    hud_mic_button.configure(command=toggle_hud_microphone)
    hud.set_quick_toggle_handlers(
        microphone=hud_mic_button.invoke,
        gpt=gpt_toggle.invoke,
        memory=memory_toggle.invoke)
    tools_button.configure(command=toggle_console_tools)
    local_button.configure(command=submit_local)
    ask_button.configure(command=submit_gpt)
    # Manual, isolated native test. No automatic online fallback or PC actions.
    gemma_trial_queue = queue.Queue()
    # Streaming: partial chat text while the local model is still generating,
    # and voice that starts from the first complete sentence (chat_stream.py).
    from chat_stream import STREAM as _chat_stream
    _chat_stream.configure(
        output=output,
        speak=lambda text: speaker.speak(text, selected_voice()),
        voice_enabled=lambda: bool(spoken_enabled.get()))
    gemma_trial_busy = [False]
    # Prefer the pinned native source packaged beside Jarvis.
    gemma_source = [str(Path(__file__).resolve().parent / "native_engine" / "koboldcpp.py")
                    if (Path(__file__).resolve().parent / "native_engine" / "koboldcpp.py").is_file()
                    else None]
    gemma_session = [None]
    gemma_session_lock = threading.Lock()

    def get_gemma_session():
        with gemma_session_lock:
            if closing:
                raise RuntimeError("Lumi in chiusura: richiesta Gemma annullata.")
            if gemma_session[0] is None:
                from local_model.native_chat_adapter import NativeChatAdapter
                from local_model.native_conversation_session import NativeConversationSession
                source = gemma_source[0]
                if not source or not Path(source).is_file():
                    raise ValueError("Sorgente Gemma non configurata.")
                gemma_session[0] = NativeConversationSession(NativeChatAdapter(source))
            return gemma_session[0]

    gemma_recent_reply = [None]

    def chat_navigation_possible():
        return not (
            closing or busy_gpt or busy_local or gemma_trial_busy[0]
            or document_busy or save_only_waiting
            or doc_dialog.phase.startswith("awaiting_")
            or pending_project_name or pending_project_rename_id is not None
            or pending_project_trash_id is not None
            or bool(pending_conversation))

    def chat_selection_changed(_old, _new):
        nonlocal conversation_epoch
        # One shared inference owner, but separate chat IDs. Revoke prior
        # follow-up shortcuts after a switch, never erase durable transcripts.
        conversation_epoch += 1
        gemma_recent_reply[0] = None
        # Navigation is refused while follow-ups are queued. Never silently
        # discard them merely because a new tab or instance was selected.

    previous_chat_tab = [str(chat_console_tab)]
    changing_chat_tab = [False]

    def on_chat_tab_change(_event=None):
        if changing_chat_tab[0]:
            return
        selected = chat_notebook.select()
        if selected == previous_chat_tab[0]:
            return
        if not chat_navigation_possible():
            changing_chat_tab[0] = True
            chat_notebook.select(previous_chat_tab[0])
            changing_chat_tab[0] = False
            write_line("CHAT > Termina la richiesta corrente prima di cambiare vista.")
            return
        if selected == str(chat_local_tab):
            if not chat_sessions_panel.activate():
                changing_chat_tab[0] = True
                chat_notebook.select(chat_console_tab)
                changing_chat_tab[0] = False
                return
        else:
            chat_selection_changed(None, None)
        previous_chat_tab[0] = selected

    chat_notebook.bind("<<NotebookTabChanged>>", on_chat_tab_change)

    def selected_chat_target():
        if chat_notebook.select() != str(chat_local_tab):
            return None
        target = chat_sessions_panel.current_target()
        if target is None or target[1] != active_project_id:
            return None
        return target

    def try_gemma_app_followup(utterance):
        from program_apps.service import normalized
        if normalized(utterance) not in (
            "me lo apri", "me la apri", "puoi aprirlo", "puoi aprirla",
            "aprilo", "aprila", "avvialo", "avviala", "fallo",
        ):
            return False
        recent = gemma_recent_reply[0]
        provider = getattr(engine, "program_apps", None)
        if (recent is None or recent[0] != conversation_epoch
                or time.monotonic() - recent[1] > 120
                or provider is None or not provider.available()
                or closing or busy_local or gemma_trial_busy[0]
                or save_only_waiting or document_busy or doc_dialog.phase != "idle"
                or pending_project_name or pending_project_rename_id is not None
                or pending_project_trash_id is not None):
            return False
        context = normalized(recent[2])
        matches = [
            row["id"] for row in provider.entries()
            if row["enabled"] and row["available"]
            and re.search(r"(?<!\w)" + re.escape(normalized(row["name"])) + r"(?!\w)", context)
        ]
        gemma_recent_reply[0] = None
        if len(matches) != 1:
            return False
        submit_local(message_override=utterance, source_utterance=utterance,
                     addon_action_id="addon.programmi_app.avvia",
                     program_call=("suggest_id", {"query": matches[0]}))
        return True

    def native_memory_request(context_id, spoken):
        """Capture UI authorization; only the returned worker reader does I/O."""
        revision = gemma_memory_revision
        wanted = context_id is not None or memory_enabled.get()
        owner = workspace if context_id is not None else (durable_brain if wanted else None)
        warnings = []
        if wanted and owner is None:
            warnings.append("Archivio dei ricordi non disponibile.")

        def read(budget):
            if closing or owner is None:
                return ""
            try:
                if context_id is None:
                    if owner is not durable_brain or revision != gemma_memory_revision:
                        return ""
                    raw = owner.prompt_context(spoken[:180], budget=budget)
                else:
                    if owner is not workspace or budget < 160:
                        return ""
                    project = owner.project(context_id)
                    if project is None or project["trashed"]:
                        return ""
                    raw = owner.prompt_context("project", context_id, spoken,
                                               budget=budget, prefer_related=True)
                value = json.loads(raw)
                if not isinstance(value, dict) or not any(value.values()):
                    return ""
                if len(raw) > budget:
                    raise ValueError("Memoria oltre il budget.")
                return raw
            except (OSError, sqlite3.Error, ValueError) as exc:
                warnings.append("Ricordi precedenti non disponibili ("
                                + type(exc).__name__ + ").")
                return ""

        def recent_pairs(count):
            if closing or owner is None:
                return ()
            try:
                if context_id is None:
                    if owner is not durable_brain or revision != gemma_memory_revision:
                        return ()
                    pairs = owner.dialogue_pairs(count)
                    if closing or owner is not durable_brain or revision != gemma_memory_revision:
                        return ()
                    return pairs
                if owner is not workspace:
                    return ()
                pairs = owner.dialogue_pairs("project", context_id, count)
                return () if closing or owner is not workspace else pairs
            except (OSError, sqlite3.Error, ValueError) as exc:
                warnings.append("Scambi recenti non disponibili (" + type(exc).__name__ + ").")
                return ()

        read.recent_pairs = recent_pairs
        return (read if owner is not None else None), owner, revision, warnings

    def submit_gemma_voice(spoken, *, typed=False):
        if closing or gemma_trial_busy[0]:
            return False
        try:
            chat_tab_active = chat_notebook.select() == str(chat_local_tab)
        except NameError:
            chat_tab_active = False
        chat_target = selected_chat_target() if chat_tab_active else None
        if chat_tab_active and chat_target is None:
            write_line("CHAT > Impossibile identificare la conversazione corrente.")
            return False
        explicit = re.match(r"^con gemma(?:[ ,:]+)(.+)$", spoken, re.I)
        candidates = ()
        if explicit:
            from program_apps.service import blocked
            provider = engine.program_apps
            question = explicit.group(1).strip()
            if blocked(question):
                write_line("LUMI > Per scegliere un’app indica un obiettivo da svolgere.")
                return False
            if provider is not None and provider.available():
                candidates = tuple(row for row in provider.entries()
                                   if row["enabled"] and row["available"])
            if not 1 <= len(candidates) <= 12:
                write_line("LUMI > Per la prova abilita da 1 a 12 app in Programmi e app.")
                return False
        if gemma_source[0] is None or not Path(gemma_source[0]).is_file():
            source = filedialog.askopenfilename(
                parent=root, title="Configura Gemma: seleziona koboldcpp.py",
                filetypes=[("Sorgente KoboldCpp", "koboldcpp.py"), ("Python", "*.py")])
            if not source:
                write_line("LUMI > Configurazione locale mancante. Nessun invio online.")
                return False
            if Path(source).name.lower() != "koboldcpp.py":
                write_line("LUMI > File sorgente non valido. Nessun invio online.")
                return False
            gemma_source[0] = source
        native_context = chat_target[0] if chat_target is not None else active_project_id
        native_document = documents.current.ident if documents.current else None
        native_actions = () if explicit else active_addon_actions()
        if explicit:
            reader, memory_owner, memory_revision, memory_warnings = (
                None, None, gemma_memory_revision, [])
        elif chat_target is not None:
            from local_model.chat_context import make_chat_history_reader
            try:
                reader = make_chat_history_reader(
                    chat_sessions_panel.store, chat_target[0],
                    project_id=chat_target[1])
            except (OSError, sqlite3.Error, ValueError) as exc:
                write_line("CHAT > Archivio locale non disponibile: " + type(exc).__name__)
                chat_sessions_panel.report_error(
                    "Archivio chat non accessibile. Nessuna richiesta inviata.")
                return False
            # The sole memory source of a chat instance is its own history.
            # No automatic global/project Second Brain recall in F2.
            memory_owner, memory_revision, memory_warnings = (
                None, gemma_memory_revision, [])
        else:
            reader, memory_owner, memory_revision, memory_warnings = (
                native_memory_request(active_project_id, spoken))
        # Make the session busy only after the selected chat and its reader
        # are valid: errors cannot strand the Gemma UI in a busy state.
        gemma_trial_busy[0] = True
        gemma_recent_reply[0] = None
        gemma_button.configure(state="disabled")
        # Typed text is the user's own message, like voice ("TU" role).
        write_line(("TU > " if typed else "UTENTE / VOCE > ") + spoken)
        voice_epoch = conversation_epoch
        from chat_stream import STREAM
        STREAM.start_request()

        def voice_worker():
            try:
                session = get_gemma_session()
                if explicit:
                    index = session.pick_program(
                        question, tuple(row["name"] for row in candidates))
                    app_id = candidates[index]["id"] if index is not None else None
                    gemma_trial_queue.put(("program_choice", (spoken, app_id), voice_epoch))
                else:
                    from conversation_router import native_intent_context_for_request
                    # Informational questions use ordinary Gemma chat: no Windows
                    # catalog and no JSON action parser. Executable requests keep
                    # the existing strict validated-intent path.
                    intent_context = native_intent_context_for_request(
                        spoken, has_document=native_document is not None,
                        addon_actions=native_actions)
                    from chat_stream import STREAM
                    session.on_stream = STREAM.sink(voice_epoch)
                    try:
                        turn = chat_transport.ask_local_first(
                            spoken, session=session, timeout=180,
                            context_id=native_context, defer_history=True,
                            memory_context=reader, intent_context=intent_context)
                    finally:
                        session.on_stream = None
                    from local_model.native_conversation_session import NativeChatTurn
                    if isinstance(turn, NativeChatTurn):
                        turn.memory_owner = memory_owner
                        turn.memory_revision = memory_revision
                        turn.memory_warning = " ".join(memory_warnings)
                        turn.document_snapshot = native_document
                        turn.chat_target = chat_target
                        turn.project_snapshot = active_project_id
                    gemma_trial_queue.put(("ok" if typed else "voice_ok", turn, voice_epoch))
            except Exception as exc:
                gemma_trial_queue.put(("error" if typed else "voice_error", str(exc)[:350], voice_epoch))
        threading.Thread(target=voice_worker, daemon=True,
                         name="jarvis-gemma").start()
        return True

    def submit_gemma_trial():
        if closing or gemma_trial_busy[0]:
            return
        question = request.get().strip()
        if not question:
            write_line("LUMI > Scrivi una domanda prima di avviare la prova.")
            return
        if (try_program_command(question) or try_gemma_app_followup(question)
                or submit_gemma_voice(question, typed=True)):
            request.set("")

    def poll_gemma_trial():
        from chat_stream import STREAM
        STREAM.drain(conversation_epoch, gemma_trial_busy[0] and not closing)
        try:
            while True:
                kind, value, voice_epoch = gemma_trial_queue.get_nowait()
                STREAM.drain(conversation_epoch, gemma_trial_busy[0] and not closing)
                STREAM.clear()
                gemma_trial_busy[0] = False
                gemma_button.configure(state="normal")
                if voice_epoch is not None and voice_epoch != conversation_epoch:
                    continue
                if kind in ("ok", "voice_ok"):
                    from local_model.native_conversation_session import NativeChatTurn
                    if isinstance(value, NativeChatTurn):
                        chat_target = getattr(value, "chat_target", None)
                        if closing or getattr(value, "project_snapshot", active_project_id) != active_project_id:
                            continue
                        if chat_target is not None:
                            if (value.context_id != chat_target[0]
                                    or selected_chat_target() != chat_target):
                                continue
                        elif value.context_id != active_project_id:
                            continue
                        if (value.context_id is None and value.memory_revision is not None
                                and value.memory_revision != gemma_memory_revision):
                            continue
                        if value.allowed_actions is not None:
                            from conversation_router import parse_native_conversation_intent, ConversationRejected
                            from dialogue_focus import is_ambiguous_short_reply
                            try:
                                intent = parse_native_conversation_intent(
                                    value.text, utterance=value.question,
                                    has_document=value.document_snapshot is not None,
                                    addon_resolver=(addon_manager.resolve if addon_manager is not None else None))
                                if intent.kind == 'capability':
                                    from program_apps.service import blocked
                                    if (intent.capability is None or
                                            intent.capability.action_id not in value.allowed_actions
                                            or is_ambiguous_short_reply(value.question)
                                            or blocked(value.question)):
                                        raise ConversationRejected('Richiesta di azione non identificata.')
                                    if (save_only_waiting or document_busy or doc_dialog.phase.startswith('awaiting_')
                                            or pending_project_name or pending_project_rename_id is not None
                                            or pending_project_trash_id is not None
                                            or pending_project_reference.question or telegram_voice_dialog.pending):
                                        raise ConversationRejected('Un altro dialogo richiede la tua risposta.')
                                    if value.accept_action():
                                        dispatch_model_capability(intent.capability, value.question,
                                                                  value.document_snapshot)
                                    continue
                                if intent.kind not in ('chat', 'clarify'):
                                    raise ConversationRejected('Formato di risposta locale non supportato.')
                                value.text = intent.reply
                            except ConversationRejected as exc:
                                if value.finish_reason == 'length':
                                    write_line('LUMI > Risposta incompleta: limite Max Output raggiunto; '
                                               'azione non eseguita. ' + str(exc))
                                    speak_result('La risposta di Gemma è stata interrotta dal limite di output. '
                                                 'Non ho eseguito alcuna azione.')
                                else:
                                    write_line('LUMI > Risposta non interpretabile: ' + str(exc))
                                    speak_result('Non riesco a interpretare la risposta di Gemma. Puoi riprovare?')
                                continue
                        # UI context/epoch cannot change during this synchronous
                        # acceptance. The metadata commit never waits for native inference.
                        # A memory switch preserves the current live dialogue,
                        # but must not newly hydrate a revoked durable owner.
                        if (value.context_id is None and value.memory_owner is not None
                                and (value.memory_owner is not durable_brain or not memory_enabled.get())):
                            value.restored_history = ()
                        if not value.commit():
                            continue
                        # Distinct transcripts are stored only in the opted-in
                        # chat DB, never in the general Second Brain.
                        context_state = (value.intent_warning, value.context_note)
                        if getattr(value._session, "_last_context_notice", None) != context_state:
                            value._session._last_context_notice = context_state
                            for notice in context_state:
                                if notice:
                                    write_line('LUMI > ' + notice)
                        if value.memory_warning:
                            write_line("MEMORIA > " + value.memory_warning)
                        owner = value.memory_owner
                        can_save = owner is not None and (
                            owner is workspace if value.context_id is not None else
                            owner is durable_brain and memory_enabled.get())
                        if chat_target is not None:
                            try:
                                chat_sessions_panel.persist_answer(
                                    chat_target[0], value.question, value.text,
                                    project_id=chat_target[1])
                            except (OSError, sqlite3.Error, ValueError) as exc:
                                write_line("CHAT > Risposta non archiviata: "
                                           + type(exc).__name__)
                                chat_sessions_panel.report_error(
                                    "Risposta non salvata su disco ("
                                    + str(chat_sessions_panel.pending_count)
                                    + " in attesa): nuovo tentativo al prossimo messaggio. "
                                    "Se chiudi Lumi prima, andranno perse.")
                        elif can_save and remember_exchange(value.question, value.text, "chat") is False:
                            write_line("MEMORIA > Scambio non archiviato.")
                        gemma_recent_reply[0] = (
                            voice_epoch, time.monotonic(),
                            value.question[:500] + " " + value.text[:500])
                        value = value.text
                if kind == "program_choice":
                    spoken, app_id = value
                    if app_id is None:
                        message = "Quale programma vuoi aprire?"
                        write_line("LUMI > " + message)
                        speak_result(message)
                    elif busy_local:
                        write_line("LUMI > Motore locale occupato. Riprova.")
                    else:
                        submit_local(message_override=spoken, source_utterance=spoken,
                                     addon_action_id="addon.programmi_app.avvia",
                                     program_call=("suggest_id", {"query": app_id}))
                elif kind == "voice_ok":
                    write_line("LUMI > " + value)
                    STREAM.speak_final(value, speak_result)
                elif kind == "voice_error":
                    write_line("GEMMA / ERRORE > " + value)
                    speak_result("Gemma locale non disponibile. Controlla la configurazione.")
                elif kind == "ok":
                    write_line("LUMI > " + value)
                    STREAM.speak_final(value, speak_result)
                else:
                    write_line("GEMMA / ERRORE > " + value)
        except queue.Empty:
            pass
        if not closing:
            root.after(150, poll_gemma_trial)

    root.after(250, poll_gemma_trial)
    gemma_button.configure(command=submit_gemma_trial)

    plan_button.configure(command=submit_plan)
    diagnostic_button.configure(
        command=lambda: try_self_diagnostic("Lumi, fai un'autodiagnosi"))
    diagnostic_cancel_button.configure(command=cancel_diagnostic)
    service_diagnostic_box = ttk.LabelFrame(integrations_settings_frame, text="Diagnostica servizi")
    service_diagnostic_box.pack(fill="x", padx=8, pady=8)
    ttk.Label(service_diagnostic_box, wraplength=540,
              text="Stato locale di GPT, voce, Gemma, memoria e Telegram, con ultimi eventi. "
                   "Aggiornamento a richiesta: nessun messaggio di prova o avvio del modello.").pack(anchor="w", padx=8, pady=5)
    ttk.Button(service_diagnostic_box, text="Apri diagnostica servizi...",
               command=open_service_diagnostics).pack(anchor="w", padx=8, pady=6)
    dictation_button.configure(command=toggle_dictation)
    voice_correction_button.configure(command=show_voice_corrections)
    choose_save_button.configure(command=choose_save_destination)
    hud_save_file_button.configure(command=choose_save_destination)
    doc_save_button.configure(
        command=lambda: handle_document_confirmation("salva e chiudi"))
    doc_discard_button.configure(command=press_discard_button)
    doc_cancel_button.configure(
        command=lambda: handle_document_confirmation("annulla"))
    spoken_switch.configure(command=save_speech_preferences)
    spoken_picker.bind("<<ComboboxSelected>>", lambda event: save_speech_preferences())
    # Cursori voce (effetto, velocità, tonalità, volume): salvati poco dopo
    # l'ultimo spostamento, senza scrivere su disco a ogni pixel.
    style_save_job = [None]

    def schedule_style_save(*_args) -> None:
        if style_save_job[0] is not None:
            try:
                root.after_cancel(style_save_job[0])
            except tk.TclError:
                pass
        style_save_job[0] = root.after(700, save_speech_preferences)

    for style_var in (spoken_effect, spoken_rate, spoken_pitch, spoken_volume):
        style_var.trace_add("write", schedule_style_save)
    refresh_voices_button.configure(command=refresh_voices)
    download_paola_button.configure(command=lambda: download_natural_voice("paola"))
    download_serena_button.configure(command=lambda: download_natural_voice("serena"))
    test_voice_button.configure(command=test_speech)
    for button in mode_buttons:
        button.configure(command=change_voice_mode)
    auto_listen_switch.configure(command=save_auto_listen_preference)
    ptt_button.bind("<ButtonPress-1>", ptt_press)
    ptt_button.bind("<ButtonRelease-1>", ptt_release)
    root.bind_all("<ButtonRelease-1>", ptt_release, add="+")
    root.bind("<FocusOut>", ptt_release, add="+")
    input_box.bind("<Return>", send_console_input)

    def close() -> None:
        nonlocal closing
        # Synchronize only creation (which never loads the model), not native
        # inference. A worker cannot publish a new owner after this snapshot.
        with gemma_session_lock:
            closing = True
            native_owner = gemma_session[0]
        if native_owner is not None:
            try:
                native_owner.close()
            except Exception:
                write_line("LUMI > Errore nell'annullamento durante la chiusura.")
        if addon_manager is not None and addon_manager._file_service is not None:
            addon_manager.file_service.reset()
        if addon_manager is not None and getattr(addon_manager,'_program_service',None) is not None:
            addon_manager.program_service.reset()
        planner_abort_event.set()
        doc_dialog.revoke_pending()
        dictation.disable()
        wake_gate.reset()
        voice.close()
        if telegram_bridge:
            telegram_bridge.stop()
        telegram_gpt_ready.clear()
        speaker.close()
        if music_service is not None:
            music_service.close()
        hud.close()
        alarm.stop()
        timer.close()
        root.destroy()
        # Non-daemon: ensure the Node child is terminated before Python exits.
        threading.Thread(target=service.stop, daemon=False, name="jarvis-gpt-shutdown").start()

    ttk.Button(frame, text="Chiudi impostazioni", command=settings_window.withdraw).pack(
        anchor="e", pady=(9, 0))
    # Settings are intentionally hidden until the gear is pressed.
    # The normal window-close control invokes the same safe shutdown.
    hud.set_close_handler(close)
    hud.set_state_provider(lambda: {
        "speaking": speaker.is_speaking(),
        # Orange only if the real Vosk input stream has actually opened.
        # Push-to-talk selected but not pressed must remain cyan.
        "listening": voice.is_user_speaking(),
        "mic_enabled": voice.is_listening(),
        "mic_selected": voice_mode.get() != STANDBY,
        "mic_push_to_talk": voice_mode.get() == PUSH_TO_TALK,
        "gpt_enabled": gpt_enabled.get(),
        "reasoning": (gemma_trial_busy[0] or
                      (gemma_session[0] is not None and gemma_session[0].is_busy) or
                      (busy_gpt and gpt_enabled.get() and
                       gpt_request_action in ("ask", "conversation", "typed_conversation"))),
        "searching": (busy_local and engine.file_access is not None and
                      engine.file_access._progress_active and
                      not engine.file_access.cancelled.is_set()),
        "thinking": (gemma_trial_busy[0] or
                     (gemma_session[0] is not None and gemma_session[0].is_busy) or
                     (busy_gpt and gpt_enabled.get()) or busy_local or document_busy),
        "connected": active_gpt,
        "memory": memory_enabled.get(),
        "orbit_nodes": orbit_nodes_cache,
    })
    def initial_launch() -> None:
        """App-only autostart: never adds Windows login/run-at-boot entries."""
        if closing:
            return
        for warning in settings_load_warnings:
            write_line("IMPOSTAZIONI > " + warning)
        settings_load_warnings.clear()
        if auto_listen_enabled.get():
            voice_mode.set(GPT_CONVERSATION)
            change_voice_mode()
        # The local SAPI voice is suppressed from Vosk input by
        # ignore_audio=speaker.is_audible, also during the cooldown.
        greeting = startup_greeting()
        write_line("LUMI > " + greeting)
        speak_result(greeting)

    root.protocol("WM_DELETE_WINDOW", close)
    settings_window.bind("<Escape>", lambda _event: settings_window.withdraw())
    root.bind("<Control-comma>", lambda _event: show_settings())
    from local_help import bind_help_shortcuts
    bind_help_shortcuts(root, settings_window, show_help, focus_command_box)
    refresh_buttons()
    input_box.focus_set()
    root.after(120, poll)
    root.after(800, diagnostic_heartbeat)
    root.after(400, refresh_voices)
    root.after(650, initial_launch)
    root.after(1100, refresh_orbit_nodes)
    if telegram_auto.get():
        root.after(1400,toggle_telegram_automatic)
    if gpt_enabled.get():
        root.after(200, lambda: run_gpt("status"))
    power.start()
    try:
        root.mainloop()
    finally:
        power.close()


if __name__ == "__main__":
    main()


