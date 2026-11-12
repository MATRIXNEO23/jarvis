"""Voce: voci, dettatura, ascolto

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

NOMI = ('selected_voice', 'save_speech_preferences', 'refresh_voices', 'download_natural_voice', 'test_speech', 'sync_dictation_ui', 'toggle_dictation', 'save_auto_listen_preference', 'ptt_press', 'ptt_release')


def installa(d):
    """Crea le funzioni per questa esecuzione di Lumi; restituisce {nome: funzione}."""
    def selected_voice() -> str:
        choice = d.spoken_voice.get()
        return "" if choice == d.DEFAULT_VOICE_LABEL else choice
    def save_speech_preferences() -> None:
        d.settings["tts_enabled"] = bool(d.spoken_enabled.get())
        d.settings["tts_voice"] = selected_voice()
        d.settings["tts_effect"] = max(0, min(100, int(d.spoken_effect.get())))
        d.speaker.effect = d.settings["tts_effect"] / 100
        import voice_style
        style = voice_style.update(rate=d.spoken_rate.get(), pitch=d.spoken_pitch.get(),
                                   volume=d.spoken_volume.get())
        d.settings["tts_rate"], d.settings["tts_pitch"], d.settings["tts_volume"] = (
            style["rate"], style["pitch"], style["volume"])
        try:
            save_settings(d.settings)
            d.spoken_status.set("Risposte vocali salvate; nessun servizio a pagamento.")
        except (OSError, ValueError) as exc:
            d.spoken_status.set("Impossibile salvare le preferenze vocali: " + str(exc)[:130])
    def refresh_voices() -> None:
        d.spoken_status.set("Rilevamento delle voci già installate in Windows...")
        d.refresh_voices_button.configure(state="disabled")

        def worker() -> None:
            try:
                d.output_queue.put(("tts_voices", installed_voices()))
            except (OSError, ValueError, TimeoutError) as exc:
                d.output_queue.put(("tts_error", str(exc)[:140]))

        threading.Thread(target=worker, daemon=True, name="jarvis-voices-list").start()
    def download_natural_voice(key: str) -> None:
        from piper_voice import LABELS, PiperVoiceError, download_voice
        d.spoken_status.set("Download della voce " + LABELS[key] + " dal repository...")
        for button in (d.download_paola_button, d.download_serena_button):
            button.configure(state="disabled")

        def worker() -> None:
            try:
                download_voice(key)
                d.output_queue.put(("tts_status", "Voce " + LABELS[key]
                                  + " scaricata e verificata. Selezionala nel menu Voce."))
                d.output_queue.put(("tts_voices", installed_voices()))
            except Exception as exc:   # ogni errore arriva all'interfaccia
                d.output_queue.put(("tts_error", "Download voce non riuscito: "
                                  + (str(exc) or type(exc).__name__)[:140]))
            finally:
                d.output_queue.put(("tts_download_done", None))

        threading.Thread(target=worker, daemon=True, name="lumi-voice-download").start()
    def test_speech() -> None:
        d.speaker.effect = max(0, min(100, int(d.spoken_effect.get()))) / 100
        import voice_style
        voice_style.update(rate=d.spoken_rate.get(), pitch=d.spoken_pitch.get(),
                           volume=d.spoken_volume.get())
        if not d.speaker.speak("Pronto. Questa è la mia voce.", selected_voice()):
            d.spoken_status.set("Sintesi vocale occupata: riprova.")
    def sync_dictation_ui(message: str) -> None:
        d.dictation_status.set(message)
        d.dictation_button.configure(text="Disattiva dettatura" if d.dictation.enabled
                                  else "Attiva dettatura")
        if not d.closing:
            d.write_line(message)
    def toggle_dictation() -> None:
        if d.dictation.enabled:
            sync_dictation_ui(d.dictation.disable())
        elif d.voice_mode.get() == CONTINUOUS:
            sync_dictation_ui(d.dictation.enable())
        else:
            sync_dictation_ui("Seleziona prima Ascolto continuo per dettare.")
    def save_auto_listen_preference() -> None:
        """Only changes NEXT app launch, never the current listening mode."""
        desired = bool(d.auto_listen_enabled.get())
        previous = d.settings["auto_listen"]
        d.settings["auto_listen"] = desired
        try:
            save_settings(d.settings)
        except (OSError, ValueError) as exc:
            d.settings["auto_listen"] = previous
            d.auto_listen_enabled.set(previous)
            messagebox.showerror(
                "Impossibile salvare l'avvio automatico",
                str(exc)[:160], parent=d.root)
            return
        d.write_line(
            "SISTEMA > Al prossimo avvio microfono "
            + ("in conversazione locale con hotword Lumi." if desired
               else "in standby, come selezionato nelle impostazioni."))
    def ptt_press(event=None) -> None:
        if d.voice.press():
            d.mic_status.set("Premi per parlare: attivazione del microfono...")
    def ptt_release(event=None) -> None:
        d.voice.release()
    funzioni = locals()
    return {nome: funzioni[nome] for nome in NOMI}
