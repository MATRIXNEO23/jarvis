"""Explicit Italian voice/chat requests for safe local project management.

No GPT, shell, system-wide file scans or inferred write permissions.
Unrelated phrases are never treated as commands.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata


@dataclass(frozen=True)
class ProjectVoiceCommand:
    action: str
    name: str = ""
    target: str = ""


_PREFIX = re.compile(r"^(?:(?:ehi|hey|ok)\s+)?jarvis[\s,.:;-]*", re.I)
_CREATE = re.compile(
    r"^(?:(?:per favore|puoi|potresti|vorrei|voglio|mi piacerebbe)\s+)?"
    r"(?:crea(?:mi|re)?|inizia(?:re)?|avvia(?:re)?|facciamo|"
    r"apri(?:mi)?\s+(?:un\s+)?nuovo)\s+"
    r"(?:un\s+)?(?:nuovo\s+)?progetto"
    r"(?:\s+(?:chiamato|denominato|dal nome|che si chiama))?"
    r"(?:\s+(.+))?$", re.I)
_OPEN = re.compile(
    r"^(?:(?:per favore|puoi|potresti)\s+)?"
    r"(?:apri(?:mi)?|riprendi|continua(?:re)?(?:\s+con)?|"
    r"passa(?:re)?\s+(?:al|a|sul)|torna(?:re)?\s+(?:al|a)|"
    r"torniamo\s+(?:al|a)|lavora(?:re)?\s+(?:sul|al))\s+"
    r"(?:il\s+|lo\s+)?(?:progetto\s+)?(.+)$", re.I)
_LIST = re.compile(
    r"^(?:elenca(?:mi)?|mostra(?:mi)?|dimmi|quali\s+sono|"
    r"fammi\s+vedere)\s+(?:(?:tutti|gli|i|miei|nostri|quali|sono)\s+)*"
    r"progetti(?:\s+attivi)?$", re.I)
_GENERAL = re.compile(
    r"^(?:torna|torniamo|passa|ritorna|vai)\s+(?:alla|a|in|al)\s+"
    r"(?:conversazione\s+)?generale$", re.I)
_FOLDER = re.compile(
    r"^(?:apri(?:mi)?|mostra(?:mi)?|fammi\s+vedere)\s+"
    r"(?:la\s+)?cartella\s+(?:del\s+|di\s+)?"
    r"(?:progetto|progetto\s+attivo|progetto\s+corrente)$", re.I)
_RENAME_NAMED = re.compile(
    r"^(?:rinomina(?:mi)?|cambia(?:mi)?\s+il\s+nome\s+(?:del|al))\s+"
    r"(?:il\s+)?progetto\s+(.+?)\s+(?:in|come|a)\s+(.+)$",re.I)
_RENAME_CURRENT = re.compile(
    r"^(?:rinomina(?:mi)?|cambia(?:mi)?\s+il\s+nome\s+(?:del|al)|"
    r"correggi\s+il\s+nome\s+(?:del|al))\s+"
    r"(?:il\s+)?progetto(?:\s+(?:corrente|attivo|questo))?"
    r"(?:\s+(?:in|come|a)\s+(.+))?$",re.I)
_TRASH = re.compile(
    r"^(?:elimina|cancella|rimuovi|metti\s+nel\s+cestino|"
    r"sposta\s+nel\s+cestino)\s+"
    r"(?:(?:il|questo)\s+)?progetto(?:\s+(.*))?$",re.I)
_RESTORE = re.compile(
    r"^(?:ripristina|recupera)\s+(?:(?:il|un)\s+)?"
    r"progetto\s+(.+)$",re.I)
_TRASH_LIST = re.compile(
    r"^(?:cestino\s+(?:dei\s+)?progetti|"
    r"(?:elenca(?:mi)?|mostra(?:mi)?|dimmi|quali\s+sono)\s+"
    r"(?:(?:i|gli|miei)\s+)?progetti\s+"
    r"(?:eliminati|cancellati|nel\s+cestino))$",re.I)
_EXTRA_LIST = re.compile(
    r"^(?:che|quali)\s+progetti\s+(?:ho|hai)(?:\s+salvati)?"
    r"|^(?:ho|ci\s+sono)\s+(?:dei\s+)?progetti\s+salvati"
    r"|^(?:elenca(?:mi)?|mostra(?:mi)?)\s+(?:i\s+)?progetti\s+salvati"
    r"|^lista\s+(?:dei\s+)?progetti$",re.I)
_NAME_PREFIX = re.compile(r"^(?:che\s+si\s+chiama|dal\s+nome|chiamato|nome)\s+",re.I)
_UNSAFE = re.compile(r"\b(?:password|passphrase|api\s*hash|codice\s*otp|token)\b",re.I)


def safe_project_name(name: str) -> str:
    """Return an owner-provided name or reject ambiguity/unsafe strings."""
    if not isinstance(name, str):
        raise ValueError("Indica un nome valido per il progetto.")
    value = " ".join(name.strip(" ,.!?;:").split())
    value = _NAME_PREFIX.sub("",value).strip(" ,.!?;:")
    if (not value or len(value)>65 or
            any(ord(ch)<32 for ch in value) or
            "/" in value or "\\" in value or
            _UNSAFE.search(value) or value.casefold() in (
                "il progetto","un progetto","nuovo progetto","progetto",
                "generale","la cartella","sul progetto")):
        raise ValueError("Nome del progetto ambiguo o non valido.")
    return value


def parse_project_voice(utterance: str) -> ProjectVoiceCommand | None:
    if not isinstance(utterance,str) or len(utterance)>260:
        return None
    text=unicodedata.normalize("NFKC",utterance).strip()
    text=_PREFIX.sub("",text).strip(" ,.!?;:")
    if not text:
        return None
    if _TRASH_LIST.fullmatch(text):
        return ProjectVoiceCommand("list_trash")
    if _LIST.fullmatch(text) or _EXTRA_LIST.fullmatch(text):
        return ProjectVoiceCommand("list")
    match=_RENAME_NAMED.fullmatch(text)
    if match and match.group(1).casefold() not in (
            "corrente","questo","attivo"):
        return ProjectVoiceCommand("rename",safe_project_name(match.group(2)),
                                   safe_project_name(match.group(1)))
    match=_RENAME_CURRENT.fullmatch(text)
    if match:
        proposed=match.group(1)
        return ProjectVoiceCommand("rename",
                                   safe_project_name(proposed) if proposed else "")
    match=_TRASH.fullmatch(text)
    if match:
        target=(match.group(1) or "").strip()
        if target.casefold() in ("corrente","attivo","questo"):
            target=""
        return ProjectVoiceCommand("trash",
                                   safe_project_name(target) if target else "")
    match=_RESTORE.fullmatch(text)
    if match:
        return ProjectVoiceCommand("restore",safe_project_name(match.group(1)))
    if _GENERAL.fullmatch(text):
        return ProjectVoiceCommand("general")
    if _FOLDER.fullmatch(text):
        return ProjectVoiceCommand("folder")
    match=_CREATE.fullmatch(text)
    if match:
        # An unnamed request is handled by a conversational follow-up.
        name=(match.group(1) or "").strip()
        return ProjectVoiceCommand("create",safe_project_name(name) if name else "")
    match=_OPEN.fullmatch(text)
    if match:
        name=match.group(1).strip()
        if name.casefold() in ("generale","conversazione generale"):
            return ProjectVoiceCommand("general")
        return ProjectVoiceCommand("open",safe_project_name(name))
    return None


def find_existing_project(projects, name: str):
    """Never silently pick the wrong similarly named project."""
    normalized=lambda v:" ".join(v.casefold().split())
    matches=[p for p in projects if normalized(p["name"])==normalized(name)]
    if len(matches)>1:
        raise ValueError("Esistono più progetti con questo nome. Usa il gestore progetti.")
    return matches[0] if matches else None


_CONFIRM_DELETE = re.compile(
    r"^(?:confermo(?:\s+(?:l[’']?eliminazione|di\s+eliminare))?|"
    r"s[ìi]\s+(?:elimina|cancella)|elimina\s+definitivamente\s+dal\s+catalogo)$",re.I)
_CANCEL_DELETE = re.compile(
    r"^(?:annulla|no|non\s+eliminare|lascia\s+stare|fermati)$",re.I)


def project_delete_response(utterance: str) -> str | None:
    """Require a deliberate confirmation following one named deletion prompt."""
    if not isinstance(utterance,str) or len(utterance)>100:
        return None
    value=unicodedata.normalize("NFKC",utterance).strip(" ,.!?;:")
    value=_PREFIX.sub("",value).strip(" ,.!?;:")
    if _CONFIRM_DELETE.fullmatch(value):
        return "confirm"
    if _CANCEL_DELETE.fullmatch(value):
        return "cancel"
    return None
