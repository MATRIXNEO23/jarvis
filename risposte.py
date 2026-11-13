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


# --- numeri della griglia: valgono senza «Lumi» mentre la griglia è aperta -----------------
# Il microfono può capire i numeri in lettere, storpiati o detti in inglese: queste varianti
# valgono SOLO in questa finestra, mai come correzioni generali.
NUMBERS = {
    1: ("1", "uno", "un", "una", "primo", "prima", "one", "uan", "wan"),
    2: ("2", "due", "du", "duo", "secondo", "seconda", "two", "tu", "tuu", "too"),
    3: ("3", "tre", "tré", "terzo", "terza", "three", "tri", "tree"),
    4: ("4", "quattro", "quatro", "quarto", "quarta", "four", "for", "fo"),
    5: ("5", "cinque", "cinqu", "cinche", "quinto", "quinta", "five", "faiv", "fai"),
    6: ("6", "sei", "sé", "sesto", "sesta", "six", "sics", "sic", "sex"),
    7: ("7", "sette", "sete", "settimo", "settima", "seven", "seven"),
    8: ("8", "otto", "oto", "ottavo", "ottava", "eight", "eit", "eigh"),
    9: ("9", "nove", "nov", "nono", "nona", "nine", "nain", "naine"),
}
_NUMBER_OF = {word: n for n, words in NUMBERS.items() for word in words}
GRID_WORDS = ["clicca", "clic", "doppio clic", "invio", "clic destro", "indietro", "chiudi griglia",
              "chiudi la griglia", "mouse a destra", "mouse a sinistra", "mouse su", "mouse giù",
              "di poco", "ancora", "lumi"]
_STATE["numbers_until"] = 0.0


def number_of(text: str):
    """«cinque», «il 5», «six» → 5; altrimenti None."""
    words = _clean(text).split()
    if words and words[0] in ("il", "la", "numero", "casella"):
        words = words[1:]
    if words and words[0] == "numero":
        words = words[1:]
    return _NUMBER_OF.get(" ".join(words)) if len(words) == 1 else None


def is_grid_command(text: str) -> bool:
    clean = _clean(text)
    return number_of(clean) is not None or any(clean == w or clean.startswith(w + " ")
                                               for w in GRID_WORDS if w != "lumi")


def expect_numbers(seconds: float = 90.0) -> None:
    _STATE["numbers_until"] = time.monotonic() + seconds


def numbers_waiting() -> bool:
    return time.monotonic() < _STATE["numbers_until"]


def numbers_done() -> None:
    _STATE["numbers_until"] = 0.0


def grammar() -> list:
    """Parole ammesse dal riconoscitore nella finestra attiva (risposta o griglia)."""
    if waiting():
        return GRAMMAR
    words = sorted({w for ws in NUMBERS.values() for w in ws if not w.isdigit()})
    return words + GRID_WORDS + ["[unk]"]
