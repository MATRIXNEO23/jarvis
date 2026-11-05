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
        self._stopping = False

    @staticmethod
    def installed_sdk() -> Path:
        base = os.environ.get("LOCALAPPDATA")
        if not base:
            return Path.home() / "AppData" / "Local" / "Jarvis" / "runtime" / "siwc" / "packages" / "local" / "dist" / "index.js"
        return Path(base) / "Jarvis" / "runtime" / "siwc" / "packages" / "local" / "dist" / "index.js"

    def start(self) -> None:
        with self._lock:
            if self._stopping:
                raise GPTUnavailable("Il collegamento GPT è in fase di arresto.")
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
        """Discard packets from a superseded child, never wake a newer one."""
        try:
            if proc.stdout:
                for line in proc.stdout:
                    try:
                        packet = json.loads(line)
                    except ValueError:
                        continue
                    if not isinstance(packet, dict):
                        continue
                    with self._lock:
                        if self._process is not proc:
                            continue
                        ident = packet.get("id")
                        target = (self._pending.get(ident)
                                  if type(ident) is int and ident > 0 else None)
                        event = packet.get("event")
                        if event == "fatal":
                            self._startup_error = str(
                                packet.get("error", "Avvio GPT fallito."))[:300]
                        if event in ("ready", "fatal"):
                            self._ready_signal.set()
                    if target is not None:
                        target.put(packet)
                    elif event in ("ready", "open_browser", "fatal"):
                        self.events.put(packet)
        finally:
            # Only the currently owned child may signal failure to current
            # callers or change readiness; stale readers cannot touch them.
            with self._lock:
                current = self._process is proc
                if current:
                    self._process = None
                    pending = list(self._pending.values())
                    if not self._ready_signal.is_set():
                        self._startup_error = "Modulo GPT terminato durante l'avvio."
                        self._ready_signal.set()
                else:
                    pending = []
            for target in pending:
                target.put({"ok": False, "error": "Servizio GPT interrotto."})
            if current:
                self.events.put({"event": "stopped"})

    def call(self, action: str, *, timeout: float = 40, authorize_send=None,
             **arguments) -> dict:
        if authorize_send is not None and not authorize_send():
            raise GPTUnavailable("Autorizzazione GPT revocata.")
        self.start()
        response: queue.Queue[dict] = queue.Queue()
        with self._lock:
            proc = self._process
            if not proc or proc.poll() is not None or not proc.stdin:
                raise GPTUnavailable("Servizio GPT non avviato.")
            if authorize_send is not None and not authorize_send():
                raise GPTUnavailable("Autorizzazione GPT revocata.")
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

    def bridge_running(self) -> bool:
        """Side-effect-free observation; no session refresh or model request."""
        with self._lock:
            proc = self._process
        return proc is not None and proc.poll() is None

    def _call_existing(self, proc: subprocess.Popen, action: str,
                       timeout: float = 3.0) -> None:
        """Shutdown request only to the owned child; NEVER call start()."""
        response: queue.Queue[dict] = queue.Queue()
        with self._lock:
            if (self._process is not proc or proc.poll() is not None
                    or not proc.stdin):
                return
            self._next_id += 1
            ident = self._next_id
            self._pending[ident] = response
            try:
                proc.stdin.write(json.dumps({"id": ident, "action": action})+"\n")
                proc.stdin.flush()
            except (OSError, ValueError):
                self._pending.pop(ident, None)
                return
        try:
            response.get(timeout=timeout)
        except queue.Empty:
            pass
        finally:
            with self._lock:
                self._pending.pop(ident, None)

    def stop(self) -> None:
        """Stop exactly the current process without accidentally respawning it."""
        with self._lock:
            if self._stopping:
                return
            self._stopping = True
            proc = self._process
        try:
            if not proc:
                return
            if proc.poll() is None:
                self._call_existing(proc, "cancel_sign_in", timeout=3)
                self._call_existing(proc, "shutdown", timeout=3)
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=2)
            with self._lock:
                if self._process is proc:
                    self._process = None
        finally:
            with self._lock:
                self._stopping = False
