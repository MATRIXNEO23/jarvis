"""Conversazione con il modello locale (Gemma/KoboldCpp)

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

NOMI = ('try_model_switch', 'dispatch_model_capability', 'get_gemma_session', 'try_gemma_app_followup', 'native_memory_request', 'submit_gemma_voice', 'submit_gemma_trial', 'poll_gemma_trial')


def installa(d):
    """Crea le funzioni per questa esecuzione di Lumi; restituisce {nome: funzione}."""
    def try_model_switch(spoken: str) -> bool:
        from voice_control import model_switch_target
        selected = model_switch_target(spoken)
        if (selected is None or d.closing or d.document_busy or d.save_only_waiting
                or d.doc_dialog.phase.startswith("awaiting_")
                or d.doc_dialog.phase == "executing" or d.pending_project_name
                or d.pending_project_rename_id is not None
                or d.pending_project_trash_id is not None
                or d.telegram_voice_dialog.pending):
            return False
        if bool(d.gpt_enabled.get()) != selected:
            d.gpt_enabled.set(selected)
            d.toggle_gpt()
        # toggle_gpt restores the old setting if persistence fails.
        model = "GPT" if d.gpt_enabled.get() else "Gemma"
        message = "Modello selezionato: " + model + "."
        d.write_line("LUMI > " + message)
        d.speak_result(message)
        return True
    def dispatch_model_capability(cap, original_phrase, doc_snapshot, refinement_token=None):
        """Shared validated capability dispatch for online and native replies."""
        current_id = (d.documents.current.ident
                      if d.documents.current else None)
        if cap is None:
            d.announce_document("Azione non disponibile.")
        elif cap.handler == 'program_apps':
            from program_apps.service import blocked, protected
            if (blocked(original_phrase) or protected(original_phrase)
                    or d.save_only_waiting or d.document_busy
                    or d.doc_dialog.phase.startswith('awaiting_')
                    or d.doc_dialog.phase=='executing'):
                d.speak_result('Nessuna app avviata: richiesta negata o altro dialogo in corso.')
            elif d.addon_manager is None or not d.addon_manager.is_active(cap.action_id):
                d.speak_result('Programmi e app non è più attivo.')
            elif not d.busy_local:
                d.submit_local(message_override=original_phrase,
                    source_utterance=original_phrase,addon_action_id=cap.action_id,
                    program_call=('launch',{'query':cap.target}))
            else:
                d.speak_result('Operazione locale in corso, riprova.')
        elif cap.handler == "file_access":
            if (d.addon_manager is None or not d.addon_manager.is_active(cap.action_id)):
                d.speak_result("Accesso file non è più attivo.")
            elif not d.busy_local:
                d.submit_local(message_override=original_phrase,
                    source_utterance=original_phrase,addon_action_id=cap.action_id,
                    file_call=(cap.file_operation,
                        d.addon_manager.file_service.arguments_for_utterance(
                            cap.file_operation,dict(cap.file_arguments),original_phrase),
                        refinement_token) if refinement_token else (cap.file_operation,
                        d.addon_manager.file_service.arguments_for_utterance(
                            cap.file_operation,dict(cap.file_arguments),original_phrase)))
            else:
                d.speak_result("Operazione file già in corso.")
        elif cap.handler == "local" and cap.plan is not None:
            # A GPT proposal cannot retain permission after
            # a local add-on is disabled or uninstalled.
            if (cap.action_id.startswith("addon.") and
                    (d.addon_manager is None or not
                     d.addon_manager.is_active(cap.action_id))):
                d.speak_result("L'add-on non è più attivo.")
            elif not d.busy_local:
                d.submit_local(
                    message_override=cap.plan.steps[0].command,
                    source_utterance=original_phrase,
                    addon_action_id=(cap.action_id if
                        cap.action_id.startswith("addon.")
                        else ""))
            else:
                d.speak_result("Operazione in corso, riprova.")
        elif cap.handler == "telegram_voice_dialog":
            # GPT proposes a name, it never authorizes
            # a contact or sends audio. Local selection
            # and two-step owner confirmation are final.
            d.try_telegram_voice_send(
                "manda un messaggio a "+cap.recipient)
        elif cap.handler == "document_open":
            if current_id is None:
                d.document_operation(
                    "open", source_utterance=original_phrase)
            else:
                d.announce_document(
                    "C'è già un Blocco note gestito da Lumi. "
                    "Dimmi cosa vuoi scriverci.")
        elif cap.handler == "document_close":
            if (doc_snapshot is not None
                    and current_id == doc_snapshot):
                d.ask_to_close_document(original_phrase)
            else:
                d.announce_document(
                    "Il documento è cambiato; non chiudo nulla.")
        elif cap.handler == "document_write":
            if cap.target == "selected_document" and (
                    doc_snapshot is None
                    or current_id != doc_snapshot):
                d.announce_document(
                    "La finestra è cambiata: nessun testo inserito.")
            elif cap.target == "new_notepad" and current_id:
                d.announce_document(
                    "C'è già un documento aperto. "
                    "Vuoi aggiungere il testo a quello?")
            else:
                d.document_operation(
                    "compose", content=cap.content,
                    target=cap.target,
                    close_after=cap.close_after,
                    source_utterance=original_phrase)
        else:
            d.announce_document("Azione del catalogo non attiva.")
    def get_gemma_session():
        with d.gemma_session_lock:
            if d.closing:
                raise RuntimeError("Lumi in chiusura: richiesta Gemma annullata.")
            if d.gemma_session[0] is None:
                from local_model.native_chat_adapter import NativeChatAdapter
                from local_model.native_conversation_session import NativeConversationSession
                source = d.gemma_source[0]
                if not source or not Path(source).is_file():
                    raise ValueError("Sorgente Gemma non configurata.")
                d.gemma_session[0] = NativeConversationSession(NativeChatAdapter(source))
            return d.gemma_session[0]
    def try_gemma_app_followup(utterance):
        from program_apps.service import normalized
        if normalized(utterance) not in (
            "me lo apri", "me la apri", "puoi aprirlo", "puoi aprirla",
            "aprilo", "aprila", "avvialo", "avviala", "fallo",
        ):
            return False
        recent = d.gemma_recent_reply[0]
        provider = getattr(d.engine, "program_apps", None)
        if (recent is None or recent[0] != d.conversation_epoch
                or time.monotonic() - recent[1] > 120
                or provider is None or not provider.available()
                or d.closing or d.busy_local or d.gemma_trial_busy[0]
                or d.save_only_waiting or d.document_busy or d.doc_dialog.phase != "idle"
                or d.pending_project_name or d.pending_project_rename_id is not None
                or d.pending_project_trash_id is not None):
            return False
        context = normalized(recent[2])
        matches = [
            row["id"] for row in provider.entries()
            if row["enabled"] and row["available"]
            and re.search(r"(?<!\w)" + re.escape(normalized(row["name"])) + r"(?!\w)", context)
        ]
        d.gemma_recent_reply[0] = None
        if len(matches) != 1:
            return False
        d.submit_local(message_override=utterance, source_utterance=utterance,
                     addon_action_id="addon.programmi_app.avvia",
                     program_call=("suggest_id", {"query": matches[0]}))
        return True
    def native_memory_request(context_id, spoken):
        """Capture UI authorization; only the returned worker reader does I/O."""
        revision = d.gemma_memory_revision
        wanted = context_id is not None or d.memory_enabled.get()
        owner = d.workspace if context_id is not None else (d.durable_brain if wanted else None)
        warnings = []
        if wanted and owner is None:
            warnings.append("Archivio dei ricordi non disponibile.")

        def read(budget):
            if d.closing or owner is None:
                return ""
            try:
                if context_id is None:
                    if owner is not d.durable_brain or revision != d.gemma_memory_revision:
                        return ""
                    raw = owner.prompt_context(spoken[:180], budget=budget)
                else:
                    if owner is not d.workspace or budget < 160:
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
            if d.closing or owner is None:
                return ()
            try:
                if context_id is None:
                    if owner is not d.durable_brain or revision != d.gemma_memory_revision:
                        return ()
                    pairs = owner.dialogue_pairs(count)
                    if d.closing or owner is not d.durable_brain or revision != d.gemma_memory_revision:
                        return ()
                    return pairs
                if owner is not d.workspace:
                    return ()
                pairs = owner.dialogue_pairs("project", context_id, count)
                return () if d.closing or owner is not d.workspace else pairs
            except (OSError, sqlite3.Error, ValueError) as exc:
                warnings.append("Scambi recenti non disponibili (" + type(exc).__name__ + ").")
                return ()

        read.recent_pairs = recent_pairs
        return (read if owner is not None else None), owner, revision, warnings
    def submit_gemma_voice(spoken, *, typed=False):
        if d.closing or d.gemma_trial_busy[0]:
            return False
        from intent_normalizer import before_model
        if before_model(spoken):
            return True              # capita dal motore interno (sinonimi) o domanda sì/no
        from model_gate import local_enabled as model_enabled, refused_local as model_refused
        if not model_enabled():
            d.write_line(model_refused(spoken))
            return True              # gestita: nessun passaggio a un altro modello
        try:
            chat_tab_active = d.chat_notebook.select() == str(d.chat_local_tab)
        except NameError:
            chat_tab_active = False
        chat_target = d.selected_chat_target() if chat_tab_active else None
        if chat_tab_active and chat_target is None:
            d.write_line("CHAT > Impossibile identificare la conversazione corrente.")
            return False
        explicit = re.match(r"^con gemma(?:[ ,:]+)(.+)$", spoken, re.I)
        candidates = ()
        if explicit:
            from program_apps.service import blocked
            provider = d.engine.program_apps
            question = explicit.group(1).strip()
            if blocked(question):
                d.write_line("LUMI > Per scegliere un’app indica un obiettivo da svolgere.")
                return False
            if provider is not None and provider.available():
                candidates = tuple(row for row in provider.entries()
                                   if row["enabled"] and row["available"])
            if not 1 <= len(candidates) <= 12:
                d.write_line("LUMI > Per la prova abilita da 1 a 12 app in Programmi e app.")
                return False
        if d.gemma_source[0] is None or not Path(d.gemma_source[0]).is_file():
            source = filedialog.askopenfilename(
                parent=d.root, title="Configura Gemma: seleziona koboldcpp.py",
                filetypes=[("Sorgente KoboldCpp", "koboldcpp.py"), ("Python", "*.py")])
            if not source:
                d.write_line("LUMI > Configurazione locale mancante. Nessun invio online.")
                return False
            if Path(source).name.lower() != "koboldcpp.py":
                d.write_line("LUMI > File sorgente non valido. Nessun invio online.")
                return False
            d.gemma_source[0] = source
        native_context = chat_target[0] if chat_target is not None else d.active_project_id
        native_document = d.documents.current.ident if d.documents.current else None
        native_actions = () if explicit else d.active_addon_actions()
        if explicit:
            reader, memory_owner, memory_revision, memory_warnings = (
                None, None, d.gemma_memory_revision, [])
        elif chat_target is not None:
            from local_model.chat_context import make_chat_history_reader
            try:
                reader = make_chat_history_reader(
                    d.chat_sessions_panel.store, chat_target[0],
                    project_id=chat_target[1])
            except (OSError, sqlite3.Error, ValueError) as exc:
                d.write_line("CHAT > Archivio locale non disponibile: " + type(exc).__name__)
                d.chat_sessions_panel.report_error(
                    "Archivio chat non accessibile. Nessuna richiesta inviata.")
                return False
            # The sole memory source of a chat instance is its own history.
            # No automatic global/project Second Brain recall in F2.
            memory_owner, memory_revision, memory_warnings = (
                None, d.gemma_memory_revision, [])
        else:
            reader, memory_owner, memory_revision, memory_warnings = (
                native_memory_request(d.active_project_id, spoken))
        # Make the session busy only after the selected chat and its reader
        # are valid: errors cannot strand the Gemma UI in a busy state.
        d.gemma_trial_busy[0] = True
        d.gemma_recent_reply[0] = None
        d.gemma_button.configure(state="disabled")
        # Typed text is the user's own message, like voice ("TU" role).
        d.write_line(("TU > " if typed else "UTENTE / VOCE > ") + spoken)
        voice_epoch = d.conversation_epoch
        from chat_stream import STREAM
        STREAM.start_request()

        def voice_worker():
            try:
                session = get_gemma_session()
                if explicit:
                    index = session.pick_program(
                        question, tuple(row["name"] for row in candidates))
                    app_id = candidates[index]["id"] if index is not None else None
                    d.gemma_trial_queue.put(("program_choice", (spoken, app_id), voice_epoch))
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
                        turn = d.chat_transport.ask_local_first(
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
                        turn.project_snapshot = d.active_project_id
                    d.gemma_trial_queue.put(("ok" if typed else "voice_ok", turn, voice_epoch))
            except Exception as exc:
                d.gemma_trial_queue.put(("error" if typed else "voice_error", str(exc)[:350], voice_epoch))
        threading.Thread(target=voice_worker, daemon=True,
                         name="jarvis-gemma").start()
        return True
    def submit_gemma_trial():
        if d.closing or d.gemma_trial_busy[0]:
            return
        question = d.request.get().strip()
        if not question:
            d.write_line("LUMI > Scrivi una domanda prima di avviare la prova.")
            return
        if (d.try_program_command(question) or try_gemma_app_followup(question)
                or submit_gemma_voice(question, typed=True)):
            d.request.set("")
    def poll_gemma_trial():
        from chat_stream import STREAM
        STREAM.drain(d.conversation_epoch, d.gemma_trial_busy[0] and not d.closing)
        try:
            while True:
                kind, value, voice_epoch = d.gemma_trial_queue.get_nowait()
                STREAM.drain(d.conversation_epoch, d.gemma_trial_busy[0] and not d.closing)
                STREAM.clear()
                d.gemma_trial_busy[0] = False
                d.gemma_button.configure(state="normal")
                if voice_epoch is not None and voice_epoch != d.conversation_epoch:
                    continue
                if kind in ("ok", "voice_ok"):
                    from local_model.native_conversation_session import NativeChatTurn
                    if isinstance(value, NativeChatTurn):
                        chat_target = getattr(value, "chat_target", None)
                        if d.closing or getattr(value, "project_snapshot", d.active_project_id) != d.active_project_id:
                            continue
                        if chat_target is not None:
                            if (value.context_id != chat_target[0]
                                    or d.selected_chat_target() != chat_target):
                                continue
                        elif value.context_id != d.active_project_id:
                            continue
                        if (value.context_id is None and value.memory_revision is not None
                                and value.memory_revision != d.gemma_memory_revision):
                            continue
                        if value.allowed_actions is not None:
                            from conversation_router import parse_native_conversation_intent, ConversationRejected
                            from dialogue_focus import is_ambiguous_short_reply
                            try:
                                intent = parse_native_conversation_intent(
                                    value.text, utterance=value.question,
                                    has_document=value.document_snapshot is not None,
                                    addon_resolver=(d.addon_manager.resolve if d.addon_manager is not None else None))
                                if intent.kind == 'capability':
                                    from program_apps.service import blocked
                                    if (intent.capability is None or
                                            intent.capability.action_id not in value.allowed_actions
                                            or is_ambiguous_short_reply(value.question)
                                            or blocked(value.question)):
                                        raise ConversationRejected('Richiesta di azione non identificata.')
                                    if (d.save_only_waiting or d.document_busy or d.doc_dialog.phase.startswith('awaiting_')
                                            or d.pending_project_name or d.pending_project_rename_id is not None
                                            or d.pending_project_trash_id is not None
                                            or d.pending_project_reference.question or d.telegram_voice_dialog.pending):
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
                                    d.write_line('LUMI > Risposta incompleta: limite Max Output raggiunto; '
                                               'azione non eseguita. ' + str(exc))
                                    d.speak_result('La risposta di Gemma è stata interrotta dal limite di output. '
                                                 'Non ho eseguito alcuna azione.')
                                else:
                                    d.write_line('LUMI > Risposta non interpretabile: ' + str(exc))
                                    d.speak_result('Non riesco a interpretare la risposta di Gemma. Puoi riprovare?')
                                continue
                        # UI context/epoch cannot change during this synchronous
                        # acceptance. The metadata commit never waits for native inference.
                        # A memory switch preserves the current live dialogue,
                        # but must not newly hydrate a revoked durable owner.
                        if (value.context_id is None and value.memory_owner is not None
                                and (value.memory_owner is not d.durable_brain or not d.memory_enabled.get())):
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
                                    d.write_line('LUMI > ' + notice)
                        if value.memory_warning:
                            d.write_line("MEMORIA > " + value.memory_warning)
                        owner = value.memory_owner
                        can_save = owner is not None and (
                            owner is d.workspace if value.context_id is not None else
                            owner is d.durable_brain and d.memory_enabled.get())
                        if chat_target is not None:
                            try:
                                d.chat_sessions_panel.persist_answer(
                                    chat_target[0], value.question, value.text,
                                    project_id=chat_target[1])
                            except (OSError, sqlite3.Error, ValueError) as exc:
                                d.write_line("CHAT > Risposta non archiviata: "
                                           + type(exc).__name__)
                                d.chat_sessions_panel.report_error(
                                    "Risposta non salvata su disco ("
                                    + str(d.chat_sessions_panel.pending_count)
                                    + " in attesa): nuovo tentativo al prossimo messaggio. "
                                    "Se chiudi Lumi prima, andranno perse.")
                        elif can_save and d.remember_exchange(value.question, value.text, "chat") is False:
                            d.write_line("MEMORIA > Scambio non archiviato.")
                        d.gemma_recent_reply[0] = (
                            voice_epoch, time.monotonic(),
                            value.question[:500] + " " + value.text[:500])
                        value = value.text
                if kind == "program_choice":
                    spoken, app_id = value
                    if app_id is None:
                        message = "Quale programma vuoi aprire?"
                        d.write_line("LUMI > " + message)
                        d.speak_result(message)
                    elif d.busy_local:
                        d.write_line("LUMI > Motore locale occupato. Riprova.")
                    else:
                        d.submit_local(message_override=spoken, source_utterance=spoken,
                                     addon_action_id="addon.programmi_app.avvia",
                                     program_call=("suggest_id", {"query": app_id}))
                elif kind == "voice_ok":
                    d.write_line("LUMI > " + value)
                    STREAM.speak_final(value, d.speak_result)
                elif kind == "voice_error":
                    d.write_line("GEMMA / ERRORE > " + value)
                    d.speak_result("Gemma locale non disponibile. Controlla la configurazione.")
                elif kind == "ok":
                    d.write_line("LUMI > " + value)
                    STREAM.speak_final(value, d.speak_result)
                else:
                    d.write_line("GEMMA / ERRORE > " + value)
        except queue.Empty:
            pass
        if not d.closing:
            d.root.after(150, poll_gemma_trial)
    funzioni = locals()
    return {nome: funzioni[nome] for nome in NOMI}
