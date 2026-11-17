"""056 C/C2: add-on Meteo (Open-Meteo), comando del motore, icone nell'HUD, aggiornamento ogni 30 min."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from addon_manager import AddonError, validate_manifest
from meteo import commands, config, runtime, service

ROOT = Path(__file__).resolve().parents[1]
JARVIS = (ROOT / "jarvis.py").read_text(encoding="utf-8")


def finto(chiamate):
    def get(url, timeout=8.0):
        chiamate.append(url)
        if "geocoding" in url:
            if "Atlantide" in url:
                return {}
            return {"results": [{"name": "Roma", "latitude": 41.89, "longitude": 12.48}]}
        return {"current_weather": {"temperature": 18.4, "weathercode": 61}}
    return get


class FrasiTests(unittest.TestCase):
    def test_frasi_di_meteo_con_e_senza_citta(self):
        self.assertEqual(commands.parse_command("che tempo fa a Roma"), ("meteo", "Roma"))
        self.assertEqual(commands.parse_command("Lumi, che tempo fa"), ("meteo", None))
        self.assertEqual(commands.parse_command("meteo Milano"), ("meteo", "Milano"))
        self.assertEqual(commands.parse_command("com'è il tempo a New York oggi"), ("meteo", "New York"))
        self.assertEqual(commands.parse_command("che tempo fa oggi"), ("meteo", None))

    def test_online_e_clima_restano_ricerche(self):
        for frase in ("cerca online meteo Roma", "com'è il clima a Tokyo in primavera",
                      "che tempo fa domani a Roma", "che ora è", "apri il meteo di roma"):
            self.assertIsNone(commands.parse_command(frase), frase)

    def test_cerca_online_meteo_arriva_prima_alla_ricerca(self):
        import lumi_comandi
        chiamate = []
        lumi_comandi.register({"ricerca": lambda s: chiamate.append(s) or True}, lambda: False)
        self.assertTrue(lumi_comandi.handle_text("cerca online meteo Roma", print, print))
        self.assertEqual(chiamate, ["cerca online meteo Roma"])


class ServizioTests(unittest.TestCase):
    def test_codici_weathercode_e_icone(self):
        casi = {0: "sole", 1: "sole", 2: "nuvola", 3: "nuvola", 45: "nuvola", 61: "pioggia", 81: "pioggia",
                71: "neve", 86: "neve", 95: "temporale", 99: "temporale"}
        for code, atteso in casi.items():
            self.assertEqual(service.categoria(code), atteso, code)

    def test_risposta_per_qualsiasi_citta_senza_chiave(self):
        chiamate = []
        svc = service.ServizioMeteo(lambda: True, get=finto(chiamate))
        self.assertEqual(svc.risposta("Roma"), "A Roma ci sono 18 gradi, pioggia.")
        self.assertTrue(all("apikey" not in u.lower() and "key" not in u.lower() for u in chiamate))
        with self.assertRaises(service.ErroreMeteo):
            svc.risposta("Atlantide")
        with self.assertRaises(service.ErroreMeteo):
            service.ServizioMeteo(lambda: True, get=finto([])).risposta()        # nessuna città predefinita

    def test_errore_di_rete_e_un_messaggio_non_un_crash(self):
        def giu(url, timeout=8.0):
            raise OSError("giù")
        with self.assertRaises(service.ErroreMeteo):
            service.ServizioMeteo(lambda: True, get=giu).risposta("Roma")

    def test_aggiornamento_al_massimo_ogni_30_minuti(self):
        chiamate, ora = [], [1000.0]
        svc = service.ServizioMeteo(lambda: True, citta=lambda: {"nome": "Roma", "lat": 1, "lon": 2},
                                    get=finto(chiamate), orologio=lambda: ora[0])
        primo = svc.aggiorna()
        self.assertEqual((primo["citta"], primo["code"]), ("Roma", 61))
        ora[0] += 29 * 60
        svc.aggiorna()
        self.assertEqual(len(chiamate), 1)             # niente rete entro 30 minuti
        ora[0] += 2 * 60
        svc.aggiorna()
        self.assertEqual(len(chiamate), 2)
        svc.aggiorna(forza=True)
        self.assertEqual(len(chiamate), 3)

    def test_spento_o_senza_citta_nessuna_rete_e_nessuna_icona(self):
        chiamate = []
        spento = service.ServizioMeteo(lambda: False, citta=lambda: {"nome": "Roma", "lat": 1, "lon": 2},
                                       get=finto(chiamate))
        self.assertIsNone(spento.aggiorna())
        senza = service.ServizioMeteo(lambda: True, citta=lambda: None, get=finto(chiamate))
        self.assertIsNone(senza.aggiorna())
        self.assertEqual(chiamate, [])


class ConfigERuntimeTests(unittest.TestCase):
    def test_citta_salvata_e_riletta_file_rovinato_e_nessuna_citta(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(config.load(tmp)["citta"])
            config.save({"nome": "Roma", "lat": 41.9, "lon": 12.5}, tmp)
            self.assertEqual(config.load(tmp)["citta"]["nome"], "Roma")
            (Path(tmp) / "config.json").write_text("{rotto", encoding="utf-8")
            self.assertIsNone(config.load(tmp)["citta"])
            (Path(tmp) / "config.json").write_text(json.dumps({"citta": {"nome": "X", "lat": 999, "lon": 0}}),
                                                   encoding="utf-8")
            self.assertIsNone(config.load(tmp)["citta"])

    def test_comando_risponde_a_voce_e_in_chat_solo_se_attivo(self):
        righe, voce = [], []
        runtime.register(service.ServizioMeteo(lambda: True, get=finto([])), lambda fn: fn())
        with mock.patch("threading.Thread") as thread:
            thread.side_effect = lambda target=None, **kw: mock.Mock(start=target)
            self.assertTrue(runtime.handle_text("che tempo fa a Roma", righe.append, voce.append))
        self.assertEqual(voce, ["A Roma ci sono 18 gradi, pioggia."])
        self.assertTrue(righe[0].startswith("METEO > "))
        runtime.register(service.ServizioMeteo(lambda: False, get=finto([])), lambda fn: fn())
        self.assertFalse(runtime.handle_text("che tempo fa a Roma", righe.append, voce.append))
        self.assertFalse(runtime.handle_text("apri il 2", righe.append, voce.append))


class PacchettoTests(unittest.TestCase):
    def test_cartella_manifesto_leggimi_e_identita(self):
        for nome in ("Meteo.jaddon", "LEGGIMI.md", "service.py", "icone.py", "ui.py", "config.py", "commands.py"):
            self.assertTrue((ROOT / "meteo" / nome).is_file(), nome)
        manifesto = json.loads((ROOT / "meteo" / "Meteo.jaddon").read_text(encoding="utf-8"))
        self.assertEqual(validate_manifest(manifesto)["id"], "meteo")
        manifesto["id"] = "altro"
        manifesto["actions"][0]["id"] = "addon.altro.consulta"
        with self.assertRaises(AddonError):
            validate_manifest(manifesto)

    def test_installato_spento_con_pagina_citta_e_icona_hud_sotto_il_globo(self):
        self.assertIn('("meteo", "meteo", "Meteo.jaddon")', JARVIS)
        self.assertNotIn('addon_manager.set_enabled("meteo"', JARVIS)        # nasce spento
        self.assertIn('"meteo": lambda box:', JARVIS)
        self.assertIn("meteo_handle_text(spoken, write_line, speak_result)", JARVIS)
        self.assertIn("root.after(30 * 60 * 1000, meteo_refresh)", JARVIS)
        hud = (ROOT / "animated_hud.py").read_text(encoding="utf-8")
        self.assertIn("canvas.pack(before=self.footer", hud)
        self.assertIn("meteo/LEGGIMI.md", (ROOT / "tools" / "build_jarvis_f5_candidate.py").read_text(encoding="utf-8"))

    def test_icone_e_hud_senza_riquadro(self):
        import tkinter as tk
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk non disponibile")
        self.addCleanup(root.destroy)
        from meteo.icone import CATEGORIE, disegna
        for categoria in CATEGORIE:
            canvas = tk.Canvas(root, width=60, height=40)
            disegna(canvas, 20, 20, categoria)
            self.assertGreater(len(canvas.find_all()), 2, categoria)
        from animated_hud import JarvisHUD
        hud = JarvisHUD(root, lambda: None)
        hud.set_weather({"citta": "Roma", "temp": 18.4, "categoria": "pioggia"})
        self.assertTrue(hud.weather_canvas.winfo_manager())
        self.assertEqual(int(hud.weather_canvas.cget("highlightthickness")), 0)
        hud.set_weather(None)
        self.assertFalse(hud.weather_canvas.winfo_manager())


if __name__ == "__main__":
    unittest.main()
