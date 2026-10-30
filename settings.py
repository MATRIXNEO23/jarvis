"""Local, dependency-free Jarvis settings. Never store secrets here."""
from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULTS = {"gpt_enabled": True}


def default_path() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if not base:
        base = str(Path.home() / ".local" / "share")
    return Path(base) / "Jarvis" / "settings.json"


def load_settings(path: Path | None = None) -> dict[str, bool]:
    target = path or default_path()
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            enabled = data.get("gpt_enabled")
            if type(enabled) is bool:
                return {"gpt_enabled": enabled}
    except (OSError, ValueError, UnicodeError):
        pass
    return DEFAULTS.copy()


def save_settings(settings: dict[str, bool], path: Path | None = None) -> None:
    target = path or default_path()
    if type(settings.get("gpt_enabled")) is not bool:
        raise ValueError("gpt_enabled must be a boolean")
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps({"gpt_enabled": settings["gpt_enabled"]}, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, target)
