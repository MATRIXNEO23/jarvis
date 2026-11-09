"""Fetch the official Piper Windows build and keep only what Lumi needs (CI only).

Source: https://github.com/rhasspy/piper/releases/tag/2023.11.14-2 (MIT),
asset piper_windows_amd64.zip, SHA-256 pinned below. Slim copy for Lumi:
- piper.exe + its DLLs (onnxruntime, espeak-ng, piper_phonemize);
- espeak-ng-data with only the Italian dictionary (it_dict) + shared tables;
- no libtashkeel (Arabic only, 10 MB);
- Visual C++ runtime DLLs copied from the Windows runner (app-local), so the
  Pavilion does not need the VC++ redistributable.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import urllib.request
import zipfile

URL = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
SHA256 = "f3c58906402b24f3a96d92145f58acba6d86c9b5db896d207f78dc80811efcea"
BINARIES = ("piper.exe", "onnxruntime.dll", "onnxruntime_providers_shared.dll",
            "espeak-ng.dll", "piper_phonemize.dll")
DATA_FILES = ("phondata", "phonindex", "phontab", "intonations", "it_dict")
DATA_DIRS = ("lang", "voices")
VC_RUNTIME = ("msvcp140.dll", "vcruntime140.dll", "vcruntime140_1.dll")
NOTICE = """Motore voce Piper (versione snella per Lumi)
Piper 2023.11.14-2, MIT - https://github.com/rhasspy/piper
eSpeak NG (fonemi), GPL-3.0 - https://github.com/espeak-ng/espeak-ng
ONNX Runtime 1.14.1, MIT - https://github.com/microsoft/onnxruntime
Runtime Visual C++ (msvcp140/vcruntime140), ridistribuibile Microsoft.
Incluso solo l'italiano. Voci Paola/Serena scaricate a parte dal repository.
"""


def keep(name: str) -> bool:
    parts = PurePosixPath(name).parts
    if len(parts) < 2 or parts[0] != "piper" or name.endswith("/"):
        return False
    rel = parts[1:]
    if len(rel) == 1:
        return rel[0] in BINARIES
    if rel[0] != "espeak-ng-data":
        return False
    if len(rel) == 2:
        return rel[1] in DATA_FILES
    return rel[1] in DATA_DIRS


def extract(data: bytes, dest: Path) -> dict:
    digest = hashlib.sha256(data).hexdigest()
    if digest != SHA256:
        raise ValueError(f"Piper ZIP SHA-256 mismatch: {digest}")
    dest = Path(dest)
    if dest.exists():
        shutil.rmtree(dest)
    files = {}
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for info in archive.infolist():
            if not keep(info.filename):
                continue
            rel = PurePosixPath(*PurePosixPath(info.filename).parts[1:])
            if ".." in rel.parts:
                raise ValueError("Percorso non valido nello ZIP Piper.")
            target = dest.joinpath(*rel.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            payload = archive.read(info)
            target.write_bytes(payload)
            files[rel.as_posix()] = len(payload)
    missing = [b for b in BINARIES if b not in files] + [
        "espeak-ng-data/" + f for f in DATA_FILES if "espeak-ng-data/" + f not in files]
    if missing:
        raise ValueError("File Piper mancanti: " + ", ".join(missing))
    (dest / "LEGGIMI-MOTORE-VOCE.txt").write_text(NOTICE, encoding="utf-8")
    return files


def copy_vc_runtime(dest: Path) -> list[str]:
    system = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32"
    copied = []
    for name in VC_RUNTIME:
        source = system / name
        if not source.is_file():
            raise ValueError("Runtime Visual C++ non trovato sul runner: " + name)
        shutil.copy2(source, Path(dest) / name)
        copied.append(name)
    return copied


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dest")
    a = parser.parse_args(argv)
    with urllib.request.urlopen(URL, timeout=120) as response:
        data = response.read()
    files = extract(data, Path(a.dest))
    runtime = copy_vc_runtime(Path(a.dest)) if os.name == "nt" else []
    total = sum(p.stat().st_size for p in Path(a.dest).rglob("*") if p.is_file())
    print(json.dumps({"files": len(files) + len(runtime) + 1, "bytes": total,
                      "vc_runtime": runtime, "sha256": SHA256}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
