"""F5.0: pure, opt-in local model profile validation.

This module is deliberately not imported by Lumi runtime. No filesystem,
network, process launching, persistence or model loading is performed here.
"""
from dataclasses import dataclass
from typing import Mapping, Any
import re
import math

_ALLOWED_FAMILIES = frozenset(("gemma", "qwen"))
_ALLOWED_BACKENDS = frozenset(("embedded", "koboldcpp"))
_PROFILE_ID = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{0,63}$")


class ProfileError(ValueError):
    """Safe validation failure with no prompts or private values."""


@dataclass(frozen=True)
class LocalModelProfile:
    profile_id: str
    family: str
    model_label: str
    backend: str
    context_size: int = 1024
    max_output: int = 256
    threads: int = 2
    blas_threads: int = 2
    temperature: float = 0.7
    top_p: float = 0.9
    seed: int = -1

    def __post_init__(self) -> None:
        if not isinstance(self.profile_id, str) or not _PROFILE_ID.fullmatch(self.profile_id):
            raise ProfileError("Invalid profile identifier")
        if self.family not in _ALLOWED_FAMILIES:
            raise ProfileError("Unsupported local model family")
        if self.backend not in _ALLOWED_BACKENDS:
            raise ProfileError("Unsupported local backend")
        if not isinstance(self.model_label, str) or not (1 <= len(self.model_label.strip()) <= 128):
            raise ProfileError("Invalid model label")
        for key, lo, hi in (
            ("context_size", 256, 32768),
            ("max_output", 1, 4096),
            ("threads", 1, 64),
            ("blas_threads", 1, 64),
        ):
            value = getattr(self, key)
            if type(value) is not int or not lo <= value <= hi:
                raise ProfileError("Invalid " + key)
        if self.max_output > self.context_size:
            raise ProfileError("Output limit exceeds context")
        for key in ("temperature", "top_p"):
            value = getattr(self, key)
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ProfileError("Invalid sampler parameter")
            if key == "temperature" and not 0 <= value <= 2:
                raise ProfileError("Invalid temperature")
            if key == "top_p" and not 0 < value <= 1:
                raise ProfileError("Invalid top_p")
        if type(self.seed) is not int or not -1 <= self.seed <= 2147483647:
            raise ProfileError("Invalid seed")


def parse_profile(data: Mapping[str, Any]) -> LocalModelProfile:
    """Reject unknown fields to prevent passing secrets or unsafe backend args."""
    if not isinstance(data, Mapping):
        raise ProfileError("Invalid profile")
    allowed = set(LocalModelProfile.__dataclass_fields__)
    if set(data) - allowed:
        raise ProfileError("Unexpected profile field")
    try:
        return LocalModelProfile(**dict(data))
    except (TypeError, KeyError) as exc:
        raise ProfileError("Invalid profile fields") from None


def default_profiles() -> tuple[LocalModelProfile, ...]:
    """Illustrative presets only; neither proves a GGUF exists nor loads it."""
    return (
        LocalModelProfile("gemma-default", "gemma", "Gemma (configure GGUF)", "embedded"),
        LocalModelProfile("qwen-local", "qwen", "Qwen (configure GGUF)", "koboldcpp"),
    )
