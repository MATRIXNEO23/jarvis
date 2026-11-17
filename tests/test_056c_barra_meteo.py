"""056c: barra come l'anteprima approvata (ordine, ⏻ disegnato, Telegram simbolo, larghezza 1366),
icone meteo con città, temperatura e ora."""
import tkinter as tk
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUD = (ROOT / "animated_hud.py").read_text(encoding="utf-8")
JARVIS = (ROOT / "jarvis.py").read_text(encoding="utf-8")


class BarraSorgenteTests(unittest.TestCase):
    def test_ordine_mic_modello_online_ricerca_memoria_telegram(self):
        self.assertLess(HUD.index('("mic", "Mic", False)'), HUD.index('("model", "Modello ▾", True)'))
        self.assertLess(HUD.index('("model", "Modello ▾", True)'), HUD.index('("memory", "Memoria", False)'))
        self.assertIn('"Online ▾", lambda: None, after="model"', JARVIS)
        self.assertIn('"Ricerca ▾", lambda: None, after="online"', JARVIS)
        self.assertIn('"Telegram", lambda: None, after="memory", simbolo="telegram"', JARVIS)

    def test_ingranaggio_e_pulsanti_finestra_come_prima(self):
        self.assertIn('text="⚙"', HUD)
        self.assertIn("_jarvis_window_anchor=self.gear", HUD)

    def test_nome_modello_non_nella_barra(self):
        src = (ROOT / "menu_modello.py").read_text(encoding="utf-8")
        self.assertIn('text="Modello ▾"', src)
        self.assertNotIn('"Modello: "', src)

    def test_power_disegnato_non_glifo(self):
        src = (ROOT / "barra_tasti.py").read_text(encoding="utf-8")
        self.assertNotIn('text="⏻"', src)
        self.assertIn("create_arc", src)


class BarraTkTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk non disponibile")
        self.addCleanup(self.root.destroy)

    def test_colori_power_e_telegram(self):
        from barra_tasti import ARANCIONE, AZZURRO, TastoBarra
        mic = TastoBarra(self.root, "Mic", None, power=True, power_on=True)
        self.assertEqual(mic.cget("power_color"), AZZURRO)
        mic.configure(power_on=False)
        self.assertEqual(mic.cget("power_color"), ARANCIONE)
        tg = TastoBarra(self.root, "Telegram", None, simbolo="telegram")
        tg.configure(text="Telegram 3", power_color="#ff0000")
        self.assertEqual(tg.cget("power_color"), "#ff0000")
        self.assertIsNone(tg.power)

    def test_barra_tutta_nella_larghezza_a_1366(self):
        from animated_hud import JarvisHUD
        self.root.geometry("1366x768+0+0")
        hud = JarvisHUD(self.root, lambda: None)
        if not hud.frame.winfo_manager():
            hud.frame.pack(fill="both", expand=True)
        hud.add_quick_button("online", "Online ▾", lambda: None, after="model")
        hud.add_quick_button("ricerca", "Ricerca ▾", lambda: None, after="online")
        hud.add_quick_button("telegram", "Telegram", lambda: None, after="memory", simbolo="telegram")
        self.root.update_idletasks()
        header = hud.quick_controls.master
        # larghezza richiesta da tutta la barra (wordmark, slide, tasti, ingranaggio) <= 1366
        self.assertLessEqual(header.winfo_reqwidth(), 1366)
        self.assertLessEqual(hud.quick_controls.winfo_reqwidth() + hud.mode_slide.winfo_reqwidth()
                             + hud.wordmark.winfo_reqwidth() + hud.gear.winfo_reqwidth(), 1366)
        larghezza = max(self.root.winfo_width(), header.winfo_reqwidth())
        self.root.geometry("%dx768+0+0" % max(larghezza, 1366))
        self.root.update()
        larghezza = self.root.winfo_width()
        tg = hud.telegram_extra_button
        self.assertLessEqual(tg.winfo_rootx() + tg.winfo_width(), self.root.winfo_rootx() + larghezza)
        self.assertLessEqual(hud.gear.winfo_rootx() + hud.gear.winfo_width(), self.root.winfo_rootx() + larghezza)
        # l'ordine a video segue la barra approvata
        xs = [hud.mic_toggle_button.winfo_rootx(), hud.model_toggle_button.winfo_rootx(),
              hud.online_extra_button.winfo_rootx(), hud.ricerca_extra_button.winfo_rootx(),
              hud.memory_toggle_button.winfo_rootx(), tg.winfo_rootx()]
        self.assertEqual(xs, sorted(xs))
        hud.frame.destroy()


class MeteoHudTests(unittest.TestCase):
    def test_icone_tutte_le_categorie(self):
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk non disponibile")
        self.addCleanup(root.destroy)
        from meteo.icone import CATEGORIE, disegna
        for categoria in CATEGORIE:
            canvas = tk.Canvas(root, width=60, height=40)
            disegna(canvas, 20, 20, categoria)
            self.assertGreaterEqual(len(canvas.find_all()), 1, categoria)

    def test_ora_accanto_al_meteo_e_ora_sveglia_visibili(self):
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk non disponibile")
        self.addCleanup(root.destroy)
        from animated_hud import JarvisHUD
        root.geometry("1100x700+0+0")
        hud = JarvisHUD(root, lambda: None)
        if not hud.frame.winfo_manager():
            hud.frame.pack(fill="both", expand=True)
        hud.set_weather({"citta": "San Venanzo", "temp": 7.2, "categoria": "pioggia"})
        hud.set_alarm_active(True)
        root.update_idletasks()
        root.update()
        testi = [hud.weather_canvas.itemcget(i, "text") for i in hud.weather_canvas.find_all()
                 if hud.weather_canvas.type(i) == "text" and hud.weather_canvas.itemcget(i, "text").strip() != "*"]
        self.assertTrue(any("San Venanzo 7°" in t and ":" in t for t in testi), testi)
        self.assertTrue(hud.clock_row.winfo_ismapped())
        self.assertTrue(hud.alarm_stop_button.winfo_ismapped())
        hud.frame.destroy()


if __name__ == "__main__":
    unittest.main()
