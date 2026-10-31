"""Local, dependency-free Jarvis settings. Never store secrets here."""
from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULTS = {"gpt_enabled": True, "tts_enabled": False, "tts_voice": "",
            "memory_enabled": False, "auto_listen": True}


def default_path() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if not base:
        base = str(Path.home() / ".local" / "share")
    return Path(base) / "Jarvis" / "settings.json"


def load_settings(path: Path | None = None) -> dict:
    target = path or default_path()
    result = DEFAULTS.copy()
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return result
        if type(data.get("gpt_enabled")) is bool:
            result["gpt_enabled"] = data["gpt_enabled"]
        if type(data.get("tts_enabled")) is bool:
            result["tts_enabled"] = data["tts_enabled"]
        if type(data.get("memory_enabled")) is bool:
            result["memory_enabled"] = data["memory_enabled"]
        if type(data.get("auto_listen")) is bool:
            result["auto_listen"] = data["auto_listen"]
        voice = data.get("tts_voice")
        if isinstance(voice, str) and len(voice) <= 180:
            result["tts_voice"] = voice
    except (OSError, ValueError, UnicodeError):
        pass
    return result


def save_settings(settings: dict, path: Path | None = None) -> None:
    target = path or default_path()
    if type(settings.get("gpt_enabled")) is not bool:
        raise ValueError("gpt_enabled must be a boolean")
    enabled = settings.get("tts_enabled", False)
    voice = settings.get("tts_voice", "")
    memory_enabled = settings.get("memory_enabled", False)
    auto_listen = settings.get("auto_listen", True)
    if (type(enabled) is not bool or type(memory_enabled) is not bool
            or type(auto_listen) is not bool
            or not isinstance(voice, str) or len(voice) > 180):
        raise ValueError("Invalid spoken reply settings")
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps({"gpt_enabled": settings["gpt_enabled"],
                               "tts_enabled": enabled, "tts_voice": voice,
                               "memory_enabled": memory_enabled,
                               "auto_listen": auto_listen},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, target)
