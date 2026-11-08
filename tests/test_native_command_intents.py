"""Gemma owner -> validated existing executor, with controlled inference/OS."""
import json
import os
import sqlite3
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import test_native_project_history as fixture
from local_engine import LocalEngine
from dialogue_focus import PendingProjectReference


@unittest.skipUnless(os.name == 'nt', 'Windows-only project')
class NativeCommandIntentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture.NativeProjectHistoryTests.setUpClass()

    def setUp(self):
        self.owner = fixture.NativeProjectHistoryTests()
        self.addCleanup(self.owner.doCleanups)
        self.owner.setUp()
        self.env = self.owner.env
        self.engine = LocalEngine(db_path=self.owner.workspace.path.with_name('native-actions.db'), windows=True)
        self.env.update(engine=self.engine, save_only_waiting=False,
            pending_project_name=False, pending_project_rename_id=None,
            pending_project_trash_id=None, announce_document=Mock(),
            pending_project_reference=PendingProjectReference(),
            document_operation=Mock(), try_telegram_voice_send=Mock(return_value=False))
        def submit_local(*, message_override, **kwargs):
            self.engine.execute(message_override)
        self.env['submit_local'] = submit_local
        # Bind the shared dispatcher when introduced; the Red owner has none.
        names = {getattr(n, 'name', '') for n in self.owner.harness.main.body}
        if 'dispatch_model_capability' in names:
            self.owner.harness.callback('dispatch_model_capability', self.env)

    def actions(self):
        with sqlite3.connect(self.engine.db_path) as db:
            return db.execute('SELECT action,status FROM tasks ORDER BY rowid').fetchall()

    def ask(self, text, *, typed=False):
        self.owner.submit(text, typed=typed)
        self.owner.finish()

    def model(self, action_id):
        return patch.object(self.owner.adapter, 'call', return_value={'text':json.dumps(
            {'kind':'capability','action_id':action_id,'arguments':{}})})

    def test_native_interpretation_executes_existing_status_action_once(self):
        with self.model('system.status') as inference:
            self.ask('Dimmi come sta il computer', typed=True)
        self.assertEqual(self.actions(), [('system_status','completed')])
        inference.assert_called_once()
        self.owner.online.call.assert_not_called()
        self.assertEqual(list(self.owner.session.history), [], 'A proposed action is not a chat answer')

    def test_native_browser_interpretation_uses_windows_default(self):
        with self.model('browser.open'), patch('local_engine.webbrowser.open', return_value=True) as browser:
            self.ask('Mi serve una finestra per navigare sul web')
        self.assertEqual(self.actions(), [('open_browser','completed')])
        browser.assert_called_once_with('https://www.google.com/', new=2)

    def test_unknown_native_capability_is_not_executed_or_committed(self):
        with self.model('shell.run'):
            self.ask('Esegui una richiesta non disponibile')
        self.assertEqual(self.actions(), [])
        self.assertEqual(list(self.owner.session.history), [])
        self.owner.online.call.assert_not_called()

    def test_duplicate_native_delivery_never_executes_twice(self):
        with self.model('system.status'):
            self.owner.submit('Dimmi come sta il computer')
            self.owner.workers.pop()()
        event = self.env['gemma_trial_queue'].get_nowait()
        self.env['gemma_trial_queue'].put(event)
        self.env['gemma_trial_queue'].put(event)
        self.env['poll_gemma_trial']()
        self.assertEqual(self.actions(), [('system_status','completed')])

    def test_revoked_native_delivery_cannot_execute(self):
        with self.model('system.status'):
            self.owner.submit('Dimmi come sta il computer')
            self.owner.workers.pop()()
        self.env['conversation_epoch'] += 1
        self.env['poll_gemma_trial']()
        self.assertEqual(self.actions(), [])
        self.assertEqual(list(self.owner.session.history), [])

    def test_structured_native_chat_keeps_only_reply_in_conversation(self):
        with patch.object(self.owner.adapter, 'call', return_value={
                'text':json.dumps({'kind':'chat','reply':'Parliamo pure di cinema.'})}):
            self.ask('Parliamo di cinema', typed=True)
        self.assertEqual(self.actions(), [])
        self.assertEqual(list(self.owner.session.history), [
            ('user','Parliamo di cinema'), ('assistant','Parliamo pure di cinema.')])

    def test_malformed_native_reply_never_executes_or_becomes_chat_history(self):
        with patch.object(self.owner.adapter, 'call', return_value={
                'text':'{"kind":"capability","action_id":"browser.open",'}):
            self.ask('Mi serve una finestra per navigare')
        self.assertEqual(self.actions(), [])
        self.assertEqual(list(self.owner.session.history), [])
        self.owner.online.call.assert_not_called()

    def test_session_stop_revokes_already_generated_action(self):
        with self.model('system.status'):
            self.owner.submit('Dimmi come sta il computer')
            self.owner.workers.pop()()
        self.owner.session.stop()
        self.env['poll_gemma_trial']()
        self.assertEqual(self.actions(), [])
        self.assertEqual(list(self.owner.session.history), [])

    def test_negated_request_cannot_authorize_model_proposal(self):
        with self.model('browser.open'), patch('local_engine.webbrowser.open') as browser:
            self.ask('Non aprire il browser')
        browser.assert_not_called()
        self.assertEqual(self.actions(), [])
        self.assertEqual(list(self.owner.session.history), [])

    def test_new_pending_dialogue_blocks_generated_action(self):
        with self.model('system.status'):
            self.owner.submit('Dimmi come sta il computer')
            self.owner.workers.pop()()
        self.env['document_busy'] = True
        self.env['poll_gemma_trial']()
        self.assertEqual(self.actions(), [])
        self.assertEqual(list(self.owner.session.history), [])

    def test_changed_document_cannot_be_closed_by_old_proposal(self):
        close = self.env['ask_to_close_document'] = Mock()
        self.env['documents'].current = SimpleNamespace(ident='old-document')
        with self.model('notepad.close'):
            self.owner.submit('Chiudi il documento che avevi aperto')
            self.owner.workers.pop()()
        self.env['documents'].current = SimpleNamespace(ident='new-document')
        self.env['poll_gemma_trial']()
        close.assert_not_called()
        self.env['announce_document'].assert_called_once()
        self.assertEqual(list(self.owner.session.history), [])

    def test_revoked_addon_is_rechecked_before_native_dispatch(self):
        from addon_manager import AddonManager
        from live_capabilities import LiveCapabilityRegistry
        from pathlib import Path
        manager = AddonManager(LiveCapabilityRegistry(), self.owner.workspace.path.parent/'addons')
        manager.install(Path('examples/addons/DiagnosticaSistema.jaddon'))
        manager.set_enabled('diagnostica_sistema', True)
        self.env['addon_manager'] = manager
        with self.model('addon.diagnostica_sistema.stato'):
            self.owner.submit('Controlla lo stato del PC')
            self.owner.workers.pop()()
        manager.set_enabled('diagnostica_sistema', False)
        self.env['poll_gemma_trial']()
        self.assertEqual(self.actions(), [])
        self.assertEqual(list(self.owner.session.history), [])

    def test_small_context_preserves_chat_without_adding_action_authority(self):
        from local_model.native_config import NativeModelConfig
        self.owner.session.config_loader = lambda: NativeModelConfig(context_size=512, max_output=128)
        self.ask('Parliamo di cinema')
        self.assertEqual(self.actions(), [])
        self.assertEqual(list(self.owner.session.history), [
            ('user','Parliamo di cinema'), ('assistant','Risposta locale 1')])
        self.assertLessEqual(len(self.owner.adapter.prompts[-1]), 256)
        self.assertTrue(any('Contesto insufficiente' in str(call)
                            for call in self.env['write_line'].call_args_list))
