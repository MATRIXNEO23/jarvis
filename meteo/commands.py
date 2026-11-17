"""Frasi del meteo: «che tempo fa a Roma», «meteo Milano», «com'è il tempo a Tokyo»,
e (056c) «meteo domani», «meteo domani a Roma», «che tempo farà domani».

Escluse le frasi con «online» (restano ricerche) e quelle sul «clima» (es. «com'è il clima a
Tokyo in primavera»): le seconde sono domande più complesse, non il tempo di adesso."""
from __future__ import annotations

import re

_WAKE = re.compile(r"^\s*(?:(?:ehi|hey|ok)\s+)?lumi[\s,!.:]*", re.I)
_CODA = re.compile(r"(?:\s+(?:oggi|adesso|ora|in\s+questo\s+momento|per\s+favore))+[\s.!?]*$", re.I)
_CITTA = r"(?:\s+(?:(?:a|ad|in|di|per|su|nella\s+città\s+di)\s+)?(?P<citta>[^\d,;:]{2,40}?))?[\s.!?]*$"
_PATTERN = re.compile(
    r"^(?:(?:che|quale)\s+tempo\s+fa|com['’]è\s+il\s+tempo|come\s+è\s+il\s+tempo|"
    r"(?:dimmi\s+)?(?:il\s+|le\s+)?(?:meteo|previsioni(?:\s+del\s+tempo)?))" + _CITTA, re.I)
_DOMANI = re.compile(r"\s*\bdomani\b\s*", re.I)
_FARA = re.compile(r"\bfarà\b|\bfara\b", re.I)
_ESCLUSE = re.compile(r"\bonline\b|\bclima\w*|\bdopodomani\b|\bsettimana\b|\bprimavera\b|"
                      r"\bestate\b|\bautunno\b|\binverno\b", re.I)


def parse_command(text: str):
    """("meteo", città o None) se è una richiesta di meteo attuale; altrimenti None."""
    if not isinstance(text, str) or len(text) > 120:
        return None
    value = _CODA.sub("", " ".join(_WAKE.sub("", text).strip().split()))
    if _ESCLUSE.search(value):
        return None
    kind = "meteo"
    if _DOMANI.search(value):           # 056c: «meteo domani», «che tempo farà domani a Roma»
        kind = "domani"
        value = " ".join(_FARA.sub("fa", _DOMANI.sub(" ", value)).split())
    match = _PATTERN.match(value)
    if not match:
        return None
    city = (match.group("citta") or "").strip(" .!?")
    return kind, (city or None)
