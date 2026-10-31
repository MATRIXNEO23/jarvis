"""Test the lightweight voice activity indicator and spoken greetings."""
from array import array
import time
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from speech_activity import SpeechActivity, pcm16_rms
from startup_greeting import greeting_for_hour
from hud_reference import CYAN, AMBER, GREEN, core_light, core_mode
from voice_control import VoiceController, GPT_CONVERSATION, STANDBY


def audio(level):
    return (array("h", [level]) * 4000).tobytes()


class ActivityTests(unittest.TestCase):
    def test_quiet_room_is_cyan_even_with_open_microphone(self):
        gate = SpeechActivity()
        self.assertFalse(gate.feed(audio(70), now=10))
        self.assertFalse(gate.feed(audio(95), now=10.25))
        self.assertEqual(core_mode(speaking=False, listening=False), "idle")
        self.assertEqual(core_light("idle", 10)[0], CYAN)

    def test_speech_is_orange_then_cyan_after_release(self):
        gate = SpeechActivity()
        gate.feed(audio(80), now=10)
        self.assertTrue(gate.feed(audio(1400), now=10.25))
        self.assertEqual(core_light("listening", 10.25)[0], AMBER)
        self.assertTrue(gate.feed(audio(60), now=10.50))
        self.assertFalse(gate.feed(audio(60), now=11.20))

    def test_jarvis_voice_is_green_not_orange(self):
        self.assertEqual(core_mode(speaking=True, listening=True), "speaking")
        self.assertEqual(core_light("speaking", 10)[0], GREEN)
        gate = SpeechActivity()
        gate.feed(audio(70), now=1)
        gate.feed(audio(1500), now=1.25)
        gate.reset()
        self.assertFalse(gate.is_active(now=1.3))

    def test_room_noise_threshold(self):
        gate = SpeechActivity()
        self.assertFalse(gate.feed(audio(500), now=1))
        self.assertFalse(gate.feed(audio(600), now=1.25))
        self.assertTrue(gate.feed(audio(1800), now=1.5))

    def test_open_stream_without_speech_is_not_orange(self):
        with TemporaryDirectory() as folder:
            voice = VoiceController(
                lambda event: None, Path(folder) / "no-audio-model")
            self.assertFalse(voice.is_listening())
            self.assertFalse(voice.is_user_speaking())
            with voice._lock:
                voice.mode = GPT_CONVERSATION
                voice._generation = 3
                voice._active_generation = 3
            self.assertTrue(voice.is_listening())
            self.assertFalse(voice.is_user_speaking())
            with voice._lock:
                voice._speech_active_until = time.monotonic() + 1
            self.assertTrue(voice.is_user_speaking())
            voice.close()
            self.assertEqual(voice.mode, STANDBY)
            self.assertFalse(voice.is_user_speaking())

    def test_audio_rms(self):
        self.assertEqual(pcm16_rms(audio(500)), 500)
        self.assertEqual(pcm16_rms(audio(-500)), 500)
        self.assertEqual(pcm16_rms(audio(0)), 0)


class GreetingTests(unittest.TestCase):
    def test_greetings_follow_hour(self):
        for hour, start in (
            (0, "Buonanotte"), (4, "Buonanotte"), (5, "Buongiorno"),
            (11, "Buongiorno"), (12, "Buon pomeriggio"),
            (17, "Buon pomeriggio"), (18, "Buonasera"), (23, "Buonasera")
        ):
            self.assertTrue(greeting_for_hour(hour).startswith(start))
            self.assertIn("signore", greeting_for_hour(hour))

    def test_invalid_hours(self):
        for hour in (-1, 24, 3.5, "oggi"):
            with self.assertRaises(ValueError):
                greeting_for_hour(hour)


if __name__ == "__main__":
    unittest.main()
