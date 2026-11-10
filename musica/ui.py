"""Configurazione dell'add-on Musica: cartella e chiave YouTube facoltativa."""
from __future__ import annotations

import threading
import tkinter as tk
from tkinter import filedialog, ttk


class MusicSettings:
    def __init__(self, parent, service, on_change=None):
        self.service = service
        self.on_change = on_change or (lambda: None)
        self.window = tk.Toplevel(parent)
        self.window.title("Lumi // Musica")
        self.window.geometry("560x330")
        frame = ttk.Frame(self.window, padding=14)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Musica", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(frame, text=("«Lumi, metti …»: cerca il brano nella cartella (anche nelle "
                               "sottocartelle, MP3/WAV/WMA/M4A) e lo suona in Lumi; se non c'è, "
                               "apre la ricerca su YouTube nel browser."),
                  wraplength=520).pack(anchor="w", pady=(4, 10))
        row = ttk.Frame(frame)
        row.pack(fill="x")
        ttk.Label(row, text="Cartella musica", width=16).pack(side="left")
        self.folder = tk.StringVar(value=service.settings.get("folder", ""))
        ttk.Entry(row, textvariable=self.folder).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Sfoglia...", command=self.browse).pack(side="left", padx=5)
        key_row = ttk.Frame(frame)
        key_row.pack(fill="x", pady=(10, 0))
        ttk.Label(key_row, text="Chiave API YouTube", width=16).pack(side="left")
        self.key = tk.StringVar(value=service.api_key())
        ttk.Entry(key_row, textvariable=self.key, show="•").pack(side="left", fill="x", expand=True)
        ttk.Label(frame, text=("Facoltativa (YouTube Data API v3, gratuita: circa 100 ricerche al "
                               "giorno). Con la chiave si apre subito il primo video invece dei "
                               "risultati. Salvata cifrata solo su questo PC."),
                  wraplength=520).pack(anchor="w", pady=(4, 10))
        self.status = tk.StringVar(value=f"Brani trovati: {len(service.tracks())}")
        ttk.Label(frame, textvariable=self.status, wraplength=520).pack(anchor="w")
        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", side="bottom")
        ttk.Button(buttons, text="Salva", command=self.save).pack(side="left")
        ttk.Button(buttons, text="Chiudi", command=self.window.destroy).pack(side="right")

    def browse(self):
        chosen = filedialog.askdirectory(parent=self.window, title="Cartella musica",
                                         initialdir=self.folder.get() or None)
        if chosen:
            self.folder.set(chosen)

    def save(self):
        folder, key = self.folder.get(), self.key.get()
        self.status.set("Salvo e cerco i brani...")

        def work():
            try:
                count = self.service.configure(folder, key)
                text = f"Salvato. Brani trovati: {count}."
            except (OSError, ValueError) as exc:
                text = "Non salvato: " + str(exc)[:120]
            try:
                self.window.after(0, lambda: (self.status.set(text), self.on_change()))
            except tk.TclError:
                pass
        threading.Thread(target=work, daemon=True, name="lumi-musica-scan").start()
