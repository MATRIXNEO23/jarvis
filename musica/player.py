"""Lettore dei brani locali con MCI di Windows (nessuna dipendenza).

Un solo thread possiede il dispositivo MCI (MCI lega gli alias al thread che
li apre); la UI manda comandi in coda e riceve lo stato con ``on_state``.
Volume indipendente da quello di Windows e dalla voce di Lumi.
"""
from __future__ import annotations

import os
from pathlib import Path
import queue
import threading


def _mci(command: str) -> tuple[int, str]:
    import ctypes
    buffer = ctypes.create_unicode_buffer(128)
    code = ctypes.windll.winmm.mciSendStringW(command, buffer, 127, None)
    return code, buffer.value


class MusicPlayer:
    ALIAS = "lumimusica"

    def __init__(self, on_state=None, mci=None):
        self.on_state = on_state or (lambda state: None)
        self._mci = mci or _mci
        self._queue: queue.Queue = queue.Queue()
        self._thread = None
        self.playlist: list[Path] = []
        self.index = -1
        self.volume = 70           # 0..100
        self.state = "stopped"     # stopped | playing | paused
        self._open = False

    # --- API per la UI (qualsiasi thread) -------------------------------
    def play(self, tracks, start: int = 0):
        self._send("play", list(tracks), start)

    def pause(self):
        self._send("pause")

    def resume(self):
        self._send("resume")

    def toggle(self):
        self._send("toggle")

    def stop(self):
        self._send("stop")

    def next(self):
        self._send("next")

    def set_volume(self, value: int):
        self._send("volume", max(0, min(100, int(value))))

    def close(self):
        self._send("close")

    @property
    def title(self) -> str:
        if 0 <= self.index < len(self.playlist):
            return self.playlist[self.index].stem
        return ""

    # --- thread proprietario --------------------------------------------
    def _send(self, *command):
        if os.name != "nt" and self._mci is _mci:
            raise OSError("Lettore musicale disponibile solo su Windows.")
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run, daemon=True, name="lumi-musica")
            self._thread.start()
        self._queue.put(command)

    def _emit(self):
        try:
            self.on_state({"state": self.state, "title": self.title, "volume": self.volume,
                           "position": self.index + 1, "total": len(self.playlist)})
        except Exception:
            pass

    def _close_track(self):
        if self._open:
            self._mci(f"close {self.ALIAS}")
            self._open = False

    def _start_track(self) -> bool:
        self._close_track()
        while 0 <= self.index < len(self.playlist):
            path = self.playlist[self.index]
            code, _ = self._mci(f'open "{path}" type mpegvideo alias {self.ALIAS}')
            if code == 0:
                self._open = True
                self._mci(f"setaudio {self.ALIAS} volume to {self.volume * 10}")
                if self._mci(f"play {self.ALIAS}")[0] == 0:
                    self.state = "playing"
                    self._emit()
                    return True
                self._close_track()
            self.index += 1          # file illeggibile: passa al successivo
        self.state = "stopped"
        self.index = -1
        self._emit()
        return False

    def _handle(self, command) -> bool:
        name = command[0]
        if name == "play":
            self.playlist, self.index = command[1], max(0, command[2])
            self._start_track()
        elif name == "pause" and self.state == "playing":
            self._mci(f"pause {self.ALIAS}")
            self.state = "paused"
            self._emit()
        elif name == "resume" and self.state == "paused":
            self._mci(f"resume {self.ALIAS}")
            self.state = "playing"
            self._emit()
        elif name == "toggle":
            return self._handle(("pause",) if self.state == "playing" else ("resume",))
        elif name == "stop":
            self._close_track()
            self.state = "stopped"
            self._emit()
        elif name == "next" and self.playlist:
            self.index += 1
            if self.index >= len(self.playlist):
                self.index = 0
            self._start_track()
        elif name == "volume":
            self.volume = command[1]
            if self._open:
                self._mci(f"setaudio {self.ALIAS} volume to {self.volume * 10}")
            self._emit()
        elif name == "close":
            self._close_track()
            self.state = "stopped"
            return False
        return True

    def _run(self):
        while True:
            try:
                command = self._queue.get(timeout=0.5)
            except queue.Empty:
                command = None
            if command is not None:
                if not self._handle(command):
                    return
                continue
            if self.state == "playing" and self._open:
                mode = self._mci(f"status {self.ALIAS} mode")[1]
                if mode == "stopped":            # brano finito: il prossimo
                    self.index += 1
                    if self.index >= len(self.playlist):
                        self._close_track()
                        self.state, self.index = "stopped", -1
                        self._emit()
                    else:
                        self._start_track()
