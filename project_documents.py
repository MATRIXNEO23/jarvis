"""No-overwrite, project-scoped TXT filename suggestions.

Only the trusted project's UUID-based AppData/files directory is writable.
The filename comes from the owner's document request, not model-provided paths.
"""
from __future__ import annotations

from pathlib import Path
import re
import unicodedata

from document_store import simple_filename


_TOPIC = re.compile(
    r"\b(?:sul|sulla|sullo|sui|sulle|sugli|su|riguardo(?:\s+a)?|"
    r"relativo\s+a|per|di)\s+(.+)$",re.I)
_BAD_WORDS = frozenset({
    "il","la","lo","gli","le","i","un","una","uno","del","della","di",
    "nel","nella","progetto","documento","file","testo","nota","note",
    "appunti","blocconote","blocco","note","questo","questa","oggi",
    "nuovo","nuova","salva","scrivi","scrivimi","crea","creami",
})
_RESERVED = frozenset({"con","prn","nul","aux","com1","lpt1"})


def _slug(text: str) -> str:
    text=unicodedata.normalize("NFKD",str(text))
    text="".join(ch for ch in text if not unicodedata.combining(ch))
    text=text.casefold()
    text=re.sub(r"[^a-z0-9]+","-",text).strip("-")
    bits=[x for x in text.split("-") if x and x not in _BAD_WORDS]
    stem="-".join(bits)[:52].rstrip("-")
    return stem if stem and stem not in _RESERVED else "appunti"


def suggested_filename(topic: str, project_name: str, *, explicit_name: str = "") -> str:
    if explicit_name:
        # An explicit owner title may be human-readable, but never a path.
        return simple_filename(explicit_name.strip())
    match=_TOPIC.search(str(topic or ""))
    if match:
        value=_slug(match.group(1))
        if value!="appunti":
            return simple_filename(value)
    value=_slug(topic)
    if value not in ("appunti","salva","salvataggio"):
        return simple_filename(value)
    return simple_filename("appunti-"+_slug(project_name))


def project_save_destination(workspace, project_id: str, topic: str,
                             *, explicit_name: str = "") -> Path:
    """Return a new available .txt path without creating or replacing any file."""
    project=workspace.project(project_id)
    if not project:
        raise ValueError("Nessun progetto valido attivo.")
    directory=workspace.project_files_directory(project_id)
    filename=suggested_filename(topic,project["name"],explicit_name=explicit_name)
    stem=filename[:-4]
    for number in range(1,1001):
        proposed=filename if number==1 else simple_filename(
            stem[:57]+"-"+str(number))
        target=directory/proposed
        if not target.exists() and not target.is_symlink():
            return target
    raise ValueError("Troppi documenti con nomi simili nel progetto.")


_SAVE = re.compile(
    r"^(?:salva(?:mi)?|salva\s+(?:questo|il)\s+(?:testo|file|documento|blocco\s+note))"
    r"(?:\s+(?:nel\s+progetto|nella\s+cartella\s+del\s+progetto))?"
    r"(?:\s+(?:(?:come|con\s+(?:il\s+)?nome)\s+)(.+))?$",re.I)


def parse_simple_save(utterance: str) -> str | None:
    """None means unrelated; empty string means save with inferred name."""
    if not isinstance(utterance,str) or len(utterance)>220:
        return None
    text=unicodedata.normalize("NFKC",utterance).strip(" ,.!?;:")
    text=re.sub(r"^(?:(?:ehi|hey|ok)\s+)?lumi[\s,.:;-]+","",text,flags=re.I)
    match=_SAVE.fullmatch(text)
    return match.group(1).strip(" ,.!?;:") if match and match.group(1) else (
        "" if match else None)
