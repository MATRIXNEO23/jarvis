"""Windows-only delivery of real file context to the external-model prompt.

The model is not called. Files, policy, memory, app callback and prompt builder
are real; Explorer discovery and opening are isolated from the CI desktop.
"""
import json
import os
import unittest

import test_file_access as access_tests
import test_file_refinement as refinement_tests
from test_activity_status import Value
from conversation_memory import ConversationMemory
from conversation_router import build_conversation_prompt
from dialogue_focus import focus_hint
from jarvis_persona import compact_memory
from live_capabilities import snapshot_capabilities, capability_status_prompt


@unittest.skipUnless(os.name == 'nt', 'Windows-only user requirement')
class FileContextDeliveryTests(unittest.TestCase):
    setUp = access_tests.FileAccessTests.setUp
    setUpClass = classmethod(refinement_tests.FileRefinementTests.setUpClass.__func__)
    callback = refinement_tests.FileRefinementTests.callback

    def memory_for(self, utterance, memory=None):
        env = dict(conversation_memory=memory or ConversationMemory(),
                   focus_hint=focus_hint, json=json, active_project_id=None,
                   addon_manager=self.manager, preference_store=None,
                   memory_enabled=Value(False), durable_brain=None)
        return self.callback('recent_memory_for_gpt', env)(utterance)

    def prompt_for(self, utterance, memory=None):
        raw = self.memory_for(utterance, memory)
        live = snapshot_capabilities(settings={}, has_document=False,
            telegram_credentials=False, telegram_voice_dependencies=False,
            registry=self.manager.registry, telethon_installed=False)
        prompt = build_conversation_prompt(utterance, memory_context=raw,
            runtime_info=capability_status_prompt(live),
            addon_actions=self.manager.active_actions())
        self.assertLessEqual(len(prompt.encode('utf-16-le')) // 2, 5000)
        return raw, prompt

    def search_folders(self):
        (self.docs / 'Minecraft Java').mkdir()
        (self.docs / 'Minecraft Bedrock').mkdir()
        result = self.engine.execute_file('search', {'query': 'Minecraft'})
        self.assertEqual(result.status, 'completed', result.message)
        self.assertEqual({p.name for p in self.files._results},
                         {'Minecraft Java', 'Minecraft Bedrock'})

    def test_found_folders_reach_the_actual_prompt_without_full_paths(self):
        self.search_folders()
        raw, prompt = self.prompt_for('Quale delle due contiene Bedrock?')
        # Establish that the producer has data before testing its consumer.
        self.assertIn('Minecraft Java', json.loads(raw)['focus']['file_results'])
        self.assertIn('Minecraft Bedrock', prompt)
        self.assertIn('Minecraft Java', prompt)
        self.assertNotIn(str(self.docs), prompt)

    def test_pending_open_and_question_survive_compaction(self):
        self.search_folders()
        result = self.engine.execute_file('open', {'target': 'Minecraft', 'kind': 'folder'})
        self.assertEqual(result.status, 'completed', result.message)
        self.assertIsNotNone(self.files._pending)
        memory = ConversationMemory()
        memory.remember('Apri la cartella di Minecraft',
                        'Quale cartella vuoi aprire?', 'clarify')
        raw, prompt = self.prompt_for('Quella di Bedrock', memory)
        self.assertIn('aprire', json.loads(raw)['focus']['file_results'])
        self.assertIn('Minecraft Bedrock', prompt)
        self.assertIn('Quale cartella vuoi aprire?', prompt)
        self.assertTrue(prompt.endswith('"Quella di Bedrock"'))

    def test_revoked_or_disabled_results_are_not_sent_to_model(self):
        for change in ('revoke', 'disable'):
            with self.subTest(change=change):
                self.files.policy.configure([(self.docs, True), (self.hidden, False)])
                self.manager.set_enabled('accesso_file', True)
                self.engine.execute_file('search', {'query': 'preventivo'})
                if change == 'revoke':
                    self.files.policy.configure([(self.docs, False)])
                else:
                    self.manager.set_enabled('accesso_file', False)
                _, prompt = self.prompt_for('Quello trovato prima')
                self.assertNotIn('preventivo-à.txt', prompt)

    def test_expired_or_replaced_results_are_not_sent_to_model(self):
        self.engine.execute_file('search', {'query': 'preventivo'})
        self.files._expires = 0
        _, prompt = self.prompt_for('Quello trovato prima')
        self.assertNotIn('preventivo-à.txt', prompt)
        self.engine.execute_file('search', {'query': 'preventivo'})
        replacement = self.docs / 'nuovo.txt'
        replacement.write_text('fixture', encoding='utf-8')
        self.engine.execute_file('search', {'query': 'nuovo'})
        _, prompt = self.prompt_for('Quello trovato adesso')
        self.assertNotIn('preventivo-à.txt', prompt)
        self.assertIn('nuovo.txt', prompt)

    def test_file_context_fits_budget_without_displacing_project_or_question(self):
        raw = json.dumps({'focus': {
            'project': {'name': 'Progetto attuale'},
            'pending_question': 'Quale cartella vuoi aprire?',
            'follow_up': 'La seconda',
            'file_results': 'Risultati file selezionabili: 1: Cartella Minecraft Java, '
                            '2: Cartella Minecraft Bedrock. ' + 'Altro risultato. ' * 100},
            'breve': [{'utente': 'x' * 260, 'jarvis': 'y' * 280}]}, ensure_ascii=False)
        for budget in (400, 850):
            with self.subTest(budget=budget):
                packed = compact_memory(raw, budget)
                self.assertLessEqual(len(packed), budget)
                focus = json.loads(packed)['focus']
                self.assertEqual(focus['selected_project'], 'Progetto attuale')
                self.assertEqual(focus['question_to_answer'], 'Quale cartella vuoi aprire?')
                self.assertIn('Minecraft Bedrock', focus['file_results'])


if __name__ == '__main__':
    unittest.main()
