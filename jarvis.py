"""Minimal Jarvis desktop application for Windows 10 x64.

Only the local commands advertised in the UI work at this stage.
ChatGPT sign-in and the microphone are deliberately not wired yet.
"""
from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from local_engine import LocalEngine, TaskResult
from settings import load_settings, save_settings


def main() -> None:
    settings = load_settings()
    root = tk.Tk()
    root.title("Jarvis — Motore locale (alpha)")
    root.geometry("670x540")
    root.minsize(530, 425)

    frame = ttk.Frame(root, padding=16)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Jarvis — alpha locale", font=("Segoe UI", 17, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Microfono SPENTO all'avvio. Nessun comando viene inviato a GPT.").pack(anchor="w", pady=(0, 8))

    gpt_enabled = tk.BooleanVar(value=settings["gpt_enabled"])
    status_text = tk.StringVar()

    def refresh() -> None:
        status_text.set(
            "GPT abilitato nelle preferenze; autenticazione e integrazione non ancora operative."
            if gpt_enabled.get() else "GPT disattivato manualmente."
        )

    def on_toggle() -> None:
        before = settings["gpt_enabled"]
        try:
            settings["gpt_enabled"] = bool(gpt_enabled.get())
            save_settings(settings)
        except (OSError, ValueError) as exc:
            settings["gpt_enabled"] = before
            gpt_enabled.set(before)
            messagebox.showerror("Errore salvataggio", str(exc), parent=root)
        refresh()

    ttk.Checkbutton(
        frame, text="Collegamento GPT abilitato (impostazione, non connessione)",
        variable=gpt_enabled, command=on_toggle
    ).pack(anchor="w")
    ttk.Label(frame, textvariable=status_text, wraplength=590).pack(anchor="w", fill="x", pady=(3, 8))

    ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=5)
    ttk.Label(frame, text="Scrivi un comando locale (esempio: stato sistema, mostra download, aiuto)").pack(anchor="w", pady=(5, 4))

    entry_row = ttk.Frame(frame)
    entry_row.pack(fill="x")
    request = tk.StringVar()
    input_box = ttk.Entry(entry_row, textvariable=request)
    input_box.pack(side="left", fill="x", expand=True, padx=(0, 8))
    send = ttk.Button(entry_row, text="Esegui")
    send.pack(side="right")

    output = scrolledtext.ScrolledText(frame, height=13, wrap="word", state="disabled", font=("Consolas", 10))
    output.pack(fill="both", expand=True, pady=(10, 0))
    output.configure(state="normal")
    output.insert("end", "Motore locale pronto. Scrivi 'aiuto' per l'elenco dei comandi.\n")
    output.configure(state="disabled")

    try:
        engine = LocalEngine()
    except (OSError, ValueError) as exc:
        messagebox.showerror("Motore non disponibile", str(exc), parent=root)
        root.destroy()
        return

    results: queue.Queue[TaskResult] = queue.Queue()
    busy = False

    def append(text: str) -> None:
        output.configure(state="normal")
        output.insert("end", text + "\n\n")
        output.see("end")
        output.configure(state="disabled")

    def submit(event: object = None) -> None:
        nonlocal busy
        if busy:
            return
        message = request.get().strip()
        if not message:
            return
        request.set("")
        append("> " + message)
        busy = True
        send.configure(state="disabled")
        # Worker never touches Tk: UI remains responsive during disk scans.
        def worker() -> None:
            try:
                results.put(engine.execute(message))
            except Exception as exc:
                results.put(TaskResult("unexpected", "internal", "failed", "Errore interno: " + str(exc)[:250]))
        threading.Thread(target=worker, daemon=True).start()

    def poll() -> None:
        nonlocal busy
        try:
            while True:
                result = results.get_nowait()
                append(f"[{result.status}] {result.message}")
                busy = False
                send.configure(state="normal")
        except queue.Empty:
            pass
        root.after(120, poll)

    send.configure(command=submit)
    input_box.bind("<Return>", submit)
    ttk.Button(frame, text="Esci", command=root.destroy).pack(anchor="e", pady=(10, 0))
    refresh()
    input_box.focus_set()
    root.after(120, poll)
    root.mainloop()


if __name__ == "__main__":
    main()
