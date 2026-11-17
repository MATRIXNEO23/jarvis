"""056b: barra in alto con tasti uniformi e icone meteo (luna con fase locale)."""
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JARVIS = (ROOT / "jarvis.py").read_text(encoding="utf-8")
HUD = (ROOT / "animated_hud.py").read_text(encoding="utf-8")


class BarraTests(unittest.TestCase):
    def test_colori_power_azzurro_acceso_arancione_spento(self):
        from barra_tasti import ARANCIONE, AZZURRO, colore_power
        self.assertEqual(colore_power(True), AZZURRO)
        self.assertEqual(colore_power(False), ARANCIONE)

    def test_ordine_e_nomi_nella_barra(self):
        self.assertIn('"Online ▾"', JARVIS)
        self.assertIn('"Ricerca ▾", lambda: None, after="online"', JARVIS)
        self.assertNotIn("Tavily ▾", JARVIS)
        self.assertIn('"✈ Telegram", lambda: None, after="memory", power=True', JARVIS)
        self.assertIn("modello_button = hud.model_toggle_button", JARVIS)
        self.assertNotIn("MODELLO ON", HUD)
        self.assertIn("TastoBarra", HUD)
        self.assertIn("SlideModalita(", HUD)

    def test_menu_modello_mostra_il_nome(self):
        src = (ROOT / "menu_modello.py").read_text(encoding="utf-8")
        self.assertIn('"Modello: "', src)


class MeteoTests(unittest.TestCase):
    def test_categorie(self):
        from meteo.service import categoria
        self.assertEqual(categoria(0), "sole")
        self.assertEqual(categoria(2), "sole_nuvola")
        self.assertEqual(categoria(3), "nuvola")
        self.assertEqual(categoria(45), "nebbia")
        self.assertEqual(categoria(63), "pioggia")
        self.assertEqual(categoria(95), "temporale")
        self.assertEqual(categoria(73), "neve")
        self.assertEqual(categoria(0, giorno=False), "luna")
        self.assertEqual(categoria(63, giorno=False), "pioggia")

    def test_fase_lunare_locale(self):
        from meteo.icone import fase_lunare
        nuova = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
        self.assertAlmostEqual(fase_lunare(nuova), 0.0, delta=0.01)
        piena = datetime(2000, 1, 21, 4, 40, tzinfo=timezone.utc)
        self.assertAlmostEqual(fase_lunare(piena), 0.5, delta=0.02)

    def test_luce_della_luna(self):
        from meteo.icone import punti_luce
        def area(pts):
            return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))) / 2
        self.assertLess(area(punti_luce(0.0, 9, 0, 0)), 0.5)                    # nuova: niente luce
        self.assertGreater(area(punti_luce(0.5, 9, 0, 0)), 200)                 # piena: disco intero
        piena = punti_luce(0.5, 9, 0, 0)
        self.assertGreater(min(x for x, _ in piena), -9.5)
        self.assertLess(min(x for x, _ in piena), -8)
        crescente = punti_luce(0.25, 9, 0, 0)
        self.assertGreaterEqual(min(x for x, _ in crescente), -0.01)    # luce a destra
        calante = punti_luce(0.75, 9, 0, 0)
        self.assertLessEqual(max(x for x, _ in calante), 0.01)          # luce a sinistra

    def test_disegna_tutte_le_icone_senza_riquadro(self):
        from meteo.icone import CATEGORIE, disegna

        class Fake:
            def __init__(self):
                self.n = 0

            def __getattr__(self, name):
                if name.startswith("create_"):
                    def fn(*a, **k):
                        self.n += 1
                        self.assertNotRect = True
                    return fn
                raise AttributeError(name)
        for cat in CATEGORIE:
            fake = Fake()
            disegna(fake, 18, 17, cat, "#46ccfa", fase=0.3)
            self.assertGreater(fake.n, 0, cat)


if __name__ == "__main__":
    unittest.main()
