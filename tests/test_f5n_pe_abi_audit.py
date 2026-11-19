"""F5N.3 synthetic PE metadata regression: no DLL load, inference or disk changes."""
import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace

from tools.f5n_bundle_audit import FILES
from tools.f5n_pe_abi_audit import PeAbiError, verify_abi_metadata, inspect_pe


def _bundle():
    return {
        "upstream_commit": "pinned",
        "files": {file: {"sha256": "a" * 64} for file in FILES},
    }


def _metadata():
    return {
        FILES[0]: {
            "exports": ["load_model", "generate", "abort_generate",
                        "token_count", "get_chat_template"],
            "imports": ["KERNEL32.dll", "koboldcpp_backend.dll"],
        },
        FILES[1]: {"exports": ["cpu_backend"], "imports": ["KERNEL32.dll"]},
        FILES[2]: {"exports": ["cpu_backend"], "imports": ["KERNEL32.dll"]},
        FILES[3]: {"exports": ["cpu_backend"], "imports": ["KERNEL32.dll"]},
    }


class TestF5N3PEABI(unittest.TestCase):
    def test_required_exports_and_forwarder(self):
        result = verify_abi_metadata(_bundle(), _metadata())
        self.assertTrue(result["common_native_api_found"])
        self.assertFalse(result["python_ctypes_layout_verified"])
        self.assertFalse(result["dll_runtime_load_verified"])
        self.assertFalse(result["model_inference_verified"])
        self.assertFalse(result["safe_model_unload_verified"])

    def test_missing_common_export_blocks(self):
        item = _metadata()
        item[FILES[0]]["exports"].remove("token_count")
        with self.assertRaisesRegex(PeAbiError, "token_count"):
            verify_abi_metadata(_bundle(), item)

    def test_missing_import_or_forwarder_blocks(self):
        item = _metadata()
        item[FILES[0]]["imports"] = ["KERNEL32.dll"]
        with self.assertRaisesRegex(PeAbiError, "backend"):
            verify_abi_metadata(_bundle(), item)
        item = _metadata()
        item[FILES[3]]["exports"] = []
        with self.assertRaisesRegex(PeAbiError, "forwarder"):
            verify_abi_metadata(_bundle(), item)

    def test_unload_name_does_not_prove_safe_release(self):
        item = _metadata()
        item[FILES[0]]["exports"].append("unload_model")
        result = verify_abi_metadata(_bundle(), item)
        self.assertTrue(result["unload_symbol_present"])
        self.assertFalse(result["safe_model_unload_verified"])

    def test_inspect_pe_uses_explicit_high_export_cap(self):
        # Fake parser intentionally rejects the default pefile 8192-symbol cap.
        with tempfile.TemporaryDirectory() as directory:
            for filename in FILES:
                file = Path(directory) / filename
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(b"MZ" + bytes(2048))

            class Parser:
                DIRECTORY_ENTRY = {
                    "IMAGE_DIRECTORY_ENTRY_EXPORT": 0,
                    "IMAGE_DIRECTORY_ENTRY_IMPORT": 1,
                }
                calls = []

                class PE:
                    def __init__(self, filename, *, fast_load, max_symbol_exports):
                        Parser.calls.append(max_symbol_exports)
                        assert max_symbol_exports > 8192
                        self.filename = filename

                    def parse_data_directories(self, *, directories):
                        assert directories == [0, 1]
                        name = self.filename.replace(chr(92), "/")
                        exports = _metadata()[next(x for x in FILES if name.endswith(x))]
                        names = exports["exports"]
                        self.DIRECTORY_ENTRY_EXPORT = SimpleNamespace(
                            struct=SimpleNamespace(NumberOfNames=len(names)),
                            symbols=[SimpleNamespace(name=n.encode("ascii")) for n in names],
                        )
                        self.DIRECTORY_ENTRY_IMPORT = [
                            SimpleNamespace(dll=n.encode("ascii"))
                            for n in exports["imports"]
                        ]

                    def close(self):
                        pass

            result = inspect_pe(directory, pe_module=Parser)
            self.assertTrue(result["common_native_api_found"])
            self.assertEqual(Parser.calls, [65536] * len(FILES))

    def test_missing_dll_metadata_blocks(self):
        item = _metadata()
        item.pop(FILES[-1])
        with self.assertRaises(PeAbiError):
            verify_abi_metadata(_bundle(), item)


if __name__ == "__main__":
    unittest.main()
