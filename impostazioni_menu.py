"""Impostazioni riordinate (15/11 sera, punto 6 della lista concordata).

Nella finestra delle impostazioni, al posto delle linguette:
    colonna 1: Interfaccia ▸ Voce ▸ Memoria ▸ Modelli ▸ Add-on ▸ Tutorial ▸ Info ▸
    colonna 2: le voci della categoria scelta (si apre di fianco, con un clic)
    a destra:  solo la parte scelta, niente scorrere tra cento opzioni.
Le sezioni esistenti non vengono riscritte: ogni riquadro viene assegnato alla sua voce
in base al titolo (MAPPA); quelli non previsti finiscono in «Altro» della categoria della
loro vecchia scheda, così non sparisce niente.
La finestra si chiude da sola quando clicchi nella finestra principale di Lumi.
"""
from __future__ import annotations

import tkinter as tk

CATEGORIE = ("Interfaccia", "Voce", "Memoria", "Modelli", "Add-on", "Tutorial", "Info")

# titolo del riquadro (inizio) -> (categoria, voce). Ordine = ordine nella colonna.
MAPPA = (
    ("Mini avatar", ("Interfaccia", "Mini avatar")),
    ("Aiuto comandi", ("Interfaccia", "Riquadro dei comandi")),
    ("Risposte vocali offline", ("Voce", "Voci")),
    ("La mia voce", ("Voce", "La mia voce")),
    ("Personalizzazione comandi", ("Voce", "Parole dei comandi e frasi")),
    ("Memoria generale", ("Memoria", "Second Brain")),
    ("Contesto del modello locale", ("Memoria", "Contesto e ricordi")),
    ("Progetti", ("Memoria", "Progetti")),
    ("Spazio su disco", ("Memoria", "Pulizia dati")),
    ("Modello locale", ("Modelli", "Modello locale")),
    ("Connessione ChatGPT", ("Modelli", "GPT dal browser")),
    ("Servizi online", ("Modelli", "Servizi online")),
    ("Orchestratore online", ("Modelli", "Orchestratore")),
    ("Add-on", ("Add-on", "Gestisci add-on")),
    ("GitHub", ("Add-on", "🐙 GitHub")),
    ("Diagnostica per Claude", ("Add-on", "🩺 Diagnostica per Claude")),
    ("Diagnostica servizi", ("Info", "Diagnostica")),
)
# Cosa non ha un riquadro col titolo (testi e caselle sciolte) segue la vecchia scheda.
SCHEDE = {"Voce": ("Voce", "Microfono e ascolto"), "Interfaccia": ("Interfaccia", "Aspetto e finestra"),
          "Timer e allarmi": ("Add-on", "⏰ Timer e sveglia"), "GPT e memoria": ("Modelli", "Altro"),
          "Progetti e servizi": ("Add-on", "Altro"), "Tutorial": ("Tutorial", "Tutorial"),
          "Info": ("Info", "Versione e licenze")}
# Schede che restano intere sotto una sola voce (es. Timer e sveglia).
INTERE = ("Timer e allarmi", "Tutorial", "Info")

BG, PANEL, TEXT, MUTED, CYAN, SEL = "#020d17", "#06192a", "#bfeeff", "#6f8fa3", "#46ccfa", "#0b2f44"


def _titolo(widget) -> str:
    try:
        return str(widget.cget("text"))
    except (tk.TclError, AttributeError):
        return ""


def assegna(tab_title: str, widget) -> tuple[str, str]:
    if tab_title not in INTERE:
        title = _titolo(widget) if widget.winfo_class() == "TLabelframe" else ""
        for prefix, place in MAPPA:
            if title.startswith(prefix):
                return place
    return SCHEDE.get(tab_title, ("Info", "Altro"))


def raccogli(pages: dict) -> dict:
    """{categoria: {voce: [(pagina, widget)]}} nell'ordine di CATEGORIE e MAPPA."""
    order = {place: n for n, (_prefix, place) in enumerate(MAPPA)}
    found = {}
    for tab_title, inner in pages.items():
        for widget in inner.winfo_children():
            if not widget.winfo_manager():
                continue
            category, item = assegna(tab_title, widget)
            found.setdefault(category, {}).setdefault(item, []).append((inner, widget))
    result = {}
    for category in CATEGORIE:
        items = found.get(category, {})

        def key(name, category=category):
            if name == "Altro":
                return (2, 0)
            position = order.get((category, name))
            return (0, 0) if position is None else (1, position)   # prima la voce generale
        result[category] = dict(sorted(items.items(), key=lambda kv: key(kv[0])))
    return result


