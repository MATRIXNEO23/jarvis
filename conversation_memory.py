"""Small, ephemeral voice-dialogue memory for Lumi's GPT conversation mode.

This is contextual recall, not an authority store, command queue, knowledge base
or persistent profile. Only the last few completed user/assistant exchanges are
kept in process memory. No file, SQLite, telemetry, network or cloud storage.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import json

MAX_TURNS = 8
MAX_UTTERANCE = 260
MAX_REPLY = 280
MAX_CONTEXT = 1050


@dataclass(frozen=True)
class VoiceTurn:
    user: str
    jarvis: str
    kind: str


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
            self._turns.append(VoiceTurn(u, a, kind))

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
                    (175, 185), (125, 135), (90, 100), (55, 65), (28, 35)):
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
        turn = self._turns[-1]
        answer = turn.jarvis.strip()
        if turn.kind not in ("clarify", "chat") or answer.count("?") != 1:
            return ""
        return answer[-180:] if answer.endswith("?") else ""
