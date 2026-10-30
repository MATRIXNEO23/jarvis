"""Optional offline Italian speech recognition. Microphone starts OFF, always.

Vosk and sounddevice are imported only in the explicitly requested listener
thread. No microphone access, model loading or network at application startup.
Only the trusted local command registry can execute speech automatically.
"""
from __future__ import annotations

import json
import re
import threading
import time
from pathlib import Path
from collections.abc import Callable

from settings import default_path

STANDBY = "standby"
PUSH_TO_TALK = "premi_per_parlare"
CONTINUOUS = "ascolto_continuo"
MODES = (STANDBY, PUSH_TO_TALK, CONTINUOUS)
MODEL_NAME = "vosk-model-small-it-0.22"


def model_directory() -> Path:
    return default_path().parent / "models" / MODEL_NAME


def speech_to_local_command(text: str) -> str | None:
    """Map speech to *existing*, non-destructive LocalEngine commands only."""
    if not isinstance(text, str):
        return None
    words = " ".join(text.casefold().strip(" .!?").split())
    words = re.sub(r"^(?:(?:ehi|ok)\s+)?jarvis[,\s:]+", "", words)
    for prefix in ("cerca nel browser ", "cerca su internet "):
        if words.startswith(prefix):
            query = " ".join(words[len(prefix):].split())
            if 1 <= len(query) <= 160 and not any(ord(ch) < 32 for ch in query):
                return "cerca nel browser " + query
            return None
    exact = {
        "apri calcolatrice": "apri calcolatrice",
        "apri la calcolatrice": "apri calcolatrice",
        "apri blocco note": "apri blocco note",
        "apri il blocco note": "apri blocco note",
        "apri esplora file": "apri esplora file",
        "apri browser": "apri browser",
        "apri il browser": "apri browser",
        "apri browser predefinito": "apri browser",
        "apri esplora risorse": "apri esplora file",
        "apri download": "apri download",
        "apri la cartella download": "apri download",
        "mostra download": "mostra download",
        "mostra i download": "mostra download",
        "stato sistema": "stato sistema",
        "controlla la ram": "stato sistema",
        "ultimi comandi": "ultimi comandi",
        "aiuto": "aiuto",
    }
    # Deliberately exclude arbitrary file paths, programs, shell and GPT.
    return exact.get(words)


class WakeWordGate:
    """Explicit wake name for continuous listening, never a microphone mode.

    A standalone 'Ehi Jarvis' arms exactly one subsequent utterance, for up to
    10 seconds. Speech without a wake name is ignored as a command. During
    manual dictation it is text, except recognized wake commands.
    """

    def __init__(self, *, timeout: float = 10.0,
                 clock: Callable[[], float] = time.monotonic):
        self.timeout = timeout
        self.clock = clock
        self.armed_until = 0.0

    def reset(self) -> None:
        self.armed_until = 0.0

    def route(self, speech: str, *, dictation_active: bool = False) -> tuple[str, str]:
        if not isinstance(speech, str) or not speech.strip():
            return "ignored", ""
        spoken = " ".join(speech.casefold().replace(",", " ").replace(":", " ").strip(" .!?").split())
        for name in ("ehi jarvis", "hey jarvis", "jarvis"):
            if spoken == name:
                self.armed_until = self.clock() + self.timeout
                return "wake", ""
            if spoken.startswith(name + " "):
                self.reset()
                return "command", spoken[len(name):].strip()
        if self.clock() < self.armed_until:
            self.reset()
            return "command", spoken
        self.reset()
        if dictation_active:
            return "dictation", speech
        return "ignored", ""


