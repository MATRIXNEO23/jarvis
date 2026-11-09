"""Natural Italian voices (Piper) for Lumi/Lumi, with optional digital effect.

Synthesis runs in a child process (``python -m piper``): if the neural runtime
cannot run on this CPU, only the child fails and the caller falls back to the
Windows voice. Voices are downloaded from the Lumi repository (voci.json)
with SHA-256 verification into the user's profile, never into the program
folder. The engine (piper-tts) is GPL-3.0 and installed separately.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request
import wave

CATALOG_URL = "https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/voci/voci.json"
PREFIX = "Piper: "
LABELS = {"paola": "Paola", "serena": "Serena"}
_MAX_TEXT = 1200


class PiperVoiceError(RuntimeError):
    pass


def voices_dir() -> Path:
    base = os.environ.get("JARVIS_TRIAL_HOME") or os.path.join(
        os.environ.get("LOCALAPPDATA", str(Path.home())), "Jarvis")
    return Path(base) / "voci"


def voice_label(key: str) -> str:
    return PREFIX + LABELS.get(key, key)


def key_from_label(label: str) -> str | None:
    if isinstance(label, str) and label.startswith(PREFIX):
        name = label[len(PREFIX):]
        return next((k for k, v in LABELS.items() if v == name), None)
    return None


def _model(key: str, folder: Path | None = None) -> Path | None:
    folder = folder or voices_dir()
    found = sorted(folder.glob(f"it_IT-{key}-*.onnx"))
    return found[0] if found and found[0].with_suffix(".onnx.json").is_file() else None


def installed_piper_voices(folder: Path | None = None) -> list[str]:
    return [voice_label(k) for k in LABELS if _model(k, folder) is not None]


def engine_available(runner=subprocess.run) -> bool:
    """True when ``piper`` imports in a child process (no crash in Lumi)."""
    try:
        proc = runner([sys.executable, "-c", "import piper"], capture_output=True,
                      timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def download_voice(key: str, *, catalog_url: str = CATALOG_URL, folder: Path | None = None,
                   opener=urllib.request.urlopen, progress=None) -> Path:
    """Download one voice listed in the repository catalog, verifying SHA-256."""
    folder = folder or voices_dir()
    folder.mkdir(parents=True, exist_ok=True)
    with opener(catalog_url, timeout=30) as response:
        catalog = json.load(response)
    voice = catalog.get("voices", {}).get(key)
    if not voice:
        raise PiperVoiceError("Voce non presente nel catalogo: " + key)
    for name, info in voice["files"].items():
        if "/" in name or "\\" in name or not name.startswith(f"it_IT-{key}-"):
            raise PiperVoiceError("Nome file voce non valido.")
        target = folder / name
        if target.is_file() and _sha256(target) == info["sha256"]:
            continue
        partial = target.with_suffix(target.suffix + ".part")
        digest, count = hashlib.sha256(), 0
        with opener(info["url"], timeout=180) as response, partial.open("wb") as out:
            while True:
                chunk = response.read(1 << 20)
                if not chunk:
                    break
                count += len(chunk)
                if count > info["bytes"]:
                    break
                digest.update(chunk)
                out.write(chunk)
                if progress:
                    progress(name, count, info["bytes"])
        if count != info["bytes"] or digest.hexdigest() != info["sha256"]:
            partial.unlink(missing_ok=True)
            raise PiperVoiceError("Download voce non integro: " + name)
        os.replace(partial, target)
    (folder / f"{key}-attribuzione.txt").write_text(
        voice.get("attribution", "") + "\n" + voice.get("license", "") + "\n", encoding="utf-8")
    model = _model(key, folder)
    if model is None:
        raise PiperVoiceError("Voce scaricata ma incompleta: " + key)
    return model


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def synthesize(text: str, key: str, out_path: Path, *, folder: Path | None = None,
               runner=subprocess.run, timeout: int = 120) -> Path:
    """Text -> WAV in an isolated child process. Raises PiperVoiceError."""
    if not isinstance(text, str) or not text.strip():
        raise PiperVoiceError("Testo vuoto.")
    model = _model(key, folder)
    if model is None:
        raise PiperVoiceError("Voce Piper non scaricata: " + LABELS.get(key, key))
    try:
        proc = runner([sys.executable, "-m", "piper", "-m", str(model), "-f", str(out_path)],
                      input=" ".join(text.split())[:_MAX_TEXT], capture_output=True, text=True,
                      encoding="utf-8", timeout=timeout,
                      creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PiperVoiceError("Motore Piper non avviato: " + type(exc).__name__) from exc
    if proc.returncode != 0 or not Path(out_path).is_file():
        detail = " ".join((proc.stderr or "").split())[-160:]
        raise PiperVoiceError(f"Motore Piper non disponibile (codice {proc.returncode}). {detail}")
    return Path(out_path)


def apply_digital_effect(in_path: Path, out_path: Path, amount: float) -> Path:
    """Holographic touch: soft chorus + short metallic echo, mixed by ``amount``.

    amount 0 copies the file unchanged; 0.2-0.3 is the recommended range.
    """
    amount = max(0.0, min(1.0, float(amount)))
    with wave.open(str(in_path), "rb") as source:
        params = source.getparams()
        frames = source.readframes(params.nframes)
    if amount <= 0 or params.sampwidth != 2 or params.nchannels != 1:
        Path(out_path).write_bytes(Path(in_path).read_bytes())
        return Path(out_path)
    import numpy as np
    dry = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
    rate = params.framerate
    n = np.arange(dry.size)
    # Chorus: copy delayed by 12 ms +/- 3 ms at 0.8 Hz.
    delay = (0.012 + 0.003 * np.sin(2 * np.pi * 0.8 * n / rate)) * rate
    index = np.clip(n - delay, 0, dry.size - 1)
    low = np.floor(index).astype(np.int64)
    frac = index - low
    chorus = dry[low] * (1 - frac) + dry[np.minimum(low + 1, dry.size - 1)] * frac
    # Metallic comb echo: 3 short taps (feels "digital", not like a hall).
    echo = np.zeros_like(dry)
    for ms, gain in ((7, 0.35), (13, 0.25), (21, 0.15)):
        shift = int(rate * ms / 1000)
        echo[shift:] += dry[:-shift] * gain
    wet = 0.6 * chorus + 0.4 * echo
    mixed = (1 - 0.5 * amount) * dry + amount * wet
    peak = float(np.max(np.abs(mixed))) or 1.0
    mixed = mixed / max(1.0, peak / 0.95)
    with wave.open(str(out_path), "wb") as target:
        target.setparams(params)
        target.writeframes((mixed * 32767).astype("<i2").tobytes())
    return Path(out_path)


def loudness_envelope(path: Path, fps: int = 30) -> list[float]:
    """0..1 loudness per frame, for the avatar's lip sync."""
    with wave.open(str(path), "rb") as source:
        params = source.getparams()
        frames = source.readframes(params.nframes)
    if params.sampwidth != 2 or not frames:
        return []
    import array
    samples = array.array("h", frames)
    step = max(1, params.framerate * params.nchannels // fps)
    values = []
    for start in range(0, len(samples), step):
        block = samples[start:start + step]
        values.append((sum(v * v for v in block) / len(block)) ** 0.5 / 32768.0 if block else 0.0)
    top = max(values) or 1.0
    return [min(1.0, v / top) for v in values]


def play_wav(path: Path) -> None:
    """Blocking playback with the Windows built-in player (stop via stop_playback)."""
    import winsound
    winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_NODEFAULT)


def stop_playback() -> None:
    try:
        import winsound
        winsound.PlaySound(None, winsound.SND_PURGE)
    except (ImportError, RuntimeError):
        pass


def speak_with_piper(text: str, key: str, *, effect: float = 0.0,
                     on_envelope=None, folder: Path | None = None,
                     runner=subprocess.run, player=play_wav) -> None:
    """Synthesize, apply effect, publish lip-sync envelope, play. Raises on failure."""
    with tempfile.TemporaryDirectory(prefix="lumi-voice-") as temp:
        raw = synthesize(text, key, Path(temp) / "raw.wav", folder=folder, runner=runner)
        final = apply_digital_effect(raw, Path(temp) / "voice.wav", effect) if effect > 0 else raw
        if on_envelope is not None:
            on_envelope(loudness_envelope(final))
        player(final)
