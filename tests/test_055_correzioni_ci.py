"""055: regressioni della CI Windows (consenso GPT senza variabile condivisa, newline, chrome)."""
import ast
import tempfile
import unittest
from pathlib import Path

import window_chrome
from local_model import profili_famiglia


class CorrezioniCiTests(unittest.TestCase):
    def test_gpt_consent_epoch_lives_on_the_function_not_in_a_shared_name(self):
        tree = ast.parse(Path("jarvis.py").read_text(encoding="utf-8"))
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        names = {n.name: n for n in main.body if isinstance(n, ast.FunctionDef)}
        for fn in ("confirm_gpt_inference", "grant_gpt_voice_consent"):
            for node in ast.walk(names[fn]):
                if isinstance(node, ast.Nonlocal):
                    self.assertNotIn("gpt_voice_consent_epoch", node.names)
        self.assertIn("consent_epoch", ast.unparse(names["grant_gpt_voice_consent"]))

    def test_profile_temp_file_keeps_unix_newlines_even_on_windows(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp = profili_famiglia._scrivi_temp(Path(tmp), "profili.json", "{\n  \"a\": 1\n}")
            self.assertNotIn(b"\r", temp.read_bytes())

    def test_window_chrome_classes_are_real_types(self):
        for group in (window_chrome._FINESTRE, window_chrome._SUPERFICI):
            self.assertTrue(all(isinstance(c, type) for c in group))


if __name__ == "__main__":
    unittest.main()
