"""Menu «RICERCA ▾» in alto (055): al posto dell'interruttore RICERCA ON/OFF.

Stessa tendina di «ONLINE ▾» (menu_modelli.MenuModelli, riusata): un elenco dei servizi di
ricerca (Tavily, Exa, Firecrawl, Linkup), ciascuno con la sua spunta e la sua barra di quota.
Per Tavily la quota è letta dall'API; per gli altri valgono le «ricerche rilevate».
«Chiavi e ordine…» apre le impostazioni dei servizi di ricerca.
"""
from __future__ import annotations

import tkinter as tk

from menu_modelli import BG, CYAN, MUTED, PANEL, TEXT, MenuModelli


def servizio_attivo(settings, keys, sr):
    """Il primo servizio spuntato, con chiave e ricerca collegata, nell'ordine scelto."""
    for service_id in settings["ordine"]:
        if (service_id in settings["attivi"] and sr.PER_ID[service_id].adattatore is not None
                and keys.presente(service_id)):
            return service_id
    return None


class MenuRicerca(MenuModelli):
    def __init__(self, root, button, *, open_settings, open_url=None, keys=None, settings_path=None, notify=None):
        self.sr = __import__("servizi_ricerca")
        super().__init__(root, button, open_settings=open_settings, open_url=open_url,
                         keys=keys or self.sr.chiavi(), settings_path=settings_path, notify=notify)

    def _settings(self):
        return self.sr.carica_impostazioni(self.settings_path)

    def _save(self, settings):
        try:
            self.sr.salva_impostazioni(settings, self.settings_path)
        except (OSError, RuntimeError) as exc:
            self.notify("RICERCA / ERRORE > Scelta non salvata: " + str(exc)[:120])
        self.refresh_button()

    def refresh_button(self):
        settings = self._settings()
        active = servizio_attivo(settings, self.keys, self.sr)
        name = self.sr.PER_ID[active].nome if active else ""
        try:
            self.button.configure(text=("RICERCA " + name + " ▾") if active else "RICERCA ▾",
                                  fg=CYAN if active else MUTED)
        except tk.TclError:
            pass

    def _fill(self, popup, settings):
        tk.Label(popup, text="Servizi di ricerca", bg=PANEL, fg=TEXT, font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(fill="x", padx=10, pady=(8, 4))
        active = servizio_attivo(settings, self.keys, self.sr)
        for service_id in settings["ordine"]:
            service = self.sr.PER_ID[service_id]
            row = tk.Frame(popup, bg="#0b2f44" if service_id == active else PANEL)
            row.pack(fill="x", padx=6, pady=1)
            var = tk.BooleanVar(value=service_id in settings["attivi"])
            self.vars[service_id] = var
            tk.Checkbutton(row, text=service.nome + ("   ← in uso" if service_id == active else ""),
                           variable=var, command=lambda i=service_id: self._toggle(i),
                           bg=row["bg"], fg=TEXT, selectcolor=BG, activebackground=row["bg"],
                           activeforeground=CYAN, anchor="w", font=("Segoe UI", 9)
                           ).pack(fill="x", padx=2)
            line = tk.Frame(row, bg=row["bg"])
            line.pack(fill="x", padx=26, pady=(0, 3))
            if service.adattatore is None:
                tk.Label(line, text="ricerca non ancora collegata", bg=row["bg"], fg=MUTED,
                         font=("Segoe UI", 8)).pack(side="left")
            elif self.keys.presente(service_id):
                info = self.sr.quota_servizio(service_id, self.keys)
                bar = tk.Canvas(line, width=110, height=8, bg="#10293a", highlightthickness=0)
                bar.pack(side="left", pady=2)
                left = 1.0 if info["usato"] is None else 1 - info["usato"]
                bar.create_rectangle(0, 0, int(110 * left), 8, fill=info["colore"], width=0)
                tk.Label(line, text=info["testo"], bg=row["bg"], fg=MUTED,
                         font=("Segoe UI", 8)).pack(side="left", padx=6)
            else:
                tk.Label(line, text="manca la chiave", bg=row["bg"], fg="#f2a33a",
                         font=("Segoe UI", 8)).pack(side="left")
                link = tk.Label(line, text="Prendi la chiave", bg=row["bg"], fg=CYAN,
                                font=("Segoe UI", 8, "underline"), cursor="hand2")
                link.pack(side="left", padx=8)
                link.bind("<Button-1>", lambda _e, u=service.chiavi: self.open_url(u))
        tk.Frame(popup, bg="#164257", height=1).pack(fill="x", padx=8, pady=4)
        settings_link = tk.Label(popup, text="Chiavi e ordine…", bg=PANEL, fg=CYAN, cursor="hand2",
                                 font=("Segoe UI", 9, "underline"), anchor="w")
        settings_link.pack(fill="x", padx=10, pady=(4, 8))
        settings_link.bind("<Button-1>", lambda _e: (self.close(), self.open_settings()))

    def _toggle(self, service_id):
        settings = self._settings()
        active = [i for i in settings["attivi"] if i != service_id]
        if self.vars[service_id].get():
            active.append(service_id)
        settings["attivi"] = [i for i in settings["ordine"] if i in active]
        self._save(settings)
        self._rebuild()
