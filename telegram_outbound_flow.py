"""Local-only Telegram contact selection and two-turn outbound voice intent.

A Telegram sender MUST be selected by numeric ID from verified contacts.
Parsing text never grants permission and never sends. No GPT parsing.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass
from collections.abc import Callable

SEND_COMMAND = re.compile(
    r"^(?:(?:ehi|ok)\s+)?(?:jarvis[,\s:]+)?"
    r"(?:manda|invia|spedisci)\s+(?:un\s+)?"
    r"(?:messaggio(?:\s+vocale)?|vocale|audio)\s+(?:a|ad)\s+"
    r"(.{2,90}?)\s*[.!?]?$", re.I
)
CONFIRM_WORDS = frozenset(("confermo", "conferma", "sì confermo", "si confermo", "invia", "manda"))
CANCEL_WORDS = frozenset(("annulla", "annullare", "non inviare", "ferma", "cancella"))


def parse_telegram_send_intent(text: str) -> str | None:
    """Return the requested name only; never interpret arbitrary free chat."""
    if not isinstance(text, str):
        return None
    cleaned = " ".join(text.strip().split())
    m = SEND_COMMAND.fullmatch(cleaned)
    return m.group(1).strip(" ,.!?") if m else None


def resolve_selected_recipient(name: str, contacts: list[dict]) -> tuple[str, dict | None]:
    """Exact full name, then unique first-name match; no first-result guesses."""
    if not isinstance(name, str) or not name.strip():
        return "missing", None
    target = " ".join(name.casefold().split())
    enabled = [c for c in contacts if type(c.get("id")) is int
               and c["id"] > 0 and c.get("enabled") is True
               and isinstance(c.get("name"), str)]
    full = [c for c in enabled if " ".join(c["name"].casefold().split()) == target]
    if len(full) == 1:
        return "ok", full[0]
    if len(full) > 1:
        return "ambiguous", None
    first = [c for c in enabled if c["name"].strip().split()
             and c["name"].strip().split()[0].casefold() == target]
    if len(first) == 1:
        return "ok", first[0]
    return ("ambiguous" if len(first) > 1 else "not_selected"), None


@dataclass(frozen=True)
class SendAction:
    kind: str
    peer_id: int = 0
    name: str = ""
    message: str = ""


class VoiceSendDialog:
    """Bounded explicit recipient -> content -> confirmation state machine."""
    def __init__(self, *, clock: Callable[[], float] = time.monotonic,
                 ttl: int = 120):
        self.clock = clock
        self.ttl = ttl
        self.reset()

    def reset(self) -> None:
        self.step = ""
        self.peer_id = 0
        self.name = ""
        self.message = ""
        self.deadline = 0.0

    @property
    def pending(self) -> bool:
        return bool(self.step)

    def _expire(self) -> bool:
        if self.step and self.clock() > self.deadline:
            self.reset()
            return True
        return False

    def begin(self, recipient: dict) -> SendAction:
        self.reset()
        self.peer_id = recipient["id"]
        self.name = recipient["name"]
        self.step = "message"
        self.deadline = self.clock() + self.ttl
        return SendAction("ask_message", self.peer_id, self.name)

    def receive(self, speech: str, selected_contacts: list[dict]) -> SendAction:
        if self._expire():
            return SendAction("expired")
        if not self.pending:
            return SendAction("not_pending")
        current = next((c for c in selected_contacts
                        if c.get("id") == self.peer_id and c.get("enabled") is True), None)
        if current is None:
            self.reset()
            return SendAction("revoked")
        text = " ".join(str(speech).split())
        word = text.casefold().strip(" .!?")
        word = re.sub(r"^(?:jarvis[,\s:]+)", "", word).strip()
        if word in CANCEL_WORDS:
            self.reset()
            return SendAction("cancelled")
        if self.step == "message":
            if not (1 <= len(text) <= 480):
                return SendAction("invalid_message", self.peer_id, self.name)
            self.message = text
            self.step = "confirm"
            self.deadline = self.clock() + self.ttl
            return SendAction("ask_confirm", self.peer_id, self.name, text)
        if word in CONFIRM_WORDS:
            result = SendAction("send", self.peer_id, self.name, self.message)
            self.reset()  # One approval only, no replay/retry.
            return result
        return SendAction("ask_confirm", self.peer_id, self.name, self.message)
