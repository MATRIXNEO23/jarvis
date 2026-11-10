"""Punto d'ingresso unico usato da Lumi (jarvis.py).

Lo stato vive qui e non in nuove variabili del costruttore dell'interfaccia:
le funzioni esistenti (try_timer_command, chiusura) restano indipendenti e,
senza add-on configurato, questi richiami non fanno nulla.
"""
from __future__ import annotations

_STATE = {"service": None, "program_parser": None}


def register(service, program_parser=None) -> None:
    _STATE["service"] = service
    _STATE["program_parser"] = program_parser


def service():
    return _STATE["service"]


def handle_text(spoken: str, write_line, speak) -> bool:
    """True se la frase era un comando musica (gestito)."""
    current = _STATE["service"]
    if current is None or not current.is_enabled():
        return False
    from .commands import parse_command
    request = parse_command(spoken)
    if request is None:
        return False
    if request[0] not in ("play", "queue", "playlist") and current.snapshot().get("mode") is None:
        # Niente in riproduzione: «stop», «avanti», «pausa»… non vengono
        # catturati dalla musica e restano agli altri comandi o al modello.
        return False
    parser = _STATE["program_parser"]
    if request[0] == "play" and parser is not None:
        # Una frase che Programmi e app riconosce resta a Programmi e app.
        try:
            if parser(spoken) is not None:
                return False
        except Exception:
            pass
    message = current.handle(*request)
    if message:
        write_line("MUSICA > " + message)
        if request[0] in ("play", "playlist") and current.mode == "browser":
            speak(message)
    return True


def close() -> None:
    current = _STATE["service"]
    if current is not None:
        current.close()
