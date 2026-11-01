"""Jarvis add-on lifecycle: data-only packages, reviewed local execution.

Installing a .jaddon file NEVER executes code, installs dependencies, runs a
shell, opens a network connection, or grants new operating-system privileges.
A manifest can expose only reviewed read-only core actions. Future executable
providers require audited application code and a new allowlisted adapter.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import threading

from capability_registry import CapabilityRejected, ResolvedCapability, resolve_capability
from live_capabilities import AddonBinding, LiveCapabilityRegistry
from settings import default_path


class AddonError(ValueError):
    pass


_ID = re.compile(r"^[a-z][a-z0-9_]{1,30}$")
_SUB = re.compile(r"^[a-z][a-z0-9_]{1,35}$")
_VERSION = re.compile(r"^(0|[1-9][0-9]{0,3})\.(0|[1-9][0-9]{0,3})\.(0|[1-9][0-9]{0,3})$")
_SAFE_TARGETS = frozenset(("system.status", "downloads.list", "history.list"))
_FILE_TARGETS = {"files.list": "elenca", "files.search": "cerca", "files.read": "leggi",
                 "files.open": "apri", "files.locate": "localizza"}
MAX_ADDONS = 20
MAX_ACTIONS = 5
MAX_FILE_BYTES = 12_000


def _safe_text(value: object, maximum: int) -> bool:
    return (isinstance(value, str) and 1 <= len(value.strip()) <= maximum
            and not any(ord(c) < 32 or ord(c) == 127 for c in value))


def _version_tuple(version: str) -> tuple[int, ...]:
    if not isinstance(version,str) or not _VERSION.fullmatch(version):
        raise AddonError("Versione add-on non valida: usa X.Y.Z.")
    return tuple(int(v) for v in version.split("."))


def validate_manifest(value: object) -> dict:
    """Reject unknown keys and unreviewed code paths, before persistent write."""
    required = {"schema_version", "id", "name", "version", "description", "actions"}
    if not isinstance(value,dict) or set(value) != required:
        raise AddonError("Struttura del pacchetto add-on non riconosciuta.")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise AddonError("Versione schema add-on non supportata.")
    addon_id = value["id"]
    if not isinstance(addon_id,str) or not _ID.fullmatch(addon_id):
        raise AddonError("ID add-on non valido.")
    if not _safe_text(value["name"], 75) or not _safe_text(value["description"], 150):
        raise AddonError("Nome o descrizione add-on non valida.")
    _version_tuple(value["version"])
    actions = value["actions"]
    if not isinstance(actions,list) or not 1 <= len(actions) <= MAX_ACTIONS:
        raise AddonError("Il pacchetto deve avere 1-5 azioni autorizzate.")
    seen = set()
    for item in actions:
        if not isinstance(item,dict) or set(item) != {
                "id", "description", "example", "core_action"}:
            raise AddonError("Descrizione azione add-on non valida.")
        name = item["id"]
        if (not isinstance(name,str) or not name.startswith("addon."+addon_id+".")
                or not _SUB.fullmatch(name[len("addon."+addon_id+"."):])
                or name in seen):
            raise AddonError("ID azione duplicato o non appartenente all'add-on.")
        if (not isinstance(item["core_action"],str)
                or item["core_action"] not in (_SAFE_TARGETS | _FILE_TARGETS.keys())):
            raise AddonError("Funzione add-on non approvata: nessun codice viene eseguito.")
        if item["core_action"] in _FILE_TARGETS and (addon_id != "accesso_file" or
                name != "addon.accesso_file."+_FILE_TARGETS[item["core_action"]]):
            raise AddonError("Identità del componente Accesso file non valida.")
        if not _safe_text(item["description"], 125) or not _safe_text(
                item["example"], 85):
            raise AddonError("Testo dell'azione non valido.")
        seen.add(name)
    # Round-trip to ensure it can be persisted without custom objects.
    return json.loads(json.dumps(value,ensure_ascii=False))


def _manifest_digest(manifest: dict) -> str:
    payload=json.dumps(manifest, ensure_ascii=False,
                       sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _decode_record(raw: object, expected_id: str) -> dict:
    if not isinstance(raw, dict) or set(raw) != {
            "manifest", "enabled", "digest"}:
        raise AddonError("Archivio add-on non riconosciuto.")
    if type(raw["enabled"]) is not bool:
        raise AddonError("Stato add-on non valido.")
    manifest=validate_manifest(raw["manifest"])
    if manifest["id"] != expected_id or raw["digest"] != _manifest_digest(manifest):
        raise AddonError("File add-on modificato senza una nuova installazione.")
    return {"manifest":manifest, "enabled":raw["enabled"],
            "digest":raw["digest"]}


def _read_json_file(path: Path, *, input_file=False) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size>MAX_FILE_BYTES:
        raise AddonError("File add-on non valido, troppo grande o collegamento simbolico.")
    try:
        data=json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise AddonError("Il file add-on non contiene JSON valido.") from exc
    return data


class AddonManager:
    """Per-user, atomic, bounded life cycle with synchronized live registry.

    Installed files are descriptive only. The implementation remains limited
    to compiled, validated existing core read-only actions. The GPT never
    receives arbitrary system access, local paths, files or contact lists.
    """

    def __init__(self, registry: LiveCapabilityRegistry,
                 folder: Path | None = None):
        if not isinstance(registry, LiveCapabilityRegistry):
            raise AddonError("Registro delle capacità assente.")
        self.registry=registry
        self.folder=(Path(folder) if folder is not None else
                     default_path().parent/"addons")
        self._lock=threading.RLock()
        self._file_service = None
        self._records: dict[str,dict] = {}
        self._registered: set[str] = set()
        self._invalid: list[str] = []
        self._consent_path=self.folder.with_name(self.folder.name+"-approvals.json")
        self._consents: dict[str,str]={}
        self.folder.mkdir(parents=True,exist_ok=True)
        if self.folder.is_symlink():
            raise AddonError("Cartella add-on non sicura.")
        self.refresh()

    @property
    def file_service(self):
        if self._file_service is None:
            from file_access.service import FileAccessService
            self._file_service = FileAccessService(
                self.folder.parent/"addon-data"/"accesso_file", self.files_enabled, descriptors=self.file_descriptors)
        return self._file_service

    def files_enabled(self, operation=None):
        with self._lock:
            return any(r["enabled"] and any(a["core_action"] in _FILE_TARGETS
                       and (operation is None or a["core_action"] == "files."+operation)
                       for a in r["manifest"]["actions"]) for r in self._records.values())

    def file_descriptors(self):
        with self._lock:
            return tuple(dict(a) for r in self._records.values() if r["enabled"]
                         for a in r["manifest"]["actions"] if a["core_action"] in _FILE_TARGETS)

    def _path(self, addon_id: str) -> Path:
        if not isinstance(addon_id,str) or not _ID.fullmatch(addon_id):
            raise AddonError("ID add-on non valido.")
        return self.folder/(addon_id+".json")

    def _save(self, addon_id: str, record: dict) -> None:
        path=self._path(addon_id)
        if path.is_symlink():
            raise AddonError("Collegamento simbolico add-on rifiutato.")
        encoded=json.dumps(record,ensure_ascii=False,indent=2)+"\n"
        if len(encoded.encode("utf-8"))>MAX_FILE_BYTES:
            raise AddonError("Add-on troppo grande.")
        temporary=path.with_suffix(".tmp")
        if temporary.exists() and temporary.is_symlink():
            raise AddonError("Percorso temporaneo add-on non sicuro.")
        try:
            temporary.write_text(encoded,encoding="utf-8")
            os.replace(temporary,path)
        finally:
            if temporary.is_file():
                temporary.unlink()

    def _read_consents(self) -> dict[str,str]:
        """Separate permission ledger: files copied into addons are NOT enabled."""
        target=self._consent_path
        if not target.exists():
            return {}
        try:
            if target.is_symlink() or target.stat().st_size>12_000:
                return {}
            data=json.loads(target.read_text(encoding="utf-8"))
            if not isinstance(data,dict) or len(data)>MAX_ADDONS:
                return {}
            if any(not isinstance(k,str) or not _ID.fullmatch(k) or
                   not isinstance(v,str) or not re.fullmatch(
                       r"[0-9a-f]{64}",v) for k,v in data.items()):
                return {}
            return data
        except (OSError,ValueError,UnicodeError):
            return {}

    def _write_consent(self, addon_id: str, digest: str | None) -> None:
        if not _ID.fullmatch(addon_id):
            raise AddonError("ID add-on non valido.")
        approvals=self._read_consents()
        if digest is None:
            approvals.pop(addon_id,None)
        else:
            if not re.fullmatch(r"[0-9a-f]{64}",digest):
                raise AddonError("Hash autorizzazione non valido.")
            approvals[addon_id]=digest
        tmp=self._consent_path.with_suffix(".tmp")
        if self._consent_path.is_symlink() or tmp.is_symlink():
            raise AddonError("File autorizzazioni add-on non sicuro.")
        try:
            tmp.write_text(json.dumps(approvals,sort_keys=True)+"\n",
                           encoding="utf-8")
            os.replace(tmp,self._consent_path)
        finally:
            if tmp.is_file():
                tmp.unlink()

    def refresh(self) -> None:
        """Observe installs/changes/removals; do not trust arbitrary new files."""
        with self._lock:
            files=sorted(self.folder.glob("*.json"))
            approvals=self._read_consents()
            fresh={}
            invalid=[]
            if len(files)>MAX_ADDONS:
                # Fail-closed rather than silently ignoring a newly added addon.
                invalid.append("troppi file add-on")
                files=[]
            for file in files:
                try:
                    if not _ID.fullmatch(file.stem):
                        raise AddonError("nome file non valido")
                    raw=_read_json_file(file)
                    record=_decode_record(raw,file.stem)
                    if (record["enabled"] and
                            approvals.get(file.stem)!=record["digest"]):
                        # Do not accept an enabled bit placed in the install
                        # directory without consent from the settings UI.
                        record["enabled"]=False
                        invalid.append(file.name+": autorizzazione mancante")
                    fresh[file.stem]=record
                except (AddonError,OSError) as exc:
                    invalid.append(file.name+" ("+str(exc)[:80]+")")
            bindings={}
            if sum(len(item["manifest"]["actions"]) for item in
                   fresh.values()) > 32:
                invalid.append("troppe azioni add-on: massimo 32")
                fresh={}
            for addon_id,record in fresh.items():
                for action in record["manifest"]["actions"]:
                    action_id=action["id"]
                    bindings[action_id]=AddonBinding(
                        action_id=action_id,
                        description=action["description"],
                        availability=lambda aid=addon_id, x=action_id,
                                            digest=record["digest"]:
                            self._available(aid,x,digest),
                        handler=lambda *args, x=action_id, **kw:
                            self.resolve(x,kw),
                        requires_approval=False,
                        available_for_gpt=True,
                    )
            for old in self._registered - set(bindings):
                self.registry.unregister(old)
            for item in bindings.values():
                self.registry.register(item)
            self._registered=set(bindings)
            self._records=fresh
            self._consents=approvals
            self._invalid=invalid
            if self._file_service is not None and not self.files_enabled():
                self._file_service.reset()

    def _available(self, addon_id: str, action_id: str, digest: str) -> bool:
        # Never perform disk I/O here; refresh() is called by the app per turn.
        with self._lock:
            item=self._records.get(addon_id)
            valid = bool(
                item and item["enabled"] is True and item["digest"]==digest
                and any(a["id"]==action_id for a in item["manifest"]["actions"]))
            if valid and any(a["id"]==action_id and a["core_action"] in _FILE_TARGETS
                             for a in item["manifest"]["actions"]):
                return self.file_service.available()
            return valid

    def list_installed(self) -> tuple[dict, ...]:
        with self._lock:
            return tuple({
                "id":addon_id, "name":r["manifest"]["name"],
                "version":r["manifest"]["version"],
                "description":r["manifest"]["description"],
                "enabled":r["enabled"],
                "action_count":len(r["manifest"]["actions"]),
            } for addon_id,r in sorted(self._records.items()))

    def warnings(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(self._invalid)

    def install(self, file_path: Path) -> dict:
        """Install or upgrade a *data-only* .jaddon JSON file, always OFF."""
        source=Path(file_path)
        if source.suffix.lower()!=".jaddon":
            raise AddonError("Seleziona un pacchetto .jaddon (JSON, senza codice).")
        manifest=validate_manifest(_read_json_file(source,input_file=True))
        addon_id=manifest["id"]
        with self._lock:
            self.refresh()
            before=self._records.get(addon_id)
            if before is None and len(self._records)>=MAX_ADDONS:
                raise AddonError("Limite add-on installati raggiunto.")
            if before:
                old_version=before["manifest"]["version"]
                if _version_tuple(manifest["version"]) <= _version_tuple(old_version):
                    raise AddonError("L'aggiornamento deve avere una versione successiva.")
            current_actions=sum(len(row["manifest"]["actions"]) for
                                ident,row in self._records.items()
                                if ident!=addon_id)
            if current_actions+len(manifest["actions"])>32:
                raise AddonError("Limite di 32 azioni add-on raggiunto.")
            record={"manifest":manifest,"enabled":False,
                    "digest":_manifest_digest(manifest)}
            # Revoke first: upgrades never inherit prior approval.
            self._write_consent(addon_id,None)
            self._save(addon_id,record)
            self.refresh()
            return {"id":addon_id,"version":manifest["version"],
                    "updated":before is not None}

    def set_enabled(self, addon_id: str, enabled: bool) -> None:
        if type(enabled) is not bool:
            raise AddonError("Selettore add-on non valido.")
        with self._lock:
            self.refresh()
            before=self._records.get(addon_id)
            if before is None:
                raise AddonError("Add-on non trovato o non valido.")
            record={**before,"enabled":enabled}
            # Revoke approval BEFORE disabling on disk. For enabling, the
            # state file remains off until the new consent is durable.
            self._write_consent(addon_id,
                                before["digest"] if enabled else None)
            self._save(addon_id,record)
            self.refresh()

    def remove(self, addon_id: str) -> None:
        with self._lock:
            self.refresh()
            if addon_id not in self._records:
                raise AddonError("Add-on non presente.")
            target=self._path(addon_id)
            if target.is_symlink():
                raise AddonError("Collegamento add-on non consentito.")
            self._write_consent(addon_id,None)
            target.unlink()
            self.refresh()

    def active_actions(self) -> tuple[dict, ...]:
        """Only enabled, checked, installed actions are sent to GPT."""
        self.refresh()
        with self._lock:
            actions=[]
            for addon_id,item in sorted(self._records.items()):
                if not item["enabled"]:
                    continue
                for action in item["manifest"]["actions"]:
                    if action["core_action"] in _FILE_TARGETS and not self.file_service.available():
                        continue
                    actions.append({"id":action["id"],
                                    "example":action["example"][:42]})
            return tuple(actions)

    def resolve(self, action_id: str, arguments: object) -> ResolvedCapability:
        """Local execution gate: recheck disk state and map to safe core plan."""
        if not isinstance(arguments,dict):
            raise CapabilityRejected("Parametri add-on non validi.")
        self.refresh()
        with self._lock:
            for record in self._records.values():
                if not record["enabled"]:
                    continue
                for action in record["manifest"]["actions"]:
                    if action["id"]==action_id:
                        if action["core_action"] in _FILE_TARGETS:
                            from file_access.service import validate_arguments
                            operation=action["core_action"].split(".")[1]
                            clean=validate_arguments(operation,arguments)
                            return ResolvedCapability(action_id=action_id,handler="file_access",
                                file_operation=operation,file_arguments=tuple(clean.items()))
                        if arguments:
                            raise CapabilityRejected("L’azione add-on non accetta parametri.")
                        delegated=resolve_capability(
                            action["core_action"],{})
                        if delegated.handler!="local" or delegated.plan is None:
                            raise CapabilityRejected("Azione add-on non eseguibile.")
                        # Preserve the add-on ID so Jarvis can recheck just
                        # before dispatch; the GPT cannot substitute the plan.
                        return ResolvedCapability(
                            action_id=action_id,handler="local",
                            plan=delegated.plan)
        raise CapabilityRejected("Add-on disattivato, rimosso o non autorizzato.")

    def is_active(self, action_id: str) -> bool:
        self.refresh()
        with self._lock:
            for record in self._records.values():
                if not record["enabled"]:
                    continue
                if any(a["id"]==action_id for a in record["manifest"]["actions"]):
                    return True
            return False
