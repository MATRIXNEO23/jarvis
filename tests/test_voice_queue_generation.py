"""JRV-AUD-007 regression: actual producer, queue and dispatch loop.

Audio worker startup and action/model boundaries are controlled. No microphone,
Vosk model, GPT account or desktop action is used.
"""
from __future__ import annotations

import ast
import copy
import json
import os
from pathlib import Path
import queue
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import test_voice_corrections_review as voice_fixture
from voice_control import VoiceController, STANDBY, PUSH_TO_TALK, CONTINUOUS, GPT_CONVERSATION


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class VoiceQueueGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        voice_fixture.VoiceCorrectionReviewTests.setUpClass()

    def setUp(self):
        self.fixture = voice_fixture.VoiceCorrectionReviewTests()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.setUp()
        self.env = self.fixture.env
        self.events = queue.Queue()
        self.control = VoiceController(
            self.events.put, Path(self.fixture.temp.name) / "unused-audio-model")
        self.addCleanup(self.control.close)
        self.enterContext(patch.object(self.control, "_start_continuous", return_value=None))
        self.env.update(
            queue=queue, output_queue=self.events, voice=self.control,
            conversation_epoch=7, pending_conversation=[], PUSH_TO_TALK=PUSH_TO_TALK,
            CYAN="#00ffff", choose_save_button=Mock(), hud_mic_button=Mock(),
            dictation_button=Mock(), ptt_button=Mock(), spoken_enabled=voice_fixture.Value(True),
            save_speech_preferences=Mock(), sync_dictation_ui=Mock(),
            mic_status=voice_fixture.Value(""), runtime_events=Mock(), closing=False,
            refresh_buttons=Mock(),
        )
        self.mode_callback = self.fixture.callback("change_voice_mode")
        self.drain = self.make_dispatch_consumer()

    def make_dispatch_consumer(self):
        # Keep the REAL dequeue and complete dispatch chain, including any
        # guards inside the event loop. Omit unrelated scheduling/diagnostics.
        poll = copy.deepcopy(self.fixture.poll)
        loop = next(n for n in ast.walk(poll) if isinstance(n, ast.For)
                    and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                            and c.func.attr == "get_nowait" for c in ast.walk(n)))
        declarations = [n for n in poll.body if isinstance(n, (ast.Nonlocal, ast.Global))]
        poll.name = "drain_voice_verification_queue"
        poll.body = declarations + [ast.Try(
            body=[loop], handlers=[ast.ExceptHandler(
                type=ast.Attribute(value=ast.Name(id="queue", ctx=ast.Load()),
                                   attr="Empty", ctx=ast.Load()),
                name=None, body=[ast.Pass()])], orelse=[], finalbody=[])]
        poll = voice_fixture.GlobalCallbacks().visit(poll)
        module = ast.fix_missing_locations(ast.Module(body=[poll], type_ignores=[]))
        exec(compile(module, "actual-voice-event-dequeue-and-dispatch", "exec"), self.env)
        return self.env[poll.name]

    def configure(self, mode):
        self.fixture.voice_environment(mode)
        self.env["doc_dialog"].revoke_pending = Mock()
        self.mode_callback()
        self.clear_observations()

    def switch(self, mode):
        self.env["voice_mode"].set(mode)
        self.mode_callback()

    def off_on(self, mode):
        self.switch(STANDBY)
        self.switch(mode)
        self.clear_observations()

    def clear_observations(self):
        for name in ("submit_local", "start_conversation_gpt", "try_file_command",
                     "try_timer_command", "try_self_diagnostic", "try_telegram_voice_send",
                     "write_line"):
            self.env[name].reset_mock()
        self.env["runtime_events"].reset_mock()

    def report(self, kind, value):
        generation = self.control._generation
        self.control._report(kind, value, generation)
        self.assertEqual(self.events.qsize(), 1)
        return generation

    def trace(self, case, old):
        result = dict(case=case, producer_generation=old,
                      consumer_generation=self.control._generation,
                      current_mode=self.env["voice_mode"].get(),
                      local_dispatches=self.env["submit_local"].call_count,
                      model_starts=self.env["start_conversation_gpt"].call_count,
                      file_dispatch_attempts=self.env["try_file_command"].call_count,
                      mic_status=self.env["mic_status"].get())
        print("VOICE_QUEUE_GENERATION_PROBE=" + json.dumps(result, ensure_ascii=True))

    def test_old_local_command_is_ignored_after_off_on(self):
        for mode in (GPT_CONVERSATION, CONTINUOUS, PUSH_TO_TALK):
            with self.subTest(mode=mode):
                self.configure(mode)
                old = self.report("voice_text", "Lumi apri browser")
                sample_before = self.env["last_voice_sample"].get()
                self.off_on(mode)
                self.assertFalse(self.control._is_current(old))
                self.drain()
                self.trace("old_local_off_on", old)
                self.env["submit_local"].assert_not_called()
                self.env["start_conversation_gpt"].assert_not_called()
                self.assertEqual(self.env["last_voice_sample"].get(), sample_before)

    def test_old_model_request_is_ignored_after_off_on(self):
        for mode in (GPT_CONVERSATION, CONTINUOUS):
            with self.subTest(mode=mode):
                self.configure(mode)
                old = self.report("voice_text", "Lumi spiegami la gravita")
                self.off_on(mode)
                self.drain()
                self.trace("old_model_off_on", old)
                self.env["start_conversation_gpt"].assert_not_called()
                self.env["try_file_command"].assert_not_called()

    def test_old_background_phrase_cannot_be_reinterpreted_after_mode_change(self):
        self.configure(GPT_CONVERSATION)
        # The same room phrase is ignored if consumed in its original mode.
        self.report("voice_text", "apri browser")
        self.drain()
        self.env["submit_local"].assert_not_called()
        self.env["start_conversation_gpt"].assert_not_called()
        old = self.report("voice_text", "apri browser")  # no hotword in original mode
        self.switch(CONTINUOUS)
        self.clear_observations()
        self.drain()
        self.trace("background_gpt_to_continuous", old)
        self.env["submit_local"].assert_not_called()
        self.env["start_conversation_gpt"].assert_not_called()

    def test_old_status_does_not_replace_new_session_status(self):
        for mode in (GPT_CONVERSATION, CONTINUOUS, PUSH_TO_TALK):
            with self.subTest(mode=mode):
                self.configure(mode)
                old = self.report("voice_status", "Voce non disponibile: errore della sessione precedente")
                self.off_on(mode)
                current_status = self.env["mic_status"].get()
                self.drain()
                self.trace("old_status_off_on", old)
                self.assertEqual(self.env["mic_status"].get(), current_status)

    def test_standby_without_reactivation_blocks_queued_command(self):
        self.configure(GPT_CONVERSATION)
        old = self.report("voice_text", "Lumi apri browser")
        self.switch(STANDBY)
        self.clear_observations()
        self.drain()
        self.trace("stay_off_control", old)
        self.env["submit_local"].assert_not_called()
        self.env["start_conversation_gpt"].assert_not_called()

    def test_current_event_dispatches_and_old_generation_cannot_enqueue(self):
        for mode in (GPT_CONVERSATION, CONTINUOUS, PUSH_TO_TALK):
            with self.subTest(mode=mode):
                self.configure(mode)
                old = self.control._generation
                self.off_on(mode)
                self.control._report("voice_text", "Lumi apri browser", old)
                self.assertTrue(self.events.empty())
                current = self.report("voice_text", "Lumi apri browser")
                self.drain()
                self.trace("fresh_control", current)
                self.env["submit_local"].assert_called_once()
                self.assertEqual(self.env["submit_local"].call_args.kwargs["message_override"],
                                 "apri browser")
                self.env["start_conversation_gpt"].assert_not_called()

    def test_current_model_request_dispatches_once(self):
        for mode in (GPT_CONVERSATION, CONTINUOUS):
            with self.subTest(mode=mode):
                self.configure(mode)
                current = self.report("voice_text", "Lumi spiegami la gravita")
                self.drain()
                self.trace("fresh_model_control", current)
                self.env["start_conversation_gpt"].assert_called_once_with(
                    "spiegami la gravita")
                self.env["submit_local"].assert_not_called()

    def test_stale_events_have_no_ui_memory_or_dictation_effects(self):
        for kind, value in (("voice_text", "Lumi apri browser"),
                            ("voice_status", "Voce non disponibile: errore vecchio")):
            with self.subTest(kind=kind):
                self.configure(CONTINUOUS)
                self.report(kind, value)
                self.off_on(CONTINUOUS)
                disable = Mock(return_value="dettatura disabilitata")
                self.env["dictation"] = SimpleNamespace(enabled=True, disable=disable)
                sample = self.env["last_voice_sample"].get()
                status = self.env["mic_status"].get()
                self.env["sync_dictation_ui"].reset_mock()
                self.drain()
                self.env["write_line"].assert_not_called()
                self.assertEqual(self.env["last_voice_sample"].get(), sample)
                self.assertEqual(self.env["mic_status"].get(), status)
                self.env["runtime_events"].record.assert_not_called()
                self.env["sync_dictation_ui"].assert_not_called()
                disable.assert_not_called()
                self.env["submit_local"].assert_not_called()
                self.env["start_conversation_gpt"].assert_not_called()

    def test_stale_then_fresh_event_keeps_current_command(self):
        self.configure(GPT_CONVERSATION)
        self.report("voice_text", "Lumi spiegami la gravita")
        self.off_on(GPT_CONVERSATION)
        self.control._report("voice_text", "Lumi apri browser", self.control._generation)
        self.drain()
        self.env["submit_local"].assert_called_once_with(
            message_override="apri browser", source_utterance="apri browser")
        self.env["start_conversation_gpt"].assert_not_called()
        self.env["write_line"].assert_called_once_with("TU > apri browser")

    def test_nonvoice_result_between_stale_and_fresh_voice_is_preserved(self):
        self.configure(GPT_CONVERSATION)
        self.env.update(spoken_status=voice_fixture.Value(""), refresh_voices_button=Mock())
        self.report("voice_text", "Lumi spiegami la gravita")
        self.off_on(GPT_CONVERSATION)
        self.events.put(("tts_error", "Errore TTS controllato"))
        self.control._report("voice_text", "Lumi apri browser", self.control._generation)
        self.drain()
        self.assertIn("Errore TTS controllato", self.env["spoken_status"].get())
        self.env["refresh_voices_button"].configure.assert_called_once_with(state="normal")
        self.env["submit_local"].assert_called_once()
        self.env["start_conversation_gpt"].assert_not_called()

    def test_invalid_voice_payloads_do_not_dispatch_or_block_next_event(self):
        # True/1.0 compare equal to integer1: they are not session identities.
        payloads = [
            lambda g: ("voice_text", "Lumi spiegami la gravita", True),
            lambda g: ("voice_text", "Lumi spiegami la gravita", float(g)),
            lambda g: ("voice_text", "Lumi spiegami la gravita", str(g)),
            lambda g: ("voice_text", "Lumi spiegami la gravita", None),
            lambda g: ("voice_text", "Lumi spiegami la gravita"),
            lambda g: ("voice_text",),
            lambda g: ("voice_text", "Lumi spiegami la gravita", g, "extra"),
            lambda g: ("voice_text", None, g),
            lambda g: ("voice_status", "Voce non disponibile: payload senza sessione"),
            lambda g: ("voice_status",),
            lambda g: ("voice_status", "Voce non disponibile: payload errato", str(g)),
        ]
        for index, payload in enumerate(payloads):
            # A failing Red subcase must not leave its following event in the
            # queue and contaminate the next independent payload scenario.
            while not self.events.empty():
                self.events.get_nowait()
            with self.subTest(payload=index):
                self.configure(GPT_CONVERSATION)
                status = self.env["mic_status"].get()
                self.events.put(payload(self.control._generation))
                self.control._report("voice_text", "Lumi apri browser", self.control._generation)
                try:
                    self.drain()
                except (IndexError, ValueError, TypeError) as exc:
                    self.fail("Malformed voice payload stopped the real dispatch loop: "
                              + type(exc).__name__)
                self.env["submit_local"].assert_called_once()
                self.env["start_conversation_gpt"].assert_not_called()
                self.env["write_line"].assert_called_once_with("TU > apri browser")
                self.env["runtime_events"].record.assert_not_called()
                self.assertEqual(self.env["mic_status"].get(), status)
                self.assertTrue(self.events.empty())

    def test_close_revokes_already_queued_voice(self):
        self.configure(GPT_CONVERSATION)
        self.report("voice_text", "Lumi apri browser")
        self.control.close()
        self.drain()
        self.env["submit_local"].assert_not_called()
        self.env["start_conversation_gpt"].assert_not_called()
        self.env["write_line"].assert_not_called()

    def test_current_status_is_displayed_in_each_listening_mode(self):
        for mode in (GPT_CONVERSATION, CONTINUOUS, PUSH_TO_TALK):
            with self.subTest(mode=mode):
                self.configure(mode)
                self.report("voice_status", "Microfono attivo — riconoscimento offline.")
                self.drain()
                self.assertEqual(self.env["mic_status"].get(),
                                 "Microfono attivo — riconoscimento offline.")

    def test_current_audio_error_keeps_feedback_and_stops_current_dictation(self):
        self.configure(CONTINUOUS)
        disable = Mock(return_value="Dettatura interrotta per errore audio.")
        self.env["dictation"] = SimpleNamespace(enabled=True, disable=disable)
        self.env["sync_dictation_ui"].reset_mock()
        error = "Voce non disponibile: errore audio corrente"
        self.report("voice_status", error)
        self.drain()
        self.assertEqual(self.env["mic_status"].get(), error)
        self.env["write_line"].assert_called_once_with("MICROFONO > " + error)
        self.env["runtime_events"].record.assert_called_once_with("voice_unavailable")
        disable.assert_called_once_with()
        self.env["sync_dictation_ui"].assert_called_once_with(
            "Dettatura interrotta per errore audio.")

