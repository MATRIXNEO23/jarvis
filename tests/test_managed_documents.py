"""No filesystem overwrite, voice save path and owned Notepad orchestration."""
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
import ctypes
import unittest

from document_store import (
    DocumentSaveError, destination_from_voice, save_new_text, simple_filename
)
from managed_documents import ManagedDocuments
from notepad_controller import ClassicNotepadBridge, NotepadSession, NotepadUnavailable


class DestinationTests(unittest.TestCase):
    def test_italian_voice_destination(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            self.assertEqual(
                destination_from_voice("Salva sul desktop come storia di Venezia",
                                       home=home),
                home / "Desktop" / "storia di venezia.txt")
            self.assertEqual(
                destination_from_voice("in documenti chiamalo il mio racconto",
                                       home=home),
                home / "Documents" / "il mio racconto.txt")
            self.assertEqual(
                destination_from_voice("salva in download nome note",
                                       home=home),
                home / "Downloads" / "note.txt")

    def test_ambiguous_or_untrusted_voice_name(self):
        for phrase in (
            "", "salva", "storia", "sul desktop", "chiamalo ciao",
            "sul desktop e nei documenti chiamalo esempio",
            "sul desktop chiamalo ../segreti",
            "sul desktop chiamalo CON",
            "sul desktop chiamalo C:/Windows/test",
            "sul desktop chiamalo una cartella\\file",
        ):
            with self.subTest(phrase=phrase):
                self.assertIsNone(destination_from_voice(phrase))
        for invalid in ("../segreti", "NUL", "COM1", "AUX",
                        "x/y", "a\\b", "dati.json", "a" * 71):
            with self.subTest(invalid=invalid):
                with self.assertRaises(DocumentSaveError):
                    simple_filename(invalid)

    def test_create_only_and_no_overwrite(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            target = folder / "racconto.txt"
            save_new_text(target, "prima riga\nseconda riga")
            self.assertEqual(target.read_text(encoding="utf-8"),
                             "prima riga\nseconda riga")
            with self.assertRaises(DocumentSaveError):
                save_new_text(target, "nuovo contenuto che cancellerebbe il precedente")
            self.assertEqual(target.read_text(encoding="utf-8"),
                             "prima riga\nseconda riga")

    def test_reject_invalid_path_and_parent(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(DocumentSaveError):
                save_new_text(root / "manca" / "documento.txt", "testo")
            with self.assertRaises(DocumentSaveError):
                save_new_text(root / "file.json", "testo")
            with self.assertRaises(DocumentSaveError):
                save_new_text(root / "file.txt", "")


class FakeNotepadBridge:
    def __init__(self):
        self.notes = {}
        self.closed = []
        self.counter = 0
        self.fail_close = False

    def open_blank(self):
        self.counter += 1
        ident = f"jarvis-note-{self.counter}"
        note = NotepadSession(ident, 100 + self.counter,
                              200 + self.counter, 300 + self.counter, object())
        self.notes[ident] = ""
        return note

    def read(self, note):
        if note.ident not in self.notes:
            raise NotepadUnavailable("Documento già chiuso.")
        return self.notes[note.ident]

    def write(self, note, content):
        self.read(note)
        self.notes[note.ident] = content

    def close(self, note, *, discard_confirmed):
        self.read(note)
        if not discard_confirmed:
            raise AssertionError("Closing without authorization")
        if self.fail_close:
            raise NotepadUnavailable("Finestra ancora aperta.")
        self.closed.append(note.ident)
        del self.notes[note.ident]


class ManagedDocumentTests(unittest.TestCase):
    def setUp(self):
        self.backend = FakeNotepadBridge()
        self.docs = ManagedDocuments(self.backend)

    def test_new_document_is_written_and_verified(self):
        result = self.docs.compose("Questa è una prova.", "new_notepad")
        self.assertEqual(result.kind, "created")
        self.assertIsNone(self.docs.current.saved_path)
        self.assertEqual(self.backend.read(self.docs.current),
                         "Questa è una prova.")
        with self.assertRaises(NotepadUnavailable):
            self.docs.compose("Secondo file", "new_notepad")

    def test_append_preserves_manually_typed_text(self):
        self.docs.compose("Testo scritto da Jarvis.", "new_notepad")
        self.backend.notes[self.docs.current.ident] += "\nModifica manuale!"
        result = self.docs.compose("Un'altra frase.", "selected_document")
        self.assertEqual(result.kind, "appended")
        self.assertEqual(self.backend.read(self.docs.current),
                         "Testo scritto da Jarvis.\nModifica manuale!\n\nUn'altra frase.")

    def test_save_and_close_saves_actual_editor_not_stale_gpt_text(self):
        with TemporaryDirectory() as tmp:
            self.docs.compose("Testo originale GPT.", "new_notepad")
            doc_id = self.docs.current.ident
            self.backend.notes[doc_id] = "Testo modificato manualmente!"
            path = Path(tmp) / "mia nota.txt"
            result = self.docs.save_and_close(doc_id, path)
            self.assertEqual(result.kind, "saved_and_closed")
            self.assertEqual(path.read_text(encoding="utf-8"),
                             "Testo modificato manualmente!")
            self.assertIsNone(self.docs.current)
            self.assertEqual(self.backend.closed, [doc_id])

    def test_file_conflict_never_closes_notepad(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "testo.txt"
            target.write_text("contenuto preesistente", encoding="utf-8")
            self.docs.compose("testo GPT", "new_notepad")
            with self.assertRaises(DocumentSaveError):
                self.docs.save_and_close(self.docs.current.ident, target)
            self.assertEqual(target.read_text(encoding="utf-8"),
                             "contenuto preesistente")
            self.assertTrue(self.docs.current)
            self.assertFalse(self.backend.closed)

    def test_save_success_and_close_failure_never_claims_closed(self):
        with TemporaryDirectory() as tmp:
            self.docs.compose("Testo.", "new_notepad")
            path = Path(tmp) / "prova.txt"
            self.backend.fail_close = True
            result = self.docs.save_and_close(self.docs.current.ident, path)
            self.assertEqual(result.kind, "saved_but_open")
            self.assertTrue(path.is_file())
            self.assertIsNotNone(self.docs.current)
            self.backend.fail_close = False
            result = self.docs.save_and_close(self.docs.current.ident, path)
            self.assertEqual(result.kind, "saved_and_closed")
            self.assertIsNone(self.docs.current)

    def test_discard_only_own_session(self):
        self.docs.compose("non salvato", "new_notepad")
        ident = self.docs.current.ident
        with self.assertRaises(NotepadUnavailable):
            self.docs.discard_and_close("notepad-estraneo")
        self.assertTrue(self.docs.current)
        self.assertEqual(
            self.docs.discard_and_close(ident).kind, "closed_without_saving")
        self.assertEqual(self.backend.closed, [ident])

    def test_manual_close_does_not_act_on_new_session(self):
        self.docs.compose("testo", "new_notepad")
        old = self.docs.current.ident
        del self.backend.notes[old]
        self.assertTrue(self.docs.forget_if_closed())
        self.assertIsNone(self.docs.current)
        self.docs.compose("testo nuovo", "new_notepad")
        with self.assertRaises(NotepadUnavailable):
            self.docs.save_and_close(old, Path.home() / "Documents" / "x.txt")

    def test_classic_win32_signatures_use_pointer_sized_values(self):
        # A regression guard for LPARAM holding pointers to UTF-16 buffers:
        self.assertEqual(ctypes.sizeof(ctypes.c_size_t),
                         ctypes.sizeof(ctypes.c_void_p))
        self.assertEqual(ctypes.sizeof(ctypes.c_ssize_t),
                         ctypes.sizeof(ctypes.c_void_p))
        # On Windows the real control is exercised only on the Pavilion,
        # never in a CI unit test that could open a user-visible application.


if __name__ == "__main__":
    unittest.main()
