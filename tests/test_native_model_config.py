"""Windows-only native model configuration regression checks."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from local_model.native_config import NativeModelConfig


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class NativeModelConfigTests(unittest.TestCase):
    def test_round_trip_all_generation_settings(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "native.json"
            expected = NativeModelConfig(
                dll="C:/Lumi/koboldcpp_noavx2.dll",
                model="C:/Models/gemma.gguf", threads=2,
                batch_threads=2, context_size=4096,
                max_output=512, temperature=0.4,
                top_k=50, top_p=0.95, seed=42)
            expected.save(path)
            self.assertEqual(NativeModelConfig.load(path), expected)

    def test_older_settings_load_without_personality(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "native.json"
            NativeModelConfig(seed=42).save(path)
            saved = json.loads(path.read_text(encoding="utf-8"))
            del saved["personality"]
            path.write_text(json.dumps(saved), encoding="utf-8")
            self.assertEqual(NativeModelConfig.load(path), NativeModelConfig(seed=42))

    def test_reject_bad_parameters(self):
        for changes in (
            {"threads": 0}, {"threads": True},
            {"context_size": 128}, {"max_output": 9000},
            {"context_size": 256, "max_output": 512},
            {"temperature": -1}, {"top_p": 1.5},
            {"seed": 2147483648}, {"model": "bad" + chr(0) + "path"}
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    NativeModelConfig(**changes).validate()

    def test_corrupt_config_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "native.json"
            path.write_text("{broken", encoding="utf-8")
            with self.assertRaises(ValueError):
                NativeModelConfig.load(path)
            self.assertEqual(path.read_text(encoding="utf-8"), "{broken")

    def test_save_invalid_does_not_replace_existing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "native.json"
            path.write_text("keep", encoding="utf-8")
            with self.assertRaises(ValueError):
                NativeModelConfig(threads=0).save(path)
            self.assertEqual(path.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
