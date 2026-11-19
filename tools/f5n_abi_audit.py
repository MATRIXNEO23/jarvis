"""F5N.1: offline, read-only ABI source inventory for native KoboldCpp.

Only inspect explicitly supplied files; never import/execute upstream Python,
load DLLs, start a model, make network requests or write files.
Use on a pinned upstream checkout and Jarvis' bundled DLL copy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


_API = ("load_model", "generate", "abort_generate", "token_count",
        "get_chat_template", "unload_model")


class AbiAuditError(ValueError):
    pass


def _read(path, *, maximum=5_000_000):
    candidate = Path(path)
    if not candidate.is_file() or candidate.stat().st_size > maximum:
        raise AbiAuditError("Required source missing or too large")
    try:
        return candidate.read_text(encoding="utf-8")
    except (UnicodeError, OSError):
        raise AbiAuditError("Source could not be decoded") from None


def inventory(expose_cpp, python_source, dll_path):
    """Conservative text-level inventory, not a proof of ABI or unload safety."""
    expose = _read(expose_cpp)
    wrapper = _read(python_source)
    dll = Path(dll_path)
    if not dll.is_file() or dll.stat().st_size == 0:
        raise AbiAuditError("Native DLL unavailable")
    digest = hashlib.sha256()
    with dll.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    entries = {}
    for name in _API:
        # Detect likely C ABI definitions in expose.cpp without treating
        # references/comments as proof of exported machine symbols.
        pattern = (r"(?m)^\s*(?:bool|int|float|double|const\s+char\s*\*|"
                   r"char\s*\*|generation_outputs|token_count_outputs)\s+"
                   + re.escape(name) + r"\s*\(")
        entries[name] = {
            "cpp_definition_candidate": bool(re.search(pattern, expose)),
            "python_ctypes_binding_reference": bool(
                re.search(r"\bhandle\." + re.escape(name) + r"\b", wrapper)),
        }
    return {
        "schema": 1,
        "dll_sha256": digest.hexdigest(),
        "dll_size_bytes": dll.stat().st_size,
        "sources": {"expose_cpp_sha256": hashlib.sha256(expose.encode()).hexdigest(),
                    "python_sha256": hashlib.sha256(wrapper.encode()).hexdigest()},
        "api": entries,
        "physical_model_unload_verified": False,
        "inference_verified": False,
        "warning": "Static inventory only; verify PE exports and runtime separately",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--expose-cpp", required=True)
    ap.add_argument("--kobold-python", required=True)
    ap.add_argument("--dll", required=True)
    args = ap.parse_args(argv)
    try:
        print(json.dumps(inventory(args.expose_cpp, args.kobold_python, args.dll),
                         indent=2, sort_keys=True))
    except (AbiAuditError, OSError, ValueError):
        ap.error("ABI source audit could not complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
