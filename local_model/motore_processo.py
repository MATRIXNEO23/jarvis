"""Motore del modello locale in un processo separato (interno a Lumi, nessuna seconda app).

Perché: la DLL di KoboldCpp, una volta caricata nel processo di Lumi, non si scarica
(native_chat_adapter: «serve un riavvio»). Nel processo figlio lo stesso motore
(stesso `NativeChatAdapter`, stessa DLL, stessi template) si chiude e si riavvia senza
chiudere Lumi: cambio modello, «riavvia il modello», memoria liberata subito. Se il
modello si blocca o cade, cade solo il figlio.

Comunicazione: righe JSON. Lumi → figlio su stdin; figlio → Lumi su una copia del
vecchio stdout (il vero stdout del figlio va nel registro, perché il motore C stampa).
Nessuna rete, nessuna porta. Scelta nelle impostazioni (motore.json); se spenta resta
il motore dentro Lumi come prima.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


# --- scelta nelle impostazioni ------------------------------------------------------------
def _settings_path() -> Path:
    from .native_settings import default_native_settings_path
    return default_native_settings_path().with_name("motore.json")


def separate_enabled() -> bool:
    try:
        return bool(json.loads(_settings_path().read_text(encoding="utf-8")).get("separato"))
    except (OSError, ValueError, AttributeError):
        return False


def set_separate(value: bool) -> None:
    path = _settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"separato": bool(value)}), encoding="utf-8")
    os.replace(tmp, path)


def adattatore(source):
    """L'adattatore da usare per la sessione: separato se scelto, altrimenti come prima."""
    if separate_enabled():
        return ProcessChatAdapter(source)
    from .native_chat_adapter import NativeChatAdapter
    return NativeChatAdapter(source)


# --- lato Lumi ------------------------------------------------------------------------------
class EngineStopped(RuntimeError):
    pass


