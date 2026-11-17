"""055 A-C: una sola catena per testo e voce, niente finestra Sì/No, ricerca in chat col dominio."""
import ast
import unittest
from pathlib import Path

import servizi_ricerca as sr

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "jarvis.py").read_text(encoding="utf-8")


def _main_func(name):
    tree = ast.parse(SRC)
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    return next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == name)


def _text(name):
    return ast.get_source_segment(SRC, _main_func(name))


class Catena(unittest.TestCase):
    def test_voice_and_typed_share_chain(self):
        self.assertIn("conversation_chain(spoken, False)", _text("start_conversation_gpt"))
        gpt = _text("submit_gpt")
        self.assertIn("conversation_chain(message, True)", gpt)
        self.assertNotIn('run_gpt("typed_conversation"', gpt)
        chain = _text("conversation_chain")
        self.assertLess(chain.index("disponibili()"), chain.index("local_after_gpt("))

    def test_chain_handles_ricerca_online_typed(self):
        self.assertIn("lumi_ricerca(spoken)", _text("conversation_chain"))

    def test_no_askyesno_in_gpt_confirmation(self):
        body = _text("confirm_gpt_inference")
        self.assertNotIn("askyesno", body)
        self.assertIn("chiedi(", body)
        for action in ("gpt_consent_yes", "gpt_consent_no"):
            self.assertIn('"%s"' % action, SRC)

    def test_testo_chat_shows_domain_next_to_title(self):
        res = sr.Risultato("Sintesi", [("Titolo [x]", "https://www.esempio.it/a?b=1")], ["anteprima"])
        text = sr.testo_chat("Tavily", res)
        self.assertIn("[Titolo (x)](https://www.esempio.it/a?b=1)  (esempio.it)", text)
        self.assertEqual(sr.dominio("non un url"), "")


if __name__ == "__main__":
    unittest.main()
