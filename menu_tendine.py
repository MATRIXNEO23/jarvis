"""Tendine della barra in alto in un solo file (riordino 060: unione di menu_modelli, menu_ricerca, menu_modello).

Tre parti, nessuna logica cambiata: «ONLINE ▾» (MenuModelli, la base), «RICERCA ▾» (MenuRicerca)
e «MODELLO ▾» (MenuModello) riusano la stessa tendina.
"""
from __future__ import annotations

import tkinter as tk


# ======================================================================
# ONLINE
# Menu «ONLINE ▾» in alto, accanto a GPT (15/11 sera, punti 2 e 3 della lista).
#
# Clic su ONLINE ▾ → tendina verticale con i servizi gratuiti: spunta, barra della quota
# (azzurra; arancione oltre metà consumo; rossa quasi finita), cosa offre gratis, quello
# in uso evidenziato, «manca la chiave» con il link per crearla. Sotto: «Usa l'online per
# tutte le domande», «Chiedi per le domande lunghe», «Chiavi e ordine…».
# Si apre con un clic e si chiude cliccando nel resto di Lumi (non quando ci passi fuori).
# I servizi a pagamento ($) restano solo nelle impostazioni, per non accenderli per sbaglio.
# ======================================================================

BG, PANEL, TEXT, MUTED, CYAN = "#020d17", "#06192a", "#bfeeff", "#6f8fa3", "#46ccfa"


def servizio_in_uso(settings, keys, account_pronto=None):
    """Il primo servizio spuntato con la chiave (o, per il GPT dal browser, collegato), nell'ordine
    scelto (o None)."""
    for service_id in settings["ordine"]:
        if service_id not in settings["attivi"]:
            continue
        if keys.presente(service_id) or (account_pronto is not None and account_pronto(service_id)):
            return service_id
    return None


