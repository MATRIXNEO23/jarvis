"""Windows integration checks for Jarvis's shared window chrome."""
import sys
import tkinter as tk
import unittest

from window_chrome import GWL_STYLE, WS_CAPTION, WS_THICKFRAME, _WindowApi, install_window_chrome


@unittest.skipUnless(sys.platform == "win32", "Requires the Windows window manager")
class WindowChromeTests(unittest.TestCase):
    def test_main_and_dialog_controls_preserve_the_close_protocol(self):
        root = tk.Tk()
        self.addCleanup(root.destroy)
        install_window_chrome(root)
        root.geometry("520x300")
        tk.Frame(root).pack(fill="both", expand=True)
        dialog = tk.Toplevel(root)
        dialog.transient(root)
        dialog.title("Impostazioni")
        tk.Frame(dialog).pack(fill="both", expand=True)
        closed = []
        dialog.protocol("WM_DELETE_WINDOW", lambda: (closed.append(True), dialog.withdraw()))
        root.update()

        api = _WindowApi()
        for window in (root, dialog):
            bar = window.nametowidget("jarvis_titlebar")
            self.assertIs(window.pack_slaves()[0], bar)
            self.assertEqual(api.get_style(api.hwnd(window), GWL_STYLE)
                             & (WS_CAPTION | WS_THICKFRAME), 0)
            self.assertEqual(set(bar.children) & {"minimize", "maximize", "close"},
                             {"minimize", "maximize", "close"})

        root.nametowidget("jarvis_titlebar.maximize").invoke()
        root.update()
        self.assertTrue(api.zoomed(api.hwnd(root)))
        root.nametowidget("jarvis_titlebar.maximize").invoke()
        root.update()
        self.assertFalse(api.zoomed(api.hwnd(root)))

        dialog.nametowidget("jarvis_titlebar.close").invoke()
        root.update()
        self.assertEqual(closed, [True])
        self.assertEqual(dialog.state(), "withdrawn")
        dialog.deiconify()
        root.update()
        self.assertEqual(len([w for w in dialog.pack_slaves()
                              if w.winfo_name() == "jarvis_titlebar"]), 1)
