"""Safe voice destinations and no-overwrite persistence for new Notepad files.

Voice chooses only a known per-user folder and a simple .txt filename.
No arbitrary model-controlled paths, directory creation, overwrite, or shell.
"""
from __future__ import annotations

import os
from pathlib import Path
import re


class DocumentSaveError(OSError):
    pass


_FOLDER_WORDS = {
    "desktop": ("desktop", "scrivania"),
    "documents": ("documenti", "documento"),
    "downloads": ("download", "scaricati"),
}
_DEFAULT_NAMES = {"", ".", "..", "con", "prn", "aux", "nul"}


def _user_folder(kind: str, home: Path | None = None) -> Path:
    if kind not in _FOLDER_WORDS:
        raise DocumentSaveError("Cartella non autorizzata.")
    home = Path(home) if home is not None else Path.home()
    names = {"desktop": "Desktop", "documents": "Documents", "downloads": "Downloads"}
    if os.name == "nt" and home == Path.home():
        try:
            import winreg
            keyname = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            registry_name = {
                "desktop": "Desktop",
                "documents": "Personal",
                "downloads": "{374DE290-123F-4565-9164-39C4925E467B}",
            }[kind]
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, keyname) as key:
                value, _ = winreg.QueryValueEx(key, registry_name)
            if isinstance(value, str) and value.strip():
                return Path(os.path.expandvars(value)).expanduser()
        except (OSError, ValueError):
            pass
    return home / names[kind]


def simple_filename(title: str) -> str:
    if not isinstance(title, str):
        raise DocumentSaveError("Nome del file non valido.")
    name = " ".join(title.strip().split())
    if name.casefold().endswith(".txt"):
        name = name[:-4].strip()
    if (not name or len(name) > 70 or "." in name or name.casefold() in _DEFAULT_NAMES
            or re.fullmatch(r"(?i:com[1-9]|lpt[1-9])", name)
            or any(ch in name for ch in '<>:"/\\|?*')
            or any(ord(c) < 32 for c in name)
            or name.startswith(".") or name.endswith(".")):
        raise DocumentSaveError("Nome del file non valido: usa soltanto un nome semplice.")
    return name + ".txt"


def destination_from_voice(phrase: str, *, home: Path | None = None) -> Path | None:
    """'Salva sul desktop come Venezia' -> user's Desktop/Venezia.txt.

    Return None to ask again when the utterance is ambiguous or incomplete.
    This is deliberately not a general-purpose path parser.
    """
    if not isinstance(phrase, str) or len(phrase) > 220:
        return None
    words = " ".join(phrase.casefold().split())
    mentioned = [kind for kind, aliases in _FOLDER_WORDS.items()
                 if any(re.search(r"\b" + re.escape(alias) + r"\b", words)
                        for alias in aliases)]
    if len(mentioned) != 1:
        return None
    folder = mentioned[0]
    found = re.search(r"\b(?:chiamalo|chiamala|chiamare|come|nome|titolo)\s+(.+)", words)
    if not found:
        return None
    title = found.group(1)
    # The path destination is a fixed alias, never a string from the model.
    suffixes = sum((list(aliases) for aliases in _FOLDER_WORDS.values()), [])
    for alias in suffixes:
        title = re.split(r"\s+(?:sul|sulla|in|nei|nella|nel|su)\s+"
                         + re.escape(alias) + r"\b", title)[0]
    title = title.strip(" ,.;:")
    try:
        filename = simple_filename(title)
    except DocumentSaveError:
        return None
    return _user_folder(folder, home=home) / filename


def save_new_text(path: Path, content: str) -> Path:
    """Create a brand-new file exclusively: existing user data is never changed."""
    path = Path(path)
    if not isinstance(content, str) or not content.strip() or len(content) > 64_000:
        raise DocumentSaveError("Contenuto del documento non valido.")
    if simple_filename(path.name) != path.name:
        raise DocumentSaveError("Il nome del file non è valido.")
    parent = path.parent
    if not parent.is_dir() or parent.is_symlink():
        raise DocumentSaveError("La cartella non esiste o è un collegamento.")
    if path.exists() or path.is_symlink():
        raise DocumentSaveError("Un file con questo nome esiste già. Scegli un altro nome.")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise DocumentSaveError("File già esistente: non sarà sovrascritto.") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    return path
