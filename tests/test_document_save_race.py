"""Owned hidden Win32 Edit fixture; no installed Notepad or user files touched.

Exercises the real bridge/orchestrator and real Windows controls/messages.
The parent uses DefWindowProc rather than the installed Notepad's save dialog.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import os
from pathlib import Path
from queue import Queue
from tempfile import TemporaryDirectory
from threading import Thread
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from document_execution import run_document_worker
from document_store import save_new_text
from managed_documents import ManagedDocuments
from notepad_controller import ClassicNotepadBridge, NotepadSession


class OwnedEditWindow:
    """Test-owned hidden classic window on its own pumping UI thread."""

    def __enter__(self):
        self.ready = Queue()
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()
        result = self.ready.get(timeout=8)
        if isinstance(result, Exception):
            raise result
        self.hwnd, self.edit = result
        self.bridge = ClassicNotepadBridge()
        self.u = self.bridge._user32()
        self.note = NotepadSession(
            "test-owned", os.getpid(), self.hwnd, self.edit,
            SimpleNamespace(poll=lambda: None), original_title="Jarvis test")
        return self

    def _run(self):
        u = ctypes.WinDLL("user32", use_last_error=True)
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        proc_type = ctypes.WINFUNCTYPE(
            ctypes.c_ssize_t, wintypes.HWND, wintypes.UINT,
            wintypes.WPARAM, wintypes.LPARAM)

        class WindowClass(ctypes.Structure):
            _fields_ = [("style", wintypes.UINT), ("proc", proc_type),
                        ("class_extra", ctypes.c_int), ("window_extra", ctypes.c_int),
                        ("instance", wintypes.HINSTANCE), ("icon", wintypes.HANDLE),
                        ("cursor", wintypes.HANDLE), ("background", wintypes.HANDLE),
                        ("menu", wintypes.LPCWSTR), ("name", wintypes.LPCWSTR)]

        u.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT,
                                    wintypes.WPARAM, wintypes.LPARAM]
        u.DefWindowProcW.restype = ctypes.c_ssize_t
        u.RegisterClassW.argtypes = [ctypes.POINTER(WindowClass)]
        u.RegisterClassW.restype = wintypes.ATOM
        u.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR,
            wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, wintypes.HWND, wintypes.HMENU,
            wintypes.HINSTANCE, ctypes.c_void_p]
        u.CreateWindowExW.restype = wintypes.HWND
        u.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND,
                                 wintypes.UINT, wintypes.UINT]
        u.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
        u.DispatchMessageW.restype = ctypes.c_ssize_t
        u.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
        u.DestroyWindow.argtypes = [wintypes.HWND]
        u.UnregisterClassW.argtypes = [wintypes.LPCWSTR, wintypes.HINSTANCE]
        k.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
        k.GetModuleHandleW.restype = wintypes.HMODULE

        @proc_type
        def proc(hwnd, msg, wp, lp):
            if msg == 0x0002:  # WM_DESTROY
                u.PostQuitMessage(0)
            return u.DefWindowProcW(hwnd, msg, wp, lp)

        instance = k.GetModuleHandleW(None)
        wc = WindowClass(0, proc, 0, 0, instance, None, None, None,
                         None, "Notepad")
        atom = u.RegisterClassW(ctypes.byref(wc))
        hwnd = None
        try:
            if not atom:
                raise ctypes.WinError(ctypes.get_last_error())
            hwnd = u.CreateWindowExW(0, "Notepad", "Jarvis test", 0x00CF0000,
                                    0, 0, 300, 200, None, None, instance, None)
            edit = u.CreateWindowExW(0, "Edit", "", 0x50000044,
                                    0, 0, 280, 180, hwnd, None, instance, None)
            if not hwnd or not edit:
                raise ctypes.WinError(ctypes.get_last_error())
            self.ready.put((int(hwnd), int(edit)))
            msg = wintypes.MSG()
            while u.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                u.TranslateMessage(ctypes.byref(msg))
                u.DispatchMessageW(ctypes.byref(msg))
        except Exception as exc:
            self.ready.put(exc)
        finally:
            if hwnd:
                u.DestroyWindow(hwnd)
            if atom:
                u.UnregisterClassW("Notepad", instance)

    def __exit__(self, *_):
        if self.u.IsWindow(wintypes.HWND(self.hwnd)):
            self.u.PostMessageW(wintypes.HWND(self.hwnd), 0x0010, 0, 0)
        self.thread.join(timeout=5)
        if self.thread.is_alive():
            raise AssertionError("Test-owned window did not shut down")


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class DocumentSaveRaceTests(unittest.TestCase):
    def test_edit_during_disk_save_is_preserved_in_open_editor(self):
        with OwnedEditWindow() as win, TemporaryDirectory() as tmp:
            docs = ManagedDocuments(win.bridge)
            docs.current = win.note
            win.bridge.write(win.note, "Versione salvata")
            path = Path(tmp) / "nota.txt"

            def save_with_edit(dest, text):
                saved = save_new_text(dest, text)
                win.bridge.write(win.note, "Versione salvata\nUltime parole")
                return saved

            with patch("managed_documents.save_new_text", side_effect=save_with_edit):
                message = run_document_worker(
                    docs, "save", document_id=win.note.ident, path=path)
            self.assertEqual(message[0], "document_ok")
            self.assertEqual(message[2].kind, "saved_but_open")
            self.assertIs(docs.current, win.note)
            self.assertEqual(path.read_text(encoding="utf-8"), "Versione salvata")
            self.assertEqual(win.bridge.read(win.note),
                             "Versione salvata\nUltime parole")
            # Failure must restore typing, not leave the user's editor locked.
            win.bridge._message(win.u, win.edit, 0x0102, ord("!"))  # WM_CHAR
            self.assertIn("!", win.bridge.read(win.note))

    def test_typing_between_dirty_clear_and_close_cannot_be_lost(self):
        with OwnedEditWindow() as win, TemporaryDirectory() as tmp:
            docs = ManagedDocuments(win.bridge)
            docs.current = win.note
            win.bridge.write(win.note, "Testo completo")
            path = Path(tmp) / "nota.txt"
            original = win.bridge._message
            observed = []

            def type_at_close(u, hwnd, code, wp=0, lp=0):
                value = original(u, hwnd, code, wp, lp)
                if code == 0x00B9 and wp == 0:  # EM_SETMODIFY(false)
                    original(u, hwnd, 0x0102, ord("!"))
                    observed.append(win.bridge.read(win.note))
                return value

            with patch.object(win.bridge, "_message", side_effect=type_at_close):
                result = docs.save_and_close(win.note.ident, path)
            self.assertEqual(observed, ["Testo completo"])
            self.assertEqual(result.kind, "saved_and_closed")
            self.assertEqual(path.read_text(encoding="utf-8"), "Testo completo")
            self.assertIsNone(docs.current)

