"""Offline timer command, WAV and popup state checks."""
from __future__ import annotations

import io
import sys
import threading
import unittest
import wave
from types import SimpleNamespace
from unittest.mock import patch

from jarvis_timer import SOUNDS, TimerPopup, alarm_wav, parse_timer_command, play_alarm


class TimerParsingTests(unittest.TestCase):
    def test_voice_and_short_commands(self):
        for text in ("timer 10 minuti", "metti un timer di 10 minuti",
                     "Jarvis, avvia timer da 10 minuti",
                     "Ehi Jarvis timer per 10 min"):
            self.assertEqual(parse_timer_command(text).seconds, 600, text)
            self.assertEqual(parse_timer_command(text).action, "start")
        self.assertEqual(parse_timer_command("timer").action, "open")
        self.assertEqual(parse_timer_command("Jarvis timer di 1 ora 2 minuti 3 secondi").seconds,
                         3723)
        self.assertEqual(parse_timer_command("timer 45 secondi").seconds, 45)

    def test_controls_and_unrelated_conversation(self):
        expected = {"pausa timer": "pause", "riprendi timer": "resume",
                    "stop timer": "stop", "reset timer": "reset",
                    "quanto manca al timer": "remaining"}
        for text, action in expected.items():
            self.assertEqual(parse_timer_command(text).action, action)
        for text in ("timer -15", "timer 100 ore", "timer 3 4 5",
                     "dimmi che ore sono", "il tempo è bello", ""):
            self.assertIsNone(parse_timer_command(text), text)

    def test_default_standalone_number_is_minutes(self):
        self.assertEqual(parse_timer_command("timer 5").seconds, 300)


class AlarmTests(unittest.TestCase):
    def test_wav_for_every_sound_and_volume(self):
        for kind in SOUNDS:
            with self.subTest(kind=kind):
                raw = alarm_wav(kind, 70)
                with wave.open(io.BytesIO(raw), "rb") as audio:
                    self.assertEqual(audio.getnchannels(), 1)
                    self.assertEqual(audio.getframerate(), 16000)
                    self.assertEqual(audio.getsampwidth(), 2)
                    self.assertGreater(audio.getnframes(), 1000)
        self.assertNotEqual(alarm_wav("digital", 0), alarm_wav("digital", 100))

    def test_invalid_sound_and_volume(self):
        for kind, volume in (("other", 20), ("digital", -1),
                             ("digital", 101), ("digital", True)):
            with self.assertRaises(ValueError):
                alarm_wav(kind, volume)

    def test_filename_wav_playback_reports_selected_backend(self):
        calls, statuses = [], []
        fake = SimpleNamespace(
            SND_FILENAME=1, SND_NODEFAULT=4, SND_MEMORY=8,
            PlaySound=lambda payload, flags: calls.append((payload, flags)),
            Beep=lambda freq, ms: self.fail("Fallback beep should not run"),
            MessageBeep=lambda: self.fail("MessageBeep should not run"),
        )
        with patch.dict(sys.modules, {"winsound": fake}):
            play_alarm("digital", 80, threading.Event(),
                       on_status=lambda *value: statuses.append(value))
        self.assertTrue(calls)
        self.assertTrue(calls[0][1] & fake.SND_FILENAME)
        self.assertTrue(statuses[0][0])
        self.assertIn("WAV", statuses[0][1])

    def test_wav_failures_fall_back_to_beep(self):
        calls, statuses = [], []
        def broken_wav(payload, flags):
            raise RuntimeError("No WAV output")
        fake = SimpleNamespace(
            SND_FILENAME=1, SND_NODEFAULT=4, SND_MEMORY=8,
            PlaySound=broken_wav,
            Beep=lambda freq, ms: calls.append((freq, ms)),
            MessageBeep=lambda: self.fail("Beep worked; system signal not needed"),
        )
        with patch.dict(sys.modules, {"winsound": fake}):
            play_alarm("double", 80, threading.Event(),
                       on_status=lambda *value: statuses.append(value))
        self.assertGreater(len(calls), 0)
        self.assertEqual(statuses[0][0], True)
        self.assertIn("bip alternativo", statuses[0][1])

    def test_volume_zero_reports_visible_error(self):
        statuses = []
        play_alarm("digital", 0, threading.Event(),
                   on_status=lambda *result: statuses.append(result))
        self.assertEqual(statuses[0][0], False)
        self.assertIn("0%", statuses[0][1])

    def test_start_resumes_when_paused_without_editing_duration(self):
        t = TimerPopup(root=None, get_preferences=lambda: {})
        t.duration = 600
        t.remaining = 185.0
        t.paused = True
        with patch.object(t, "show"), patch.object(t, "resume") as resume:
            self.assertTrue(t.start())
            resume.assert_called_once()

    def test_remaining_and_pause_use_monotonic_time_without_tk(self):
        # Logic can be exercised on build agents without any desktop.
        t = TimerPopup(root=None, get_preferences=lambda: {})
        t.duration = 120
        t.remaining = 120.0
        t.running = True
        t.deadline = 200.0
        with patch("jarvis_timer.time.monotonic", return_value=125.0):
            self.assertEqual(t.remaining_text(), "01:15")
        t.running = False
        self.assertEqual(t.remaining_text(), "01:15")


if __name__ == "__main__":
    unittest.main()
