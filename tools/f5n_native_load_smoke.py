"""F5N.4: Windows-only, isolated native DLL load smoke test.

No GGUF, no server, no model API invocation. This verifies only that Windows
can resolve the pinned four-file candidate and look up selected exports.
A separate child process contains loader crashes or hangs; NEVER use this tool
to load or replace Jarvis's production DLL.
"""
import argparse
import ctypes
import json
import os
from pathlib import Path
import subprocess
import sys
import shutil

from .f5n_bundle_audit import inspect_bundle
from .f5n_pe_abi_audit import REQUIRED_COMMON_EXPORTS


class NativeSmokeError(RuntimeError):
    pass


def expected_paths(root):
    base = Path(root).resolve(strict=True)
    bundle = inspect_bundle(base)
    route = base / "backend_routes" / "koboldcpp_noavx2"
    return {
        "root": base,
        "common": base / "koboldcpp_common.dll",
        "backend": base / "koboldcpp_noavx2.dll",
        "route": route / "koboldcpp_backend.dll",
        "sha256": bundle["files"],
    }


def dependency_diagnostics(paths):
    """Report PE imports and likely missing dynamic dependencies, read-only.

    This is diagnostic evidence only, not proof of Windows loader resolution.
    """
    try:
        import pefile
    except ImportError:
        return {"error": "pefile missing in isolated CI worker"}
    search_dirs = [paths["root"], paths["route"].parent,
                   Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32"]
    compiler = shutil.which("g++.exe")
    if compiler:
        search_dirs.append(Path(compiler).parent)
    result = {"compiler": compiler, "search_dirs": [str(p) for p in search_dirs],
              "imports": {}, "not_found_in_checked_dirs": {}}
    for key in ("route", "common", "backend"):
        pe = pefile.PE(str(paths[key]), fast_load=True)
        try:
            pe.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
            names = sorted({entry.dll.decode("ascii", "replace")
                            for entry in getattr(pe, "DIRECTORY_ENTRY_IMPORT", ())
                            if entry.dll})
        finally:
            pe.close()
        result["imports"][key] = names
        # Windows KnownDLLs/API sets are resolved by the OS and do not
        # need to exist as files; list potential absences without assertions.
        result["not_found_in_checked_dirs"][key] = [
            name for name in names
            if not name.lower().startswith(("api-ms-", "ext-ms-"))
            and not any((directory / name).is_file() for directory in search_dirs)
        ]
    return result


def load_worker(root):
    """Executed only in the expendable Windows subprocess."""
    if os.name != "nt" or not hasattr(os, "add_dll_directory"):
        raise NativeSmokeError("Windows DLL directories required")
    paths = expected_paths(root)
    with os.add_dll_directory(str(paths["root"])), os.add_dll_directory(str(paths["route"].parent)):
        # Identical load sequence to pinned upstream koboldcpp.py:init_library.
        route_handle = ctypes.CDLL(str(paths["route"]))
        try:
            common_handle = ctypes.CDLL(str(paths["common"]))
        except OSError as exc:
            diagnostic = dependency_diagnostics(paths)
            raise NativeSmokeError(
                "Common DLL load failed; PE dependency diagnostic="
                + json.dumps(diagnostic, sort_keys=True)
                + "; original error=" + str(exc)) from exc
        symbols = sorted(REQUIRED_COMMON_EXPORTS)
        for symbol in symbols:
            getattr(common_handle, symbol)
        # Keep both handles alive until the output has been constructed.
        assert route_handle is not None
        return {
            "schema": 1,
            "candidate": "windows-x64-noavx2",
            "looked_up_symbols": symbols,
            "dll_sha256": {k: v["sha256"] for k, v in paths["sha256"].items()},
            "windows_loader_verified": True,
            "ctypes_layout_verified": False,
            "gguf_load_verified": False,
            "model_inference_verified": False,
            "safe_unload_verified": False,
            "pavilion_cpu_verified": False,
        }


def run_isolated(root, *, timeout=60, runner=None):
    if os.name != "nt":
        raise NativeSmokeError("Windows runner required")
    paths = expected_paths(root)
    if runner is None:
        runner = subprocess.run
    command = [sys.executable, "-m", "tools.f5n_native_load_smoke",
               "--worker", str(paths["root"])]
    try:
        proc = runner(command, capture_output=True, text=True,
                      timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise NativeSmokeError("Native child process timed out") from exc
    if proc.returncode != 0:
        raise NativeSmokeError(
            "Windows native loader failed in isolated child "
            f"(exit={proc.returncode}): {proc.stderr[-2500:]}")
    try:
        result = json.loads(proc.stdout)
    except (ValueError, TypeError) as exc:
        raise NativeSmokeError("Native child returned invalid JSON") from exc
    if result.get("looked_up_symbols") != sorted(REQUIRED_COMMON_EXPORTS) or not result.get("windows_loader_verified"):
        raise NativeSmokeError("Native child did not confirm required exports")
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--worker", action="store_true",
                   help="Only for a disposable Windows CI child process")
    p.add_argument("build_dir")
    args = p.parse_args(argv)
    try:
        result = (load_worker(args.build_dir) if args.worker
                  else run_isolated(args.build_dir))
    except (NativeSmokeError, OSError, ValueError, AttributeError) as exc:
        p.error("F5N.4 loader proof failed: " + str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
