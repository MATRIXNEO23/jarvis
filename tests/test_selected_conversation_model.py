"""Regression: GPT selection must reach online routing, not local inference."""
import ast
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


@unittest.skipUnless(os.name == 'nt', 'Windows-only project requirement')
class SelectedConversationModelTests(unittest.TestCase):
    def test_voice_gpt_selection_does_not_start_gemma(self):
        tree = ast.parse(Path('jarvis.py').read_text(encoding='utf-8'))
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
        callback = next(n for n in main.body if isinstance(n, ast.FunctionDef)
                        and n.name == 'start_conversation_gpt')
        gemma = Mock(return_value=True)
        online = Mock(return_value=True)
        env = dict(closing=False, voice_mode=SimpleNamespace(get=lambda: 'conversation'),
                   GPT_CONVERSATION='conversation', CONTINUOUS='continuous', PUSH_TO_TALK='premi_per_parlare',
                   gpt_spuntato=lambda: True, active_gpt=True,
                   busy_gpt=False, try_self_diagnostic=Mock(return_value=False),
                   submit_gemma_voice=gemma, run_gpt=online, offer_gpt=online,
                   documents=SimpleNamespace(current=None), conversation_epoch=7,
                   current_capability_snapshot=lambda _: {'telegram_voice_send': False},
                   build_conversation_prompt=__import__('conversation_router').build_conversation_prompt,
                   recent_memory_for_gpt=lambda _: '', capability_status_prompt=lambda _: '',
                   active_addon_actions=lambda: (), ConversationRejected=ValueError,
                   write_line=Mock(), speak_result=Mock())
        chain = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == 'conversation_chain')
        after = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == 'local_after_gpt')
        fast = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == 'fast_mode')
        env.update(settings={}, last_question=[''])        # 056: Basso consumo di serie
        exec(compile(ast.Module(body=[callback, chain, after, fast], type_ignores=[]), 'real-voice-router', 'exec'), env)
        with __import__('unittest').mock.patch('servizi_online.disponibili', return_value=False):
            env['start_conversation_gpt']('Parliamo della giornata')
        gemma.assert_called_once_with('Parliamo della giornata', typed=False, route='locale')   # 055: nessun «Uso GPT?»

    def test_conversation_consent_reused_but_other_functions_stay_separate(self):
        import test_activity_status as fixture
        fixture.ActivityStatusTests.setUpClass()
        harness = fixture.ActivityStatusTests()
        self.addCleanup(harness.doCleanups)
        env, workers, _ = harness.environment()
        env['gpt_conversation_session_grant'] = None
        run = harness.callback('run_gpt', env)
        for channel in ('typed_conversation', 'conversation'):
            self.assertTrue(run(channel, prompt='Dialogo', utterance='Ciao', epoch=7))
            workers.pop()()
            env['busy_gpt'] = False
        self.assertEqual(env['messagebox'].askyesno.call_count, 1)
        from local_model.online_permissions import OnlinePermissionPolicy, default_online_permissions_path
        policy = OnlinePermissionPolicy.load(default_online_permissions_path())
        policy.set_mode('chat.conversation', 'never')
        policy.save(default_online_permissions_path())
        self.assertFalse(run('conversation', prompt='Non inviare'))
        self.assertEqual(workers, [])

    def test_telegram_online_contact_does_not_use_local_model(self):
        import test_activity_status as fixture
        fixture.ActivityStatusTests.setUpClass()
        harness = fixture.ActivityStatusTests()
        self.addCleanup(harness.doCleanups)
        env, _, _ = harness.environment()
        env.update(get_gemma_session=Mock(), ask_telegram_gpt=Mock(),
                   telegram_assistant_prompt=lambda *a: 'prompt', settings={'telegram_online_contacts': [5]},
                   ask_telegram_online=Mock(return_value=''))
        reply = harness.callback('ask_telegram_reply', env)
        self.assertEqual(reply('Ciao', '', SimpleNamespace(is_enabled=lambda: True), 5), '')
        env['get_gemma_session'].assert_not_called()
        env['ask_telegram_online'].assert_called_once()

    def test_queued_ask_result_and_error_are_discarded_after_model_switch(self):
        import test_activity_status as fixture
        fixture.ActivityStatusTests.setUpClass()
        for failed in (False, True):
            with self.subTest(failed=failed):
                harness = fixture.ActivityStatusTests()
                self.addCleanup(harness.doCleanups)
                env, workers, _ = harness.environment()
                if failed:
                    env['service'].call.side_effect = RuntimeError('Vecchia richiesta')
                else:
                    env['service'].call.return_value = {'text': 'Vecchia risposta'}
                self.assertTrue(harness.callback('run_gpt', env)('ask', prompt='Testo lungo', source='Testo'))
                workers.pop()()
                env['conversation_epoch'] += 2  # GPT -> Gemma -> GPT
                env['active_gpt'] = False
                harness.receive('gpt_error' if failed else 'gpt_ok', env)
                env['speak_result'].assert_not_called()
                env['remember_exchange'].assert_not_called()
                self.assertFalse(env['active_gpt'])

    def test_push_to_talk_can_start_selected_gpt_conversation(self):
        tree = ast.parse(Path('jarvis.py').read_text(encoding='utf-8'))
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
        callback = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == 'start_conversation_gpt')
        env = dict(closing=False, voice_mode=SimpleNamespace(get=lambda: 'premi_per_parlare'),
                   GPT_CONVERSATION='conversation', CONTINUOUS='continuous', PUSH_TO_TALK='premi_per_parlare',
                   gpt_spuntato=lambda: True, active_gpt=False,
                   try_self_diagnostic=Mock(return_value=False), submit_gemma_voice=Mock(),
                   offer_gpt=Mock(), write_line=Mock(), speak_result=Mock())
        chain = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == 'conversation_chain')
        after = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == 'local_after_gpt')
        fast = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == 'fast_mode')
        env.update(settings={}, last_question=[''])        # 056: Basso consumo di serie
        exec(compile(ast.Module(body=[callback, chain, after, fast], type_ignores=[]), 'actual-ptt', 'exec'), env)
        with __import__('unittest').mock.patch('servizi_online.disponibili', return_value=False):
            env['start_conversation_gpt']('Parliamo')
        env['submit_gemma_voice'].assert_called_once_with('Parliamo', typed=False, route='locale')   # 055: GPT non collegato, si passa oltre

    def test_ptt_free_speech_routes_without_overwriting_console_draft(self):
        import test_voice_corrections_review as fixture
        from voice_control import PUSH_TO_TALK
        fixture.VoiceCorrectionReviewTests.setUpClass()
        harness = fixture.VoiceCorrectionReviewTests()
        self.addCleanup(harness.doCleanups)
        harness.setUp()
        harness.voice_environment(PUSH_TO_TALK)
        env = harness.env
        env['request'] = fixture.Value('Bozza da conservare')
        harness.receive_voice('Parliamo della giornata')
        env['start_conversation_gpt'].assert_called_once_with('Parliamo della giornata')
        self.assertEqual(env['request'].get(), 'Bozza da conservare')

    def test_pending_telegram_message_has_priority_in_console_and_voice(self):
        import test_activity_status as callbacks
        import test_typed_timer_routing as typed
        import test_voice_corrections_review as voice
        from voice_control import GPT_CONVERSATION
        callbacks.ActivityStatusTests.setUpClass()
        voice.VoiceCorrectionReviewTests.setUpClass()
        for channel in ('console','voice'):
            with self.subTest(channel=channel):
                if channel == 'console':
                    harness = typed.TypedTimerTests()
                    self.addCleanup(harness.doCleanups)
                    env = harness.environment('usa GPT')
                else:
                    harness = voice.VoiceCorrectionReviewTests()
                    self.addCleanup(harness.doCleanups)
                    harness.setUp()
                    harness.voice_environment(GPT_CONVERSATION)
                    env = harness.env
                env.update(closing=False, document_busy=False, pending_project_name=False,
                           pending_project_rename_id=None, pending_project_trash_id=None,
                           telegram_voice_dialog=SimpleNamespace(pending=True),
                           try_telegram_voice_send=Mock(return_value=True))
                if channel == 'console':
                    env['send_console_input']()
                else:
                    harness.receive_voice('Lumi usa GPT')
                env['try_telegram_voice_send'].assert_called_once_with(
                    'usa GPT' if channel == 'console' else 'usa gpt')

