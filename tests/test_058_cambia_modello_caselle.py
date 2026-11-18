"""058 (04:50): «cambia modello» propone solo i 3 modelli delle caselle fisse."""
import unittest
from pathlib import Path

from local_model import scelta_modello as sm

ROOT = Path(__file__).resolve().parents[1]


class ProposteTests(unittest.TestCase):
    def test_tre_modelli_a_voce_con_la_domanda(self):
        righe = [(1, Path("a/Gemma-2-2b.gguf"), True), (2, Path("b/Qwen2.5-3b.gguf"), False),
                 (3, Path("c/Llama-3.gguf"), False)]
        testo, frase, per_numero = sm.proposta_caselle(righe)
        self.assertTrue(frase.startswith("1 "))
        self.assertIn(", 2 ", frase)
        self.assertIn(", 3 ", frase)
        self.assertTrue(frase.endswith(": quale carico?"))
        self.assertEqual(set(per_numero), {1, 2, 3})
        self.assertIn("(in uso)", testo)

    def test_una_casella_vuota_non_si_propone_e_i_numeri_restano_quelli_delle_caselle(self):
        righe = [(1, Path("a/Gemma.gguf"), False), (2, None, False), (3, Path("c/Llama.gguf"), True)]
        _testo, frase, per_numero = sm.proposta_caselle(righe)
        self.assertNotIn("2 ", frase.replace("Gemma-2", ""))
        self.assertEqual(set(per_numero), {1, 3})
        self.assertEqual(per_numero[3], Path("c/Llama.gguf"))

    def test_nessun_modello_nelle_caselle_rimanda_alla_pagina_modelli(self):
        _t, frase, per_numero = sm.proposta_caselle([(1, None, False), (2, None, False), (3, None, False)])
        self.assertEqual(per_numero, {})
        self.assertIn("pagina Modelli", frase)

    def test_jarvis_usa_le_caselle_e_non_l_elenco_completo(self):
        src = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        corpo = src[src.index("    def lumi_model_choose() -> None:"):src.index("    def lumi_model_restart() -> None:")]
        self.assertIn('__import__("menu_tendine").voci()', corpo)
        self.assertIn("sm.proposta_caselle(righe)", corpo)
        self.assertNotIn("elenca_modelli()", corpo)
        self.assertNotIn("show_results", corpo)                 # niente finestra con l'elenco completo
        self.assertIn("risposte", corpo)                        # la risposta 1/2/3 vale senza «Lumi»

    def test_aiuto_aggiornato(self):
        help_text = (ROOT / "local_help.py").read_text(encoding="utf-8")
        self.assertIn("caselle 1, 2 e 3", help_text)
        self.assertIn("quale carico?", help_text)


if __name__ == "__main__":
    unittest.main()
