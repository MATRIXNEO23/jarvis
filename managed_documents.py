"""Single-session safe document orchestration for classic Notepad.

GPT's document text is data. Only a Jarvis-owned verified classic Notepad
window may be edited/closed. Existing user files are never overwritten.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from document_store import save_new_text
from notepad_controller import ClassicNotepadBridge, NotepadSession, NotepadUnavailable


@dataclass(frozen=True)
class DocumentOperation:
    kind: str
    message: str
    document_id: str | None = None
    saved_path: Path | None = None


class ManagedDocuments:
    def __init__(self, bridge: ClassicNotepadBridge | None = None):
        self.bridge = bridge or ClassicNotepadBridge()
        self.current: NotepadSession | None = None

    def open_blank(self) -> DocumentOperation:
        # A manually closed owned Notepad must never block a new document.
        self.forget_if_closed()
        if self.current is not None:
            raise NotepadUnavailable(
                "C'è già un Blocco note gestito da Jarvis. "
                "Chiudilo prima di aprirne uno nuovo.")
        note = self.bridge.open_blank()
        self.current = note
        return DocumentOperation(
            "opened", "Ho aperto un nuovo Blocco note gestito da Jarvis.",
            note.ident)

    def compose(self, text: str, target: str) -> DocumentOperation:
        if not isinstance(text, str) or not text.strip() or len(text) > 4500:
            raise ValueError("Testo troppo lungo o vuoto.")
        if target == "new_notepad":
            self.forget_if_closed()
            if self.current is not None:
                raise NotepadUnavailable(
                    "Un documento di Jarvis è già aperto. Chiedi di aggiungere "
                    "il testo a quel documento oppure chiudilo prima.")
            self.open_blank()
            note = self._note()
            self.bridge.write(note, text)
            return DocumentOperation(
                "created", "Ho scritto il testo in un nuovo Blocco note. "
                "Il documento non è ancora salvato.", note.ident)
        if target == "selected_document":
            note = self._note()
            # Append instead of silently replacing existing or manually typed text.
            existing = self.bridge.read(note)
            separator = "\n\n" if existing.strip() else ""
            combined = existing + separator + text
            if len(combined) > 64_000:
                raise ValueError("Il documento non può superare i 64.000 caratteri.")
            self.bridge.write(note, combined)
            return DocumentOperation(
                "appended", "Ho aggiunto il testo nel Blocco note gestito da Jarvis. "
                "Le modifiche non sono ancora salvate.", note.ident)
        raise ValueError("Destinazione documento sconosciuta.")

    def _note(self, ident: str | None = None) -> NotepadSession:
        note = self.current
        if note is None or (ident is not None and note.ident != ident):
            raise NotepadUnavailable("Nessun documento di Jarvis corrispondente.")
        return note

    def save_only(self, ident: str, path: Path) -> DocumentOperation:
        """Save without closing the owned Notepad window; never overwrite.

        If the document changed after an earlier save, save a new version
        using the supplied fresh path. Old files remain untouched.
        """
        note=self._note(ident)
        text=self.bridge.read(note)
        dest=Path(path)
        if note.saved_path is not None and note.saved_path.is_file():
            previous=note.saved_path.read_text(encoding="utf-8")
            if previous==text:
                return DocumentOperation(
                    "saved_open","Documento già salvato in "+str(note.saved_path)
                    +". Blocco note rimane aperto.",note.ident,note.saved_path)
            if dest==note.saved_path:
                raise NotepadUnavailable(
                    "Il documento è stato modificato: serve un nuovo nome "
                    "per non sovrascrivere la versione precedente.")
        saved_path=save_new_text(dest,text)
        note.saved_path=saved_path
        return DocumentOperation(
            "saved_open","Copia del testo salvata in "+str(saved_path)
            +". Blocco note rimane aperto.",note.ident,saved_path)

    def save_and_close(self, ident: str, path: Path) -> DocumentOperation:
        note = self._note(ident)
        text = self.bridge.read(note)
        dest = Path(path)
        if note.saved_path is None:
            # New files only; no overwriting of previously existing files.
            saved_path = save_new_text(dest, text)
            note.saved_path = saved_path
        else:
            # An earlier version is immutable. An edited document can be
            # saved as a NEW file; an unchanged copy can simply be closed.
            previous=note.saved_path.read_text(encoding="utf-8")
            if previous != text:
                if note.saved_path == dest:
                    raise NotepadUnavailable(
                        "Il documento è stato modificato. Scegli un nuovo nome "
                        "per non sovrascrivere la versione precedente.")
                note.saved_path = save_new_text(dest, text)
        try:
            self.bridge.close(note, discard_confirmed=False, saved_text=text)
        except (OSError, ValueError) as exc:
            return DocumentOperation(
                "saved_but_open",
                "Una copia del testo è stata salvata in " + str(note.saved_path)
                + ". Blocco note resta aperto: " + str(exc),
                note.ident, note.saved_path)
        self.current = None
        return DocumentOperation(
            "saved_and_closed",
            "Documento salvato in " + str(note.saved_path) + " e Blocco note chiuso.",
            ident, note.saved_path)

    def discard_and_close(self, ident: str) -> DocumentOperation:
        note = self._note(ident)
        # Caller must have obtained the explicit second discard confirmation.
        self.bridge.close(note, discard_confirmed=True)
        self.current = None
        return DocumentOperation("closed_without_saving",
                                 "Blocco note chiuso senza salvare le modifiche.",
                                 ident)

    def close_clean(self, ident: str) -> DocumentOperation:
        note = self._note(ident)
        # The UI's earlier clean flag cannot authorize discarding later edits.
        if note.saved_path is None:
            raise NotepadUnavailable("Il documento non ha una copia salvata verificabile.")
        saved_text = note.saved_path.read_text(encoding="utf-8")
        self.bridge.close(note, discard_confirmed=False, saved_text=saved_text)
        self.current = None
        return DocumentOperation("closed", "Documento chiuso.", ident)

    def forget_if_closed(self) -> bool:
        """Drop only a DEFINITELY closed owned window, never a live document.

        A read failure isn't evidence of closure (Win32 timeout, a saved title,
        a temporarily unavailable Edit control). Preserve the session in such
        cases so unsaved user text can never be discarded by mistake.
        """
        note=self.current
        if note is None:
            return False
        if self.bridge.session_state(note) != "closed":
            return False
        self.current=None
        return True
