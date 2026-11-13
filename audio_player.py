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
STALL_SECONDS = 3.0               # audio fermo (dispositivo occupato, es. app Netflix)


class AudioBusyError(OSError):
    """L'uscita audio non va avanti: un altro programma la sta occupando."""
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
    try:
        _play_mci(path, max_seconds)
    except AudioBusyError:
        # Il lettore di Windows (MCI) resta fermo quando un'altra app, es. Netflix,
        # tiene l'uscita audio: riprovo con WASAPI condiviso (sounddevice, già usato
        # per il microfono), che suona insieme agli altri programmi.
        if path.suffix.lower() != ".wav" or _STOP.is_set():
            raise
        _play_shared(path)


def _play_shared(path: Path) -> None:
    """WASAPI condiviso via sounddevice (RawOutputStream: niente numpy)."""
    import wave
    try:
        import sounddevice as sd
    except ImportError as exc:
        raise AudioBusyError("Audio occupato da un altro programma e riproduzione "
                             "alternativa non disponibile: " + str(exc)[:80]) from exc
    with wave.open(str(path), "rb") as source:
        rate, channels, width = source.getframerate(), source.getnchannels(), source.getsampwidth()
        frames = source.readframes(source.getnframes())
    if width != 2:
        raise AudioBusyError("Audio occupato da un altro programma.")
    step = rate // 20 * channels * 2                  # 50 ms per blocco
    try:
        with sd.RawOutputStream(samplerate=rate, channels=channels, dtype="int16") as stream:
            for start in range(0, len(frames), step):
                if _STOP.is_set():
                    break
                _notify(start / float(rate * channels * 2))
                stream.write(frames[start:start + step])
    except Exception as exc:
        raise AudioBusyError("Audio occupato da un altro programma anche in modalità "
                             "condivisa: togli «controllo esclusivo» nelle proprietà degli "
                             "altoparlanti. " + str(exc)[:80]) from exc
    finally:
        _notify(-1.0)


def _play_mci(path: Path, max_seconds: float) -> None:
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
        length = _mci(f"status {alias} length")[1]
        if length.isdigit() and int(length) > 0:
            # Mai più della durata vera + qualche secondo (prima: fino a 10 minuti).
            max_seconds = min(max_seconds, int(length) / 1000.0 + STALL_SECONDS)
        if _mci(f"play {alias}")[0] != 0:
            raise OSError("Riproduzione non avviata.")
        started = time.monotonic()
        last_position, moved_at = None, started
        while not _STOP.is_set():
            now = time.monotonic()
            mode = _mci(f"status {alias} mode")[1]
            position = _mci(f"status {alias} position")[1]
            if position.isdigit():
                _notify(int(position) / 1000.0)
                if position != last_position:
                    last_position, moved_at = position, now
            if mode not in ("playing", "seeking", "not ready", ""):
                break
            if now - moved_at > STALL_SECONDS or now - started > max_seconds:
                _mci(f"stop {alias}")
                raise AudioBusyError("Audio occupato da un altro programma: "
                                     "la voce di Lumi non esce.")
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
