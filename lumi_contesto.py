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
