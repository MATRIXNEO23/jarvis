"""Quota dei servizi di ricerca: contatori locali (giorno e mese) e, per Tavily, quota reale.
Dicitura onesta (FIX 4): i contatori locali sono «ricerche rilevate» (solo quelle riuscite, non
tutte le richieste che possono consumare crediti). Tavily ha un endpoint ufficiale GET /usage:
`reale()` lo legge (cache di 5 minuti) e, se manca la chiave o la rete, resta il contatore.

Stessa forma di servizi_online.quote.stato (usato 0..1, colore, testo), così la barra è lo
stesso componente grafico. Nessuna API di consumo è collegata (non provabile da qui): il testo
dice sempre «stima». I contatori restano sul PC (servizi_ricerca_uso.json), senza chiavi.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

AZZURRO, ARANCIONE, ROSSO = "#46ccfa", "#f2a33a", "#ff5c5c"


def _file() -> Path:
    from settings import default_path
    return default_path().parent / "servizi_ricerca_uso.json"


def carica(path: Path | None = None) -> dict:
    try:
        data = json.loads((path or _file()).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError, RuntimeError):
        return {}


def registra(service_id: str, *, oggi: str | None = None, path: Path | None = None) -> None:
    """Conta una ricerca riuscita (giorno e mese)."""
    oggi = oggi or time.strftime("%Y-%m-%d")
    data = carica(path)
    item = data.setdefault(service_id, {})
    if item.get("giorno") != oggi:
        item.update(giorno=oggi, oggi=0)
    if item.get("mese") != oggi[:7]:
        item.update(mese=oggi[:7], mese_n=0)
    item["oggi"] = int(item.get("oggi", 0)) + 1
    item["mese_n"] = int(item.get("mese_n", 0)) + 1
    target = path or _file()
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(".tmp")
    temp.write_text(json.dumps(data), encoding="utf-8")
    os.replace(temp, target)


def stato(service_id: str, limite_mese: int = 0, *, oggi: str | None = None,
          data: dict | None = None, path: Path | None = None) -> dict:
    """{'oggi', 'mese', 'limite', 'usato' (0..1 o None), 'colore', 'testo', 'stima': True}."""
    oggi = oggi or time.strftime("%Y-%m-%d")
    item = dict((data if data is not None else carica(path)).get(service_id, {}))
    today = int(item.get("oggi", 0)) if item.get("giorno") == oggi else 0
    month = int(item.get("mese_n", 0)) if item.get("mese") == oggi[:7] else 0
    used = max(0.0, min(1.0, month / limite_mese)) if limite_mese else None
    colour = AZZURRO if used is None or used <= 0.5 else (ARANCIONE if used < 0.9 else ROSSO)
    if used is None:
        text = "ricerche rilevate: %d oggi, %d nel mese" % (today, month)
    else:
        text = "ricerche rilevate: %d/%d nel mese, %d oggi (non è la quota reale)" % (
            month, limite_mese, today)
    return {"oggi": today, "mese": month, "limite": limite_mese or None, "usato": used,
            "colore": colour, "testo": text, "stima": True}


USO_URL = {"tavily": "https://api.tavily.com/usage"}
_CACHE: dict = {}
_VALIDITA = 300.0


def _leggi_uso(service_id: str, key: str, get, timeout: float = 8.0) -> dict | None:
    """Tavily: {'key': {'usage', 'limit'}, 'account': {'plan_usage', 'plan_limit'}} (docs ufficiali)."""
    data = get(USO_URL[service_id], key, timeout)
    if not isinstance(data, dict):
        return None
    k, a = data.get("key") or {}, data.get("account") or {}
    for used, limit in ((a.get("plan_usage"), a.get("plan_limit")), (k.get("usage"), k.get("limit"))):
        if isinstance(used, int) and isinstance(limit, int) and limit > 0:
            return {"usati": used, "limite": limit}
    return None


def reale(service_id: str, key: str, *, get=None, adesso: float | None = None) -> dict | None:
    """Quota letta dall'API del servizio (solo se esiste l'endpoint gratuito), nella forma di
    stato(); None se non disponibile: il chiamante usa allora le «ricerche rilevate»."""
    if service_id not in USO_URL or not key:
        return None
    adesso = time.monotonic() if adesso is None else adesso
    cached = _CACHE.get(service_id)
    if cached is not None and adesso - cached[0] < _VALIDITA:
        return cached[1]
    if get is None:
        from online.servizi_online import _get as get
    try:
        uso = _leggi_uso(service_id, key, get)
    except Exception:                                   # rete, chiave, formato: mai bloccare la UI
        uso = None
    info = None
    if uso is not None:
        used = max(0.0, min(1.0, uso["usati"] / uso["limite"]))
        info = {"oggi": None, "mese": uso["usati"], "limite": uso["limite"], "usato": used,
                "colore": AZZURRO if used <= 0.5 else (ARANCIONE if used < 0.9 else ROSSO),
                "testo": "%d/%d crediti usati (letto da Tavily)" % (uso["usati"], uso["limite"]),
                "stima": False}
    _CACHE[service_id] = (adesso, info)
    return info
