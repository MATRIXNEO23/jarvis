"""F5.1: read-only model availability checks, never load or select a model.

The caller supplies an explicitly chosen GGUF path for embedded models or an
already constructed, locally restricted KoboldServerCanary for server models.
No directory scanning, network during import, storage, downloads or fallback.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .model_profiles_f5 import LocalModelProfile, ProfileError


@dataclass(frozen=True)
class ModelAvailability:
    profile_id: str
    backend: str
    available: bool
    status: str
    model_identity: Optional[str] = None


def inspect_embedded(profile: LocalModelProfile, *, gguf_path: str,
                     dll_path: str) -> ModelAvailability:
    """Check paths only. Does not verify ABI, format, model family or loadability."""
    if not isinstance(profile, LocalModelProfile) or profile.backend != "embedded":
        raise ProfileError("Wrong profile backend for file inspection")
    if not isinstance(gguf_path, str) or not isinstance(dll_path, str):
        raise ProfileError("Invalid local file configuration")
    if not gguf_path or not dll_path or "\x00" in gguf_path or "\x00" in dll_path:
        return ModelAvailability(profile.profile_id, "embedded", False,
                                 "missing_configuration")
    # No user-controlled file is opened; directory, symlink-to-directory and
    # paths referring to anything other than regular files are rejected.
    try:
        model = Path(gguf_path)
        dll = Path(dll_path)
        if not model.is_file():
            return ModelAvailability(profile.profile_id, "embedded", False,
                                     "gguf_unavailable")
        if not dll.is_file():
            return ModelAvailability(profile.profile_id, "embedded", False,
                                     "library_unavailable")
    except (OSError, ValueError):
        return ModelAvailability(profile.profile_id, "embedded", False,
                                 "file_check_failed")
    # The configured path is not an authoritative model name or family.
    return ModelAvailability(profile.profile_id, "embedded", True,
                             "files_present_not_loaded")


def inspect_koboldcpp(profile: LocalModelProfile, *, canary,
                      expected_model: str) -> ModelAvailability:
    """Explicitly probe a running local KoboldCpp and require exact model ID.

    The caller owns canary creation (strict loopback validation is in F4.1).
    No prompt is sent. Errors are converted into safe finite status codes.
    """
    if not isinstance(profile, LocalModelProfile) or profile.backend != "koboldcpp":
        raise ProfileError("Wrong profile backend for KoboldCpp probe")
    from .kobold_server_canary import KoboldServerCanary, KoboldCanaryError
    if not isinstance(canary, KoboldServerCanary):
        raise ProfileError("Verified local canary required")
    if (type(expected_model) is not str or not expected_model.strip()
            or len(expected_model) > 256):
        raise ProfileError("Explicit expected model identity required")
    try:
        loaded = canary.probe()
    except (KoboldCanaryError, OSError):
        return ModelAvailability(profile.profile_id, "koboldcpp", False,
                                 "server_unavailable_or_unverified")
    if loaded != expected_model:
        return ModelAvailability(profile.profile_id, "koboldcpp", False,
                                 "model_mismatch")
    return ModelAvailability(profile.profile_id, "koboldcpp", True,
                             "model_verified", model_identity=loaded)
