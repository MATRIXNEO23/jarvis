"""F5.2 experimental multi-model settings panel.

This is an opt-in, side-effect-free editor. Values remain in this window only;
it neither persists settings nor switches the live Lumi model. The runtime
configuration and the old Gemma settings dialog remain authoritative.
"""
from dataclasses import replace
import tkinter as tk
from tkinter import ttk

from .model_profiles_f5 import ProfileError, default_profiles


_FIELDS = (
    ("context_size", "Context Size"),
    ("max_output", "Max Output"),
    ("threads", "Thread CPU"),
    ("blas_threads", "Thread BLAS"),
    ("temperature", "Temperature"),
    ("top_p", "Top P"),
    ("seed", "Seed (-1 casuale)"),
)
_INTS = frozenset(("context_size", "max_output", "threads", "blas_threads", "seed"))


def apply_profile_draft(current, fields):
    """Validate a complete draft without side effects or partial mutation."""
    changes = {}
    for key, _ in _FIELDS:
        raw = fields[key]
        if type(raw) is not str or not raw.strip():
            raise ProfileError("Campo mancante: " + key)
        try:
            changes[key] = int(raw.strip()) if key in _INTS else float(raw.strip())
        except (ValueError, OverflowError):
            raise ProfileError("Valore non valido: " + key) from None
    return replace(current, **changes)


class MultiModelSettingsF5Window:
    """Preview editor, not yet a model picker connected to conversation."""

    def __init__(self, parent):
        self.profiles = {p.profile_id: p for p in default_profiles()}
        self.active_id = "gemma-default"
        self.window = tk.Toplevel(parent)
        self.window.title("Lumi // Multimodello F5 (anteprima)")
        self.window.geometry("590x490")
        self.window.minsize(480, 420)
        host = ttk.Frame(self.window, padding=14)
        host.pack(fill="both", expand=True)
        ttk.Label(host, text="Modelli locali — anteprima F5",
                  font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(host, text="Questa finestra non cambia il modello della chat, "
                  "non avvia KoboldCpp e non modifica le impostazioni Gemma esistenti.",
                  wraplength=530).pack(anchor="w", pady=(5, 10))
        row = ttk.Frame(host)
        row.pack(fill="x", pady=(0, 8))
        ttk.Label(row, text="Profilo", width=18).pack(side="left")
        self.selected = tk.StringVar(value=self.active_id)
        self.selector = ttk.Combobox(row, textvariable=self.selected,
                                    state="readonly", width=29,
                                    values=tuple(self.profiles))
        self.selector.pack(side="left", fill="x", expand=True)
        self.selector.bind("<<ComboboxSelected>>", self._select)
        self.detail = tk.StringVar()
        ttk.Label(host, textvariable=self.detail, wraplength=530).pack(anchor="w", pady=(0, 8))
        self.values = {}
        for key, label in _FIELDS:
            row = ttk.Frame(host)
            row.pack(fill="x", pady=3)
            ttk.Label(row, text=label, width=18).pack(side="left")
            variable = tk.StringVar()
            self.values[key] = variable
            ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True)
        self.status = tk.StringVar(value="Anteprima: nessun modello caricato o selezionato per Lumi.")
        ttk.Label(host, textvariable=self.status, wraplength=530).pack(anchor="w", pady=(10, 7))
        buttons = ttk.Frame(host)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Valida bozza", command=self.validate).pack(side="left")
        ttk.Button(buttons, text="Ripristina bozza", command=self.reset).pack(side="left", padx=6)
        ttk.Button(buttons, text="Chiudi", command=self.window.destroy).pack(side="right")
        self._fill()

    def _fill(self):
        p = self.profiles[self.active_id]
        self.selected.set(self.active_id)
        self.detail.set("Famiglia: " + p.family + " | Backend previsto: " + p.backend
                        + " | Non verificato né attivato")
        for key, _ in _FIELDS:
            self.values[key].set(str(getattr(p, key)))

    def _select(self, unused_event=None):
        # Keep the validated, in-memory draft for each profile. Unsaved edits
        # are discarded, not silently applied to another model.
        selected = self.selected.get()
        if selected not in self.profiles:
            self.selected.set(self.active_id)
            return
        self.active_id = selected
        self._fill()
        self.status.set("Profilo visualizzato; nessuna modifica al runtime Lumi.")

    def validate(self):
        try:
            current = self.profiles[self.active_id]
            revised = apply_profile_draft(current, {
                key: variable.get() for key, variable in self.values.items()
            })
        except (ProfileError, KeyError, TypeError) as exc:
            self.status.set("Bozza non valida: " + str(exc))
            return False
        self.profiles[self.active_id] = revised
        self.status.set("Bozza valida in memoria. Non salvata su disco; "
                        "non applicata al motore della chat.")
        return True

    def reset(self):
        self.profiles[self.active_id] = next(
            p for p in default_profiles() if p.profile_id == self.active_id)
        self._fill()
        self.status.set("Bozza ripristinata. Impostazioni Lumi inalterate.")
