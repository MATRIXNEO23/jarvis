"""Impostazioni dell'add-on Musica nel profilo dati (non nella cartella del codice).

- addon-data/musica/config.json: cartelle musica e volume.
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
    result = {"folder": "", "folders": [], "volume": 70}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return result
    folders = data.get("folders")
    if not isinstance(folders, list):
        folders = [data.get("folder")]           # vecchio formato: una sola cartella
    result["folders"] = clean_folders(folders)
    result["folder"] = result["folders"][0] if result["folders"] else ""
    if type(data.get("volume")) is int and 0 <= data["volume"] <= 100:
        result["volume"] = data["volume"]
    return result


MAX_FOLDERS = 20


def clean_folders(values) -> list[str]:
    """Cartelle valide, senza doppioni (stesso ordine), al massimo MAX_FOLDERS."""
    result, seen = [], set()
    for value in values or []:
        if not isinstance(value, str):
            continue
        value = value.strip()
        key = os.path.normcase(os.path.normpath(value)) if value else ""
        if value and len(value) <= 400 and key not in seen:
            seen.add(key)
            result.append(value)
        if len(result) >= MAX_FOLDERS:
            break
    return result


def save(values: dict, folder: Path | None = None) -> None:
    base = Path(folder or data_folder())
    base.mkdir(parents=True, exist_ok=True)
    folders = clean_folders(values.get("folders") or [values.get("folder", "")])
    clean = {"folder": folders[0] if folders else "", "folders": folders,
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
