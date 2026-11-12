"""Documenti, progetti e piani

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

NOMI = ('begin_project_work', 'update_document_buttons', 'announce_document', 'ask_to_close_document', 'automatic_document_destination', 'execute_document_choice', 'press_discard_button', 'journal_plan_approved', 'journal_plan_step', 'journal_plan_finished', 'submit_plan')


def installa(d):
    """Crea le funzioni per questa esecuzione di Lumi; restituisce {nome: funzione}."""
    def begin_project_work(title: str, source: str = "local",
                           *, project_id: str | None = None,
                           planned: bool = False):
        """Persist a work ticket BEFORE executing a project operation."""
        ident=project_id if project_id is not None else d.active_project_id
        if ident is None:
            return None
        if d.workspace is None:
            d.workspace_status.set("Memoria progetto non disponibile: azione bloccata.")
            return False
        try:
            return (ident,d.workspace.begin_step(
                ident,title[:240],source=source,planned=planned))
        except (OSError,sqlite3.Error,WorkspaceError) as exc:
            d.workspace_status.set("Checkpoint non scritto: "+str(exc)[:110])
            return False
    def update_document_buttons() -> None:
        pending = (d.doc_dialog.phase.startswith("awaiting_") or d.save_only_waiting) and not d.document_busy
        can_choose = d.doc_dialog.phase == "awaiting_close_choice" and not d.document_busy
        d.doc_save_button.configure(state="normal" if can_choose else "disabled")
        d.doc_discard_button.configure(
            state="normal" if can_choose else "disabled")
        d.doc_cancel_button.configure(state="normal" if pending else "disabled")
        destination_ready = (
            (d.doc_dialog.phase == "awaiting_save_destination" or d.save_only_waiting)
            and not d.document_busy)
        d.choose_save_button.configure(
            state="normal" if destination_ready else "disabled")
        d.hud_save_file_button.configure(
            state="normal" if destination_ready else "disabled")
        if pending and not d.doc_choices.winfo_manager():
            d.doc_choices.pack(fill="x", pady=(0, 5), before=d.input_row)
        elif not pending and d.doc_choices.winfo_manager():
            d.doc_choices.pack_forget()
    def announce_document(message: str) -> None:
        update_document_buttons()
        d.document_status.set(message)
        d.write_line("DOCUMENTO > " + message)
        d.speak_result(message)
    def ask_to_close_document(source_utterance: str = "") -> None:
        if d.document_busy:
            announce_document("Attendi la fine della scrittura prima di chiudere.")
            return
        if d.doc_dialog.phase != "editing" or d.doc_dialog.document_id is None:
            announce_document("Non ho un documento Blocco note gestito da Lumi da chiudere.")
            return
        decision = d.doc_dialog.request_close()
        if decision.kind == "close_clean":
            # The user could have manually edited the text in the meantime.
            # Never discard an apparently clean document without asking.
            d.doc_dialog.phase = "awaiting_close_choice"
            d.doc_dialog.dirty = True
            question = "Vuoi salvare e chiudere, chiudere senza salvare oppure annullare?"
            announce_document(question)
            if source_utterance:
                d.remember_exchange(source_utterance, question, "clarify")
        else:
            announce_document(decision.message)
            if source_utterance:
                d.remember_exchange(source_utterance, decision.message, "clarify")
    def automatic_document_destination(*, explicit_name: str = "") -> Path | None:
        """Use this document's original project, never a newly selected one."""
        if d.workspace is None or d.document_owner_project_id is None:
            return None
        return project_save_destination(
            d.workspace,d.document_owner_project_id,d.document_topic,
            explicit_name=explicit_name)
    def execute_document_choice(decision, *, path: Path | None = None) -> None:
        if decision.kind == "ask_destination":
            try:
                path=automatic_document_destination()
            except (OSError,ValueError,WorkspaceError) as exc:
                announce_document("Cartella progetto non disponibile: "+str(exc)[:100])
                return
            if path is not None:
                selected=d.doc_dialog.provide_destination(str(path))
                execute_document_choice(selected,path=path)
                return
        if decision.kind in ("save_then_close", "save_as_then_close"):
            destination = path if path is not None else (
                Path(d.doc_dialog.saved_path) if d.doc_dialog.saved_path else None)
            if (path is None and d.doc_dialog.saved_path and
                    d.document_owner_project_id is not None):
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
                    d.doc_dialog.phase = "awaiting_save_destination"
                    announce_document("Dove vuoi salvare? Per esempio: "
                                      "sul desktop come storia di Venezia.")
                    d.choose_save_button.configure(state="normal")
                    return
                if d.doc_dialog.phase=="awaiting_save_destination":
                    d.doc_dialog.provide_destination(str(destination))
            d.choose_save_button.configure(state="disabled")
            d.document_operation("save", document_id=decision.document_id,
                               path=destination)
        elif decision.kind == "discard_then_close":
            d.choose_save_button.configure(state="disabled")
            d.document_operation("discard", document_id=decision.document_id)
        else:
            announce_document(decision.message)
            d.choose_save_button.configure(
                state="normal" if d.doc_dialog.phase == "awaiting_save_destination"
                else "disabled")
    def press_discard_button() -> None:
        if d.doc_dialog.phase == "awaiting_close_choice":
            # The named button itself is an explicit decision after Jarvis
            # requested a choice; no extra spoken magic phrase.
            d.handle_document_confirmation("chiudi senza salvare")
    def journal_plan_approved(plan):
        """Capture the project identity before the plan's worker starts."""
        if d.active_project_id is None:
            return None
        tickets=[]
        project_id=d.active_project_id
        for step in plan.steps:
            ticket=begin_project_work(step.description,"planner",
                                      project_id=project_id,planned=True)
            if ticket is False:
                for prior in tickets:
                    d.finish_project_work(prior,"interrupted","Avvio piano non riuscito.")
                raise WorkspaceError("Impossibile memorizzare i passi: nessuna esecuzione.")
            tickets.append(ticket)
        return tuple(tickets)
    def journal_plan_step(tickets,index,status,message,receipt):
        if not tickets:
            return
        if not 1 <= index <= len(tickets):
            raise WorkspaceError("Indice passo fuori piano.")
        result=d.finish_project_work(
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
            d.finish_project_work(ticket,"interrupted","Piano terminato: "+reason)
    def submit_plan() -> None:
        if not d.gpt_enabled.get() or not d.active_gpt or d.busy_gpt or d.closing:
            return
        from local_model.online_permissions import authorize_online_request
        open_planner(
            d.root, d.service, d.engine,
            lambda: bool(d.gpt_enabled.get() and d.active_gpt and not d.busy_gpt and not d.closing),
            d.local_execution_lock, d.planner_abort_event,
            on_approved=journal_plan_approved,
            on_step=journal_plan_step,
            on_finished=journal_plan_finished,
            confirm_inference=lambda detail: authorize_online_request(
                "planner.create", confirm=lambda: d.confirm_gpt_inference(detail)),
            consent_generation=lambda: d.conversation_epoch,
        )
    funzioni = locals()
    return {nome: funzioni[nome] for nome in NOMI}
