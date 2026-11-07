"""Local, dependency-free Jarvis settings. Never store secrets here."""
from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULTS = {"gpt_enabled": True, "tts_enabled": False, "tts_voice": "",
            "memory_enabled": False, "auto_listen": True,
            "keep_awake_fullscreen": False,
            "telegram_enabled": False, "telegram_peer_id": 0,
            "telegram_contact_name": "", "telegram_contacts": [],
            "timer_sound": "digital", "timer_volume": 80,
            "timer_repeat": True, "timer_audio_mode": "auto"}


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


TELEGRAM_PROFILE_LIMIT = 180


def normalize_telegram_profiles(value):
    if not isinstance(value, dict):
        return {}
    return {key: profile.strip() for key, profile in value.items()
            if isinstance(key, str) and len(key) <= 20 and key.isascii()
            and key.isdecimal() and key[0] != "0"
            and isinstance(profile, str) and 0 < len(profile.strip()) <= TELEGRAM_PROFILE_LIMIT}


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


def _read_settings_object(target: Path) -> dict:
    """Shared read validation for loading and safe replacement of a profile."""
    data = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Oggetto JSON impostazioni richiesto.")
    for flag in ("gpt_enabled", "auto_listen"):
        if flag in data and type(data[flag]) is not bool:
            raise ValueError("Preferenza di avvio non valida.")
    return data


def load_settings(path: Path | None = None, *, warnings: list[str] | None = None) -> dict:
    target = path or default_path()
    result = DEFAULTS.copy()
    try:
        data = _read_settings_object(target)
        if type(data.get("gpt_enabled")) is bool:
            result["gpt_enabled"] = data["gpt_enabled"]
        if type(data.get("tts_enabled")) is bool:
            result["tts_enabled"] = data["tts_enabled"]
        if type(data.get("memory_enabled")) is bool:
            result["memory_enabled"] = data["memory_enabled"]
        if type(data.get("auto_listen")) is bool:
            result["auto_listen"] = data["auto_listen"]
        if type(data.get("keep_awake_fullscreen")) is bool:
            result["keep_awake_fullscreen"] = data["keep_awake_fullscreen"]
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
        profiles = normalize_telegram_profiles(data.get("telegram_contact_profiles"))
        if profiles:
            result["telegram_contact_profiles"] = profiles
        sound = data.get("timer_sound")
        if isinstance(sound, str) and sound in (
                "digital", "double", "electronic", "siren", "soft"):
            result["timer_sound"] = sound
        volume = data.get("timer_volume")
        if type(volume) is int and 0 <= volume <= 100:
            result["timer_volume"] = volume
        if type(data.get("timer_repeat")) is bool:
            result["timer_repeat"] = data["timer_repeat"]
        if data.get("timer_audio_mode") in ("auto", "beep"):
            result["timer_audio_mode"] = data["timer_audio_mode"]
        voice = data.get("tts_voice")
        if isinstance(voice, str) and len(voice) <= 180:
            result["tts_voice"] = voice
    except FileNotFoundError:
        # Preserve the agreed first-installation/legacy defaults. A missing
        # file is different from an existing file we could not interpret.
        pass
    except (OSError, ValueError, UnicodeError):
        result.update(gpt_enabled=False, auto_listen=False, tts_enabled=False,
                      memory_enabled=False, telegram_enabled=False,
                      keep_awake_fullscreen=False)
        if warnings is not None:
            warnings.append(
                "Impostazioni non leggibili: avvio prudente con microfono e GPT spenti. "
                "File originale conservato: " + str(target) + ". "
                "Chiudi Jarvis, conserva una copia dell'originale e ripristina "
                "un settings.json valido da backup.")
    return result


def save_settings(settings: dict, path: Path | None = None) -> None:
    target = path or default_path()
    if type(settings.get("gpt_enabled")) is not bool:
        raise ValueError("gpt_enabled must be a boolean")
    enabled = settings.get("tts_enabled", False)
    voice = settings.get("tts_voice", "")
    memory_enabled = settings.get("memory_enabled", False)
    auto_listen = settings.get("auto_listen", True)
    keep_awake_fullscreen = settings.get("keep_awake_fullscreen", False)
    telegram_enabled = settings.get("telegram_enabled", False)
    peer = settings.get("telegram_peer_id", 0)
    peer_name = settings.get("telegram_contact_name", "")
    contacts = settings.get("telegram_contacts", [])
    sound = settings.get("timer_sound", "digital")
    volume = settings.get("timer_volume", 80)
    repeat = settings.get("timer_repeat", True)
    audio_mode = settings.get("timer_audio_mode", "auto")
    if (sound not in ("digital", "double", "electronic", "siren", "soft")
            or type(sound) is not str or type(volume) is not int
            or not 0 <= volume <= 100 or type(repeat) is not bool
            or audio_mode not in ("auto", "beep")):
        raise ValueError("Invalid timer alarm preferences")
    if not isinstance(contacts, list) or normalize_telegram_contacts(contacts) != contacts:
        raise ValueError("Invalid Telegram contact selection")
    if (type(enabled) is not bool or type(memory_enabled) is not bool
            or type(auto_listen) is not bool or type(keep_awake_fullscreen) is not bool
            or type(telegram_enabled) is not bool
            or type(peer) is not int or peer < 0
            or not isinstance(peer_name,str) or len(peer_name) > 90
            or not isinstance(voice, str) or len(voice) > 180):
        raise ValueError("Invalid spoken reply settings")
    # Recheck the target itself, even if the caller copied a fallback dict or
    # corruption happened after load. Never replace unreadable recoverable data.
    try:
        _read_settings_object(target)
    except FileNotFoundError:
        pass
    except (OSError, ValueError, UnicodeError) as exc:
        raise OSError(
            "Impostazioni originali non leggibili: chiudi Jarvis e ripristina "
            "una copia valida; file non sovrascritto.") from exc
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps({"gpt_enabled": settings["gpt_enabled"],
                               "tts_enabled": enabled, "tts_voice": voice,
                               "memory_enabled": memory_enabled,
                               "auto_listen": auto_listen,
                               "keep_awake_fullscreen": keep_awake_fullscreen,
                               "telegram_enabled": telegram_enabled,
                               "telegram_peer_id": peer,
                               "telegram_contact_name": peer_name,
                               "telegram_contacts": contacts,
                               "telegram_contact_profiles": normalize_telegram_profiles(
                                   settings.get("telegram_contact_profiles")),
                               "timer_sound": sound, "timer_volume": volume,
                               "timer_repeat": repeat,
                               "timer_audio_mode": audio_mode},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, target)
