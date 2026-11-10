"""Riproduzione audio con posizione reale (MCI di Windows, nessuna dipendenza).

La posizione di riproduzione viene comunicata mentre l'audio suona, cosi'
il labiale dell'avatar segue il suono vero (anche se l'apertura del file
o la decodifica MP3 tardano) invece di un orologio stimato.
"""
from __future__ import annotations

import os
from pathlib import Path
import threading
import time

POSITION_LISTENER = None          # callable(seconds) impostato da Lumi
_STOP = threading.Event()
_LOCK = threading.Lock()


def _notify(seconds: float) -> None:
    listener = POSITION_LISTENER
    if listener is not None:
        try:
            listener(seconds)
        except Exception:
            pass


def _mci(command: str) -> tuple[int, str]:
    import ctypes
    buffer = ctypes.create_unicode_buffer(128)
    code = ctypes.windll.winmm.mciSendStringW(command, buffer, 127, None)
    return code, buffer.value


def play(path: Path, *, max_seconds: float = 600) -> None:
    """Blocca fino alla fine; stop() la interrompe. WAV o MP3."""
    path = Path(path)
    if os.name != "nt":
        raise OSError("Riproduzione audio disponibile solo su Windows.")
    _STOP.clear()
    kind = "mpegvideo" if path.suffix.lower() == ".mp3" else "waveaudio"
    alias = f"lumiaudio{threading.get_ident()}"
    with _LOCK:
        code, _ = _mci(f'open "{path}" type {kind} alias {alias}')
    if code != 0:
        if kind == "waveaudio":
            import winsound          # ripiego: senza posizione, avvio stimato
            _notify(0.0)
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_NODEFAULT)
            return
        raise OSError(f"Riproduzione MP3 non disponibile (MCI {code}).")
    try:
        _mci(f"set {alias} time format milliseconds")
        if _mci(f"play {alias}")[0] != 0:
            raise OSError("Riproduzione non avviata.")
        started = time.monotonic()
        while not _STOP.is_set() and time.monotonic() - started < max_seconds:
            mode = _mci(f"status {alias} mode")[1]
            position = _mci(f"status {alias} position")[1]
            if position.isdigit():
                _notify(int(position) / 1000.0)
            if mode not in ("playing", "seeking", "not ready", ""):
                break
            time.sleep(0.03)
        if _STOP.is_set():
            _mci(f"stop {alias}")
    finally:
        _mci(f"close {alias}")
        _notify(-1.0)                 # fine: bocca chiusa


def stop() -> None:
    _STOP.set()
    if os.name == "nt":
        try:
            import winsound
            winsound.PlaySound(None, winsound.SND_PURGE)
        except (ImportError, RuntimeError):
            pass
