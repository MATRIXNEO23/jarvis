"""Small fail-closed state machine for a visible, bounded JARVIS source audit.

Controls UI state only; never starts/executes files or calls a model.
Timed-out worker threads cannot be forcibly killed. Their later queue events
must be ignored by run ID and the caller caps concurrently live workers.
"""
from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from collections.abc import Callable


@dataclass(frozen=True)
class DiagnosticSnapshot:
    run_id: int
    active: bool
    phase: str
    completed: int
    total: int
    elapsed_seconds: int
    progress_percent: int


class DiagnosticSession:
    def __init__(self, *, clock: Callable[[],float] = monotonic,
                 stall_seconds: float = 12.0,
                 timeout_seconds: float = 120.0):
        if not 0 < stall_seconds < timeout_seconds:
            raise ValueError("Intervalli diagnostici non validi.")
        self._clock=clock
        self.stall_seconds=stall_seconds
        self.timeout_seconds=timeout_seconds
        self._next_id=0
        self._id=0
        self._started=0.0
        self._last_progress=0.0
        self._stall_reported=False
        self._phase="pronta"
        self._completed=0
        self._total=0

    @property
    def active(self) -> bool:
        return self._id!=0

    @property
    def current_id(self) -> int:
        return self._id

    def start(self) -> int | None:
        if self.active:
            return None
        self._next_id+=1
        self._id=self._next_id
        self._started=self._clock()
        self._last_progress=self._started
        self._stall_reported=False
        self._phase="avvio"
        self._completed=0
        self._total=0
        return self._id

    def progress(self, run_id: int, phase: str,
                 completed: int=0,total: int=0) -> bool:
        if not self.active or run_id!=self._id:
            return False
        if not isinstance(phase,str) or phase not in (
                "inventario","sintassi","consigli","completamento"):
            return False
        total=max(0,min(int(total),1000))
        completed=max(0,min(int(completed),total)) if total else 0
        self._phase=phase
        self._completed=completed
        self._total=total
        self._last_progress=self._clock()
        self._stall_reported=False
        return True

    def finish(self,run_id: int, *, succeeded: bool) -> bool:
        if not self.active or run_id!=self._id:
            return False
        self._id=0
        self._phase="completata" if succeeded else "errore"
        self._completed=self._total
        return True

    def cancel(self) -> int | None:
        """Release UI ownership; cannot stop an OS/Python worker thread."""
        if not self.active:
            return None
        prior=self._id
        self._id=0
        self._phase="annullata"
        return prior

    def check(self) -> str:
        """Poll on Tk main thread; returns '', 'stalled' or 'timeout' once."""
        if not self.active:
            return ""
        now=self._clock()
        if now-self._started>=self.timeout_seconds:
            self._id=0
            self._phase="tempo esaurito"
            return "timeout"
        if (not self._stall_reported
                and now-self._last_progress>=self.stall_seconds):
            self._stall_reported=True
            return "stalled"
        return ""

    def snapshot(self) -> DiagnosticSnapshot:
        elapsed=(max(0,int(self._clock()-self._started))
                 if self.active else 0)
        progress=(min(99,round(100*self._completed/self._total))
                  if self.active and self._total else 0)
        if not self.active and self._phase=="completata":
            progress=100
        return DiagnosticSnapshot(self._id,self.active,self._phase,
                                  self._completed,self._total,
                                  elapsed,progress)
