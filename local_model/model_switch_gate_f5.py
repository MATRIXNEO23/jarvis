"""F5.3a: safe model-switch gate; no runtime integration or model loading.

A local engine's cooperative abort is NOT evidence that its GGUF allocation was
released. Require explicit lifecycle confirmation from the owner before any
new engine may be started. This class never invokes or stops an engine itself.
"""
from dataclasses import dataclass
from threading import RLock

from .model_profiles_f5 import LocalModelProfile, ProfileError


class SwitchRejected(RuntimeError):
    """A model transition is unsafe or unsupported; no state was changed."""


@dataclass(frozen=True)
class SwitchSnapshot:
    active_profile_id: str
    generation: int
    blocked: bool


class ModelSwitchGate:
    """Pure, bounded orchestration state; does not own sessions or history.

    The host must implement actual cancellation, join and deterministic model
    release *before* calling confirm_released. Missing guarantees fail closed.
    """

    def __init__(self, active: LocalModelProfile):
        if not isinstance(active, LocalModelProfile):
            raise ProfileError("Valid initial profile required")
        self._lock = RLock()
        self._active = active
        self._generation = 0
        self._pending = None
        self._blocked = False
        self._target_ready = False

    def snapshot(self) -> SwitchSnapshot:
        with self._lock:
            return SwitchSnapshot(self._active.profile_id,
                                  self._generation, self._blocked)

    def begin(self, candidate: LocalModelProfile, *, busy: bool,
              backend_ready: bool, chat_template_verified: bool) -> int:
        if not isinstance(candidate, LocalModelProfile):
            raise ProfileError("Valid target profile required")
        if type(busy) is not bool or type(backend_ready) is not bool or type(chat_template_verified) is not bool:
            raise ProfileError("Explicit switch checks required")
        with self._lock:
            if self._pending is not None or self._blocked:
                raise SwitchRejected("Previous switch not safely completed")
            if candidate.profile_id == self._active.profile_id:
                raise SwitchRejected("Selected profile is already active")
            if busy:
                raise SwitchRejected("Wait for current model operations")
            if not backend_ready:
                raise SwitchRejected("Target backend not verified")
            if not chat_template_verified:
                raise SwitchRejected("Target chat template not verified")
            self._generation += 1
            self._pending = (self._generation, candidate)
            # The owner must release the previous model before any commit.
            self._blocked = True
            self._target_ready = False
            return self._generation

    def confirm_released(self, ticket: int, *, released: bool) -> None:
        """Owner attests physical release; 'stop requested' must never count."""
        if type(released) is not bool:
            raise ProfileError("Explicit model release confirmation required")
        with self._lock:
            if (self._pending is None or type(ticket) is not int
                    or self._pending[0] != ticket):
                raise SwitchRejected("Stale switch ticket")
            if not released:
                raise SwitchRejected("Model release unverified; switching blocked")
            self._blocked = False

    def confirm_target_ready(self, ticket: int, *, ready: bool) -> None:
        """The host must attest successful startup after prior release."""
        if type(ready) is not bool:
            raise ProfileError("Explicit target readiness required")
        with self._lock:
            if (self._pending is None or self._blocked or type(ticket) is not int
                    or self._pending[0] != ticket):
                raise SwitchRejected("Target cannot start before prior release")
            if not ready:
                raise SwitchRejected("Target startup unverified")
            self._target_ready = True

    def commit(self, ticket: int) -> SwitchSnapshot:
        with self._lock:
            if (self._pending is None or self._blocked or not self._target_ready or type(ticket) is not int
                    or self._pending[0] != ticket):
                raise SwitchRejected("Cannot switch before verified release and startup")
            self._active = self._pending[1]
            self._pending = None
            self._target_ready = False
            return self.snapshot()

    def cancel_before_release(self, ticket: int) -> SwitchSnapshot:
        """Cancel only before attempting resource release; retain old owner."""
        with self._lock:
            if (self._pending is None or type(ticket) is not int
                    or self._pending[0] != ticket or not self._blocked):
                raise SwitchRejected("Cannot restore a released model implicitly")
            self._pending = None
            self._blocked = False
            self._target_ready = False
            return self.snapshot()
