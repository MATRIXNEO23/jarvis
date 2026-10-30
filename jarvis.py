"""Jarvis alpha — tested local commands + optional official ChatGPT connector.

No speech recognition yet: the microphone always starts disabled.
GPT is enabled in preferences by default, but requires installing the official
SDK and explicit sign-in in the browser before it can answer.
"""
from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import webbrowser

from gpt_client import GPTClient, GPTUnavailable
from local_engine import LocalEngine, TaskResult
from settings import load_settings, save_settings


def main() -> None:
    settings = load_settings()
    root = tk.Tk()
    root.title("Jarvis — alpha")
    root.geometry("780x640")
    root.minsize(630, 500)

    frame = ttk.Frame(root, padding=15)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Jarvis", font=("Segoe UI", 17, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Microfono: SPENTO all'avvio (voce non ancora installata)").pack(anchor="w", pady=(2, 12))

    service = GPTClient()
    output_queue: queue.Queue[tuple] = queue.Queue()
    gpt_enabled = tk.BooleanVar(value=settings["gpt_enabled"])
    gpt_status = tk.StringVar(value="GPT: inizializzazione" if gpt_enabled.get() else "GPT: disattivato")
    busy_local = False
    busy_gpt = False
    closing = False
    active_gpt = False

    def write_line(text: str) -> None:
        output.configure(state="normal")
        output.insert("end", text + "\n\n")
        output.see("end")
        output.configure(state="disabled")

    def display_status(state: dict) -> None:
        nonlocal active_gpt
        connected = state.get("status") == "connected" and state.get("sharing") is True
        active_gpt = connected
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
                result = service.call(action, timeout=timeout, **params)
                output_queue.put(("gpt_ok", action, result))
            except Exception as exc:
                output_queue.put(("gpt_error", action, str(exc)[:400]))
        threading.Thread(target=worker, daemon=True, name="jarvis-gpt-worker").start()

    def toggle_gpt() -> None:
        nonlocal active_gpt
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
    ask_button.pack(side="left")

    output = scrolledtext.ScrolledText(frame, height=15, wrap="word", state="disabled", font=("Consolas", 10))
    output.pack(fill="both", expand=True, pady=(12, 0))
    write_line("Jarvis locale pronto. Scrivi 'aiuto' per vedere i comandi disponibili.")

    try:
        engine = LocalEngine()
    except (OSError, ValueError) as exc:
        messagebox.showerror("Motore locale non disponibile", str(exc), parent=root)
        root.destroy()
        return

    def submit_local(event=None) -> None:
        nonlocal busy_local
        if busy_local or closing:
            return
        message = request.get().strip()
        if not message:
            return
        request.set("")
        write_line("COMANDO LOCALE > " + message)
        busy_local = True
        refresh_buttons()

        def worker() -> None:
            try:
                output_queue.put(("local", engine.execute(message)))
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
                if kind == "local":
                    result = data[0]
                    busy_local = False
                    write_line(f"[{result.status}] {result.message}")
                elif kind == "gpt_ok":
                    action, result = data
                    busy_gpt = False
                    if gpt_enabled.get():
                        if action == "ask":
                            write_line("GPT > " + result.get("text", "(nessuna risposta)"))
                            gpt_status.set("GPT: connesso")
                            active_gpt = True
                        elif action == "disconnect":
                            display_status({"status": "disconnected", "sharing": False})
                            write_line("Account scollegato da Jarvis.")
                        else:
                            display_status(result)
                    else:
                        active_gpt = False
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
                    if gpt_enabled.get():
                        gpt_status.set("GPT: modulo non pronto.")
                        write_line("GPT: " + str(event.get("error", "errore")))
                elif event.get("event") == "stopped" and gpt_enabled.get() and not busy_gpt:
                    active_gpt = False
                    gpt_status.set("GPT: servizio arrestato.")
                refresh_buttons()
        except queue.Empty:
            pass
        root.after(120, poll)

    local_button.configure(command=submit_local)
    ask_button.configure(command=submit_gpt)
    input_box.bind("<Return>", submit_local)

    def close() -> None:
        nonlocal closing
        closing = True
        root.destroy()
        # Non-daemon: ensure the Node child is terminated before Python exits.
        threading.Thread(target=service.stop, daemon=False, name="jarvis-gpt-shutdown").start()

    ttk.Button(frame, text="Esci", command=close).pack(anchor="e", pady=(9, 0))
    root.protocol("WM_DELETE_WINDOW", close)
    refresh_buttons()
    input_box.focus_set()
    root.after(120, poll)
    if gpt_enabled.get():
        root.after(200, lambda: run_gpt("status"))
    root.mainloop()


if __name__ == "__main__":
    main()
