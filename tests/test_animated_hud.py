"""Animated HUD math and speaker status; no GUI or microphone is opened."""
import math
import unittest
from threading import Event

from animated_hud import (
    BG, BLUE, TURQUOISE, WHITE, LAND, TICK_MS,
    interpolate_color, projected_earth_point, JarvisHUD, WindowsCPU,
)
from hud_reference import AMBER, GREEN, CYAN, core_light, core_mode, clip_coast, COASTS
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
        self.assertEqual(BG, "#010711")

    def test_three_audio_states_have_distinct_center_colors(self):
        self.assertEqual(core_mode(speaking=False,listening=False),"idle")
        self.assertEqual(core_mode(speaking=False,listening=True),"listening")
        self.assertEqual(core_mode(speaking=True,listening=True),"speaking")
        idle_color,idle_pulse=core_light("idle",0)
        listen_color,_=core_light("listening",0)
        speak_color,_=core_light("speaking",0)
        self.assertEqual((idle_color,listen_color,speak_color),
                         (CYAN,AMBER,GREEN))
        self.assertNotEqual(idle_color,listen_color)
        self.assertNotEqual(idle_color,speak_color)
        self.assertGreater(core_light("listening",.2)[1],
                           core_light("listening",0)[1])
        self.assertNotEqual(core_light("speaking",0)[1],
                            core_light("speaking",.2)[1])

    def test_geographic_land_has_visible_front_clipping(self):
        africa=COASTS[0]
        visible=clip_coast(africa,0,100)
        self.assertGreater(len(visible),6)
        self.assertTrue(all(abs(x)<=101 and abs(y)<=101 for x,y in visible))
        # After half turn Africa is not visible on the front hemisphere.
        self.assertEqual(clip_coast(africa,math.pi,100),[])

    def test_cpu_sample_safe_when_not_windows(self):
        import os
        if os.name!="nt":
            self.assertIsNone(WindowsCPU().sample())

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
