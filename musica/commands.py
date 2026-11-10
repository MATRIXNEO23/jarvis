"""Frasi locali dell'add-on Musica (nessun modello, nessuna rete)."""
from __future__ import annotations

import re

_WAKE = re.compile(r"^\s*(?:ehi\s+|ok\s+)?lumi[\s,!.:]*", re.IGNORECASE)
_PLAY = re.compile(
    r"^(?:metti|mettimi|suona|suonami|riproduci|fammi\s+sentire|fammi\s+ascoltare|"
    r"voglio\s+ascoltare|ascoltiamo)\s+"
    r"(?:(?:la\s+canzone|il\s+brano|la\s+musica\s+di|musica\s+di|un\s+po'\s+di|"
    r"qualcosa\s+di|il\s+pezzo)\s+)?(?P<query>.+?)[\s.!?]*$", re.IGNORECASE)
_QUEUE = re.compile(
    r"^(?:(?:metti|aggiungi)\s+(?:in|alla)\s+coda|accoda)\s+(?P<query>.+?)[\s.!?]*$"
    r"|^aggiungi\s+(?P<query2>.+?)\s+(?:in|alla)\s+coda[\s.!?]*$", re.IGNORECASE)
_PLAYLIST = re.compile(
    r"^(?:metti|suona|riproduci|fammi\s+sentire|ascoltiamo)\s+(?:la\s+)?playlist\s+"
    r"(?P<query>.+?)[\s.!?]*$", re.IGNORECASE)
# «metti un timer», «metti la sveglia», «metti in pausa»… non sono musica.
_NOT_MUSIC = re.compile(
    r"^(?:un\s+|il\s+|la\s+|una\s+|lo\s+|l')?(?:timer|sveglia|promemoria|allarme|volume|"
    r"in\s+pausa|pausa|nota|appunt\w*|muto|film|serie|episodio|puntata|netflix|"
    r"prime\s+video|disney|cartella|file)\b", re.IGNORECASE)
_SIMPLE = (
    ("pause", r"(?:metti\s+in\s+)?pausa(?:\s+(?:la\s+)?musica)?|ferma\s+un\s+attimo(?:\s+la\s+musica)?"),
    ("resume", r"riprendi(?:\s+la\s+musica)?|continua\s+(?:la\s+)?musica|fai\s+ripartire\s+la\s+musica"
               r"|play"),
    ("stop", r"(?:ferma|stop|spegni|basta)\s+(?:la\s+)?musica|stop\s+musica|stop"),
    ("next", r"(?:prossima|prossimo)(?:\s+(?:canzone|brano|pezzo))?|(?:canzone|brano)\s+successiv[oa]"
             r"|avanti|vai\s+avanti"
             r"|passa\s+(?:alla\s+prossima|al\s+prossimo)|salta(?:\s+(?:canzone|brano))?"),
    ("prev", r"(?:torna\s+)?indietro|(?:canzone|brano|video)\s+precedente|(?:metti\s+)?(?:la\s+|il\s+)?precedente"),
    ("volume_up", r"alza\s+(?:il\s+)?volume\s+(?:della\s+)?musica|musica\s+più\s+forte"),
    ("volume_down", r"abbassa\s+(?:il\s+)?volume\s+(?:della\s+)?musica|musica\s+più\s+piano"),
)


def parse_command(text: str):
    """("play"|"queue"|"playlist", testo) | (azione, "") | None se non è musica."""
    if not isinstance(text, str):
        return None
    value = _WAKE.sub("", text.strip()).strip()
    value = re.sub(r"\s+", " ", value)
    if not value or len(value) > 160:
        return None
    for action, pattern in _SIMPLE:
        if re.fullmatch(pattern + r"[\s.!?]*", value, re.IGNORECASE):
            return action, ""
    match = _QUEUE.match(value)
    if match:
        query = (match.group("query") or match.group("query2") or "").strip(" \"'«»")
        return ("queue", query) if query and len(query) <= 120 else None
    match = _PLAYLIST.match(value)
    if match:
        query = match.group("query").strip(" \"'«»")
        return ("playlist", query) if query and len(query) <= 60 else None
    match = _PLAY.match(value)
    if match:
        query = match.group("query").strip(" \"'«»")
        if query and not _NOT_MUSIC.match(query) and len(query) <= 120:
            return "play", query
    return None
