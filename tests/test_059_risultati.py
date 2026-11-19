"""059: la finestra dei risultati è un pop-up (Toplevel) dentro lo schermo, con colonne proprie per il
meteo; a fine lettura Lumi chiede «Chiudo la finestra?» (sì/no senza «Lumi»)."""
import time
import tkinter as tk
import unittest
from pathlib import Path

from file_access import ui
import lumi_comandi
import risposte

ROOT = Path(__file__).resolve().parents[1]


class PopupTest(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: %s" % exc)
        self.root.geometry("800x600+0+0")

    def tearDown(self):
        self.root.destroy()

    def meteo(self):
        from meteo.service import elenco_settimana
        giorni = [{"data": "2026-11-%02d" % (19 + i), "max": 15.0, "min": 8.0, "code": 61, "prob": 40}
                  for i in range(7)]
        return elenco_settimana("Roma", giorni)

    def test_e_un_toplevel_separato_e_dentro_lo_schermo(self):
        vista = ui.show_results(self.root, self.meteo(), lambda *a: None, lambda *a: True)
        self.root.update()
        finestra = vista.window
        self.assertIsInstance(finestra, tk.Toplevel)
        self.assertNotEqual(finestra.state(), "zoomed")
        larghezza, altezza = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.assertGreaterEqual(finestra.winfo_x(), 0)
        self.assertGreaterEqual(finestra.winfo_y(), 0)
        self.assertLessEqual(finestra.winfo_width(), larghezza)
        self.assertLessEqual(finestra.winfo_height(), altezza)

    def test_colonne_proprie_per_il_meteo(self):
        vista = ui.show_results(self.root, self.meteo(), lambda *a: None, lambda *a: True)
        titoli = [vista.tree.heading(c)["text"] for c in vista.tree["displaycolumns"]]
        self.assertEqual(titoli, ["Giorno", "Cielo", "Minima", "Massima", "Pioggia %"])
        prima = vista.tree.item("1")["values"]
        self.assertEqual(len(prima), 5)
        self.assertEqual(str(prima[4]), "40 %")

    def test_le_colonne_dei_file_tornano_dopo_il_meteo(self):
        vista = ui.show_results(self.root, self.meteo(), lambda *a: None, lambda *a: True)
        ui.show_results(self.root, {"token": "t", "items": [("File", "a.txt", "C:/a.txt")], "summary": "x"},
                        lambda *a: None, lambda *a: True)
        titoli = [vista.tree.heading(c)["text"] for c in vista.tree["displaycolumns"]]
        self.assertEqual(titoli, ["N.", "Tipo", "Nome", "Percorso"])

    def test_chiudi_i_risultati_chiude_il_popup(self):
        ui.show_results(self.root, self.meteo(), lambda *a: None, lambda *a: True)
        self.assertTrue(ui.chiudi_risultati(self.root))
        self.assertFalse(ui.chiudi_risultati(self.root))


class DomandaChiusuraTest(unittest.TestCase):
    def test_sì_chiude_senza_lumi(self):
        eseguite, dette = [], []
        lumi_comandi.register({"close_results": lambda: eseguite.append("chiuso")}, lambda: False)
        lumi_comandi.chiedi("close_results", "Chiudo la finestra?", dette.append, dette.append,
                            seconds=90, lettura="Settimana a Roma: da 8 a 15 gradi.")
        self.assertIn("LUMI > Chiudo la finestra?", dette)
        self.assertTrue(risposte.waiting())              # sì/no valgono senza dire «Lumi»
        self.assertTrue(lumi_comandi.handle_text("sì", dette.append, dette.append))
        self.assertEqual(eseguite, ["chiuso"])
        risposte.done()

    def test_no_non_chiude(self):
        eseguite = []
        lumi_comandi.register({"close_results": lambda: eseguite.append("chiuso")}, lambda: False)
        lumi_comandi.chiedi("close_results", "Chiudo la finestra?", lambda t: None, lambda t: None, seconds=90)
        lumi_comandi.handle_text("no", lambda t: None, lambda t: None)
        self.assertEqual(eseguite, [])
        risposte.done()

    def test_il_comando_chiudi_i_risultati_resta(self):
        self.assertEqual(lumi_comandi.parse("chiudi i risultati"), "close_results")

    def test_meteo_chiede_dopo_la_lettura(self):
        from meteo import runtime
        chiesto = []

        class Servizio:
            def is_enabled(self): return True
            def risposta_settimana(self, nome): return "Settimana.", {"items": [], "token": "x", "summary": ""}

        ordine = []
        runtime.register(Servizio(), lambda fn: fn(), lambda elenco: ordine.append("finestra"),
                         lambda letto: (ordine.append("domanda"), chiesto.append(letto)))
        import threading
        fatto = threading.Event()
        runtime.handle_text("meteo settimana", lambda t: None,
                            lambda t: (ordine.append("voce"), fatto.set()))
        self.assertTrue(fatto.wait(5))
        time.sleep(0.2)
        self.assertEqual(ordine, ["finestra", "voce", "domanda"])
        self.assertEqual(chiesto, ["Settimana."])

    def test_cablaggio_in_jarvis(self):
        src = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        self.assertIn('"close_results", "Chiudo la finestra?"', src)


if __name__ == "__main__":
    unittest.main()
