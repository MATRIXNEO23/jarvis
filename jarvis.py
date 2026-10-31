"""Jarvis alpha — local commands, GPT conversation and offline voice.

App startup may automatically enable the locally configured Vosk microphone.
A visible settings switch can disable auto-listening for future launches; all
modes, including Standby, remain manually selectable at any time.
GPT requires the official SDK and an explicit account sign-in.
"""
from __future__ import annotations

import os
import queue
from collections import deque
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
from diagnostic_handoff import (build_external_review_prompt,
                                is_external_review_request, wants_external_advice,
                                summarize_operation_outcomes)
from settings import default_path
from telegram_commands import explicit_telegram_note
from telegram_bridge import TelegramBridge
from telegram_security import credentials_present
from telegram_voice import missing_voice_dependencies
from jarvis_persona import build_chat_prompt
from startup_greeting import startup_greeting
from adaptive_voice import SpeechCorrections, SpeechCorrectionError
from second_brain import SecondBrain, BrainError
from memory_boundaries import (PreferenceStore, OperationJournal, MemoryBoundaryError,
                               observed_local_result, observed_saved_file)
from preference_voice import parse_preference_intent
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

from document_dialog import DocumentDialog
from document_language import classify_document_choice
from document_store import destination_from_voice
from managed_documents import ManagedDocuments
from document_recovery import release_closed_document
from gpt_client import GPTClient, GPTUnavailable
from local_engine import LocalEngine, TaskResult
from offline_tts import OfflineSpeaker, installed_voices
from planner_ui import open_planner
from settings import load_settings, save_settings
from voice_control import (VoiceController, WakeWordGate, STANDBY, PUSH_TO_TALK, CONTINUOUS,
                           GPT_CONVERSATION, speech_to_local_command)


