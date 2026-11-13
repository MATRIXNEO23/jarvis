"""Natural Italian voices (Piper) for Lumi, with optional digital effect.

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
import threading
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
    """True with the bundled piper.exe, or when ``piper`` imports in a child process."""
    if bundled_engine() is not None and runner is subprocess.run:
        return True
    try:
        proc = runner([sys.executable, "-c", "import piper"], capture_output=True,
                      timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def download_voice(key: str, *, catalog_url: str = CATALOG_URL, folder: Path | None = None,
                   opener=urllib.request.urlopen, progress=None) -> Path:
    """Download one voice ZIP listed in the repository catalog and extract it.

    The ZIP hash and every extracted file hash are verified; only the files
    named in the catalog are extracted (no paths from the archive are used).
    """
    import zipfile
    folder = folder or voices_dir()
    folder.mkdir(parents=True, exist_ok=True)
    with opener(catalog_url, timeout=30) as response:
        catalog = json.load(response)
    voice = catalog.get("voices", {}).get(key)
    if not voice or "zip" not in voice:
        raise PiperVoiceError("Voce non presente nel catalogo: " + key)
    package = voice["zip"]
    partial = folder / (key + ".zip.part")
    digest, count = hashlib.sha256(), 0
    try:
        with opener(package["url"], timeout=180) as response, partial.open("wb") as out:
            while True:
                chunk = response.read(1 << 20)
                if not chunk:
                    break
                count += len(chunk)
                if count > package["bytes"]:
                    break
                digest.update(chunk)
                out.write(chunk)
                if progress:
                    progress(key, count, package["bytes"])
        if count != package["bytes"] or digest.hexdigest() != package["sha256"]:
            raise PiperVoiceError("Download voce non integro: " + key)
        with zipfile.ZipFile(partial) as archive:
            for name, info in voice["files"].items():
                if "/" in name or "\\" in name or not name.startswith(f"it_IT-{key}-"):
                    raise PiperVoiceError("Nome file voce non valido.")
                data = archive.read(name)
                if hashlib.sha256(data).hexdigest() != info["sha256"]:
                    raise PiperVoiceError("File voce non integro: " + name)
                temp = folder / (name + ".part")
                temp.write_bytes(data)
                os.replace(temp, folder / name)
    finally:
        partial.unlink(missing_ok=True)
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


# Persistent child process: the voice model is loaded ONCE, not per sentence.
# It stays a separate process, so an engine crash never closes Lumi.
_WORKER_CODE = r"""
import json, sys, wave
from piper import PiperVoice
voice = PiperVoice.load(sys.argv[1])
sys.stdout.write("ready\n"); sys.stdout.flush()
for line in sys.stdin:
    try:
        req = json.loads(line)
        scale = float(req.get("length_scale") or 1.0)
        with wave.open(req["out"], "wb") as wav_file:
            done = False
            if abs(scale - 1.0) > 1e-3:
                try:
                    from piper import SynthesisConfig
                    voice.synthesize_wav(req["text"], wav_file,
                                         syn_config=SynthesisConfig(length_scale=scale))
                    done = True
                except (ImportError, TypeError):
                    done = False
            if not done:
                voice.synthesize_wav(req["text"], wav_file)
        sys.stdout.write("ok\n")
    except Exception as exc:
        sys.stdout.write("err " + type(exc).__name__ + " " + " ".join(str(exc).split())[:200] + "\n")
    sys.stdout.flush()
