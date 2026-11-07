"""Optional settings dialog for idle memory processing; does not start a worker."""
from dataclasses import replace
import tkinter as tk
from tkinter import messagebox, ttk

from .memory_preferences import MemoryPreferences, default_memory_preferences_path


class MemoryPreferencesWindow:
    def __init__(self, parent, *, path=None):
        self.path = path or default_memory_preferences_path()
        self.current = MemoryPreferences.load(self.path)
        self.window = tk.Toplevel(parent)
        self.window.title("Jarvis // Memoria e inattivita")
        self.window.geometry("590x490")
        self.window.minsize(480, 440)
        frame = ttk.Frame(self.window, padding=14)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Memoria locale - impostazioni",
                  font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Contesto Gemma: limite in caratteri, spazi inclusi. "
                  "La sintesi automatica non è ancora collegata.",
                  wraplength=530).pack(anchor="w", pady=8)
        fields = (
            ("idle_seconds", "Inattivita prima sintesi (secondi)"),
            ("recent_messages", "Ultimi messaggi conservati"),
            ("summarize_every", "Sintesi ogni N messaggi"),
            ("summary_max_tokens", "Limite riassunto (non collegato)"),
            ("prompt_max_tokens", "Caratteri massimi nel prompt"),
            ("max_background_jobs", "Lavori simultanei (max 1)"),
        )
        self.values = {}
        for key, title in fields:
            line = ttk.Frame(frame)
            line.pack(fill="x", pady=3)
            ttk.Label(line, text=title, width=38).pack(side="left")
            var = tk.StringVar(value=str(getattr(self.current, key)))
            self.values[key] = var
            ttk.Entry(line, textvariable=var, width=9).pack(side="right")
        for key, title in (
            ("conversation_priority", "Priorita assoluta alla conversazione"),
            ("pause_on_heavy_load", "Sospendi con carico elevato"),
            ("background_summaries", "Abilita sintesi in inattivita"),
        ):
            var = tk.BooleanVar(value=getattr(self.current, key))
            self.values[key] = var
            ttk.Checkbutton(frame, text=title, variable=var).pack(anchor="w", pady=3)
        self.status = tk.StringVar(value="Le modifiche non avviano alcuna sintesi.")
        ttk.Label(frame, textvariable=self.status, wraplength=520).pack(
            anchor="w", pady=8)
        buttons = ttk.Frame(frame)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Salva", command=self.save).pack(side="left")
        ttk.Button(buttons, text="Valori iniziali",
                   command=self.reset).pack(side="left", padx=6)
        ttk.Button(buttons, text="Chiudi",
                   command=self.window.destroy).pack(side="right")

    def reset(self):
        defaults = MemoryPreferences()
        for key, variable in self.values.items():
            variable.set(getattr(defaults, key))
        self.status.set("Premi Salva per confermare i valori iniziali.")

    def save(self):
        try:
            values = {}
            for key, variable in self.values.items():
                value = variable.get()
                values[key] = value if isinstance(variable, tk.BooleanVar) else int(value)
            revised = replace(self.current, **values).validate()
            revised.save(self.path)
            self.current = revised
            self.status.set("Impostazioni salvate; nessuna build necessaria.")
        except (ValueError, TypeError, OSError) as exc:
            messagebox.showerror("Jarvis / Memoria", str(exc),
                                 parent=self.window)
