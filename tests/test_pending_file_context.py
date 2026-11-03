"""Windows-only R02: unresolved clarifications must keep their local goal.

Real temporary files, permissions, application callbacks and prompt builder.
The external-model transport and worker scheduling are controlled; no login,
microphone or personal desktop is exercised.
"""
import json
import os
import unittest
from unittest.mock import patch

import test_file_access as access_tests
import test_file_refinement as refinement_tests
import test_file_context_delivery as context_tests


@unittest.skipUnless(os.name == 'nt', 'Windows-only user requirement')
class PendingFileContextTests(unittest.TestCase):
    setUp = access_tests.FileAccessTests.setUp
    setUpClass = classmethod(refinement_tests.FileRefinementTests.setUpClass.__func__)
    callback = refinement_tests.FileRefinementTests.callback
    environment = refinement_tests.FileRefinementTests.environment
    receive = refinement_tests.FileRefinementTests.receive
    memory_for = context_tests.FileContextDeliveryTests.memory_for
    prompt_for = context_tests.FileContextDeliveryTests.prompt_for

    def missing_name(self):
        operation, args = self.files.parse_command('cercami un file')
        result = self.engine.execute_file(operation, args)
        self.assertEqual(result.status, 'completed', result.message)
        self.assertIsNotNone(self.files._pending)
        return self.files._result_token

    def test_missing_name_survives_unparsed_clarification_then_real_search(self):
        token = self.missing_name()
        env, workers = self.environment()
        phrase = 'Non ricordo il nome preciso, possiamo restringere la ricerca?'
        self.assertFalse(env['try_file_command'](phrase))
        self.assertFalse(workers, 'An uncertain clarification must not perform an action')
        self.assertEqual(self.files._result_token, token)
        self.assertIsNotNone(self.files._pending)
        raw, prompt = self.prompt_for(phrase)
        self.assertIn('Quale file o cartella vuoi cercare?',
                      json.loads(raw)['focus']['file_results'])
        self.assertIn('Richiesta file in attesa', prompt)
        self.assertTrue(env['try_file_command']('preventivo'))
        self.assertEqual(len(workers), 1)
        workers.pop(0)()
        with patch('file_access.ui.show_results'):
            self.receive('local', env)
        self.assertEqual([p.name for p in self.files._results], ['preventivo-à.txt'])
        env['service'].call.assert_not_called()

    def test_result_choice_survives_paraphrase_before_model_interpretation(self):
        (self.docs / 'preventivo-secondo.txt').write_text('secondo', encoding='utf-8')
        result = self.engine.execute_file('read', {'target': 'preventivo'})
        self.assertEqual(result.status, 'completed', result.message)
        self.assertIsNotNone(self.files._pending)
        env, workers = self.environment()
        phrase = 'Mi riferisco alla versione preparata insieme ieri'
        self.assertFalse(env['try_file_command'](phrase))
        self.assertFalse(workers)
        self.assertIsNotNone(self.files._pending)
        _, prompt = self.prompt_for(phrase)
        self.assertIn('preventivo-à.txt', prompt)
        self.assertIn('preventivo-secondo.txt', prompt)
        self.assertIn('leggere', prompt)

    def test_waiting_refinement_keeps_original_question_for_natural_answer(self):
        result = self.engine.execute_file('search', {'query': 'nome pronunciato'})
        token = result.file_listing['refinement']
        self.files.refinement_context(token, 'cerca file nome pronunciato')
        self.files.refinement_question(token, 'Ricordi una parte del nome?')
        env, workers = self.environment()
        phrase = 'Non ricordo il nome preciso'
        env['service'].call.return_value = {'text': json.dumps(
            {'kind': 'clarify', 'reply': 'Ti ricordi almeno una parola del nome?'})}
        self.assertTrue(env['try_file_command'](phrase))
        self.assertEqual(len(workers), 1)
        workers.pop(0)()
        prompt = env['service'].call.call_args.kwargs['prompt']
        self.assertIn('nome pronunciato', prompt)
        self.assertIn('Ricordi una parte del nome?', prompt)
        self.assertIn(phrase, prompt)
        self.receive('conversation_ok', env)
        self.assertFalse(workers)
        self.assertFalse(env['busy_local'])
        self.assertTrue(self.files.refinement_live(token))

    def test_cancel_expiry_revocation_and_project_change_do_not_retain_goal(self):
        for change in ('cancel', 'expiry', 'revoke', 'disable', 'project'):
            with self.subTest(change=change):
                self.manager.set_enabled('accesso_file', True)
                self.files.policy.configure([(self.docs, True), (self.hidden, False)])
                self.files.reset(None)
                self.missing_name()
                env, workers = self.environment()
                if change == 'cancel':
                    self.assertTrue(env['try_file_command']('annulla'))
                elif change == 'expiry':
                    self.files._expires = 0
                elif change == 'revoke':
                    self.files.policy.configure([(self.docs, False)])
                elif change == 'disable':
                    self.manager.set_enabled('accesso_file', False)
                else:
                    env['active_project_id'] = 'other-project'
                self.assertFalse(env['try_file_command']('Non ricordo il nome preciso'))
                self.assertFalse(workers)
                _, prompt = self.prompt_for('Non ricordo il nome preciso')
                self.assertNotIn('Richiesta file in attesa', prompt)

    def test_new_precise_request_supersedes_old_question(self):
        self.missing_name()
        (self.docs / 'fattura.txt').write_text('fattura', encoding='utf-8')
        env, workers = self.environment()
        self.assertTrue(env['try_file_command']('cerca file fattura'))
        workers.pop(0)()
        with patch('file_access.ui.show_results'):
            self.receive('local', env)
        self.assertIsNone(self.files._pending)
        self.assertEqual([p.name for p in self.files._results], ['fattura.txt'])


if __name__ == '__main__':
    unittest.main()
