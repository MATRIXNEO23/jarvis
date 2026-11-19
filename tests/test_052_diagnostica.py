"""052 punto 10: la diagnostica raggiunge le funzioni nuove (ricerca e modelli), senza chiavi."""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from online import servizi_online
from online import servizi_ricerca
from diagnostica_claude import server_mcp, strumenti
from local_model import scelta_modello
from local_model.native_config import NativeModelConfig


def crea():
    return strumenti.crea(navigazione=lambda: None, apri_impostazioni=lambda: None,
                          addon_manager=lambda: None, cambia_addon=lambda *a: False,
                          cervello=lambda: None, elenco_chat=lambda: None)


class DiagnosticaNuoveFunzioniTests(unittest.TestCase):
    def test_tools_are_listed_for_claude(self):
        names = {t["name"]: t["op"] for t in server_mcp.STRUMENTI}
        self.assertEqual(names["lumi_ricerca"], "ricerca")
        self.assertEqual(names["lumi_modelli"], "modelli")
        self.assertTrue({"ricerca", "modelli"} <= set(crea()))

    def test_ricerca_reports_state_and_never_the_key(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            keys = servizi_online.Chiavi(path=folder / "k.keys", protect=lambda v, e: v[::-1],
                                         ids=servizi_ricerca.PER_ID)
            keys.salva("tavily", "tvly-NONMOSTRARE")
            servizi_ricerca.salva_impostazioni({"ordine": ["tavily", "exa", "firecrawl", "linkup"],
                                                "attivi": ["tavily", "exa"]}, folder / "s.json")
            real_load = servizi_ricerca.carica_impostazioni
            with mock.patch.object(servizi_ricerca, "chiavi", lambda path=None: keys), \
                    mock.patch.object(servizi_ricerca, "carica_impostazioni",
                                      lambda path=None: real_load(folder / "s.json")):
                answer = crea()["ricerca"]({})
        self.assertTrue(answer["ok"])
        self.assertNotIn("NONMOSTRARE", repr(answer))
        by_id = {s["id"]: s for s in answer["servizi"]}
        self.assertTrue(by_id["tavily"]["pronto"])
        self.assertTrue(by_id["exa"]["spuntato"])
        self.assertFalse(by_id["exa"]["pronto"])          # niente chiave e ricerca non collegata
        self.assertEqual(by_id["linkup"]["link_chiave"], "https://app.linkup.so")

    def test_modelli_lists_what_cambia_modello_would_offer(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "uno.gguf").write_bytes(b"GGUF")
            (folder / "due.gguf").write_bytes(b"GGUF")
            config = folder / "native.json"
            NativeModelConfig(model=str(folder / "uno.gguf")).save(config)
            with mock.patch.object(scelta_modello, "_percorso_config", lambda: config):
                answer = crea()["modelli"]({})
        self.assertEqual([m["nome"] for m in answer["modelli"]], ["uno", "due"])  # 055: il modello in uso apre l'elenco
        self.assertTrue(answer["in_uso"].endswith("uno.gguf"))


if __name__ == "__main__":
    unittest.main()
