"""Tk editor for explicit per-function GPT authorization.

Only listed capability IDs are editable. Unknown capabilities remain denied.
"""
import tkinter as tk
from tkinter import messagebox, ttk

from .online_permissions import OnlinePermissionPolicy, default_online_permissions_path


KNOWN_CAPABILITIES = (
    ("chat.conversation", "Conversazione con GPT"),
    ("web.search", "Ricerca Web assistita"),
    ("web.navigate", "Navigazione Web assistita"),
    ("files.search", "Ricerca file assistita"),
    ("telegram.compose", "Preparazione messaggi Telegram"),
)
MODE_OPTIONS = (
    ("Mai (solo locale)", "never"),
    ("Chiedi autorizzazione", "ask"),
    ("Autorizzato per questa funzione", "allowed"),
)
LABEL_TO_MODE = dict(MODE_OPTIONS)
MODE_TO_LABEL = {value: label for label, value in MODE_OPTIONS}


class OnlinePermissionsWindow:
    def __init__(self, parent, *, path=None):
        self.path = path or default_online_permissions_path()
        self.policy = OnlinePermissionPolicy.load(self.path)
        self.window = tk.Toplevel(parent)
        self.window.title("Jarvis - Autorizzazioni GPT per funzione")
        self.window.geometry("590x410")
        self.window.transient(parent)
        frame = ttk.Frame(self.window, padding=14)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="GPT online: autorizzazioni per singola funzione",
                  font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))
        ttk.Label(frame, text=(
            "Predefinito: Mai. Le modifiche non attivano GPT da sole. "
            "Le azioni sensibili richiedono conferme separate."),
            wraplength=530).pack(anchor="w", pady=(0, 12))
        self.variables = {}
        for capability, label in KNOWN_CAPABILITIES:
            line = ttk.Frame(frame)
            line.pack(fill="x", pady=5)
            ttk.Label(line, text=label, width=31).pack(side="left")
            variable = tk.StringVar(value=MODE_TO_LABEL[self.policy.mode(capability)])
            ttk.Combobox(line, textvariable=variable, state="readonly",
                         values=list(LABEL_TO_MODE), width=28).pack(side="left", fill="x")
            self.variables[capability] = variable
        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=16)
        ttk.Button(actions, text="Salva", command=self.save).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Ripristina tutto su Mai",
                   command=self.reset).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Chiudi", command=self.window.destroy).pack(side="right")

    def save(self):
        try:
            new = OnlinePermissionPolicy(dict(self.policy.rules))
            for capability, variable in self.variables.items():
                new.set_mode(capability, LABEL_TO_MODE[variable.get()])
            new.save(self.path)
            self.policy = new
        except (OSError, ValueError, KeyError) as exc:
            messagebox.showerror("Permessi GPT", str(exc), parent=self.window)
            return
        messagebox.showinfo("Permessi GPT", "Impostazioni salvate.", parent=self.window)

    def reset(self):
        for variable in self.variables.values():
            variable.set(MODE_TO_LABEL["never"])
        self.save()