class Navigazione:
    """Due colonne a sinistra e la parte scelta a destra, dentro la finestra esistente."""

    def __init__(self, window, notebook, pages: dict, *, main_root=None):
        self.window = window
        self.notebook = notebook
        self.pages = pages                       # titolo scheda -> frame interno
        self.tabs = {}                           # frame interno -> scheda del notebook
        for tab in notebook.tabs():
            title = notebook.tab(tab, "text")
            if title in pages:
                self.tabs[str(pages[title])] = tab
        self.packing = {}                        # widget -> opzioni di pack originali
        for inner in pages.values():
            for widget in inner.winfo_children():
                if widget.winfo_manager() == "pack":
                    info = widget.pack_info()
                    info.pop("in", None)
                    self.packing[str(widget)] = info
        self.tree = raccogli(pages)
        style = __import__("tkinter.ttk", fromlist=["Style"]).Style(window)
        style.layout("LumiNoTabs.TNotebook.Tab", [])
        notebook.configure(style="LumiNoTabs.TNotebook")
        self.nav = tk.Frame(window, bg=PANEL)
        self.nav.pack(side="left", fill="y", before=notebook)
        self.cats = tk.Frame(self.nav, bg=PANEL)
        self.cats.pack(side="left", fill="y", padx=(6, 0), pady=6)
        self.items = tk.Frame(self.nav, bg=PANEL)
        self.items.pack(side="left", fill="y", padx=6, pady=6)
        self.buttons = {}
        for category in CATEGORIE:
            if not self.tree.get(category):
                continue
            button = tk.Button(self.cats, text=category + "  ▸", anchor="w", width=13,
                               command=lambda c=category: self.apri_categoria(c), bg=PANEL, fg=TEXT,
                               activebackground=SEL, activeforeground=CYAN, relief="flat", bd=0,
                               font=("Segoe UI", 10), padx=8, pady=5, cursor="hand2")
            button.pack(fill="x", pady=1)
            self.buttons[category] = button
        self.item_buttons = {}
        self.current = (None, None)
        if main_root is not None:
            main_root.bind_all("<Button-1>", self._click_main, add="+")
            self.main_root = main_root
        first = next(iter(self.buttons), None)
        if first:
            self.apri_categoria(first)

    def apri_categoria(self, category):
        for name, button in self.buttons.items():
            button.configure(bg=SEL if name == category else PANEL,
                             fg=CYAN if name == category else TEXT)
        for child in self.items.winfo_children():
            child.destroy()
        self.item_buttons = {}
        for item in self.tree.get(category, {}):
            button = tk.Button(self.items, text=item, anchor="w", width=24,
                               command=lambda i=item: self.mostra(category, i), bg=PANEL, fg=TEXT,
                               activebackground=SEL, activeforeground=CYAN, relief="flat", bd=0,
                               font=("Segoe UI", 9), padx=8, pady=4, cursor="hand2")
            button.pack(fill="x", pady=1)
            self.item_buttons[item] = button
        items = list(self.tree.get(category, {}))
        if items:
            self.mostra(category, items[0])

    def mostra(self, category, item):
        """Mostra solo i riquadri della voce scelta."""
        entries = self.tree.get(category, {}).get(item, [])
        if not entries:
            return
        inner = entries[0][0]
        for page in self.pages.values():
            for widget in page.winfo_children():
                if widget.winfo_manager() == "pack":
                    widget.pack_forget()
        for page, widget in entries:
            widget.pack(in_=page, **self.packing.get(str(widget), {"fill": "x"}))
        tab = self.tabs.get(str(inner))
        if tab is not None:
            self.notebook.select(tab)
        for name, button in self.item_buttons.items():
            button.configure(bg=SEL if name == item else PANEL, fg=CYAN if name == item else TEXT)
        self.current = (category, item)
        try:                                      # in cima alla parte scelta
            canvas = inner.master
            canvas.yview_moveto(0)
        except (tk.TclError, AttributeError):
            pass

    def voci(self):
        return {category: list(items) for category, items in self.tree.items() if items}

    def _click_main(self, event):
        """Clic nella finestra principale: le impostazioni si chiudono da sole."""
        try:
            if (self.window.winfo_viewable() and event.widget.winfo_toplevel() is self.main_root):
                self.window.withdraw()
        except (tk.TclError, AttributeError):
            pass


