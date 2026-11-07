"""Opt-in native Gemma settings dialog; no model loading or activation."""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .native_config import NativeModelConfig, PERSONALITY_LIMIT
from .native_settings import (
    EDITABLE_FIELDS, default_native_settings_path, update_native_settings,
)


class NativeSettingsWindow:
    def __init__(self, parent, *, path=None, on_save=None, get_session=None):
        self.path = path or default_native_settings_path()
        self.on_save = on_save
        self.get_session = get_session
        self.current = (NativeModelConfig.load(self.path)
                        if self.path.exists() else NativeModelConfig())
        self.window = tk.Toplevel(parent)
        self.window.title("Jarvis // Modello locale Gemma")
        self.window.geometry("590x610")
        self.window.minsize(460, 500)
        frame = ttk.Frame(self.window, padding=14)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Gemma locale - configurazione",
                  font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Salvare non avvia il modello. I nuovi valori saranno usati "
                  "dalla prossima richiesta, con ricaricamento solo se necessario.",
                  wraplength=520).pack(anchor="w", pady=(5, 12))
        self.values = {}
        labels = {
            "model": "Modello GGUF", "threads": "Thread CPU",
            "batch_threads": "Thread batch", "context_size": "Context Size",
            "max_output": "Max Output", "temperature": "Temperatura",
            "top_k": "Top-K", "top_p": "Top-P", "seed": "Seed (-1 casuale)",
        }
        for key in EDITABLE_FIELDS:
            if key == "personality":
                continue
            line = ttk.Frame(frame)
            line.pack(fill="x", pady=3)
            ttk.Label(line, text=labels[key], width=19).pack(side="left")
            variable = tk.StringVar(value=str(getattr(self.current, key)))
            self.values[key] = variable
            ttk.Entry(line, textvariable=variable).pack(side="left", fill="x", expand=True)
            if key == "model":
                ttk.Button(line, text="Sfoglia...", command=self.browse).pack(side="left", padx=5)
        ttk.Label(frame, text=f"Carattere e stile (facoltativo, max {PERSONALITY_LIMIT} caratteri)").pack(
            anchor="w", pady=(6, 2))
        self.personality = tk.Text(frame, height=3, width=1, wrap="word",
                                   bg="#031522", fg="#d7f6ff", insertbackground="#d7f6ff")
        self.personality.insert("1.0", self.current.personality)
        self.personality.pack(fill="x")
        ttk.Label(frame, text="Es. Parla come Jarvis: preciso, con ironia secca.",
                  wraplength=420).pack(anchor="w", pady=(2, 0))
        self.status = tk.StringVar(value="Modello disattivato finché non viene attivato esplicitamente.")
        ttk.Label(frame, textvariable=self.status, wraplength=520).pack(
            anchor="w", pady=10)
        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=5)
        ttk.Button(buttons, text="Salva", command=self.save).pack(side="left")
        ttk.Button(buttons, text="Ripristina campi", command=self.reset).pack(
            side="left", padx=6)
        ttk.Button(buttons, text="Chiudi", command=self.window.destroy).pack(side="right")

    def browse(self):
        selected = filedialog.askopenfilename(
            parent=self.window, title="Scegli modello GGUF",
            filetypes=[("Modello GGUF", "*.gguf")])
        if selected:
            self.values["model"].set(selected)

    def reset(self):
        defaults = NativeModelConfig()
        for key, variable in self.values.items():
            variable.set(str(getattr(defaults, key)))
        self.personality.delete("1.0", "end")
        self.status.set("Valori predefiniti mostrati; premi Salva per confermare.")

    def save(self):
        try:
            changes = {"personality": self.personality.get("1.0", "end-1c").strip()}
            for key, variable in self.values.items():
                value = variable.get().strip()
                if key in ("threads", "batch_threads", "context_size",
                           "max_output", "top_k", "seed"):
                    changes[key] = int(value)
                elif key in ("temperature", "top_p"):
                    changes[key] = float(value)
                else:
                    changes[key] = value
            revised, reload_needed = update_native_settings(self.current, changes)
            revised.save(self.path)
            self.current = revised
            if callable(self.on_save):
                self.on_save(revised, reload_needed)
            self.status.set("Impostazioni salvate. " + (
                "Ricaricamento automatico alla prossima richiesta." if reload_needed
                else "Valori usati dalla prossima generazione."))
            return True
        except (OSError, ValueError, TypeError) as exc:
            messagebox.showerror("Jarvis / Gemma",
                                 "Impostazioni non valide: " + str(exc),
                                 parent=self.window)
            return False