class VoiceController:
    """Three user-selected modes, serialized audio worker and revocable audio.

    A change of mode never happens automatically; failures leave the selected
    mode unchanged but close the microphone. No auto-retry after audio errors.
    """

    def __init__(self, notify: Callable[[tuple], None],
                 model_dir: Path | None = None,
                 ignore_audio: Callable[[], bool] | None = None):
        self.notify = notify
        self.ignore_audio = ignore_audio
        self.model_dir = Path(model_dir) if model_dir else model_directory()
        self.mode = STANDBY
        self._lock = threading.RLock()
        self._stop: threading.Event | None = None
        self._worker: threading.Thread | None = None
        self._generation = 0
        self._closed = False
        self._model = None

    def set_mode(self, mode: str) -> None:
        if mode not in MODES:
            raise ValueError("Modalità microfono non valida.")
        with self._lock:
            if self._closed:
                return
            self.mode = mode
            self._generation += 1
            if self._stop is not None:
                self._stop.set()
            if mode == STANDBY:
                self._model = None
        if mode == CONTINUOUS:
            self._start_continuous()

    def _begin_locked(self) -> None:
        stop = threading.Event()
        generation = self._generation
        self._stop = stop
        self._worker = threading.Thread(
            target=self._listen, args=(stop, generation),
            name="jarvis-offline-microphone", daemon=True
        )
        self._worker.start()

    def _start_continuous(self) -> None:
        with self._lock:
            if self._closed or self.mode != CONTINUOUS:
                return
            if self._worker is None or not self._worker.is_alive():
                self._begin_locked()

    def press(self) -> bool:
        with self._lock:
            if self._closed or self.mode != PUSH_TO_TALK:
                return False
            if self._worker is not None and self._worker.is_alive():
                return False
            self._begin_locked()
            return True

    def release(self) -> None:
        with self._lock:
            if self.mode == PUSH_TO_TALK and self._stop is not None:
                self._stop.set()

    def close(self) -> None:
        with self._lock:
            self._closed = True
            self.mode = STANDBY
            self._generation += 1
            self._model = None
            if self._stop is not None:
                self._stop.set()

    def _is_current(self, generation: int) -> bool:
        with self._lock:
            return (not self._closed and generation == self._generation
                    and self.mode != STANDBY)

    def _report(self, kind: str, value: str, generation: int) -> None:
        if self._is_current(generation):
            self.notify((kind, value))

    def _listen(self, stop: threading.Event, generation: int) -> None:
        failed = False
        try:
            if not self.model_dir.is_dir():
                raise RuntimeError(
                    "Modello italiano mancante: installa la voce seguendo docs/VOCE_OFFLINE.md."
                )
            try:
                import sounddevice as sd
                from vosk import Model, KaldiRecognizer
            except ImportError as exc:
                raise RuntimeError(
                    "Componenti vocali mancanti: esegui installa_voce.bat."
                ) from exc
            with self._lock:
                model = self._model
            if model is None:
                model = Model(str(self.model_dir))
                with self._lock:
                    if self._is_current(generation) and not stop.is_set():
                        self._model = model
            if stop.is_set() or not self._is_current(generation):
                return
            recognizer = KaldiRecognizer(model, 16000)
            self._report("voice_status", "Microfono attivo — riconoscimento offline.", generation)
            # Blocking reads last about 250 ms. The stream closes on stop/error.
            # No recordings are written to disk or sent over the network.
            with sd.RawInputStream(samplerate=16000, blocksize=4000,
                                   channels=1, dtype="int16") as stream:
                fragments: list[str] = []
                suppressed = False
                while not stop.is_set() and self._is_current(generation):
                    data, overflow = stream.read(4000)
                    # Keep the microphone open; ignore self-generated speaker audio.
                    if self.ignore_audio and self.ignore_audio():
                        if not suppressed:
                            recognizer = KaldiRecognizer(model, 16000)
                            fragments.clear()
                            suppressed = True
                        continue
                    if suppressed:
                        recognizer = KaldiRecognizer(model, 16000)
                        suppressed = False
                    if overflow:
                        self._report("voice_status", "Audio in ritardo: parla più lentamente.", generation)
                    if recognizer.AcceptWaveform(bytes(data)):
                        part = json.loads(recognizer.Result()).get("text", "").strip()
                        if part:
                            if self.mode == PUSH_TO_TALK:
                                fragments.append(part)
                            else:
                                self._report("voice_text", part, generation)
                if self._is_current(generation) and self.mode == PUSH_TO_TALK:
                    final = json.loads(recognizer.FinalResult()).get("text", "").strip()
                    message = " ".join([*fragments, final]).strip()
                    if message:
                        self._report("voice_text", message, generation)
        except Exception as exc:
            failed = True
            self._report("voice_status", "Voce non disponibile: " + str(exc)[:220], generation)
        finally:
            self._report("voice_status", "Microfono spento.", generation)
            with self._lock:
                if self._worker is threading.current_thread():
                    self._worker = None
                restart = (not failed and not self._closed
                           and self.mode == CONTINUOUS
                           and self._generation != generation)
            if restart:
                self._start_continuous()
