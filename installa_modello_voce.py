"""Explicit, one-time download of the official Italian Vosk model.

Never called during Jarvis startup. Extract only safe files into an isolated
temporary directory; do not overwrite an existing model or user data.
"""
from __future__ import annotations

import shutil
import stat
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from voice_control import MODEL_NAME, model_directory

MODEL_URL = "https://alphacephei.com/vosk/models/" + MODEL_NAME + ".zip"
MAX_ZIP = 100 * 1024 * 1024
MAX_UNPACKED = 350 * 1024 * 1024
MAX_FILES = 10000


def unpack_model(archive: Path, destination_parent: Path) -> Path:
    """Validate the ZIP and install it without unsafe paths or overwrites."""
    destination = destination_parent / MODEL_NAME
    if destination.exists():
        if (destination / "am" / "final.mdl").is_file():
            return destination
        raise ValueError("Una cartella modello incompleta esiste già. Rinominata prima di riprovare.")
    with tempfile.TemporaryDirectory(prefix=".jarvis-voice-", dir=destination_parent) as folder:
        stage = Path(folder)
        with zipfile.ZipFile(archive) as zf:
            entries = zf.infolist()
            if not entries or len(entries) > MAX_FILES:
                raise ValueError("Archivio modello vuoto o eccessivo.")
            total = 0
            for info in entries:
                name = info.filename.replace("\\", "/")
                rel = Path(name)
                if (rel.is_absolute() or ".." in rel.parts or
                    not rel.parts or rel.parts[0] != MODEL_NAME or
                    ":" in name or
                    stat.S_ISLNK(info.external_attr >> 16)):
                    raise ValueError("Percorso non valido nell'archivio del modello.")
                total += info.file_size
                if total > MAX_UNPACKED:
                    raise ValueError("Archivio modello troppo grande.")
            for info in entries:
                target = stage.joinpath(*Path(info.filename.replace("\\", "/")).parts)
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(info) as src, target.open("wb") as dst:
                        shutil.copyfileobj(src, dst)
        staged_model = stage / MODEL_NAME
        if not (staged_model / "am" / "final.mdl").is_file():
            raise ValueError("Modello italiano non valido: file am/final.mdl mancante.")
        staged_model.rename(destination)
    return destination


def install() -> Path:
    destination = model_directory()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if (destination / "am" / "final.mdl").is_file():
        print("Modello vocale già installato.")
        return destination
    if destination.exists():
        raise ValueError("La cartella modello esiste già ma è incompleta: rinominala e riprova.")
    with tempfile.TemporaryDirectory(prefix=".jarvis-voice-download-", dir=destination.parent) as folder:
        archive = Path(folder) / (MODEL_NAME + ".zip")
        print("Download del modello italiano ufficiale (circa 48 MB)...")
        with urllib.request.urlopen(MODEL_URL, timeout=30) as response:
            with archive.open("wb") as output:
                total = 0
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    total += len(block)
                    if total > MAX_ZIP:
                        raise ValueError("Download troppo grande, operazione annullata.")
                    output.write(block)
        return unpack_model(archive, destination.parent)


if __name__ == "__main__":
    try:
        print("Modello disponibile in:", install())
        print("Riavvia Jarvis: il microfono resterà spento fino all'attivazione manuale.")
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print("Installazione modello non riuscita:", exc)
        raise SystemExit(1)
