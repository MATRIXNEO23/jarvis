"""Standalone, lightweight Jarvis countdown pop-up and offline Windows alarms."""
from __future__ import annotations

import io
import math
import os
import re
import tempfile
import struct
import threading
import time
import wave
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk
from typing import Callable

SOUNDS = {
    "digital": "Bip digitale",
    "double": "Doppio bip",
    "electronic": "Allarme elettronico",
    "siren": "Sirena",
    "soft": "Avviso delicato",
}
RED, DIM, CYAN, BG = "#fa4d49", "#3a1b25", "#22cee9", "#061421"


@dataclass(frozen=True)
class TimerCommand:
    action: str
    seconds: int | None = None


def parse_timer_command(text: str) -> TimerCommand | None:
    """Bounded, local interpretation; never send timer commands to GPT."""
    if not isinstance(text, str) or not (0 < len(text) <= 200):
        return None
    value = " ".join(text.casefold().strip(" .,!?").split())
    value = re.sub(r"^(?:ehi\s+)?jarvis\s*[,.:]?\s*", "", value)
    if not re.search(r"\btimer\b", value):
        return None
    if re.search(r"-\s*\d", value):
        return None
    for action, expressions in (
        ("pause", ("pausa", "metti in pausa", "sospendi")),
        ("resume", ("riprendi", "continua")),
        ("stop", ("stop", "ferma", "arresta", "annulla", "spegni")),
        ("reset", ("reset", "azzera", "reimposta")),
        ("remaining", ("quanto manca", "tempo rimasto")),
    ):
        if any(expression in value for expression in expressions):
            return TimerCommand(action)
    # An unqualified "timer" opens the manual editor without starting it.
    parts = re.findall(r"(\d{1,3})\s*(ore?|minuti?|min|secondi?|sec)", value)
    seconds = 0
    if parts:
        for number, unit in parts:
            quantity = int(number)
            if unit.startswith("or"):
                seconds += quantity * 3600
            elif unit.startswith("min"):
                seconds += quantity * 60
            else:
                seconds += quantity
    else:
        numbers = re.findall(r"\d+", value)
        if len(numbers) == 1:
            seconds = int(numbers[0]) * 60
        elif numbers:
            return None
    if not 0 < seconds <= 99 * 3600 + 59 * 60 + 59:
        return TimerCommand("open") if seconds == 0 else None
    return TimerCommand("start", seconds)


def _alarm_pattern(sound: str) -> tuple[tuple[float, float], ...]:
    patterns = {
        "digital": ((980, .17), (0, .11), (980, .17), (0, .22)),
        "double": ((1050, .12), (0, .08), (1050, .12), (0, .30)),
        "electronic": ((660, .20), (880, .20), (1120, .20), (0, .15)),
        "siren": ((580, .18), (700, .18), (850, .18), (1050, .18)),
        "soft": ((523, .18), (659, .18), (784, .24), (0, .2)),
    }
    return patterns.get(sound, patterns["digital"])


