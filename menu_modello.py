"""Tendina «MODELLO ▾» in alto (056 D): le 3 caselle del modello offline, per cambiarlo al volo.

Stessa tendina di «ONLINE ▾» (menu_modelli.MenuModelli, riusata). Il cambio passa da `on_use`
(lumi_model_use in jarvis.py: salva la scelta, carica il profilo e riavvia il motore, così in
memoria resta un solo modello). L'on/off è il pulsante «MODELLO ON/OFF» che esiste già.
"""
from __future__ import annotations

import tkinter as tk

from menu_modelli import BG, CYAN, MUTED, PANEL, TEXT, MenuModelli


def voci(config_path=None):
    """[(numero, percorso|None, in_uso)] per le caselle 1, 2 e 3."""
    from local_model import registro_modelli, scelta_modello
    in_uso = scelta_modello.modello_in_uso(config_path)
    caselle = registro_modelli.caselle(scelta_modello.elenca_modelli(config_path), str(in_uso), config_path)
    chiave = registro_modelli.chiave
    return [(n, caselle.get(n), bool(caselle.get(n) and in_uso and chiave(caselle[n]) == chiave(in_uso)))
            for n in registro_modelli.CASELLE]


class MenuModello(MenuModelli):
    def __init__(self, root, button, *, on_use, open_settings, config_path=None, notify=None):
        self.on_use = on_use
        self.config_path = config_path
        super().__init__(root, button, open_settings=open_settings, notify=notify)

    def _settings(self):
        return {}

    def refresh_button(self):
        try:
            from local_model import scelta_modello
            in_uso = scelta_modello.modello_in_uso(self.config_path)
            nome = scelta_modello.nome_breve(in_uso)[:22] if in_uso else ""
            self.button.configure(text=("Modello: " + nome + " ▾") if nome else "Modello ▾")
        except (tk.TclError, OSError, ValueError, RuntimeError):
            pass

    def _fill(self, popup, settings):
        from local_model import scelta_modello
        tk.Label(popup, text="Modello offline", bg=PANEL, fg=TEXT, font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(fill="x", padx=10, pady=(8, 4))
        try:
            righe = voci(self.config_path)
        except (OSError, ValueError, RuntimeError) as exc:
            self.notify("MODELLO LOCALE > Elenco non disponibile: " + str(exc)[:100])
            righe = []
        for numero, modello, in_uso in righe:
            nome = scelta_modello.nome_breve(modello)[:30] if modello else "(vuota)"
            tk.Button(popup, text="%d  %s%s" % (numero, nome, "   ← in uso" if in_uso else ""),
                      command=lambda m=modello: self._usa(m), state="normal" if modello else "disabled",
                      bg="#0b2f44" if in_uso else PANEL, fg=CYAN if in_uso else TEXT,
                      activebackground="#136488", activeforeground="white", disabledforeground=MUTED,
                      anchor="w", relief="flat", bd=0, padx=10, pady=3, font=("Segoe UI", 9),
                      cursor="hand2").pack(fill="x", padx=6, pady=1)
        tk.Frame(popup, bg="#164257", height=1).pack(fill="x", padx=8, pady=4)
        link = tk.Label(popup, text="Altri modelli e profili…", bg=PANEL, fg=CYAN, cursor="hand2",
                        font=("Segoe UI", 9, "underline"), anchor="w")
        link.pack(fill="x", padx=10, pady=(0, 8))
        link.bind("<Button-1>", lambda _e: (self.close(), self.open_settings()))

    def _usa(self, modello):
        self.close()
        if modello is not None:
            self.on_use(modello)
            self.refresh_button()
