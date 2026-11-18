"""058 (approvato 04:22): due tendine accanto alla casella della chat, stile barra 057 (azzurro su blu).

«Modello ▾»: Automatico, poi i soli servizi online spuntati nella tendina Online in alto. Decide
SOLO quale servizio usare quando la catena arriva all'online (comandi → modello offline → online
col «Vado online?» restano come sono): Automatico segue l'ordine della tendina Online, un servizio
scelto va per primo con gli altri di ripiego. «Potenza ▾»: Auto, Bassa, Media, Alta, valida per i
servizi che supportano il ragionamento (Auto = bassa in chat, normale nei lavori
dell'orchestratore). Le scelte stanno in servizi_online.json (campi modello_chat e potenza).
Le tendine si aprono SOPRA il tasto (la casella è in fondo alla finestra) e restano dentro Lumi."""
from __future__ import annotations

import tkinter as tk

from menu_modelli import BG, CYAN, MUTED, PANEL, TEXT, MenuModelli

DESCRIZIONI_POTENZA = {"auto": "Auto (bassa in chat, normale per i lavori)", "bassa": "Bassa: veloce",
                       "media": "Media", "alta": "Alta: ragiona di più, più lenta"}


def posiziona(popup, button, finestra, margine: int = 4) -> tuple[int, int]:
    """Coordinate (x, y) dello schermo per `popup`: sopra il tasto se c'è posto, altrimenti sotto, e
    sempre dentro la finestra `finestra`. Chiamare dopo update_idletasks()."""
    larghezza, altezza = popup.winfo_reqwidth(), popup.winfo_reqheight()
    sinistra, alto = finestra.winfo_rootx(), finestra.winfo_rooty()
    destra, basso = sinistra + finestra.winfo_width(), alto + finestra.winfo_height()
    x = button.winfo_rootx()
    x = min(x, destra - larghezza - margine)          # non esce a destra
    x = max(x, sinistra + margine)                    # né a sinistra
    sopra = button.winfo_rooty() - altezza - 2
    y = sopra if sopra >= alto + margine else button.winfo_rooty() + button.winfo_height() + 2
    y = min(y, basso - altezza - margine)
    y = max(y, alto + margine)
    return int(x), int(y)


class _Tendina(MenuModelli):
    """Tendina compatta: stessa meccanica di «Online ▾» (apri/chiudi con un clic), posizione sopra il tasto."""
    titolo = ""

    def __init__(self, root, button, *, notify=None, settings_path=None, finestra=None):
        self.finestra = finestra or root
        super().__init__(root, button, open_settings=lambda: None, notify=notify,
                         settings_path=settings_path)

    def refresh_button(self):
        pass                                   # il nome del tasto è fisso («Modello ▾» / «Potenza ▾»)

    def open(self):
        popup = tk.Toplevel(self.root, bg=PANEL, highlightthickness=1, highlightbackground="#1191c6")
        popup.overrideredirect(True)
        try:
            popup.attributes("-topmost", True)
        except tk.TclError:
            pass
        self.popup = popup
        self.vars = {}
        self._fill(popup, self._settings())
        popup.update_idletasks()
        x, y = posiziona(popup, self.button, self.finestra)
        popup.geometry("+%d+%d" % (x, y))
        popup.bind("<Escape>", lambda _e: self.close())

    def _voce(self, popup, testo, scelto, command):
        tk.Button(popup, text=testo + ("   ←" if scelto else ""), command=command,
                  bg="#0b2f44" if scelto else PANEL, fg=CYAN if scelto else TEXT,
                  activebackground="#136488", activeforeground="white", anchor="w", relief="flat",
                  bd=0, padx=10, pady=3, font=("Segoe UI", 9), cursor="hand2").pack(fill="x", padx=6, pady=1)

    def _titolo(self, popup):
        tk.Label(popup, text=self.titolo, bg=PANEL, fg=TEXT, font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(fill="x", padx=10, pady=(8, 4))

    def _scegli(self, campo, valore):
        settings = self._settings()
        settings[campo] = valore
        self._save(settings)
        self.close()


class TendinaModello(_Tendina):
    titolo = "Modello online"

    def _fill(self, popup, settings):
        self._titolo(popup)
        scelto = settings.get("modello_chat", "auto")
        attivi = settings.get("attivi", [])
        if scelto not in attivi:
            scelto = "auto"                   # un servizio non più spuntato torna ad Automatico
        self._voce(popup, "Automatico (ordine della tendina Online)", scelto == "auto",
                   lambda: self._scegli("modello_chat", "auto"))
        for ident in settings["ordine"]:
            service = self.so.PER_ID[ident]
            if ident in attivi and service.gratis:
                self._voce(popup, service.nome, scelto == ident,
                           lambda i=ident: self._scegli("modello_chat", i))
        tk.Label(popup, text="La catena non cambia: prima i comandi e il modello offline;\n"
                             "qui scegli solo quale online usare dopo il tuo «sì».",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 8), justify="left", anchor="w"
                 ).pack(fill="x", padx=10, pady=(4, 8))


class TendinaPotenza(_Tendina):
    titolo = "Potenza (ragionamento)"

    def _fill(self, popup, settings):
        self._titolo(popup)
        scelto = settings.get("potenza", "auto")
        for nome in self.so.POTENZE:
            self._voce(popup, DESCRIZIONI_POTENZA[nome], scelto == nome,
                       lambda n=nome: self._scegli("potenza", n))
        tk.Label(popup, text="Vale per i servizi che la supportano\n(Gemini, OpenRouter, Groq gpt-oss, OpenAI).",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 8), justify="left", anchor="w"
                 ).pack(fill="x", padx=10, pady=(4, 8))


def crea_tasti(riga, *, prima_di=None, espandi=False):
    """Crea i due tasti nella riga della casella, alla stessa altezza (fill y). (modello, potenza)."""
    from barra_tasti import TastoBarra
    tasti = []
    for testo in ("Modello ▾", "Potenza ▾"):
        tasto = TastoBarra(riga, testo, None)
        opzioni = dict(side="left", fill="both" if espandi else "y", padx=(0, 4), expand=espandi)
        if prima_di is not None:
            opzioni["before"] = prima_di
        tasto.pack(**opzioni)
        tasti.append(tasto)
    return tuple(tasti)


def collega(root, tasti, *, notify=None, settings_path=None, finestra=None):
    """Collega le tendine ai tasti. Restituisce (tendina_modello, tendina_potenza)."""
    modello, potenza = tasti
    return (TendinaModello(root, modello, notify=notify, settings_path=settings_path, finestra=finestra),
            TendinaPotenza(root, potenza, notify=notify, settings_path=settings_path, finestra=finestra))
