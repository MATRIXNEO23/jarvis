"""Gemma prose must reach chat; malformed action payloads never execute."""
import os
import unittest
from unittest.mock import Mock
import test_native_project_history as fixture
from local_model.native_conversation_session import NativeChatTurn

@unittest.skipUnless(os.name == 'nt', 'Windows-only project requirement')
class NativePlainReplyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture.NativeProjectHistoryTests.setUpClass()

    def environment(self):
        harness = fixture.NativeProjectHistoryTests()
        self.addCleanup(harness.doCleanups)
        harness.setUp()
        env = harness.env
        env['dispatch_model_capability'] = Mock()
        return harness, env

    def deliver(self, harness, env, text, kind='voice_ok'):
        turn = NativeChatTurn(harness.session, None, 'Rispondimi al contesto', text, 0)
        turn.allowed_actions = frozenset({'browser.open'})
        env['gemma_trial_queue'].put((kind, turn, env['conversation_epoch']))
        env['poll_gemma_trial']()
        return turn

    def test_plain_conversation_is_displayed_spoken_and_committed(self):
        for channel in ('ok', 'voice_ok'):
            with self.subTest(channel=channel):
                harness, env = self.environment()
                text = 'Stavamo parlando di Mussolini. Quale aspetto vuoi approfondire?'
                turn = self.deliver(harness, env, text, channel)
                env['write_line'].assert_called_with('GEMMA > ' + text)
                env['speak_result'].assert_called_once_with(text)
                self.assertEqual(list(harness.session.history), [
                    ('user', 'Rispondimi al contesto'), ('assistant', text)])
                self.assertFalse(turn.commit())
                env['dispatch_model_capability'].assert_not_called()

    def test_structured_chat_keeps_existing_validation(self):
        harness, env = self.environment()
        self.deliver(harness, env, '{"kind":"chat","reply":"Parliamo del contesto."}')
        env['write_line'].assert_called_with('GEMMA > Parliamo del contesto.')
        self.assertEqual(list(harness.session.history)[-1], ('assistant','Parliamo del contesto.'))
        env['dispatch_model_capability'].assert_not_called()

    def test_malformed_action_is_not_downgraded_to_prose_or_remembered(self):
        for raw in ('{"kind":"capability","action_id":"browser.open","arguments":',
                    'Proposta: {"kind":"capability","action_id":"browser.open","arguments":{}}',
                    '```json\n{"kind":"capability"\n```'):
            with self.subTest(raw=raw):
                harness, env = self.environment()
                self.deliver(harness, env, raw)
                self.assertEqual(list(harness.session.history), [])
                env['dispatch_model_capability'].assert_not_called()
                message = env['write_line'].call_args.args[0]
                self.assertIn('Gemma', message)
                self.assertNotIn('GPT', message)

    def test_invalid_structured_schema_is_still_rejected(self):
        harness, env = self.environment()
        self.deliver(harness, env, '{"kind":"chat","reply":"Ciao","action_id":"browser.open"}')
        self.assertEqual(list(harness.session.history), [])
        env['dispatch_model_capability'].assert_not_called()
