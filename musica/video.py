"""Riquadro video al posto del globo: LumiVideo.exe (WebView2) incorporato.

Stesso riquadro per i video della cartella (<video> HTML5) e per YouTube
(lettore ufficiale incorporato, IFrame Player API: l'audio non viene estratto).
Processo separato: se WebView2 manca o va in errore, Lumi non si chiude e la
musica torna al browser. Avviato solo quando serve, chiuso quando finisce.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import threading

HOST = Path(__file__).resolve().parent / "video_bin" / "LumiVideo.exe"
VIDEO_EXTENSIONS = frozenset((".mp4", ".webm", ".m4v", ".mov"))


def available() -> bool:
    return os.name == "nt" and HOST.is_file()


class VideoPanel:
    def __init__(self, data_dir: Path, on_event=None, popen=subprocess.Popen):
        self.data_dir = Path(data_dir)
        self.on_event = on_event or (lambda event: None)
        self.popen = popen
        self.proc = None
        self.state = "stopped"
        self.position = 0.0
        self._lock = threading.Lock()

    def start(self, parent_hwnd: int) -> None:
        with self._lock:
            if self.proc is not None and self.proc.poll() is None:
                return
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.proc = self.popen(
                [str(HOST), str(int(parent_hwnd)), str(self.data_dir)],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                text=True, encoding="utf-8",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            threading.Thread(target=self._read, args=(self.proc,), daemon=True,
                             name="lumi-video-events").start()

    def _read(self, proc) -> None:
        for line in proc.stdout:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if not isinstance(event, dict):
                continue
            if event.get("ev") == "state":
                self.state = str(event.get("state"))
            elif event.get("ev") == "position":
                try:
                    self.position = float(event.get("seconds") or 0)
                except (TypeError, ValueError):
                    pass
            try:
                self.on_event(event)
            except Exception:
                pass
        self.state = "stopped"
        try:
            self.on_event({"ev": "closed"})
        except Exception:
            pass

    def send(self, **command) -> bool:
        proc = self.proc
        if proc is None or proc.poll() is not None:
            return False
        try:
            proc.stdin.write(json.dumps(command) + "\n")
            proc.stdin.flush()
            return True
        except OSError:
            return False

    def youtube(self, video_id: str) -> bool:
        return self.send(cmd="youtube", id=video_id)

    def file(self, path: Path) -> bool:
        return self.send(cmd="file", path=str(path))

    def close(self) -> None:
        with self._lock:
            proc, self.proc = self.proc, None
        if proc is not None:
            self.send_to(proc, cmd="quit")
            try:
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except OSError:
                    pass
        self.state = "stopped"

    @staticmethod
    def send_to(proc, **command) -> None:
        try:
            proc.stdin.write(json.dumps(command) + "\n")
            proc.stdin.flush()
        except (OSError, ValueError):
            pass
