"""Opt-in Windows dictation into one user-selected foreground text field.

No global hooks, no clipboard changes, no microphone control and no background
keyboard automation. Actual injection requires explicit dictation activation.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import os
import re
from collections.abc import Callable


def dictation_voice_action(phrase: str) -> str | None:
    """Only exact user commands change dictation; ordinary speech is data."""
    if not isinstance(phrase, str):
        return None
    words = " ".join(phrase.casefold().strip(" ,.!?").split())
    words = re.sub(r"^(?:(?:ehi|ok)\s+)?jarvis[,\s:]+", "", words)
    if words in ("attiva dettatura", "attiva dettatura vocale",
                 "inizia dettatura", "inizia dettatura vocale"):
        return "start"
    if words in ("disattiva dettatura", "disattiva dettatura vocale",
                 "interrompi dettatura", "interrompi dettatura vocale",
                 "ferma dettatura", "termina dettatura"):
        return "stop"
    return None


@dataclass(frozen=True)
class FocusedWindow:
    window: int
    focus: int
    pid: int
    password_field: bool = False


class _GUIThreadInfo(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("flags", wintypes.DWORD),
                ("hwndActive", wintypes.HWND), ("hwndFocus", wintypes.HWND),
                ("hwndCapture", wintypes.HWND), ("hwndMenuOwner", wintypes.HWND),
                ("hwndMoveSize", wintypes.HWND), ("hwndCaret", wintypes.HWND),
                ("rcCaret", wintypes.RECT)]


def foreground_editor() -> FocusedWindow | None:
    """Discover foreground window and native focused control; no focus stealing."""
    if os.name != "nt":
        return None
    user32 = ctypes.windll.user32
    hwnd = int(user32.GetForegroundWindow() or 0)
    if not hwnd:
        return None
    pid = wintypes.DWORD(0)
    thread_id = user32.GetWindowThreadProcessId(wintypes.HWND(hwnd), ctypes.byref(pid))
    if not thread_id:
        return None
    info = _GUIThreadInfo()
    info.cbSize = ctypes.sizeof(info)
    if not user32.GetGUIThreadInfo(thread_id, ctypes.byref(info)):
        return None
    focus = int(info.hwndFocus or 0)
    if not focus:
        return None
    class_name = ctypes.create_unicode_buffer(100)
    user32.GetClassNameW(wintypes.HWND(focus), class_name, 100)
    native_password = False
    if class_name.value.casefold() == "edit":
        # ES_PASSWORD protects conventional native input fields. Web DOM
        # password inputs are not introspectable by this API.
        style = user32.GetWindowLongW(wintypes.HWND(focus), -16)
        native_password = bool(style & 0x20)
    return FocusedWindow(hwnd, focus, int(pid.value), native_password)


class _KeybdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_uint16), ("wScan", ctypes.c_uint16),
                ("dwFlags", ctypes.c_uint32), ("time", ctypes.c_uint32),
                ("dwExtraInfo", ctypes.c_size_t)]


class _InputUnion(ctypes.Union):
    _fields_ = [("ki", _KeybdInput)]


class _Input(ctypes.Structure):
    _anonymous_ = ("union",)
    _fields_ = [("type", ctypes.c_uint32), ("union", _InputUnion)]


def send_unicode_text(text: str) -> None:
    """Send user-dictated Unicode keystrokes; never use shell or clipboard."""
    if os.name != "nt":
        raise OSError("Dettatura disponibile solo su Windows.")
    user32 = ctypes.windll.user32
    user32.SendInput.argtypes = [ctypes.c_uint32, ctypes.POINTER(_Input), ctypes.c_int]
    user32.SendInput.restype = ctypes.c_uint32
    # For newlines use real Return; other characters via KEYEVENTF_UNICODE.
    for char in text:
        units = [0] if char == "\n" else [
            int.from_bytes(char.encode("utf-16-le")[i:i + 2], "little")
            for i in range(0, len(char.encode("utf-16-le")), 2)
        ]
        keys: list[_Input] = []
        for unit in units:
            for up in (False, True):
                if char == "\n":
                    key = _KeybdInput(0x0D, 0, 0x0002 if up else 0, 0, 0)
                else:
                    key = _KeybdInput(0, unit, 0x0004 | (0x0002 if up else 0), 0, 0)
                keys.append(_Input(1, _InputUnion(ki=key)))
        arr = (_Input * len(keys))(*keys)
        sent = user32.SendInput(len(keys), arr, ctypes.sizeof(_Input))
        if sent != len(keys):
            raise OSError("Windows non ha accettato l'inserimento del testo.")


class DesktopDictation:
    """Arms only on user request; binds to a single foreground focused control."""

    def __init__(self, *, app_pid: int | None = None, windows: bool | None = None,
                 focus_provider: Callable[[], FocusedWindow | None] = foreground_editor,
                 sender: Callable[[str], None] = send_unicode_text):
        self.app_pid = os.getpid() if app_pid is None else app_pid
        self.windows = (os.name == "nt") if windows is None else windows
        self.focus_provider = focus_provider
        self.sender = sender
        self.enabled = False
        self.target: FocusedWindow | None = None

    def _eligible(self, found: FocusedWindow | None) -> bool:
        return bool(found and found.window and found.focus
                    and found.pid != self.app_pid and not found.password_field)

    def enable(self) -> str:
        if not self.windows:
            return "Dettatura disponibile solo su Windows."
        self.enabled = True
        current = self.focus_provider()
        self.target = current if self._eligible(current) else None
        if self.target:
            return "Dettatura attiva nella finestra selezionata. Parla per scrivere."
        return ("Dettatura pronta: clicca nel campo di testo di un altro programma "
                "e inizia a parlare.")

    def disable(self) -> str:
        self.enabled = False
        self.target = None
        return "Dettatura disattivata. La modalità del microfono non è cambiata."

    def insert(self, phrase: str) -> str:
        if not self.enabled:
            return "Dettatura non attiva."
        if not isinstance(phrase, str) or not phrase.strip():
            return "Nessun testo riconosciuto."
        speech = phrase.strip()
        if len(speech) > 300 or any(ord(ch) < 32 for ch in speech):
            return "Testo troppo lungo o non valido; non inserito."
        current = self.focus_provider()
        if not self._eligible(current):
            return "Nessun campo di testo esterno valido; testo non inserito."
        if self.target is None:
            self.target = current
        if (current.window, current.focus, current.pid) != (
                self.target.window, self.target.focus, self.target.pid):
            return ("La finestra o il campo selezionato è cambiato: dettatura sospesa. "
                    "Di' 'Jarvis, disattiva dettatura', poi riattivala nella nuova finestra.")
        rendered = "\n" if speech in ("a capo", "vai a capo", "nuova riga") else speech + " "
        # Revalidate immediately before input (the user may switch windows).
        fresh = self.focus_provider()
        if fresh != current:
            return "Il campo di testo ha perso il focus: nulla è stato scritto."
        try:
            self.sender(rendered)
        except (OSError, ValueError):
            return "Windows non ha inserito il testo; controlla la finestra selezionata."
        return "Dettatura inserita nel campo selezionato."
