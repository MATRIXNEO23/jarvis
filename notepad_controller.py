"""Controls ONLY a new classic Windows 10 Notepad process owned by Jarvis.

Conservative Win32 API: no global keystrokes, clipboard, generic window closing,
taskkill, arbitrary process enumeration for actions or shell. Modern Notepad
with a different control hierarchy is explicitly unsupported and left open.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import time
from uuid import uuid4


WM_CLOSE = 0x0010
WM_SETTEXT = 0x000C
WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E
EM_SETMODIFY = 0x00B9
_MAX_TEXT = 64_000
_TIMEOUT_MS = 1200


class NotepadUnavailable(OSError):
    pass


@dataclass
class NotepadSession:
    ident: str
    pid: int
    hwnd: int
    edit: int
    process: object
    saved_path: Path | None = None
    original_title: str = ""


def _class_of(user32, hwnd: int) -> str:
    name = ctypes.create_unicode_buffer(128)
    user32.GetClassNameW(wintypes.HWND(hwnd), name, len(name))
    return name.value


def _title_of(user32, hwnd: int) -> str:
    title = ctypes.create_unicode_buffer(260)
    user32.GetWindowTextW(wintypes.HWND(hwnd), title, len(title))
    return title.value.lstrip("* ").strip()


def _pid_of(user32, hwnd: int) -> int:
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(wintypes.HWND(hwnd), ctypes.byref(pid))
    return int(pid.value)


class ClassicNotepadBridge:
    def __init__(self, *, launcher=subprocess.Popen):
        self.launcher = launcher

    @staticmethod
    def _user32():
        if os.name != "nt":
            raise NotepadUnavailable("Blocco note Windows non disponibile.")
        u = ctypes.WinDLL("user32", use_last_error=True)
        u.IsWindow.argtypes = [wintypes.HWND]
        u.IsWindow.restype = wintypes.BOOL
        u.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        u.GetClassNameW.restype = ctypes.c_int
        u.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        u.GetWindowTextW.restype = ctypes.c_int
        u.IsChild.argtypes = [wintypes.HWND, wintypes.HWND]
        u.IsChild.restype = wintypes.BOOL
        u.GetWindowThreadProcessId.argtypes = [
            wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        u.GetWindowThreadProcessId.restype = wintypes.DWORD
        u.EnumWindows.argtypes = [ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, ctypes.c_ssize_t),
                                  ctypes.c_ssize_t]
        u.EnumWindows.restype = wintypes.BOOL
        u.EnumChildWindows.argtypes = [wintypes.HWND,
                                        ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, ctypes.c_ssize_t),
                                        ctypes.c_ssize_t]
        u.EnumChildWindows.restype = wintypes.BOOL
        u.SendMessageTimeoutW.argtypes = [
            wintypes.HWND, wintypes.UINT, ctypes.c_size_t, ctypes.c_ssize_t,
            wintypes.UINT, wintypes.UINT, ctypes.POINTER(ctypes.c_size_t)]
        u.SendMessageTimeoutW.restype = ctypes.c_ssize_t
        u.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT,
                                    wintypes.WPARAM, ctypes.c_ssize_t]
        u.PostMessageW.restype = wintypes.BOOL
        return u

    @staticmethod
    def _windows(user32, callback, parent: int | None = None):
        fun = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, ctypes.c_ssize_t)
        results: list[int] = []
        def cb(hwnd, _param):
            n = int(hwnd or 0)
            if n and callback(n):
                results.append(n)
            return True
        callback_ref = fun(cb)
        if parent is None:
            user32.EnumWindows(callback_ref, 0)
        else:
            user32.EnumChildWindows(wintypes.HWND(parent), callback_ref, 0)
        return results

    def _find_window(self, u, pid: int):
        options = self._windows(u, lambda hwnd: (
            _pid_of(u, hwnd) == pid and _class_of(u, hwnd) == "Notepad"))
        if len(options) != 1:
            return None
        hwnd = options[0]
        fields = self._windows(u, lambda child: (
            _pid_of(u, child) == pid and _class_of(u, child) == "Edit"), hwnd)
        if len(fields) != 1:
            return None
        return hwnd, fields[0]

    def open_blank(self) -> NotepadSession:
        u = self._user32()
        process = self.launcher(["notepad.exe"], close_fds=True, shell=False)
        deadline = time.monotonic() + 6
        while time.monotonic() < deadline:
            if process.poll() is not None:
                break
            found = self._find_window(u, process.pid)
            if found:
                hwnd, edit = found
                title = _title_of(u, hwnd)
                if not title:
                    raise NotepadUnavailable(
                        "Non riesco a identificare in sicurezza il titolo del documento.")
                return NotepadSession(uuid4().hex, process.pid, hwnd, edit,
                                      process, original_title=title)
            time.sleep(0.12)
        raise NotepadUnavailable(
            "Non riesco a controllare in sicurezza il Blocco note aperto. "
            "La finestra eventualmente avviata rimane aperta.")

    def session_state(self, note: NotepadSession) -> str:
        """Return 'closed', 'open' or 'uncertain' for the ORIGINAL owned window.

        Never infer closure merely because reading text timed out, the title
        changed (e.g. manual Save As), or the Edit control is inaccessible.
        A dead process, missing original HWND, or a reused HWND with a
        different PID unambiguously ends this tracked session. This does
        not close, read, write or select any unrelated window.
        """
        try:
            if note.process.poll() is not None:
                return "closed"
            u = self._user32()
            if not u.IsWindow(wintypes.HWND(note.hwnd)):
                return "closed"
            actual_pid = _pid_of(u, note.hwnd)
            if actual_pid and actual_pid != note.pid:
                return "closed"
            if actual_pid != note.pid:
                return "uncertain"
            if _class_of(u, note.hwnd) != "Notepad":
                return "uncertain"
            # Manual saving changes the window title, not its identity.
            # Missing/changed Edit must not be interpreted as a closed window.
            return "open"
        except (OSError, ValueError, TypeError):
            return "uncertain"

    def _verify(self, note: NotepadSession):
        u = self._user32()
        if (note.process.poll() is not None
                or not u.IsWindow(wintypes.HWND(note.hwnd))
                or not u.IsWindow(wintypes.HWND(note.edit))
                or _pid_of(u, note.hwnd) != note.pid
                or _pid_of(u, note.edit) != note.pid
                or _class_of(u, note.hwnd) != "Notepad"
                or _class_of(u, note.edit) != "Edit"
                or not u.IsChild(wintypes.HWND(note.hwnd), wintypes.HWND(note.edit))
                or _title_of(u, note.hwnd) != note.original_title):
            raise NotepadUnavailable(
                "La finestra Blocco note associata a questo documento è cambiata. "
                "Nessuna azione eseguita.")
        return u

    @staticmethod
    def _message(u, hwnd: int, code: int, wparam: int = 0, lparam: int = 0) -> int:
        value = ctypes.c_size_t(0)
        ok = u.SendMessageTimeoutW(wintypes.HWND(hwnd), code, wparam, lparam,
                                    0x0002, _TIMEOUT_MS, ctypes.byref(value))
        if not ok:
            raise NotepadUnavailable(
                "Blocco note non risponde ai messaggi Windows; operazione non eseguita.")
        return int(value.value)

    def read(self, note: NotepadSession) -> str:
        u = self._verify(note)
        length = self._message(u, note.edit, WM_GETTEXTLENGTH)
        if length > _MAX_TEXT:
            raise NotepadUnavailable("Documento troppo grande per il controllo vocale.")
        buffer = ctypes.create_unicode_buffer(length + 2)
        length_read = self._message(
            u, note.edit, WM_GETTEXT, length + 2,
            int(ctypes.cast(buffer, ctypes.c_void_p).value))
        if length_read > length + 1:
            raise NotepadUnavailable("Risposta non attendibile di Blocco note.")
        return buffer.value.replace("\r\n", "\n")

    def write(self, note: NotepadSession, text: str) -> None:
        if not isinstance(text, str) or len(text) > _MAX_TEXT or "\x00" in text:
            raise ValueError("Testo non valido o troppo lungo.")
        u = self._verify(note)
        native = ctypes.create_unicode_buffer(text.replace("\r\n", "\n").replace("\n", "\r\n"))
        ok = self._message(
            u, note.edit, WM_SETTEXT, 0,
            int(ctypes.cast(native, ctypes.c_void_p).value))
        if not ok:
            raise NotepadUnavailable("Blocco note ha rifiutato il testo.")
        if self.read(note) != text.replace("\r\n", "\n"):
            raise NotepadUnavailable("La verifica del testo inserito in Blocco note è fallita.")
        self._message(u, note.edit, EM_SETMODIFY, 1)

    def close(self, note: NotepadSession, *, discard_confirmed: bool) -> None:
        """Close only the verified owned window after policy authorization.

        Prevent a native unsaved prompt by clearing the Edit dirty bit ONLY
        after confirmed save or a separate explicit discard confirmation.
        """
        if not discard_confirmed:
            raise ValueError("La chiusura richiede un salvataggio verificato o consenso.")
        u = self._verify(note)
        self._message(u, note.edit, EM_SETMODIFY, 0)
        if not u.PostMessageW(wintypes.HWND(note.hwnd), WM_CLOSE, 0, 0):
            self._message(u, note.edit, EM_SETMODIFY, 1)
            raise NotepadUnavailable("Impossibile richiedere la chiusura del documento.")
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if not u.IsWindow(wintypes.HWND(note.hwnd)):
                return
            time.sleep(0.1)
        # If still open, never report a success; preserve the dirty bit.
        if u.IsWindow(wintypes.HWND(note.edit)):
            self._message(u, note.edit, EM_SETMODIFY, 1)
        raise NotepadUnavailable(
            "Blocco note non ha confermato la chiusura: finestra lasciata aperta.")
