"""Passo 1 della divisione di jarvis.py: il contesto comune esiste ed è creato da main()."""
import ast
import unittest
from pathlib import Path

import lumi_contesto

FIELDS = ("root", "write_line", "speak_result", "settings", "output_queue", "service",
          "workspace", "addon_manager")


class ContextTests(unittest.TestCase):
    def test_create_keeps_references_and_extra(self):
        lines = []
        ctx = lumi_contesto.crea(root="finestra", write_line=lines.append,
                                 speak_result=lambda text: None, settings={}, altro=5)
        self.assertIs(lumi_contesto.attuale(), ctx)
        ctx.write_line("ciao")
        self.assertEqual(lines, ["ciao"])
        self.assertEqual(ctx.get("altro"), 5)
        self.assertIsNone(ctx.get("manca"))

    def test_main_creates_context_after_every_reference(self):
        source = Path(__file__).resolve().parents[1].joinpath("jarvis.py").read_text(encoding="utf-8")
        main = next(n for n in ast.parse(source).body
                    if isinstance(n, ast.FunctionDef) and n.name == "main")
        call = next(n for n in ast.walk(main) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute) and n.func.attr == "crea")
        self.assertEqual(tuple(k.arg for k in call.keywords), FIELDS)
        for name in FIELDS:
            defined = [n.lineno for n in ast.walk(main)
                       if (isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, ast.Store))
                       or (isinstance(n, ast.FunctionDef) and n.name == name)]
            self.assertTrue(defined and min(defined) < call.lineno, name)


if __name__ == "__main__":
    unittest.main()
