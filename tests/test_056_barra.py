"""056 B e D: slide Basso consumo/Veloce al posto di «INTERFACCIA NEURALE», niente «GPT ON»,
tendina MODELLO con le 3 caselle (un solo on/off, quello esistente)."""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
HUD = (ROOT / "animated_hud.py").read_text(encoding="utf-8")
JARVIS = (ROOT / "jarvis.py").read_text(encoding="utf-8")


class BarraSorgenteTests(unittest.TestCase):
    def test_slide_al_posto_della_scritta_e_niente_gpt_on(self):
        self.assertNotIn('text="//  INTERFACCIA NEURALE"', HUD)
        self.assertIn("SlideModalita(", HUD)
        self.assertNotIn('"GPT ON"', HUD)
        self.assertNotIn('("gpt", ', HUD)
        self.assertNotIn("gpt_toggle_button", HUD)

    def test_modalita_salvata_con_save_settings_e_ripristinata_se_fallisce(self):
        corpo = JARVIS[JARVIS.index("def save_mode("):JARVIS.index("hud.set_mode_handler(save_mode)")]
        self.assertIn("save_settings(settings)", corpo)
        self.assertIn('settings["modalita"] = previous', corpo)
        self.assertIn("return False", corpo)
        self.assertIn('hud.mode_slide.imposta(settings.get("modalita", "basso_consumo"))', JARVIS)

    def test_tendina_modello_accanto_al_pulsante_on_off_esistente(self):
        self.assertIn("modello_button = hud.model_toggle_button", JARVIS)
        self.assertIn('on_use=lambda target: lumi_model_use(target)', JARVIS[JARVIS.index("menu_modello"):])
        self.assertIn('after="mic"', JARVIS)        # ONLINE ▾ non dipende più dal pulsante GPT


class SlideTests(unittest.TestCase):
    def setUp(self):
        import tkinter as tk
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk non disponibile")
        self.addCleanup(self.root.destroy)

    def test_clic_cambia_modalita_e_scorre_solo_se_salva(self):
        from slide_modalita import SlideModalita
        visti = []
        slide = SlideModalita(self.root, on_change=lambda m: visti.append(m) or True)
        self.assertEqual(slide.modalita, "basso_consumo")
        slide.scegli("veloce")
        self.assertEqual((slide.modalita, visti), ("veloce", ["veloce"]))
        rifiuta = SlideModalita(self.root, on_change=lambda m: False)
        rifiuta.scegli("veloce")
        self.assertEqual(rifiuta.modalita, "basso_consumo")

    def test_imposta_non_richiama_il_salvataggio(self):
        from slide_modalita import SlideModalita
        visti = []
        slide = SlideModalita(self.root, on_change=visti.append)
        slide.imposta("veloce")
        self.assertEqual((slide.modalita, visti), ("veloce", []))


class MenuModelloTests(unittest.TestCase):
    def test_voci_sono_le_tre_caselle_con_il_modello_in_uso(self):
        import menu_modello
        from local_model import registro_modelli, scelta_modello
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.gguf", Path(tmp) / "b.gguf"
            a.write_bytes(b"x")
            b.write_bytes(b"x")
            with mock.patch.object(scelta_modello, "modello_in_uso", return_value=str(b)), \
                    mock.patch.object(scelta_modello, "elenca_modelli", return_value=[a, b]), \
                    mock.patch.object(registro_modelli, "caselle", return_value={1: a, 2: b, 3: None}):
                righe = menu_modello.voci()
        self.assertEqual([(n, in_uso) for n, _m, in_uso in righe], [(1, False), (2, True), (3, False)])

    def test_scegliere_una_casella_chiama_il_cambio_modello_esistente(self):
        import tkinter as tk
        import menu_modello
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk non disponibile")
        self.addCleanup(root.destroy)
        usati = []
        bottone = tk.Button(root)
        menu = menu_modello.MenuModello(root, bottone, on_use=usati.append, open_settings=lambda: None)
        menu._usa(Path("m.gguf"))
        menu._usa(None)
        self.assertEqual(usati, [Path("m.gguf")])


if __name__ == "__main__":
    unittest.main()
