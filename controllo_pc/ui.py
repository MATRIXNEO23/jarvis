"""Configurazione del Controllo PC: nomi tuoi per le finestre, conferme, mouse."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class ControlSettings:
    def __init__(self, parent, service, on_change=None):
        self.service = service
        self.on_change = on_change or (lambda: None)
        self.window = tk.Toplevel(parent)
        self.window.title("Lumi // Controllo PC")
        self.window.geometry("640x520")
        frame = ttk.Frame(self.window, padding=12)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Nomi tuoi per le finestre", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(frame, wraplength=600, text=(
            "Scrivi accanto a una finestra aperta il nome con cui vuoi chiamarla "
            "(es. «lavoro»), poi Salva: «passa a lavoro». Il nome vale per quel programma "
            "anche le prossime volte. A voce: «chiama questa finestra lavoro».")).pack(anchor="w", pady=(2, 6))
        holder = ttk.Frame(frame)
        holder.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(holder, highlightthickness=0, height=230)
        scroll = ttk.Scrollbar(holder, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.rows = ttk.Frame(self.canvas)
        self.canvas.create_window(0, 0, window=self.rows, anchor="nw")
        self.rows.bind("<Configure>", lambda _e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(6, 10))
        ttk.Button(buttons, text="Salva nomi", command=self.save_names).pack(side="left")
        ttk.Button(buttons, text="Aggiorna elenco", command=self.fill).pack(side="left", padx=6)

        ttk.Label(frame, text="Conferme e mouse", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="Chiedi conferma le prime").pack(side="left")
        self.times = tk.IntVar(value=service.settings["confirm_times"])
        ttk.Spinbox(row, from_=0, to=10, width=4, textvariable=self.times).pack(side="left", padx=4)
        ttk.Label(row, text="volte, poi ricorda (le azioni delicate chiedono sempre).").pack(side="left")
        self.visible = tk.BooleanVar(value=service.settings["visible_mouse"])
        ttk.Checkbutton(frame, text="Mostra il movimento del mouse prima del clic",
                        variable=self.visible).pack(anchor="w")
        bottom = ttk.Frame(frame)
        bottom.pack(fill="x", pady=(8, 0))
        ttk.Button(bottom, text="Salva", command=self.save_options).pack(side="left")
        ttk.Button(bottom, text="Dimentica azioni ricordate",
                   command=lambda: self.status.set(service.forget_approvals())).pack(side="left", padx=6)
        ttk.Button(bottom, text="Chiudi", command=self.window.destroy).pack(side="right")
        self.status = tk.StringVar()
        ttk.Label(frame, textvariable=self.status, wraplength=600).pack(anchor="w", pady=(6, 0))
        self.entries = []
        self.fill()

    def fill(self):
        for child in self.rows.winfo_children():
            child.destroy()
        self.entries = []
        items = self.service.windows()
        if not items:
            ttk.Label(self.rows, text="Nessuna finestra aperta oltre a Lumi.").grid(row=0, column=0)
            return
        ttk.Label(self.rows, text="Finestra aperta", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Label(self.rows, text="Il mio nome", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=1, sticky="w")
        for index, window in enumerate(items[:30], start=1):
            label = window["title"][:55] + f"  ({window['process']})"
            ttk.Label(self.rows, text=label).grid(row=index, column=0, sticky="w", padx=(0, 8))
            value = tk.StringVar(value=self.service.nickname_of(window))
            ttk.Entry(self.rows, textvariable=value, width=20).grid(row=index, column=1, sticky="w")
            self.entries.append((window, value, value.get()))

    def save_names(self):
        messages = []
        for window, value, before in self.entries:
            name = value.get().strip()
            if name == before:
                continue
            if before:
                self.service.remove_nickname(before)
            if name:
                messages.append(self.service.set_nickname(name, window))
        if not messages:
            try:
                self.service.save()
            except OSError as exc:
                self.status.set("Non salvato: " + str(exc)[:80])
                return
        self.status.set(" ".join(messages)[:300] or "Salvato.")
        self.on_change()
        self.fill()

    def save_options(self):
        try:
            self.service.settings["confirm_times"] = max(0, min(int(self.times.get()), 10))
        except (tk.TclError, ValueError):
            self.status.set("Numero di conferme non valido.")
            return
        self.service.settings["visible_mouse"] = bool(self.visible.get())
        try:
            self.service.save()
        except OSError as exc:
            self.status.set("Non salvato: " + str(exc)[:80])
            return
        self.status.set("Salvato.")
