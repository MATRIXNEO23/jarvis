"""Interruttore MODELLO ON/OFF (barra in alto, accanto a GPT).

OFF: nessuna richiesta va al modello (né Gemma/locale né GPT). Funzionano solo i
comandi interni deterministici: serve a provare il motore interno da solo.
Non salvato: a ogni avvio Lumi riparte con il modello ON (nessuna sorpresa).
Le risposte automatiche di Telegram non dipendono da questo interruttore.
"""
from __future__ import annotations

_STATE = {"enabled": True, "local": True}


def enabled() -> bool:
    return _STATE["enabled"]


def set_enabled(value: bool) -> None:
    _STATE["enabled"] = bool(value)


def toggle_message() -> str:
    set_enabled(not enabled())
    if enabled():
        return "MODELLO ON > Le richieste non riconosciute tornano al modello."
    return ("MODELLO OFF > Solo comandi interni: le frasi non riconosciute non vanno "
            "né a Gemma né a GPT.")


def refused(text: str) -> str:
    short = " ".join(str(text).split())[:80]
    return (f"MODELLO OFF > «{short}» non è un comando interno: nessun modello usato. "
            "Riattiva con MODELLO ON in alto.")


# --- «cervello locale» a voce (Gemma/KoboldCpp sul PC) -----------------------------------
# Come MODELLO: non salvato, a ogni avvio riparte acceso. Il cervello online (GPT e i
# futuri gratuiti) usa l'interruttore GPT già esistente.
def local_enabled() -> bool:
    return _STATE["enabled"] and _STATE["local"]


def set_local(value: bool) -> str:
    _STATE["local"] = bool(value)
    if not value:
        return "Cervello locale spento: le frasi non vanno più al modello sul PC."
    if not _STATE["enabled"]:
        return "Cervello locale acceso, ma MODELLO è OFF: riattivalo in alto per usarlo."
    return "Cervello locale acceso."


def refused_local(text: str) -> str:
    if not _STATE["enabled"]:
        return refused(text)
    short = " ".join(str(text).split())[:80]
    return (f"CERVELLO LOCALE SPENTO > «{short}» non è un comando interno: nessun modello usato. "
            "Di' «attiva cervello locale» per riaccenderlo.")
