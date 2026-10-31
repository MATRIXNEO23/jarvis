"""Local, dependency-free Jarvis settings. Never store secrets here."""
from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULTS = {"gpt_enabled": True, "tts_enabled": False, "tts_voice": "",
            "memory_enabled": False, "auto_listen": True,
            "telegram_enabled": False, "telegram_peer_id": 0,
            "telegram_contact_name": ""}


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
        if type(data.get("telegram_enabled")) is bool:
            result["telegram_enabled"] = data["telegram_enabled"]
        peer = data.get("telegram_peer_id")
        if type(peer) is int and peer >= 0:
            result["telegram_peer_id"] = peer
        name = data.get("telegram_contact_name")
        if isinstance(name, str) and len(name) <= 90:
            result["telegram_contact_name"] = name
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
    telegram_enabled = settings.get("telegram_enabled", False)
    peer = settings.get("telegram_peer_id", 0)
    peer_name = settings.get("telegram_contact_name", "")
    if (type(enabled) is not bool or type(memory_enabled) is not bool
            or type(auto_listen) is not bool
            or type(telegram_enabled) is not bool
            or type(peer) is not int or peer < 0
            or not isinstance(peer_name,str) or len(peer_name) > 90
            or not isinstance(voice, str) or len(voice) > 180):
        raise ValueError("Invalid spoken reply settings")
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps({"gpt_enabled": settings["gpt_enabled"],
                               "tts_enabled": enabled, "tts_voice": voice,
                               "memory_enabled": memory_enabled,
                               "auto_listen": auto_listen,
                               "telegram_enabled": telegram_enabled,
                               "telegram_peer_id": peer,
                               "telegram_contact_name": peer_name},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, target)
