"""Comandi a voce su Lumi stessa: riduci a icona, chiudi, riavvia, nascondi/sveglia
l'avatar, spegni il PC (solo detto esplicitamente e con conferma).

Funzionano anche con Lumi ridotta a icona (il microfono resta attivo).
jarvis.py registra le azioni (register); qui nessuna variabile nuova nelle sue funzioni.
"""
from __future__ import annotations

import re
import time

_WAKE = re.compile(r"^\s*(?:(?:ehi|hey|ok)\s+)?lumi[\s,!.:]*", re.IGNORECASE)
_END = r"[\s.!?]*$"
_PATTERNS = (
    # «minimizza» da solo resta del Controllo PC (finestra in uso): qui solo forme
    # riferite a Lumi.
    ("minimize", re.compile(r"^(?:minimizzati|riduciti|riduci\s+a\s+icona|"
                            r"mettiti\s+(?:da\s+parte|in\s+basso))" + _END, re.I)),
    ("minimize", re.compile(r"^(?:minimizza|riduci\s+a\s+icona|riduci)\s+(?:lumi|jarvis)" + _END, re.I)),
    ("close", re.compile(r"^(?:chiudi(?:ti)?|spegni(?:ti)?|esci\s+da|termina)\s+(?:lumi|jarvis)" + _END, re.I)),
    ("close", re.compile(r"^(?:chiuditi|spegniti)" + _END, re.I)),
    ("restart", re.compile(r"^(?:riavvia(?:ti)?)(?:\s+lumi|\s+jarvis)?" + _END, re.I)),
    ("shutdown_pc", re.compile(r"^spegni\s+(?:il\s+)?(?:pc|computer)" + _END, re.I)),
    ("cancel_shutdown", re.compile(r"^annulla\s+(?:lo\s+)?spegnimento" + _END, re.I)),
    ("hide", re.compile(r"^(?:nascondi(?:ti)?|nascondi\s+(?:l'\s*)?avatar|sparisci)" + _END, re.I)),
    ("wake", re.compile(r"^(?:svegliati|sveglia|torna\s+qui|fatti\s+vedere|mostrati|"
                        r"mostra\s+(?:l'\s*)?avatar)" + _END, re.I)),
)
_YES = {"si", "sì", "conferma", "confermo", "ok", "va bene", "certo", "procedi"}
_NO = {"no", "annulla", "lascia stare", "no grazie"}

_STATE = {"actions": None, "pending": None, "is_hidden_ui": lambda: False}


def parse(text: str):
    if not isinstance(text, str) or len(text) > 80:
        return None
    value = _WAKE.sub("", text).strip()
    for action, pattern in _PATTERNS:
        if pattern.match(value):
            return action
    return None


def register(actions: dict, is_hidden_ui) -> None:
    """actions: minimize, close, restart, shutdown_pc, hide, wake → funzioni senza argomenti.
    is_hidden_ui(): True se Lumi è ridotta a icona o l'avatar è nascosto."""
    _STATE.update(actions=actions, is_hidden_ui=is_hidden_ui, pending=None)


def handle_text(spoken: str, write_line, speak) -> bool:
    actions = _STATE["actions"]
    if actions is None:
        return False
    from frasi_lumi import say
    pending = _STATE["pending"]
    if pending is not None:
        _STATE["pending"] = None
        action, deadline = pending
        word = " ".join(_WAKE.sub("", spoken).casefold().strip(" .!?").split())
        if time.monotonic() <= deadline and word in _YES:
            actions[action]()
            return True
        if time.monotonic() <= deadline and word in _NO:
            reply = say("annullato")
            write_line("LUMI > " + reply)
            speak(reply)
            return True
    action = parse(spoken)
    if action is None:
        return False
    # «sveglia» da sola resta la sveglia (add-on) quando Lumi è già davanti;
    # serve a riaprire Lumi solo se è ridotta a icona o nascosta.
    value = " ".join(_WAKE.sub("", spoken).casefold().strip(" .!?").split())
    if action == "wake" and value == "sveglia" and not _STATE["is_hidden_ui"]():
        return False
    if action in ("restart", "shutdown_pc"):
        _STATE["pending"] = (action, time.monotonic() + 60)
        question = ("Mi riavvio adesso? Di' sì o no." if action == "restart" else
                    "Spengo davvero il computer? Salva prima il tuo lavoro. Di' sì o no.")
        write_line("LUMI > " + question)
        speak(question)
        return True
    actions[action]()
    return True
