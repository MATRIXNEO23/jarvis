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


def _invoke(payload: dict, *, timeout: int = 90) -> str:
    if os.name != "nt":
        raise OSError("Risposta vocale disponibile solo su Windows.")
    command = ["powershell.exe", "-NoLogo", "-NoProfile", "-NonInteractive",
               "-EncodedCommand", _POWERSHELL_ENCODED]
    encoded_input = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    completed = subprocess.run(
        command, input=encoded_input, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, timeout=timeout, check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0:
        raise OSError("La sintesi vocale Windows non è disponibile.")
    return completed.stdout.decode("utf-8-sig", errors="replace").strip()


def installed_voices() -> list[str]:
    """Return only voices installed locally, without network downloads."""
    raw = _invoke({"mode": "list"}, timeout=25)
    data = json.loads(raw) if raw else []
    if isinstance(data, str):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("Elenco delle voci Windows non valido.")
    return [name for name in data if isinstance(name, str) and name.strip()][:100]


class OfflineSpeaker:
    """Bounded, background TTS. Optional and independent of listening mode."""

    def __init__(self, runner: Callable[..., str] = _invoke):
        self._runner = runner
        self._messages: queue.Queue[tuple[str, str] | None] = queue.Queue(maxsize=3)
        self._busy = threading.Event()
        self._closed = threading.Event()
        self._cooldown_until = 0.0
        self._worker: threading.Thread | None = None

    def is_audible(self) -> bool:
        """Guard recognition against the computer's own spoken output."""
        return self._busy.is_set() or time.monotonic() < self._cooldown_until

    def speak(self, text: str, voice: str = "") -> bool:
        if self._closed.is_set() or not isinstance(text, str) or not text.strip():
            return False
        if not isinstance(voice, str) or len(voice) > 180:
            return False
        snippet = " ".join(text.split())[:_MAX_SPEECH]
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
                self._runner({"mode": "speak", "text": text, "voice": voice},
                             timeout=90)
            except (OSError, ValueError, subprocess.TimeoutExpired):
                pass  # Spoken output is optional; never break the local command.
            finally:
                self._cooldown_until = time.monotonic() + 1.0
                self._busy.clear()

    def close(self) -> None:
        self._closed.set()
        while True:
            try:
                self._messages.get_nowait()
            except queue.Empty:
                break
