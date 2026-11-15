"""Riga di stato sotto la chat e stop immediato (passo 3, 15/11).

Cinque stati con colore (decisione 15/11):
  attesa     grigio    microfono acceso, aspetta «Lumi» (o microfono spento)
  ascolto    azzurro   dopo «Lumi», o modalità ascolto continuo
  elabora    giallo    modello locale o GPT al lavoro
  parla      verde     Lumi sta parlando
  occupato   rosso     un comando o un documento è in corso: i nuovi comandi non passano

«Lumi, fermati» («fermo», «ferma tutto», «basta») e il pulsante «■ Ferma» chiamano la
stessa funzione di jarvis.py (ferma voce, risposta del modello e GPT in attesa). La frase
vale solo mentre Lumi parla o elabora: altrimenti passa agli altri comandi (es. «fermati»
come «no» a una domanda in sospeso). «stop/pausa/play» restano dei lettori audio-video
(decisione 15/11); «annulla» resta com'era.
Limite: mentre Lumi parla il microfono ignora l'audio (niente eco della sua voce), quindi
in quel momento funziona il pulsante, non la voce.
"""
from __future__ import annotations

import re
import time
import tkinter as tk

STATI = {
    "attesa": ("In attesa di «Lumi»", "#7f95a3"),
    "spento": ("Microfono spento", "#7f95a3"),
    "ascolto": ("In ascolto", "#46ccfa"),
    "elabora": ("Sto elaborando…", "#f2c94c"),
    "parla": ("Sto parlando", "#5fd38d"),
    "occupato": ("Occupato: aspetta", "#ff6b6b"),
}

_STOP = re.compile(
    r"^\s*(?:(?:(?:ehi|hey|ok)\s+)?lumi[\s,!.:]*)?(?:fermati|fermo|ferma\s+tutto|basta)[\s.!?]*$",
    re.IGNORECASE)


_MODEL_STOP = [0.0]


def mark_model_stop() -> None:
    _MODEL_STOP[0] = time.monotonic()


def consume_model_stop(window: float = 60.0) -> bool:
    """True una volta sola dopo un «fermati» che ha interrotto il modello."""
    stopped, _MODEL_STOP[0] = _MODEL_STOP[0], 0.0
    return bool(stopped) and time.monotonic() - stopped < window


def is_stop(text: str) -> bool:
    """La voce arriva già senza «Lumi» (lo toglie il riconoscitore); niente «stop»."""
    return isinstance(text, str) and len(text) < 60 and bool(_STOP.match(text))


def stato(*, speaking: bool, busy: bool, thinking: bool, mic_on: bool,
          always_listening: bool, armed: bool) -> str:
    if speaking:
        return "parla"
    if busy:
        return "occupato"
    if thinking:
        return "elabora"
    if not mic_on:
        return "spento"
    if always_listening or armed:
        return "ascolto"
    return "attesa"


class RigaStato:
    """Pallino + testo + pulsante «■ Ferma» (attivo solo quando c'è qualcosa da fermare)."""

    def __init__(self, parent, *, read_state, on_stop, bg: str, period_ms: int = 250):
        self.read_state = read_state
        self.period_ms = period_ms
        self.current = None
        self.frame = tk.Frame(parent, bg=bg)
        self.dot = tk.Label(self.frame, text="●", bg=bg, font=("Segoe UI", 10))
        self.dot.pack(side="left", padx=(2, 4))
        self.label = tk.Label(self.frame, bg=bg, font=("Segoe UI", 9), anchor="w")
        self.label.pack(side="left", fill="x", expand=True)
        self.button = tk.Button(
            self.frame, text="■ Ferma", command=on_stop, font=("Segoe UI", 8),
            bg="#3a1414", fg="#ffb3b3", activebackground="#6b1f1f",
            activeforeground="white", relief="flat", bd=0, padx=8, cursor="hand2")
        self.button.pack(side="right")
        self.aggiorna()

    def aggiorna(self) -> None:
        try:
            key = self.read_state()
        except Exception:          # lo stato non deve mai fermare la finestra
            key = self.current or "attesa"
        if key != self.current:
            self.current = key
            text, colour = STATI.get(key, STATI["attesa"])
            self.dot.configure(fg=colour)
            self.label.configure(text=text, fg=colour)
            active = key in ("parla", "occupato", "elabora")
            self.button.configure(state="normal" if active else "disabled")
        try:
            self.frame.after(self.period_ms, self.aggiorna)
        except tk.TclError:
            pass
