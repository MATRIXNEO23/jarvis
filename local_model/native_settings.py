"""Safe editable settings for the opt-in native model.

Editing is separate from loading a native DLL; callers apply changes only
after the current generation has stopped and the model is reloaded.
"""
from dataclasses import asdict, replace
from pathlib import Path

from .native_config import NativeModelConfig


EDITABLE_FIELDS = (
    "model", "threads", "batch_threads", "context_size", "max_output",
    "temperature", "top_k", "top_p", "seed", "personality",
)
RELOAD_FIELDS = frozenset(("model", "threads", "batch_threads", "context_size"))


def update_native_settings(current, changes):
    if not isinstance(current, NativeModelConfig):
        raise TypeError("Configurazione nativa richiesta.")
    if not isinstance(changes, dict):
        raise TypeError("Modifiche impostazioni non valide.")
    unknown = set(changes) - set(EDITABLE_FIELDS)
    if unknown:
        raise ValueError("Parametro non configurabile: " + ", ".join(sorted(unknown)))
    revised = replace(current, **changes).validate()
    needs_reload = any(
        getattr(current, field) != getattr(revised, field)
        for field in RELOAD_FIELDS
    )
    return revised, needs_reload


def native_settings_view(config):
    """Displayable values; DLL path remains internal, never an executable."""
    if not isinstance(config, NativeModelConfig):
        raise TypeError("Configurazione nativa richiesta.")
    config.validate()
    return {key: getattr(config, key) for key in EDITABLE_FIELDS}


def default_native_settings_path():
    import os
    trial = os.environ.get("JARVIS_TRIAL_HOME")
    if trial:
        return Path(trial) / "addon-data" / "modello_locale" / "native.json"
    local = os.environ.get("LOCALAPPDATA")
    if not local:
        raise RuntimeError("LOCALAPPDATA non disponibile per configurazione Windows.")
    return Path(local) / "Jarvis" / "addon-data" / "modello_locale" / "native.json"