def main() -> None:
    settings = load_settings()
    root = tk.Tk()
    root.title("JARVIS // Interfaccia")
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

    # Every existing setting remains available without crowding the main HUD.
    # The settings window is created once, hidden until the user presses ⚙.
    settings_window = tk.Toplevel(root)
    settings_window.title("JARVIS // Impostazioni")
    settings_window.geometry("820x650")
    settings_window.minsize(650, 480)
    settings_window.withdraw()
    settings_window.protocol("WM_DELETE_WINDOW", settings_window.withdraw)
    settings_canvas = tk.Canvas(settings_window, bg=BG, highlightthickness=0)
    settings_scrollbar = ttk.Scrollbar(
        settings_window, orient="vertical", command=settings_canvas.yview)
    settings_scrollbar.pack(side="right", fill="y")
    settings_canvas.pack(side="left", fill="both", expand=True)
    settings_canvas.configure(yscrollcommand=settings_scrollbar.set)
    settings_inner = ttk.Frame(settings_canvas)
    settings_item = settings_canvas.create_window(
        (0, 0), window=settings_inner, anchor="nw")
    settings_inner.bind(
        "<Configure>",
        lambda event: settings_canvas.configure(
            scrollregion=settings_canvas.bbox("all")))
    settings_canvas.bind(
        "<Configure>",
        lambda event: settings_canvas.itemconfigure(
            settings_item, width=event.width))

    def show_settings() -> None:
        settings_window.deiconify()
        settings_window.lift()
        settings_window.focus_set()

    hud = JarvisHUD(root, show_settings)
    workspace_status=tk.StringVar(value="Progetti: inizializzazione.")
    telegram_status=tk.StringVar(value="Telegram: disattivato.")
    active_context_label=tk.StringVar(value="Contesto: GENERALE")
    active_project_id=None
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
    telegram_auto=tk.BooleanVar(value=settings["telegram_enabled"])
    orbit_nodes_cache=()

    frame = ttk.Frame(settings_inner, padding=15)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Impostazioni JARVIS",
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
    for label, mode in (("Standby (spento)", STANDBY),
                        ("Premi per parlare", PUSH_TO_TALK),
                        ("Ascolto continuo (Ehi Jarvis)", CONTINUOUS),
                        ("Conversazione continua GPT", GPT_CONVERSATION)):
        button = ttk.Radiobutton(mode_row, text=label, variable=voice_mode, value=mode)
        button.pack(side="left", padx=(0, 12))
        mode_buttons.append(button)
    auto_listen_enabled = tk.BooleanVar(value=settings["auto_listen"])
    auto_listen_switch = ttk.Checkbutton(
        audio_controls,
        text="Avvia Jarvis già in Conversazione continua GPT (microfono attivo)",
        variable=auto_listen_enabled)
    auto_listen_switch.pack(anchor="w", pady=(5, 1))
    ttk.Label(
        audio_controls,
        text="Il microfono resta acceso fino a quando scegli Standby. "
             "La voce non viene salvata: Vosk trascrive in locale; "
             "le frasi vengono inviate a GPT quando connesso.",
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
        speech_controls, text="Jarvis risponde a voce", variable=spoken_enabled)
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
    spoken_status = tk.StringVar(value="Voci locali: da rilevare.")
    ttk.Label(speech_controls, textvariable=spoken_status, wraplength=680).pack(anchor="w")

    # A compact popup keeps the existing Pavilion main window usable.
    last_voice_sample = tk.StringVar(value="Nessuna frase ancora riconosciuta.")
    voice_correction_button = ttk.Button(
        dictation_row, text="Correggi voce...")
    voice_correction_button.pack(side="right", padx=(6, 0))

    document_controls = ttk.Frame(frame)
    document_controls.pack(fill="x", pady=(0, 6))
    document_status = tk.StringVar(value="Documenti: nessuno aperto da Jarvis.")
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
    diagnostic_row = ttk.Frame(hud.command_host)
    diagnostic_row.pack(fill="x", pady=(0, 4))
    ttk.Label(diagnostic_row, textvariable=diagnostic_status,
              anchor="w").pack(side="left", fill="x", expand=True)
    ttk.Progressbar(diagnostic_row, mode="determinate", maximum=100,
                    variable=diagnostic_percent, length=110).pack(side="right")
    diagnostic_cancel_button = ttk.Button(
        diagnostic_row, text="Annulla", state="disabled")
    diagnostic_cancel_button.pack(side="right", padx=(0, 6))
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
    output_queue: queue.Queue[tuple] = queue.Queue()
    gpt_enabled = tk.BooleanVar(value=settings["gpt_enabled"])
    gpt_status = tk.StringVar(value="GPT: inizializzazione" if gpt_enabled.get() else "GPT: disattivato")
    busy_local = False
    busy_gpt = False
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
                    "jarvis >", "gpt >", "lia >"))
                else "errore" if (
                    "[failed]" in low or "[rejected]" in low
                    or low.startswith(("errore", "gpt: impossibile")))
                else "sistema")
        identity = {"utente":"●  TU",
                    "jarvis":"◉  JARVIS",
                    "azione":"✓  OPERAZIONE",
                    "errore":"!  ERRORE",
                    "sistema":"·  SISTEMA"}[role]
        # Strip repeated provider prefixes without hiding the actual result.
        prefixes = ("utente >", "tu >", "domanda a gpt >", "comando locale >",
                    "jarvis >", "gpt >", "lia >", "documento >",
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

    def remember_exchange(user: str, reply: str, kind: str = "chat") -> None:
        if re.search(r"\b(password|passphrase|token|pin|codice otp)\b",
                     user + " " + reply, re.I):
            return
        conversation_memory.remember(user, reply, kind)
        # Explicitly created project memory advances independently from
        # the general-chat Second Brain opt-in switch.
        if active_project_id is not None:
            if workspace is not None:
                try:
                    workspace.add_turn("project",active_project_id,
                                       user,reply,kind)
                except (OSError,sqlite3.Error,WorkspaceError) as exc:
                    workspace_status.set("Memoria progetto: "+str(exc)[:90])
            return
        if not memory_enabled.get():
            return
        if durable_brain is not None:
            try:
                durable_brain.remember_turn(user, reply, kind)
                memory_status_refresh()
            except (OSError, sqlite3.Error, BrainError) as exc:
                memory_status.set("Memoria locale non scritta: " + str(exc)[:95])

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

    def refresh_orbit_nodes() -> None:
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
                peer_id=settings.get("telegram_peer_id",0)
                if peer_id:
                    counts=workspace.telegram_counts(peer_id)
                    if counts["received"] or counts["replied"]:
                        items.append({
                            "id":"telegram:"+str(peer_id),
                            "kind":"telegram",
                            "name":settings.get("telegram_contact_name","Contatto")
                                   +" · ricevuti "+str(counts["received"])
                                   +" / risposti "+str(counts["replied"])
                                   +" / nuovi "+str(counts["unread"])})
                    notes=workspace.pending_for_contact(peer_id)
                    if notes:
                        items.append({"id":"telegram:pending",
                                      "kind":"pending",
                                      "name":"Da riferire: "+str(len(notes))})
                orbit_nodes_cache=tuple(items[:36])
                workspace_status.set(
                    "Progetti: "+str(len(projects))+" attivi. "
                    +"Archivi separati sul disco.")
            except (OSError,sqlite3.Error,WorkspaceError) as exc:
                workspace_status.set("Memoria progetti: "+str(exc)[:95])
        root.after(2600,refresh_orbit_nodes)

    def switch_context(project_id=None) -> bool:
        nonlocal active_project_id,conversation_epoch,pending_preference
        if busy_gpt or busy_local or document_busy:
            write_line("JARVIS > Finisco questa operazione prima di cambiare progetto.")
            return False
        if documents.current is not None or doc_dialog.phase != "idle":
            write_line("JARVIS > Chiudi il documento di Blocco note prima di cambiare progetto.")
            speak_result("Chiudi prima il documento aperto, per non confondere i progetti.")
            return False
        if project_id is not None:
            if (workspace is None or not workspace.project(project_id)
                    or workspace.project(project_id)["trashed"]):
                write_line("JARVIS > Progetto non trovato o nel cestino.")
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
        conversation_epoch+=1
        conversation_memory.clear()
        pending_conversation.clear()
        pending_project_reference.reset()
        pending_preference=None
        write_line(
            "JARVIS > "+("Progetto aperto: "+project["name"]+"."
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
                write_line("JARVIS > "+message)
                speak_result(message)
                return True
            return False

        def can_modify() -> bool:
            return (not busy_gpt and not busy_local and not document_busy
                    and documents.current is None and doc_dialog.phase=="idle")

        def acknowledge(message: str) -> bool:
            write_line("JARVIS > "+message)
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
                    message="Nel database attuale non risultano progetti. Controlla la cartella dati di Jarvis."
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
                write_line("JARVIS > Chiarimento annullato.")
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
                    write_line("JARVIS > "+message)
                    speak_result(message)
                    return True
                # The answer explicitly chooses the target requested by Jarvis.
                original=waiting
                if not switch_context(match["id"]):
                    pending_project_reference.reset()
                    return True
                write_line("JARVIS > Riferimento risolto: progetto "+match["name"]+".")
                if gpt_enabled.get() and active_gpt and not busy_gpt:
                    # Resume the previous READ-ONLY question in *chat* mode,
                    # never via the executor or an old capability intent.
                    try:
                        prompt=build_chat_prompt(
                            original,memory_context=recent_memory_for_gpt(original))
                        run_gpt("ask",prompt=prompt,source=original)
                        return True
                    except ValueError:
                        pass
                steps=workspace.project_steps(match["id"],limit=1)
                last=(" Ultima attività: "+steps[0]["title"]+
                      ", stato "+steps[0]["status"]+".") if steps else (
                      " Nessuna attività ancora registrata.")
                message="Progetto "+match["name"]+" selezionato."+last
                write_line("JARVIS > "+message)
                speak_result(message)
                return True
            except (OSError,sqlite3.Error,WorkspaceError,ValueError) as exc:
                pending_project_reference.reset()
                message="Non riesco a consultare il progetto: "+str(exc)[:100]
                write_line("JARVIS > "+message)
                speak_result(message)
                return True
        if pending_project_reference.start_if_needed(
                spoken,selected=active_project_id is not None):
            message="Quale progetto salvato vuoi aprire per risponderti?"
            write_line("JARVIS > "+message)
            speak_result(message)
            return True
        return False

    def handle_unanchored_short_reply(spoken: str) -> bool:
        """Never pretend an isolated yes/no confirms a stale action."""
        if (not is_ambiguous_short_reply(spoken)
                or conversation_memory.last_question()):
            return False
        message="A quale domanda ti riferisci?"
        write_line("JARVIS > "+message)
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
                write_line("JARVIS > "+message)
                speak_result(message)
                return True
            if answer in ("annulla","no","lascia stare","non salvare"):
                write_line("JARVIS > Preferenza non salvata.")
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
        write_line("JARVIS > "+message)
        speak_result(message)
        return True

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
        approved=messagebox.askyesno(
            "JARVIS — valutazione esterna",
            "Vuoi inviare al GPT collegato soltanto un rapporto tecnico "
            "ridotto dell'autodiagnosi?\n\n"
            "Contiene: file sorgenti RELATIVI, righe, segnali statici, "
            "indicatori generali e CONTEGGI ANONIMI delle operazioni.\n"
            "NON contiene codice completo, credenziali, documenti, "
            "log di sistema, percorsi personali né dati dei progetti.\n\n"
            "È un'analisi di possibili miglioramenti, NON una verifica "
            "del corretto funzionamento e non autorizza modifiche.",
            parent=root)
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
                last_diagnostic_audit,snapshot,outcomes)
        except (ValueError,TypeError) as exc:
            write_line("DIAGNOSTICA > Non posso preparare il rapporto: "
                       +str(exc)[:140])
            return True
        write_line("DIAGNOSTICA > Consenso ricevuto. Invio SOLO metadati "
                   "della diagnosi locale al GPT esterno per suggerimenti.")
        run_gpt("ask",prompt=prompt,source="")
        return True

    def update_diagnostic_ui() -> None:
        """Render the real local audit state, never infer it from GPT."""
        snapshot=diagnostic_session.snapshot()
        diagnostic_percent.set(snapshot.progress_percent)
        if snapshot.active:
            amount=(f"{snapshot.completed}/{snapshot.total}"
                    if snapshot.total else "preparazione")
            diagnostic_status.set(
                f"Autodiagnosi: {snapshot.phase} {amount} "
                f"({snapshot.elapsed_seconds} s)")
        else:
            diagnostic_status.set("Autodiagnosi: "+snapshot.phase)
        diagnostic_cancel_button.configure(
            state="normal" if snapshot.active else "disabled")

    def cancel_diagnostic() -> None:
        """Stop waiting, revoke external consent and reject late results."""
        nonlocal diagnostic_busy,pending_external_review
        old_run=diagnostic_session.cancel()
        if old_run is None:
            return
        diagnostic_busy=False
        pending_external_review=False
        update_diagnostic_ui()
        write_line("DIAGNOSTICA > Richiesta #"+str(old_run)+
                   " annullata nell'interfaccia. Il worker potrebbe "
                   "terminare dopo; i suoi risultati saranno ignorati.")
        speak_result("Ho annullato l'attesa della diagnosi. "
                     "Nessun file è stato modificato.")

    def try_self_diagnostic(spoken: str) -> bool:
        """Local bounded audit, visible progress and recoverable worker errors."""
        nonlocal diagnostic_busy,pending_external_review
        if is_external_review_request(spoken):
            return offer_external_diagnostic_review()
        request_kind=diagnostic_request(spoken)
        if request_kind is None:
            return False
        mode,module=request_kind
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
                     "Non avvio altri controlli; chiudi e riapri Jarvis.")
            diagnostic_status.set("Autodiagnosi: processi non responsivi")
            write_line("DIAGNOSTICA > "+message)
            speak_result(message)
            return True
        run_id=diagnostic_session.start()
        if run_id is None:
            return True
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

    def telegram_activity_window() -> None:
        peer_id=settings.get("telegram_peer_id",0)
        if workspace is None or not peer_id:
            return
        win=tk.Toplevel(root)
        win.title("JARVIS // Telegram — cronologia del contatto")
        win.geometry("640x420")
        log=tk.Text(win,wrap="word",bg="#031522",fg="#d7f6ff",
                    padx=12,pady=8)
        log.pack(fill="both",expand=True)
        try:
            records=workspace.telegram_activity(peer_id,limit=60)
            for item in reversed(records):
                direction=("RICEVUTO" if item["direction"]=="incoming"
                           else "JARVIS HA RISPOSTO")
                log.insert("end",item["when"]+"  "+direction
                           +" ["+item["kind"]+"]\n"
                           +item["text"][:260]+"\n\n")
            workspace.mark_telegram_read(peer_id)
        except (OSError,sqlite3.Error,WorkspaceError) as exc:
            log.insert("end","Archivio Telegram non leggibile: "+str(exc)[:100])
        log.configure(state="disabled")

    def orbit_open(identifier:str) -> None:
        if identifier.startswith("telegram:"):
            if identifier=="telegram:pending":
                write_line("JARVIS > Messaggi da riferire in attesa del contatto.")
            telegram_activity_window()
        elif identifier=="projects:more":
            open_project_manager()
        else:
            switch_context(identifier)

    def queue_telegram_note(message:str) -> bool:
        peer_id=settings.get("telegram_peer_id",0)
        if not peer_id or workspace is None:
            write_line("JARVIS > Devi prima autorizzare un contatto Telegram.")
            return False
        try:
            workspace.note_for_contact(peer_id,message)
        except (OSError,sqlite3.Error,WorkspaceError) as exc:
            write_line("JARVIS > Non posso salvare il messaggio: "+str(exc)[:100])
            return False
        write_line("JARVIS > Messaggio memorizzato per "
                   +settings["telegram_contact_name"]
                   +". Lo riferirò al prossimo contatto, se Telegram è attivo.")
        return True

    def leave_telegram_note_dialog() -> None:
        if not settings.get("telegram_peer_id"):
            telegram_status.set("Configura prima il contatto autorizzato.")
            return
        message=simpledialog.askstring(
            "JARVIS / Telegram",
            "Che cosa devo riferire al contatto autorizzato?",
            parent=root)
        if message:
            queue_telegram_note(message)

    def maybe_queue_telegram_note(message:str) -> bool:
        parsed=explicit_telegram_note(
            message,settings.get("telegram_contact_name",""))
        if parsed is None:
            return False
        queue_telegram_note(parsed)
        return True

    def ask_telegram_gpt(prompt:str) -> str:
        # Runs in a worker: no Tk variable or widget is accessed here.
        if not telegram_gpt_ready.is_set():
            return ""
        try:
            result=service.call("ask",prompt=prompt,timeout=120)
            return str(result.get("text",""))
        except (GPTUnavailable,OSError,RuntimeError):
            return ""

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
            peer_id=settings.get("telegram_peer_id",0)
            if not peer_id or not credentials_present() or workspace is None:
                telegram_auto.set(False)
                telegram_status.set(
                    "Telegram: configura prima l'account e un solo contatto.")
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
            telegram_bridge=TelegramBridge(
                workspace,peer_id,
                settings["telegram_contact_name"],ask_telegram_gpt,
                output_queue.put,voice_name=selected_voice())
            if telegram_bridge.start():
                settings["telegram_enabled"]=True
                telegram_status.set("Telegram: collegamento in corso, SOLO "
                                    +settings["telegram_contact_name"]+".")
        try:
            save_settings(settings)
        except (OSError,ValueError) as exc:
            telegram_status.set("Impossibile salvare Telegram: "+str(exc)[:100])
            if telegram_bridge:
                telegram_bridge.stop()
            telegram_auto.set(False)
            settings["telegram_enabled"]=False

    def telegram_reconfigure():
        if telegram_bridge:
            telegram_bridge.stop()
        current=load_settings()
        for key in ("telegram_peer_id","telegram_contact_name"):
            settings[key]=current[key]
        settings["telegram_enabled"]=False
        telegram_auto.set(False)
        telegram_status.set(
            "Contatto autorizzato: "+(
                settings["telegram_contact_name"] or "nessuno"
            )+"; risposte spente.")
        save_settings(settings)

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

    def run_gpt(action: str, **params) -> None:
        nonlocal busy_gpt
        if busy_gpt or not gpt_enabled.get() or closing:
            return
        busy_gpt = True
        refresh_buttons()
        if action == "sign_in":
            gpt_status.set("GPT: in attesa del login nel browser...")
        elif action in ("ask", "conversation"):
            gpt_status.set("GPT: elaborazione richiesta...")
        elif action == "disconnect":
            gpt_status.set("GPT: scollegamento...")
        else:
            gpt_status.set("GPT: verifica connessione...")

        def worker() -> None:
            epoch = params.get("epoch") if action == "conversation" else None
            doc_snapshot = params.get("document_id") if action == "conversation" else None
            user_utterance = params.get("utterance", "") if action == "conversation" else ""
            typed_question = params.get("source", "") if action == "ask" else ""
            try:
                timeout = 600 if action == "sign_in" else 180 if action in ("ask", "conversation") else 40
                sdk_action = "ask" if action == "conversation" else action
                sdk_params = {key: value for key, value in params.items()
                              if key not in ("epoch", "document_id", "utterance", "source")}
                result = service.call(sdk_action, timeout=timeout, **sdk_params)
                if action == "conversation":
                    output_queue.put(("conversation_ok", epoch, doc_snapshot,
                                      user_utterance, result))
                else:
                    output_queue.put(("gpt_ok", action, result, typed_question))
            except Exception as exc:
                if action == "conversation":
                    output_queue.put(("conversation_error", epoch, user_utterance,
                                      str(exc)[:220]))
                else:
                    output_queue.put(("gpt_error", action, str(exc)[:400]))
        threading.Thread(target=worker, daemon=True, name="jarvis-gpt-worker").start()

    def start_conversation_gpt(spoken: str) -> None:
        """Send one speech turn with the latest completed dialogue attached.

        Local self-diagnostics ALWAYS take precedence over conversational
        model guesses about access to Jarvis's own files.
        """
        if not closing and try_self_diagnostic(spoken):
            return
        if (busy_gpt or closing or voice_mode.get() != GPT_CONVERSATION
                or not gpt_enabled.get() or not active_gpt):
            return
        reconcile_document_session(force=True)
        snapshot = documents.current.ident if documents.current else None
        try:
            prompt = build_conversation_prompt(
                spoken, has_document=snapshot is not None,
                memory_context=recent_memory_for_gpt(spoken))
        except ConversationRejected as exc:
            write_line("JARVIS > " + str(exc))
            return
        write_line("JARVIS > Elaboro la tua richiesta...")
        run_gpt("conversation", prompt=prompt,
                epoch=conversation_epoch,
                document_id=snapshot, utterance=spoken)

    def toggle_gpt() -> None:
        nonlocal active_gpt, conversation_epoch
        previous = settings["gpt_enabled"]
        try:
            settings["gpt_enabled"] = bool(gpt_enabled.get())
            save_settings(settings)
        except (OSError, ValueError) as exc:
            settings["gpt_enabled"] = previous
            gpt_enabled.set(previous)
            messagebox.showerror("Impossibile salvare", str(exc), parent=root)
            return
        if gpt_enabled.get():
            gpt_status.set("GPT: attivo nelle impostazioni; controllo collegamento...")
            run_gpt("status")
        else:
            conversation_epoch += 1
            pending_conversation.clear()
            doc_dialog.revoke_pending()
            planner_abort_event.set()
            active_gpt = False
            gpt_status.set("GPT: disattivato manualmente")
            threading.Thread(target=service.stop, daemon=True).start()
            refresh_buttons()

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
        if not messagebox.askyesno(
            "Cancella il Second Brain",
            "Eliminare scambi, operazioni e correzioni vocali archiviate da Lia? "
            "Questa operazione non può essere annullata. "
            "La cronologia delle attività del motore locale resta separata.",
            parent=root,
        ):
            return
        try:
            target = durable_brain if durable_brain is not None else SecondBrain()
            target.clear_all()
            conversation_memory.clear()
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

    ttk.Checkbutton(
        frame, text="Abilita collegamento ChatGPT (attivo di default, spegnimento manuale)",
        variable=gpt_enabled, command=toggle_gpt
    ).pack(anchor="w")
    ttk.Label(frame, textvariable=gpt_status, wraplength=710).pack(anchor="w", pady=(5, 6))

    gpt_buttons = ttk.Frame(frame)
    gpt_buttons.pack(fill="x", pady=(0, 7))
    connect = ttk.Button(gpt_buttons, text="Connetti ChatGPT", command=lambda: run_gpt("sign_in"))
    connect.pack(side="left", padx=(0, 8))
    disconnect = ttk.Button(gpt_buttons, text="Scollega account", command=lambda: run_gpt("disconnect"))
    disconnect.pack(side="left")
    ttk.Label(frame, text="Il login usa il browser ufficiale; nessuna chiave API e nessuna fatturazione a consumo.").pack(anchor="w")

    brain_controls = ttk.Frame(frame)
    brain_controls.pack(fill="x", pady=(5, 3))
    memory_toggle = ttk.Checkbutton(
        brain_controls, text="Second Brain locale (ricorda conversazioni e attività)",
        variable=memory_enabled, command=toggle_memory)
    memory_toggle.pack(side="left", padx=(0, 10))
    memory_clear_button = ttk.Button(
        brain_controls, text="Cancella memoria generale (non progetti)", command=clear_saved_memory)
    memory_clear_button.pack(side="right")
    ttk.Label(frame, textvariable=memory_status, wraplength=710).pack(
        anchor="w", pady=(0, 2))
    ttk.Label(
        frame,
        text="I ricordi restano sul PC. Se usi ChatGPT, gli estratti pertinenti "
             "vengono inviati al modello per comprendere il contesto; "
             "non vengono salvati i corpi completi delle email.",
        wraplength=710
    ).pack(anchor="w", pady=(0, 4))

    workspace_panel=ttk.LabelFrame(
        frame,text="Progetti — contesto indipendente e continuità",padding=8)
    workspace_panel.pack(fill="x",pady=(6,8))
    ttk.Label(frame,
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
        frame,text="Telegram — un solo contatto e risposte vocali",padding=8)
    telegram_panel.pack(fill="x",pady=(3,10))
    telegram_toggle=ttk.Checkbutton(
        telegram_panel,text="Risposte vocali automatiche ON / OFF",
        variable=telegram_auto)
    telegram_toggle.pack(anchor="w")
    telegram_row=ttk.Frame(telegram_panel)
    telegram_row.pack(fill="x",pady=(4,3))
    telegram_configure_button=ttk.Button(
        telegram_row,text="Configura Telegram (accesso sicuro)")
    telegram_configure_button.pack(side="left",padx=(0,8))
    telegram_reload_button=ttk.Button(
        telegram_row,text="Rileggi contatto autorizzato")
    telegram_reload_button.pack(side="left",padx=(0,8))
    telegram_note_button=ttk.Button(
        telegram_row,text="Lascia un messaggio per il contatto")
    telegram_note_button.pack(side="left")
    ttk.Label(
        telegram_panel,textvariable=telegram_status,wraplength=690
    ).pack(anchor="w",pady=(3,0))
    ttk.Label(
        telegram_panel,
        text="Solo la chat privata autorizzata; le risposte sono note vocali "
             "SAPI/OGG e JARVIS si presenta come assistente. "
             "Occorrono Telethon gratuito e FFmpeg locale. Nessun invio "
             "di test o risposta finché non attivi questa opzione.",
        wraplength=690).pack(anchor="w",pady=(3,0))

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
    buttons_row = ttk.Frame(hud.command_host)
    # Hidden until the user clicks ⋯, like secondary controls in the concept.
    local_button = ttk.Button(buttons_row, text="Esegui locale")
    local_button.pack(side="left", padx=(0, 4))
    ask_button = ttk.Button(buttons_row, text="Chiedi a GPT")
    ask_button.pack(side="left", padx=(0, 4))
    plan_button = ttk.Button(buttons_row, text="Pianifica attività")
    plan_button.pack(side="left", padx=(0, 4))
    diagnostic_button = ttk.Button(buttons_row, text="Autodiagnosi Jarvis")
    diagnostic_button.pack(side="left")

    # Native Tk text with a dark ttk scrollbar matches the concept's
    # streamlined chat panel without third-party UI or web technologies.
    chat_panel = ttk.Frame(hud.console_host)
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
    write_line("Jarvis locale pronto. Scrivi 'aiuto' per vedere i comandi disponibili.")

    try:
        engine = LocalEngine()
    except (OSError, ValueError) as exc:
        messagebox.showerror("Motore locale non disponibile", str(exc), parent=root)
        root.destroy()
        return

    speaker = OfflineSpeaker(notify_error=lambda reason: output_queue.put(("tts_error", reason)))
    voice = VoiceController(output_queue.put, ignore_audio=speaker.is_audible)
    wake_gate = WakeWordGate()
    dictation = DesktopDictation()

    def selected_voice() -> str:
        choice = spoken_voice.get()
        return "" if choice == DEFAULT_VOICE_LABEL else choice

    def save_speech_preferences() -> None:
        settings["tts_enabled"] = bool(spoken_enabled.get())
        settings["tts_voice"] = selected_voice()
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

    def test_speech() -> None:
        if not speaker.speak("Pronto. Questa è la voce di Jarvis.", selected_voice()):
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
            try:
                if operation == "open" or (
                        operation == "compose" and target == "new_notepad"):
                    documents.forget_if_closed()
                if operation == "open":
                    result = documents.open_blank()
                elif operation == "compose":
                    result = documents.compose(content, target)
                elif operation == "save" and path is not None:
                    result = documents.save_and_close(document_id, path)
                elif operation == "save_only" and path is not None:
                    result = documents.save_only(document_id, path)
                elif operation == "discard":
                    result = documents.discard_and_close(document_id)
                else:
                    raise ValueError("Operazione documento non consentita.")
                output_queue.put(("document_ok", operation, result, close_after))
            except (OSError, ValueError) as exc:
                output_queue.put(("document_error", operation, str(exc)[:250]))

        # A started save must finish even when the Jarvis UI closes.
        threading.Thread(target=worker, daemon=False, name="jarvis-document-worker").start()

    def ask_to_close_document(source_utterance: str = "") -> None:
        if document_busy:
            announce_document("Attendi la fine della scrittura prima di chiudere.")
            return
        if doc_dialog.phase != "editing" or doc_dialog.document_id is None:
            announce_document("Non ho un documento Blocco note gestito da Jarvis da chiudere.")
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
            + ("in conversazione continua GPT." if desired
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
            mic_status.set("Conversazione GPT selezionata: frasi trascritte e inviate a GPT. "
                           "Parla senza dire Ehi Jarvis.")
            if not spoken_enabled.get():
                spoken_enabled.set(True)
                save_speech_preferences()
            if not gpt_enabled.get() or not active_gpt:
                write_line("Conversazione GPT: per le richieste non locali collega ChatGPT.")
        else:
            mic_status.set("Ascolto continuo con Ehi Jarvis selezionato.")

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
        open_planner(
            root, service, engine,
            lambda: bool(gpt_enabled.get() and active_gpt and not busy_gpt and not closing),
            local_execution_lock, planner_abort_event,
            on_approved=journal_plan_approved,
            on_step=journal_plan_step,
            on_finished=journal_plan_finished,
        )

    def submit_local(event=None, message_override: str | None = None,
                     source_utterance: str = "") -> None:
        nonlocal busy_local, last_user_for_action, project_local_ticket
        nonlocal local_operation_id
        if busy_local or closing:
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
            write_line("JARVIS > Impossibile salvare il checkpoint: comando non eseguito.")
            return
        if operation_ledger is None:
            finish_project_work(project_local_ticket,"interrupted",
                                "Registro operativo non disponibile.")
            project_local_ticket=None
            write_line("JARVIS > Registro operativo non disponibile: non eseguo.")
            return
        try:
            local_operation_id=operation_ledger.begin(
                "local_request",origin="local",project_id=active_project_id or "")
            operation_ledger.running(local_operation_id)
        except (OSError,sqlite3.Error,MemoryBoundaryError) as exc:
            finish_project_work(project_local_ticket,"interrupted",
                                "Impossibile registrare l'operazione.")
            project_local_ticket=None
            write_line("JARVIS > Operazione bloccata: "+str(exc)[:95])
            return
        busy_local = True
        refresh_buttons()

        def worker() -> None:
            try:
                with local_execution_lock:
                    result = engine.execute(message)
                output_queue.put(("local", result))
            except Exception:
                output_queue.put(("local", TaskResult("-", "internal", "failed",
                    "Errore interno: controlla i dati di Jarvis.")))
        threading.Thread(target=worker, daemon=True).start()

    def submit_gpt() -> None:
        if closing:
            return
        message = request.get().strip()
        if not message:
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
        request.set("")
        write_line("DOMANDA A GPT > " + message)
        try:
            prompt = build_chat_prompt(
                message, memory_context=recent_memory_for_gpt(message))
        except ValueError as exc:
            request.set(message)
            write_line("JARVIS > " + str(exc))
            return
        run_gpt("ask", prompt=prompt, source=message)

    def diagnostic_heartbeat() -> None:
        """Independent watchdog: runs even if another event handler fails."""
        nonlocal diagnostic_busy,pending_external_review
        if closing:
            return
        root.after(800,diagnostic_heartbeat)
        check=diagnostic_session.check()
        if check=="timeout":
            diagnostic_busy=False
            pending_external_review=False
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
        nonlocal diagnostic_busy,last_diagnostic_audit,pending_external_review
        nonlocal last_user_for_action, last_user_for_document
        nonlocal project_local_ticket, project_document_ticket
        nonlocal document_topic,document_owner_project_id,save_only_waiting
        if closing:
            return
        # A malformed or unexpected event must not permanently kill the
        # event pump and strand an in-progress diagnostic forever.
        root.after(120, poll)
        reconcile_document_session()
        try:
            while True:
                kind, *data = output_queue.get_nowait()
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
                    write_line("DIAGNOSTICA > "+format_audit(audit))
                    write_line("DIAGNOSTICA > Se vuoi un parere del modello "
                               "esterno, puoi chiedere: "
                               "'Jarvis, valuta la diagnosi con GPT'. "
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
                    update_diagnostic_ui()
                    write_line("DIAGNOSTICA > Analisi non completata. "
                               "Errore locale: "+str(error_type)[:90]+
                               ". Puoi riprovare con il pulsante.")
                    speak_result("La diagnosi non è riuscita. "
                                 "Ho scritto il tipo di errore nella console.")
                elif kind == "project_journal_error":
                    workspace_status.set("Esito progetto non registrato: "+str(data[0])[:100])
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
                        telegram_auto.set(False)
                        settings["telegram_enabled"]=False
                        try:
                            save_settings(settings)
                        except (OSError,ValueError):
                            pass
                        telegram_status.set("Telegram: collegamento terminato.")
                elif kind == "voice_status":
                    if voice_mode.get() != STANDBY:
                        mic_status.set(data[0])
                    if (dictation.enabled and
                            (str(data[0]).startswith("Microfono spento") or
                             str(data[0]).startswith("Voce non disponibile"))):
                        sync_dictation_ui(dictation.disable())
                elif kind == "voice_text":
                    raw_spoken = str(data[0]).strip()
                    spoken = raw_spoken
                    if raw_spoken and voice_mode.get() != STANDBY:
                        # No new acoustic model or background training:
                        # correct approved app names in a single cached pass.
                        last_voice_sample.set(raw_spoken)
                        if speech_lexicon is not None and memory_enabled.get():
                            spoken = speech_lexicon.correct(raw_spoken)
                            if spoken != raw_spoken:
                                write_line("VOCABOLARIO LIA > " + spoken)
                    if voice_mode.get() != STANDBY and spoken and not speaker.is_audible():
                        if voice_mode.get() == GPT_CONVERSATION:
                            write_line("TU > " + spoken)
                            # Safe local diagnostics must not wait for a GPT
                            # response or a stale Notepad confirmation.
                            if try_self_diagnostic(spoken):
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
                            elif gpt_enabled.get() and active_gpt:
                                if busy_gpt:
                                    if len(pending_conversation) < 3:
                                        pending_conversation.append(
                                            (conversation_epoch, spoken))
                                        write_line(
                                            "JARVIS > Ho ricevuto la frase. "
                                            "La considero appena termino la risposta.")
                                    else:
                                        write_line(
                                            "JARVIS > Ho già tre frasi in attesa. "
                                            "Ripeti quest'ultima tra poco.")
                                else:
                                    start_conversation_gpt(spoken)
                            elif not active_gpt or not gpt_enabled.get():
                                speak_result("GPT non è connesso. Puoi ancora usare i comandi locali.")
                                write_line("GPT non connesso: frase non inviata.")
                            else:
                                write_line("GPT sta rispondendo: attendi prima di parlare.")
                            continue
                        route_type = "command"  # Push-to-talk already requires a manual press.
                        if voice_mode.get() == CONTINUOUS:
                            route_type, spoken = wake_gate.route(
                                spoken, dictation_active=dictation.enabled)
                            if route_type == "wake":
                                mic_status.set("Ehi Jarvis riconosciuto: ascolto il prossimo comando.")
                            if route_type not in ("command", "dictation"):
                                continue
                        if route_type == "dictation":
                            # Only manual dictation may insert free speech.
                            sync_dictation_ui(dictation.insert(spoken))
                            continue
                        # Log commands that passed the wake/press gate.
                        # Do not record free dictation or phrases ignored by wake.
                        write_line("TU > " + spoken)
                        if try_self_diagnostic(spoken):
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
                elif kind == "local":
                    result = data[0]
                    busy_local = False
                    write_line(f"[{result.status}] {result.message}")
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
                            write_line("JARVIS > Registro operazioni: "+str(exc)[:90])
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
                        speak_result(result.message)
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
                            write_line("JARVIS > Registro documento: "+str(exc)[:90])
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
                            write_line("JARVIS > Registro documento: "+str(exc)[:90])
                    document_operation_id=None
                    finish_project_work(project_document_ticket,"failed",error_message)
                    project_document_ticket = None
                    remember_exchange(last_user_for_document or operation,
                                      error_message, "error")
                    last_user_for_document = ""
                elif kind == "conversation_ok":
                    busy_gpt = False
                    epoch, doc_snapshot, original_phrase, result = data
                    if (epoch == conversation_epoch and
                            voice_mode.get() == GPT_CONVERSATION and
                            gpt_enabled.get() and active_gpt):
                        try:
                            intent = parse_conversation_intent(
                                result.get("text", ""),
                                has_document=doc_snapshot is not None)
                        except ConversationRejected as exc:
                            write_line("GPT: impossibile interpretare la risposta: " + str(exc))
                            speak_result("Non ho capito con sicurezza. Puoi ripetere?")
                            remember_exchange(
                                original_phrase, "Non ho capito con sicurezza. Puoi ripetere?",
                                "clarify")
                        else:
                            if (is_ambiguous_short_reply(original_phrase)
                                    and intent.kind not in ("chat","clarify")):
                                message=("Per eseguire un'azione, dimmi "
                                         "esplicitamente cosa vuoi fare.")
                                write_line("JARVIS > "+message)
                                speak_result(message)
                                remember_exchange(original_phrase,message,"clarify")
                                continue
                            if intent.kind in ("chat", "clarify"):
                                write_line("JARVIS > " + intent.reply)
                                speak_result(intent.reply)
                                remember_exchange(original_phrase, intent.reply,
                                                  intent.kind)
                            elif intent.kind == "capability":
                                cap = intent.capability
                                current_id = (documents.current.ident
                                              if documents.current else None)
                                if cap is None:
                                    announce_document("Azione non disponibile.")
                                elif cap.handler == "local" and cap.plan is not None:
                                    if not busy_local:
                                        submit_local(
                                            message_override=cap.plan.steps[0].command,
                                            source_utterance=original_phrase)
                                    else:
                                        speak_result("Operazione in corso, riprova.")
                                elif cap.handler == "document_open":
                                    if current_id is None:
                                        document_operation(
                                            "open", source_utterance=original_phrase)
                                    else:
                                        announce_document(
                                            "C'è già un Blocco note gestito da Jarvis. "
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
                                        "da Jarvis. Non ho inserito il testo.")
                                elif current_id is not None and intent.target == "new_notepad":
                                    announce_document(
                                        "C'è già un documento aperto da Jarvis. "
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
                    busy_gpt = False
                    epoch, original_phrase, reason = data
                    if epoch == conversation_epoch and voice_mode.get() == GPT_CONVERSATION:
                        write_line("Conversazione GPT: " + reason)
                        speak_result("GPT non è disponibile. Puoi riprovare.")
                        remember_exchange(original_phrase, "GPT non disponibile, riprova.",
                                          "error")
                elif kind == "gpt_ok":
                    action, result, *rest = data
                    busy_gpt = False
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
                            write_line("Account scollegato da Jarvis.")
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
                    spoken_status.set("Voci Windows non disponibili: " + str(data[0]))
                    refresh_voices_button.configure(state="normal")
                elif kind == "gpt_error":
                    action, reason = data
                    busy_gpt = False
                    active_gpt = False if action != "ask" else active_gpt
                    if gpt_enabled.get():
                        gpt_status.set("GPT: collegamento non disponibile o richiesta fallita.")
                        write_line("GPT: " + str(reason))
                refresh_buttons()
        except queue.Empty:
            pass

        try:
            while True:
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
                    conversation_epoch += 1
                    planner_abort_event.set()
                    if gpt_enabled.get():
                        gpt_status.set("GPT: modulo non pronto.")
                        write_line("GPT: " + str(event.get("error", "errore")))
                elif event.get("event") == "stopped" and gpt_enabled.get() and not busy_gpt:
                    conversation_epoch += 1
                    planner_abort_event.set()
                    active_gpt = False
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

    def send_console_input(event=None) -> None:
        message=request.get().strip()
        if not message:
            return
        reconcile_document_session(force=True)
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
        if try_self_diagnostic(message):
            request.set("")
            return
        if maybe_queue_telegram_note(message):
            request.set("")
            return
        if gpt_enabled.get() and active_gpt:
            if busy_gpt:
                write_line("JARVIS > Sto già elaborando. Attendi la risposta.")
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
    hud.set_orbit_open_handler(orbit_open)
    hud_send_button.configure(command=send_console_input)
    hud_mic_button.configure(command=toggle_hud_microphone)
    tools_button.configure(command=toggle_console_tools)
    local_button.configure(command=submit_local)
    ask_button.configure(command=submit_gpt)
    plan_button.configure(command=submit_plan)
    diagnostic_button.configure(
        command=lambda: try_self_diagnostic("Jarvis, fai un'autodiagnosi"))
    diagnostic_cancel_button.configure(command=cancel_diagnostic)
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
    refresh_voices_button.configure(command=refresh_voices)
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
        closing = True
        planner_abort_event.set()
        doc_dialog.revoke_pending()
        dictation.disable()
        wake_gate.reset()
        voice.close()
        if telegram_bridge:
            telegram_bridge.stop()
        telegram_gpt_ready.clear()
        speaker.close()
        hud.close()
        root.destroy()
        # Non-daemon: ensure the Node child is terminated before Python exits.
        threading.Thread(target=service.stop, daemon=False, name="jarvis-gpt-shutdown").start()

    ttk.Button(frame, text="Esci", command=close).pack(anchor="e", pady=(9, 0))
    # Settings are intentionally hidden until the gear is pressed.
    # The normal window-close control invokes the same safe shutdown.
    hud.set_close_handler(close)
    hud.set_state_provider(lambda: {
        "speaking": speaker.is_speaking(),
        # Orange only if the real Vosk input stream has actually opened.
        # Push-to-talk selected but not pressed must remain cyan.
        "listening": voice.is_user_speaking(),
        "mic_enabled": voice.is_listening(),
        "thinking": busy_gpt or busy_local or document_busy,
        "connected": active_gpt,
        "memory": memory_enabled.get(),
        "orbit_nodes": orbit_nodes_cache,
    })
    def initial_launch() -> None:
        """App-only autostart: never adds Windows login/run-at-boot entries."""
        if closing:
            return
        if auto_listen_enabled.get():
            voice_mode.set(GPT_CONVERSATION)
            change_voice_mode()
        # The local SAPI voice is suppressed from Vosk input by
        # ignore_audio=speaker.is_audible, also during the cooldown.
        greeting = startup_greeting()
        write_line("JARVIS > " + greeting)
        speak_result(greeting)

    root.protocol("WM_DELETE_WINDOW", close)
    settings_window.bind("<Escape>", lambda _event: settings_window.withdraw())
    root.bind("<Control-comma>", lambda _event: show_settings())
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
    root.mainloop()


if __name__ == "__main__":
    main()
