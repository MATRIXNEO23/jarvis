"""Keep the display and PC awake while Lumi is maximized in front."""
import ctypes
from ctypes import wintypes
import sys

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002


class ForegroundPower:
    def __init__(self, root, enabled):
        self.root = root
        self.enabled = enabled
        self.active = False
        self.job = None
        if sys.platform == "win32":
            from window_chrome import _WindowApi
            self.window_api = _WindowApi()
            user = ctypes.WinDLL("user32", use_last_error=True)
            self.foreground = user.GetForegroundWindow
            self.foreground.argtypes, self.foreground.restype = [], wintypes.HWND
            self.execution_state = ctypes.WinDLL("kernel32", use_last_error=True).SetThreadExecutionState
            self.execution_state.argtypes = [wintypes.DWORD]
            self.execution_state.restype = wintypes.DWORD
        else:
            self.execution_state = None

    def _apply(self, wanted):
        if self.execution_state is None or wanted == self.active:
            return
        flags = ES_CONTINUOUS
        if wanted:
            flags |= ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        if self.execution_state(flags):
            self.active = wanted

    def start(self):
        if self.execution_state is not None and self.job is None:
            self.refresh()

    def refresh(self):
        self.job = None
        wanted = False
        if self.enabled() and self.root.winfo_ismapped():
            hwnd = self.window_api.hwnd(self.root)
            wanted = bool(hwnd and self.foreground() == hwnd and self.window_api.zoomed(hwnd))
        self._apply(wanted)
        self.job = self.root.after(500, self.refresh)

    def close(self):
        self._apply(False)
