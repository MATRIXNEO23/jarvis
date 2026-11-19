"""Città predefinita dell'add-on Meteo: addon-data/meteo/config.json nel profilo dati."""
from __future__ import annotations

import json
import os
from pathlib import Path

from settings import default_path


def data_folder() -> Path:
    return default_path().parent / "addon-data" / "meteo"


def load(folder: Path | None = None) -> dict:
    """{"citta": {"nome", "lat", "lon"} | None}; file mancante o rovinato = nessuna città."""
    try:
        data = json.loads((Path(folder or data_folder()) / "config.json").read_text(encoding="utf-8"))
        city = data.get("citta")
        if (isinstance(city, dict) and isinstance(city.get("nome"), str) and city["nome"].strip()
                and isinstance(city.get("lat"), (int, float)) and isinstance(city.get("lon"), (int, float))
                and -90 <= city["lat"] <= 90 and -180 <= city["lon"] <= 180):
            return {"citta": {"nome": city["nome"].strip()[:60], "lat": float(city["lat"]),
                              "lon": float(city["lon"])}}
    except (OSError, ValueError, AttributeError):
        pass
    return {"citta": None}


def save(city: dict | None, folder: Path | None = None) -> None:
    target = Path(folder or data_folder())
    target.mkdir(parents=True, exist_ok=True)
    path = target / "config.json"
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps({"citta": city}, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, path)
