"""Integrated window controls for Jarvis's Tk windows on Windows."""
import ctypes
from ctypes import wintypes
import sys
import tkinter as tk


GWL_STYLE = -16
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
GA_ROOT = 2
FRAME_CHANGED = 0x0037  # FRAMECHANGED | NOACTIVATE | NOZORDER | NOMOVE | NOSIZE


class _WindowApi:
    def __init__(self):
        user = ctypes.WinDLL("user32", use_last_error=True)

        def bind(name, result, *args):
            function = getattr(user, name)
            function.restype = result
            function.argtypes = args
            return function

        self.ancestor = bind("GetAncestor", wintypes.HWND, wintypes.HWND, wintypes.UINT)
        self.get_style = bind("GetWindowLongW", wintypes.LONG, wintypes.HWND, ctypes.c_int)
        self.set_style = bind("SetWindowLongW", wintypes.LONG,
                              wintypes.HWND, ctypes.c_int, wintypes.LONG)
        self.set_position = bind("SetWindowPos", wintypes.BOOL, wintypes.HWND,
                                 wintypes.HWND, *([ctypes.c_int] * 4), wintypes.UINT)
        self.release_capture = bind("ReleaseCapture", wintypes.BOOL)
        self.send = bind("SendMessageW", wintypes.LPARAM, wintypes.HWND,
                         wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
        self.post = bind("PostMessageW", wintypes.BOOL, wintypes.HWND,
                         wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
        self.show = bind("ShowWindow", wintypes.BOOL, wintypes.HWND, ctypes.c_int)
        self.zoomed = bind("IsZoomed", wintypes.BOOL, wintypes.HWND)

    def hwnd(self, window):
        return self.ancestor(window.winfo_id(), GA_ROOT)

    def strip_frame(self, hwnd):
        original = self.get_style(hwnd, GWL_STYLE)
        if not original:
            return False
        style = original & ~(WS_CAPTION | WS_THICKFRAME)
        if original == style:
            return True
        ctypes.set_last_error(0)
        if not self.set_style(hwnd, GWL_STYLE, style) and ctypes.get_last_error():
            return False
        if self.set_position(hwnd, None, 0, 0, 0, 0, FRAME_CHANGED):
            return True
        self.set_style(hwnd, GWL_STYLE, original)
        return False


def install_window_chrome(root):
    """Style the root and each mapped Tk toplevel in this application."""
    if sys.platform != "win32":
        return
    api = _WindowApi()

    def attach(window):
        if not window.winfo_exists() or not window.winfo_ismapped():
            return
        if window.overrideredirect() or window.grid_slaves():
            return
        hwnd = api.hwnd(window)
        if not hwnd or not api.strip_frame(hwnd):
            return
        bar = getattr(window, "_jarvis_titlebar", None)
        if bar is not None:
            bar.title_label.configure(text=window.title())
            return

        bar = tk.Frame(window, bg="#091c2b", name="jarvis_titlebar")
        window._jarvis_titlebar = bar
        children = window.pack_slaves()
        bar.pack(side="top", fill="x", **({"before": children[0]} if children else {}))

        def minimize():
            owner = window.transient()
            target = window.nametowidget(owner) if owner else window
            api.show(api.hwnd(target), 6)  # SW_MINIMIZE

        def toggle_maximize():
            handle = api.hwnd(window)
            api.show(handle, 9 if api.zoomed(handle) else 3)  # SW_RESTORE / SW_MAXIMIZE

        def close():
            api.post(api.hwnd(window), 0x0010, 0, 0)  # WM_CLOSE preserves Tk protocols

        for label, name, action in (("×", "close", close),
                                    ("□", "maximize", toggle_maximize),
                                    ("–", "minimize", minimize)):
            button = tk.Button(bar, text=label, name=name, command=action, width=4,
                               bg="#091c2b", fg="#d9f3ff", activebackground="#16415a",
                               activeforeground="#ffffff", bd=0, highlightthickness=0)
            button.pack(side="right", ipady=3)

        title = tk.Label(bar, text=window.title(), bg="#091c2b", fg="#83cce8",
                         anchor="w", padx=10)
        title.pack(side="left", fill="x", expand=True)
        bar.title_label = title

        def drag(event):
            api.release_capture()
            position = (event.x_root & 0xffff) | ((event.y_root & 0xffff) << 16)
            api.send(api.hwnd(window), 0x00A1, 2, position)  # WM_NCLBUTTONDOWN, HTCAPTION

        title.bind("<ButtonPress-1>", drag)
        bar.bind("<ButtonPress-1>", drag)

    def on_map(event):
        if isinstance(event.widget, (tk.Tk, tk.Toplevel)):
            root.after_idle(attach, event.widget)

    root.bind_all("<Map>", on_map, add="+")
