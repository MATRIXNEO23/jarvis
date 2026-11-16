"""Descrizione di un servizio di ricerca online: un file per servizio in servizi_ricerca/servizi/.

Stesso schema dei servizi online (servizi_online/base.py): per cambiare indirizzo, link della
chiave o passi di un servizio si modifica solo il suo file. `adattatore` è la funzione che
fa la ricerca vera; None = voce predisposta (chiave e link già nelle impostazioni, ricerca
non ancora collegata: Lumi la salta).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Risultato:
    riassunto: str
    link: tuple = ()                  # ((titolo, indirizzo), ...)


@dataclass(frozen=True)
class Ricerca:
    id: str
    nome: str
    chiavi: str                       # pagina ufficiale dove si crea la chiave
    ordine: int = 99
    limite: str = ""                  # cosa offre gratis, in parole semplici
    passi: tuple = field(default_factory=tuple)
    adattatore: object = None         # callable(key, query, approfondisci, timeout, post) -> Risultato
