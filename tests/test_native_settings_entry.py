"""Guard the opt-in settings entry point in Lumi."""
import ast
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch


class NativeSettingsEntryTests(unittest.TestCase):
    def test_jarvis_entry_is_explicit_and_does_not_auto_load(self):
        source = Path(__file__).resolve().parents[1] / "jarvis.py"
        text = source.read_text(encoding="utf-8")
        tree = ast.parse(text)
        self.assertIn("Configura Gemma locale...", text)
        self.assertIn("def open_native_model_settings():", text)
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        callback = next(n for n in main.body if isinstance(n, ast.FunctionDef)
                        and n.name == "open_native_model_settings")
        owner = Mock()
        parent = object()
        env = {"settings_window": parent, "get_gemma_session": owner,
               "messagebox": SimpleNamespace(showerror=Mock())}
        exec(compile(ast.Module(body=[callback], type_ignores=[]), "settings-entry", "exec"), env)
        with patch("local_model.native_ui.NativeSettingsWindow") as panel:
            env["open_native_model_settings"]()
        self.assertIs(panel.call_args.args[0], parent)
        self.assertIs(panel.call_args.kwargs.get("get_session"), owner)
        owner.assert_not_called()
        self.assertNotIn("create_native_provider(", text)
        self.assertNotIn("NativeGemmaBridge(", text)


if __name__ == "__main__":
    unittest.main()
