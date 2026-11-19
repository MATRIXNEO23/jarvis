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


class TelegramUiMoveTests(unittest.TestCase):
    """Passo 2a: le funzioni Telegram spostate leggono i valori ATTUALI di main()."""

    def test_moved_functions_use_live_values(self):
        try:
            from telegram_addon.lumi_ui import NOMI, installa
        except ImportError as exc:          # tkinter assente fuori da Windows
            self.skipTest(str(exc))
        state = {"settings": {"telegram_contacts": [{"id": 1, "enabled": True},
                                                    {"id": 2, "enabled": False}]},
                 "addon_manager": None}
        funcs = installa(lumi_contesto.Vivo(settings=lambda: state["settings"],
                                            addon_manager=lambda: state["addon_manager"]))
        self.assertEqual(sorted(funcs), sorted(NOMI))
        self.assertEqual(funcs["selected_telegram_contacts"](), [{"id": 1, "enabled": True}])
        state["settings"] = {"telegram_contacts": []}           # main cambia il valore
        self.assertEqual(funcs["selected_telegram_contacts"](), [])
        self.assertTrue(funcs["telegram_addon_enabled"]())

    def test_main_binds_every_moved_name(self):
        source = Path(__file__).resolve().parents[1].joinpath("jarvis.py").read_text(encoding="utf-8")
        root = Path(__file__).resolve().parents[1]
        modules = [root / "telegram_addon" / "lumi_ui.py", root / "local_model" / "conversazione_lumi.py",
                   *sorted((root / "lumi_parti").glob("*.py"))]
        seen = set()
        for module in modules:
            tree = ast.parse(module.read_text(encoding="utf-8"))
            nomi = [n for n in tree.body if isinstance(n, ast.Assign)
                    and getattr(n.targets[0], "id", "") == "NOMI"]
            if not nomi:
                continue
            for name in ast.literal_eval(nomi[0].value):
                self.assertNotIn("    def " + name + "(", source, name)   # niente doppioni
                self.assertIn(name, source)
                self.assertNotIn(name, seen, name)
                seen.add(name)
            installa = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                            and n.name == "installa")
            defined = {n.name for n in installa.body if isinstance(n, ast.FunctionDef)}
            self.assertEqual(defined, set(ast.literal_eval(nomi[0].value)), module.name)
