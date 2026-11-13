"""F5N.2 bundle completeness and no side effects (Windows CI)."""
import unittest
import tempfile
from pathlib import Path

from tools.f5n_bundle_audit import BundleError, FILES, UPSTREAM_SHA, inspect_bundle


class TestF5NBundleAudit(unittest.TestCase):
    def test_valid_split_bundle_does_not_execute_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in FILES:
                p = root / relative
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b"MZ" + b"\0" * 2048)
            info = inspect_bundle(root)
            self.assertEqual(info["upstream_commit"], UPSTREAM_SHA)
            self.assertEqual(set(info["files"]), set(FILES))
            self.assertFalse(info["runtime_abi_verified"])
            self.assertFalse(info["safe_model_unload_verified"])

    def test_reject_missing_route_or_invalid_pe(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in FILES[:-1]:
                p = root / relative
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b"MZ" + b"\0" * 2048)
            with self.assertRaises(BundleError):
                inspect_bundle(root)
            last = root / FILES[-1]
            last.parent.mkdir(parents=True, exist_ok=True)
            last.write_bytes(b"xx" + b"\0" * 2048)
            with self.assertRaises(BundleError):
                inspect_bundle(root)
            last.write_bytes(b"MZ" + b"\0" * 2048)
            self.assertEqual(len(inspect_bundle(root)["files"]), 4)


if __name__ == "__main__":
    unittest.main()
