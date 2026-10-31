"""Live, bounded capability observations for the external ChatGPT bridge.

A catalog entry is never execution authority. Built-in actions must already
exist in capability_registry's compiled binding/dispatcher; a future add-on
must register a real, reviewed local handler with its owner and availability
probe. This module never imports untrusted add-on code or sends credentials.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import threading
from typing import Callable

from capability_registry import load_catalog


_ADDON_ID = re.compile(r"^addon\.[a-z][a-z0-9_]{1,30}\.[a-z][a-z0-9_]{1,35}$")
_MAX_ADAPTERS = 32


@dataclass(frozen=True)
class AddonBinding:
    """A local add-on manager may register ONLY after loading a vetted handler."""
    action_id: str
    description: str
    availability: Callable[[], bool]
    handler: Callable[..., object]
    requires_approval: bool = True
    available_for_gpt: bool = False


class LiveCapabilityRegistry:
    """Small memory-only bindings, refreshed at each GPT request.

    Add-on installation/uninstallation triggers register/unregister in its
    trusted local lifecycle manager; dynamic user switch changes are probed
    afresh for every snapshot. No arbitrary manifest grants execution rights.
    """
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._addon: dict[str, AddonBinding] = {}

    def register(self, binding: AddonBinding) -> None:
        if (not isinstance(binding, AddonBinding)
                or not _ADDON_ID.fullmatch(binding.action_id)
                or not isinstance(binding.description, str)
                or not 1 <= len(binding.description.strip()) <= 130
                or any(ord(c) < 32 for c in binding.description)
                or not callable(binding.availability)
                or not callable(binding.handler)
                or type(binding.requires_approval) is not bool
                or type(binding.available_for_gpt) is not bool):
            raise ValueError("Registrazione add-on non valida o senza handler.")
        with self._lock:
            if binding.action_id not in self._addon and len(self._addon) >= _MAX_ADAPTERS:
                raise ValueError("Limite delle capacità add-on raggiunto.")
            self._addon[binding.action_id] = binding

    def unregister(self, action_id: str) -> None:
        with self._lock:
            self._addon.pop(action_id, None)

    def available_addons(self) -> tuple[dict, ...]:
        with self._lock:
            bindings = tuple(self._addon.values())
        reports = []
        for binding in sorted(bindings, key=lambda item: item.action_id):
            try:
                verified = binding.availability() is True
            except Exception:
                verified = False
            reports.append({
                "id": binding.action_id,
                "does": binding.description,
                "approval": binding.requires_approval,
                # An add-on is visible but cannot issue GPT tool commands
                # without a separately reviewed local dispatcher binding.
                "status": "installed" if verified else "disabled",
                "mode": ("gateway_locale_verificato" if
                         binding.available_for_gpt else
                         "informativo_non_azione_GPT"),
            })
        return tuple(reports)

    def local_binding(self, action_id: str) -> AddonBinding | None:
        """Only the privileged local addon gateway can call this method."""
        with self._lock:
            return self._addon.get(action_id)


def _is_telethon_installed() -> bool:
    try:
        return importlib.util.find_spec("telethon") is not None
    except (ImportError, ValueError):
        return False


def snapshot_capabilities(
        *, settings: dict, has_document: bool,
        telegram_credentials: bool,
        telegram_voice_dependencies: bool,
        voice_stream_open: bool = False,
        registry: LiveCapabilityRegistry | None = None,
        telethon_installed: bool | None = None) -> dict:
    """One current, redacted observation; no network or disk data enumeration.

    GPT receives only counts, booleans and reviewed action IDs. A bound local
    handler is still required for execution. Unknown status fails closed.
    """
    if telethon_installed is None:
        telethon_installed = _is_telethon_installed()
    contacts = settings.get("telegram_contacts", [])
    chosen = [c for c in contacts
              if isinstance(c, dict) and c.get("enabled") is True
              and type(c.get("id")) is int and c["id"] > 0]
    telegram_ready = bool(
        telegram_credentials and telegram_voice_dependencies
        and telethon_installed and chosen)
    auto_reply = telegram_ready and settings.get("telegram_enabled") is True
    descriptors = load_catalog()
    listed = tuple(entry["id"] for entry in descriptors)
    enabled_core = tuple(id for id in listed
                         if has_document or id != "notepad.close")
    # Deliberately do not expose names, IDs, messages or secret settings.
    result = {
        "core_actions": enabled_core,
        "catalog_version": hashlib.sha256(json.dumps(
            descriptors, ensure_ascii=False, sort_keys=True).encode(
            "utf-8")).hexdigest()[:12],
        "document_open": bool(has_document),
        "telegram_voice_send": telegram_ready,
        "telegram_auto_reply": auto_reply,
        "telegram_selected_count": min(len(chosen), 80),
        "telegram_reason": ("pronto" if telegram_ready else
                            "configurazione/contatti/dipendenze mancanti"),
        "mic_stream_open": voice_stream_open is True,
        "whatsapp": "non implementato",
        "addons": registry.available_addons() if registry is not None else (),
    }
    hashed = json.dumps(result, ensure_ascii=False,
                        separators=(",", ":"), sort_keys=True)
    result["revision"] = hashlib.sha256(
        hashed.encode("utf-8")).hexdigest()[:12]
    return result


def capability_status_prompt(snapshot: dict, max_chars: int = 850) -> str:
    """Return only current, bounded evidence; no ability may be invented."""
    safe = {
        "rev": snapshot.get("revision", "sconosciuta"),
        "telegram_vocale": ("disponibile_via_dialogo_locale" if snapshot.get(
            "telegram_voice_send") is True else "non_disponibile"),
        "telegram_risposte_automatiche": (
            "attive" if snapshot.get("telegram_auto_reply") is True else "spente"),
        "contatti_autorizzati": snapshot.get("telegram_selected_count", 0),
        "microfono": ("stream_aperto" if snapshot.get("mic_stream_open") is True
                      else "non_osservato_aperto"),
        "whatsapp": "non_implementato",
        "addon": [
            {"id":a["id"],"stato":a["status"],
             "funzione":a["does"][:52],
             "esecuzione_GPT":("tramite_gateway_locale" if
                 a.get("mode")=="gateway_locale_verificato" and
                 a.get("status")=="installed" else "non_abilitata")}
            for a in snapshot.get("addons", ())[:5]
        ],
    }
    output=json.dumps(safe,ensure_ascii=False,separators=(",", ":"))
    if len(output)>max_chars:
        safe["addon"]=[]
        output=json.dumps(safe,ensure_ascii=False,separators=(",", ":"))
    if len(output)>max_chars:
        raise ValueError("Stato capacità eccede il limite del bridge.")
    return output
