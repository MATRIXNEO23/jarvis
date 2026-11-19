"""Slide «Basso consumo / Veloce» in alto a sinistra (056 B), al posto di «INTERFACCIA NEURALE».

Riusa l'interruttore a scorrimento delle add-on (addon_righe.Interruttore): pallino a sinistra =
Basso consumo (offline, online solo col «sì»), a destra = Veloce (primo modello online della
lista, offline di riserva). Il salvataggio lo fa chi ascolta `on_change` (jarvis.py → save_settings).
"""
from __future__ import annotations

import tkinter as tk

from addon_righe import Interruttore

BG, ACCESO, SPENTO = "#020d17", "#46ccfa", "#4985a7"
ETICHETTE = {"basso_consumo": "Basso consumo", "veloce": "Veloce"}


class SlideModalita(tk.Frame):
    def __init__(self, parent, *, on_change=None, modalita="basso_consumo", bg=BG):
        super().__init__(parent, bg=bg)
        self.on_change = on_change
        self.sinistra = tk.Label(self, text=ETICHETTE["basso_consumo"], bg=bg, font=("Consolas", 9))
        self.sinistra.pack(side="left")
        self.interruttore = Interruttore(self, acceso=modalita == "veloce", bg=bg,
                                         comando=self._cambia)
        self.interruttore.pack(side="left", padx=6)
        self.destra = tk.Label(self, text=ETICHETTE["veloce"], bg=bg, font=("Consolas", 9))
        self.destra.pack(side="left")
        for label, modo in ((self.sinistra, "basso_consumo"), (self.destra, "veloce")):
            label.bind("<Button-1>", lambda _e, m=modo: self.scegli(m))
            label.configure(cursor="hand2")
        self._colora(modalita)

    @property
    def modalita(self) -> str:
        return "veloce" if self.interruttore.acceso else "basso_consumo"

    def _colora(self, modalita):
        self.sinistra.configure(fg=ACCESO if modalita == "basso_consumo" else SPENTO)
        self.destra.configure(fg=ACCESO if modalita == "veloce" else SPENTO)

    def _cambia(self, voluto: bool) -> bool:
        modo = "veloce" if voluto else "basso_consumo"
        ok = self.on_change(modo) if self.on_change else True
        if ok is not False:
            self._colora(modo)
            return True
        return False

    def scegli(self, modo: str) -> None:
        """Clic sull'etichetta: stesso effetto di far scorrere l'interruttore."""
        if modo != self.modalita:
            self.interruttore.clic()

    def imposta(self, modo: str) -> None:
        """Allinea la slide al valore salvato (senza richiamare on_change)."""
        if modo in ETICHETTE and modo != self.modalita:
            self.interruttore.imposta(modo == "veloce", anima=False)
        self._colora(self.modalita)
