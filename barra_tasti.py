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


class IconaCanvas(tk.Canvas):
    """Simbolo disegnato sul Canvas (057): il glifo ⏻ del font esce come un quadratino.
    forma = "power" (arco aperto in alto + stanghetta) o "telegram" (aeroplano di carta)."""

    def __init__(self, parent, forma, colore, *, lato=22, bg=FONDO):
        super().__init__(parent, width=lato, height=lato, bg=bg, highlightthickness=0, bd=0,
                         cursor="hand2")
        self.forma, self.lato, self.colore = forma, lato, colore
        self.ridisegna()

    def colora(self, colore):
        self.colore = str(colore)
        self.ridisegna()

    def ridisegna(self):
        self.delete("all")
        c, k = self.colore, self.lato / 2.0
        if self.forma == "power":
            r = k * 0.55
            self.create_arc(k - r, k - r + 1, k + r, k + r + 1, start=120, extent=300,
                            style="arc", outline=c, width=2)
            self.create_line(k, k - r - 2, k, k + 1, fill=c, width=2, capstyle="round")
        else:
            a, b, d, e = (3, k + 1), (self.lato - 3, 4), (k - 1, self.lato - 4), (k + 2, k + 3)
            self.create_polygon(*a, *b, *d, outline=c, fill="", width=1)
            self.create_line(*a, *e, *b, fill=c, width=1)
            self.create_line(*e, k - 1, self.lato - 4, fill=c, width=1)


class TastoBarra(tk.Frame):
    def __init__(self, parent, text, command=None, *, power_command=None, power=False,
                 power_on=False, bg_barra=None, simbolo=None):
        super().__init__(parent, bg=FONDO, highlightthickness=1, highlightbackground=BORDO,
                         highlightcolor=AZZURRO, bd=0)
        self._enabled = True
        self._command = command
        self._power_command = power_command
        self._simbolo = simbolo
        self._testo = text
        if simbolo:       # Telegram: solo il simbolo, nessuna scritta; il colore è lo stato
            self.label = IconaCanvas(self, simbolo, AZZURRO, lato=24)
            self.label.pack(side="left", padx=5, pady=3)
        else:
            self.label = tk.Label(self, text=text, bg=FONDO, fg=AZZURRO, font=("Consolas", 9, "bold"),
                                  padx=7, pady=4, cursor="hand2")
            self.label.pack(side="left")
        self.power = None
        if power and not simbolo or power_command is not None:
            tk.Frame(self, bg=BORDO, width=1).pack(side="left", fill="y", pady=3)
            self.power = IconaCanvas(self, "power", colore_power(power_on), lato=22)
            self.power.pack(side="left", padx=4)
            self.power.bind("<Button-1>", lambda _e: self._click(self._power_command))
        self.label.bind("<Button-1>", lambda _e: self._click(self._command))
        for part in (self.label, self.power):
            if part is not None:
                part.bind("<Enter>", lambda _e, p=part: p.configure(bg=FONDO_ATTIVO))
                part.bind("<Leave>", lambda _e, p=part: p.configure(bg=FONDO))
        if simbolo:
            self._power_color = AZZURRO

    def _click(self, callback):
        if self._enabled and callable(callback):
            callback()

    def configure(self, cnf=None, **kw):
        """text, command, state, power_on, power_command; `fg` è ignorato (stile unico)."""
        if cnf:
            kw = dict(cnf, **kw)
        if "text" in kw:
            self._testo = kw.pop("text")
            if not self._simbolo:
                self.label.configure(text=self._testo)
        if "command" in kw:
            self._command = kw.pop("command")
        if "power_command" in kw:
            self._power_command = kw.pop("power_command")
        if "power_color" in kw:
            # Telegram: colore di stato deciso il 15/11 (telegram_vista.stato), non il semplice on/off.
            self._power_color = kw.pop("power_color")
            if self.power is not None:
                self.power.colora(self._power_color)
            elif self._simbolo:
                self.label.colora(self._power_color)
        if "power_on" in kw and self.power is not None:
            if getattr(self, "_power_color", None) is None:
                self.power.colora(colore_power(bool(kw["power_on"])))
            kw.pop("power_on")
        if "state" in kw:
            self._enabled = kw.pop("state") != "disabled"
        kw.pop("fg", None)
        if kw:
            super().configure(**kw)

    config = configure

    def invoke(self):
        """Come tk.Button.invoke: per i tasti con ⏻ è l'accensione/spegnimento."""
        self._click(self._power_command or self._command)

    def cget(self, key):
        if key == "text":
            return self._testo
        if key == "fg":
            col = getattr(self, "_power_color", None)
            return col or str(self.label.cget("fg") if not self._simbolo else self.label.colore)
        if key == "power_on":
            return self.power is not None and self.power.colore == AZZURRO
        if key == "power_color":
            return self.power.colore if self.power is not None else (
                self.label.colore if self._simbolo else "")
        return super().cget(key)
