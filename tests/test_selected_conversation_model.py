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
                   GPT_CONVERSATION='conversation', CONTINUOUS='continuous',
                   gpt_enabled=SimpleNamespace(get=lambda: True), active_gpt=True,
                   busy_gpt=False, try_self_diagnostic=Mock(return_value=False),
                   submit_gemma_voice=gemma, run_gpt=online,
                   documents=SimpleNamespace(current=None), conversation_epoch=7,
                   current_capability_snapshot=lambda _: {'telegram_voice_send': False},
                   build_conversation_prompt=__import__('conversation_router').build_conversation_prompt,
                   recent_memory_for_gpt=lambda _: '', capability_status_prompt=lambda _: '',
                   active_addon_actions=lambda: (), ConversationRejected=ValueError,
                   write_line=Mock(), speak_result=Mock())
        exec(compile(ast.Module(body=[callback], type_ignores=[]), 'real-voice-router', 'exec'), env)
        env['start_conversation_gpt']('Parliamo della giornata')
        gemma.assert_not_called()
        online.assert_called_once()

    def test_console_selected_gpt_wins_over_configured_gemma(self):
        import test_typed_timer_routing as fixture
        harness = fixture.TypedTimerTests()
        self.addCleanup(harness.doCleanups)
        env = harness.environment('Parliamo della giornata')
        env.update(gpt_enabled=SimpleNamespace(get=lambda: True), active_gpt=True,
                   busy_gpt=False, submit_gpt=Mock())
        env['send_console_input']()
        env['submit_gemma_trial'].assert_not_called()
        env['submit_gpt'].assert_called_once()

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

    def test_telegram_selected_but_disconnected_does_not_use_local_model(self):
        import test_activity_status as fixture
        fixture.ActivityStatusTests.setUpClass()
        harness = fixture.ActivityStatusTests()
        self.addCleanup(harness.doCleanups)
        env, _, _ = harness.environment()
        env.update(get_gemma_session=Mock(), ask_telegram_gpt=Mock(),
                   telegram_assistant_prompt=lambda *a: 'prompt', settings={'gpt_enabled': True})
        reply = harness.callback('ask_telegram_reply', env)
        self.assertEqual(reply('Ciao', '', SimpleNamespace(is_enabled=lambda: True)), '')
        env['get_gemma_session'].assert_not_called()

    def test_switch_synonyms_change_existing_toggle_without_model_inference(self):
        import test_typed_timer_routing as fixture
        for phrase, selected in [('passa a GPT', True), ('torna a Gemma', False),
                                 ('usa GPT', True), ('avvia Gemma', False)]:
            with self.subTest(phrase=phrase):
                harness = fixture.TypedTimerTests()
                self.addCleanup(harness.doCleanups)
                env = harness.environment(phrase)
                import test_activity_status as callbacks
                callbacks.ActivityStatusTests.setUpClass()
                env.update(gpt_enabled=callbacks.Value(not selected), toggle_gpt=Mock(),
                           closing=False, document_busy=False)
                # Compile new handler only when present, so the baseline really
                # follows the old console routing instead of a missing symbol.
                main = next(n for n in ast.parse(Path('jarvis.py').read_text()).body
                            if isinstance(n, ast.FunctionDef) and n.name == 'main')
                handler = next((n for n in main.body if isinstance(n, ast.FunctionDef)
                                and n.name == 'try_model_switch'), None)
                if handler:
                    exec(compile(ast.Module(body=[handler],type_ignores=[]),'model-switch','exec'),env)
                env['send_console_input']()
                env['toggle_gpt'].assert_called_once()
                self.assertEqual(env['gpt_enabled'].get(), selected)
                env['submit_gemma_trial'].assert_not_called()
