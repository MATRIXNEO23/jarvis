"""Native settings validation and non-destructive configuration tests."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from local_model.native_config import NativeModelConfig
from local_model.native_settings import (
    default_native_settings_path, native_settings_view, update_native_settings,
)


@unittest.skipUnless(os.name == "nt", "Windows-only")
class NativeSettingsTests(unittest.TestCase):
    def test_generation_settings_do_not_require_reload(self):
        original = NativeModelConfig()
        updated, reload_required = update_native_settings(
            original, {"max_output": 256, "temperature": 0.5, "top_k": 40})
        self.assertFalse(reload_required)
        self.assertEqual(original.max_output, 128)
        self.assertEqual(updated.max_output, 256)

    def test_context_and_threads_require_reload(self):
        for field, value in (("context_size", 4096), ("threads", 3),
                             ("batch_threads", 3), ("model", "another.gguf")):
            with self.subTest(field=field):
                _, reload_required = update_native_settings(
                    NativeModelConfig(), {field: value})
                self.assertTrue(reload_required)

    def test_rejects_unknown_and_invalid_without_mutation(self):
        original = NativeModelConfig()
        for changes in ({"dll": "injected.dll"}, {"max_output": 999999},
                        {"threads": 0}, {"temperature": float("nan")},
                        {"max_output": "128"}):
            with self.subTest(changes=str(changes)):
                with self.assertRaises(ValueError):
                    update_native_settings(original, changes)
        self.assertEqual(original, NativeModelConfig())

    def test_settings_are_isolated_from_main_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"JARVIS_TRIAL_HOME": tmp}):
                path = default_native_settings_path()
                self.assertEqual(
                    path, Path(tmp) / "addon-data" / "modello_locale" / "native.json")
                self.assertNotEqual(path, Path(tmp) / "settings.json")
                config = NativeModelConfig(max_output=64)
                config.save(path)
                self.assertEqual(NativeModelConfig.load(path), config)

    def test_view_excludes_dll(self):
        values = native_settings_view(NativeModelConfig())
        self.assertNotIn("dll", values)
        self.assertIn("context_size", values)
        self.assertIn("max_output", values)


if __name__ == "__main__":
    unittest.main()
