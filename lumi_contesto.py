"""Contesto comune di Lumi: le cose che i pezzi di jarvis.py condividono.

Passo 1 del piano docs/PIANO-DIVISIONE-JARVIS.md. `main()` crea il contesto una volta,
dopo aver costruito finestra, console, voce e servizi; i moduli che verranno spostati
fuori da jarvis.py (Telegram, modello locale, gestori di poll…) lo ricevono invece di
leggere le variabili interne di main(). Qui nessuna logica: solo i riferimenti.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

_CURRENT: dict = {"ctx": None}


@dataclass
class Contesto:
    root: Any                                 # finestra Tk principale
    write_line: Callable[[str], None]         # scrive nella console di Lumi
    speak_result: Callable[[str], None]       # fa parlare Lumi (se la voce è attiva)
    settings: Any                             # impostazioni salvate nel profilo
    output_queue: Any = None                  # coda degli eventi letta da poll()
    service: Any = None                       # servizio GPT
    workspace: Any = None                     # memoria di lavoro
    addon_manager: Any = None                 # gestore degli add-on
    extra: dict = field(default_factory=dict)  # altri riferimenti, per nome

    def get(self, name: str, default=None):
        return getattr(self, name, self.extra.get(name, default))


def crea(**values) -> Contesto:
    known = {k: values.pop(k) for k in list(values) if k in Contesto.__dataclass_fields__}
    ctx = Contesto(**known, extra=values)
    _CURRENT["ctx"] = ctx
    return ctx


def attuale() -> Contesto | None:
    """Il contesto di questa esecuzione di Lumi (None prima dell'avvio)."""
    return _CURRENT["ctx"]


class Vivo:
    """Riferimenti «vivi» a variabili di main(): ogni lettura chiede il valore attuale.

    main() passa una lambda per nome (es. telegram_bridge=lambda: telegram_bridge); il
    modulo spostato legge d.telegram_bridge e ottiene sempre il valore del momento, anche
    se main() lo ha cambiato dopo o lo definisce più avanti (come una funzione annidata).
    """

    def __init__(self, **getters):
        object.__setattr__(self, "_getters", getters)

    def __getattr__(self, name):
        try:
            getter = self._getters[name]
        except KeyError:
            raise AttributeError(name) from None
        return getter()
