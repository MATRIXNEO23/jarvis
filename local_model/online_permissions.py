"""Explicit, per-capability online permission. Never infer consent from a prompt.

The default is DENY, including for unknown capabilities. Configuration does not
authorize side effects; a separate action confirmation remains necessary.
"""
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import tempfile

_MODES = frozenset(("never", "ask", "allowed"))
_ID = re.compile(r"^[a-z][a-z0-9_.-]{0,79}$")


def validate_capability(capability):
    if not isinstance(capability, str) or not _ID.fullmatch(capability):
        raise ValueError("Identificatore funzione non valido.")
    return capability


@dataclass
class OnlinePermissionPolicy:
    rules: dict = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.rules, dict):
            raise ValueError("Regole GPT non valide.")
        for name, mode in self.rules.items():
            validate_capability(name)
            if mode not in _MODES:
                raise ValueError("Modalita GPT non valida.")

    def mode(self, capability):
        return self.rules.get(validate_capability(capability), "never")

    def set_mode(self, capability, mode):
        validate_capability(capability)
        if mode not in _MODES:
            raise ValueError("Modalita GPT non valida.")
        self.rules[capability] = mode

    def decide(self, capability, *, confirmed=False):
        """Return 'local_only', 'request_consent' or 'online_permitted'.

        confirmed=True means consent for this *individual request* only;
        it never modifies saved rules.
        """
        mode = self.mode(capability)
        if mode == "never":
            return "local_only"
        if mode == "ask" and confirmed is not True:
            return "request_consent"
        return "online_permitted"

    @classmethod
    def load(cls, path):
        path = Path(path)
        if not path.exists():
            return cls()
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(obj, dict) or obj.get("version") != 1:
                raise ValueError("Versione permessi non valida.")
            return cls(obj["rules"])
        except (OSError, UnicodeError, KeyError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("Permessi GPT danneggiati: nessuna autorizzazione concessa.") from exc

    def save(self, path):
        self.__post_init__()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent,
                prefix=path.name + ".", suffix=".tmp", delete=False
            ) as stream:
                temporary = Path(stream.name)
                json.dump({"version": 1, "rules": self.rules}, stream, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()


def default_online_permissions_path():
    base = os.environ.get("JARVIS_TRIAL_HOME")
    if base:
        return Path(base) / "addon-data" / "modello_locale" / "online-permissions.json"
    local = os.environ.get("LOCALAPPDATA")
    if not local:
        raise RuntimeError("LOCALAPPDATA non disponibile.")
    return Path(local) / "Jarvis" / "addon-data" / "modello_locale" / "online-permissions.json"
