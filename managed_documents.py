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

    def compose(self, text: str, target: str) -> DocumentOperation:
        if not isinstance(text, str) or not text.strip() or len(text) > 4500:
            raise ValueError("Testo troppo lungo o vuoto.")
        if target == "new_notepad":
            if self.current is not None:
                raise NotepadUnavailable(
                    "Un documento di Jarvis è già aperto. Chiedi di aggiungere "
                    "il testo a quel documento oppure chiudilo prima.")
            note = self.bridge.open_blank()
            self.bridge.write(note, text)
            self.current = note
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

    def save_and_close(self, ident: str, path: Path) -> DocumentOperation:
        note = self._note(ident)
        text = self.bridge.read(note)
        dest = Path(path)
        if note.saved_path is None:
            # New files only; no overwriting of previously existing files.
            saved_path = save_new_text(dest, text)
            note.saved_path = saved_path
        else:
            if note.saved_path != dest:
                raise NotepadUnavailable(
                    "Il documento è stato salvato in una posizione diversa. "
                    "Non effettuo un secondo salvataggio automatico.")
            # Re-close without overwriting if an earlier save succeeded but
            # the Windows close failed; manual edits after save are not lost.
            if note.saved_path.read_text(encoding="utf-8") != text:
                raise NotepadUnavailable(
                    "Il documento è cambiato dopo il salvataggio precedente. "
                    "Rimane aperto; occorre scegliere come salvare le nuove modifiche.")
        try:
            self.bridge.close(note, discard_confirmed=True)
        except (OSError, ValueError) as exc:
            return DocumentOperation(
                "saved_but_open",
                "Il documento è stato salvato in " + str(note.saved_path)
                + ", ma Blocco note non si è chiuso: " + str(exc),
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
        # Only the UI's explicitly verified clean document can use this path.
        self.bridge.close(note, discard_confirmed=True)
        self.current = None
        return DocumentOperation("closed", "Documento chiuso.", ident)

    def forget_if_closed(self) -> bool:
        """Do not revive a manually closed window from an earlier voice turn."""
        note = self.current
        if note is None:
            return False
        try:
            self.bridge.read(note)
        except NotepadUnavailable:
            self.current = None
            return True
        return False
