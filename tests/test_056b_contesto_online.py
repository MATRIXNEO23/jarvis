"""056b: contesto online proporzionato alla richiesta."""
import json
import unittest

import contesto_online as co

SCAMBI = [{"utente": "q%d" % i, "lia": "a%d" % i, "tipo": "chat"} for i in range(8)]
RAW = json.dumps({"breve": SCAMBI, "progress": [1], "permanente": {"related": [1]},
                  "focus": {"file_results": "x", "program_request": "y", "altro": 1}})


class ContestoOnlineTests(unittest.TestCase):
    def test_saluto_solo_ultimo_scambio(self):
        out = json.loads(co.proporziona(RAW, "ciao"))
        self.assertEqual(out, {"breve": [SCAMBI[-1]]})
        self.assertEqual(co.ULTIMO["profilo"], "minimo")
        self.assertGreater(co.ULTIMO["token_stimati"], 0)

    def test_approfondisci_fino_a_sei_scambi(self):
        out = json.loads(co.proporziona(RAW, "approfondisci il tema della Roma antica"))
        self.assertEqual(len(out["breve"]), 6)
        self.assertNotIn("file_results", out["focus"])      # allegati solo se servono
        self.assertEqual(co.ULTIMO["profilo"], "ampio")

    def test_file_nominato_tiene_la_scheda(self):
        out = json.loads(co.proporziona(RAW, "apri il file che hai trovato prima"))
        self.assertIn("file_results", out["focus"])

    def test_il_codice_scrive_i_token_nel_log_e_nella_diagnostica(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        self.assertIn("ONLINE > contesto", (root / "contesto_online.py").read_text(encoding="utf-8"))
        self.assertIn("contesto_online", (root / "jarvis.py").read_text(encoding="utf-8"))
        self.assertIn("ultimo_contesto_online", (root / "diagnostica_claude" / "strumenti.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