class ProcessChatAdapter:
    """Stessa interfaccia di NativeChatAdapter, ma il motore vive in un processo figlio."""

    def __init__(self, source, *, command=None):
        self.source = source
        self.config = None
        self._command = command
        self._proc = None
        self._lock = threading.RLock()        # una richiesta alla volta (come la sessione)
        self._counts = None

    # processo ----------------------------------------------------------------------------
    def _start(self):
        command = self._command or [sys.executable, "-u", "-m", "local_model.motore_processo",
                                    "--figlio", str(self.source)]
        log = _settings_path().with_name("motore.log")
        try:
            log.parent.mkdir(parents=True, exist_ok=True)
            err = open(log, "ab")
        except OSError:
            err = subprocess.DEVNULL
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        self._proc = subprocess.Popen(command, cwd=str(ROOT), stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE, stderr=err, creationflags=flags)
        if err is not subprocess.DEVNULL:
            err.close()

    def _send(self, message, *, on_stream=None, timeout=None):
        proc = self._proc
        if proc is None or proc.poll() is not None:
            raise EngineStopped("Motore del modello locale non attivo.")
        try:
            proc.stdin.write((json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8"))
            proc.stdin.flush()
        except (OSError, ValueError) as exc:
            raise EngineStopped("Motore del modello locale chiuso.") from exc
        deadline = None if timeout is None else time.monotonic() + timeout + 60
        watchdog = None
        if deadline is not None:
            watchdog = threading.Timer(timeout + 60, lambda: proc.poll() is None and proc.kill())
            watchdog.daemon = True
            watchdog.start()
        try:
            while True:
                line = proc.stdout.readline()
                if not line:
                    raise EngineStopped("Il motore del modello locale si è fermato.")
                reply = json.loads(line.decode("utf-8"))
                if "stream" in reply:
                    if on_stream is not None:
                        on_stream(reply["stream"])
                    continue
                if "error" in reply:
                    raise _error(reply)
                return reply.get("result")
        finally:
            if watchdog is not None:
                watchdog.cancel()

    # interfaccia NativeChatAdapter ---------------------------------------------------------
    def prepare(self, *, config=None):
        from .native_config import NativeModelConfig
        from .native_settings import RELOAD_FIELDS, default_native_settings_path
        if config is None:
            config = NativeModelConfig.load(default_native_settings_path())
        if not isinstance(config, NativeModelConfig):
            raise TypeError("Configurazione nativa richiesta.")
        config.validate()
        with self._lock:
            previous = self.config
            changed = previous is not None and any(
                getattr(previous, f) != getattr(config, f) for f in RELOAD_FIELDS | {"dll"})
            if changed:
                self._stop_process()          # modello diverso: nuovo motore, niente riavvio di Lumi
            if self._proc is None or self._proc.poll() is not None:
                self._start()
            result = self._send({"op": "prepare", "config": asdict(config)})
            self._counts = bool(result and result.get("counts"))
            self.config = config

    def context_token_counter(self):
        if self._proc is None or self.config is None:
            raise RuntimeError("Native model not prepared")
        if not self._counts:
            return None

        def count(prompt):
            with self._lock:
                return int(self._send({"op": "count", "prompt": prompt}))
        return count

    def call(self, action, *, timeout=120, prompt_budget=None, **arguments):
        if action != "ask":
            raise ValueError("Native adapter supports ask only")
        from .token_stream import current
        callback = current()
        with self._lock:
            return self._send({"op": "ask", "timeout": timeout, "prompt_budget": prompt_budget,
                               "arguments": arguments, "stream": callback is not None},
                              on_stream=callback, timeout=timeout)

    def stop(self):
        # Come NativeChatAdapter.stop: la prossima richiesta ricarica il modello. Qui il
        # processo si chiude davvero e la memoria del modello si libera subito.
        self._stop_process()
        self.config = None

    def _stop_process(self):
        proc, self._proc = self._proc, None
        if proc is None:
            return
        try:
            proc.kill()
            proc.wait(timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            pass
        for stream in (proc.stdin, proc.stdout):
            try:
                stream.close()
            except (OSError, AttributeError):
                pass


def _error(reply):
    from .native_bridge import NativeRestartRequired
    kinds = {"ValueError": ValueError, "TypeError": TypeError, "TimeoutError": TimeoutError,
             "NativeRestartRequired": NativeRestartRequired}
    return kinds.get(reply.get("error"), RuntimeError)(reply.get("message", "Errore del motore."))


# --- lato figlio ------------------------------------------------------------------------------
def _child(source):
    proto = os.fdopen(os.dup(1), "w", encoding="utf-8", buffering=1)
    os.dup2(2, 1)                              # le stampe del motore vanno nel registro
    sys.stdout = sys.stderr
    write_lock = threading.Lock()

    def send(message):
        with write_lock:
            proto.write(json.dumps(message, ensure_ascii=False) + "\n")
            proto.flush()

    from .native_chat_adapter import NativeChatAdapter
    from .native_config import NativeModelConfig
    from .token_stream import streaming
    adapter = NativeChatAdapter(source)
    for line in sys.stdin:
        try:
            request = json.loads(line)
            op = request.get("op")
            if op == "prepare":
                adapter.prepare(config=NativeModelConfig(**request["config"]))
                send({"result": {"counts": adapter.context_token_counter() is not None}})
            elif op == "count":
                send({"result": adapter.context_token_counter()(request["prompt"])})
            elif op == "ask":
                sink = (lambda text: send({"stream": text})) if request.get("stream") else None
                with streaming(sink):
                    result = adapter.call("ask", timeout=request.get("timeout", 120),
                                          prompt_budget=request.get("prompt_budget"),
                                          **request.get("arguments", {}))
                send({"result": result})
            else:
                send({"error": "ValueError", "message": "Operazione sconosciuta."})
        except Exception as exc:              # noqa: BLE001 — l'errore torna a Lumi
            send({"error": type(exc).__name__, "message": str(exc)[:500]})
    adapter.stop()


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--figlio":
        _child(sys.argv[2])
