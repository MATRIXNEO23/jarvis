"""Guard the opt-in settings entry point in Jarvis."""
import ast
from pathlib import Path
import unittest


class NativeSettingsEntryTests(unittest.TestCase):
    def test_jarvis_entry_is_explicit_and_does_not_auto_load(self):
        source = Path(__file__).resolve().parents[1] / "jarvis.py"
        text = source.read_text(encoding="utf-8")
        tree = ast.parse(text)
        self.assertIn("Configura Gemma locale...", text)
        self.assertIn("def open_native_model_settings():", text)
        self.assertIn("NativeSettingsWindow(settings_window)", text)
        self.assertNotIn("create_native_provider(", text)
        self.assertNotIn("NativeGemmaBridge(", text)


if __name__ == "__main__":
    unittest.main()
