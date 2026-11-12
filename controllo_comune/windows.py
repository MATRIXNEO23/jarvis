"""Finestre, mouse e tastiera di Windows con ctypes (nessuna dipendenza).

Solo funzioni dirette di Windows: elenco finestre (EnumWindows), passaggio
(SetForegroundWindow), chiusura normale (WM_CLOSE: il programma chiede da sé se
salvare), mouse e tasti (SendInput). Su altri sistemi le funzioni non fanno nulla.
"""
from __future__ import annotations

import os
import sys
import time

from . import gate

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    try:
        dwmapi = ctypes.WinDLL("dwmapi")
    except OSError:
        dwmapi = None

    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.GetWindow.argtypes = [wintypes.HWND, wintypes.UINT]
    user32.GetWindow.restype = wintypes.HWND
    user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.IsIconic.argtypes = [wintypes.HWND]
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.SetForegroundWindow.argtypes = [wintypes.HWND]
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.IsWindow.argtypes = [wintypes.HWND]
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]

    ULONG_PTR = ctypes.c_size_t

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                    ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                    ("dwExtraInfo", ULONG_PTR)]

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD),
                    ("wParamH", wintypes.WORD)]

    class _UNION(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]

    class INPUT(ctypes.Structure):
        _anonymous_ = ("u",)
        _fields_ = [("type", wintypes.DWORD), ("u", _UNION)]

    user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]

GW_OWNER = 4
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x80
WM_CLOSE = 0x0010
SW_RESTORE = 9
DWMWA_CLOAKED = 14
KEYEVENTF_KEYUP = 0x2
KEYEVENTF_UNICODE = 0x4
MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x2, 0x4
MOUSEEVENTF_WHEEL = 0x800
VK_MENU = 0x12

# Nomi dei tasti in italiano e inglese -> codice virtuale Windows.
KEYS = {
    "ctrl": 0x11, "control": 0x11, "controllo": 0x11, "alt": 0x12, "shift": 0x10,
    "maiusc": 0x10, "maiuscolo": 0x10, "win": 0x5B, "windows": 0x5B, "invio": 0x0D,
    "enter": 0x0D, "tab": 0x09, "esc": 0x1B, "escape": 0x1B, "spazio": 0x20, "space": 0x20,
    "canc": 0x2E, "cancella": 0x2E, "delete": 0x2E, "backspace": 0x08, "indietro": 0x08,
    "su": 0x26, "giu": 0x28, "sinistra": 0x25, "destra": 0x27, "home": 0x24, "inizio": 0x24,
    "fine": 0x23, "end": 0x23, "pagsu": 0x21, "paggiu": 0x22,
    **{f"f{n}": 0x6F + n for n in range(1, 13)},
    **{chr(c): ord(chr(c).upper()) for c in range(ord("a"), ord("z") + 1)},
    **{str(d): 0x30 + d for d in range(10)},
}


def _title(hwnd) -> str:
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value


def _pid(hwnd) -> int:
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def _process_name(pid: int) -> str:
    handle = kernel32.OpenProcess(0x1000, False, pid)   # QUERY_LIMITED_INFORMATION
    if not handle:
        return ""
    try:
        size = wintypes.DWORD(520)
        buffer = ctypes.create_unicode_buffer(520)
        if kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
            return os.path.basename(buffer.value)
        return ""
    finally:
        kernel32.CloseHandle(handle)


def _cloaked(hwnd) -> bool:
    if dwmapi is None:
        return False
    value = wintypes.DWORD()
    try:
        dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(value), ctypes.sizeof(value))
    except OSError:
        return False
    return bool(value.value)


def open_windows() -> list[dict]:
    """Finestre principali visibili, dalla più recente: {hwnd, title, process, pid, lumi}.
    Esclude finestre strumento e nascoste; quelle di Lumi hanno lumi=True."""
    if not IS_WINDOWS:
        return []
    own = os.getpid()
    result = []

    def callback(hwnd, _lparam):
        try:
            if (not user32.IsWindowVisible(hwnd) or user32.GetWindow(hwnd, GW_OWNER)
                    or user32.GetWindowLongW(hwnd, GWL_EXSTYLE) & WS_EX_TOOLWINDOW
                    or _cloaked(hwnd)):
                return True
            title = _title(hwnd)
            pid = _pid(hwnd)
            if not title or title == "Program Manager":
                return True
            # Lumi compare nell'elenco (richiesta utente), segnata: le azioni su di
            # lei chiedono sempre conferma.
            result.append({"hwnd": int(hwnd), "title": title[:200], "pid": pid,
                           "process": _process_name(pid), "lumi": pid == own})
        except Exception:
            pass
        return True
    user32.EnumWindows(WNDENUMPROC(callback), 0)
    return result[:60]


def exists(hwnd: int) -> bool:
    return bool(IS_WINDOWS and user32.IsWindow(hwnd))


def _send(inputs) -> None:
    array = (INPUT * len(inputs))(*inputs)
    user32.SendInput(len(inputs), array, ctypes.sizeof(INPUT))


def _key(vk, up=False):
    return INPUT(type=1, ki=KEYBDINPUT(wVk=vk, wScan=0, dwFlags=KEYEVENTF_KEYUP if up else 0,
                                       time=0, dwExtraInfo=0))


