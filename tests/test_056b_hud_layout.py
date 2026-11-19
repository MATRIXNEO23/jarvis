"""056b: ora, sveglia, meteo, DISCO C e RETE hanno posizioni distinte dentro l'area visibile."""
import unittest
import tkinter as tk


class HudLayoutTests(unittest.TestCase):
    def test_posizioni_distinte_e_visibili(self):
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk non disponibile")
        self.addCleanup(root.destroy)
        from animated_hud import JarvisHUD
        for height in (700, 560):
            root.geometry("1100x%d+0+0" % height)
            hud = JarvisHUD(root, lambda: None)
            hud.frame.pack(fill="both", expand=True) if not hud.frame.winfo_manager() else None
            hud.set_weather({"citta": "Roma", "temp": 18.4, "categoria": "sole"})
            hud.set_alarm_active(True)
            root.update_idletasks()
            root.update()
            area = hud.visual
            top, bottom = area.winfo_rooty(), area.winfo_rooty() + area.winfo_height()
            parti = {"ora": hud.clock_row, "sveglia": hud.alarm_stop_button, "meteo": hud.weather_canvas,
                     "disco": hud.disk_tile.canvas if hasattr(hud.disk_tile, "canvas") else hud.footer,
                     "rete": hud.network_tile.canvas if hasattr(hud.network_tile, "canvas") else hud.footer}
            boxes = {}
            for name, w in parti.items():
                self.assertTrue(w.winfo_ismapped(), name)
                y0, y1 = w.winfo_rooty(), w.winfo_rooty() + w.winfo_height()
                self.assertGreaterEqual(y0, top, name)
                self.assertLessEqual(y1, bottom + 1, "%s fuori dall'area (%d)" % (name, height))
                boxes[name] = (w.winfo_rootx(), y0, w.winfo_rootx() + w.winfo_width(), y1)
            # ora e meteo non si sovrappongono (righe diverse)
            self.assertLessEqual(boxes["meteo"][3], boxes["ora"][1] + 1)
            self.assertLessEqual(boxes["meteo"][3], boxes["disco"][1] + 1)
            # disco e rete: colonne diverse
            self.assertNotEqual(boxes["disco"][0], boxes["rete"][0])
            hud.frame.destroy()


if __name__ == "__main__":
    unittest.main()
