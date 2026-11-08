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
                self.assertIn("Ricaricamento", window.status.get())
                window.reset()
                self.assertEqual(window.personality.get("1.0", "end-1c"), "")
                self.assertEqual(NativeModelConfig.load(target).context_size, 4096)
                window.window.destroy()
            finally:
                root.destroy()

    def test_prompt_diagnostic_window_is_manual_and_does_not_start_model(self):
        from unittest.mock import Mock
        with tempfile.TemporaryDirectory() as tmp:
            root = tk.Tk()
            root.withdraw()
            try:
                fake = Mock()
                fake.prompt_diagnostic.return_value = (
                    "DIAGNOSTICA PROMPT GEMMA — SOLO RAM, NON SALVATA")
                window = NativeSettingsWindow(
                    root, path=Path(tmp) / "native.json",
                    get_session=lambda: fake)
                window.open_prompt_diagnostics()
                dialogs = [x for x in window.window.winfo_children()
                           if isinstance(x, tk.Toplevel)]
                self.assertEqual(len(dialogs), 1)
                dialog = dialogs[0]

                def walk(widget):
                    yield widget
                    for child in widget.winfo_children():
                        yield from walk(child)

                buttons = {item.cget("text"): item for item in walk(dialog)
                           if item.winfo_class() == "TButton"}
                fake.arm_prompt_diagnostic.assert_not_called()
                fake.prompt_diagnostic.assert_not_called()
                buttons["Acquisisci prossima domanda"].invoke()
                fake.arm_prompt_diagnostic.assert_called_once_with()
                buttons["Aggiorna"].invoke()
                fake.prompt_diagnostic.assert_called_once_with()
                text = next(x for x in walk(dialog) if isinstance(x, tk.Text))
                self.assertIn("SOLO RAM", text.get("1.0", "end"))
                buttons["Scarta"].invoke()
                fake.clear_prompt_diagnostic.assert_called_once_with()
                self.assertEqual(text.get("1.0", "end").strip(), "")
                dialog.destroy()
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
