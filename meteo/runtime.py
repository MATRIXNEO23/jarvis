"""Punto d'ingresso dell'add-on Meteo usato da jarvis.py (stesso schema di musica/runtime.py).

Il comando risponde a voce per qualsiasi città; la rete gira in un thread e la risposta torna
sul thread dell'interfaccia con `post`. Add-on spento: nessuna frase viene presa."""
from __future__ import annotations

import threading

_STATE = {"service": None, "post": None, "show": None, "ask_close": None}


def register(service, post, show=None, ask_close=None) -> None:
    """`show(elenco)`: apre la finestra dei risultati (058, «meteo settimana» e «meteo completo»).
    `ask_close(testo_letto)`: 059, a fine lettura Lumi chiede «Chiudo la finestra?»."""
    _STATE.update(service=service, post=post, show=show, ask_close=ask_close)


def service():
    return _STATE["service"]


def handle_text(spoken: str, write_line, speak, show_listing=None) -> bool:
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
        listing = None
        try:
            if request[0] == "settimana":          # 058: riassunto a voce, 7 giorni nella finestra
                text, listing = current.risposta_settimana(request[1])
            elif ":" in request[0] or request[0] == "riepilogo":
                text, listing = current.risposta_estesa(request[0], request[1])
            else:
                text = (current.risposta_domani if request[0] == "domani" else current.risposta)(request[1])
        except ErroreMeteo as exc:
            text = str(exc)
        except Exception as exc:                       # mai silenzio
            text = "Il meteo ha dato un errore (" + type(exc).__name__ + ")."
        def done():
            write_line("METEO > " + text)
            mostra = show_listing or _STATE["show"]
            if listing is not None and mostra is not None:
                try:
                    mostra(listing)
                except Exception:                  # la finestra non deve fermare la voce
                    write_line("METEO > Finestra dei risultati non disponibile.")
            speak(text)
            chiedi = _STATE["ask_close"]
            if listing is not None and mostra is not None and chiedi is not None:
                try:
                    chiedi(text)               # dopo la lettura: «Chiudo la finestra?»
                except Exception:
                    pass
        post(done)

    threading.Thread(target=work, daemon=True, name="lumi-meteo").start()
    return True
