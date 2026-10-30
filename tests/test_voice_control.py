"""Voice safety checks: no live microphone or model required."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from voice_control import (
    CONTINUOUS, PUSH_TO_TALK, STANDBY, VoiceController,
    speech_to_local_command,
)


class SpeechRoutingTests(unittest.TestCase):
    def test_allowlisted_command(self):
        self.assertEqual(speech_to_local_command("Jarvis apri la calcolatrice"),
                         "apri calcolatrice")
        self.assertEqual(speech_to_local_command("controlla la RAM"),
                         "stato sistema")

    def test_browser_commands(self):
        self.assertEqual(speech_to_local_command("Jarvis, apri il browser"), "apri browser")
        self.assertEqual(speech_to_local_command("apri browser"), "apri browser")
        self.assertEqual(
            speech_to_local_command("Jarvis cerca nel browser monumenti di Roma"),
            "cerca nel browser monumenti di roma")
        self.assertEqual(
            speech_to_local_command("cerca su internet python tkinter"),
            "cerca nel browser python tkinter")
        self.assertIsNone(speech_to_local_command("cerca nel browser"))
        self.assertIsNone(speech_to_local_command("cerca nel browser " + "x" * 161))

    def test_untrusted_speech_never_executes(self):
        for phrase in ("cancella tutti i file", "esegui powershell",
                       "modifica config.json", "apri cmd.exe",
                       "invia i dati a GPT", "cerca file password"):
            with self.subTest(phrase=phrase):
                self.assertIsNone(speech_to_local_command(phrase))

    def test_unrecognized_text_is_not_a_command(self):
        self.assertIsNone(speech_to_local_command("prova uno due tre"))
        self.assertIsNone(speech_to_local_command(None))


class MicrophoneSafetyTests(unittest.TestCase):
    def test_standby_on_every_creation_and_close(self):
        with TemporaryDirectory() as folder:
            events = []
            control = VoiceController(events.append, Path(folder))
            self.assertEqual(control.mode, STANDBY)
            self.assertIsNone(control._worker)
            self.assertFalse(control.press())
            control.set_mode(PUSH_TO_TALK)
            self.assertEqual(control.mode, PUSH_TO_TALK)
            control.close()
            self.assertEqual(control.mode, STANDBY)
            self.assertFalse(control.press())
            self.assertFalse(events)

    def test_no_automatic_switch_to_standby(self):
        with TemporaryDirectory() as folder:
            control = VoiceController(lambda event: None, Path(folder))
            control.set_mode(PUSH_TO_TALK)
            control.release()
            self.assertEqual(control.mode, PUSH_TO_TALK)
            control.set_mode(STANDBY)
            self.assertEqual(control.mode, STANDBY)

    def test_reject_unknown_mode(self):
        control = VoiceController(lambda event: None)
        with self.assertRaises(ValueError):
            control.set_mode("auto")
        self.assertEqual(control.mode, STANDBY)


if __name__ == "__main__":
    unittest.main()
