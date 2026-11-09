"""F5.3b: opt-in lifecycle of an EXPLICITLY owned local model subprocess.

No default executable, model, network, server startup or Jarvis wiring.
No shell; the caller must validate its own executable/model, CLI flags and
loopback configuration before supplying a command. This module never kills
unrelated processes or treats abort of the embedded DLL as verified unload.
"""
import subprocess
import threading
import math


class OwnedProcessError(RuntimeError):
    """Safe lifecycle failure; no command, model or private prompt in errors."""


class OwnedModelProcess:
    """Owns exactly one directly spawned subprocess, without external PID lookup.

    An exited child is positively released using wait(); failure to wait
    leaves the instance blocked. The owner must explicitly call start().
    """

    def __init__(self, *, spawn=None):
        self._spawn = spawn or subprocess.Popen
        self._lock = threading.RLock()
        self._child = None
        self._blocked = False

    @property
    def blocked(self):
        with self._lock:
            return self._blocked

    def start(self, command, *, cwd=None):
        """Launch only after explicit caller selection; never invoke a shell."""
        if (type(command) not in (list, tuple) or not command
                or any(type(x) is not str or not x or "\x00" in x for x in command)):
            raise OwnedProcessError("Invalid explicit local command")
        if cwd is not None and (type(cwd) is not str or not cwd or "\x00" in cwd):
            raise OwnedProcessError("Invalid working directory")
        with self._lock:
            if self._blocked or self._child is not None:
                raise OwnedProcessError("Previous model not confirmed released")
            # No stdin input or inherited stdout containing prompts; never shell.
            try:
                self._child = self._spawn(
                    list(command), cwd=cwd, shell=False, stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except (OSError, ValueError):
                raise OwnedProcessError("Could not start local model") from None
            return self._child.pid

    def is_running(self):
        with self._lock:
            return self._child is not None and self._child.poll() is None

    def stop(self, *, timeout=10):
        """Confirm child exited before permitting another model.

        If termination/join fails, remain blocked: no speculative replacement.
        """
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0 < timeout <= 120:
            raise OwnedProcessError("Invalid stop timeout")
        with self._lock:
            child = self._child
            if child is None:
                if self._blocked:
                    raise OwnedProcessError("Unverified model release")
                return True
            self._blocked = True
            try:
                if child.poll() is None:
                    child.terminate()
                child.wait(timeout=timeout)
            except (OSError, subprocess.TimeoutExpired):
                raise OwnedProcessError("Model termination unverified") from None
            self._child = None
            self._blocked = False
            return True
