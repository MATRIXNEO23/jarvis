"""Jarvis alpha — local commands, optional GPT and opt-in offline voice.

The microphone always starts OFF; only a user action opens an audio stream.
The optional speech model is never loaded at application startup.
GPT requires the official SDK and an explicit sign-in.
"""
from __future__ import annotations

import queue
from desktop_dictation import DesktopDictation, dictation_voice_action
from conversation_router import (
    ConversationRejected, build_conversation_prompt, parse_conversation_intent,
)
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import webbrowser

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

    def write_line(text: str) -> None:
        output.configure(state="normal")
        output.insert("end", text + "\n\n")
        output.see("end")
        output.configure(state="disabled")

    def display_status(state: dict) -> None:
        nonlocal active_gpt
        connected = state.get("status") == "connected" and state.get("sharing") is True
        active_gpt = connected
        if not connected:
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
        elif action == "ask":
            gpt_status.set("GPT: elaborazione richiesta...")
        elif action == "disconnect":
            gpt_status.set("GPT: scollegamento...")
        else:
            gpt_status.set("GPT: verifica connessione...")

        def worker() -> None:
            try:
                timeout = 600 if action == "sign_in" else 180 if action == "ask" else 40
                sdk_action = "ask" if action == "conversation" else action
                epoch = params.pop("epoch", None) if action == "conversation" else None
                result = service.call(sdk_action, timeout=timeout, **params)
                if action == "conversation":
                    output_queue.put(("conversation_ok", epoch, result))
                else:
                    output_queue.put(("gpt_ok", action, result))
            except Exception as exc:
                if action == "conversation":
                    output_queue.put(("conversation_error", str(exc)[:220]))
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
            planner_abort_event.set()
            active_gpt = False
            gpt_status.set("GPT: disattivato manualmente")
            threading.Thread(target=service.stop, daemon=True).start()
            refresh_buttons()

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

    def submit_local(event=None, message_override: str | None = None) -> None:
        nonlocal busy_local
        if busy_local or closing:
            return
        message = (message_override if message_override is not None else request.get()).strip()
        if not message:
            return
        if message_override is None:
            request.set("")
        write_line("COMANDO LOCALE > " + message)
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
        nonlocal busy_local, busy_gpt, active_gpt
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
                            # Explicit opt-in conversation: each recognized phrase
                            # may go to GPT; safe known local tools remain offline.
                            command = speech_to_local_command(spoken)
                            if command:
                                if not busy_local:
                                    submit_local(message_override=command)
                                else:
                                    write_line("Motore locale occupato: riprova.")
                            elif gpt_enabled.get() and active_gpt and not busy_gpt:
                                try:
                                    prompt = build_conversation_prompt(spoken)
                                except ConversationRejected as exc:
                                    write_line("Conversazione: " + str(exc))
                                else:
                                    write_line("CONVERSAZIONE GPT > " + spoken)
                                    run_gpt("conversation", prompt=prompt,
                                            epoch=conversation_epoch)
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
                                submit_local(message_override=command)
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
                    if result.status == "completed":
                        speak_result(result.message)
                elif kind == "conversation_ok":
                    busy_gpt = False
                    epoch, result = data
                    if (epoch == conversation_epoch and
                            voice_mode.get() == GPT_CONVERSATION and
                            gpt_enabled.get() and active_gpt):
                        try:
                            intent = parse_conversation_intent(result.get("text", ""))
                        except ConversationRejected as exc:
                            write_line("GPT: impossibile interpretare la risposta: " + str(exc))
                            speak_result("Non ho capito con sicurezza. Puoi ripetere?")
                        else:
                            if intent.kind in ("chat", "clarify"):
                                write_line("JARVIS > " + intent.reply)
                                speak_result(intent.reply)
                            elif intent.kind == "tool":
                                if intent.plan is not None and not busy_local:
                                    command = intent.plan.steps[0].command
                                    submit_local(message_override=command)
                                else:
                                    speak_result("Sono occupato, riprova.")
                            elif intent.kind == "compose_document":
                                # The safe document writer is not integrated yet.
                                # Never pretend that text has been written.
                                write_line("BOZZA GPT (non salvata né inserita) > " + intent.content)
                                speak_result(
                                    "Ho preparato il testo. La scrittura automatica nei documenti "
                                    "non è ancora attiva in questa versione sperimentale.")
                            elif intent.kind == "close_document":
                                speak_result(
                                    "Non posso ancora chiudere il documento e gestire "
                                    "il salvataggio automaticamente. Non lo chiuderò.")
                elif kind == "conversation_error":
                    busy_gpt = False
                    write_line("Conversazione GPT: " + data[0])
                    if voice_mode.get() == GPT_CONVERSATION:
                        speak_result("GPT non è disponibile. Puoi riprovare.")
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
                    planner_abort_event.set()
                    if gpt_enabled.get():
                        gpt_status.set("GPT: modulo non pronto.")
                        write_line("GPT: " + str(event.get("error", "errore")))
                elif event.get("event") == "stopped" and gpt_enabled.get() and not busy_gpt:
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
