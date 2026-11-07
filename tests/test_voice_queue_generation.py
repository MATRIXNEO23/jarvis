"""JRV-AUD-007 verification only: actual producer, queue and dispatch loop.

Audio worker startup and action/model boundaries are controlled. No runtime
patch, microphone, Vosk model, GPT account or desktop action is used.
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
                old = self.report("voice_text", "Jarvis apri browser")
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
                old = self.report("voice_text", "Jarvis spiegami la gravita")
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
        old = self.report("voice_text", "Jarvis apri browser")
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
                self.control._report("voice_text", "Jarvis apri browser", old)
                self.assertTrue(self.events.empty())
                current = self.report("voice_text", "Jarvis apri browser")
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
                current = self.report("voice_text", "Jarvis spiegami la gravita")
                self.drain()
                self.trace("fresh_model_control", current)
                self.env["start_conversation_gpt"].assert_called_once_with(
                    "spiegami la gravita")
                self.env["submit_local"].assert_not_called()