"""


ENGINE_DIR = Path(__file__).resolve().parent / "voce_engine" / "piper"


def bundled_engine() -> Path | None:
    """piper.exe shipped inside Lumi (no Python packages, no installation)."""
    exe = ENGINE_DIR / "piper.exe"
    return exe if os.name == "nt" and exe.is_file() else None


def _ascii_path(path: Path) -> str:
    """piper.exe reads argv as narrow text: use the 8.3 short path if needed."""
    text = str(path)
    if text.isascii() or os.name != "nt":
        return text
    try:
        import ctypes
        buffer = ctypes.create_unicode_buffer(1024)
        if ctypes.windll.kernel32.GetShortPathNameW(text, buffer, 1024) and buffer.value.isascii():
            return buffer.value
    except Exception:
        pass
    raise PiperVoiceError("Percorso della voce con caratteri speciali: motore incluso non utilizzabile.")


class _PiperWorker:
    """Persistent engine. ``exe`` mode: bundled piper.exe with --json-input,
    run inside the audio folder so file names stay plain ASCII.
    Otherwise: the piper-tts Python package in a child interpreter."""

    def __init__(self, model: Path, timeout: float = 90, exe: Path | None = None,
                 length_scale: float = 1.0):
        self.model = Path(model)
        self.length_scale = length_scale
        self.lock = threading.Lock()
        self.timeout = timeout
        self.exe = exe
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        if exe is not None:
            self.cwd = _audio_dir()
            self.proc = subprocess.Popen(
                [str(exe), "--model", _ascii_path(self.model), "--json-input", "--quiet",
                 "--length_scale", f"{self.length_scale:.3f}"],
                cwd=str(self.cwd), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, text=True, encoding="utf-8", creationflags=flags)
            return
        self.cwd = None
        self.proc = subprocess.Popen(
            [sys.executable, "-c", _WORKER_CODE, str(self.model)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8", creationflags=flags)
        if self._read() != "ready":
            self.close()
            raise PiperVoiceError("Motore Piper persistente non avviato.")

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

    def synth(self, text: str, out_path: Path) -> Path:
        with self.lock:
            if not self.alive():
                raise PiperVoiceError("Motore Piper chiuso.")
            out_path = Path(out_path)
            if self.exe is not None:
                if out_path.parent.resolve() != Path(self.cwd).resolve():
                    raise PiperVoiceError("Cartella audio non valida per il motore.")
                request = {"text": text, "output_file": out_path.name}
            else:
                request = {"text": text, "out": str(out_path),
                           "length_scale": self.length_scale}
            try:
                self.proc.stdin.write(json.dumps(request) + "\n")
                self.proc.stdin.flush()
            except OSError as exc:
                self.close()
                raise PiperVoiceError("Motore Piper interrotto.") from exc
            answer = self._read()
        if self.exe is not None and answer and answer.endswith(out_path.name):
            answer = "ok"
        if answer != "ok" or not Path(out_path).is_file():
            if not answer:
                self.close()
            raise PiperVoiceError("Motore Piper: " + (answer or "nessuna risposta")[:200])
        return Path(out_path)

    def close(self) -> None:
        try:
            if self.proc.poll() is None:
                self.proc.kill()
        except OSError:
            pass


_WORKERS: dict[str, _PiperWorker] = {}
_WORKERS_LOCK = threading.Lock()


def _worker_for(model: Path, exe: Path | None = None,
                length_scale: float = 1.0) -> _PiperWorker:
    # piper.exe takes length_scale only at start: a speed change restarts it.
    key = str(Path(model).resolve()) + "|" + str(exe) + "|" + f"{length_scale:.3f}"
    with _WORKERS_LOCK:
        worker = _WORKERS.get(key)
        if worker is None or not worker.alive():
            for other in _WORKERS.values():   # one voice in RAM at a time
                other.close()
            _WORKERS.clear()
            worker = _WORKERS[key] = _PiperWorker(Path(model), exe=exe,
                                                  length_scale=length_scale)
        return worker


def shutdown_workers() -> None:
    with _WORKERS_LOCK:
        for worker in _WORKERS.values():
            worker.close()
        _WORKERS.clear()


def synthesize(text: str, key: str, out_path: Path, *, folder: Path | None = None,
               runner=None, timeout: int = 120, length_scale: float = 1.0) -> Path:
    """Text -> WAV in an isolated child process. Raises PiperVoiceError.

    Default: persistent worker (model loaded once). If it cannot run, or a
    test injects ``runner``, fall back to one ``python -m piper`` per call.
    """
    if not isinstance(text, str) or not text.strip():
        raise PiperVoiceError("Testo vuoto.")
    model = _model(key, folder)
    if model is None:
        raise PiperVoiceError("Voce Piper non scaricata: " + LABELS.get(key, key))
    clean = " ".join(text.split())[:_MAX_TEXT]
    if runner is None:
        exe = bundled_engine()
        if exe is not None and Path(out_path).parent.resolve() == _audio_dir().resolve():
            try:
                return _worker_for(model, exe, length_scale).synth(clean, Path(out_path))
            except (PiperVoiceError, OSError):
                shutdown_workers()
        try:
            return _worker_for(model, None, length_scale).synth(clean, Path(out_path))
        except (PiperVoiceError, OSError):
            shutdown_workers()
        runner = subprocess.run
    try:
        proc = runner([sys.executable, "-m", "piper", "-m", str(model), "-f", str(out_path)],
                      input=clean, capture_output=True, text=True,
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
    try:
        import numpy as np
    except ImportError:
        return _digital_effect_plain(frames, params, out_path, amount)
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


def _digital_effect_plain(frames: bytes, params, out_path: Path, amount: float) -> Path:
    """Same effect without numpy (bundled engine, plain Python)."""
    import array
    import math
    dry = array.array("h", frames)
    if sys.byteorder != "little":
        dry.byteswap()
    rate = params.framerate
    size = len(dry)
    taps = [(int(rate * ms / 1000), gain) for ms, gain in ((7, 0.35), (13, 0.25), (21, 0.15))]
    step = 2 * math.pi * 0.8 / rate
    keep = 1 - 0.5 * amount
    mixed = [0.0] * size
    peak = 1.0
    for n in range(size):
        delay = (0.012 + 0.003 * math.sin(step * n)) * rate
        pos = n - delay
        if pos <= 0:
            chorus = dry[0]
        else:
            low = int(pos)
            frac = pos - low
            high = low + 1 if low + 1 < size else low
            chorus = dry[low] * (1 - frac) + dry[high] * frac
        echo = 0.0
        for shift, gain in taps:
            if n >= shift:
                echo += dry[n - shift] * gain
        value = keep * dry[n] + amount * (0.6 * chorus + 0.4 * echo)
        mixed[n] = value
        if abs(value) > peak:
            peak = abs(value)
    scale = min(1.0, 0.95 * 32767 / peak)
    out = array.array("h", (int(v * scale) for v in mixed))
    if sys.byteorder != "little":
        out.byteswap()
    with wave.open(str(out_path), "wb") as target:
        target.setparams(params)
        target.writeframes(out.tobytes())
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
    """Riproduzione bloccante con posizione reale per il labiale (stop_playback ferma)."""
    import audio_player
    audio_player.play(Path(path))


def stop_playback() -> None:
    try:
        import audio_player
        audio_player.stop()
    except Exception:
        pass


_PREPARED: dict[tuple, tuple[threading.Thread, dict]] = {}
_PREPARED_LOCK = threading.Lock()
_AUDIO_DIR: Path | None = None


def _audio_dir() -> Path:
    global _AUDIO_DIR
    if _AUDIO_DIR is None or not _AUDIO_DIR.is_dir():
        _AUDIO_DIR = Path(tempfile.mkdtemp(prefix="lumi-voice-"))
    return _AUDIO_DIR


def apply_pitch_volume(in_path: Path, out_path: Path, pitch: float, gain: float) -> Path:
    """Tonalità (ricampionamento: alza/abbassa e accorcia/allunga di ``pitch``,
    compensato a monte con length_scale) e volume. Senza numpy se serve."""
    with wave.open(str(in_path), "rb") as source:
        params = source.getparams()
        frames = source.readframes(params.nframes)
    if params.sampwidth != 2 or params.nchannels != 1 or (
            abs(pitch - 1.0) < 1e-3 and abs(gain - 1.0) < 1e-3):
        Path(out_path).write_bytes(Path(in_path).read_bytes())
        return Path(out_path)
    import array
    samples = array.array("h", frames)
    if sys.byteorder != "little":
        samples.byteswap()
    size = len(samples)
    length = max(1, int(size / pitch))
    try:
        import numpy as np
        src = np.asarray(samples, dtype=np.float32)
        pos = np.arange(length, dtype=np.float64) * pitch
        out = np.interp(pos, np.arange(size), src) * gain
        data = np.clip(out, -32768, 32767).astype("<i2").tobytes()
    except ImportError:
        out = array.array("h")
        for n in range(length):
            x = n * pitch
            i = int(x)
            j = i + 1 if i + 1 < size else i
            f = x - i
            v = (samples[i] * (1 - f) + samples[j] * f) * gain if i < size else 0
            out.append(max(-32768, min(32767, int(v))))
        if sys.byteorder != "little":
            out.byteswap()
        data = out.tobytes()
    with wave.open(str(out_path), "wb") as target:
        target.setparams(params)
        target.writeframes(data)
    return Path(out_path)


def _render(text: str, key: str, effect: float, folder, runner) -> Path:
    import voice_style
    style = voice_style.current()
    pitch = voice_style.pitch_factor(style)
    length_scale = pitch / voice_style.speed_factor(style)
    base = _audio_dir() / f"v{threading.get_ident()}-{id(text)}-{os.getpid()}"
    raw = synthesize(text, key, base.with_suffix(".raw.wav"), folder=folder, runner=runner,
                     length_scale=length_scale)
    styled = raw
    if abs(pitch - 1.0) > 1e-3 or style["volume"] != 100:
        styled = apply_pitch_volume(raw, base.with_suffix(".styled.wav"), pitch,
                                    voice_style.gain(style))
        raw.unlink(missing_ok=True)
    if effect > 0:
        final = apply_digital_effect(styled, base.with_suffix(".wav"), effect)
        styled.unlink(missing_ok=True)
        return final
    return styled

def prepare(text: str, key: str, *, effect: float = 0.0, folder: Path | None = None,
            runner=None) -> None:
    """Start synthesizing ``text`` in background (next sentence while one plays)."""
    import voice_style
    token = (text, key, round(effect, 3), str(folder), tuple(sorted(voice_style.current().items())))
    with _PREPARED_LOCK:
        if token in _PREPARED:
            return
        box: dict = {}

        def work():
            try:
                box["path"] = _render(text, key, effect, folder, runner)
            except Exception as exc:   # reported when the sentence is spoken
                box["error"] = exc
        thread = threading.Thread(target=work, daemon=True, name="lumi-voice-prepare")
        _PREPARED[token] = (thread, box)
    thread.start()


def speak_with_piper(text: str, key: str, *, effect: float = 0.0,
                     on_envelope=None, folder: Path | None = None,
                     runner=None, player=play_wav, upcoming: str | None = None) -> None:
    """Synthesize (or take the prefetched audio), publish lip-sync, play.

    The envelope is published right before the sound starts, so the avatar's
    mouth moves with the audio, not while the voice is still being prepared.
    """
    import voice_style
    token = (text, key, round(effect, 3), str(folder), tuple(sorted(voice_style.current().items())))
    with _PREPARED_LOCK:
        prepared = _PREPARED.pop(token, None)
    if prepared is not None:
        thread, box = prepared
        thread.join()
        if "error" in box:
            raise box["error"] if isinstance(box["error"], PiperVoiceError) else PiperVoiceError(
                "Sintesi non riuscita: " + type(box["error"]).__name__)
        final = box["path"]
    else:
        final = _render(text, key, effect, folder, runner)
    try:
        if upcoming:
            prepare(upcoming, key, effect=effect, folder=folder, runner=runner)
        if on_envelope is not None:
            on_envelope(loudness_envelope(final))
        player(final)
    finally:
        Path(final).unlink(missing_ok=True)
