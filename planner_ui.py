"""Approval-gated GPT planning window for Jarvis.

No GPT output is interpreted as Python, shell, path or executable code.
Only locally validated commands are sent to the existing LocalEngine.
"""
from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from typing import Callable
from threading import Lock

from action_planner import ApprovedPlan, PlanRejected, build_planning_prompt, parse_plan
from plan_runner import run_approved_plan


def open_planner(parent: tk.Tk, service, engine, is_available: Callable[[], bool],
                 execution_lock: Lock, abort_event: threading.Event,
                 on_approved=None, on_step=None, on_finished=None) -> None:
    previous = getattr(parent, "_jarvis_planner_window", None)
    if previous is not None and previous.winfo_exists():
        previous.lift()
        previous.focus_force()
        return

    window = tk.Toplevel(parent)
    parent._jarvis_planner_window = window
    window.title("Jarvis — Pianificazione controllata con GPT")
    window.geometry("690x560")
    window.minsize(570, 410)

    panel = ttk.Frame(window, padding=14)
    panel.pack(fill="both", expand=True)
    ttk.Label(panel, text="Pianifica con GPT", font=("Segoe UI", 14, "bold")).pack(anchor="w")
    ttk.Label(
        panel,
        text=("GPT propone soltanto. Nessuna operazione parte senza il tuo consenso. "
              "Disponibili solo comandi locali già autorizzati (massimo 5 passi)."),
        wraplength=640,
    ).pack(anchor="w", pady=(5, 10))
    ttk.Label(panel, text="Descrivi il compito:").pack(anchor="w")
    request = tk.StringVar()
    entry = ttk.Entry(panel, textvariable=request)
    entry.pack(fill="x", pady=(2, 9))

    controls = ttk.Frame(panel)
    controls.pack(fill="x")
    status = tk.StringVar(value="Pronto: descrivi il compito e premi 'Crea piano'.")
    results = scrolledtext.ScrolledText(
        panel, wrap="word", height=18, state="disabled", font=("Consolas", 10),
    )
    pending: ApprovedPlan | None = None
    busy = False
    phase = "idle"
    cancel_requested = False
    closed = False
    events: queue.Queue[tuple] = queue.Queue()
    cancel_event = threading.Event()
    tracking = None  # Durable tickets for the particular approved plan.

    def show(text: str) -> None:
        if closed:
            return
        results.configure(state="normal")
        results.insert("end", text + "\n\n")
        results.see("end")
        results.configure(state="disabled")

    def buttons() -> None:
        if closed:
            return
        enabled = is_available()
        create_button.configure(state="normal" if not busy and enabled else "disabled")
        approve_button.configure(
            state="normal" if not busy and pending is not None and enabled and not abort_event.is_set() else "disabled"
        )
        cancel_button.configure(
            state="normal" if pending is not None or (busy and not cancel_requested)
            else "disabled"
        )

    def create() -> None:
        nonlocal pending, busy, phase, cancel_requested
        if busy:
            return
        if not is_available():
            messagebox.showwarning(
                "GPT non disponibile",
                "Connetti GPT nella finestra principale di Jarvis prima di pianificare.",
                parent=window,
            )
            return
        try:
            text = request.get().strip()
            prompt = build_planning_prompt(text)
        except PlanRejected as exc:
            messagebox.showwarning("Richiesta non valida", str(exc), parent=window)
            return
        if not messagebox.askyesno(
            "Conferma GPT online",
            "Inviare a GPT online la richiesta di pianificazione? "
            "Potrai decidere separatamente se eseguire il piano.",
            parent=window, default="no",
        ):
            return
        if closed or not is_available():
            return
        # Only a new approved request can clear an earlier revocation.
        abort_event.clear()
        pending = None
        busy = True
        phase = "planning"
        cancel_requested = False
        status.set("GPT sta preparando una proposta. Nessun comando viene eseguito.")
        show("RICHIESTA > " + text)
        buttons()

        def worker() -> None:
            try:
                if abort_event.is_set():
                    events.put(("error", "Richiesta di pianificazione annullata."))
                    return
                response = service.call("ask", timeout=180, prompt=prompt)
                plan = parse_plan(response.get("text", ""))
                events.put(("planned", plan))
            except Exception as exc:
                # Never show stack traces or any sensitive protocol detail.
                events.put(("error", str(exc)[:300]))

        threading.Thread(target=worker, name="jarvis-gpt-planner", daemon=True).start()

    def approve() -> None:
        nonlocal pending, busy, phase, cancel_requested, tracking
        if busy or pending is None:
            return
        if abort_event.is_set():
            pending = None
            status.set("Piano scartato: autorizzazione revocata.")
            buttons()
            return
        if not is_available():
            pending = None
            status.set("Piano scartato: GPT disattivato o scollegato.")
            buttons()
            return
        preview = pending.preview()
        choices = "\n".join(f"{idx}. {s.command} [{s.risk}]"
                            for idx, s in enumerate(pending.steps, 1))
        if not messagebox.askyesno(
            "Autorizzazione esplicita",
            "Autorizzi Jarvis a eseguire, nell'ordine, questi comandi locali?\n\n"
            + choices + "\n\nNessun comando diverso è permesso.",
            parent=window,
        ):
            status.set("Esecuzione non autorizzata: piano mantenuto come anteprima.")
            buttons()
            return
        accepted = pending
        # Stop before executing if the project checkpoint cannot be persisted.
        try:
            tracking = on_approved(accepted) if on_approved is not None else None
        except (OSError,ValueError,RuntimeError) as exc:
            status.set("Checkpoint progetto fallito: piano non eseguito.")
            show("Nessuna azione avviata: "+str(exc)[:160])
            buttons()
            return
        pending = None
        busy = True
        phase = "running"
        cancel_requested = False
        cancel_event.clear()
        status.set("Esecuzione autorizzata. Puoi interrompere tra un passo e il successivo.")
        show("PIANO AUTORIZZATO > " + accepted.intent)
        buttons()

        def worker() -> None:
            def notify_tracked(event) -> None:
                # Worker thread: journaling uses SQLite/files only, NEVER Tk.
                try:
                    if event[0]=="step" and on_step is not None:
                        on_step(tracking,event[1],event[4],event[5],
                                event[6] if len(event)>6 else "")
                    elif event[0]=="finished" and on_finished is not None:
                        on_finished(tracking,event[1])
                except Exception:
                    # Do not allow later steps after a missing audit receipt.
                    abort_event.set()
                    events.put(("journal_error",
                                "Checkpoint del progetto non registrato: "
                                "esecuzione interrotta in sicurezza."))
                events.put(event)
            run_approved_plan(
                accepted, engine, execution_lock, cancel_event,
                abort_event, notify_tracked
            )

        threading.Thread(target=worker, name="jarvis-local-planned-task",
                         daemon=True).start()

    def cancel() -> None:
        nonlocal pending, cancel_requested
        if pending is not None:
            pending = None
            status.set("Piano scartato: nessun comando è stato eseguito.")
            show("Piano annullato prima dell'esecuzione.")
        if busy:
            cancel_requested = True
            if phase == "running":
                cancel_event.set()
                status.set("Interruzione richiesta: non partiranno ulteriori passi.")
            else:
                status.set("Proposta annullata: l'eventuale risposta GPT verrà ignorata.")
        buttons()

    create_button = ttk.Button(controls, text="Crea piano con GPT", command=create)
    create_button.pack(side="left", padx=(0, 7))
    approve_button = ttk.Button(controls, text="Approva ed esegui", command=approve)
    approve_button.pack(side="left", padx=(0, 7))
    cancel_button = ttk.Button(controls, text="Annulla", command=cancel)
    cancel_button.pack(side="left")

    ttk.Label(panel, textvariable=status, wraplength=640).pack(anchor="w", pady=(12, 5))
    results.pack(fill="both", expand=True)
    show("Esempio: 'Apri la calcolatrice, poi mostrami le informazioni di sistema'.")
    show("Il piano resta soltanto una proposta finché premi 'Approva ed esegui'.")

    def poll() -> None:
        nonlocal busy, pending, phase, cancel_requested
        if closed:
            return
        # Query Tk state on the UI thread only, never from worker threads.
        if abort_event.is_set() or not is_available():
            if pending is not None:
                pending = None
                status.set("Piano scartato perché GPT è stato disattivato.")
            if busy and phase == "running":
                cancel_event.set()
            if busy and phase == "planning":
                cancel_requested = True
        try:
            while True:
                event, *values = events.get_nowait()
                if event == "planned":
                    busy = False
                    phase = "idle"
                    pending = None if cancel_requested or not is_available() else values[0]
                    if pending is not None:
                        show(pending.preview())
                        status.set("Piano valido: controlla i passi e decidi se autorizzarlo.")
                    else:
                        status.set("Proposta scartata; nessuna azione eseguita.")
                    cancel_requested = False
                elif event == "error":
                    busy = False
                    phase = "idle"
                    if not cancel_requested:
                        show("Pianificazione respinta: " + values[0])
                        status.set("Nessun piano approvabile. Nessun comando eseguito.")
                    else:
                        status.set("Richiesta annullata.")
                    cancel_requested = False
                elif event == "step":
                    index, count, description, result, message, *receipts = values
                    show(f"PASSO {index}/{count}: {description}\n[{result}] {message}")
                elif event == "journal_error":
                    show(values[0])
                    status.set(values[0])
                elif event == "finished":
                    busy = False
                    phase = "idle"
                    status.set("Esecuzione: " + values[0] + ".")
                    show("Esecuzione: " + values[0] + ".")
                    cancel_requested = False
                buttons()
        except queue.Empty:
            pass
        window.after(120, poll)

    def close() -> None:
        nonlocal closed, pending
        closed = True
        pending = None
        abort_event.set()
        cancel_event.set()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", close)
    entry.bind("<Return>", lambda event: create())
    buttons()
    entry.focus_set()
    window.after(120, poll)
