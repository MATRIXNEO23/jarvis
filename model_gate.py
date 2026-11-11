"""Interruttore MODELLO ON/OFF (barra in alto, accanto a GPT).

OFF: nessuna richiesta va al modello (né Gemma/locale né GPT). Funzionano solo i
comandi interni deterministici: serve a provare il motore interno da solo.
Non salvato: a ogni avvio Lumi riparte con il modello ON (nessuna sorpresa).
Le risposte automatiche di Telegram non dipendono da questo interruttore.
"""
from __future__ import annotations

_STATE = {"enabled": True}


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
