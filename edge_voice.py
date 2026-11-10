"""Voci Microsoft Edge (online, gratuite) tramite il pacchetto edge-tts.

- Facoltative: richiedono installa_voce_edge.bat (pip edge-tts) e Internet.
  Il testo da leggere viene inviato al servizio di sintesi di Microsoft.
- Sintesi in un processo figlio persistente (edge-tts/aiohttp non entrano
  nella RAM di Lumi; un errore non chiude Lumi). La frase successiva viene
  preparata mentre suona la precedente.
- Audio MP3 riprodotto con MCI di Windows (nessuna dipendenza). Il labiale
  usa i tempi delle parole restituiti dal servizio (WordBoundary).
- Errore o rete assente: EdgeVoiceError -> Lumi torna alla voce di Windows.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import threading

PREFIX = "Edge: "
VOICES = {
    "isabella": ("Isabella", "it-IT-IsabellaNeural"),
    "elsa": ("Elsa", "it-IT-ElsaNeural"),
    "diego": ("Diego", "it-IT-DiegoNeural"),
    "giuseppe": ("Giuseppe", "it-IT-GiuseppeMultilingualNeural"),
}
_MAX_TEXT = 1200


class EdgeVoiceError(RuntimeError):
    pass


def voice_label(key: str) -> str:
    return PREFIX + VOICES[key][0] + " (online)"


def key_from_label(label) -> str | None:
    if not isinstance(label, str) or not label.startswith(PREFIX):
        return None
    name = label[len(PREFIX):].split(" (", 1)[0].strip().casefold()
    return name if name in VOICES else None


_AVAILABLE: bool | None = None


def engine_available(runner=subprocess.run) -> bool:
    """edge-tts importabile in un processo figlio (controllo fatto una volta)."""
    global _AVAILABLE
    if _AVAILABLE is None or runner is not subprocess.run:
        try:
            proc = runner([sys.executable, "-c", "import edge_tts"], capture_output=True,
                          timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            result = proc.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            result = False
        if runner is not subprocess.run:
            return result
        _AVAILABLE = result
    return _AVAILABLE


def installed_edge_voices() -> list[str]:
    return [voice_label(k) for k in VOICES] if engine_available() else []


_WORKER_CODE = r"""
import asyncio, json, sys
import edge_tts

async def run(req):
    try:
        comm = edge_tts.Communicate(req["text"], req["voice"], boundary="WordBoundary")
    except TypeError:
        comm = edge_tts.Communicate(req["text"], req["voice"])
    marks = []
    with open(req["out"], "wb") as audio:
        async for chunk in comm.stream():
            kind = chunk.get("type")
            if kind == "audio":
                audio.write(chunk["data"])
            elif kind in ("WordBoundary", "SentenceBoundary"):
                marks.append([chunk["offset"] / 1e7, chunk["duration"] / 1e7])
    return marks

sys.stdout.write("ready\n"); sys.stdout.flush()
for line in sys.stdin:
    try:
        marks = asyncio.run(asyncio.wait_for(run(json.loads(line)), 45))
        sys.stdout.write(json.dumps({"ok": True, "marks": marks}) + "\n")
    except Exception as exc:
        sys.stdout.write(json.dumps({"ok": False, "error": type(exc).__name__ + ": "
                                     + " ".join(str(exc).split())[:200]}) + "\n")
    sys.stdout.flush()
