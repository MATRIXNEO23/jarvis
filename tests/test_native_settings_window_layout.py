"""028: Salva / Prova generazione sempre visibili nella finestra del modello locale
(la 026 aveva allungato il modulo e su uno schermo da 768 px i pulsanti uscivano)."""
import tempfile
import tkinter as tk
import unittest
from pathlib import Path


def find_buttons(widget, found):
    for child in widget.winfo_children():
        try:
            text = child.cget("text")
        except tk.TclError:
            text = ""
        if text in ("Salva", "Prova generazione"):
            found[text] = child
        find_buttons(child, found)
    return found


class SettingsWindowLayoutTests(unittest.TestCase):
    def test_save_and_test_buttons_are_inside_the_visible_window(self):
        try:
            root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Nessun display: " + str(exc))
        root.withdraw()
        try:
            from local_model.native_ui import NativeSettingsWindow
            with tempfile.TemporaryDirectory() as folder:
                panel = NativeSettingsWindow(root, path=Path(folder) / "native.json")
                panel.window.geometry("640x420")       # schermo piccolo
                panel.window.update()
                buttons = find_buttons(panel.window, {})
                self.assertEqual(set(buttons), {"Salva", "Prova generazione"})
                bottom = panel.window.winfo_rooty() + panel.window.winfo_height()
                for button in buttons.values():
                    self.assertTrue(button.winfo_ismapped())
                    self.assertLessEqual(button.winfo_rooty() + button.winfo_height(), bottom + 1)
                panel.window.destroy()
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
