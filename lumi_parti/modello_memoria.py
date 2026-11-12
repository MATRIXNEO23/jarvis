"""Modello locale, memoria, cervelli e diagnostica

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

NOMI = ('open_multimodel_f5_preview', 'open_memory_preferences', 'draw_diagnostic_meter', 'current_capability_snapshot', 'lumi_brain_local', 'lumi_brain_online')


def installa(d):
    """Crea le funzioni per questa esecuzione di Lumi; restituisce {nome: funzione}."""
    def open_multimodel_f5_preview():
        try:
            from local_model.multimodel_ui_f5 import MultiModelSettingsF5Window
            MultiModelSettingsF5Window(d.settings_window)
        except (OSError, ValueError, RuntimeError, ImportError) as exc:
            messagebox.showerror("Lumi / Multimodello F5", str(exc),
                                 parent=d.settings_window)
    def open_memory_preferences():
        try:
            from local_model.memory_ui import MemoryPreferencesWindow
            MemoryPreferencesWindow(d.settings_window, get_session=d.get_gemma_session)
        except (OSError, ValueError, RuntimeError, ImportError) as exc:
            messagebox.showerror("Lumi / Memoria", str(exc), parent=d.settings_window)
    def draw_diagnostic_meter(_event=None):
        d.diagnostic_meter.delete("progress")
        w=max(1,d.diagnostic_meter.winfo_width())
        h=max(1,d.diagnostic_meter.winfo_height())
        progress=max(0,min(100,d.diagnostic_percent.get()))
        d.diagnostic_meter.create_rectangle(
            0,0,w*progress/100,h,fill="#17b8e5",outline="",
            tags="progress")
    def current_capability_snapshot(has_document:bool=False) -> dict:
        """Re-evaluate runtime permissions on every external GPT request."""
        if d.addon_manager is not None:
            try:
                d.addon_manager.refresh()
            except (AddonError,OSError,ValueError):
                # Fail closed: do not claim stale addon actions are available.
                for binding in d.addon_capability_registry.available_addons():
                    d.addon_capability_registry.unregister(binding["id"])
        try:
            stream=d.voice.is_listening()
        except (AttributeError,RuntimeError,OSError):
            stream=False
        return snapshot_capabilities(
            settings=d.settings,
            has_document=has_document,
            telegram_credentials=credentials_present(),
            telegram_voice_dependencies=(not missing_voice_dependencies()),
            voice_stream_open=stream,
            registry=d.addon_capability_registry)
    def lumi_brain_local(value: bool) -> None:
        text = __import__("model_gate").set_local(value)
        d.write_line("LUMI > " + text)
        d.speak_result(text)
    def lumi_brain_online(value: bool) -> None:
        # Stesso interruttore GPT delle Impostazioni (ChatGPT ora, gratuiti in futuro).
        if bool(d.gpt_enabled.get()) != value:
            d.gpt_toggle.invoke()
        text = "Cervello online " + ("acceso." if d.gpt_enabled.get() else "spento.")
        if value and not d.gpt_enabled.get():
            text = "Non riesco ad accendere il cervello online: controlla il collegamento GPT."
        d.write_line("LUMI > " + text)
        d.speak_result(text)
    funzioni = locals()
    return {nome: funzioni[nome] for nome in NOMI}
