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
from notepad_controller import ClassicNotepadBridge, NotepadSession, NotepadUnavailable


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

    def test_failed_close_restores_dirty_and_editability(self):
        for failure in ("post", "timeout", "lock", "lock_timeout", "read"):
            with self.subTest(failure=failure), OwnedEditWindow() as win:
                with TemporaryDirectory() as tmp:
                    docs = ManagedDocuments(win.bridge)
                    docs.current = win.note
                    win.bridge.write(win.note, "Da conservare")
                    original = win.bridge._message
                    injected = []

                    def fail(u, hwnd, code, wp=0, lp=0):
                        if code == 0x00CF and wp == 1:  # EM_SETREADONLY
                            injected.append("lock")
                            if failure == "lock":
                                return 0
                            value = original(u, hwnd, code, wp, lp)
                            if failure == "lock_timeout":
                                raise NotepadUnavailable("Timeout dopo lock")
                            return value
                        if failure == "read" and injected and code == 0x000E:
                            raise NotepadUnavailable("Lettura non disponibile")
                        return original(u, hwnd, code, wp, lp)

                    # Substitute failed delivery/time only; preserve real Edit APIs.
                    from contextlib import ExitStack
                    with ExitStack() as stack:
                        stack.enter_context(patch.object(
                            win.bridge, "_user32", return_value=win.u))
                        stack.enter_context(patch.object(
                            win.bridge, "_message", side_effect=fail))
                        if failure in ("post", "timeout"):
                            stack.enter_context(patch.object(
                                win.u, "PostMessageW", return_value=failure == "timeout"))
                        if failure == "timeout":
                            stack.enter_context(patch(
                                "notepad_controller.time.monotonic", side_effect=[0, 4]))
                        result = docs.save_and_close(
                            win.note.ident, Path(tmp) / "copia.txt")
                    self.assertEqual(result.kind, "saved_but_open")
                    self.assertIs(docs.current, win.note)
                    self.assertEqual(win.bridge.read(win.note), "Da conservare")
                    self.assertEqual(original(win.u, win.edit, 0x00B8), 1)  # dirty
                    original(win.u, win.edit, 0x0102, ord("!"))
                    self.assertIn("!", win.bridge.read(win.note))
                    self.assertEqual(result.saved_path.read_text(encoding="utf-8"),
                                     "Da conservare")

    def test_original_read_only_style_survives_failed_close(self):
        with OwnedEditWindow() as win, TemporaryDirectory() as tmp:
            docs = ManagedDocuments(win.bridge)
            docs.current = win.note
            win.bridge.write(win.note, "Testo protetto")
            win.bridge._message(win.u, win.edit, 0x00CF, 1)
            with patch.object(win.bridge, "_user32", return_value=win.u):
                with patch.object(win.u, "PostMessageW", return_value=False):
                    result = docs.save_and_close(win.note.ident, Path(tmp) / "nota.txt")
            self.assertEqual(result.kind, "saved_but_open")
            win.bridge._message(win.u, win.edit, 0x0102, ord("!"))
            self.assertEqual(win.bridge.read(win.note), "Testo protetto")

    def test_renamed_owned_window_is_unlocked_after_failed_close(self):
        with OwnedEditWindow() as win, TemporaryDirectory() as tmp:
            docs = ManagedDocuments(win.bridge)
            docs.current = win.note
            win.bridge.write(win.note, "Da conservare")

            def rename_instead_of_close(*_):
                title = ctypes.create_unicode_buffer("Rinominato")
                win.bridge._message(win.u, win.hwnd, 0x000C, 0,
                                    int(ctypes.cast(title, ctypes.c_void_p).value))
                return False

            with patch.object(win.bridge, "_user32", return_value=win.u):
                with patch.object(win.u, "PostMessageW", side_effect=rename_instead_of_close):
                    result = docs.save_and_close(win.note.ident, Path(tmp) / "nota.txt")
            self.assertEqual(result.kind, "saved_but_open")
            win.note.original_title = "Rinominato"  # fixture adopts its own title
            win.bridge._message(win.u, win.edit, 0x0102, ord("!"))
            self.assertIn("!", win.bridge.read(win.note))

    def test_explicit_discard_still_closes_unsaved_text(self):
        with OwnedEditWindow() as win:
            docs = ManagedDocuments(win.bridge)
            docs.current = win.note
            win.bridge.write(win.note, "Scarto autorizzato")
            self.assertEqual(docs.discard_and_close(win.note.ident).kind,
                             "closed_without_saving")
            self.assertIsNone(docs.current)
            self.assertFalse(win.u.IsWindow(wintypes.HWND(win.hwnd)))

    def test_clean_close_requires_current_text_to_match_saved_copy(self):
        with OwnedEditWindow() as win, TemporaryDirectory() as tmp:
            docs = ManagedDocuments(win.bridge)
            docs.current = win.note
            win.bridge.write(win.note, "Testo ancora non salvato")
            with self.assertRaises(NotepadUnavailable):
                docs.close_clean(win.note.ident)
            path = Path(tmp) / "nota.txt"
            docs.save_only(win.note.ident, path)
            win.bridge.write(win.note, "Modifica manuale")
            with self.assertRaises(NotepadUnavailable):
                docs.close_clean(win.note.ident)
            self.assertIs(docs.current, win.note)
            self.assertEqual(win.bridge.read(win.note), "Modifica manuale")
            self.assertEqual(path.read_text(encoding="utf-8"), "Testo ancora non salvato")
            win.bridge.write(win.note, "Testo ancora non salvato")
            self.assertEqual(docs.close_clean(win.note.ident).kind, "closed")
            self.assertIsNone(docs.current)

    def test_close_without_authorization_or_with_wrong_identity_is_rejected(self):
        from dataclasses import replace
        with OwnedEditWindow() as win:
            win.bridge.write(win.note, "Non toccare")
            with self.assertRaises(ValueError):
                win.bridge.close(win.note, discard_confirmed=False)
            foreign = replace(win.note, pid=win.note.pid + 1000)
            with self.assertRaises(NotepadUnavailable):
                win.bridge.close(foreign, discard_confirmed=True)
            self.assertEqual(win.bridge.read(win.note), "Non toccare")
            self.assertEqual(win.bridge._message(win.u, win.edit, 0x00B8), 1)

    def test_failed_second_save_preserves_both_versions_and_later_edit(self):
        with OwnedEditWindow() as win, TemporaryDirectory() as tmp:
            docs = ManagedDocuments(win.bridge)
            docs.current = win.note
            win.bridge.write(win.note, "Prima versione")
            old = Path(tmp) / "prima.txt"
            fresh = Path(tmp) / "seconda.txt"
            docs.save_only(win.note.ident, old)
            win.bridge.write(win.note, "Seconda versione")

            def save_with_edit(dest, text):
                saved = save_new_text(dest, text)
                win.bridge.write(win.note, "Terza versione ancora aperta")
                return saved

            with patch("managed_documents.save_new_text", side_effect=save_with_edit):
                result = docs.save_and_close(win.note.ident, fresh)
            self.assertEqual(result.kind, "saved_but_open")
            self.assertEqual(old.read_text(encoding="utf-8"), "Prima versione")
            self.assertEqual(fresh.read_text(encoding="utf-8"), "Seconda versione")
            self.assertEqual(win.bridge.read(win.note), "Terza versione ancora aperta")

