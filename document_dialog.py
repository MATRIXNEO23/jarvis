"""A deterministic, no-side-effects dialog for voice-driven document closing.

This is a policy/state component only. It never types into applications, reads
or writes files, kills processes, or sends requests to GPT. A separate trusted
executor must check document identity, paths, backups, save outcomes and GUI
ownership before carrying out any operation requested by a transition.
"""
from __future__ import annotations

from dataclasses import dataclass
import re


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
        return " ".join(re.sub(r"[.,!?;:]+", " ", phrase.casefold()).split())

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

    def reply(self, phrase: str) -> DialogResponse:
        text = self._normalise(phrase)
        doc = self.document_id
        if self.phase == "awaiting_close_choice":
            if text in ("annulla", "non chiudere", "lascia aperto",
                        "lascia aperta", "torna indietro"):
                self.phase = "editing"
                return DialogResponse("cancel", "Chiusura annullata. Il documento resta aperto.", doc)
            if text in ("salva e chiudi", "salva ed esci", "salva e esci",
                        "salva", "salva e chiudilo", "salva e chiudila"):
                if self.saved_path is None:
                    self.phase = "awaiting_save_destination"
                    return DialogResponse(
                        "ask_destination",
                        "Il documento non ha ancora un nome o una posizione di salvataggio. "
                        "Scegli il file prima di salvare e chiudere.",
                        doc,
                    )
                self.phase = "executing"
                return DialogResponse("save_then_close",
                                      "Salvataggio e chiusura richiesti al gestore locale.",
                                      doc)
            if text in ("chiudi senza salvare", "esci senza salvare",
                        "non salvare", "scarta modifiche",
                        "chiudi e non salvare"):
                self.phase = "awaiting_discard_confirmation"
                return DialogResponse(
                    "ask_discard_confirmation",
                    f"Le modifiche a {self.document_name} andranno perse. "
                    "Vuoi davvero uscire senza salvare? "
                    "Di' «confermo uscita senza salvare» oppure «annulla».",
                    doc,
                )
            return DialogResponse("invalid", "Rispondi: salva e chiudi, "
                                  "chiudi senza salvare oppure annulla.", doc)

        if self.phase == "awaiting_discard_confirmation":
            if text in ("annulla", "non chiudere", "no"):
                self.phase = "editing"
                return DialogResponse("cancel", "Chiusura annullata; modifiche conservate.", doc)
            if text == "confermo uscita senza salvare":
                self.phase = "executing"
                return DialogResponse("discard_then_close",
                                      "Scarto modifiche e chiusura richiesti al gestore locale.",
                                      doc)
            return DialogResponse(
                "invalid",
                "Per non salvare devi dire «confermo uscita senza salvare», "
                "oppure «annulla».",
                doc,
            )

        if self.phase == "awaiting_save_destination":
            if text in ("annulla", "non chiudere", "no"):
                self.phase = "editing"
                return DialogResponse("cancel", "Nessun file salvato; documento ancora aperto.", doc)
            return DialogResponse(
                "ask_destination",
                "Usa la selezione del file nell'interfaccia per indicare dove salvare. "
                "Non scelgo automaticamente un percorso.",
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
