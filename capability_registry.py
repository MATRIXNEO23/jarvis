"""Read-only capability catalog for the Jarvis conversational GPT.

The shipped JSON describes supported actions to GPT and to the user. It is
NOT executable configuration. Every ID is bound to a compiled allowlist of
specific, reviewed Python handlers or planner tools. GPT output may select an
ID, but cannot create commands, scripts, paths or new implementations.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from action_planner import ApprovedPlan, PlanRejected, parse_plan

CATALOG_PATH = Path(__file__).with_name("jarvis_commands.json")
_MAX_CATALOG_BYTES = 32_000
_MAX_DOCUMENT_CONTENT = 4500

# This is the actual security boundary. The JSON file is just documentation
# and discovery; adding arbitrary IDs or changing bindings in it cannot add
# executable powers.
_LOCAL_BINDINGS = {
    "explorer.open": "open_explorer",
    "explorer.downloads": "open_downloads",
    "explorer.drive_c": "open_drive_c",
    "calculator.open": "open_calculator",
    "browser.open": "open_browser",
    "browser.search": "web_search",
    "system.status": "system_status",
    "downloads.list": "list_downloads",
    "downloads.find": "find_download",
    "history.list": "history",
}
_DOCUMENT_BINDINGS = frozenset({
    "notepad.open", "notepad.close", "notepad.write",
})
_TELEGRAM_BINDINGS = frozenset({"telegram.voice.start"})
_ALLOWED_IDS = frozenset(_LOCAL_BINDINGS) | _DOCUMENT_BINDINGS | _TELEGRAM_BINDINGS


class CapabilityRejected(ValueError):
    """The action is unknown, unavailable or its arguments violate policy."""


@dataclass(frozen=True)
class ResolvedCapability:
    action_id: str
    handler: str
    plan: ApprovedPlan | None = None
    content: str = ""
    target: str = ""
    close_after: bool = False
    recipient: str = ""


def load_catalog(path: Path | None = None) -> tuple[dict, ...]:
    """Validate a descriptive JSON file; never evaluate code from its fields."""
    file = Path(path) if path is not None else CATALOG_PATH
    try:
        if not file.is_file() or file.stat().st_size > _MAX_CATALOG_BYTES:
            raise CapabilityRejected("Catalogo delle azioni mancante o troppo grande.")
        raw = file.read_text(encoding="utf-8")
        document = json.loads(raw)
    except (OSError, UnicodeError, ValueError) as exc:
        raise CapabilityRejected("Catalogo delle capacità non valido.") from exc
    if (not isinstance(document, dict)
            or set(document) != {"schema_version", "description", "actions"}
            or type(document["schema_version"]) is not int
            or document["schema_version"] != 1
            or not isinstance(document["description"], str)
            or not isinstance(document["actions"], list)
            or len(document["actions"]) != len(_ALLOWED_IDS)):
        raise CapabilityRejected("Struttura del catalogo non autorizzata.")
    result = []
    seen: set[str] = set()
    for item in document["actions"]:
        if not isinstance(item, dict) or set(item) != {
                "id", "application", "description", "examples", "risk"}:
            raise CapabilityRejected("Campi del catalogo non autorizzati.")
        name = item["id"]
        if not isinstance(name, str) or name not in _ALLOWED_IDS or name in seen:
            raise CapabilityRejected("Azione catalogo sconosciuta o duplicata.")
        for field in ("application", "description", "risk"):
            value = item[field]
            if (not isinstance(value, str) or not value.strip()
                    or len(value) > 350
                    or any(ord(c) < 32 for c in value)):
                raise CapabilityRejected("Descrizione capacità non valida.")
        examples = item["examples"]
        if (not isinstance(examples, list) or not 1 <= len(examples) <= 5
                or any(not isinstance(x, str) or not x.strip()
                       or len(x) > 130 or any(ord(c) < 32 for c in x)
                       for x in examples)):
            raise CapabilityRejected("Esempi di comandi non validi.")
        seen.add(name)
        result.append(item)
    if seen != _ALLOWED_IDS:
        raise CapabilityRejected("Catalogo incompleto o modificato.")
    return tuple(result)


def capability_prompt(*, has_document: bool = False,
                      compact: bool = False,
                      telegram_send_ready: bool = False) -> str:
    """Compact description generated from the catalog, not hardcoded examples."""
    actions = []
    for item in load_catalog():
        aid = item["id"]
        # A missing session never authorizes Notepad close or append.
        if aid == "notepad.close" and not has_document:
            continue
        if aid == "telegram.voice.start" and not telegram_send_ready:
            continue
        if compact:
            actions.append({
                "id": aid,
                "does": item["description"][:68],
                "example": item["examples"][0],
            })
        else:
            actions.append({
                "id": aid,
                "app": item["application"],
                "does": item["description"],
                "example": item["examples"][0],
            })
    rendered = json.dumps(actions, ensure_ascii=False, separators=(",", ":"))
    if len(rendered) > 3500:
        raise CapabilityRejected("Catalogo troppo lungo per GPT.")
    return rendered


def resolve_capability(action_id: object, arguments: object,
                       *, has_document: bool = False,
                       telegram_send_ready: bool = False) -> ResolvedCapability:
    """Resolve only a compiled handler and validated arguments; never execute."""
    if (not isinstance(action_id, str) or action_id not in _ALLOWED_IDS
            or not isinstance(arguments, dict)):
        raise CapabilityRejected("Capacità non riconosciuta o parametri non validi.")
    # Enforce the shipped descriptor to catch an inconsistent installation.
    if action_id not in {item["id"] for item in load_catalog()}:
        raise CapabilityRejected("Capacità non presente nel catalogo ufficiale.")
    if action_id == "telegram.voice.start":
        if not telegram_send_ready:
            raise CapabilityRejected("Invio vocale Telegram non disponibile.")
        if set(arguments) != {"recipient"}:
            raise CapabilityRejected("Indica soltanto il nome del destinatario.")
        name = arguments["recipient"]
        if (not isinstance(name, str) or not 2 <= len(name.strip()) <= 90
                or any(ord(ch) < 32 for ch in name)):
            raise CapabilityRejected("Destinatario Telegram non valido.")
        # Name is not authority: the local UI performs exact/unique match and
        # requires a separate confirmed message before any network send.
        return ResolvedCapability(action_id, "telegram_voice_dialog",
                                  recipient=name.strip())
    if action_id in _LOCAL_BINDINGS:
        tool = _LOCAL_BINDINGS[action_id]
        try:
            payload = json.dumps({
                "intent": "Richiesta verificata di Jarvis",
                "steps": [{"tool_id": tool, "arguments": arguments}],
            }, ensure_ascii=False)
            plan = parse_plan(payload)
        except (PlanRejected, TypeError, ValueError) as exc:
            raise CapabilityRejected("Argomenti non consentiti per questa azione.") from exc
        return ResolvedCapability(action_id=action_id, handler="local",
                                  plan=plan)
    if action_id == "notepad.open":
        if arguments:
            raise CapabilityRejected("Aprire Blocco note non accetta parametri.")
        if has_document:
            raise CapabilityRejected(
                "C'è già un documento di Jarvis aperto. Scegli quel documento.")
        return ResolvedCapability(action_id, "document_open")
    if action_id == "notepad.close":
        if arguments:
            raise CapabilityRejected("Chiudere Blocco note non accetta parametri GPT.")
        if not has_document:
            raise CapabilityRejected(
                "Nessun Blocco note creato da Jarvis è associato alla richiesta.")
        return ResolvedCapability(action_id, "document_close")
    if action_id == "notepad.write":
        if set(arguments) not in (
            {"content", "target"},
            {"content", "target", "close_after"},
        ):
            raise CapabilityRejected("La scrittura accetta solo testo e destinazione.")
        text = arguments["content"]
        target = arguments["target"]
        close_after = arguments.get("close_after", False)
        if (not isinstance(text, str) or not text.strip()
                or len(text) > _MAX_DOCUMENT_CONTENT
                or any(ord(ch) < 32 and ch not in "\n\t" for ch in text)
                or target not in ("new_notepad", "selected_document")
                or type(close_after) is not bool):
            raise CapabilityRejected("Testo o destinazione del documento non validi.")
        if target == "selected_document" and not has_document:
            raise CapabilityRejected(
                "Nessun documento di Jarvis identificato per la scrittura.")
        if target == "new_notepad" and has_document:
            raise CapabilityRejected(
                "Un documento di Jarvis è già aperto: scegli se aggiungerci testo.")
        return ResolvedCapability(action_id, "document_write",
                                  content=text, target=target,
                                  close_after=close_after)
    raise CapabilityRejected("Nessun esecutore autorizzato per l'azione.")