# --- pagine nuove: Tutorial e Info ------------------------------------------------------------
def pagina_tutorial(parent, *, start_tutorial, reset_tutorials, open_voice_training):
    from tkinter import ttk
    import aiuto_comandi
    ttk.Label(parent, text="Tutorial", font=("Segoe UI", 12, "bold")).pack(anchor="w")
    ttk.Label(parent, wraplength=520, text=(
        "Fai partire quello che vuoi: Lumi ti dice un comando alla volta e aspetta che tu lo "
        "faccia. Durante il tutorial: «salta passo», «esci dal tutorial».")).pack(anchor="w", pady=(2, 8))
    for mode, steps in aiuto_comandi.PASSI.items():
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=2)
        ttk.Button(row, text="▶", width=3, command=lambda m=mode: start_tutorial(m)).pack(side="left")
        ttk.Label(row, text="%s (%d passi)" % (aiuto_comandi.NOMI.get(mode, mode), len(steps))
                  ).pack(side="left", padx=6)
    row = ttk.Frame(parent)
    row.pack(fill="x", pady=(8, 2))
    ttk.Button(row, text="▶", width=3, command=open_voice_training).pack(side="left")
    ttk.Label(row, text="La mia voce: allenamento della voce sui comandi").pack(side="left", padx=6)
    ttk.Button(parent, text="Riproponi i tutorial la prima volta in ogni finestra",
               command=reset_tutorials).pack(anchor="w", pady=(10, 0))


def versione(root_dir=None) -> dict:
    """Dati della build dal file VERSIONE.json del pacchetto (o «sviluppo»)."""
    import json
    from pathlib import Path
    path = Path(root_dir or Path(__file__).resolve().parent) / "VERSIONE.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {"nome": "Lumi " + str(data.get("build_label", "?")),
                "commit": str(data.get("source_commit", ""))[:7],
                "motore": str(data.get("upstream_koboldcpp_commit", ""))[:7]}
    except (OSError, ValueError):
        return {"nome": "Lumi (versione di sviluppo)", "commit": "", "motore": ""}


def licenze(root_dir=None) -> list[tuple[str, str]]:
    """(nome, licenza) delle parti di altri incluse nel pacchetto, lette dai file presenti."""
    from pathlib import Path
    base = Path(root_dir or Path(__file__).resolve().parent)
    out = []
    if (base / "native_engine" / "LICENSE.md").is_file() or (base / "native_engine").is_dir():
        out.append(("KoboldCpp (motore del modello locale)", "AGPL-3.0 — native_engine/LICENSE.md"))
    readme = base / "terze_parti" / "LEGGIMI.md"
    try:
        for line in readme.read_text(encoding="utf-8").splitlines():
            cells = [c.strip(" `") for c in line.split("|")]
            if len(cells) > 5 and cells[1].endswith("/") and cells[1] != "Cartella":
                out.append((cells[2] + " " + cells[3].split(" (")[0], cells[4].split(" (")[0]))
    except OSError:
        pass
    return out


def pagina_info(parent, root_dir=None):
    from tkinter import ttk
    info = versione(root_dir)
    ttk.Label(parent, text=info["nome"], font=("Segoe UI", 14, "bold")).pack(anchor="w")
    details = []
    if info["commit"]:
        details.append("sorgente " + info["commit"])
    if info["motore"]:
        details.append("motore KoboldCpp " + info["motore"])
    if details:
        ttk.Label(parent, text=" · ".join(details), foreground="#888").pack(anchor="w")
    ttk.Label(parent, text="Parti di altri incluse e licenze", font=("Segoe UI", 10, "bold")
              ).pack(anchor="w", pady=(12, 2))
    for name, licence in licenze(root_dir) or [("Nessuna parte esterna trovata", "")]:
        ttk.Label(parent, text="• %s — %s" % (name, licence), wraplength=520).pack(anchor="w")
