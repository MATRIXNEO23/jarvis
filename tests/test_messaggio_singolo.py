"""Il messaggio dell'utente compare una volta sola in chat (bug riferito il 15/11)."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SingleMessageTests(unittest.TestCase):
    def test_voice_message_written_once(self):
        source = (ROOT / "local_model" / "conversazione_lumi.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                  and n.name == "submit_gemma_voice")
        body = ast.get_source_segment(source, fn)
        self.assertNotIn("UTENTE / VOCE", body)        # a voce lo scrive già il microfono
        self.assertIn('if typed:\n            d.write_line("TU > " + spoken)', body)
        jarvis = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        before = jarvis.index('write_line("TU > " + spoken)')
        self.assertLess(before, jarvis.index("start_conversation_gpt(spoken)", before))


if __name__ == "__main__":
    unittest.main()


class ProjectWordTests(unittest.TestCase):
    """«passa a …» senza la parola progetto resta a finestre e programmi (15/11)."""

    def test_project_needs_the_word_progetto(self):
        from project_voice import parse_project_voice
        for text in ("progetto Alfa", "apri progetto Alfa", "Lumi, passa a progetto Alfa",
                     "torna al progetto Alfa", "riprendi il progetto Alfa"):
            command = parse_project_voice(text)
            self.assertEqual((command.action, command.name), ("open", "Alfa"), text)
        for text in ("passa a Chrome", "apri Netflix", "torna a Blocco note", "riprendi timer"):
            self.assertIsNone(parse_project_voice(text), text)
        self.assertEqual(parse_project_voice("torna alla generale").action, "general")
