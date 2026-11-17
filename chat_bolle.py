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
                 limit: int = LIMITE, deepen=None) -> None:
        self.text = text
        self.copy = copy
        self.read = read
        self.regenerate = regenerate
        self.deepen = deepen          # 056: pulsante «Approfondisci» (conferma, poi online)
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

    def cronologia(self, title: str, pairs, identity: dict, shown: int = LIMITE // 2) -> None:
        """Chat aperta dall'elenco: gli ultimi `shown` scambi; sopra, se ce ne sono
        altri, «▲ messaggi precedenti» ne carica altri 50 (decisione 15/11)."""
        pairs = list(pairs)
        text = self.text
        text.configure(state="normal")
        text.delete("1.0", "end")
        self.azzera()
        self.limit = max(LIMITE, 2 * shown)
        older = len(pairs) - shown
        if older > 0:
            more = tk.Button(
                text, text="▲ messaggi precedenti (%d)" % older,
                command=lambda: text.after_idle(
                    lambda: self.cronologia(title, pairs, identity, shown + 50)),
                bg="#0b2f44", fg="#9fd8f0", relief="flat", bd=0, padx=8,
                font=("Segoe UI", 8), cursor="hand2")
            text.window_create("end", window=more)
            self.bars["__precedenti__"] = more
            text.insert("end", "\n")
        text.insert("end", "— " + title + " —\n\n", ("sistema_titolo",))
        for question, answer in pairs[-shown:] if shown else []:
            for role, body in (("utente", question), ("jarvis", answer)):
                mark = self.inizio()
                text.insert("end", identity[role] + "\n", (role, "message_head"))
                text.insert("end", body + "\n\n", role)
                self.fine(role, body, mark)
        if older > 0:
            text.see("1.0")
        else:
            text.see("end")
        text.configure(state="disabled")

    def messaggi(self, title: str, items, action=None) -> None:
        """Conversazione non del modello (es. Telegram): bolle senza copia/leggi/rigenera.
        items: [(intestazione, «utente»|«jarvis», testo)]; action: (etichetta, funzione)."""
        text = self.text
        text.configure(state="normal")
        text.delete("1.0", "end")
        self.azzera()
        text.insert("end", "— " + title + " —\n", ("sistema_titolo",))
        if action is not None:
            button = tk.Button(text, text=action[0], command=action[1], bg="#0b2f44",
                               fg="#9fd8f0", relief="flat", bd=0, padx=8,
                               font=("Segoe UI", 8), cursor="hand2")
            text.window_create("end", window=button)
            self.bars["__azione__"] = button
        text.insert("end", "\n\n")
        if not items:
            text.insert("end", "Nessun messaggio ancora.\n", ("sistema_titolo",))
        for header, role, body in items:
            start = text.index("end-1c")
            text.insert("end", header + "\n", (role, "message_head"))
            text.insert("end", str(body) + "\n\n", role)
            text.tag_add(BOLLA.get(role, "bolla_jarvis"), start, "end-1c")
        text.see("end")
        text.configure(state="disabled")

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
                      **style).pack(side="left", padx=(0, 4))
            if self.deepen is not None:
                tk.Button(bar, text="Approfondisci", command=self.deepen,
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
