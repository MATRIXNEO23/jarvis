"""Impostazioni dell'add-on Musica nel profilo dati (non nella cartella del codice).

- addon-data/musica/config.json: cartella musica e volume.
- addon-data/musica/youtube-key.dpapi: chiave API YouTube cifrata con DPAPI
  (leggibile solo dallo stesso utente Windows), mai nel repository.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path

from settings import default_path


def data_folder() -> Path:
    return default_path().parent / "addon-data" / "musica"


def _protect(value: bytes, encrypt: bool) -> bytes:
    from telegram_security import _windows_dpapi
    return _windows_dpapi(value, encrypt)


def load(folder: Path | None = None) -> dict:
    path = Path(folder or data_folder()) / "config.json"
    result = {"folder": "", "volume": 70}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return result
    if isinstance(data.get("folder"), str) and len(data["folder"]) <= 400:
        result["folder"] = data["folder"]
    if type(data.get("volume")) is int and 0 <= data["volume"] <= 100:
        result["volume"] = data["volume"]
    return result


def save(values: dict, folder: Path | None = None) -> None:
    base = Path(folder or data_folder())
    base.mkdir(parents=True, exist_ok=True)
    clean = {"folder": str(values.get("folder", ""))[:400],
             "volume": max(0, min(100, int(values.get("volume", 70))))}
    tmp = base / "config.json.tmp"
    tmp.write_text(json.dumps(clean, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, base / "config.json")


def load_api_key(folder: Path | None = None, protect=_protect) -> str:
    path = Path(folder or data_folder()) / "youtube-key.dpapi"
    try:
        raw = path.read_bytes()
        return protect(base64.b64decode(raw), False).decode("utf-8").strip()
    except Exception:
        return ""


def save_api_key(key: str, folder: Path | None = None, protect=_protect) -> None:
    base = Path(folder or data_folder())
    path = base / "youtube-key.dpapi"
    key = "".join(str(key or "").split())
    if not key:
        if path.exists():
            path.unlink()
        return
    if len(key) > 120 or not key.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Chiave API non valida.")
    base.mkdir(parents=True, exist_ok=True)
    tmp = base / "youtube-key.dpapi.tmp"
    tmp.write_bytes(base64.b64encode(protect(key.encode("utf-8"), True)))
    os.replace(tmp, path)
