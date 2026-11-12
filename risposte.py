"""Risposte sì/no alle domande di Lumi, capite anche quando il microfono storpia
le parole corte («s», «se», «ci» per «sì»; «non», «nò» per «no»).

Le varianti valgono SOLO come risposta a una domanda in sospeso: non diventano
mai comandi (per questo non si possono insegnare come correzioni della voce).
Dopo una domanda, `expect_answer` apre per qualche secondo una finestra in cui:
- non serve dire «Lumi» (anche nella modalità con il nome obbligatorio);
- il riconoscimento vocale ascolta solo le parole di risposta (più preciso).
"""
from __future__ import annotations

import re
import time

YES = {"si", "sì", "s", "se", "sei", "ci", "sci", "sii", "sìì", "certo", "certamente", "ok",
       "okay", "va bene", "vai", "conferma", "confermo", "esatto", "giusto", "procedi", "fallo",
       "si grazie", "sì grazie", "si si", "sì sì", "proprio", "d'accordo", "daccordo"}
NO = {"no", "non", "nò", "noo", "nooo", "no grazie", "annulla", "lascia stare", "niente",
      "non farlo", "nulla", "stop"}
# Parole per il riconoscimento ristretto (grammatica Vosk) durante l'attesa.
GRAMMAR = ["sì", "si", "no", "non", "certo", "ok", "conferma", "esatto", "giusto", "procedi",
           "va bene", "annulla", "lascia stare", "niente", "lumi", "[unk]"]
_WAKE = re.compile(r"^\s*(?:(?:ehi|hey|ok)\s+)?lumi[\s,!.:]*", re.IGNORECASE)
_STATE = {"until": 0.0}
ANSWER_SECONDS = 10.0


def _clean(text: str) -> str:
    value = _WAKE.sub("", str(text or ""))
    return " ".join(re.sub(r"[^\wàèéìòù' ]+", " ", value.casefold()).split())


def is_yes(text: str) -> bool:
    return _clean(text) in YES


def is_no(text: str) -> bool:
    return _clean(text) in NO


def is_answer(text: str) -> bool:
    return is_yes(text) or is_no(text)


def expect_answer(seconds: float = ANSWER_SECONDS, speech_text: str = "") -> None:
    """Lumi ha appena fatto una domanda: la risposta vale per `seconds` dopo che
    ha finito di parlare (stima dalla lunghezza della frase detta)."""
    speaking = min(12.0, 0.075 * len(speech_text or "")) if speech_text else 0.0
    _STATE["until"] = time.monotonic() + speaking + seconds


def waiting() -> bool:
    return time.monotonic() < _STATE["until"]


def done() -> None:
    _STATE["until"] = 0.0
