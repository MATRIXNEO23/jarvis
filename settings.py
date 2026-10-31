"""Local, dependency-free Jarvis settings. Never store secrets here."""
from __future__ import annotations

import json
import os
from pathlib import Path

from timer_alarm import ALARM_PATTERNS, DEFAULT_ALARM

DEFAULTS = {"gpt_enabled": True, "tts_enabled": False, "tts_voice": "",
            "memory_enabled": False, "auto_listen": True,
            "telegram_enabled": False, "telegram_peer_id": 0,
            "telegram_contact_name": "", "telegram_contacts": [],
            "timer_sound": DEFAULT_ALARM, "timer_volume": 65,
            "timer_repeat": False}


def normalize_telegram_contacts(value) -> list[dict]:
    """Preserve only explicitly selected verified numeric IDs; no tokens."""
    if not isinstance(value, list):
        return []
    accepted = []
    seen = set()
    for item in value[:250]:
        if not isinstance(item, dict):
            continue
        peer_id, name = item.get("id"), item.get("name")
        if (type(peer_id) is not int or peer_id <= 0 or peer_id in seen
                or not isinstance(name, str) or not name.strip()
                or len(name) > 90 or type(item.get("enabled")) is not bool):
            continue
        seen.add(peer_id)
        accepted.append({"id": peer_id, "name": name.strip(),
                         "enabled": item["enabled"]})
        if len(accepted) >= 80:
            break
    return accepted


def default_path() -> Path:
    # Trial launcher redirects Jarvis's own settings, workspace, preferences,
    # Telegram auth and add-ons without replacing the user's live installation.
    trial_home=os.environ.get("JARVIS_TRIAL_HOME")
    if trial_home:
        return Path(trial_home)/"settings.json"
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
        contacts = data.get("telegram_contacts")
        if isinstance(contacts, list):
            result["telegram_contacts"] = normalize_telegram_contacts(contacts)
        elif result["telegram_peer_id"] and result["telegram_contact_name"]:
            # One-time, lossless compatibility with the original single-contact
            # configuration; a later explicit [] is respected.
            result["telegram_contacts"] = [{
                "id": result["telegram_peer_id"],
                "name": result["telegram_contact_name"], "enabled": True,
            }]
        timer_sound=data.get("timer_sound")
        if isinstance(timer_sound,str) and timer_sound in ALARM_PATTERNS:
            result["timer_sound"]=timer_sound
        timer_volume=data.get("timer_volume")
        if type(timer_volume) is int and 0<=timer_volume<=100:
            result["timer_volume"]=timer_volume
        timer_repeat=data.get("timer_repeat")
        if type(timer_repeat) is bool:
            result["timer_repeat"]=timer_repeat
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
    contacts = settings.get("telegram_contacts", [])
    timer_sound=settings.get("timer_sound",DEFAULT_ALARM)
    timer_volume=settings.get("timer_volume",65)
    timer_repeat=settings.get("timer_repeat",False)
    if (timer_sound not in ALARM_PATTERNS
            or type(timer_volume) is not int or not 0<=timer_volume<=100
            or type(timer_repeat) is not bool):
        raise ValueError("Impostazioni allarme timer non valide")
    if not isinstance(contacts, list) or normalize_telegram_contacts(contacts) != contacts:
        raise ValueError("Invalid Telegram contact selection")
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
                               "telegram_contact_name": peer_name,
                               "telegram_contacts": contacts,
                               "timer_sound": timer_sound,
                               "timer_volume": timer_volume,
                               "timer_repeat": timer_repeat},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, target)