def alarm_wav(sound: str = "digital", volume: int = 80) -> bytes:
    """Generate short PCM WAV wholly in memory; volume is actually applied."""
    if sound not in SOUNDS or type(volume) is not int or not 0 <= volume <= 100:
        raise ValueError("Impostazioni suoneria non valide.")
    rate, amplitude = 16000, int(18500 * volume / 100)
    samples = bytearray()
    for frequency, duration in _alarm_pattern(sound):
        count = int(rate * duration)
        for index in range(count):
            if frequency:
                # Fade in/out to prevent clicks; no files or external libraries.
                edge = min(1.0, index / 160, (count - index) / 160)
                sample = int(amplitude * max(0, edge) *
                             math.sin(2 * math.pi * frequency * index / rate))
            else:
                sample = 0
            samples.extend(struct.pack("<h", sample))
    stream = io.BytesIO()
    with wave.open(stream, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(samples)
    return stream.getvalue()


def _report_audio(callback: Callable[[bool, str], None] | None,
                  success: bool, message: str) -> None:
    """Report if an audio API was accepted, not whether speakers were heard."""
    if callback is not None:
        try:
            callback(success, message)
        except Exception:
            pass  # The window might already have closed.


def play_alarm(sound: str, volume: int, stop: threading.Event,
               *, repeat: bool = False, mode: str = "auto",
               on_status: Callable[[bool, str], None] | None = None) -> None:
    """Try WAV filename, WAV memory, beeps and a Windows system signal.

    Manual beep mode is useful when Windows accepts WAV but plays no sound.
    """
    if mode not in ("auto", "beep"):
        _report_audio(on_status, False, "Metodo audio non valido.")
        return
    if volume == 0:
        _report_audio(on_status, False, "Volume timer a 0%: aumentalo.")
        return
    try:
        import winsound
        payload = alarm_wav(sound, volume)
    except (ImportError, ValueError, OSError) as exc:
        _report_audio(on_status, False, "Audio Windows non disponibile: " + str(exc))
        return

    path = None
    if mode == "auto":
        try:
            # Close the file before asking Windows to open it.
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output:
                output.write(payload)
                path = output.name
        except OSError:
            path = None

    try:
        first = True
        while not stop.is_set():
            success, method = False, ""
            if mode == "auto" and path:
                try:
                    winsound.PlaySound(path, winsound.SND_FILENAME |
                                       winsound.SND_NODEFAULT)
                    success, method = True, "WAV di Windows"
                except (RuntimeError, OSError):
                    pass
            if mode == "auto" and not success and not stop.is_set():
                try:
                    winsound.PlaySound(payload, winsound.SND_MEMORY |
                                       winsound.SND_NODEFAULT)
                    success, method = True, "WAV in memoria"
                except (RuntimeError, OSError):
                    pass
            if not success and not stop.is_set():
                try:
                    for frequency, duration in _alarm_pattern(sound):
                        if stop.is_set():
                            break
                        if frequency:
                            winsound.Beep(int(frequency), max(1, int(duration * 1000)))
                        else:
                            stop.wait(duration)
                    if not stop.is_set():
                        success, method = True, "bip alternativo Windows"
                except (RuntimeError, OSError):
                    pass
            if not success and not stop.is_set():
                try:
                    winsound.MessageBeep()
                    success, method = True, "segnale di sistema Windows"
                except (RuntimeError, OSError):
                    pass
            if first and not stop.is_set():
                _report_audio(
                    on_status, success,
                    ("Riproduzione inviata a " + method +
                     ". Se non senti nulla, controlla l'uscita audio di Windows.")
                    if success else
                    ("Windows non riesce a riprodurre l'allarme: "
                     "controlla altoparlanti e dispositivo audio."))
                first = False
            if not success or not repeat:
                return
    finally:
        if path:
            try:
                os.unlink(path)
            except OSError:
                pass


class TimerPopup:
    """One Tk toplevel, created only on demand; main Jarvis HUD is untouched."""

    def __init__(self, root: tk.Misc, get_preferences: Callable[[], dict]):
        self.root = root
        self.get_preferences = get_preferences
        self.window: tk.Toplevel | None = None
        self.digits: tk.Canvas | None = None
        self.status: tk.StringVar | None = None
        self.hours: tk.StringVar | None = None
        self.minutes: tk.StringVar | None = None
        self.seconds: tk.StringVar | None = None
        self.duration = 600
        self.remaining = 600.0
        self.deadline = 0.0
        self.running = False
        self.paused = False
        self._last_label = ""
        self._timer_id: str | None = None
        self._alarm_stop = threading.Event()
        self._sound_generation = 0
        self.audio_feedback: tk.StringVar | None = None

    def _alive(self) -> bool:
        return self.window is not None and bool(self.window.winfo_exists())

    def show(self) -> None:
        if self._alive():
            self.window.deiconify()
            self.window.lift()
            return
        window = tk.Toplevel(self.root)
        self.window = window
        window.title("JARVIS // TIMER")
        window.geometry("390x324")
        window.resizable(False, False)
        window.configure(bg=BG)
        window.protocol("WM_DELETE_WINDOW", self.close)
        header = tk.Frame(window, bg=BG)
        header.pack(fill="x", padx=14, pady=(10, 4))
        tk.Label(header, text="◉  TIMER", fg=CYAN, bg=BG,
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        self.status = tk.StringVar(value="Pronto")
        self.audio_feedback = tk.StringVar(value="")
        tk.Label(header, textvariable=self.status, bg=BG, fg="#88b5c8",
                 font=("Segoe UI", 9)).pack(side="right")
        self.digits = tk.Canvas(window, width=360, height=90, bg="#020b12",
                                highlightthickness=1, highlightbackground="#12617c")
        self.digits.pack(padx=14, pady=(1, 9))
        editor = tk.Frame(window, bg=BG)
        editor.pack()
        self.hours = tk.StringVar(value="00")
        self.minutes = tk.StringVar(value="10")
        self.seconds = tk.StringVar(value="00")
        for label, var, limit in (("ORE", self.hours, 99),
                                  ("MIN", self.minutes, 59),
                                  ("SEC", self.seconds, 59)):
            cell = tk.Frame(editor, bg=BG)
            cell.pack(side="left", padx=12)
            tk.Label(cell, text=label, bg=BG, fg=CYAN,
                     font=("Segoe UI", 8)).pack()
            ttk.Spinbox(cell, from_=0, to=limit, width=4,
                        textvariable=var, wrap=True, justify="center").pack(pady=3)
        buttons = tk.Frame(window, bg=BG)
        buttons.pack(pady=(8, 2))
        for label, callback in (("START", self.start), ("PAUSA", self.pause),
                                ("STOP", self.stop), ("RESET", self.reset)):
            tk.Button(buttons, text=label, command=callback,
                      bg="#092c43", fg=CYAN, activebackground="#14445a",
                      activeforeground="white", relief="flat",
                      font=("Segoe UI", 9, "bold"), padx=10, pady=6
                      ).pack(side="left", padx=4)
        tk.Label(window, textvariable=self.audio_feedback, wraplength=350,
                 fg="#f1bc73", bg=BG, justify="center",
                 font=("Segoe UI", 9)).pack(padx=12, pady=(5, 0))
        self._last_label = ""
        self._draw(force=True)

    def _time_text(self) -> str:
        value = max(0, math.ceil(self.remaining - 0.001))
        hours, remainder = divmod(value, 3600)
        minutes, seconds = divmod(remainder, 60)
        return (f"{hours:02}:{minutes:02}:{seconds:02}" if hours
                else f"{minutes:02}:{seconds:02}")

    def _draw(self, *, force: bool = False) -> None:
        if not self._alive() or self.digits is None:
            return
        label = self._time_text()
        if not force and label == self._last_label:
            return
        self._last_label = label
        canvas = self.digits
        canvas.delete("digits")
        advance, colon = 39, 15
        width = sum(colon if char == ":" else advance for char in label)
        x = (360 - width) / 2
        segments = {
            "0": "abcedf", "1": "bc", "2": "abged",
            "3": "abgcd", "4": "fgbc", "5": "afgcd",
            "6": "afgecd", "7": "abc", "8": "abcdefg",
            "9": "abfgcd",
        }
        # Seven short LED bars, with an intentionally dim off-state.
        bars = {
            "a": (5, 2, 29, 8), "b": (28, 7, 34, 32),
            "c": (28, 35, 34, 60), "d": (5, 60, 29, 66),
            "e": (0, 35, 6, 60), "f": (0, 7, 6, 32),
            "g": (5, 31, 29, 37),
        }
        for char in label:
            if char == ":":
                for y in (24, 48):
                    canvas.create_oval(x+5, y, x+9, y+4,
                                       fill=RED, outline="", tags="digits")
                x += colon
                continue
            enabled = set(segments[char])
            for name, (x0,y0,x1,y1) in bars.items():
                canvas.create_rectangle(x+x0, y0+11, x+x1, y1+11,
                                        width=0, fill=RED if name in enabled else DIM,
                                        tags="digits")
            x += advance

    def _sync_inputs(self) -> None:
        if self.hours is None or self.minutes is None or self.seconds is None:
            return
        h, rem = divmod(self.duration, 3600)
        m, s = divmod(rem, 60)
        for var, value in ((self.hours, h), (self.minutes, m), (self.seconds, s)):
            var.set(f"{value:02}")

    def _read_inputs(self) -> int | None:
        try:
            h, m, s = (int(var.get()) for var in
                       (self.hours, self.minutes, self.seconds))
        except (ValueError, TypeError, AttributeError):
            return None
        if not (0 <= h <= 99 and 0 <= m < 60 and 0 <= s < 60):
            return None
        return h * 3600 + m * 60 + s

    def _cancel_tick(self) -> None:
        if self._timer_id is not None:
            try:
                self.root.after_cancel(self._timer_id)
            except tk.TclError:
                pass
            self._timer_id = None

    def _silence(self) -> None:
        self._alarm_stop.set()
        self._sound_generation += 1

    def _audio_result(self, generation: int, success: bool, message: str) -> None:
        def apply() -> None:
            if generation != self._sound_generation or not self._alive():
                return
            if self.audio_feedback is not None:
                self.audio_feedback.set(message)
            if not success and self.status is not None:
                self.status.set("ERRORE AUDIO")
        try:
            self.root.after(0, apply)
        except (RuntimeError, tk.TclError):
            pass

    def start(self, seconds: int | None = None) -> bool:
        self.show()
        if seconds is None and self.paused and self.remaining > 0:
            self.resume()
            return True
        duration = seconds if seconds is not None else self._read_inputs()
        if duration is None or not 1 <= duration <= 359999:
            self.status.set("Indica un tempo valido.")
            return False
        self._silence()
        self._cancel_tick()
        if self.audio_feedback is not None:
            self.audio_feedback.set("")
        self.duration = duration
        self.remaining = float(duration)
        self.deadline = time.monotonic() + duration
        self.running = True
        self.paused = False
        self._sync_inputs()
        self.status.set("Conto alla rovescia")
        self._draw(force=True)
        self._tick()
        return True

    def _tick(self) -> None:
        self._timer_id = None
        if not self.running:
            return
        self.remaining = max(0.0, self.deadline - time.monotonic())
        self._draw()
        if self.remaining <= 0:
            self.running = False
            self.paused = False
            self.status.set("ALLARME")
            self._silence()
            self._alarm_stop = threading.Event()
            generation = self._sound_generation
            if self.audio_feedback is not None:
                self.audio_feedback.set("Tentativo di riproduzione dell'allarme...")
            pref = self.get_preferences()
            threading.Thread(target=play_alarm,
                             args=(pref.get("timer_sound", "digital"),
                                   pref.get("timer_volume", 80), self._alarm_stop),
                             kwargs={"repeat": pref.get("timer_repeat", True),
                                     "mode": pref.get("timer_audio_mode", "auto"),
                                     "on_status": lambda success, message:
                                     self._audio_result(generation, success, message)},
                             daemon=True, name="jarvis-timer-alarm").start()
        else:
            self._timer_id = self.root.after(200, self._tick)

    def pause(self) -> None:
        if self.running:
            self.remaining = max(0, self.deadline - time.monotonic())
            self.running = False
            self.paused = True
            self._cancel_tick()
            self.status.set("In pausa")
            self._draw()

    def resume(self) -> None:
        if self.running:
            return
        if self.remaining <= 0:
            return
        self.show()
        self._silence()
        self.deadline = time.monotonic() + self.remaining
        self.running = True
        self.paused = False
        self.status.set("Conto alla rovescia")
        self._tick()

    def stop(self) -> None:
        self.running = False
        self.paused = False
        self._cancel_tick()
        self._silence()
        if self._alive():
            self.status.set("Fermato")
            if self.audio_feedback is not None:
                self.audio_feedback.set("")

    def reset(self) -> None:
        self.stop()
        self.remaining = float(self.duration)
        if self._alive():
            self._sync_inputs()
            self.status.set("Pronto")
            self._draw(force=True)

    def remaining_text(self) -> str:
        if self.running:
            self.remaining = max(0, self.deadline - time.monotonic())
        return self._time_text()

    def close(self) -> None:
        self.stop()
        if self._alive():
            self.window.destroy()
        self.window = None
        self.digits = None


def preview_sound(sound: str, volume: int, *,
                  mode: str = "auto",
                  on_status: Callable[[bool, str], None] | None = None) -> None:
    """Play one sample and report the audio result to settings."""
    threading.Thread(target=play_alarm,
                     args=(sound, volume, threading.Event()),
                     kwargs={"mode": mode, "on_status": on_status},
                     daemon=True, name="jarvis-timer-preview").start()
