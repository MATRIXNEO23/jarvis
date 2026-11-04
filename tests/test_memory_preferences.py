from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from local_model.memory_preferences import MemoryPreferences


class MemoryPreferencesTests(unittest.TestCase):
    def test_defaults_and_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.json"
            original = MemoryPreferences.load(path)
            self.assertEqual(original.idle_seconds, 60)
            self.assertEqual(original.recent_messages, 8)
            self.assertTrue(original.conversation_priority)
            changed = replace(original, idle_seconds=90, prompt_max_tokens=1024)
            changed.save(path)
            self.assertEqual(MemoryPreferences.load(path), changed)

    def test_reject_invalid_without_overwriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.json"
            original = MemoryPreferences()
            original.save(path)
            before = path.read_bytes()
            for changes in (
                {"idle_seconds": 0},
                {"idle_seconds": True},
                {"max_background_jobs": 2},
                {"summary_max_tokens": 700, "prompt_max_tokens": 600},
                {"conversation_priority": "false"},
            ):
                with self.subTest(changes=changes), self.assertRaises(ValueError):
                    replace(original, **changes).save(path)
                self.assertEqual(path.read_bytes(), before)

    def test_model_window_reservation(self):
        prefs = MemoryPreferences()
        self.assertEqual(prefs.available_prompt_tokens(2048, 128), 600)
        self.assertEqual(prefs.available_prompt_tokens(512, 128), 256)
        with self.assertRaises(ValueError):
            prefs.available_prompt_tokens(256, 200)
        with self.assertRaises(ValueError):
            prefs.available_prompt_tokens(1024, True)

    def test_corrupt_preferences_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.json"
            path.write_text("{bad")
            with self.assertRaises(ValueError):
                MemoryPreferences.load(path)
            self.assertEqual(path.read_text(), "{bad")


if __name__ == "__main__":
    unittest.main()
