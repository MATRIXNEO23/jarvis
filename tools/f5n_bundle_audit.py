"""F5N.2: validate the pinned, split-DLL KoboldCpp Windows build bundle.

Read-only; never load a PE file or modify Jarvis. The upstream build at
6d2fedf... uses a common DLL, CPU variant and backend route forwarder.
"""
from pathlib import Path
import hashlib
import json


UPSTREAM_SHA = "6d2fedf8624e5f05926af3191f9efdcb13c4133c"
FILES = (
    "koboldcpp_common.dll",
    "koboldcpp_default.dll",
    "koboldcpp_noavx2.dll",
    "backend_routes/koboldcpp_noavx2/koboldcpp_backend.dll",
)


class BundleError(ValueError):
    pass


def inspect_bundle(root):
    root = Path(root)
    if not root.is_dir():
        raise BundleError("Build directory not found")
    results = {}
    for relative in FILES:
        path = root.joinpath(*relative.split("/"))
        if not path.is_file() or path.is_symlink():
            raise BundleError("Incomplete or redirected DLL bundle")
        if path.stat().st_size < 1024:
            raise BundleError("DLL artifact is empty or unexpectedly small")
        with path.open("rb") as stream:
            # Check PE magic only. Does NOT prove ISA or ABI compatibility.
            if stream.read(2) != b"MZ":
                raise BundleError("Artifact is not a PE executable")
            digest = hashlib.sha256()
            stream.seek(0)
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        results[relative] = {
            "sha256": digest.hexdigest(),
            "size_bytes": path.stat().st_size,
        }
    return {
        "schema": 1,
        "upstream_commit": UPSTREAM_SHA,
        "arch": "windows-x64-cpu-noavx2-candidate",
        "files": results,
        "runtime_abi_verified": False,
        "pavilion_performance_verified": False,
        "safe_model_unload_verified": False,
    }


def main(argv=None):
    import argparse
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("build_dir", help="Pinned KoboldCpp checkout root")
    args = cli.parse_args(argv)
    try:
        print(json.dumps(inspect_bundle(args.build_dir), indent=2))
    except (OSError, BundleError) as exc:
        cli.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
