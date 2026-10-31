"""Run with: py -3 -m unittest discover -s tests"""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from settings import load_settings, save_settings


class SettingsTests(unittest.TestCase):
    def test_default_chatgpt_enabled(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            self.assertEqual(load_settings(path), {"gpt_enabled": True, "tts_enabled": False, "tts_voice": "",
                                                         "memory_enabled": False,
                                                         "auto_listen": True,"telegram_enabled": False,"telegram_peer_id": 0,"telegram_contact_name": "", "telegram_contacts": [], "timer_sound": "digital", "timer_volume": 80, "timer_repeat": True, "timer_audio_mode": "auto"})

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

    def test_tts_preferences_persist_without_losing_gpt(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            save_settings({"gpt_enabled": False, "tts_enabled": True,
                           "tts_voice": "Voce italiana"}, path)
            self.assertEqual(load_settings(path),
                             {"gpt_enabled": False, "tts_enabled": True,
                              "tts_voice": "Voce italiana", "memory_enabled": False,
                              "auto_listen": True,"telegram_enabled": False,"telegram_peer_id": 0,"telegram_contact_name": "", "telegram_contacts": [], "timer_sound": "digital", "timer_volume": 80, "timer_repeat": True, "timer_audio_mode": "auto"})

    def test_memory_opt_in_is_persistent_and_independent(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            self.assertFalse(load_settings(path)["memory_enabled"])
            save_settings({"gpt_enabled": True, "memory_enabled": True}, path)
            self.assertTrue(load_settings(path)["memory_enabled"])
            save_settings({"gpt_enabled": False, "memory_enabled": False}, path)
            self.assertFalse(load_settings(path)["memory_enabled"])
            with self.assertRaises(ValueError):
                save_settings({"gpt_enabled": True,
                               "memory_enabled": "enabled"}, path)

    def test_auto_listening_default_and_explicit_opt_out(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            self.assertTrue(load_settings(path)["auto_listen"])
            save_settings({"gpt_enabled": True, "auto_listen": False}, path)
            self.assertFalse(load_settings(path)["auto_listen"])
            save_settings({"gpt_enabled": True, "auto_listen": True}, path)
            self.assertTrue(load_settings(path)["auto_listen"])
            with self.assertRaises(ValueError):
                save_settings({"gpt_enabled": True, "auto_listen": "no"}, path)

    def test_existing_settings_are_migrated(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            path.write_text('{"gpt_enabled": false}', encoding="utf-8")
            self.assertEqual(load_settings(path)["gpt_enabled"], False)
            self.assertEqual(load_settings(path)["tts_enabled"], False)

    def test_timer_preferences_round_trip_and_validation(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            current = load_settings(path)
            current.update(timer_sound="siren", timer_volume=35, timer_repeat=False)
            save_settings(current, path)
            self.assertEqual(load_settings(path)["timer_sound"], "siren")
            self.assertEqual(load_settings(path)["timer_volume"], 35)
            self.assertFalse(load_settings(path)["timer_repeat"])
            self.assertEqual(load_settings(path)["timer_audio_mode"], "auto")
            current["timer_audio_mode"] = "beep"
            save_settings(current, path)
            self.assertEqual(load_settings(path)["timer_audio_mode"], "beep")
            for change in ({"timer_sound": "invalid"},
                           {"timer_volume": 101},
                           {"timer_volume": True},
                           {"timer_repeat": "false"},
                           {"timer_audio_mode": "invalid"}):
                changed = dict(current, **change)
                with self.assertRaises(ValueError):
                    save_settings(changed, path)
            self.assertEqual(load_settings(path)["telegram_contacts"], [])

    def test_reject_non_bool(self):
        with TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                save_settings({"gpt_enabled": "yes"}, Path(folder) / "settings.json")


if __name__ == "__main__":
    unittest.main()
