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
        header = tk.Frame(root)
        header.pack(fill="x")
        root._jarvis_window_header = header
        tk.Frame(root).pack(fill="both", expand=True)
        dialog = tk.Toplevel(root)
        dialog.withdraw()
        dialog.title("Impostazioni")
        tk.Frame(dialog).pack(fill="both", expand=True)
        closed = []
        root.protocol("WM_DELETE_WINDOW", lambda: closed.append("root"))
        dialog.protocol("WM_DELETE_WINDOW", lambda: (closed.append("settings"), dialog.withdraw()))
        root.update()
        dialog.deiconify()
        root.update()

        api = _WindowApi()
        for window in (root, dialog):
            bar = window._jarvis_window_buttons
            self.assertEqual(bar.pack_info()["fill"], "none")
            self.assertTrue(all(isinstance(child, tk.Button) for child in bar.winfo_children()))
        self.assertIs(root._jarvis_window_buttons.master, header)
        for window in (root, dialog):
            self.assertEqual(api.get_style(api.hwnd(window), GWL_STYLE)
                             & (WS_CAPTION | WS_THICKFRAME), 0)
            self.assertEqual(set(window._jarvis_window_buttons.children) & {"minimize", "maximize", "close"},
                             {"minimize", "maximize", "close"})

        root._jarvis_window_buttons.nametowidget("maximize").invoke()
        root.update()
        self.assertTrue(api.zoomed(api.hwnd(root)))
        root._jarvis_window_buttons.nametowidget("maximize").invoke()
        root.update()
        self.assertFalse(api.zoomed(api.hwnd(root)))

        dialog._jarvis_window_buttons.nametowidget("close").invoke()
        root.update()
        self.assertEqual(closed, ["settings"])
        self.assertTrue(root.winfo_ismapped())
        self.assertEqual(dialog.state(), "withdrawn")
        dialog.deiconify()
        root.update()
        self.assertEqual(len([w for w in dialog.pack_slaves()
                              if w.winfo_name() == "jarvis_window_buttons"]), 1)

        child = tk.Toplevel(dialog)
        tk.Frame(child).pack(fill="both", expand=True)
        root.update()
        child._jarvis_window_buttons.nametowidget("close").invoke()
        self.assertFalse(child.winfo_exists())
        self.assertTrue(dialog.winfo_ismapped())
        self.assertTrue(root.winfo_ismapped())
        self.assertEqual(closed, ["settings"])

    def test_top_edge_moves_each_window_independently(self):
        import ctypes
        from ctypes import wintypes

        root = tk.Tk()
        self.addCleanup(root.destroy)
        install_window_chrome(root)
        root.geometry("400x250+40+40")
        settings = tk.Toplevel(root)
        settings.geometry("360x220+100+100")
        child = tk.Toplevel(settings)
        child.geometry("320x180+150+150")
        root.update()

        api = _WindowApi()

        def position(window):
            rect = wintypes.RECT()
            self.assertTrue(api.get_rect(api.hwnd(window), ctypes.byref(rect)))
            return rect.left, rect.top

        for window in (root, settings, child):
            with self.subTest(window=window):
                others = {other: position(other) for other in (root, settings, child)
                          if other is not window}
                before = position(window)
                x, y = window.winfo_rootx() + 15, window.winfo_rooty() + 3
                window.event_generate("<ButtonPress-1>", rootx=x, rooty=y)
                window.event_generate("<Motion>", state=0x0100, rootx=x+27, rooty=y+19)
                window.event_generate("<ButtonRelease-1>", rootx=x+27, rooty=y+19)
                root.update()
                self.assertEqual(position(window), (before[0]+27, before[1]+19))
                for other, previous in others.items():
                    self.assertEqual(position(other), previous)
