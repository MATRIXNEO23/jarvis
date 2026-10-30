"""A deterministic, no-side-effects dialog for voice-driven document closing.

This is a policy/state component only. It never types into applications, reads
or writes files, kills processes, or sends requests to GPT. A separate trusted
executor must check document identity, paths, backups, save outcomes and GUI
ownership before carrying out any operation requested by a transition.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from document_language import classify_document_choice


@dataclass(frozen=True)
class DialogResponse:
    kind: str
    message: str
    document_id: str | None = None


class DocumentDialog:
    """A single explicitly selected document, with revocable pending choices."""

    def __init__(self) -> None:
        self.document_id: str | None = None
        self.document_name: str | None = None
        self.saved_path: str | None = None
        self.dirty = False
        self.phase = "idle"

    @staticmethod
    def _normalise(phrase: str) -> str:
        if not isinstance(phrase, str):
            return ""
        words = " ".join(re.sub(r"[.,!?;:]+", " ", phrase.casefold()).split())
        for prefix in ("ehi jarvis ", "hey jarvis ", "jarvis "):
            if words.startswith(prefix):
                words = words[len(prefix):]
                break
        return words

    def begin(self, document_id: str, document_name: str, *,
              dirty: bool, saved_path: str | None = None) -> DialogResponse:
        """Start managing a document only after the UI/executor identifies it."""
        if (self.phase != "idle" or not isinstance(document_id, str)
                or not document_id.strip() or len(document_id) > 150
                or not isinstance(document_name, str) or not document_name.strip()
                or len(document_name) > 180
                or type(dirty) is not bool
                or (saved_path is not None and
                    (not isinstance(saved_path, str) or not saved_path.strip()))):
            raise ValueError("Documento non identificabile o sessione già attiva.")
        self.document_id = document_id
        self.document_name = document_name
        self.saved_path = saved_path
        self.dirty = dirty
        self.phase = "editing"
        return DialogResponse("ready", f"Documento selezionato: {document_name}.",
                              document_id)

    def mark_dirty(self) -> None:
        if self.phase != "editing":
            raise ValueError("Modifica non consentita durante la chiusura.")
        self.dirty = True

    def request_close(self) -> DialogResponse:
        if self.phase != "editing" or self.document_id is None:
            return DialogResponse("invalid", "Nessun documento pronto da chiudere.")
        if not self.dirty:
            self.phase = "executing"
            return DialogResponse("close_clean",
                                  "Chiudo il documento senza modifiche da salvare.",
                                  self.document_id)
        self.phase = "awaiting_close_choice"
        return DialogResponse(
            "ask_choice",
            f"Per {self.document_name}: vuoi salvare e chiudere, "
            "chiudere senza salvare oppure annullare?",
            self.document_id,
        )

    def request_close_with_choice(self, phrase: str) -> DialogResponse:
        """Direct explicit instruction: 'chiudi senza salvare' is one consent.

        No GPT inference or additional password-like sentence is required.
        A standalone 'chiudi' still requests a choice.
        """
        choice = classify_document_choice(phrase, pending=False)
        if choice not in ("save", "discard"):
            return DialogResponse(
                "invalid", "Non è chiaro se vuoi salvare. "
                "Chiedimi di chiudere, poi dimmi come preferisci procedere.",
                self.document_id)
        preliminary = self.request_close()
        if preliminary.kind == "ask_choice":
            return self.reply(phrase)
        return preliminary

    def reply(self, phrase: str) -> DialogResponse:
        choice = classify_document_choice(phrase, pending=True)
        doc = self.document_id
        if self.phase == "awaiting_close_choice":
            if choice == "cancel":
                self.phase = "editing"
                return DialogResponse(
                    "cancel", "Chiusura annullata. Il documento resta aperto.", doc)
            if choice == "save":
                if self.saved_path is None:
                    self.phase = "awaiting_save_destination"
                    return DialogResponse(
                        "ask_destination",
                        "Il documento non ha ancora un nome o una posizione di salvataggio. "
                        "Dimmi dove salvarlo, per esempio: sul desktop come appunti.",
                        doc,
                    )
                self.phase = "executing"
                return DialogResponse(
                    "save_then_close", "Salvataggio e chiusura richiesti al gestore locale.",
                    doc)
            if choice == "discard":
                # Explicit 'chiudi senza salvare' is already the user's choice.
                # Never demand an arbitrary second spoken formula.
                self.phase = "executing"
                return DialogResponse(
                    "discard_then_close",
                    "Chiusura senza salvataggio richiesta esplicitamente dall'utente.",
                    doc,
                )
            return DialogResponse(
                "invalid",
                "Non ho capito se vuoi salvare o no: vuoi salvare e chiudere, "
                "uscire senza salvare oppure lasciare aperto?",
                doc,
            )

        if self.phase == "awaiting_save_destination":
            if choice == "cancel":
                self.phase = "editing"
                return DialogResponse(
                    "cancel", "Salvataggio annullato, documento ancora aperto.", doc)
            return DialogResponse(
                "ask_destination",
                "Dimmi dove salvare, per esempio 'sul desktop come appunti', "
                "oppure scegli la cartella dall'interfaccia.",
                doc,
            )

        return DialogResponse("ignored", "Nessuna conferma di chiusura in attesa.", doc)

    def provide_destination(self, path: str) -> DialogResponse:
        """Only a trusted UI-selected destination is accepted as a proposal."""
        if self.phase != "awaiting_save_destination" or not isinstance(path, str) or not path.strip():
            return DialogResponse("invalid", "Destinazione di salvataggio non valida.",
                                  self.document_id)
        # The executor MUST check target safety, permissions, conflicts and backups.
        self.phase = "executing"
        return DialogResponse("save_as_then_close",
                              "Salvataggio nella destinazione scelta e chiusura richiesti.",
                              self.document_id)

    def operation_completed(self, document_id: str, *, succeeded: bool) -> DialogResponse:
        """An executor acknowledgement, never an unverified claim of save."""
        if self.phase != "executing" or document_id != self.document_id:
            raise ValueError("Conferma esecuzione estranea al documento attivo.")
        if succeeded:
            self.reset()
            return DialogResponse("closed", "Documento chiuso.")
        self.phase = "editing"
        return DialogResponse("failed", "Operazione non riuscita; documento mantenuto aperto.",
                              document_id)

    def revoke_pending(self) -> None:
        """On GPT disconnect/mode changes; cannot resurrect an old confirmation."""
        if self.phase.startswith("awaiting_"):
            self.phase = "editing"

    def reset(self) -> None:
        """On app close, user document switch or successful close."""
        self.document_id = None
        self.document_name = None
        self.saved_path = None
        self.dirty = False
        self.phase = "idle"
