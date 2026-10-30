"""Windows-only ChatGPT DevKit child process client.

Pipe protocol: one JSON message per line, private to Jarvis. The Node child
owns the OAuth flow and encrypted credentials. No ChatGPT API key is accepted.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading


class GPTUnavailable(RuntimeError):
    pass


class GPTClient:
    def __init__(self, app_dir: Path | None = None) -> None:
        self.app_dir = Path(app_dir) if app_dir else Path(__file__).resolve().parent
        self.events: queue.Queue[dict] = queue.Queue()
        self._lock = threading.Lock()
        self._next_id = 0
        self._pending: dict[int, queue.Queue[dict]] = {}
        self._process: subprocess.Popen | None = None
        self._ready_signal = threading.Event()
        self._startup_error: str | None = None

    @staticmethod
    def installed_sdk() -> Path:
        base = os.environ.get("LOCALAPPDATA")
        if not base:
            return Path.home() / "AppData" / "Local" / "Jarvis" / "runtime" / "siwc" / "packages" / "local" / "dist" / "index.js"
        return Path(base) / "Jarvis" / "runtime" / "siwc" / "packages" / "local" / "dist" / "index.js"

    def start(self) -> None:
        with self._lock:
            if self._process and self._process.poll() is None:
                signal = self._ready_signal
            else:
                if os.name != "nt":
                    raise GPTUnavailable("Il collegamento GPT richiede Windows 10/11.")
                if not self.installed_sdk().is_file():
                    raise GPTUnavailable("SDK GPT non installato. Esegui installa_gpt.ps1.")
                node = shutil.which("node")
                if not node:
                    raise GPTUnavailable("Node.js 22 o successivo non trovato nel PATH.")
                script = self.app_dir / "gpt_bridge.mjs"
                if not script.is_file():
                    raise GPTUnavailable("Manca il modulo gpt_bridge.mjs.")
                flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
                self._startup_error = None
                self._ready_signal = threading.Event()
                signal = self._ready_signal
                try:
                    self._process = subprocess.Popen(
                        [node, str(script)], cwd=str(self.app_dir),
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
                        errors="replace", bufsize=1, creationflags=flags,
                    )
                except OSError as exc:
                    raise GPTUnavailable(f"Impossibile avviare GPT: {exc}") from exc
                proc = self._process
                threading.Thread(target=self._read_loop, args=(proc,), daemon=True,
                                 name="jarvis-gpt-pipe").start()
        # The JS bridge builds the SDK asynchronously. No request may be sent
        # before its explicit 'ready' packet, otherwise piped input is lost.
        if not signal.wait(timeout=45):
            raise GPTUnavailable("Timeout durante l'avvio del modulo GPT.")
        with self._lock:
            if self._startup_error:
                raise GPTUnavailable(self._startup_error)
            if not self._process or self._process.poll() is not None:
                raise GPTUnavailable("Il modulo GPT è terminato prima di essere pronto.")

    def _read_loop(self, proc: subprocess.Popen) -> None:
        try:
            if proc.stdout:
                for line in proc.stdout:
                    try:
                        packet = json.loads(line)
                    except ValueError:
                        continue
                    if not isinstance(packet, dict):
                        continue
                    ident = packet.get("id")
                    if isinstance(ident, int) and ident > 0:
                        with self._lock:
                            target = self._pending.get(ident)
                        if target:
                            target.put(packet)
                    elif packet.get("event") in ("ready", "open_browser", "fatal"):
                        if packet.get("event") == "ready":
                            self._ready_signal.set()
                        elif packet.get("event") == "fatal":
                            with self._lock:
                                self._startup_error = str(
                                    packet.get("error", "Avvio GPT fallito.")
                                )[:300]
                            self._ready_signal.set()
                        self.events.put(packet)
        finally:
            # An unexpected exit releases blocked callers rather than hanging.
            with self._lock:
                if self._process is proc:
                    self._process = None
                pending = list(self._pending.values())
            for target in pending:
                target.put({"ok": False, "error": "Servizio GPT interrotto."})
            if not self._ready_signal.is_set():
                with self._lock:
                    self._startup_error = "Modulo GPT terminato durante l'avvio."
                self._ready_signal.set()
            self.events.put({"event": "stopped"})

    def call(self, action: str, *, timeout: float = 40, **arguments) -> dict:
        self.start()
        response: queue.Queue[dict] = queue.Queue()
        with self._lock:
            proc = self._process
            if not proc or proc.poll() is not None or not proc.stdin:
                raise GPTUnavailable("Servizio GPT non avviato.")
            self._next_id += 1
            request_id = self._next_id
            self._pending[request_id] = response
            payload = json.dumps({"id": request_id, "action": action, **arguments}, ensure_ascii=False)
            try:
                proc.stdin.write(payload + "\n")
                proc.stdin.flush()
            except (OSError, ValueError) as exc:
                self._pending.pop(request_id, None)
                raise GPTUnavailable("Comunicazione con GPT non disponibile.") from exc
        try:
            reply = response.get(timeout=timeout)
            if reply.get("ok") is not True:
                raise GPTUnavailable(str(reply.get("error", "Operazione GPT fallita."))[:500])
            result = reply.get("result")
            return result if isinstance(result, dict) else {"value": result}
        except queue.Empty as exc:
            raise GPTUnavailable("GPT non ha risposto entro il limite previsto.") from exc
        finally:
            with self._lock:
                self._pending.pop(request_id, None)

    def stop(self) -> None:
        with self._lock:
            proc = self._process
        if not proc:
            return
        if proc.poll() is None:
            try:
                self.call("cancel_sign_in", timeout=3)
            except (GPTUnavailable, OSError):
                pass
            try:
                self.call("shutdown", timeout=3)
            except (GPTUnavailable, OSError):
                pass
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
        with self._lock:
            if self._process is proc:
                self._process = None
