"""Optional spoken replies using Windows 10's built-in SAPI voices.

Offline, no third-party packages, no clipboard, and no microphone ownership.
PowerShell receives JSON on stdin; dictated or GPT text is never interpreted
as code or inserted into the command line.
"""
from __future__ import annotations

import json
import os
import queue
import subprocess
import threading
import time
from collections.abc import Callable

# The PowerShell source is fixed. User text and voice names are JSON data on stdin.
_PS_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
Add-Type -AssemblyName System.Speech
$request = [Console]::In.ReadToEnd() | ConvertFrom-Json
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    if ($request.mode -eq 'list') {
        $voices = @($synth.GetInstalledVoices() | Where-Object { $_.Enabled } |
            ForEach-Object { $_.VoiceInfo.Name })
        ConvertTo-Json -InputObject $voices -Compress
    } elseif ($request.mode -eq 'speak') {
        if ($request.voice) { $synth.SelectVoice([string]$request.voice) }
        $synth.Rate = 0
        $synth.Speak([string]$request.text)
    } else {
        throw 'Unsupported operation'
    }
} finally {
    $synth.Dispose()
}
"""
_POWERSHELL_ENCODED = __import__("base64").b64encode(_PS_SCRIPT.encode("utf-16-le")).decode("ascii")
_MAX_SPEECH = 600
_MAX_SPEECH_MESSAGE = 2800


def _speech_chunks(text: str) -> tuple[str, ...]:
    """Bounded, word-safe SAPI chunks; never silently clip a procedure at 600."""
    text = " ".join(text.split())[:_MAX_SPEECH_MESSAGE].strip()
    parts = []
    while len(text) > _MAX_SPEECH:
        chunk = text[:_MAX_SPEECH]
        # Prefer a natural sentence boundary, but avoid tiny fragments.
        candidates = [chunk.rfind(mark) for mark in (". ", "? ", "! ", "; ")]
        cut = max(candidates)
        if cut >= _MAX_SPEECH // 2:
            cut += 1
        else:
            cut = chunk.rfind(" ")
            if cut <= 0:
                cut = _MAX_SPEECH
        parts.append(text[:cut].strip())
        text = text[cut:].strip()
    if text:
        parts.append(text)
    return tuple(parts)



def _kill_for_cleanup(process, error) -> bool:
    """Keep the primary exception if Windows refuses helper termination."""
    try:
        process.kill()
        return True
    except OSError:
        error.add_note("Impossibile terminare l'helper vocale durante la pulizia.")
        return False


def _invoke(payload: dict, *, timeout: int = 90, owner=None) -> str:
    if os.name != "nt":
        raise OSError("Risposta vocale disponibile solo su Windows.")
    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    powershell = os.path.join(system_root,"System32","WindowsPowerShell","v1.0","powershell.exe")
    command = [powershell, "-NoLogo", "-NoProfile", "-NonInteractive",
               "-EncodedCommand", _POWERSHELL_ENCODED]
    encoded_input = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    options = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                   cwd=system_root)  # Never pin the installation folder.
    if owner is None:
        completed = subprocess.run(command, input=encoded_input, timeout=timeout,
                                   check=False, **options)
        output, returncode = completed.stdout, completed.returncode
    else:
        # Creation/communicate/wait never hold the speaker metadata lock.
        process = subprocess.Popen(command, stdin=subprocess.PIPE, **options)
        try:
            with process:
                accepted = owner._attach_process(process)
                if not accepted:
                    owner._terminate_process(process)
                try:
                    # A publication rejected after close sends no speech text.
                    output, _ = process.communicate(
                        input=encoded_input if accepted else None, timeout=timeout)
                except subprocess.TimeoutExpired as error:
                    if _kill_for_cleanup(process, error):
                        try:
                            process.communicate()
                        except Exception:
                            error.add_note("Errore nel rilascio delle pipe dell'helper vocale.")
                    raise
                except BaseException as error:
                    _kill_for_cleanup(process, error)
                    raise
                if not accepted:
                    return ""
                returncode = process.returncode
        finally:
            # Keep the owned handle visible until context cleanup has closed
            # all pipes/waited for exit, including exceptional communicate.
            owner._detach_process(process)
    if returncode != 0:
        raise OSError("La sintesi vocale Windows non è disponibile.")
    return output.decode("utf-8-sig", errors="replace").strip()


def installed_voices() -> list[str]:
    """Return only voices installed locally, without network downloads."""
    raw = _invoke({"mode": "list"}, timeout=25)
    data = json.loads(raw) if raw else []
    if isinstance(data, str):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("Elenco delle voci Windows non valido.")
    windows = [name for name in data if isinstance(name, str) and name.strip()][:100]
    # Downloaded natural voices (Piper) first; Windows voices stay available.
    from piper_voice import installed_piper_voices
    return installed_piper_voices() + windows


class OfflineSpeaker:
    """Bounded, background TTS. Optional and independent of listening mode."""

    def __init__(self, runner: Callable[..., str] | None = None,
                 notify_error: Callable[[str], None] | None = None):
        self._runner = runner
        self._notify_error = notify_error
        self._messages: queue.Queue[tuple[str, str] | None] = queue.Queue(maxsize=3)
        self._busy = threading.Event()
        self._closed = threading.Event()
        self._cooldown_until = 0.0
        self._worker: threading.Thread | None = None
        self._process_lock = threading.Lock()
        self._process: subprocess.Popen | None = None
        # Natural voice options (Piper): effect 0..1 and lip-sync callback.
        self.effect = 0.0
        self.on_envelope: Callable[[list], None] | None = None
        self._piper_speaker = None

    def _attach_process(self, process) -> bool:
        with self._process_lock:
            if self._closed.is_set():
                return False
            self._process = process
            return True

    def _detach_process(self, process) -> None:
        with self._process_lock:
            if self._process is process:
                self._process = None

    def _terminate_process(self, process) -> None:
        try:
            if process.poll() is None:
                process.terminate()
        except OSError:
            if self._notify_error:
                self._notify_error("Impossibile interrompere il processo vocale di Lumi.")

    def is_audible(self) -> bool:
        """Guard recognition against the computer's own spoken output."""
        return self._busy.is_set() or time.monotonic() < self._cooldown_until

    def is_speaking(self) -> bool:
        """True only while SAPI is actually synthesizing speech, not cooldown."""
        return self._busy.is_set()

    def speak(self, text: str, voice: str = "") -> bool:
        if self._closed.is_set() or not isinstance(text, str) or not text.strip():
            return False
        if not isinstance(voice, str) or len(voice) > 180:
            return False
        snippet = " ".join(text.split())[:_MAX_SPEECH_MESSAGE]
        with self._process_lock:
            if self._closed.is_set():
                return False
            try:
                self._messages.put_nowait((snippet, voice))
            except queue.Full:
                return False
            if self._worker is None or not self._worker.is_alive():
                self._worker = threading.Thread(target=self._run, daemon=True,
                                                name="jarvis-offline-speaker")
                self._worker.start()
        return True

    def _run(self) -> None:
        while not self._closed.is_set():
            try:
                item = self._messages.get(timeout=0.3)
            except queue.Empty:
                continue
            if item is None:
                break
            text, voice = item
            if self._closed.is_set():
                break
            self._busy.set()
            try:
                from piper_voice import PiperVoiceError, key_from_label, speak_with_piper
                piper_key = key_from_label(voice)
                if piper_key is not None:
                    try:
                        speaker = self._piper_speaker or speak_with_piper
                        speaker(text, piper_key, effect=self.effect,
                                on_envelope=self.on_envelope)
                        continue
                    except PiperVoiceError as exc:
                        if self._notify_error and not self._closed.is_set():
                            self._notify_error("Voce naturale non disponibile, uso la voce "
                                               "Windows. " + str(exc)[:160])
                        voice = ""
                for part in _speech_chunks(text):
                    if self._closed.is_set():
                        break
                    payload = {"mode": "speak", "text": part, "voice": voice}
                    if self._runner is None:
                        _invoke(payload, timeout=90, owner=self)
                    else:
                        self._runner(payload, timeout=90)
            except (OSError, ValueError, subprocess.TimeoutExpired):
                if self._notify_error and not self._closed.is_set():
                    self._notify_error("Impossibile riprodurre la voce selezionata.")
            finally:
                self._cooldown_until = time.monotonic() + 1.0
                self._busy.clear()

    def close(self) -> None:
        with self._process_lock:
            if self._closed.is_set():
                return
            self._closed.set()
            while True:
                try:
                    self._messages.get_nowait()
                except queue.Empty:
                    break
            process = self._process
        if process is not None:
            self._terminate_process(process)
        from piper_voice import stop_playback
        stop_playback()
