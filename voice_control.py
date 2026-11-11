"""Offline Italian Vosk recognition with externally configured microphone mode.

Only the desktop UI decides whether listening starts automatically. Vosk and
sounddevice import on the listener thread; no model runs before that choice.
Only the trusted local command registry can execute speech automatically.
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
from pathlib import Path
from collections.abc import Callable

from settings import default_path
from speech_activity import SpeechActivity

STANDBY = "standby"
PUSH_TO_TALK = "premi_per_parlare"
CONTINUOUS = "ascolto_continuo"
GPT_CONVERSATION = "conversazione_gpt"
MODES = (STANDBY, PUSH_TO_TALK, CONTINUOUS, GPT_CONVERSATION)
MODEL_NAME = "vosk-model-small-it-0.22"


def model_directory() -> Path:
    """Share the existing read-only Vosk model with an isolated trial profile.

    The trial copies settings and memory, not the large offline speech model.
    The installed original model is read, never moved or overwritten.
    """
    preferred=default_path().parent / "models" / MODEL_NAME
    if preferred.is_dir() or not os.environ.get("JARVIS_TRIAL_HOME"):
        return preferred
    source = os.environ.get("JARVIS_TRIAL_SOURCE")
    if source:
        source_model = Path(source) / "models" / MODEL_NAME
        if source_model.is_dir():
            return source_model
    localappdata=os.environ.get("LOCALAPPDATA")
    if localappdata:
        installed=Path(localappdata)/"Jarvis"/"models"/MODEL_NAME
        if installed.is_dir():
            return installed
    return preferred


def speech_to_local_command(text: str) -> str | None:
    """Map speech to *existing*, non-destructive LocalEngine commands only."""
    if not isinstance(text, str):
        return None
    words = " ".join(text.casefold().strip(" .!?").split())
    words = re.sub(r"^(?:(?:ehi|ok)\s+)?lumi[,\s:]+", "", words)
    words = re.sub(r"^(?:per favore|gentilmente)\s+", "", words)
    words = re.sub(r"\s+per favore$", "", words)
    words = re.sub(r"^(?:mi )?(?:puoi|potresti)\s+", "", words)
    for prefix in ("cerca nel browser ", "cerca su internet "):
        if words.startswith(prefix):
            query = " ".join(words[len(prefix):].split())
            if 1 <= len(query) <= 160 and not any(ord(ch) < 32 for ch in query):
                return "cerca nel browser " + query
            return None
    opening = re.fullmatch(r"(?:apri(?:mi)?|avvia(?:mi)?|lancia(?:mi)?)\s+(?:(?:il|la|un|una)\s+)?(.+)", words)
    if opening:
        target = {
            "calcolatrice": "apri calcolatrice", "calc": "apri calcolatrice",
            "blocco note": "apri blocco note", "notepad": "apri blocco note",
            "esplora file": "apri esplora file", "esplora risorse": "apri esplora file",
            "browser": "apri browser", "browser predefinito": "apri browser",
            "download": "apri download", "cartella download": "apri download",
            "cartella dei download": "apri download",
            "disco locale c": "apri disco locale c",
            "unità c": "apri disco locale c", "unita c": "apri disco locale c",
        }.get(opening.group(1))
        if target:
            return target
    if re.fullmatch(r"(?:mostra(?:mi)?|visualizza)\s+(?:(?:la cartella dei|la cartella|i)\s+)?download", words):
        return "apri download"
    if re.fullmatch(r"(?:mostra(?:mi)?|visualizza|controlla)\s+(?:lo\s+)?stato\s+(?:del\s+)?sistema", words):
        return "stato sistema"
    exact = {
        "stato sistema": "stato sistema",
        "stato": "stato sistema",
        "stato del sistema": "stato sistema",
        "stato del computer": "stato sistema",
        "stato del pc": "stato sistema",
        "dimmi lo stato del sistema": "stato sistema",
        "dimmi lo stato del computer": "stato sistema",
        "dimmi lo stato del pc": "stato sistema",
        "dimmi come sta il computer": "stato sistema",
        "come sta il computer": "stato sistema",
        "controlla sistema": "stato sistema",
        "controlla la ram": "stato sistema",
        "ultimi comandi": "ultimi comandi",
        "cronologia": "ultimi comandi",
        "elenca download": "elenca download",
        "lista download": "elenca download",
        "aiuto": "aiuto",
        "help": "aiuto", "comandi": "aiuto",
    }
    # Deliberately exclude arbitrary file paths, programs, shell and GPT.
    return exact.get(words)


class WakeWordGate:
    """Explicit wake name for continuous listening, never a microphone mode.

    A standalone 'Ehi Lumi' arms exactly one subsequent utterance, for up to
    10 seconds (6 seconds in the modes that require the name in every command). Speech without a wake name is ignored as a command. During
    manual dictation it is text, except recognized wake commands.
    """

    # «Lumi» da solo nelle modalità che vogliono il nome in ogni comando: Lumi
    # resta in ascolto per una sola frase, entro pochi secondi (richiesta utente:
    # «almeno 2-3 secondi»; il tempo conta fino alla fine della frase riconosciuta,
    # quindi c'è margine per pronunciarla). Poi torna a ignorare la stanza.
    SHORT_WAKE_SECONDS = 6.0

    def __init__(self, *, timeout: float = 10.0,
                 clock: Callable[[], float] = time.monotonic,
                 short_timeout: float | None = None):
        self.timeout = timeout
        self.short_timeout = self.SHORT_WAKE_SECONDS if short_timeout is None else short_timeout
        self.clock = clock
        self.armed_until = 0.0

    def reset(self) -> None:
        self.armed_until = 0.0

    def route(self, speech: str, *, dictation_active: bool = False,
              require_name: bool = False) -> tuple[str, str]:
        # Passive microphone modes require a name in every command; a bare
        # name opens a SHORT window for exactly one following phrase.
        if not isinstance(speech, str) or not speech.strip():
            return "ignored", ""
        spoken = " ".join(speech.casefold().replace(",", " ").replace(":", " ").strip(" .!?").split())
        for name in ("ehi lumi", "hey lumi", "lumi"):
            if spoken == name:
                self.armed_until = self.clock() + (
                    self.short_timeout if require_name else self.timeout)
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
        # Generation-bound state of the actual Windows audio input stream.
        # Selecting a listening mode is not proof that Vosk opened a mic.
        self._active_generation = -1
        self._speech_active_until = 0.0

    def is_listening(self) -> bool:
        """Real microphone-stream state for the HUD, not a mode toggle."""
        with self._lock:
            return (not self._closed and self.mode != STANDBY
                    and self._active_generation == self._generation)

    def is_user_speaking(self) -> bool:
        """True only while actual input audio exceeds the speech threshold.

        Unlike is_listening(), this is False between spoken phrases, even
        while continuous GPT microphone capture is still running.
        """
        with self._lock:
            return (not self._closed and self.mode != STANDBY
                    and self._active_generation == self._generation
                    and time.monotonic() < self._speech_active_until)

    def set_mode(self, mode: str) -> None:
        if mode not in MODES:
            raise ValueError("Modalità microfono non valida.")
        with self._lock:
            if self._closed:
                return
            self.mode = mode
            self._generation += 1
            self._active_generation = -1
            self._speech_active_until = 0.0
            if self._stop is not None:
                self._stop.set()
            if mode == STANDBY:
                self._model = None
        if mode in (CONTINUOUS, GPT_CONVERSATION):
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
            if self._closed or self.mode not in (CONTINUOUS, GPT_CONVERSATION):
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
            self._active_generation = -1
            self._speech_active_until = 0.0
            self._model = None
            if self._stop is not None:
                self._stop.set()

    def _is_current(self, generation: int) -> bool:
        with self._lock:
            return (not self._closed and generation == self._generation
                    and self.mode != STANDBY)

    def accepts_event(self, generation: object) -> bool:
        """Recheck a queued event before the UI consumes it, including close."""
        return type(generation) is int and self._is_current(generation)

    def _report(self, kind: str, value: str, generation: int) -> None:
        if self._is_current(generation):
            self.notify((kind, value, generation))

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
            # Blocking reads last about 250 ms. The stream closes on stop/error.
            # No recordings are written to disk or sent over the network.
            with sd.RawInputStream(samplerate=16000, blocksize=4000,
                                   channels=1, dtype="int16") as stream:
                with self._lock:
                    if self._is_current(generation) and not stop.is_set():
                        self._active_generation = generation
                self._report("voice_status", "Microfono attivo — riconoscimento offline.", generation)
                fragments: list[str] = []
                suppressed = False
                activity = SpeechActivity()
                while not stop.is_set() and self._is_current(generation):
                    data, overflow = stream.read(4000)
                    pcm = bytes(data)
                    # Keep the microphone open; ignore self-generated speaker audio.
                    # Neither TTS greetings nor responses light the USER indicator.
                    if self.ignore_audio and self.ignore_audio():
                        activity.reset()
                        with self._lock:
                            if self._generation == generation:
                                self._speech_active_until = 0.0
                        if not suppressed:
                            recognizer = KaldiRecognizer(model, 16000)
                            fragments.clear()
                            suppressed = True
                        continue
                    if suppressed:
                        recognizer = KaldiRecognizer(model, 16000)
                        suppressed = False
                    activity.feed(pcm)
                    with self._lock:
                        if self._is_current(generation) and not stop.is_set():
                            self._speech_active_until = activity.active_until
                    if overflow:
                        self._report("voice_status", "Audio in ritardo: parla più lentamente.", generation)
                    if recognizer.AcceptWaveform(pcm):
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
            if not failed:
                self._report("voice_status", "Microfono spento.", generation)
            with self._lock:
                if self._active_generation == generation:
                    self._active_generation = -1
                    self._speech_active_until = 0.0
                if self._worker is threading.current_thread():
                    self._worker = None
                # A failed OBSOLETE worker must not suppress a newer,
                # explicitly selected continuous/GPT mode. Never retry when
                # the CURRENT generation fails: manual mode remains in control.
                restart = (not self._closed
                           and self.mode in (CONTINUOUS, GPT_CONVERSATION)
                           and self._generation != generation)
            if restart:
                self._start_continuous()



def model_switch_target(text: str):
    """Explicit full-phrase model selection; mentions/negations do not switch."""
    text = ' '.join(str(text).casefold().strip(' .!?').split())
    text = re.sub(r'^(?:(?:ehi|hey|ok)\s+)?lumi[\s,:;-]+', '', text)
    match = re.fullmatch(
        r'(?:passa(?:mi)?\s+a|torna\s+a|usa|utilizza|attiva|avvia)\s+'
        r'(?:il\s+modello\s+)?(gpt|chat\s*gpt|gemma)(?:\s+per favore)?', text)
    return None if match is None else match.group(1) != 'gemma'
