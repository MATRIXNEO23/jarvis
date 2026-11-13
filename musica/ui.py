"""Configurazione dell'add-on Musica: cartelle e chiave YouTube facoltativa."""
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
        self.window.geometry("560x430")
        frame = ttk.Frame(self.window, padding=14)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Musica", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(frame, text=("«Lumi, metti …»: cerca il brano nelle cartelle (anche nelle "
                               "sottocartelle, audio e video) e lo suona in Lumi; se non c'è, "
                               "apre la ricerca su YouTube nel browser."),
                  wraplength=520).pack(anchor="w", pady=(4, 10))
        ttk.Label(frame, text="Cartelle musica").pack(anchor="w")
        row = ttk.Frame(frame)
        row.pack(fill="x")
        self.folder_list = tk.Listbox(row, height=5, activestyle="none", highlightthickness=0)
        self.folder_list.pack(side="left", fill="x", expand=True)
        for folder in service.folders():
            self.folder_list.insert("end", folder)
        side = ttk.Frame(row)
        side.pack(side="left", padx=5, anchor="n")
        ttk.Button(side, text="Aggiungi...", command=self.browse).pack(fill="x")
        ttk.Button(side, text="Rimuovi", command=self.remove).pack(fill="x", pady=(4, 0))
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
        ttk.Button(buttons, text="Elenco brani...", command=self.open_list).pack(side="left", padx=6)
        ttk.Button(buttons, text="Chiudi", command=self.window.destroy).pack(side="right")

    def open_list(self):
        from .bar import TrackList
        TrackList(self.window, self.service, lambda text: self.status.set(text))

    def browse(self):
        current = list(self.folder_list.get(0, "end"))
        chosen = filedialog.askdirectory(parent=self.window, title="Aggiungi cartella musica",
                                         initialdir=(current[-1] if current else None))
        if chosen and chosen not in current:
            self.folder_list.insert("end", chosen)
            self.status.set("Cartella aggiunta: premi Salva.")

    def remove(self):
        for index in reversed(self.folder_list.curselection()):
            self.folder_list.delete(index)
            self.status.set("Cartella tolta dall'elenco (i file restano): premi Salva.")

    def save(self):
        folder, key = list(self.folder_list.get(0, "end")), self.key.get()
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
