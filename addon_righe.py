"""Righe degli add-on nelle Impostazioni (concordato a voce il 15/11 sera).

Ogni add-on: icona + nome, accanto un interruttore a scorrimento.
- clic sull'interruttore: acceso / spento (scorre da una parte all'altra);
- icona azzurra se acceso, arancione se spento;
- clic sull'icona o sul nome: si apre il suo menu a destra.
"""
from __future__ import annotations

import tkinter as tk

AZZURRO, ARANCIONE = "#46ccfa", "#ff9f43"
PANEL, SEL, TEXT, BINARIO = "#06192a", "#0b2f44", "#bfeeff", "#29404f"

ICONE = {"accesso_file": "📁", "programmi_app": "🚀", "sveglia": "⏰", "musica": "🎵",
         "controllo_pc": "🖥", "telegram": "✈", "modello_locale": "🧠", "meteo": "⛅",
         "diagnostica_sistema": "🩺"}
ICONA_GENERICA = "🧩"


def icona(addon_id: str) -> str:
    return ICONE.get(addon_id, ICONA_GENERICA)


def colore(enabled: bool) -> str:
    return AZZURRO if enabled else ARANCIONE


class Interruttore(tk.Canvas):
    """Interruttore a scorrimento: pallino a destra = acceso, a sinistra = spento."""

    W, H, PASSI = 38, 20, 6

    def __init__(self, parent, *, acceso=False, comando=None, bg=PANEL):
        super().__init__(parent, width=self.W, height=self.H, bg=bg, highlightthickness=0,
                         bd=0, cursor="hand2")
        self.acceso = bool(acceso)
        self.comando = comando
        self.in_corso = False
        r = self.H // 2
        self.binario = self.create_oval(0, 0, self.H, self.H, width=0)
        self.binario2 = self.create_oval(self.W - self.H, 0, self.W, self.H, width=0)
        self.binario3 = self.create_rectangle(r, 0, self.W - r, self.H, width=0)
        self.pallino = self.create_oval(0, 0, 0, 0, fill="#e9f7ff", width=0)
        self._x = self._meta(self.acceso)
        self._disegna()
        self.bind("<Button-1>", lambda _e: self.clic())

    def _meta(self, acceso):
        return self.W - self.H // 2 if acceso else self.H // 2

    def _disegna(self):
        fill = AZZURRO if self.acceso else BINARIO
        for item in (self.binario, self.binario2, self.binario3):
            self.itemconfigure(item, fill=fill)
        r = self.H // 2 - 3
        self.coords(self.pallino, self._x - r, self.H // 2 - r, self._x + r, self.H // 2 + r)

    def imposta(self, acceso: bool, anima: bool = True):
        self.acceso = bool(acceso)
        meta = self._meta(self.acceso)
        if not anima:
            self._x = meta
            self._disegna()
            return
        passo = (meta - self._x) / self.PASSI

        def muovi(n=self.PASSI):
            if n <= 1:
                self._x = meta
            else:
                self._x += passo
            self._disegna()
            if n > 1:
                self.after(15, lambda: muovi(n - 1))
        muovi()

    def clic(self):
        """Chiede il cambio; scorre solo se il cambio è avvenuto davvero."""
        voluto = not self.acceso
        self.in_corso = True
        try:
            ok = self.comando(voluto) if self.comando else True
        finally:
            self.in_corso = False
        if ok:
            self.imposta(voluto)


class RigheAddon:
    """Elenco degli add-on installati dentro `parent`.

    elenco()          -> [{"id", "name", "enabled"}]
    apri(id)          mostra il menu dell'add-on
    cambia(id, bool)  accende/spegne, ritorna True se è cambiato
    """

    def __init__(self, parent, *, elenco, apri, cambia):
        self.frame = tk.Frame(parent, bg=PANEL)
        self.elenco, self.apri_cb, self.cambia_cb = elenco, apri, cambia
        self.righe = {}          # id -> (riga, icona, nome, interruttore)
        self.scelto = None
        self.aggiorna()

    def aggiorna(self):
        for child in self.frame.winfo_children():
            child.destroy()
        self.righe = {}
        try:
            items = list(self.elenco())
        except Exception as exc:        # l'elenco non deve rompere le impostazioni
            tk.Label(self.frame, text="Add-on non disponibili: " + str(exc)[:60], bg=PANEL,
                     fg=ARANCIONE, wraplength=200, justify="left").pack(anchor="w")
            return
        for item in items:
            ident = item["id"]
            row = tk.Frame(self.frame, bg=PANEL)
            row.pack(fill="x", pady=1)
            switch = Interruttore(row, acceso=item["enabled"],
                                  comando=lambda v, i=ident: self._cambia(i, v))
            switch.pack(side="right", padx=(4, 6))
            icon = tk.Label(row, text=icona(ident), bg=PANEL, fg=colore(item["enabled"]),
                            font=("Segoe UI Symbol", 13), cursor="hand2", width=2)
            icon.pack(side="left", padx=(6, 2))
            name = tk.Label(row, text=item["name"], bg=PANEL, fg=TEXT, anchor="w",
                            font=("Segoe UI", 9), cursor="hand2")
            name.pack(side="left", fill="x", expand=True)
            for widget in (row, icon, name):
                widget.bind("<Button-1>", lambda _e, i=ident: self.apri(i))
            self.righe[ident] = (row, icon, name, switch)
        if self.scelto in self.righe:
            self._evidenzia(self.scelto)

    def sincronizza(self):
        """Aggiorna colori e interruttori senza ricostruire le righe."""
        try:
            items = {item["id"]: item for item in self.elenco()}
        except Exception:
            return
        if set(items) != set(self.righe):          # add-on installati o rimossi
            self.aggiorna()
            return
        for ident, (_row, icon, _name, switch) in self.righe.items():
            enabled = bool(items[ident]["enabled"])
            icon.configure(fg=colore(enabled))
            if switch.acceso != enabled and not switch.in_corso:
                switch.imposta(enabled, anima=False)

    def _cambia(self, ident, voluto):
        ok = bool(self.cambia_cb(ident, voluto))
        if ok and ident in self.righe:
            self.righe[ident][1].configure(fg=colore(voluto))
        return ok

    def _evidenzia(self, ident):
        for key, (row, icon, name, switch) in self.righe.items():
            bg = SEL if key == ident else PANEL
            for widget in (row, icon, name, switch):
                widget.configure(bg=bg)

    def apri(self, ident):
        self.scelto = ident
        self._evidenzia(ident)
        self.apri_cb(ident)
