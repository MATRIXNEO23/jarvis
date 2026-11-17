"""Quota dei servizi di ricerca: stima dai contatori locali (giorno e mese).

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
        text = "stima: %d ricerche oggi, %d nel mese" % (today, month)
    else:
        text = "stima: %d%% rimasto (%d/%d nel mese, %d oggi)" % (
            round((1 - used) * 100), month, limite_mese, today)
    return {"oggi": today, "mese": month, "limite": limite_mese or None, "usato": used,
            "colore": colour, "testo": text, "stima": True}
