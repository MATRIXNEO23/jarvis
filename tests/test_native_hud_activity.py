"""Actual native owner/HUD callbacks, controlled ABI, Windows only.

No real model, Telegram account or microphone. Every worker is gated, released
and joined by the existing ownership fixture, including on the Red revision.
"""
from local_model.native_bridge import NativeRestartRequired
import os
import gc
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import test_activity_status as callbacks
import test_native_cancellation as cancellation
import test_native_trial_ownership as ownership


@unittest.skipUnless(os.name == 'nt', 'Windows-only project requirement')
class NativeHudActivityTests(unittest.TestCase):
    worker = cancellation.NativeCancellationTests.worker

    def tearDown(self):
        gc.collect()

    def setUp(self):
        self.harness = ownership.NativeTrialOwnershipTests()
        self.addCleanup(self.harness.doCleanups)
        self.harness.setUp()
        self.session, self.abi = self.harness.session, self.harness.abi
        callbacks.ActivityStatusTests.setUpClass()
        self.callbacks = callbacks.ActivityStatusTests()
        self.addCleanup(self.callbacks.doCleanups)
        self.env, _, self.provider = self.callbacks.environment(permissions=False)
        self.env['gemma_session'][0] = self.session
        self.env['gpt_enabled'].set(False)

    def snapshot(self, *, busy):
        # If a future property takes the inference lock, fail in a bounded
        # observer rather than hanging the UI/test behind native generate.
        observed = self.worker(lambda: (getattr(self.session, 'is_busy', None), self.provider()))
        self.assertTrue(observed.done.wait(1), 'HUD status waited for native inference')
        self.assertIsNone(observed.error)
        native, state = observed.value
        self.assertIs(native, busy, 'Session must publish a Boolean metadata snapshot')
        self.assertIs(state['thinking'], busy)
        self.assertIs(state['reasoning'], busy)
        return state

    def finish(self, job):
        self.abi.release.set()
        self.assertTrue(job.done.wait(2))
        self.assertIsNone(job.error)
        self.snapshot(busy=False)

    def active(self, request):
        job = self.worker(request)
        self.assertTrue(self.abi.first_started.wait(2))
        self.snapshot(busy=True)
        return job

    def test_idle_snapshot_does_not_prepare_or_call_native_backend(self):
        with (patch.object(self.session.adapter, 'prepare') as prepare,
              patch.object(self.session.adapter, 'call') as call,
              patch.object(self.session, 'config_loader', side_effect=AssertionError('No settings I/O')) as config,
              patch.object(self.session, 'memory_loader', side_effect=AssertionError('No memory I/O')) as memory):
            for _ in range(5):
                self.snapshot(busy=False)
        prepare.assert_not_called()
        call.assert_not_called()
        config.assert_not_called()
        memory.assert_not_called()
        self.assertEqual(self.abi.loads, [])

    def test_chat_is_visible_with_gpt_disabled_and_returns_idle(self):
        job = self.active(lambda: self.session.ask('Ciao'))
        self.assertFalse(self.env['gemma_trial_busy'][0])
        self.finish(job)
        self.assertEqual(job.value, 'Risposta locale controllata')
        self.assertEqual(len(self.session.history), 2)

    def test_deferred_turn_is_busy_only_during_generation_not_until_commit(self):
        job = self.active(lambda: self.session.prepare_turn('Turno differito'))
        self.finish(job)
        self.assertEqual(list(self.session.history), [])
        self.assertTrue(job.value.commit())
        self.snapshot(busy=False)

    def test_actual_telegram_local_callback_updates_same_hud_owner(self):
        from telegram_bridge import telegram_assistant_prompt, telegram_local_prompt
        self.env.update(get_gemma_session=Mock(return_value=self.session),
                        ask_telegram_gpt=Mock(), telegram_assistant_prompt=telegram_assistant_prompt,
                        telegram_local_prompt=telegram_local_prompt, settings={"gpt_enabled": False})
        reply = self.callbacks.callback('ask_telegram_reply', self.env)
        bridge = SimpleNamespace(is_enabled=lambda: True)
        job = self.active(lambda: reply('Ciao', '', bridge, 123))
        self.finish(job)
        self.env['ask_telegram_gpt'].assert_not_called()
        self.assertEqual(job.value, 'Risposta locale controllata')
        self.assertEqual(list(self.session.history), [])

    def test_generated_settings_trial_is_visible_without_chat_busy_flag(self):
        panel = self.harness.window()
        panel.test_model()
        self.assertTrue(self.abi.first_started.wait(2))
        self.assertFalse(self.env['gemma_trial_busy'][0])
        self.snapshot(busy=True)
        self.harness.finish_workers()
        self.snapshot(busy=False)
        self.assertTrue(panel.status_value.startswith('TEST RIUSCITO'), panel.status_value)
        self.assertEqual(list(self.session.history), [])

    def test_program_suggestion_is_visible_and_keeps_chat_history_empty(self):
        job = self.active(lambda: self.session.pick_program('Video', ('Video',)))
        self.finish(job)
        self.assertEqual(list(self.session.history), [])

    def test_preparation_is_busy_before_the_first_native_generate(self):
        entered, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)
        def initialize(*args):
            entered.set()
            if not release.wait(3):
                raise RuntimeError('Fixture preparation release timed out')
            self.abi.initialize(*args)
        with patch('local_model.native_factory.initialize_kobold_cpu', side_effect=initialize):
            job = self.worker(lambda: self.session.ask('Prepara'))
            self.assertTrue(entered.wait(2))
            self.assertEqual(self.abi.calls, [])
            self.snapshot(busy=True)
            release.set()
            self.finish(job)

    def test_nested_ask_remains_busy_while_its_outer_commit_is_pending(self):
        from local_model.native_conversation_session import NativeChatTurn
        entered, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)
        original = NativeChatTurn.commit
        def commit(turn):
            entered.set()
            if not release.wait(3):
                raise RuntimeError('Fixture commit release timed out')
            return original(turn)
        self.abi.release.set()
        with patch.object(NativeChatTurn, 'commit', commit):
            job = self.worker(lambda: self.session.ask('Annidato'))
            self.assertTrue(entered.wait(2))
            self.assertEqual(self.abi.active, 0)
            self.snapshot(busy=True)
            release.set()
            self.assertTrue(job.done.wait(2))
        self.assertIsNone(job.error)
        self.snapshot(busy=False)

    def test_queued_request_is_visible_and_close_does_not_fake_its_exit(self):
        original = self.session.lock
        original.acquire()
        observed = cancellation.ObservedLock(original)
        self.session.lock = observed
        try:
            job = self.worker(lambda: self.session.ask('In coda'))
            self.assertTrue(observed.waiting.wait(2))
            self.snapshot(busy=True)
            self.assertEqual(self.abi.loads, [])
            self.session.close()
            self.snapshot(busy=True)
            self.assertFalse(job.done.is_set())
        finally:
            original.release()
        self.assertTrue(job.done.wait(2))
        self.assertIsInstance(job.error, RuntimeError)
        self.assertEqual(self.abi.calls, [])
        self.snapshot(busy=False)

    def test_ignored_abort_keeps_busy_until_real_generation_exits_after_timeout(self):
        aborted = threading.Event()
        with patch.object(self.abi, 'abort', side_effect=aborted.set):
            job = self.active(lambda: self.session.ask('Timeout', timeout=0.05))
            self.assertTrue(aborted.wait(1))
            self.assertFalse(job.done.is_set())
            self.snapshot(busy=True)
            self.abi.release.set()
            self.assertTrue(job.done.wait(2))
        self.assertIsInstance(job.error, TimeoutError)
        self.snapshot(busy=False)
        self.assertEqual(list(self.session.history), [])

    def test_normal_stop_unwinds_busy_and_next_request_can_recover(self):
        job = self.active(lambda: self.session.ask('Annulla'))
        stopped = self.worker(self.session.stop)
        self.assertTrue(stopped.done.wait(2))
        self.assertIsNone(stopped.error)
        self.assertTrue(job.done.wait(2))
        self.assertIsInstance(job.error, RuntimeError)
        self.snapshot(busy=False)
        # F5N.7: no in-process native reload after stop; busy still unwinds.
        with self.assertRaises(NativeRestartRequired):
            self.session.ask('Riprendi')
        self.snapshot(busy=False)

    def test_errors_and_closed_requests_do_not_leave_stale_busy_metadata(self):
        cases = (
            ('config_loader', ValueError('configuration')),
            ('_prepare', OSError('prepare')),
        )
        for name, error in cases:
            with self.subTest(phase=name), patch.object(self.session, name, side_effect=error):
                with self.assertRaises(type(error)):
                    self.session.ask('Errore')
                self.snapshot(busy=False)
        self.abi.release.set()
        for error in (RuntimeError('generate'), TimeoutError('timeout')):
            with self.subTest(error=type(error).__name__), patch.object(self.session.adapter, 'call', side_effect=error):
                with self.assertRaises(type(error)):
                    self.session.ask('Errore')
                self.snapshot(busy=False)
        with self.assertRaisesRegex(ValueError, 'build prompt'):
            self.session.ask_isolated(lambda _: (_ for _ in ()).throw(ValueError('build prompt')))
        self.snapshot(busy=False)
        self.session.close()
        with self.assertRaises(RuntimeError):
            self.session.ask('Dopo chiusura')
        self.snapshot(busy=False)

    def test_stop_with_ignored_abort_keeps_busy_until_native_really_exits(self):
        aborted = threading.Event()
        with patch.object(self.abi, 'abort', side_effect=aborted.set):
            job = self.active(lambda: self.session.ask('Stop non cooperativo'))
            stopped = self.worker(self.session.stop)
            self.assertTrue(aborted.wait(1))
            self.assertFalse(stopped.done.is_set())
            self.assertFalse(job.done.is_set())
            self.snapshot(busy=True)
            self.abi.release.set()
            self.assertTrue(job.done.wait(2))
            self.assertTrue(stopped.done.wait(2))
        self.assertIsInstance(job.error, RuntimeError)
        self.assertIsNone(stopped.error)
        self.snapshot(busy=False)
        # F5N.7: no in-process native reload after stop; busy still unwinds.
        with self.assertRaises(NativeRestartRequired):
            self.session.ask('Riprendi')
        self.snapshot(busy=False)

    def test_pending_chat_flag_and_existing_gpt_local_document_flags_are_preserved(self):
        self.env['gemma_session'][0] = None
        self.env['get_gemma_session'] = Mock(side_effect=AssertionError('HUD must not create a session'))
        self.env['gemma_trial_busy'][0] = True
        state = self.provider()
        self.assertTrue(state['thinking'])
        self.assertTrue(state['reasoning'])
        self.env['gemma_trial_busy'][0] = False
        self.env['gpt_enabled'].set(True)
        self.env.update(busy_gpt=True, gpt_request_action='typed_conversation')
        self.assertTrue(self.provider()['reasoning'])
        self.env['busy_gpt'] = False
        for flag in ('busy_local', 'document_busy'):
            self.env[flag] = True
            self.assertTrue(self.provider()['thinking'])
            self.env[flag] = False
        self.assertFalse(self.provider()['thinking'])
        self.env['get_gemma_session'].assert_not_called()

    def test_real_tk_status_shows_native_reasoning_and_keeps_voice_priority(self):
        import tkinter as tk
        from animated_hud import JarvisHUD
        job = self.worker(lambda: self.session.ask('Indicatore'))
        self.assertTrue(self.abi.first_started.wait(2))
        root = tk.Tk()
        root.withdraw()
        hud = JarvisHUD(root, lambda: None)
        hud.set_state_provider(self.provider)
        try:
            hud._advance()
            root.update_idletasks()
            self.assertIn('JARVIS STA RAGIONANDO', hud.chat_info.get())
            self.env['speaker'].is_speaking = lambda: True
            hud._advance()
            self.assertIn('JARVIS STA PARLANDO', hud.chat_info.get())
        finally:
            self.abi.release.set()
            finished = job.done.wait(2)
            try:
                hud.close()
            finally:
                root.destroy()
        self.assertTrue(finished)
        self.assertIsNone(job.error)
