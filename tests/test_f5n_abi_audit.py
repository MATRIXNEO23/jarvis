"""F5N.1: pure filesystem/source ABI inventory tests (Windows CI)."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from tools.f5n_abi_audit import AbiAuditError, inventory


class TestF5NAbiAudit(unittest.TestCase):
    def test_inventory_is_explicit_and_does_not_load_dll(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            cpp = root / "expose.cpp"
            py = root / "koboldcpp.py"
            dll = root / "noavx2.dll"
            cpp.write_text(
                'extern "C" {\nbool load_model(const load_model_inputs inputs) {return true;}\n'
                'const char* get_chat_template() {return ""; }\n'
                '// unload_model(); is NOT a definition\n}\n', encoding="utf-8")
            py.write_text('handle.load_model.argtypes = []\n'
                          'handle.get_chat_template.restype = None\n', encoding="utf-8")
            dll.write_bytes(b"Not executable DLL bytes; never loaded")
            result = inventory(cpp, py, dll)
            self.assertEqual(result["dll_sha256"], hashlib.sha256(dll.read_bytes()).hexdigest())
            self.assertTrue(result["api"]["load_model"]["cpp_definition_candidate"])
            self.assertTrue(result["api"]["load_model"]["python_ctypes_binding_reference"])
            self.assertTrue(result["api"]["get_chat_template"]["cpp_definition_candidate"])
            self.assertFalse(result["api"]["unload_model"]["cpp_definition_candidate"])
            self.assertFalse(result["api"]["unload_model"]["python_ctypes_binding_reference"])
            self.assertFalse(result["physical_model_unload_verified"])
            self.assertFalse(result["inference_verified"])

    def test_unavailable_or_empty_dll_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            cpp = root / "expose.cpp"
            py = root / "koboldcpp.py"
            cpp.write_text("bool load_model(){}", encoding="utf-8")
            py.write_text("handle.load_model", encoding="utf-8")
            with self.assertRaises(AbiAuditError):
                inventory(cpp, py, root / "nonexistent.dll")
            empty = root / "empty.dll"
            empty.write_bytes(b"")
            with self.assertRaises(AbiAuditError):
                inventory(cpp, py, empty)


if __name__ == "__main__":
    unittest.main()
