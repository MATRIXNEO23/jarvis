"""Jarvis configuration UI — minimal first version for Windows 10 x64.

This first version stores preferences. It does not claim a live ChatGPT
connection until the official Sign in with ChatGPT bridge is integrated.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from settings import load_settings, save_settings


def main() -> None:
    settings = load_settings()
    root = tk.Tk()
    root.title("Jarvis — Impostazioni")
    root.geometry("525x285")
    root.minsize(430, 260)

    frame = ttk.Frame(root, padding=18)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Jarvis", font=("Segoe UI", 17, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Windows 10 — modalita leggera", padding=(0, 4, 0, 12)).pack(anchor="w")

    gpt_enabled = tk.BooleanVar(value=settings["gpt_enabled"])
    status_text = tk.StringVar()

    def refresh() -> None:
        if gpt_enabled.get():
            status_text.set(
                "GPT abilitato (predefinito). Connessione ufficiale non ancora installata."
            )
        else:
            status_text.set("GPT disattivato manualmente.")

    def on_toggle() -> None:
        previous = settings["gpt_enabled"]
        desired = bool(gpt_enabled.get())
        try:
            settings["gpt_enabled"] = desired
            save_settings(settings)
        except (OSError, ValueError) as exc:
            settings["gpt_enabled"] = previous
            gpt_enabled.set(previous)
            messagebox.showerror("Impossibile salvare", str(exc), parent=root)
        refresh()

    ttk.Checkbutton(
        frame,
        text="Abilita collegamento a ChatGPT (interruttore manuale)",
        variable=gpt_enabled,
        command=on_toggle,
    ).pack(anchor="w", pady=4)

    ttk.Label(
        frame,
        textvariable=status_text,
        wraplength=470,
        padding=(2, 4, 0, 12),
    ).pack(anchor="w", fill="x")

    ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=5)
    ttk.Label(frame, text="Microfono: STANDBY (spento all'avvio)").pack(anchor="w", pady=4)
    ttk.Label(
        frame,
        text="L'attivazione vocale e il collegamento reale con ChatGPT "
             "saranno aggiunti nei prossimi moduli. Nessun processo AI in background "
             "e nessuna API a consumo vengono avviati da questa versione.",
        wraplength=470,
    ).pack(anchor="w", fill="x")

    ttk.Button(frame, text="Chiudi", command=root.destroy).pack(side="bottom", anchor="e", pady=(12, 0))
    refresh()
    root.mainloop()


if __name__ == "__main__":
    main()
