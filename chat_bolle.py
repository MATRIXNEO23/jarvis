"""Bolle della chat (passo 2c, opzione B, 15/11).

Ogni messaggio tuo o di Lumi è un blocco a sé dentro la console esistente:
- i tuoi messaggi rientrati a destra, quelli di Lumi a sinistra, con sfondo;
- sotto ogni risposta di Lumi: «copia», «leggi», «rigenera» (rigenera rimanda
  la tua domanda precedente, se c'è);
- restano disegnati gli ultimi LIMITE messaggi; i più vecchi spariscono solo
  dalla vista (l'archivio della chat non viene toccato).
"""
from __future__ import annotations

import tkinter as tk

LIMITE = 100
BOLLA = {"utente": "bolla_utente", "jarvis": "bolla_jarvis"}


class Bolle:
    def __init__(self, text: tk.Text, *, copy, read, regenerate,
                 limit: int = LIMITE) -> None:
        self.text = text
        self.copy = copy
        self.read = read
        self.regenerate = regenerate
        self.limit = limit
        self.marks: list[str] = []
        self.bars: dict[str, tk.Widget] = {}  # segno del messaggio -> barra
        self.counter = 0
        self.last_user = ""
        text.tag_configure("bolla_utente", lmargin1=90, lmargin2=90, rmargin=14,
                           background="#0a2233")
        text.tag_configure("bolla_jarvis", lmargin1=6, lmargin2=6, rmargin=90,
                           background="#05202f")

    def inizio(self) -> str:
        """Segna l'inizio di un messaggio; va chiamato prima di inserirlo."""
        self.counter += 1
        mark = "bolla_%d" % self.counter
        self.text.mark_set(mark, "end-1c")
        self.text.mark_gravity(mark, "left")
        self.marks.append(mark)
        return mark

    def fine(self, role: str, body: str, mark: str) -> None:
        """Colora la bolla, aggiunge i pulsanti alle risposte, taglia i vecchi."""
        tag = BOLLA.get(role)
        if tag:
            self.text.tag_add(tag, mark, "end-1c")
        if role == "utente":
            self.last_user = body
        elif role == "jarvis":
            self._barra(body, self.last_user)
        self._taglia()

    def azzera(self) -> None:
        for widget in self.bars.values():
            widget.destroy()
        self.bars.clear()
        for mark in self.marks:
            self.text.mark_unset(mark)
        self.marks.clear()
        self.last_user = ""

    def _barra(self, answer: str, question: str) -> None:
        bar = tk.Frame(self.text, bg=self.text.cget("bg"))
        style = dict(bg="#0b2f44", fg="#9fd8f0", activebackground="#136488",
                     activeforeground="white", relief="flat", bd=0, padx=7,
                     pady=1, font=("Segoe UI", 8), cursor="hand2")
        tk.Button(bar, text="copia", command=lambda: self.copy(answer),
                  **style).pack(side="left", padx=(0, 4))
        tk.Button(bar, text="leggi", command=lambda: self.read(answer),
                  **style).pack(side="left", padx=(0, 4))
        if question:
            tk.Button(bar, text="rigenera",
                      command=lambda: self.regenerate(question),
                      **style).pack(side="left")
        # Subito sotto il testo della risposta, prima della riga vuota finale.
        self.text.window_create("end-2c", window=bar, padx=6)
        if self.marks:
            self.bars[self.marks[-1]] = bar

    def _taglia(self) -> None:
        extra = len(self.marks) - self.limit
        if extra <= 0:
            return
        old, self.marks = self.marks[:extra], self.marks[extra:]
        self.text.delete("1.0", self.marks[0])
        for mark in old:
            bar = self.bars.pop(mark, None)
            if bar is not None:
                bar.destroy()
            self.text.mark_unset(mark)
