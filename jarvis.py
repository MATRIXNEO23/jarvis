"""Jarvis alpha — local commands, optional GPT and opt-in offline voice.

The microphone always starts OFF; only a user action opens an audio stream.
The optional speech model is never loaded at application startup.
GPT requires the official SDK and an explicit sign-in.
"""
from __future__ import annotations

import queue
import json
import re
import sqlite3
from conversation_memory import ConversationMemory
from second_brain import SecondBrain, BrainError
from desktop_dictation import DesktopDictation, dictation_voice_action
from conversation_router import (
    ConversationRejected, build_conversation_prompt, parse_conversation_intent,
)
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import webbrowser

from document_dialog import DocumentDialog
from document_language import classify_document_choice
from document_store import destination_from_voice
from managed_documents import ManagedDocuments
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
    root.title("Jarvis — alpha")
    root.geometry("840x740")
    root.minsize(630, 560)

    frame = ttk.Frame(root, padding=15)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Jarvis", font=("Segoe UI", 17, "bold")).pack(anchor="w")
    mic_status = tk.StringVar(value="Microfono: SPENTO all'avvio")
    ttk.Label(frame, textvariable=mic_status, wraplength=710).pack(anchor="w", pady=(2, 6))
    voice_mode = tk.StringVar(value=STANDBY)
    audio_controls = ttk.LabelFrame(frame, text="Voce offline — attivazione solo manuale", padding=8)
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

    document_controls = ttk.Frame(frame)
    document_controls.pack(fill="x", pady=(0, 6))
    document_status = tk.StringVar(value="Documenti: nessuno aperto da Jarvis.")
    ttk.Label(document_controls, textvariable=document_status, wraplength=530).pack(
        side="left", fill="x", expand=True)
    choose_save_button = ttk.Button(document_controls, text="Scegli dove salvare",
                                    state="disabled")
    choose_save_button.pack(side="right", padx=(6, 0))
    doc_choices = ttk.Frame(frame)
    doc_choices.pack(fill="x", pady=(0, 5))
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
    conversation_memory = ConversationMemory()
    last_user_for_action = ""
    last_user_for_document = ""
    memory_enabled = tk.BooleanVar(value=settings["memory_enabled"])
    memory_status = tk.StringVar(value="Second Brain: inizializzazione.")
    durable_brain: SecondBrain | None = None
    if memory_enabled.get():
        try:
            durable_brain = SecondBrain()
            memory_status.set("Second Brain: attivo (memoria locale sul PC).")
        except (OSError, ValueError) as exc:
            memory_enabled.set(False)
            memory_status.set("Second Brain non disponibile: " + str(exc)[:90])
    else:
        memory_status.set("Second Brain: disattivato, conversazione breve solo in RAM.")

    def write_line(text: str) -> None:
        output.configure(state="normal")
        output.insert("end", text + "\n\n")
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
        if re.search(r"\\b(password|passphrase|token|pin|codice otp)\\b",
                     user + " " + reply, re.I):
            return
        conversation_memory.remember(user, reply, kind)
        if durable_brain is not None and memory_enabled.get():
            try:
                durable_brain.remember_turn(user, reply, kind)
                memory_status_refresh()
            except (OSError, sqlite3.Error, BrainError) as exc:
                memory_status.set("Memoria locale non scritta: " + str(exc)[:95])

    def remember_completed_action(action_id: str, application: str,
                                  summary: str, receipt_id: str,
                                  *, filename: str = "", folder: str = "") -> None:
        if durable_brain is None or not memory_enabled.get():
            return
        metadata = {}
        if filename:
            metadata["file_name"] = filename[:140]
        if folder:
            metadata["folder"] = folder[:140]
        try:
            durable_brain.record_completed_action(
                action_id, application, summary,
                receipt_id=receipt_id, metadata=metadata, verified=True)
            memory_status_refresh()
        except (OSError, sqlite3.Error, BrainError) as exc:
            memory_status.set("Ricevuta non registrata: " + str(exc)[:90])

    def recent_memory_for_gpt(spoken: str) -> str:
        short = conversation_memory.context(max_chars=360)
        if durable_brain is None or not memory_enabled.get():
            return short
        try:
            long = durable_brain.prompt_context(spoken, budget=540)
        except (OSError, sqlite3.Error, BrainError) as exc:
            memory_status.set("Ricerca memoria non disponibile: " + str(exc)[:80])
            return short
        return json.dumps({"breve": json.loads(short),
                           "permanente": json.loads(long)}, ensure_ascii=False)

    def display_status(state: dict) -> None:
        nonlocal active_gpt, conversation_epoch
        connected = state.get("status") == "connected" and state.get("sharing") is True
        active_gpt = connected
        if not connected:
            conversation_epoch += 1
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
            try:
                timeout = 600 if action == "sign_in" else 180 if action in ("ask", "conversation") else 40
                sdk_action = "ask" if action == "conversation" else action
                sdk_params = {key: value for key, value in params.items()
                              if key not in ("epoch", "document_id", "utterance")}
                result = service.call(sdk_action, timeout=timeout, **sdk_params)
                if action == "conversation":
                    output_queue.put(("conversation_ok", epoch, doc_snapshot,
                                      user_utterance, result))
                else:
                    output_queue.put(("gpt_ok", action, result))
            except Exception as exc:
                if action == "conversation":
                    output_queue.put(("conversation_error", epoch, user_utterance,
                                      str(exc)[:220]))
                else:
                    output_queue.put(("gpt_error", action, str(exc)[:400]))
        threading.Thread(target=worker, daemon=True, name="jarvis-gpt-worker").start()

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
            doc_dialog.revoke_pending()
            planner_abort_event.set()
            active_gpt = False
            gpt_status.set("GPT: disattivato manualmente")
            threading.Thread(target=service.stop, daemon=True).start()
            refresh_buttons()

    def toggle_memory() -> None:
        nonlocal durable_brain
        desired = bool(memory_enabled.get())
        previous = bool(settings["memory_enabled"])
        candidate = durable_brain
        if desired and candidate is None:
            try:
                candidate = SecondBrain()
            except (OSError, sqlite3.Error, ValueError) as exc:
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
        memory_status_refresh(
            "La memoria già salvata resta sul PC fino a cancellazione esplicita."
            if not desired else "Memoria attiva anche dopo il prossimo riavvio.")

    def clear_saved_memory() -> None:
        if not messagebox.askyesno(
            "Cancella il Second Brain",
            "Eliminare gli scambi e le operazioni archiviate localmente da Lia? "
            "Questa operazione non può essere annullata. "
            "La cronologia delle attività del motore locale resta separata.",
            parent=root,
        ):
            return
        try:
            target = durable_brain if durable_brain is not None else SecondBrain()
            target.clear_all()
            conversation_memory.clear()
            memory_status_refresh("Memoria salvata cancellata su richiesta.")
        except (OSError, sqlite3.Error, ValueError) as exc:
            memory_status.set("Cancellazione memoria non riuscita: " + str(exc)[:100])

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
        brain_controls, text="Cancella memoria salvata", command=clear_saved_memory)
    memory_clear_button.pack(side="right")
    ttk.Label(frame, textvariable=memory_status, wraplength=710).pack(
        anchor="w", pady=(0, 4))

    ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=(13, 8))
    ttk.Label(frame, text="Digita un comando locale oppure una domanda per GPT").pack(anchor="w", pady=(0, 6))
    input_row = ttk.Frame(frame)
    input_row.pack(fill="x")
    request = tk.StringVar()
    input_box = ttk.Entry(input_row, textvariable=request)
    input_box.pack(side="left", fill="x", expand=True, padx=(0, 6))
    local_button = ttk.Button(input_row, text="Esegui locale")
    local_button.pack(side="left", padx=(0, 5))
    ask_button = ttk.Button(input_row, text="Chiedi a GPT")
    ask_button.pack(side="left", padx=(0, 5))
    plan_button = ttk.Button(input_row, text="Pianifica attività")
    plan_button.pack(side="left")

    output = scrolledtext.ScrolledText(frame, height=10, wrap="word", state="disabled", font=("Consolas", 10))
    output.pack(fill="both", expand=True, pady=(12, 0))
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
        pending = doc_dialog.phase.startswith("awaiting_") and not document_busy
        can_choose = doc_dialog.phase == "awaiting_close_choice" and not document_busy
        doc_save_button.configure(state="normal" if can_choose else "disabled")
        doc_discard_button.configure(
            state="normal" if can_choose else "disabled")
        doc_cancel_button.configure(state="normal" if pending else "disabled")
        choose_save_button.configure(
            state="normal" if doc_dialog.phase == "awaiting_save_destination"
            and not document_busy else "disabled")

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
        nonlocal document_busy, last_user_for_document
        if document_busy or closing:
            announce_document("Sto già lavorando sul documento: attendi.")
            return
        document_busy = True
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

    def execute_document_choice(decision, *, path: Path | None = None) -> None:
        if decision.kind in ("save_then_close", "save_as_then_close"):
            destination = path if path is not None else (
                Path(doc_dialog.saved_path) if doc_dialog.saved_path else None)
            if destination is None:
                doc_dialog.phase = "awaiting_save_destination"
                announce_document("Dove vuoi salvare? Per esempio: "
                                  "sul desktop come storia di Venezia.")
                choose_save_button.configure(state="normal")
                return
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
        if doc_dialog.phase != "awaiting_save_destination" or document_busy:
            return
        selected = filedialog.asksaveasfilename(
            parent=root, title="Dove vuoi salvare il nuovo file?",
            defaultextension=".txt", filetypes=[("File di testo", "*.txt")])
        if selected:
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



    def change_voice_mode() -> None:
        nonlocal conversation_epoch
        selected = voice_mode.get()
        conversation_epoch += 1
        doc_dialog.revoke_pending()
        choose_save_button.configure(state="disabled")
        wake_gate.reset()
        voice.set_mode(selected)
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

    def submit_plan() -> None:
        if not gpt_enabled.get() or not active_gpt or busy_gpt or closing:
            return
        open_planner(
            root, service, engine,
            lambda: bool(gpt_enabled.get() and active_gpt and not busy_gpt and not closing),
            local_execution_lock, planner_abort_event,
        )

    def submit_local(event=None, message_override: str | None = None,
                     source_utterance: str = "") -> None:
        nonlocal busy_local, last_user_for_action
        if busy_local or closing:
            return
        message = (message_override if message_override is not None else request.get()).strip()
        if not message:
            return
        if message_override is None:
            request.set("")
        write_line("COMANDO LOCALE > " + message)
        last_user_for_action = source_utterance or message
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
        if not gpt_enabled.get() or not active_gpt or busy_gpt or closing:
            return
        message = request.get().strip()
        if not message:
            return
        if len(message) > 5000:
            messagebox.showwarning("Testo troppo lungo", "Massimo 5000 caratteri.", parent=root)
            return
        request.set("")
        write_line("DOMANDA A GPT > " + message)
        run_gpt("ask", prompt=message)

    def poll() -> None:
        nonlocal busy_local, busy_gpt, active_gpt, conversation_epoch, document_busy
        nonlocal last_user_for_action, last_user_for_document
        if closing:
            return
        try:
            while True:
                kind, *data = output_queue.get_nowait()
                if kind == "voice_status":
                    if voice_mode.get() != STANDBY:
                        mic_status.set(data[0])
                    if (dictation.enabled and
                            (str(data[0]).startswith("Microfono spento") or
                             str(data[0]).startswith("Voce non disponibile"))):
                        sync_dictation_ui(dictation.disable())
                elif kind == "voice_text":
                    spoken = str(data[0]).strip()
                    if voice_mode.get() != STANDBY and spoken and not speaker.is_audible():
                        if voice_mode.get() == GPT_CONVERSATION:
                            # Pending document decisions never go through GPT:
                            # only the owner of this selected document may close.
                            if doc_dialog.phase.startswith("awaiting_"):
                                handle_document_confirmation(spoken)
                                continue
                            if doc_dialog.phase == "executing" or document_busy:
                                write_line("Blocco note: operazione in corso, attendi.")
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
                            elif gpt_enabled.get() and active_gpt and not busy_gpt:
                                snapshot = (documents.current.ident
                                            if documents.current else None)
                                try:
                                    prompt = build_conversation_prompt(
                                        spoken, has_document=snapshot is not None,
                                        memory_context=recent_memory_for_gpt(spoken))
                                except ConversationRejected as exc:
                                    write_line("Conversazione: " + str(exc))
                                else:
                                    write_line("CONVERSAZIONE GPT > " + spoken)
                                    run_gpt("conversation", prompt=prompt,
                                            epoch=conversation_epoch,
                                            document_id=snapshot, utterance=spoken)
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
                        dictation_action = dictation_voice_action(spoken)
                        if dictation_action == "stop":
                            sync_dictation_ui(dictation.disable())
                        elif dictation_action == "start":
                            if voice_mode.get() == CONTINUOUS:
                                sync_dictation_ui(dictation.enable())
                            else:
                                sync_dictation_ui(
                                    "Per dettare in altre finestre seleziona Ascolto continuo.")
                        else:
                            write_line("VOCE (offline) > " + spoken)
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
                    remember_exchange(
                        source, result.message,
                        "action" if result.status == "completed" else "error")
                    if result.status == "completed":
                        remember_completed_action(
                            result.action, result.action.split("_")[0],
                            result.message, result.task_id)
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
                    elif result.kind == "saved_but_open":
                        if doc_dialog.phase == "executing":
                            doc_dialog.operation_completed(
                                result.document_id, succeeded=False)
                        if result.saved_path is not None:
                            doc_dialog.saved_path = str(result.saved_path)
                        choose_save_button.configure(state="disabled")
                    announce_document(result.message)
                    source = last_user_for_document or operation
                    last_user_for_document = ""
                    remember_exchange(source, result.message, "action")
                    if result.kind in ("opened", "created", "appended",
                                       "saved_and_closed", "closed_without_saving",
                                       "saved_but_open", "closed"):
                        from uuid import uuid4
                        action_name = ("notepad.open" if result.kind == "opened"
                                       else "notepad.write" if result.kind in (
                                           "created", "appended")
                                       else "notepad.save" if result.kind == "saved_but_open"
                                       else "notepad.close")
                        filename = (result.saved_path.name
                                    if result.saved_path is not None else "")
                        folder = (result.saved_path.parent.name
                                  if result.saved_path is not None else "")
                        remember_completed_action(
                            action_name, "Blocco note", result.message,
                            "jarvis:" + uuid4().hex,
                            filename=filename, folder=folder)
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
                    action, result = data
                    busy_gpt = False
                    if gpt_enabled.get():
                        if action == "ask":
                            write_line("GPT > " + result.get("text", "(nessuna risposta)"))
                            speak_result(result.get("text", ""))
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
        root.after(120, poll)

    local_button.configure(command=submit_local)
    ask_button.configure(command=submit_gpt)
    plan_button.configure(command=submit_plan)
    dictation_button.configure(command=toggle_dictation)
    choose_save_button.configure(command=choose_save_destination)
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
    ptt_button.bind("<ButtonPress-1>", ptt_press)
    ptt_button.bind("<ButtonRelease-1>", ptt_release)
    root.bind_all("<ButtonRelease-1>", ptt_release, add="+")
    root.bind("<FocusOut>", ptt_release, add="+")
    input_box.bind("<Return>", submit_local)

    def close() -> None:
        nonlocal closing
        closing = True
        planner_abort_event.set()
        doc_dialog.revoke_pending()
        dictation.disable()
        wake_gate.reset()
        voice.close()
        speaker.close()
        root.destroy()
        # Non-daemon: ensure the Node child is terminated before Python exits.
        threading.Thread(target=service.stop, daemon=False, name="jarvis-gpt-shutdown").start()

    ttk.Button(frame, text="Esci", command=close).pack(anchor="e", pady=(9, 0))
    root.protocol("WM_DELETE_WINDOW", close)
    refresh_buttons()
    input_box.focus_set()
    root.after(120, poll)
    root.after(400, refresh_voices)
    if gpt_enabled.get():
        root.after(200, lambda: run_gpt("status"))
    root.mainloop()


if __name__ == "__main__":
    main()
