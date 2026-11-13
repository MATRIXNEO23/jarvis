"""Lettura degli elementi delle finestre con LumiControl.exe (UI Automation, sola lettura)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def helper_path() -> Path:
    return Path(__file__).resolve().parent / "uia_bin" / "LumiControl.exe"


def _run(args, timeout):
    exe = helper_path()
    if not exe.is_file():
        raise FileNotFoundError(f"Manca {exe} (reinstalla il pacchetto completo).")
    flags = 0x08000000 if sys.platform == "win32" else 0      # CREATE_NO_WINDOW
    done = subprocess.run([str(exe), *args], capture_output=True, timeout=timeout,
                          creationflags=flags)
    data = json.loads(done.stdout.decode("utf-8", "replace").strip() or "{}")
    if not data.get("ok"):
        raise RuntimeError(str(data.get("error", "lettura non riuscita"))[:160])
    return data


def list_elements(hwnd: int, timeout: float = 8.0) -> list[dict]:
    """Elementi visibili della finestra: nome, tipo, posizione, abilitato."""
    data = _run(["list", str(int(hwnd)), "400"], timeout)
    return [i for i in data.get("items", []) if isinstance(i, dict)]


def focused_element(timeout: float = 5.0) -> dict | None:
    """Elemento che ha il fuoco della tastiera (es. il file selezionato con le frecce)."""
    data = _run(["focused"], timeout)
    item = data.get("item")
    return item if isinstance(item, dict) else None


def ocr_elements(hwnd: int, timeout: float = 15.0) -> list[dict]:
    """Scritte visibili lette con l'OCR integrato di Windows 10 (offline): per i
    programmi che non dichiarano i loro elementi (es. copertine, pulsanti disegnati)."""
    data = _run(["ocr", str(int(hwnd))], timeout)
    return [i for i in data.get("items", []) if isinstance(i, dict)]


def play_shapes(hwnd: int, timeout: float = 10.0) -> list[dict]:
    """Pulsanti «play» disegnati (cerchio chiaro con triangolo scuro), senza modelli."""
    data = _run(["play", str(int(hwnd))], timeout)
    return [i for i in data.get("items", []) if isinstance(i, dict)]
