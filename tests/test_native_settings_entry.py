"""Guard the opt-in settings entry point in Lumi."""
import ast
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch


class NativeSettingsEntryTests(unittest.TestCase):
    def test_jarvis_entry_apre_la_pagina_senza_finestre_e_senza_caricare_il_modello(self):
        text = (Path(__file__).resolve().parents[1] / "jarvis.py").read_text(encoding="utf-8")
        tree = ast.parse(text)
        self.assertIn("def open_native_model_settings():", text)
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        callback = next(n for n in main.body if isinstance(n, ast.FunctionDef)
                        and n.name == "open_native_model_settings")
        body = ast.unparse(callback)
        self.assertIn("settings_navigation.mostra('Modelli', 'Modelli offline')", body)
        self.assertNotIn("Toplevel", body)
        self.assertIn("embed=True", text)
        self.assertNotIn("create_native_provider(", text)
        self.assertNotIn("NativeGemmaBridge(", text)


if __name__ == "__main__":
    unittest.main()
