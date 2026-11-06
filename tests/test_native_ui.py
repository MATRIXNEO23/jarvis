"""Windows Tk smoke test: settings panel must never start inference."""
import os
from pathlib import Path
import tempfile
import tkinter as tk
import unittest

from local_model.native_config import NativeModelConfig
from local_model.native_ui import NativeSettingsWindow


@unittest.skipUnless(os.name == "nt", "Windows only")
class NativeSettingsUITests(unittest.TestCase):
    def test_save_and_reload_without_activation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = tk.Tk()
            root.withdraw()
            try:
                target = Path(tmp) / "native.json"
                window = NativeSettingsWindow(root, path=target)
                window.values["context_size"].set("4096")
                window.values["max_output"].set("256")
                window.personality.insert("1.0", "Ironia secca e tono preciso.")
                window.save()
                self.assertEqual(NativeModelConfig.load(target).personality, "Ironia secca e tono preciso.")
                window.reset()
                self.assertEqual(window.personality.get("1.0", "end-1c"), "")
                self.assertEqual(NativeModelConfig.load(target).context_size, 4096)
                self.assertIn("Ricaricamento", window.status.get())
                window.window.destroy()
            finally:
                root.destroy()

    def test_invalid_value_does_not_replace_saved_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "native.json"
            NativeModelConfig().save(target)
            original = target.read_bytes()
            root = tk.Tk()
            root.withdraw()
            try:
                window = NativeSettingsWindow(root, path=target)
                window.values["threads"].set("not-a-number")
                from unittest.mock import patch
                with patch("local_model.native_ui.messagebox.showerror"):
                    window.save()
                self.assertEqual(target.read_bytes(), original)
                window.window.destroy()
            finally:
                root.destroy()


if __name__ == "__main__":
    unittest.main()
