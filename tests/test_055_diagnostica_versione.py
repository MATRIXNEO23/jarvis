"""055 G-H: versione nella diagnostica e strumenti aggiornati per le nuove funzioni."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JARVIS = (ROOT / "jarvis.py").read_text(encoding="utf-8")
STRUMENTI = (ROOT / "diagnostica_claude" / "strumenti.py").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github" / "workflows" / "f5n-koboldcpp-native-dll-windows.yml").read_text(encoding="utf-8")


class VersioneTests(unittest.TestCase):
    def test_lumi_stato_and_lumi_online_show_the_version(self):
        self.assertIn('"versione": __import__("impostazioni_menu").versione()', JARVIS)
        online = STRUMENTI[STRUMENTI.index("def online"):STRUMENTI.index("def ricerca")]
        self.assertIn('"versione"', online)

    def test_build_number_is_056(self):          # 056: portato da 055
        self.assertIn("--number 058", WORKFLOW)
        self.assertNotIn("--number 055", WORKFLOW)

    def test_diagnostic_tools_cover_new_features(self):
        ricerca = STRUMENTI[STRUMENTI.index("def ricerca"):STRUMENTI.index("def modelli")]
        self.assertIn("quota_servizio", ricerca)
        modelli = STRUMENTI[STRUMENTI.index("def modelli"):STRUMENTI.index("def telegram_")]
        for word in ("caselle", "mancanti", "profilo_in_uso"):
            self.assertIn(word, modelli)


if __name__ == "__main__":
    unittest.main()