"""


class _EdgeWorker:
    def __init__(self, timeout: float = 60):
        self.lock = threading.Lock()
        self.timeout = timeout
        self.proc = subprocess.Popen(
            [sys.executable, "-c", _WORKER_CODE], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if self._read() != "ready":
            self.close()
            raise EdgeVoiceError("Voce Edge non disponibile: esegui installa_voce_edge.bat.")

    def _read(self) -> str:
        timer = threading.Timer(self.timeout, self.close)
        timer.daemon = True
        timer.start()
        try:
            return (self.proc.stdout.readline() or "").strip()
        finally:
            timer.cancel()

    def alive(self) -> bool:
        return self.proc.poll() is None

    def synth(self, text: str, voice: str, out_path: Path) -> list:
        with self.lock:
            if not self.alive():
                raise EdgeVoiceError("Voce Edge chiusa.")
            try:
                self.proc.stdin.write(json.dumps({"text": text, "voice": voice,
                                                  "out": str(out_path)}) + "\n")
                self.proc.stdin.flush()
            except OSError as exc:
                self.close()
                raise EdgeVoiceError("Voce Edge interrotta.") from exc
            line = self._read()
        try:
            answer = json.loads(line)
        except ValueError:
            self.close()
            raise EdgeVoiceError("Voce Edge: nessuna risposta.") from None
        if not answer.get("ok") or not Path(out_path).is_file() or Path(out_path).stat().st_size == 0:
            raise EdgeVoiceError("Voce Edge non disponibile (rete?): "
                                 + str(answer.get("error", ""))[:160])
        return [m for m in answer.get("marks", []) if isinstance(m, list) and len(m) == 2]

    def close(self) -> None:
        try:
            if self.proc.poll() is None:
                self.proc.kill()
        except OSError:
            pass


_WORKER: _EdgeWorker | None = None
_WORKER_LOCK = threading.Lock()


def _worker() -> _EdgeWorker:
    global _WORKER
    with _WORKER_LOCK:
        if _WORKER is None or not _WORKER.alive():
            _WORKER = _EdgeWorker()
        return _WORKER


def shutdown_worker() -> None:
    global _WORKER
    with _WORKER_LOCK:
        if _WORKER is not None:
            _WORKER.close()
        _WORKER = None


def envelope_from_marks(marks, fps: int = 30) -> list[float]:
    """Curva per il labiale dai tempi delle parole: bocca mossa solo sulle
    parole, ~5 sillabe al secondo, chiusa nelle pause."""
    import math
    if not marks:
        return []
    end = max(o + d for o, d in marks)
    values = [0.0] * (int(end * fps) + 2)
    for offset, duration in marks:
        start, stop = int(offset * fps), int((offset + duration) * fps)
        for frame in range(start, max(start + 1, stop)):
            t = frame / fps - offset
            values[frame] = max(values[frame], .35 + .6 * abs(math.sin(math.pi * 5.0 * t)))
    return values


def synthesize(text: str, key: str, out_path: Path, synth=None) -> list:
    if key not in VOICES:
        raise EdgeVoiceError("Voce Edge sconosciuta.")
    clean = " ".join(str(text).split())[:_MAX_TEXT]
    if not clean:
        raise EdgeVoiceError("Testo vuoto.")
    try:
        if synth is not None:
            return synth(clean, VOICES[key][1], Path(out_path))
        return _worker().synth(clean, VOICES[key][1], Path(out_path))
    except EdgeVoiceError:
        if synth is None:
            shutdown_worker()
        raise
    except OSError as exc:
        shutdown_worker()
        raise EdgeVoiceError("Voce Edge non avviata: " + type(exc).__name__) from exc


# --- riproduzione MP3: audio_player (MCI con posizione reale) ------------
def play_mp3(path: Path) -> None:
    import audio_player
    try:
        audio_player.play(Path(path))
    except OSError as exc:
        raise EdgeVoiceError(str(exc)) from exc


def stop_playback() -> None:
    try:
        import audio_player
        audio_player.stop()
    except Exception:
        pass


# --- frase successiva preparata in anticipo --------------------------------
_PREPARED: dict[tuple, tuple[threading.Thread, dict]] = {}
_PREPARED_LOCK = threading.Lock()


def _render(text: str, key: str, synth=None) -> tuple[Path, list]:
    from piper_voice import _audio_dir
    path = _audio_dir() / f"edge-{os.getpid()}-{threading.get_ident()}-{id(text)}.mp3"
    return path, synthesize(text, key, path, synth=synth)


def prepare(text: str, key: str, synth=None) -> None:
    token = (text, key)
    with _PREPARED_LOCK:
        if token in _PREPARED:
            return
        box: dict = {}

        def work():
            try:
                box["result"] = _render(text, key, synth)
            except Exception as exc:
                box["error"] = exc
        thread = threading.Thread(target=work, daemon=True, name="lumi-edge-prepare")
        _PREPARED[token] = (thread, box)
    thread.start()


def speak_with_edge(text: str, key: str, *, on_envelope=None, upcoming: str | None = None,
                    synth=None, player=play_mp3, **_ignored) -> None:
    with _PREPARED_LOCK:
        prepared = _PREPARED.pop((text, key), None)
    if prepared is not None:
        thread, box = prepared
        thread.join()
        if "error" in box:
            error = box["error"]
            raise error if isinstance(error, EdgeVoiceError) else EdgeVoiceError(
                "Sintesi Edge non riuscita: " + type(error).__name__)
        path, marks = box["result"]
    else:
        path, marks = _render(text, key, synth)
    try:
        if upcoming:
            prepare(upcoming, key, synth)
        if on_envelope is not None:
            on_envelope(envelope_from_marks(marks))
        player(path)
    finally:
        try:
            Path(path).unlink()
        except OSError:
            pass
