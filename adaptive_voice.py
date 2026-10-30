"""Lightweight, user-approved Vosk transcript corrections for Lia.

No new speech model, background training, audio recording, internet or cloud API.
Corrections live in the same local SQLite file as the opt-in Second Brain.
Only short non-command words / application names can be learned, and the
original wake, confirmation and negation words are never changed.
"""
from __future__ import annotations

import re
import sqlite3
import unicodedata
from pathlib import Path

from settings import default_path

MAX_ENTRIES = 80
MAX_WORDS = 4
MAX_CHARS = 65

# Exclude control words, negations, confirmations, and wake words from BOTH
# sides. They must never be changed by a remembered transcription correction.
_CONTROL_WORDS = frozenset({
    "ehi", "hey", "jarvis", "lia", "ok", "si", "sì", "no", "non", "senza",
    "apri", "aprimi", "apertura", "chiudi", "chiudimi", "chiuderlo", "chiudila",
    "esci", "uscire", "salva", "salvare", "salvami", "scarta", "cancella",
    "elimina", "esegui", "lancia", "invia", "manda", "conferma", "annulla",
    "ferma", "stop", "spegni", "accendi", "formatta", "sovrascrivi", "paga",
    "compra", "eliminare", "rimuovi", "confermato", "password", "token", "pin",
    "sempre", "mai", "disattiva", "attiva", "dettatura", "microfono",
})


class SpeechCorrectionError(ValueError):
    pass


def _normalize(term: object) -> str:
    if not isinstance(term, str):
        raise SpeechCorrectionError("Correzione non testuale.")
    # Keep accents. Do not allow path separators, punctuation, digits, symbols
    # or line breaks to become parts of a new voice command.
    text = " ".join(unicodedata.normalize("NFKC", term).casefold().split())
    words = text.split()
    if (not text or len(text) > MAX_CHARS or len(words) > MAX_WORDS
            or any(not re.fullmatch(r"[a-zàèéìíîòóùú]+", w) for w in words)
            or any(w in _CONTROL_WORDS for w in words)):
        raise SpeechCorrectionError(
            "Inserisci soltanto 1-4 parole di vocabolario, "
            "senza comandi, negazioni o conferme.")
    return text


class SpeechCorrections:
    """Small compiled in-memory lexicon; SQLite changes only on user approval."""

    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else default_path().with_name(
            "second_brain.sqlite3")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._rules: list[tuple[re.Pattern, str]] = []
        self._initialize()
        self.reload()

    def _db(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.path), timeout=5)

    def _initialize(self) -> None:
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS speech_corrections(
                heard TEXT PRIMARY KEY,
                intended TEXT NOT NULL,
                confirmed_by_user INTEGER NOT NULL CHECK(confirmed_by_user=1)
            )""")

    def reload(self) -> None:
        with self._db() as db:
            pairs = db.execute(
                "SELECT heard, intended FROM speech_corrections "
                "ORDER BY LENGTH(heard) DESC, heard LIMIT ?",
                (MAX_ENTRIES + 1,),
            ).fetchall()
        if len(pairs) > MAX_ENTRIES:
            raise SpeechCorrectionError("Troppe correzioni vocali memorizzate.")
        rules = []
        for source, target in pairs:
            if source != _normalize(source) or target != _normalize(target):
                raise SpeechCorrectionError("Correzione vocale archiviata non valida.")
            rules.append((re.compile(
                r"(?<!\w)" + re.escape(source) + r"(?!\w)", re.I), target))
        self._rules = rules

    def add(self, heard: str, intended: str, *, user_confirmed: bool = False) -> None:
        if user_confirmed is not True:
            raise SpeechCorrectionError(
                "Le correzioni vocali richiedono una conferma esplicita dell'utente.")
        source = _normalize(heard)
        target = _normalize(intended)
        if source == target:
            raise SpeechCorrectionError("Il riconoscimento è già uguale alla correzione.")
        with self._db() as db:
            count = db.execute("SELECT COUNT(*) FROM speech_corrections").fetchone()[0]
            exists = db.execute(
                "SELECT 1 FROM speech_corrections WHERE heard=?", (source,)
            ).fetchone() is not None
            if count >= MAX_ENTRIES and not exists:
                raise SpeechCorrectionError("Dizionario pieno: elimina prima una correzione.")
            db.execute(
                "INSERT INTO speech_corrections(heard,intended,confirmed_by_user) "
                "VALUES(?,?,1) ON CONFLICT(heard) DO UPDATE SET "
                "intended=excluded.intended, confirmed_by_user=1",
                (source, target),
            )
        self.reload()

    def correct(self, recognized: str) -> str:
        """One pass, not iterative; never lets a rule cascade into another."""
        if not isinstance(recognized, str) or not recognized:
            return recognized
        # Vosk output is typically lowercase, but retain unrelated casing.
        # Split into fixed matches on original text; never rewrite an inserted
        # replacement in the same pass.
        matches: list[tuple[int, int, str]] = []
        for pattern, target in self._rules:
            for match in pattern.finditer(recognized):
                matches.append((match.start(), match.end(), target))
        matches.sort(key=lambda item: (item[0], -(item[1]-item[0])))
        accepted = []
        boundary = 0
        for start, end, target in matches:
            if start >= boundary:
                accepted.append((start, end, target))
                boundary = end
        if not accepted:
            return recognized
        result, position = [], 0
        for start, end, target in accepted:
            result.extend((recognized[position:start], target))
            position = end
        result.append(recognized[position:])
        return "".join(result)

    def count(self) -> int:
        return len(self._rules)

    def clear(self) -> None:
        """Only through explicit UI confirmation; cannot be invoked by GPT."""
        with self._db() as db:
            db.execute("DELETE FROM speech_corrections")
        self._rules.clear()
