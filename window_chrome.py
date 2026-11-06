"""Integrated window controls for Jarvis's Tk windows on Windows."""
import ctypes
from ctypes import wintypes
import sys
import tkinter as tk
from tkinter import ttk


GWL_STYLE = -16
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
GA_ROOT = 2
DRAG_EDGE_HEIGHT = 10
MOVE_ONLY = 0x0015  # NOACTIVATE | NOZORDER | NOSIZE
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
        self.get_rect = bind("GetWindowRect", wintypes.BOOL, wintypes.HWND,
                             ctypes.POINTER(wintypes.RECT))
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
        if getattr(window, "_jarvis_window_buttons", None) is not None:
            return

        header = getattr(window, "_jarvis_window_header", None)
        children = window.pack_slaves()
        host = header if header is not None else window
        background = host.cget("background")
        if header is None and children:
            content = children[0]
            if isinstance(content, ttk.Widget):
                style = content.cget("style") or content.winfo_class()
                background = ttk.Style(window).lookup(style, "background") or background
            elif "background" in content.keys():
                background = content.cget("background")
            window.configure(background=background)

        buttons = tk.Frame(host, bg=background, name="jarvis_window_buttons")
        window._jarvis_window_buttons = buttons
        if header is not None:
            buttons.pack(side="right")
        else:
            buttons.pack(side="top", anchor="e", **({"before": children[0]} if children else {}))

        def minimize():
            owner = window.transient()
            target = window.nametowidget(owner) if owner else window
            api.show(api.hwnd(target), 6)  # SW_MINIMIZE

        def toggle_maximize():
            handle = api.hwnd(window)
            api.show(handle, 9 if api.zoomed(handle) else 3)  # SW_RESTORE / SW_MAXIMIZE
            buttons.nametowidget("maximize").configure(text="❐" if api.zoomed(handle) else "□")

        def close():
            # Invoke the protocol on this Tk object, even if Windows has
            # reparented or recreated the window's native wrapper.
            handler = window.protocol("WM_DELETE_WINDOW")
            if handler:
                window.tk.call(handler)
            else:
                window.destroy()

        for label, name, action in (("×", "close", close),
                                    ("□", "maximize", toggle_maximize),
                                    ("–", "minimize", minimize)):
            button = tk.Button(buttons, text=label, name=name, command=action, width=4,
                               bg=background, fg="#000000" if sum(window.winfo_rgb(background)) > 98000
                               else "#d9f3ff", activebackground="#16415a",
                               activeforeground="#ffffff", bd=0, highlightthickness=0)
            button.pack(side="right", ipady=3)

        drag_origin = None

        def start_drag(event, *, anywhere=False):
            nonlocal drag_origin
            drag_origin = None
            if not anywhere:
                on_edge = (0 <= event.y_root - window.winfo_rooty() < DRAG_EDGE_HEIGHT
                           and isinstance(event.widget, (tk.Tk, tk.Toplevel, tk.Frame,
                                                         tk.Label, tk.Canvas, ttk.Frame, ttk.Label)))
                if event.widget is not header and not on_edge:
                    return
            handle = api.hwnd(window)
            rect = wintypes.RECT()
            if handle and not api.zoomed(handle) and api.get_rect(handle, ctypes.byref(rect)):
                drag_origin = (handle, rect.left - event.x_root, rect.top - event.y_root)
                return "break"

        def move_drag(event):
            if drag_origin is None:
                return
            handle, dx, dy = drag_origin
            api.set_position(handle, None, event.x_root + dx, event.y_root + dy, 0, 0, MOVE_ONLY)
            return "break"

        def end_drag(_event):
            nonlocal drag_origin
            drag_origin = None

        window.bind("<ButtonPress-1>", start_drag, add="+")
        window.bind("<Alt-ButtonPress-1>", lambda event: start_drag(event, anywhere=True), add="+")
        window.bind("<B1-Motion>", move_drag, add="+")
        window.bind("<ButtonRelease-1>", end_drag, add="+")
        window.bind("<Unmap>", end_drag, add="+")

    def on_map(event):
        if isinstance(event.widget, (tk.Tk, tk.Toplevel)):
            root.after_idle(attach, event.widget)

    root.bind_all("<Map>", on_map, add="+")
