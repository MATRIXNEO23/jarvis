"""Console routing regressions: real parser/engine, controlled OS boundaries."""
import os
import sqlite3
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import test_typed_timer_routing as fixture
from local_engine import LocalEngine
from voice_control import speech_to_local_command


@unittest.skipUnless(os.name == 'nt', 'Windows-only project')
class InternalCommandRoutingTests(unittest.TestCase):
    def environment(self, text):
        harness = fixture.TypedTimerTests()
        self.addCleanup(harness.doCleanups)
        env = harness.environment(text)
        # The existing fixture supplies an isolated profile and a valid unused
        # GGUF path, so the baseline really takes the configured Gemma branch.
        from local_model.native_settings import default_native_settings_path
        folder = default_native_settings_path().parent
        downloads = folder / 'Downloads'
        downloads.mkdir(exist_ok=True)
        engine = LocalEngine(download_dir=downloads, db_path=folder/'routing.db', windows=True)
        env.update(engine=engine, speech_to_local_command=speech_to_local_command,
                   busy_local=False, document_operation=Mock())
        def submit_local(event=None, message_override=None, **kwargs):
            engine.execute(message_override if message_override is not None else env['request'].get())
        env['submit_local'] = submit_local
        return env, engine

    def actions(self, engine):
        with sqlite3.connect(engine.db_path) as db:
            return db.execute('SELECT action, status FROM tasks ORDER BY rowid').fetchall()

    def test_system_status_from_normal_send_bypasses_configured_gemma(self):
        env, engine = self.environment('stato sistema')
        env['send_console_input']()
        self.assertEqual(self.actions(engine), [('system_status', 'completed')])
        env['submit_gemma_trial'].assert_not_called()

    def test_default_browser_needs_no_program_apps_and_opens_once(self):
        env, engine = self.environment('apri browser')
        with patch('local_engine.webbrowser.open', return_value=True) as browser:
            env['send_console_input']()
        self.assertEqual(self.actions(engine), [('open_browser', 'completed')])
        browser.assert_called_once_with('https://www.google.com/', new=2)
        env['submit_gemma_trial'].assert_not_called()

    def test_internal_synonyms_share_the_existing_action(self):
        for phrase, command in (
            ('avvia la calcolatrice', 'apri calcolatrice'),
            ('lancia la calcolatrice', 'apri calcolatrice'),
            ('mostrami lo stato del sistema', 'stato sistema'),
            ('mostra Download', 'apri download'),
            ('apri il browser predefinito', 'apri browser'),
        ):
            with self.subTest(phrase=phrase):
                self.assertEqual(speech_to_local_command(phrase), command)

    def test_negated_or_conversational_mentions_are_not_local_actions(self):
        for phrase in ('non aprire il browser', 'spiegami come avviare la calcolatrice',
                       'se dico apri browser cosa succede?', 'non mostrare Download'):
            with self.subTest(phrase=phrase):
                self.assertIsNone(speech_to_local_command(phrase))

    def test_pending_document_and_project_keep_ownership(self):
        for pending in ('document', 'project'):
            env, engine = self.environment('stato sistema')
            if pending == 'document':
                env['doc_dialog'].phase = 'awaiting_save'
                env['handle_document_confirmation'] = Mock()
            else:
                env['pending_project_name'] = True
                env['project_voice_command'] = Mock(return_value=True)
            env['send_console_input']()
            self.assertEqual(self.actions(engine), [])
            env['submit_gemma_trial'].assert_not_called()

    def test_existing_program_interception_still_precedes_model(self):
        env, engine = self.environment('apri Netflix')
        env['try_file_command'] = Mock(return_value=True)
        env['send_console_input']()
        env['try_file_command'].assert_called_once_with('apri Netflix')
        env['submit_gemma_trial'].assert_not_called()
        self.assertEqual(self.actions(engine), [])
