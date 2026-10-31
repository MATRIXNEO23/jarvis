"""No-network timer regression: parse, countdown, alarm and app wiring."""
import io
import os
from pathlib import Path
import struct
import tempfile
import unittest
import wave
from unittest.mock import patch

from timer_core import (
    Countdown, MAX_TIMER_SECONDS, TimerIntent, format_remaining,
    parse_timer_intent)
from timer_alarm import ALARM_PATTERNS, alarm_wave, AlarmPlayer
from settings import load_settings, save_settings


class FakeClock:
    def __init__(self):
        self.now=1000.0
    def __call__(self):
        return self.now
    def advance(self,seconds):
        self.now+=seconds


class TimerParserTests(unittest.TestCase):
    def test_exact_local_start_phrases(self):
        examples={
            "timer 5 minuti":300,
            "Jarvis, metti un timer di dieci minuti":600,
            "imposta timer per 1 ora e 30 minuti":5400,
            "avvia timer di 15 secondi":15,
            "timer due minuti e trenta secondi":150,
            "ehi jarvis timer venticinque minuti":1500,
            "metti un timer di un minuto":60,
            "timer 23 ore 59 minuti 59 secondi":MAX_TIMER_SECONDS,
        }
        for phrase,value in examples.items():
            with self.subTest(phrase=phrase):
                self.assertEqual(parse_timer_intent(phrase),
                                 TimerIntent("start",value))

    def test_timer_alone_opens_editable_window_without_starting(self):
        for phrase in ("timer", "Jarvis timer", "apri timer",
                       "metti un timer"):
            self.assertEqual(parse_timer_intent(phrase),TimerIntent("open"))

    def test_control_commands(self):
        for phrase,action in (
                ("pausa timer","pause"),("metti in pausa il timer","pause"),
                ("stop timer","stop"),("ferma timer","stop"),
                ("riprendi timer","resume"),("resetta timer","reset")):
            self.assertEqual(parse_timer_intent(phrase),TimerIntent(action))

    def test_untrusted_or_out_of_range_not_executed(self):
        for phrase in ("Mi piace il timer","Non avviare un timer",
                       "timer 30 ore", "timer 0 minuti",
                       "timer 200000 minuti","timer 5 minuti 8 minuti",
                       "apri blocco note","timer 1 minuto e avvia powershell"):
            with self.subTest(phrase=phrase):
                result=parse_timer_intent(phrase)
                self.assertFalse(result and result.action=="start")

    def test_digital_format_ceils_until_expiry(self):
        self.assertEqual(format_remaining(60),"00:01:00")
        self.assertEqual(format_remaining(59.8),"00:01:00")
        self.assertEqual(format_remaining(0),"00:00:00")
        self.assertEqual(format_remaining(3601),"01:00:01")


class CountdownTests(unittest.TestCase):
    def test_elapsed_pause_resume_and_one_alarm(self):
        clock=FakeClock()
        timer=Countdown(90,clock=clock)
        self.assertTrue(timer.start())
        clock.advance(29.7)
        self.assertAlmostEqual(timer.remaining(),60.3)
        self.assertTrue(timer.pause())
        clock.advance(200)
        self.assertAlmostEqual(timer.remaining(),60.3)
        self.assertTrue(timer.start())
        clock.advance(60.3)
        self.assertTrue(timer.check_finished())
        self.assertFalse(timer.check_finished())
        self.assertEqual(timer.remaining(),0)
        self.assertEqual(timer.state,"finished")

    def test_stop_reset_and_validity(self):
        clock=FakeClock()
        timer=Countdown(20,clock=clock)
        timer.start()
        clock.advance(8)
        timer.stop()
        self.assertEqual(timer.remaining(),20)
        self.assertEqual(timer.state,"stopped")
        self.assertFalse(timer.check_finished())
        for invalid in (0,-1,MAX_TIMER_SECONDS+1,1.5,True):
            with self.assertRaises(ValueError):
                timer.set_duration(invalid)


class AlarmSettingsTests(unittest.TestCase):
    def test_generated_pcm_has_requested_volume(self):
        silent=alarm_wave(850,.1,0)
        loud=alarm_wave(850,.1,90)
        with wave.open(io.BytesIO(silent),"rb") as sound:
            self.assertEqual(sound.getnchannels(),1)
            self.assertEqual(sound.getframerate(),22050)
            self.assertFalse(any(sound.readframes(9999)))
        with wave.open(io.BytesIO(loud),"rb") as sound:
            self.assertTrue(any(sound.readframes(9999)))

    def test_each_sound_offline_and_settings_survive_restart(self):
        self.assertGreaterEqual(len(ALARM_PATTERNS),3)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"settings.json"
            original=load_settings(path)
            original.update(timer_sound="Triplo impulso",timer_volume=35,
                            timer_repeat=True,auto_listen=True,
                            telegram_enabled=False)
            save_settings(original,path)
            restored=load_settings(path)
            self.assertEqual(restored["timer_sound"],"Triplo impulso")
            self.assertEqual(restored["timer_volume"],35)
            self.assertTrue(restored["timer_repeat"])
            self.assertTrue(restored["auto_listen"])
            self.assertEqual(restored["telegram_contacts"],[])

    def test_invalid_alarm_settings_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"settings.json"
            settings=load_settings(path)
            settings["timer_volume"]="full"
            with self.assertRaises(ValueError):
                save_settings(settings,path)
            self.assertFalse(path.exists())
        player=AlarmPlayer()
        with self.assertRaises(ValueError):
            player.play("malicious.wav",50)


class JarvisTimerIntegrationTests(unittest.TestCase):
    def test_routes_voice_modes_and_typed_buttons_before_external_gpt(self):
        source=(Path(__file__).resolve().parent.parent/"jarvis.py").read_text(
            encoding="utf-8")
        self.assertEqual(source.count("if try_timer_command(spoken):"),2)
        self.assertIn("if try_timer_command(message):",source)
        self.assertIn("timer_popup=TimerPopup(root,alarm_player",source)
        self.assertIn("timer_popup.close()",source)
        self.assertIn("settings_targets.update({",source)
        self.assertIn('"timer":timer_settings',source)
        self.assertIn('"telegram":telegram_panel',source)
        self.assertIn('"addons":addon_panel',source)
        self.assertIn("timer_preview.configure(command=",source)
        self.assertIn("timer_sound_picker.bind",source)


if __name__=="__main__":
    unittest.main()
