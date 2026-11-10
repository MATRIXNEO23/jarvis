"""Comandi personalizzati: parole a scelta dell'utente -> comando già esistente.

Esempio: «sparami {testo}» -> «metti {testo}», «buonanotte» -> «ferma la musica».
La frase viene solo riscritta prima dei comandi locali (voce e casella di testo):
non aggiunge nuovi poteri, il comando risultante passa dagli stessi controlli.
Salvati nel profilo: command-aliases.json (mai nel repository, mai cancellati
se non dall'utente).
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from pathlib import Path

MAX_ALIASES = 300
MAX_PHRASE = 80
MAX_COMMAND = 160
_SLOT = re.compile(r"\{([a-zA-Z_]{1,20})\}")
_WAKE = re.compile(r"^\s*((?:ehi\s+|ok\s+)?lumi[\s,!.:]*)", re.IGNORECASE)
_cache = {"path": None, "mtime": None, "items": []}


def default_file() -> Path | None:
    try:
        from settings import default_path
        return default_path().parent / "command-aliases.json"
    except Exception:
        return None


def _normal(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9{}_]+", " ", text.lower()).split())


def clean(items) -> list[dict]:
    result, seen = [], set()
    for item in items or []:
        if not isinstance(item, dict):
            continue
        phrase = " ".join(str(item.get("phrase", "")).split())[:MAX_PHRASE]
        command = " ".join(str(item.get("command", "")).split())[:MAX_COMMAND]
        section = " ".join(str(item.get("section", "")).split())[:40]
        key = _normal(phrase)
        if not key or not command or key in seen:
            continue
        # Ogni {segnaposto} del comando deve esistere nella frase.
        if not set(_SLOT.findall(command)) <= set(_SLOT.findall(phrase)):
            continue
        seen.add(key)
        result.append({"section": section, "phrase": phrase, "command": command})
        if len(result) >= MAX_ALIASES:
            break
    return result


def load(path: Path | None = None) -> list[dict]:
    path = Path(path) if path else default_file()
    if path is None:
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return clean(data.get("aliases") if isinstance(data, dict) else None)


def save(items, path: Path | None = None) -> None:
    path = Path(path) if path else default_file()
    if path is None:
        raise OSError("Profilo non disponibile.")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"aliases": clean(items)}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    os.replace(tmp, path)
    _cache["mtime"] = None


def _pattern(phrase: str):
    parts, last = [], 0
    for match in _SLOT.finditer(phrase):
        parts.append(re.escape(_normal(phrase[last:match.start()])))
        parts.append(f"(?P<{match.group(1)}>.+?)")
        last = match.end()
    parts.append(re.escape(_normal(phrase[last:])))
    body = r"\s*".join(p for p in parts if p)
    return re.compile(r"^" + body + r"$")


def _items(path=None):
    path = Path(path) if path else default_file()
    try:
        mtime = path.stat().st_mtime if path else None
    except OSError:
        mtime = None
    if _cache["path"] != path or _cache["mtime"] != mtime:
        _cache.update(path=path, mtime=mtime, items=load(path) if mtime else [])
    return _cache["items"]


def rewrite(text: str, items=None, path=None) -> str:
    """Testo -> comando personalizzato (con «Lumi,» iniziale conservato), o testo invariato."""
    if not isinstance(text, str) or not text.strip() or len(text) > 300:
        return text
    items = _items(path) if items is None else clean(items)
    if not items:
        return text
    wake = _WAKE.match(text)
    prefix = wake.group(1) if wake else ""
    body = _normal(text[len(prefix):]).replace("{", "").replace("}", "")
    for item in items:
        match = _pattern(item["phrase"]).fullmatch(body)
        if match:
            values = match.groupdict()
            command = _SLOT.sub(lambda m: values.get(m.group(1), ""), item["command"])
            return (prefix + command).strip()
    return text
