"""Voice safety checks: no live microphone or model required."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from desktop_dictation import DesktopDictation, FocusedWindow, dictation_voice_action
from voice_control import (
    CONTINUOUS, PUSH_TO_TALK, STANDBY, GPT_CONVERSATION, VoiceController,
    speech_to_local_command, WakeWordGate,
)


class SpeechRoutingTests(unittest.TestCase):
    def test_allowlisted_command(self):
        self.assertEqual(speech_to_local_command("Jarvis apri la calcolatrice"),
                         "apri calcolatrice")
        self.assertEqual(speech_to_local_command("controlla la RAM"),
                         "stato sistema")
        self.assertEqual(speech_to_local_command("Ehi Jarvis apri disco locale C"),
                         "apri disco locale c")

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


class WakeWordTests(unittest.TestCase):
    def test_command_requires_name_in_continuous_mode(self):
        now = [100.0]
        gate = WakeWordGate(clock=lambda: now[0])
        self.assertEqual(gate.route("apri blocco note"), ("ignored", ""))
        self.assertEqual(gate.route("Ehi Jarvis apri blocco note"),
                         ("command", "apri blocco note"))
        self.assertEqual(gate.route("Ehi Jarvis, apri il browser"),
                         ("command", "apri il browser"))
        self.assertEqual(gate.route("apri la calcolatrice"), ("ignored", ""))
        self.assertEqual(gate.route("Ehi Jarvis"), ("wake", ""))
        now[0] += 4
        self.assertEqual(gate.route("Apri il browser"),
                         ("command", "apri il browser"))
        self.assertEqual(gate.route("apri il browser"), ("ignored", ""))

    def test_dictation_toggle_is_voice_command_with_wake_name(self):
        gate = WakeWordGate(clock=lambda: 42.0)
        window = FocusedWindow(21, 22, 200)
        writes = []
        editor = DesktopDictation(
            app_pid=100, windows=True,
            focus_provider=lambda: window, sender=writes.append,
        )
        # The listener does not execute free-standing requests in continuous.
        self.assertEqual(gate.route("attiva dettatura"), ("ignored", ""))
        # An explicit wake phrase can activate dictation without clicking Jarvis.
        kind, phrase = gate.route("Ehi Jarvis, attiva dettatura")
        self.assertEqual((kind, dictation_voice_action(phrase)), ("command", "start"))
        editor.enable()
        kind, phrase = gate.route("questa frase va scritta",
                                  dictation_active=editor.enabled)
        self.assertEqual(kind, "dictation")
        editor.insert(phrase)
        self.assertEqual(writes, ["questa frase va scritta "])
        # While dictation is active the stop phrase must NOT become text.
        kind, phrase = gate.route("Ehi Jarvis disattiva dettatura",
                                  dictation_active=editor.enabled)
        self.assertEqual((kind, dictation_voice_action(phrase)), ("command", "stop"))
        editor.disable()
        self.assertEqual(writes, ["questa frase va scritta "])
        # The wake word can also be spoken as a separate utterance.
        self.assertEqual(gate.route("Ehi Jarvis"), ("wake", ""))
        kind, phrase = gate.route("attiva dettatura")
        self.assertEqual((kind, dictation_voice_action(phrase)), ("command", "start"))

    def test_wake_expires_without_switching_microphone_mode(self):
        now = [100.0]
        gate = WakeWordGate(timeout=10, clock=lambda: now[0])
        gate.route("Jarvis")
        now[0] += 11
        self.assertEqual(gate.route("apri blocco note"), ("ignored", ""))

    def test_dictation_treats_uncued_speech_as_text(self):
        gate = WakeWordGate()
        self.assertEqual(gate.route("una frase libera", dictation_active=True),
                         ("dictation", "una frase libera"))
        self.assertEqual(gate.route("ehi Jarvis disattiva dettatura",
                                    dictation_active=True),
                         ("command", "disattiva dettatura"))
        gate.route("ehi jarvis")
        self.assertEqual(gate.route("disattiva dettatura",
                                    dictation_active=True),
                         ("command", "disattiva dettatura"))


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

    def test_gpt_conversation_mode_requires_manual_selection(self):
        with TemporaryDirectory() as folder:
            events = []
            control = VoiceController(events.append, Path(folder) / "no-model")
            self.assertEqual(control.mode, STANDBY)
            self.assertFalse(control.press())
            control.set_mode(GPT_CONVERSATION)
            self.assertEqual(control.mode, GPT_CONVERSATION)
            # Missing model may stop the audio stream, never flip the chosen
            # mode to standby and never start an unrequested paid service.
            worker = control._worker
            if worker is not None:
                worker.join(timeout=3)
            self.assertEqual(control.mode, GPT_CONVERSATION)
            control.close()
            self.assertEqual(control.mode, STANDBY)

    def test_reject_unknown_mode(self):
        control = VoiceController(lambda event: None)
        with self.assertRaises(ValueError):
            control.set_mode("auto")
        self.assertEqual(control.mode, STANDBY)


if __name__ == "__main__":
    unittest.main()
