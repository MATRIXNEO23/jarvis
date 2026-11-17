"""Menu «ONLINE ▾» in alto, accanto a GPT (15/11 sera, punti 2 e 3 della lista).

Clic su ONLINE ▾ → tendina verticale con i servizi gratuiti: spunta, barra della quota
(azzurra; arancione oltre metà consumo; rossa quasi finita), cosa offre gratis, quello
in uso evidenziato, «manca la chiave» con il link per crearla. Sotto: «Usa l'online per
tutte le domande», «Chiedi per le domande lunghe», «Chiavi e ordine…».
Si apre con un clic e si chiude cliccando nel resto di Lumi (non quando ci passi fuori).
I servizi a pagamento ($) restano solo nelle impostazioni, per non accenderli per sbaglio.
"""
from __future__ import annotations

import tkinter as tk

BG, PANEL, TEXT, MUTED, CYAN = "#020d17", "#06192a", "#bfeeff", "#6f8fa3", "#46ccfa"


def servizio_in_uso(settings, keys):
    """Il primo servizio spuntato con la chiave, nell'ordine scelto (o None)."""
    for service_id in settings["ordine"]:
        if service_id in settings["attivi"] and keys.presente(service_id):
            return service_id
    return None


class MenuModelli:
    def __init__(self, root, button, *, open_settings, open_url=None, keys=None,
                 settings_path=None, notify=None):
        import servizi_online
        self.so = servizi_online
        self.root = root
        self.button = button
        self.open_settings = open_settings
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

    def refresh_button(self):
        settings = self._settings()
        active = servizio_in_uso(settings, self.keys)
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
            # 056c: il clic arriva dal Label DENTRO il tasto (TastoBarra), non dal tasto: prima la
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
        active = servizio_in_uso(settings, self.keys)
        quote = __import__("servizi_online.quote", fromlist=["stato"])
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
            if self.keys.presente(service_id):
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
