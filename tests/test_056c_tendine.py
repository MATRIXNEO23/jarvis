"""057: il clic su ogni tasto ▾ apre la sua tendina (prima il bind_all la richiudeva subito perché il
clic arriva dal Label dentro il tasto), il clic su ⏻ non la apre; spunte del pannello non riaccendono
servizi spenti altrove (bug E)."""
import tempfile
import tkinter as tk
import unittest
from pathlib import Path


class FakeKeys:
    def presente(self, _id):
        return False


class TendineTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk non disponibile")
        self.addCleanup(self.root.destroy)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _clic(self, widget):
        self.root.update()
        widget.event_generate("<Button-1>", x=2, y=2)
        self.root.update()

    def test_clic_su_online_e_ricerca_apre_il_menu_e_power_no(self):
        from barra_tasti import TastoBarra
        from menu_modelli import MenuModelli
        from menu_ricerca import MenuRicerca
        frame = tk.Frame(self.root)
        frame.pack()
        casi = []
        for classe, nome, kw in ((MenuModelli, "Online ▾", {}), (MenuRicerca, "Ricerca ▾", {})):
            tasto = TastoBarra(frame, nome, None, power=True)
            tasto.pack(side="left")
            menu = classe(self.root, tasto, open_settings=lambda: None, keys=FakeKeys(),
                          settings_path=Path(self.tmp.name) / (nome[:3] + ".json"), **kw)
            casi.append((tasto, menu))
        for tasto, menu in casi:
            self._clic(tasto.power)
            self.assertIsNone(menu.popup, "⏻ non deve aprire la tendina")
            self._clic(tasto.label)
            self.assertIsNotNone(menu.popup, "il clic sul tasto ▾ deve aprire la tendina")
            self._clic(tasto.label)
            self.assertIsNone(menu.popup, "un secondo clic la chiude")

    def test_tendina_modello_usa_lo_stesso_controllo(self):
        src = (Path(__file__).resolve().parents[1] / "menu_modelli.py").read_text(encoding="utf-8")
        self.assertIn('str(self.button) + "."', src)      # MenuModello e MenuRicerca ereditano da qui
        from menu_modello import MenuModello
        from menu_ricerca import MenuRicerca
        from menu_modelli import MenuModelli
        self.assertTrue(issubclass(MenuModello, MenuModelli) and issubclass(MenuRicerca, MenuModelli))


class SpunteTests(unittest.TestCase):
    def test_spunta_vecchia_non_riaccende_un_servizio_spento_altrove(self):
        import servizi_online as so

        class Var:
            def __init__(self, v):
                self.v = v

            def get(self):
                return self.v

            def set(self, v):
                self.v = v
        ordine = ["a", "mistral", "b"]
        base = {"mistral"}                                  # il pannello aveva Mistral spuntato
        vars_ = {i: Var(i in base) for i in ordine}
        # la tendina ha spento tutto; il pannello salva toccando solo «b»
        vars_["b"].set(True)
        attivi = so.unisci_attivi([], ordine, {i: v.get() for i, v in vars_.items()}, base)
        self.assertEqual(attivi, ["b"])
        so.allinea_spunte(vars_, attivi)
        self.assertFalse(vars_["mistral"].get())
        base = set(attivi)
        vars_["a"].set(True)                                # secondo salvataggio
        attivi = so.unisci_attivi(attivi, ordine, {i: v.get() for i, v in vars_.items()}, base)
        self.assertEqual(attivi, ["a", "b"])               # Mistral non è tornato


if __name__ == "__main__":
    unittest.main()
