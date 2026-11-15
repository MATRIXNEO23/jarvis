"""Quote dei servizi online: quanto hai usato oggi e quanto resta (15/11 sera).

- Conta richieste e token di ogni servizio, giorno per giorno (e token del mese).
- Se il servizio dice quante richieste restano (Groq nelle intestazioni della risposta),
  usa quel numero; altrimenti confronta il conteggio di Lumi con il limite noto del
  servizio o con quello scritto da te nelle impostazioni.
- Colori della barra: azzurra; arancione quando hai usato più di metà; rossa sotto il 10%.
- Avviso una volta al giorno quando superi la soglia (80% di serie).
Il conteggio è di Lumi: se usi la stessa chiave altrove, il servizio può finire prima.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

AZZURRO, ARANCIONE, ROSSO = "#46ccfa", "#f2a33a", "#ff5c5c"


def _file() -> Path:
    from settings import default_path
    return default_path().parent / "servizi_online_uso.json"


def _oggi() -> str:
    return time.strftime("%Y-%m-%d")


def carica(path: Path | None = None) -> dict:
    try:
        data = json.loads((path or _file()).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError, RuntimeError):
        return {}


def _salva(data: dict, path: Path | None = None) -> None:
    path = path or _file()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data), encoding="utf-8")
    os.replace(temp, path)


def _voce(data: dict, service_id: str) -> dict:
    today, month = _oggi(), _oggi()[:7]
    item = data.setdefault(service_id, {})
    if item.get("giorno") != today:
        item.update(giorno=today, richieste=0, token=0, rimaste=None, limite_letto=None,
                    avvisato=False)
    if item.get("mese") != month:
        item.update(mese=month, token_mese=0)
    return item


def _intero(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def registra(service_id: str, tokens=None, headers=None, *, soglia: float = 0.8,
             limite_utente=None, path: Path | None = None) -> str:
    """Conta una richiesta; restituisce un avviso da mostrare (o «»)."""
    data = carica(path)
    item = _voce(data, service_id)
    item["richieste"] += 1
    used = _intero(tokens) or 0
    item["token"] += used
    item["token_mese"] += used
    headers = {str(k).lower(): v for k, v in (headers or {}).items()}
    remaining = _intero(headers.get("x-ratelimit-remaining-requests"))
    limit = _intero(headers.get("x-ratelimit-limit-requests"))
    if remaining is not None:
        item["rimaste"] = remaining
    if limit is not None:
        item["limite_letto"] = limit
    _salva(data, path)
    info = stato(service_id, limite_utente=limite_utente, data=data)
    if info["usato"] is not None and info["usato"] >= soglia and not item["avvisato"]:
        item["avvisato"] = True
        _salva(data, path)
        return "Hai usato il %d%% delle richieste di oggi di %s." % (round(info["usato"] * 100), service_id)
    return ""


def stato(service_id: str, *, limite_utente=None, data=None, path: Path | None = None) -> dict:
    """{'richieste', 'token', 'limite', 'usato' (0..1 o None), 'colore', 'testo'}."""
    import servizi_online
    data = data if data is not None else carica(path)
    item = dict(data.get(service_id, {}))
    if item.get("giorno") != _oggi():
        item = {"richieste": 0, "token": 0, "rimaste": None, "limite_letto": None}
    service = servizi_online.PER_ID.get(service_id)
    limit = (_intero(limite_utente) or item.get("limite_letto")
             or (service.richieste_giorno if service else None))
    used = None
    if limit:
        if item.get("rimaste") is not None and item.get("limite_letto"):
            used = 1 - item["rimaste"] / item["limite_letto"]
        else:
            used = item.get("richieste", 0) / limit
        used = max(0.0, min(1.0, used))
    colour = AZZURRO if used is None or used <= 0.5 else (ARANCIONE if used < 0.9 else ROSSO)
    if used is None:
        text = "%d richieste oggi" % item.get("richieste", 0)
    else:
        text = "%d%% rimasto (%d/%d oggi)" % (round((1 - used) * 100), item.get("richieste", 0), limit)
    return {"richieste": item.get("richieste", 0), "token": item.get("token", 0), "limite": limit,
            "usato": used, "colore": colour, "testo": text}


def stima_token(messages) -> int:
    """Stima semplice: circa 4 caratteri per token."""
    return sum(len(str(m.get("content") or "")) for m in messages) // 4
