"""F5N.3: inspect Windows PE exports/imports without loading or executing DLLs.

This test is a preflight for the pinned KoboldCpp 6d2fedf source bundle.
A successful check is NOT an ABI struct-layout, ISA, inference or RAM-unload proof.
Requires the third-party 'pefile' parser in the isolated Windows CI only.
"""
from pathlib import Path
import argparse
import json

from .f5n_bundle_audit import inspect_bundle, FILES


REQUIRED_COMMON_EXPORTS = frozenset({
    "load_model", "generate", "abort_generate", "token_count",
    "get_chat_template",
})
ROUTE_FILE = "backend_routes/koboldcpp_noavx2/koboldcpp_backend.dll"
COMMON_FILE = "koboldcpp_common.dll"
BACKEND_FILE = "koboldcpp_noavx2.dll"


class PeAbiError(ValueError):
    pass


def verify_abi_metadata(bundle, metadata):
    """Verify parsed metadata; metadata keys match FILES and are pure data."""
    if set(metadata) != set(FILES):
        raise PeAbiError("PE files missing or unexpected")
    for filename, item in metadata.items():
        if not isinstance(item, dict) or not isinstance(item.get("exports"), list) or not isinstance(item.get("imports"), list):
            raise PeAbiError("Malformed PE metadata")
        if not all(isinstance(x, str) for x in item["exports"] + item["imports"]):
            raise PeAbiError("Malformed PE symbol names")

    common_exports = set(metadata[COMMON_FILE]["exports"])
    missing = sorted(REQUIRED_COMMON_EXPORTS - common_exports)
    if missing:
        # Fail closed, but report the actual PE names to distinguish export
        # visibility from unexpected naming or a parsing problem.
        sample = sorted(common_exports)[:25]
        raise PeAbiError("Common DLL missing required native API: "
                         + ", ".join(missing)
                         + "; common export count=" + str(len(common_exports))
                         + "; first exports=" + repr(sample))
    if "unload_model" in common_exports:
        # Not asserting safety: merely report that a symbol exists.
        unload_present = True
    else:
        unload_present = False

    if "koboldcpp_backend.dll" not in {x.lower() for x in metadata[COMMON_FILE]["imports"]}:
        raise PeAbiError("Common DLL does not import the expected backend route")
    if not metadata[ROUTE_FILE]["exports"]:
        raise PeAbiError("No backend route forwarder exports")
    if not metadata[BACKEND_FILE]["exports"]:
        raise PeAbiError("No selected backend exports")
    return {
        "upstream_commit": bundle["upstream_commit"],
        "required_common_exports": sorted(REQUIRED_COMMON_EXPORTS),
        "common_native_api_found": True,
        "backend_route_exports_count": len(metadata[ROUTE_FILE]["exports"]),
        "cpu_backend_exports_count": len(metadata[BACKEND_FILE]["exports"]),
        "unload_symbol_present": unload_present,
        "dll_metadata": metadata,
        "dll_sha256": {name: bundle["files"][name]["sha256"] for name in FILES},
        "python_ctypes_layout_verified": False,
        "dll_runtime_load_verified": False,
        "model_inference_verified": False,
        "safe_model_unload_verified": False,
    }


def inspect_pe(root, *, pe_module=None):
    """Read on-disk PE metadata without calling LoadLibrary or ctypes."""
    if pe_module is None:
        try:
            import pefile as pe_module
        except ImportError:
            raise PeAbiError("Missing isolated PE parser dependency") from None
    bundle = inspect_bundle(root)
    # pefile's default MAX_SYMBOL_EXPORT_COUNT is 0x2000 (8192).
    # Upstream's common DLL exports more than 8192 symbols, so the
    # previous parser silently truncated the export table before our ABI.
    # Increase the read ceiling ONLY in this standalone research audit.
    # A hard maximum keeps malformed PE headers from demanding huge scans.
    cap = 65536
    if hasattr(pe_module, "MAX_SYMBOL_EXPORT_COUNT"):
        pe_module.MAX_SYMBOL_EXPORT_COUNT = cap
    metadata = {}
    for relative in FILES:
        target = Path(root).joinpath(*relative.split("/"))
        pe = None
        try:
            pe = pe_module.PE(str(target), fast_load=True)
            pe.parse_data_directories(
                directories=[
                    pe_module.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"],
                    pe_module.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                ])
            export_table = getattr(pe, "DIRECTORY_ENTRY_EXPORT", None)
            if export_table is not None:
                count = int(export_table.struct.NumberOfNames)
                if count > cap:
                    raise PeAbiError("PE named-export count exceeds safe audit cap")
                parsed_names = sum(sym.name is not None for sym in export_table.symbols)
                if parsed_names < count:
                    raise PeAbiError("Incomplete PE export enumeration")
            exports = sorted({
                sym.name.decode("ascii", errors="replace")
                for sym in getattr(export_table, "symbols", ())
                if sym.name is not None
            })
            imports = sorted({
                item.dll.decode("ascii", errors="replace")
                for item in getattr(pe, "DIRECTORY_ENTRY_IMPORT", ())
                if item.dll is not None
            })
            metadata[relative] = {"exports": exports, "imports": imports}
        except PeAbiError:
            raise
        except (OSError, ValueError, AttributeError, UnicodeError) as exc:
            raise PeAbiError("PE metadata inspection failed") from None
        finally:
            if pe is not None:
                pe.close()
    return verify_abi_metadata(bundle, metadata)


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("build_dir", help="Isolated Windows candidate checkout")
    args = cli.parse_args(argv)
    try:
        print(json.dumps(inspect_pe(args.build_dir), indent=2, sort_keys=True))
    except (PeAbiError, OSError, ValueError) as exc:
        cli.error("Native PE ABI metadata gate failed: " + str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
