"""056b: ogni funzione nuova ha aiuto comandi e frasi a voce (meteo incluso)."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AiutoMeteoTests(unittest.TestCase):
    def test_aiuto_ha_sezione_meteo_con_frasi_che_il_comando_riconosce(self):
        text = (ROOT / "local_help.py").read_text(encoding="utf-8")
        self.assertIn("'Meteo':", text)
        self.assertIn("FULL_TITLES", text)
        from meteo.commands import parse_command
        for frase in ("che tempo fa a Roma", "meteo Milano", "com’è il tempo a Tokyo"):
            self.assertEqual(parse_command(frase)[0], "meteo", frase)
        self.assertIn("che tempo fa a Roma", text)
        self.assertIn("meteo Milano", text)

    def test_capacita_meteo_registrata(self):
        import json
        data = json.loads((ROOT / "meteo" / "Meteo.jaddon").read_text(encoding="utf-8"))
        self.assertEqual(data["actions"][0]["core_action"], "weather.local")

    def test_aiuto_modelli_descrive_la_pagina_unica(self):
        text = (ROOT / "local_help.py").read_text(encoding="utf-8")
        self.assertIn("MODELLI OFFLINE", text)
        self.assertNotIn("Anteprima multimodello", text)


if __name__ == "__main__":
    unittest.main()
