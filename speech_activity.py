"""Tiny energy-based voice activity indicator for the LUMI reactor.

The recognizer still uses Vosk. This module is ONLY a status light:
it never opens the microphone, changes listening modes, stores audio, or
authorizes/forwards words. Its approximate detection can also react to noise.
"""
from __future__ import annotations

from array import array
from math import isqrt
import sys
import time


def pcm16_rms(pcm: bytes) -> int:
    """Sample mono signed 16-bit LE microphone PCM without extra packages."""
    if not isinstance(pcm, (bytes, bytearray)) or len(pcm) < 2:
        return 0
    # Audio callbacks from sounddevice use 16-bit little-endian samples.
    size = len(pcm) - len(pcm) % 2
    samples = array("h")
    samples.frombytes(pcm[:size])
    if sys.byteorder != "little":
        samples.byteswap()
    if not samples:
        return 0
    # 16 kHz * 250 ms block: sample every fourth point (~1000 samples).
    total = 0
    count = 0
    for index in range(0, len(samples), 4):
        value = samples[index]
        total += value * value
        count += 1
    return isqrt(total // max(1, count))


class SpeechActivity:
    """Adaptive background floor plus a short release tail for visual pulses."""

    def __init__(self, *, min_rms: int = 240,
                 release_seconds: float = 0.63) -> None:
        self.min_rms = max(80, int(min_rms))
        self.release_seconds = min(2.0, max(.2, float(release_seconds)))
        self.background: float | None = None
        self.active_until = 0.0

    def feed(self, pcm: bytes, *, now: float | None = None) -> bool:
        when = time.monotonic() if now is None else float(now)
        rms = pcm16_rms(pcm)
        if self.background is None:
            # First 250 ms calibrate room noise, without falsely marking
            # microphone initialization as somebody speaking.
            self.background = float(max(75, rms))
            return False
        threshold = max(self.min_rms, self.background * 2.4)
        if rms >= threshold and rms > 0:
            self.active_until = when + self.release_seconds
        elif when >= self.active_until:
            # Background adapts mostly during idle; quick downward recovery.
            rate = .13 if rms < self.background else .045
            self.background = max(
                55.0, self.background * (1.0 - rate) + rms * rate)
        return self.is_active(now=when)

    def is_active(self, *, now: float | None = None) -> bool:
        when = time.monotonic() if now is None else float(now)
        return self.active_until > when

    def reset(self) -> None:
        """Call whenever TTS audio is playing or a mic stream stops."""
        self.background = None
        self.active_until = 0.0
