"""Small, ephemeral voice-dialogue memory for Jarvis's GPT conversation mode.

This is contextual recall, not an authority store, command queue, knowledge base
or persistent profile. Only the last few completed user/assistant exchanges are
kept in process memory. No file, SQLite, telemetry, network or cloud storage.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import json
import re

MAX_TURNS = 16
MAX_UTTERANCE = 450
MAX_REPLY = 650
MAX_CONTEXT = 2400


def pending_question(answer: str, kind: str = "chat") -> str:
    """Capture a final single question before truncating a long answer."""
    if kind not in ("chat", "clarify") or not isinstance(answer, str):
        return ""
    clean = " ".join(answer.replace("\x00", " ").split())
    if not clean.endswith("?") or clean.count("?") != 1:
        return ""
    question = re.split(r"(?:[.!]|…)\s+", clean)[-1]
    return question[-180:]


def bounded_answer(answer: str, maximum: int, kind: str = "chat") -> str:
    """Keep a real trailing question in the existing bounded SQLite field."""
    text = " ".join(answer.split())
    question = pending_question(text, kind)
    if len(text) > maximum and question:
        return text[:maximum-len(question)-2] + "… " + question
    return text[:maximum]


@dataclass(frozen=True)
class VoiceTurn:
    user: str
    jarvis: str
    kind: str
    question: str = ""


class ConversationMemory:
    """Bounded preceding context; untrusted history never authorizes action."""

    def __init__(self, limit: int = MAX_TURNS):
        if type(limit) is not int or not 1 <= limit <= MAX_TURNS:
            raise ValueError("Numero di scambi non valido.")
        self._turns: deque[VoiceTurn] = deque(maxlen=limit)

    def __len__(self) -> int:
        return len(self._turns)

    def clear(self) -> None:
        self._turns.clear()

    @staticmethod
    def _clean(value: str, maximum: int) -> str:
        if not isinstance(value, str):
            return ""
        # A failed Vosk transcription should not add untrusted control bytes.
        text = " ".join(value.replace("\x00", " ").split())
        return text[:maximum].strip()

    def remember(self, user: str, jarvis: str, kind: str = "chat") -> None:
        """Call only when an answer/intent outcome is known; not before GPT."""
        if kind not in ("chat", "clarify", "action", "error"):
            raise ValueError("Tipo di ricordo conversazionale non valido.")
        u = self._clean(user, MAX_UTTERANCE)
        a = self._clean(jarvis, MAX_REPLY)
        if u and a:
            self._turns.append(VoiceTurn(u, a, kind, pending_question(jarvis, kind)))

    def snapshot(self) -> tuple[dict, ...]:
        """All bounded records for one final prompt selection, oldest first."""
        return tuple({"utente": turn.user, "jarvis": turn.jarvis,
                      "tipo": turn.kind, "question": turn.question}
                     for turn in self._turns)

    def context(self, max_chars: int = MAX_CONTEXT) -> str:
        """JSON with the latest turns that fit, newest turn always preferred."""
        if type(max_chars) is not int or max_chars < 30:
            return "[]"
        budget = min(max_chars, MAX_CONTEXT)
        selected = []
        # Keep the newest follow-up even when a long assistant answer would
        # otherwise exceed the entire budget. Older turns are less important.
        for turn in reversed(self._turns):
            included = False
            for maximum_user, maximum_reply in (
                    (320, 340), (220, 230), (150, 160), (95, 110), (55, 65), (28, 35)):
                item = {
                    "utente": turn.user[:maximum_user],
                    "lia": turn.jarvis[:maximum_reply],
                    "tipo": turn.kind,
                }
                candidate = [item] + selected
                if len(json.dumps(candidate, ensure_ascii=False,
                                  separators=(",", ":"))) <= budget:
                    selected = candidate
                    included = True
                    break
            if not included:
                break
        return json.dumps(selected, ensure_ascii=False, separators=(",", ":"))

    def last_question(self) -> str:
        """Useful in tests and GUI, but never interpreted as current consent."""
        if not self._turns:
            return ""
        return self._turns[-1].question
