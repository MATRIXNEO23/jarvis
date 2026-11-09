"""F5N.4 smoke guard tests: never call native Windows loader in unit CI."""
import os
from pathlib import Path
import tempfile
import unittest

from tools.f5n_bundle_audit import FILES
from tools.f5n_native_load_smoke import (
    NativeSmokeError, expected_paths, run_isolated, toolchain_runtime_imports,
)


class NativeSmokeGuardTests(unittest.TestCase):
    def test_bundle_route_paths_and_no_side_effects(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            for relative in FILES:
                path = root.joinpath(*relative.split("/"))
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"MZ" + bytes(1024))
            result = expected_paths(root)
            # Windows may expand the temporary directory 8.3 alias
            # (RUNNER~1) into its canonical long path (runneradmin).
            canonical_root = result["root"]
            self.assertEqual(result["route"], canonical_root / FILES[-1])
            self.assertEqual(result["common"], canonical_root / FILES[0])
            self.assertEqual(result["backend"], canonical_root / FILES[2])

    @unittest.skipIf(os.name == "nt", "Non-Windows guard only")
    def test_non_windows_cannot_run_native_load(self):
        with self.assertRaisesRegex(NativeSmokeError, "Windows"):
            run_isolated("/tmp/does-not-exist")

    def test_toolchain_runtime_imports_are_reported_per_dll(self):
        # Mirrors the WinError 127 run 42595625501: MSYS2 runtime imports.
        imports = {
            "route": {"KERNEL32.dll", "msvcrt.dll"},
            "common": {"KERNEL32.dll", "koboldcpp_backend.dll",
                       "libstdc++-6.dll", "libgcc_s_seh-1.dll",
                       "libwinpthread-1.dll"},
            "backend": {"KERNEL32.dll", "LIBSTDC++-6.DLL"},
        }
        paths = {key: key for key in imports}
        self.assertEqual(
            toolchain_runtime_imports(paths, read_imports=imports.__getitem__),
            {"common": ["libgcc_s_seh-1.dll", "libstdc++-6.dll",
                        "libwinpthread-1.dll"],
             "backend": ["libstdc++-6.dll"]})

    def test_self_contained_bundle_has_no_runtime_imports(self):
        imports = {key: {"KERNEL32.dll", "msvcrt.dll", "WS2_32.dll"}
                   for key in ("route", "common", "backend")}
        paths = {key: key for key in imports}
        self.assertEqual(
            toolchain_runtime_imports(paths, read_imports=imports.__getitem__), {})


if __name__ == "__main__":
    unittest.main()
