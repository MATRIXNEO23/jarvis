"""Voice safety checks: no live microphone or model required."""
import unittest
import os
import threading
from pathlib import Path
from unittest.mock import patch
from tempfile import TemporaryDirectory

from desktop_dictation import DesktopDictation, FocusedWindow, dictation_voice_action
from voice_control import (
    CONTINUOUS, PUSH_TO_TALK, STANDBY, GPT_CONVERSATION, VoiceController,
    speech_to_local_command, WakeWordGate,
)


class SpeechRoutingTests(unittest.TestCase):
    def test_allowlisted_command(self):
        self.assertEqual(speech_to_local_command("Lumi apri la calcolatrice"),
                         "apri calcolatrice")
        self.assertEqual(speech_to_local_command("controlla la RAM"),
                         "stato sistema")
        self.assertEqual(speech_to_local_command("Ehi Lumi apri disco locale C"),
                         "apri disco locale c")

    def test_browser_commands(self):
        self.assertEqual(speech_to_local_command("Lumi, apri il browser"), "apri browser")
        self.assertEqual(speech_to_local_command("apri browser"), "apri browser")
        self.assertEqual(
            speech_to_local_command("Lumi cerca nel browser monumenti di Roma"),
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
        self.assertEqual(gate.route("Ehi Lumi apri blocco note"),
                         ("command", "apri blocco note"))
        self.assertEqual(gate.route("Ehi Lumi, apri il browser"),
                         ("command", "apri il browser"))
        self.assertEqual(gate.route("apri la calcolatrice"), ("ignored", ""))
        self.assertEqual(gate.route("Ehi Lumi"), ("wake", ""))
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
        kind, phrase = gate.route("Ehi Lumi, attiva dettatura")
        self.assertEqual((kind, dictation_voice_action(phrase)), ("command", "start"))
        editor.enable()
        kind, phrase = gate.route("questa frase va scritta",
                                  dictation_active=editor.enabled)
        self.assertEqual(kind, "dictation")
        editor.insert(phrase)
        self.assertEqual(writes, ["questa frase va scritta "])
        # While dictation is active the stop phrase must NOT become text.
        kind, phrase = gate.route("Ehi Lumi disattiva dettatura",
                                  dictation_active=editor.enabled)
        self.assertEqual((kind, dictation_voice_action(phrase)), ("command", "stop"))
        editor.disable()
        self.assertEqual(writes, ["questa frase va scritta "])
        # The wake word can also be spoken as a separate utterance.
        self.assertEqual(gate.route("Ehi Lumi"), ("wake", ""))
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
        self.assertEqual(gate.route("ehi Lumi disattiva dettatura",
                                    dictation_active=True),
                         ("command", "disattiva dettatura"))
        gate.route("ehi lumi")
        self.assertEqual(gate.route("disattiva dettatura",
                                    dictation_active=True),
                         ("command", "disattiva dettatura"))


class VoiceModelTrialPathTests(unittest.TestCase):
    def test_trial_reuses_existing_original_vosk_model_without_copying(self):
        from voice_control import model_directory, MODEL_NAME
        with TemporaryDirectory() as directory:
            base=Path(directory)
            original=base/"Jarvis"/"models"/MODEL_NAME
            original.mkdir(parents=True)
            trial=base/"Jarvis-Telegram50-Trial"
            trial.mkdir()
            with patch.dict(os.environ,{"LOCALAPPDATA":str(base),
                                         "JARVIS_TRIAL_HOME":str(trial)}):
                self.assertEqual(model_directory(),original)
                self.assertFalse((trial/"models"/MODEL_NAME).exists())

    def test_trial_reuses_model_from_launcher_source(self):
        from voice_control import model_directory, MODEL_NAME
        with TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "Jarvis-Telegram50-Trial"
            model = source / "models" / MODEL_NAME
            model.mkdir(parents=True)
            with patch.dict(os.environ, {
                "LOCALAPPDATA": str(base),
                "JARVIS_TRIAL_HOME": str(base / "Jarvis-Gemma-Trial"),
                "JARVIS_TRIAL_SOURCE": str(source),
            }):
                self.assertEqual(model_directory(), model)

    def test_trial_prefers_its_own_model_if_present(self):
        from voice_control import model_directory, MODEL_NAME
        with TemporaryDirectory() as directory:
            base=Path(directory)
            trial=base/"Jarvis-Telegram50-Trial"
            personal=trial/"models"/MODEL_NAME
            personal.mkdir(parents=True)
            with patch.dict(os.environ,{"LOCALAPPDATA":str(base),
                                         "JARVIS_TRIAL_HOME":str(trial)}):
                self.assertEqual(model_directory(),personal)


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

    def test_missing_model_leaves_the_error_as_last_status(self):
        with TemporaryDirectory() as folder:
            events = []
            control = VoiceController(events.append, Path(folder) / "no-model")
            control.mode = CONTINUOUS
            control._listen(threading.Event(), 0)
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0][0], "voice_status")
            self.assertIn("Modello italiano mancante", events[0][1])

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

    def test_hud_listening_requires_real_current_microphone_stream(self):
        # Selecting an always-listening mode is not enough to show orange
        # when microphone initialization failed or is still loading.
        with TemporaryDirectory() as folder:
            control = VoiceController(lambda event: None,
                                      Path(folder) / "nonexistent")
            self.assertFalse(control.is_listening())
            with control._lock:
                control.mode = CONTINUOUS
                control._generation = 8
                control._active_generation = 7
            self.assertFalse(control.is_listening())
            with control._lock:
                control._active_generation = 8
            self.assertTrue(control.is_listening())
            control.close()
            self.assertFalse(control.is_listening())
            self.assertEqual(control.mode, STANDBY)

    def test_reject_unknown_mode(self):
        control = VoiceController(lambda event: None)
        with self.assertRaises(ValueError):
            control.set_mode("auto")
        self.assertEqual(control.mode, STANDBY)


if __name__ == "__main__":
    unittest.main()


class ShortWakeWindowTests(unittest.TestCase):
    def test_bare_name_waits_for_next_phrase_in_name_required_modes(self):
        now = [100.0]
        gate = WakeWordGate(clock=lambda: now[0])
        self.assertEqual(gate.route("Lumi", require_name=True), ("wake", ""))
        now[0] += 3.0                                    # pausa di 3 secondi
        self.assertEqual(gate.route("apri il browser", require_name=True),
                         ("command", "apri il browser"))
        self.assertEqual(gate.route("e poi un'altra frase", require_name=True), ("ignored", ""))
        gate.route("Lumi", require_name=True)
        now[0] += 7.0                                    # troppo tardi: la stanza resta ignorata
        self.assertEqual(gate.route("apri il browser", require_name=True), ("ignored", ""))
        self.assertEqual(gate.route("Lumi apri il browser", require_name=True),
                         ("command", "apri il browser"))
