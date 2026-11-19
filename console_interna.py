"""Una sola finestra (15/11 sera, punto 7): niente console nera.

Lumi parte con pythonw (avvia_lumi.bat); quello che prima finiva nella finestra nera
(print, errori, avvisi) va in un file (console.log nel profilo, massimo ~2 MB con una copia
precedente) e dentro Lumi come righe «sistema»: non disturbano la chat e si vedono in
DIAGNOSTICA (filtro SISTEMA). Se Lumi non riesce ad avviarsi, compare una finestra con
l'errore e il percorso del file.
"""
from __future__ import annotations

import collections
import os
import sys
import threading
import traceback
from pathlib import Path

MAX_BYTES = 2 * 1024 * 1024
_PENDING = collections.deque(maxlen=500)
_LOCK = threading.Lock()
_STATE = {"path": None, "installed": False}


def percorso() -> Path:
    try:
        from settings import default_path
        return default_path().parent / "console.log"
    except Exception:
        return Path(os.environ.get("TEMP", ".")) / "lumi-console.log"


def _scrivi_file(text: str) -> None:
    path = _STATE["path"] or percorso()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size > MAX_BYTES:
            os.replace(path, path.with_name("console.old.log"))
        with open(path, "a", encoding="utf-8", errors="replace") as stream:
            stream.write(text)
    except OSError:
        pass


class _Tee:
    """Scrive su file, mette le righe in coda per Lumi e (se c'è) sulla console vera."""

    def __init__(self, original):
        self.original = original
        self.partial = ""
        self.encoding = "utf-8"

    def write(self, text):
        if not isinstance(text, str):
            text = str(text)
        with _LOCK:
            _scrivi_file(text)
            self.partial += text
            *lines, self.partial = self.partial.split("\n")
            for line in lines:
                if line.strip():
                    _PENDING.append(line[:400])
        if self.original is not None:
            try:
                self.original.write(text)
            except Exception:
                pass
        return len(text)

    def flush(self):
        if self.original is not None:
            try:
                self.original.flush()
            except Exception:
                pass

    def isatty(self):
        return False


def installa(path: Path | None = None) -> None:
    if _STATE["installed"]:
        return
    _STATE["path"] = path
    sys.stdout = _Tee(sys.stdout)
    sys.stderr = _Tee(sys.stderr)

    def thread_error(args):
        traceback.print_exception(args.exc_type, args.exc_value, args.exc_traceback)
    threading.excepthook = thread_error
    _STATE["installed"] = True


def preleva(limit: int = 50) -> list[str]:
    """Righe nuove da mostrare in Lumi (al massimo `limit` per volta)."""
    out = []
    with _LOCK:
        while _PENDING and len(out) < limit:
            out.append(_PENDING.popleft())
    return out


def errore_fatale() -> None:
    """Lumi non è partita: lo dice in una finestra (senza console non si vedrebbe nulla)."""
    text = traceback.format_exc()
    _scrivi_file(text)
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Lumi non si è avviata",
                             text[-1500:] + "\n\nDettagli in: " + str(_STATE["path"] or percorso()))
        root.destroy()
    except Exception:
        pass
