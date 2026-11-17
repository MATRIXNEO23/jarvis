"""Tasti della barra in alto (056b): tutti con lo stesso stile, tema Lumi (azzurro su blu).

Un tasto ha il nome (con ▾ se apre una tendina) e, se serve, un ⏻ nello STESSO tasto:
clic sul nome = comando (es. apre la tendina), clic su ⏻ = accende/spegne.
⏻ acceso = azzurro, spento = arancione. Il resto della barra non possiede stato:
lo ricevono configure(text=..., power_on=...).
"""
from __future__ import annotations

import tkinter as tk

FONDO = "#072c44"
FONDO_ATTIVO = "#0c4968"
AZZURRO = "#46ccfa"
ARANCIONE = "#ff9a1f"
BORDO = "#1191c6"
GRIGIO = "#729bb3"


def colore_power(acceso: bool) -> str:
    return AZZURRO if acceso else ARANCIONE


class TastoBarra(tk.Frame):
    def __init__(self, parent, text, command=None, *, power_command=None, power=False,
                 power_on=False, bg_barra=None):
        super().__init__(parent, bg=FONDO, highlightthickness=1, highlightbackground=BORDO,
                         highlightcolor=AZZURRO, bd=0)
        self._enabled = True
        self._command = command
        self._power_command = power_command
        self.label = tk.Label(self, text=text, bg=FONDO, fg=AZZURRO, font=("Consolas", 9),
                              padx=7, pady=4, cursor="hand2")
        self.label.pack(side="left")
        self.power = None
        if power or power_command is not None:
            self.power = tk.Label(self, text="⏻", bg=FONDO, fg=colore_power(power_on),
                                  font=("Segoe UI Symbol", 10), padx=6, pady=2, cursor="hand2")
            self.power.pack(side="left")
            self.power.bind("<Button-1>", lambda _e: self._click(self._power_command))
        self.label.bind("<Button-1>", lambda _e: self._click(self._command))
        for part in (self.label, self.power):
            if part is not None:
                part.bind("<Enter>", lambda _e, p=part: p.configure(bg=FONDO_ATTIVO))
                part.bind("<Leave>", lambda _e, p=part: p.configure(bg=FONDO))

    def _click(self, callback):
        if self._enabled and callable(callback):
            callback()

    def configure(self, cnf=None, **kw):
        """text, command, state, power_on, power_command; `fg` è ignorato (stile unico)."""
        if cnf:
            kw = dict(cnf, **kw)
        if "text" in kw:
            self.label.configure(text=kw.pop("text"))
        if "command" in kw:
            self._command = kw.pop("command")
        if "power_command" in kw:
            self._power_command = kw.pop("power_command")
        if "power_color" in kw:
            # Telegram: colore di stato deciso il 15/11 (telegram_vista.stato), non il semplice on/off.
            if self.power is not None:
                self.power.configure(fg=kw["power_color"])
            self._power_color = kw.pop("power_color")
        if "power_on" in kw and self.power is not None:
            if getattr(self, "_power_color", None) is None:
                self.power.configure(fg=colore_power(bool(kw["power_on"])))
            kw.pop("power_on")
        if "state" in kw:
            self._enabled = kw.pop("state") != "disabled"
        kw.pop("fg", None)
        if kw:
            super().configure(**kw)

    config = configure

    def cget(self, key):
        if key == "text":
            return self.label.cget("text")
        if key == "fg":
            return self.label.cget("fg")
        if key == "power_on":
            return self.power is not None and str(self.power.cget("fg")) == AZZURRO
        if key == "power_color":
            return str(self.power.cget("fg")) if self.power is not None else ""
        return super().cget(key)
