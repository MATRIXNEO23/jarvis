"""Punto d'ingresso dell'add-on Meteo usato da jarvis.py (stesso schema di musica/runtime.py).

Il comando risponde a voce per qualsiasi città; la rete gira in un thread e la risposta torna
sul thread dell'interfaccia con `post`. Add-on spento: nessuna frase viene presa."""
from __future__ import annotations

import threading

_STATE = {"service": None, "post": None}


def register(service, post) -> None:
    _STATE.update(service=service, post=post)


def service():
    return _STATE["service"]


def handle_text(spoken: str, write_line, speak) -> bool:
    current = _STATE["service"]
    if current is None or not current.is_enabled():
        return False
    from .commands import parse_command
    from .service import ErroreMeteo
    request = parse_command(spoken)
    if request is None:
        return False
    post = _STATE["post"] or (lambda fn: fn())

    def work():
        try:
            text = current.risposta(request[1])
        except ErroreMeteo as exc:
            text = str(exc)
        except Exception as exc:                       # mai silenzio
            text = "Il meteo ha dato un errore (" + type(exc).__name__ + ")."
        post(lambda: (write_line("METEO > " + text), speak(text)))

    threading.Thread(target=work, daemon=True, name="lumi-meteo").start()
    return True