def focus(hwnd: int) -> bool:
    """Porta davanti la finestra (anche se ridotta a icona)."""
    gate.require()
    if not exists(hwnd):
        return False
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, SW_RESTORE)
    # Windows permette il cambio di primo piano dopo un tasto: un Alt «vuoto».
    _send([_key(VK_MENU), _key(VK_MENU, True)])
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.15)
    return int(user32.GetForegroundWindow() or 0) == int(hwnd)


def close(hwnd: int) -> bool:
    """Chiusura normale, come la X: se c'è da salvare lo chiede il programma."""
    gate.require()
    return bool(exists(hwnd) and user32.PostMessageW(hwnd, WM_CLOSE, 0, 0))


def window_rect(hwnd: int):
    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return None
    return rect.left, rect.top, rect.right, rect.bottom


def move_mouse(x: int, y: int, visible: bool = True) -> None:
    """Porta il puntatore su (x, y); visible: con un breve movimento visibile."""
    gate.require()
    if not IS_WINDOWS:
        return
    if visible:
        point = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(point))
        steps = 12
        for i in range(1, steps + 1):
            user32.SetCursorPos(int(point.x + (x - point.x) * i / steps),
                                int(point.y + (y - point.y) * i / steps))
            time.sleep(0.012)
    user32.SetCursorPos(int(x), int(y))


def click(x: int, y: int, visible: bool = True, double: bool = False, right: bool = False) -> None:
    if not IS_WINDOWS:
        return
    move_mouse(x, y, visible)
    down, up = (0x8, 0x10) if right else (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP)
    for _ in range(2 if double else 1):
        _send([INPUT(type=0, mi=MOUSEINPUT(0, 0, 0, down, 0, 0)),
               INPUT(type=0, mi=MOUSEINPUT(0, 0, 0, up, 0, 0))])
        time.sleep(0.05)


def type_text(text: str) -> None:
    """Scrive il testo carattere per carattere (Unicode, anche accenti)."""
    gate.require()
    gate.require()
    if not IS_WINDOWS:
        return
    inputs = []
    for char in text[:2000]:
        if char == "\n":
            inputs += [_key(0x0D), _key(0x0D, True)]
            continue
        raw = char.encode("utf-16-le")          # emoji: due unità (surrogate)
        for index in range(0, len(raw), 2):
            code = raw[index] | (raw[index + 1] << 8)
            inputs.append(INPUT(type=1, ki=KEYBDINPUT(0, code, KEYEVENTF_UNICODE, 0, 0)))
            inputs.append(INPUT(type=1, ki=KEYBDINPUT(0, code, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, 0)))
    for start in range(0, len(inputs), 200):
        _send(inputs[start:start + 200])
        time.sleep(0.01)


def press(keys: list[str]) -> bool:
    """Scorciatoia: ["ctrl", "c"] -> Ctrl+C."""
    gate.require()
    if not IS_WINDOWS:
        return False
    codes = [KEYS[k] for k in keys if k in KEYS]
    if len(codes) != len(keys) or not codes:
        return False
    _send([_key(c) for c in codes] + [_key(c, True) for c in reversed(codes)])
    return True


def scroll(clicks: int) -> None:
    """clicks > 0 su, < 0 giù (una tacca della rotella = 120)."""
    gate.require()
    if not IS_WINDOWS:
        return
    # Una tacca alla volta (alcuni programmi ignorano un salto unico grande).
    notch = ctypes.c_ulong((120 if clicks > 0 else -120) & 0xFFFFFFFF).value
    for _ in range(min(abs(int(clicks)), 30)):
        _send([INPUT(type=0, mi=MOUSEINPUT(0, 0, notch, MOUSEEVENTF_WHEEL, 0, 0))])
        time.sleep(0.03)


SW_MINIMIZE, SW_MAXIMIZE = 6, 3


def show_window(hwnd: int, how: str) -> bool:
    """how: "minimizza" | "ingrandisci" | "ripristina"."""
    gate.require()
    if not exists(hwnd):
        return False
    code = {"minimizza": SW_MINIMIZE, "ingrandisci": SW_MAXIMIZE, "ripristina": SW_RESTORE}[how]
    user32.ShowWindow(hwnd, code)
    return True


def foreground() -> int:
    """La finestra in primo piano adesso (anche se l'hai portata davanti col mouse)."""
    if not IS_WINDOWS:
        return 0
    return int(user32.GetForegroundWindow() or 0)


def screen_size():
    """Larghezza e altezza dello schermo principale."""
    if not IS_WINDOWS:
        return None
    return int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1))


def cursor():
    """Posizione attuale del puntatore."""
    if not IS_WINDOWS:
        return None
    point = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return int(point.x), int(point.y)


def kill(pid: int) -> bool:
    """Chiusura forzata (come «Termina attività»): solo dopo conferma, mai Lumi."""
    gate.require()
    if not IS_WINDOWS or not pid or int(pid) == os.getpid():
        return False
    PROCESS_TERMINATE = 0x1
    handle = kernel32.OpenProcess(PROCESS_TERMINATE, False, int(pid))
    if not handle:
        return False
    try:
        return bool(kernel32.TerminateProcess(handle, 1))
    finally:
        kernel32.CloseHandle(handle)