class MenuModelli:
    def __init__(self, root, button, *, open_settings, open_url=None, keys=None,
                 settings_path=None, notify=None, on_connect=None):
        from online import servizi_online
        self.so = servizi_online
        self.root = root
        self.button = button
        self.open_settings = open_settings
        self.on_connect = on_connect or open_settings      # 058: «Collega» del GPT dal browser
        self.open_url = open_url or __import__("webbrowser").open
        self.keys = keys or servizi_online.Chiavi()
        self.settings_path = settings_path
        self.notify = notify or (lambda text: None)     # 056 E: gli errori di salvataggio si dicono
        self.popup = None
        button.configure(command=self.toggle)
        root.bind_all("<Button-1>", self._click_anywhere, add="+")
        self.refresh_button()

    def _settings(self):
        return self.so.carica_impostazioni(self.settings_path)

    def _save(self, settings):
        try:
            self.so.salva_impostazioni(settings, self.settings_path)
        except (OSError, RuntimeError) as exc:
            self.notify("ONLINE / ERRORE > Scelta non salvata: " + str(exc)[:120])
        self.refresh_button()

    def _account_pronto(self, service_id):
        service = self.so.PER_ID.get(service_id)
        return bool(service is not None and service.tipo == "account" and self.so._account_pronto())

    def _in_uso(self, settings):
        return servizio_in_uso(settings, self.keys, self._account_pronto)

    def refresh_button(self):
        settings = self._settings()
        active = self._in_uso(settings)
        name = self.so.PER_ID[active].nome.split()[0] if active else ""
        try:
            self.button.configure(text="Online ▾")
        except tk.TclError:
            pass

    # --- apertura e chiusura ---------------------------------------------------------------
    def toggle(self):
        if self.popup is not None:
            self.close()
        else:
            self.open()

    def close(self):
        popup, self.popup = self.popup, None
        if popup is not None:
            try:
                popup.destroy()
            except tk.TclError:
                pass
        self.refresh_button()

    def _click_anywhere(self, event):
        if self.popup is None:
            return
        widget = event.widget
        try:
            # 057: il clic arriva dal Label DENTRO il tasto (TastoBarra), non dal tasto: prima la
            # tendina si apriva e il bind_all la richiudeva subito. Il ⏻ del tasto non è «dentro».
            on_button = (widget is self.button or str(widget).startswith(str(self.button) + ".")) \
                and widget is not getattr(self.button, "power", None)
            inside = str(widget).startswith(str(self.popup)) or on_button
        except Exception:
            inside = False
        if not inside:
            self.close()

    def open(self):
        settings = self._settings()
        popup = tk.Toplevel(self.root, bg=PANEL, highlightthickness=1, highlightbackground="#1191c6")
        popup.overrideredirect(True)
        try:
            popup.attributes("-topmost", True)
        except tk.TclError:
            pass
        self.popup = popup
        self.vars = {}
        self._fill(popup, settings)
        popup.update_idletasks()
        x = self.button.winfo_rootx() + self.button.winfo_width() - popup.winfo_reqwidth()
        y = self.button.winfo_rooty() + self.button.winfo_height() + 2
        popup.geometry("+%d+%d" % (max(0, x), y))
        popup.bind("<Escape>", lambda _e: self.close())
        popup.focus_set()

    def _fill(self, popup, settings):
        tk.Label(popup, text="Servizi online", bg=PANEL, fg=TEXT, font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(fill="x", padx=10, pady=(8, 4))
        active = self._in_uso(settings)
        quote = __import__("online.servizi_online.quote", fromlist=["stato"])
        for service_id in settings["ordine"]:
            service = self.so.PER_ID[service_id]
            if not service.gratis:
                continue
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
            if service.tipo == "account":
                # 058: GPT dal browser, non un servizio a chiave: collegato / non collegato.
                pronto = self._account_pronto(service_id)
                tk.Label(line, text="collegato" if pronto else "non collegato", bg=row["bg"],
                         fg="#3ddc97" if pronto else "#f2a33a", font=("Segoe UI", 8)).pack(side="left")
                if not pronto:
                    link = tk.Label(line, text="Collega", bg=row["bg"], fg=CYAN,
                                    font=("Segoe UI", 8, "underline"), cursor="hand2")
                    link.pack(side="left", padx=8)
                    link.bind("<Button-1>", lambda _e: (self.close(), self.on_connect()))
            elif self.keys.presente(service_id):
                info = quote.stato(service_id, limite_utente=settings["limiti"].get(service_id))
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
            errore = self.so.ULTIMO_ERRORE.get(service_id)
            if errore:                       # 058: l'ultimo errore, finché il servizio non risponde di nuovo
                tk.Label(row, text="ultimo errore: " + str(errore)[:60], bg=row["bg"], fg="#f2a33a",
                         font=("Segoe UI", 8), anchor="w").pack(fill="x", padx=26)
            tk.Label(row, text=service.limite, bg=row["bg"], fg=MUTED, font=("Segoe UI", 8),
                     wraplength=330, justify="left", anchor="w").pack(fill="x", padx=26, pady=(0, 4))
        tk.Frame(popup, bg="#164257", height=1).pack(fill="x", padx=8, pady=4)
        self.use_always = tk.BooleanVar(value=settings["usa_sempre"])
        self.ask_long = tk.BooleanVar(value=settings["proponi_lunghe"])
        for text, var in (("Usa l'online per tutte le domande", self.use_always),
                          ("Chiedi per le domande lunghe", self.ask_long)):
            tk.Checkbutton(popup, text=text, variable=var, command=self._toggle_options, bg=PANEL,
                           fg=TEXT, selectcolor=BG, activebackground=PANEL, anchor="w",
                           font=("Segoe UI", 9)).pack(fill="x", padx=8)
        settings_link = tk.Label(popup, text="Chiavi e ordine…", bg=PANEL, fg=CYAN, cursor="hand2",
                                 font=("Segoe UI", 9, "underline"), anchor="w")
        settings_link.pack(fill="x", padx=10, pady=(4, 8))
        settings_link.bind("<Button-1>", lambda _e: (self.close(), self.open_settings()))

    def _toggle(self, service_id):
        settings = self._settings()
        on = self.vars[service_id].get()
        active = [i for i in settings["attivi"] if i != service_id]
        if on:
            active.append(service_id)
        settings["attivi"] = [i for i in settings["ordine"] if i in active]
        self._save(settings)
        self._rebuild()

    def _rebuild(self):
        """Ridisegna la tendina aperta (es. cambia il servizio «in uso»)."""
        if self.popup is None:
            return
        for child in self.popup.winfo_children():
            child.destroy()
        self.vars = {}
        self._fill(self.popup, self._settings())

    def _toggle_options(self):
        settings = self._settings()
        settings["usa_sempre"] = self.use_always.get()
        settings["proponi_lunghe"] = self.ask_long.get()
        self._save(settings)


# ======================================================================
# RICERCA
# Menu «RICERCA ▾» in alto (055): al posto dell'interruttore RICERCA ON/OFF.
#
# Stessa tendina di «ONLINE ▾» (MenuModelli, riusata): un elenco dei servizi di
# ricerca (Tavily, Exa, Firecrawl, Linkup), ciascuno con la sua spunta e la sua barra di quota.
# Per Tavily la quota è letta dall'API; per gli altri valgono le «ricerche rilevate».
# «Chiavi e ordine…» apre le impostazioni dei servizi di ricerca.
# ======================================================================

def servizio_attivo(settings, keys, sr):
    """Il primo servizio spuntato, con chiave e ricerca collegata, nell'ordine scelto."""
    for service_id in settings["ordine"]:
        if (service_id in settings["attivi"] and sr.PER_ID[service_id].adattatore is not None
                and keys.presente(service_id)):
            return service_id
    return None


class MenuRicerca(MenuModelli):
    def __init__(self, root, button, *, open_settings, open_url=None, keys=None, settings_path=None, notify=None):
        self.sr = __import__("online").servizi_ricerca
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
            self.button.configure(text="Ricerca ▾")
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


# ======================================================================
# MODELLO
# Tendina «MODELLO ▾» in alto (056 D): le 3 caselle del modello offline, per cambiarlo al volo.
#
# Stessa tendina di «ONLINE ▾» (MenuModelli, riusata). Il cambio passa da `on_use`
# (lumi_model_use in jarvis.py: salva la scelta, carica il profilo e riavvia il motore, così in
# memoria resta un solo modello). L'on/off è il pulsante «MODELLO ON/OFF» che esiste già.
# ======================================================================

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
            self.button.configure(text="Modello ▾")   # 057: il nome si vede solo nella tendina
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
