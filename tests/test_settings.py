"""Run with: py -3 -m unittest discover -s tests"""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from settings import load_settings, save_settings


class SettingsTests(unittest.TestCase):
    def test_default_chatgpt_enabled(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            self.assertEqual(load_settings(path), {"gpt_enabled": True})

    def test_disable_then_reenable_persists(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            save_settings({"gpt_enabled": False}, path)
            self.assertFalse(load_settings(path)["gpt_enabled"])
            save_settings({"gpt_enabled": True}, path)
            self.assertTrue(load_settings(path)["gpt_enabled"])

    def test_invalid_file_falls_back_to_default(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            path.write_text('{"gpt_enabled": "no"}', encoding="utf-8")
            self.assertTrue(load_settings(path)["gpt_enabled"])

    def test_reject_non_bool(self):
        with TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                save_settings({"gpt_enabled": "yes"}, Path(folder) / "settings.json")


if __name__ == "__main__":
    unittest.main()
