"""F5.1 read-only availability tests; no server or GGUF needed."""
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from local_model.model_profiles_f5 import default_profiles, ProfileError
from local_model.model_availability_f5 import inspect_embedded, inspect_koboldcpp
from local_model.kobold_server_canary import KoboldServerCanary, KoboldCanaryError


class TestF51Availability(unittest.TestCase):
    def setUp(self):
        self.gemma, self.qwen = default_profiles()

    def test_embedded_missing_configuration(self):
        result = inspect_embedded(self.gemma, gguf_path="", dll_path="")
        self.assertFalse(result.available)
        self.assertEqual(result.status, "missing_configuration")

    def test_embedded_paths_are_checked_without_loading(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / "model.gguf"
            dll = Path(tmp) / "kobold.dll"
            self.assertEqual(inspect_embedded(self.gemma, gguf_path=str(model),
                             dll_path=str(dll)).status, "gguf_unavailable")
            model.write_bytes(b"fake")
            self.assertEqual(inspect_embedded(self.gemma, gguf_path=str(model),
                             dll_path=str(dll)).status, "library_unavailable")
            dll.write_bytes(b"fake")
            got = inspect_embedded(self.gemma, gguf_path=str(model), dll_path=str(dll))
            self.assertTrue(got.available)
            self.assertEqual(got.status, "files_present_not_loaded")
            self.assertIsNone(got.model_identity)

    def test_wrong_backend_rejected(self):
        with self.assertRaises(ProfileError):
            inspect_embedded(self.qwen, gguf_path="a", dll_path="b")
        with self.assertRaises(ProfileError):
            inspect_koboldcpp(self.gemma, canary=None, expected_model="x")

    def test_server_probe_is_read_only_and_exact(self):
        canary = KoboldServerCanary()
        with patch.object(KoboldServerCanary, "probe", return_value="Qwen-GGUF") as probe:
            good = inspect_koboldcpp(self.qwen, canary=canary,
                                     expected_model="Qwen-GGUF")
            self.assertTrue(good.available)
            self.assertEqual(good.model_identity, "Qwen-GGUF")
            mismatch = inspect_koboldcpp(self.qwen, canary=canary,
                                         expected_model="other")
            self.assertFalse(mismatch.available)
            self.assertEqual(mismatch.status, "model_mismatch")
            self.assertEqual(probe.call_count, 2)

    def test_server_is_not_reachable(self):
        canary = KoboldServerCanary()
        with patch.object(KoboldServerCanary, "probe",
                          side_effect=KoboldCanaryError("no server")):
            got = inspect_koboldcpp(self.qwen, canary=canary, expected_model="Qwen")
            self.assertFalse(got.available)
            self.assertEqual(got.status, "server_unavailable_or_unverified")

    def test_server_does_not_accept_unverified_client(self):
        with self.assertRaises(ProfileError):
            inspect_koboldcpp(self.qwen, canary=object(), expected_model="Qwen")

    def test_no_automatic_switch_or_chat(self):
        import inspect
        from local_model import model_availability_f5
        source = inspect.getsource(model_availability_f5)
        for forbidden in (".generate(", ".load(", ".ask(", "subprocess.",
                          "open(", "os.system(", ".save("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
