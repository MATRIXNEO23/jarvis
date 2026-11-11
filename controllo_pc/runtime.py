"""Punto d'ingresso unico usato da Lumi (jarvis.py), come musica/runtime.py.

Lo stato vive qui (nessuna nuova variabile nelle funzioni di jarvis.py).
Con l'add-on spento o non registrato non fa nulla e non intercetta frasi.
"""
from __future__ import annotations

_STATE = {"service": None}


def register(service) -> None:
    _STATE["service"] = service


def service():
    return _STATE["service"]


def claims_first(spoken: str) -> bool:
    """True se una parola corta («indietro», «giù», «apri», «il 3»…) va al Controllo PC
    PRIMA degli altri comandi (es. «indietro» della musica), perché lo stai usando ora."""
    current = _STATE["service"]
    if current is None or not current.is_enabled():
        return False
    if current.pending is not None:
        return True                         # risposta sì/no a una sua domanda
    from .commands import parse_command
    request = parse_command(spoken)
    return (request is not None and request[0] in current.SHORT_ACTIONS + ("pick",)
            and current.recent())


def handle_text(spoken: str, write_line, speak) -> bool:
    """True se la frase era per il Controllo PC (gestita)."""
    current = _STATE["service"]
    if current is None or not current.is_enabled():
        return False
    reply = current.answer(spoken)          # «sì»/«no» a una conferma in sospeso
    if reply is None:
        from .commands import parse_command
        request = parse_command(spoken)
        if request is None or not current.claims(*request):
            return False
        try:
            reply = current.handle(*request)
        except Exception as exc:            # errore visibile, mai crash di Lumi
            reply = "Controllo PC: " + str(exc)[:120]
        if reply is None:
            return False                    # nessuna finestra/elemento: ad altri comandi
    write_line("CONTROLLO PC > " + reply)
    first = reply.split("\n", 1)[0]
    if "\n" not in reply or len(first) < 90:
        speak(first)                        # elenchi mai letti a voce: solo l'intestazione
    return True
