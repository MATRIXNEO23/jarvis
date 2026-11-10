"""Cartella musica: elenco brani e ricerca per nome del file."""
from __future__ import annotations

import os
from pathlib import Path
import re
import unicodedata

AUDIO_EXTENSIONS = frozenset((".mp3", ".wav", ".wma", ".m4a"))
# Riquadro (WebView2): formati che Chromium/Edge riproduce.
VIDEO_EXTENSIONS = frozenset((".mp4", ".webm", ".m4v", ".mov", ".mkv"))
# Altri video: si aprono con il lettore predefinito di Windows.
EXTERNAL_VIDEO_EXTENSIONS = frozenset((".avi", ".wmv", ".mpg", ".mpeg", ".flv", ".3gp"))
EXTENSIONS = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS | EXTERNAL_VIDEO_EXTENSIONS
MAX_FILES = 20000


def normalized(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


def scan(folder) -> list[Path]:
    """Brani nella cartella e sottocartelle (senza seguire collegamenti)."""
    root = Path(folder or "")
    if not str(folder or "").strip() or not root.is_dir():
        return []
    found: list[Path] = []
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for name in sorted(files):
            if Path(name).suffix.lower() in EXTENSIONS:
                found.append(Path(current) / name)
                if len(found) >= MAX_FILES:
                    return found
    return found


def scan_all(folders) -> list[Path]:
    """Brani di più cartelle (una cartella dentro un'altra non duplica i brani)."""
    found: list[Path] = []
    seen: set[str] = set()
    for folder in folders or []:
        for track in scan(folder):
            key = os.path.normcase(str(track))
            if key not in seen:
                seen.add(key)
                found.append(track)
                if len(found) >= MAX_FILES:
                    return found
    return found


def root_of(track, folders) -> str | None:
    """La cartella (fra quelle scelte) che contiene il brano, la più specifica."""
    best = None
    path = os.path.normcase(os.path.normpath(str(track)))
    for folder in folders or []:
        base = os.path.normcase(os.path.normpath(str(folder)))
        if path.startswith(base.rstrip("\\/") + os.sep) and (best is None or len(folder) > len(best)):
            best = folder
    return best


def folder_tree(tracks, folders):
    """Cartelle radice e mappa cartella -> {"subdirs", "tracks"} dall'elenco brani
    già letto (nessuna nuova lettura del disco)."""
    dirs: dict[str, dict] = {}
    roots: list[str] = []
    for track in tracks:
        track = Path(track)
        # Stessa forma dei percorsi dei brani (su Windows «C:/x» diventa «C:\\x»),
        # altrimenti aprendo la cartella radice non si trova nulla.
        root = str(Path(root_of(track, folders) or track.parent))
        if root not in roots:
            roots.append(root)
        parent = str(track.parent)
        dirs.setdefault(parent, {"subdirs": [], "tracks": []})["tracks"].append(track)
        child = parent
        while os.path.normcase(child) != os.path.normcase(root):
            up = os.path.dirname(child)
            if not up or up == child:
                break
            entry = dirs.setdefault(up, {"subdirs": [], "tracks": []})
            if child in entry["subdirs"]:
                break
            entry["subdirs"].append(child)
            child = up
    for entry in dirs.values():
        entry["subdirs"].sort(key=str.lower)
    return roots, dirs


def tracks_under(dirs, key) -> list[Path]:
    """Brani della cartella e delle sottocartelle, in ordine di navigazione."""
    result, stack = [], [key]
    while stack:
        entry = dirs.get(stack.pop(0), {"subdirs": [], "tracks": []})
        result.extend(entry["tracks"])
        stack[0:0] = entry["subdirs"]
    return result


def best_matches(tracks: list[Path], query: str, limit: int = 20) -> list[Path]:
    """Brani che contengono tutte le parole cercate, i più aderenti prima."""
    words = normalized(query).split()
    if not words:
        return []
    scored = []
    for track in tracks:
        name = normalized(track.stem)
        full = normalized(" ".join(track.parts[-3:]))
        if all(w in full for w in words):
            score = (0 if name == " ".join(words) else 1,
                     0 if all(w in name for w in words) else 1, len(name))
            scored.append((score, str(track).lower(), track))
    scored.sort()
    return [t for *_rest, t in scored[:limit]]


def is_video(path) -> bool:
    return Path(path).suffix.lower() in (VIDEO_EXTENSIONS | EXTERNAL_VIDEO_EXTENSIONS)


def is_panel_video(path) -> bool:
    return Path(path).suffix.lower() in VIDEO_EXTENSIONS
