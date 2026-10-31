"""Animated HUD math and speaker status; no GUI or microphone is opened."""
import math
import unittest
from threading import Event

from animated_hud import (
    BG, BLUE, TURQUOISE, WHITE, LAND, TICK_MS,
    interpolate_color, projected_earth_point, JarvisHUD,
)
from offline_tts import OfflineSpeaker


class AnimatedHUDGeometryTests(unittest.TestCase):
    def test_core_uses_a_fixed_blue_to_turquoise_color_transition(self):
        self.assertEqual(interpolate_color(BLUE, TURQUOISE, 0), BLUE)
        self.assertEqual(interpolate_color(BLUE, TURQUOISE, 1), TURQUOISE)
        mid = interpolate_color(BLUE, TURQUOISE, .5)
        self.assertNotEqual(mid, BLUE)
        self.assertNotEqual(mid, TURQUOISE)
        self.assertEqual(interpolate_color(BLUE, TURQUOISE, -5), BLUE)
        self.assertEqual(interpolate_color(BLUE, TURQUOISE, 25), TURQUOISE)
        self.assertTrue(mid.startswith("#"))
        self.assertEqual(len(mid), 7)

    def test_globe_orthographic_projection_hides_back_of_planet(self):
        self.assertIsNotNone(projected_earth_point(0, 0, 0, 100))
        self.assertIsNone(projected_earth_point(0, 180, 0, 100))
        self.assertAlmostEqual(
            projected_earth_point(0, 90, 0, 100)[0], 100, delta=.0001)
        self.assertEqual(projected_earth_point(90, 0, 0, 100)[1], -100)
        front = projected_earth_point(0, 0, math.pi, 100)
        self.assertIsNone(front)

    def test_earth_is_visible_but_low_overhead(self):
        self.assertGreater(len(LAND), 50)
        self.assertLess(len(LAND), 600)
        self.assertGreaterEqual(TICK_MS, 90)
        self.assertLessEqual(TICK_MS, 220)
        self.assertEqual(BG, "#020b13")

    def test_hud_has_safe_shutdown_api(self):
        # A fake HUD has no Tk widgets, but its stop mechanism should be
        # independent from the microphone state and other background threads.
        hud = object.__new__(JarvisHUD)
        hud.closed = False
        hud.close()
        self.assertTrue(hud.closed)


class OfflineSpeechActivityTests(unittest.TestCase):
    def test_speech_status_is_actual_sapi_busy_not_recognition_cooldown(self):
        blocked = Event()
        finish = Event()

        def fake_sapi(_payload, *, timeout):
            blocked.set()
            finish.wait(2)
            return ""

        speaker = OfflineSpeaker(runner=fake_sapi)
        try:
            self.assertFalse(speaker.is_speaking())
            self.assertTrue(speaker.speak("Ciao, sto parlando."))
            self.assertTrue(blocked.wait(timeout=2))
            self.assertTrue(speaker.is_speaking())
            finish.set()
            for _ in range(80):
                if not speaker.is_speaking():
                    break
                import time
                time.sleep(.02)
            self.assertFalse(speaker.is_speaking())
            self.assertTrue(speaker.is_audible())
        finally:
            finish.set()
            speaker.close()


if __name__ == "__main__":
    unittest.main()
