"""056: lumi_stato mostra modalità e meteo; versione 056 nel workflow della build f5n."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JARVIS = (ROOT / "jarvis.py").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github" / "workflows" / "f5n-koboldcpp-native-dll-windows.yml").read_text(encoding="utf-8")


class DiagnosticaTests(unittest.TestCase):
    def test_lumi_stato_ha_modalita_e_meteo(self):
        stato = JARVIS[JARVIS.index("return Ponte("):JARVIS.index("in_chat=lambda text")]
        self.assertIn('"modalita": settings.get("modalita", "basso_consumo")', stato)
        self.assertIn('"meteo": meteo_status()', stato)
        corpo = JARVIS[JARVIS.index("def meteo_status("):JARVIS.index("def meteo_refresh(")]
        for chiave in ('"attivo"', '"citta"', '"temperatura"', '"icona"'):
            self.assertIn(chiave, corpo)

    def test_build_056_nel_workflow_e_nella_descrizione_del_server(self):
        self.assertIn("--number 056", WORKFLOW)
        self.assertIn("Lumi-056-PROVA.zip", WORKFLOW)
        server = (ROOT / "diagnostica_claude" / "server_mcp.py").read_text(encoding="utf-8")
        self.assertIn("modalità", server)
        self.assertIn("meteo", (ROOT / "diagnostica_claude" / "LEGGIMI.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
