"""058 (5): finestre e pagine con tasti e campi sempre visibili a 1366x768, senza schermo intero.
Apre ogni finestra costruibile senza dipendenze e controlla che nessun widget esca dall'area
visibile o da quella scorrevole (tela con barra, testo, elenco)."""
import tempfile
import tkinter as tk
import unittest
from pathlib import Path

SCHERMO = (1366, 768)
TOLLERANZA = 2
AUTOSCORREVOLI = ("Text", "Listbox", "Treeview")


def scorrevole(widget) -> bool:
    """True se il widget sta dentro una tela con barra di scorrimento verticale."""
    parent = widget.master
    while parent is not None:
        if isinstance(parent, tk.Canvas):
            try:
                if parent.cget("yscrollcommand"):
                    return True
            except tk.TclError:
                pass
        parent = getattr(parent, "master", None)
    return False


def fuori_area(window, schermo=SCHERMO) -> list:
    """Widget visibili che escono dalla finestra o dallo schermo e non sono scorrevoli."""
    window.update()
    sinistra, alto = window.winfo_rootx(), window.winfo_rooty()
    destra = sinistra + min(window.winfo_width(), schermo[0])
    basso = alto + min(window.winfo_height(), schermo[1])
    errori = []

    def visita(widget):
        for figlio in widget.winfo_children():
            if isinstance(figlio, tk.Toplevel):
                continue
            if figlio.winfo_viewable() and figlio.winfo_width() > 2 and figlio.winfo_height() > 2:
                if not scorrevole(figlio):
                    x, y = figlio.winfo_rootx(), figlio.winfo_rooty()
                    fine_x, fine_y = x + figlio.winfo_width(), y + figlio.winfo_height()
                    if (x < sinistra - TOLLERANZA or y < alto - TOLLERANZA
                            or fine_x > destra + TOLLERANZA or fine_y > basso + TOLLERANZA):
                        errori.append("%s %s (%d,%d)-(%d,%d) fuori da (%d,%d)-(%d,%d)" % (
                            figlio.winfo_class(), figlio, x, y, fine_x, fine_y,
                            sinistra, alto, destra, basso))
            visita(figlio)

    visita(window)
    return errori


def _costruttori(root, cartella):
    from command_words_ui import CommandWordsWindow
    from local_model.memory_ui import MemoryPreferencesWindow
    from local_model.multimodel_ui_f5 import MultiModelSettingsF5Window
    from local_model.native_ui import NativeSettingsWindow
    from local_model.online_permissions_ui import OnlinePermissionsWindow
    from runtime_diagnostics_ui import ServiceDiagnosticsWindow
    base = Path(cartella)
    return {
        "Modello locale": lambda: NativeSettingsWindow(root, path=base / "native.json"),
        "Memoria del modello": lambda: MemoryPreferencesWindow(root, path=base / "memoria.json"),
        "Modelli offline": lambda: MultiModelSettingsF5Window(root),
        "Permessi online": lambda: OnlinePermissionsWindow(root, path=base / "permessi.json"),
        "Personalizzazione comandi": lambda: CommandWordsWindow(root),
        "Diagnostica servizi": lambda: ServiceDiagnosticsWindow(root, get_report=lambda: "ok"),
    }


class FinestreSenzaSchermoIntero(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Nessun display: " + str(exc))
        self.root.geometry("1366x768+0+0")

    def tearDown(self):
        self.root.destroy()

    def test_adatta_non_supera_l_area_utile_e_fissa_il_minimo(self):
        from finestra_adatta import MARGINE_X, MARGINE_Y, adatta
        win = tk.Toplevel(self.root)
        tk.Button(win, text="Salva").pack(side="bottom")
        win.geometry("1600x1000+700+500")
        win.update()
        self.assertTrue(adatta(win, SCHERMO))
        win.update()
        self.assertLessEqual(win.winfo_width(), SCHERMO[0] - MARGINE_X)
        self.assertLessEqual(win.winfo_height(), SCHERMO[1] - MARGINE_Y)
        self.assertLessEqual(win.winfo_x() + win.winfo_width(), SCHERMO[0])
        self.assertGreaterEqual(win.minsize()[0], win.winfo_reqwidth() - 1)
        self.assertFalse(adatta(win, SCHERMO))            # una sola volta
        win.destroy()

    def test_il_rilevatore_trova_un_tasto_tagliato_e_accetta_la_tela_scorrevole(self):
        win = tk.Toplevel(self.root)
        win.geometry("300x200+0+0")
        tk.Button(win, text="Salva").place(x=10, y=500)        # fuori dai 200 px della finestra
        win.update()
        self.assertTrue(fuori_area(win))
        win.destroy()
        win = tk.Toplevel(self.root)
        win.geometry("300x200+0+0")
        canvas = tk.Canvas(win)
        barra = tk.Scrollbar(win, command=canvas.yview)
        canvas.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        interno = tk.Frame(canvas)
        canvas.create_window(0, 0, window=interno, anchor="nw")
        tk.Button(interno, text="Giù in fondo", pady=400).pack()
        win.update()
        self.assertEqual(fuori_area(win), [])
        win.destroy()

    def test_ogni_finestra_costruibile_resta_dentro_a_1366x768(self):
        from finestra_adatta import adatta
        aperte, saltate, problemi = 0, [], []
        with tempfile.TemporaryDirectory() as cartella:
            for nome, crea in _costruttori(self.root, cartella).items():
                try:
                    oggetto = crea()
                except Exception as exc:                       # non costruibile senza il resto di Lumi
                    saltate.append("%s: %s" % (nome, type(exc).__name__))
                    continue
                finestra = getattr(oggetto, "window", oggetto)
                finestra.update()
                adatta(finestra, SCHERMO)
                for errore in fuori_area(finestra):
                    problemi.append(nome + ": " + errore)
                aperte += 1
                finestra.destroy()
        self.assertGreaterEqual(aperte, 3, "finestre non costruibili: %s" % saltate)
        self.assertEqual(problemi, [])


if __name__ == "__main__":
    unittest.main()
