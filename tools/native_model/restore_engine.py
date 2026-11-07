"""Restore the already-built native dependency from immutable public Git data.

Build/CI utility only: no application ZIP, compilation, GGUF, native execution
or Actions artifact API. Local archive input supports verified offline reuse.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
from tempfile import NamedTemporaryFile, TemporaryDirectory
import urllib.parse
import urllib.request
import zipfile


DLL_NAME = "koboldcpp_noavx2.dll"
REFERENCE_PATH = Path(__file__).with_name("engine-reference.json")
CHUNK = 1024 * 1024
MAX_BYTES = 64 * CHUNK
FIELDS = frozenset(("schema_version", "repository", "git_commit", "archive_path",
                    "archive_bytes", "archive_sha256", "dll_member", "dll_bytes",
                    "dll_sha256", "upstream_commit", "upstream_python_sha256"))


class NativeReferenceError(ValueError):
    pass


def _relative(value):
    return (isinstance(value, str) and bool(value) and "\\" not in value
            and not any(ord(c) < 32 for c in value)
            and not PurePosixPath(value).is_absolute()
            and ".." not in PurePosixPath(value).parts
            and str(PurePosixPath(value)) == value)


def _validate(reference):
    if not isinstance(reference, dict) or set(reference) != FIELDS:
        raise NativeReferenceError("Manifest dipendenza non riconosciuto.")
    if type(reference["schema_version"]) is not int or reference["schema_version"] != 1:
        raise NativeReferenceError("Schema dipendenza non supportato.")
    repo = reference["repository"]
    if (not isinstance(repo, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo)
            or any(part in (".", "..") for part in repo.split("/"))):
        raise NativeReferenceError("Repository della dipendenza non valido.")
    for key in ("git_commit", "upstream_commit"):
        if not isinstance(reference[key], str) or not re.fullmatch(r"[0-9a-f]{40}", reference[key]):
            raise NativeReferenceError("Serve un commit immutabile per la dipendenza.")
    for key in ("archive_sha256", "dll_sha256", "upstream_python_sha256"):
        if not isinstance(reference[key], str) or not re.fullmatch(r"[0-9a-f]{64}", reference[key]):
            raise NativeReferenceError("SHA256 della dipendenza non valido.")
    for key in ("archive_bytes", "dll_bytes"):
        if type(reference[key]) is not int or not 0 < reference[key] <= MAX_BYTES:
            raise NativeReferenceError("Dimensione della dipendenza non valida.")
    archive, member = reference["archive_path"], reference["dll_member"]
    if not _relative(archive) or not archive.startswith("Download/") or not archive.endswith(".zip"):
        raise NativeReferenceError("Percorso archivio non valido.")
    if not _relative(member) or PurePosixPath(member).name != DLL_NAME:
        raise NativeReferenceError("Membro DLL non valido.")
    return dict(reference)


def load_reference(path=REFERENCE_PATH):
    try:
        return _validate(json.loads(Path(path).read_text(encoding="utf-8")))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise NativeReferenceError("Manifest dipendenza illeggibile.") from exc


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while chunk := stream.read(CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def _download(reference, path):
    url = ("https://raw.githubusercontent.com/" + reference["repository"] + "/"
           + reference["git_commit"] + "/"
           + urllib.parse.quote(reference["archive_path"], safe="/"))
    size = 0
    digest = hashlib.sha256()
    request = urllib.request.Request(url, headers={"User-Agent": "Jarvis-native-dependency"})
    with urllib.request.urlopen(request, timeout=45) as response, path.open("xb") as output:
        while chunk := response.read(CHUNK):
            size += len(chunk)
            if size > reference["archive_bytes"]:
                raise NativeReferenceError("Archivio scaricato oltre la dimensione fissata.")
            digest.update(chunk)
            output.write(chunk)
    if size != reference["archive_bytes"] or digest.hexdigest() != reference["archive_sha256"]:
        raise NativeReferenceError("Download incompleto o SHA256 archivio diverso.")


def _install(archive, destination, reference):
    if (archive.is_symlink() or not archive.is_file()
            or archive.stat().st_size != reference["archive_bytes"]
            or _sha256(archive) != reference["archive_sha256"]):
        raise NativeReferenceError("Dimensione o SHA256 archivio diverso dal riferimento.")
    if destination.is_symlink():
        raise NativeReferenceError("Cartella dipendenza collegata: operazione rifiutata.")
    source = destination / "koboldcpp.py"
    if source.exists() or source.is_symlink():
        if source.is_symlink() or not source.is_file() or source.stat().st_size > 2 * CHUNK:
            raise NativeReferenceError("Sorgente ABI non verificabile.")
        normalized = source.read_bytes().replace(b"\r\n", b"\n")
        if hashlib.sha256(normalized).hexdigest() != reference["upstream_python_sha256"]:
            raise NativeReferenceError("Sorgente ABI diverso dalla revisione della DLL.")
    staging = None
    try:
        with zipfile.ZipFile(archive) as bundle:
            members = [item for item in bundle.infolist() if item.filename == reference["dll_member"]]
            if len(members) != 1:
                raise NativeReferenceError("DLL assente o duplicata nell'archivio.")
            member = members[0]
            if (member.is_dir() or stat.S_ISLNK(member.external_attr >> 16)
                    or member.flag_bits & 1 or member.file_size != reference["dll_bytes"]):
                raise NativeReferenceError("Membro DLL non valido o dimensione diversa.")
            destination.mkdir(parents=True, exist_ok=True)
            digest, size = hashlib.sha256(), 0
            with NamedTemporaryFile(dir=destination, prefix=".native-engine-", suffix=".tmp",
                                    delete=False) as output:
                staging = Path(output.name)
                with bundle.open(member) as stream:
                    while chunk := stream.read(CHUNK):
                        size += len(chunk)
                        if size > reference["dll_bytes"]:
                            raise NativeReferenceError("DLL oltre la dimensione fissata.")
                        digest.update(chunk)
                        output.write(chunk)
                output.flush()
                os.fsync(output.fileno())
            if size != reference["dll_bytes"] or digest.hexdigest() != reference["dll_sha256"]:
                raise NativeReferenceError("DLL estratta diversa dalla dipendenza verificata.")
        target = destination / DLL_NAME
        try:
            # Publish without a replace/overwrite race; staging is on the same volume.
            os.link(staging, target)
        except FileExistsError:
            if (target.is_symlink() or not target.is_file()
                    or target.stat().st_size != reference["dll_bytes"]
                    or _sha256(target) != reference["dll_sha256"]):
                raise NativeReferenceError("DLL esistente diversa: nessuna sovrascrittura.") from None
        return target
    except zipfile.BadZipFile as exc:
        raise NativeReferenceError("Archivio ZIP non valido.") from exc
    finally:
        if staging is not None:
            staging.unlink(missing_ok=True)


def restore_engine(destination, *, archive=None, reference=None):
    reference = load_reference() if reference is None else _validate(reference)
    destination = Path(destination)
    if archive is not None:
        return _install(Path(archive), destination, reference)
    with TemporaryDirectory(prefix="jarvis-native-reference-") as temporary:
        downloaded = Path(temporary) / "reference.zip"
        _download(reference, downloaded)
        return _install(downloaded, destination, reference)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--archive", type=Path, help="Copia locale identica dello ZIP fissato")
    args = parser.parse_args()
    try:
        reference = load_reference()
        dll = restore_engine(args.destination, archive=args.archive, reference=reference)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, "Ripristino dipendenza nativa fallito: " + str(exc) + "\n")
    print(json.dumps({"native_engine": "restored_verified", "file": dll.name,
                      "sha256": reference["dll_sha256"], "bytes": reference["dll_bytes"],
                      "source_commit": reference["git_commit"]}))


if __name__ == "__main__":
    main()
