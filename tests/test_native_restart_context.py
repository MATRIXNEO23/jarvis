"""Restart continuity through real UI callbacks, SQLite, and context selection."""
import os
import sqlite3
import unittest
import test_native_durable_memory as durable


@unittest.skipUnless(os.name == 'nt', 'Windows-only project requirement')
class RestartContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        durable.NativeDurableMemoryTests.setUpClass()

    def setUp(self):
        self.f = durable.NativeDurableMemoryTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)

    def reopen(self):
        self.f.reopen()
        self.f.fixture.adapter.context_token_counter = lambda: lambda text: (len(text)+3)//4+1

    def long_answer(self):
        return 'Una spiegazione storica dettagliata. ' * 90 + 'La parola clown era una metafora conclusiva.'

    def test_general_restart_preserves_late_reference_in_original_role(self):
        self.f.brain.remember_turn('Parliamo di Mussolini', self.long_answer())
        self.reopen()
        prompt = self.f.ask('Perché hai detto clown?')
        self.assertIn('Parliamo di Mussolini', prompt)
        self.assertIn('clown era una metafora', prompt.split('<start_of_turn>model')[1])
        self.assertEqual(len(self.f.fixture.adapter.prompts), 1)
        self.f.fixture.online.call.assert_not_called()

    def test_project_restart_preserves_detail_without_crossing_partitions(self):
        fixture = self.f.fixture
        fixture.workspace.add_turn('project', fixture.project_a, 'Mussolini progetto A', self.long_answer())
        fixture.workspace.add_turn('project', fixture.project_b, 'RISERVATO_B', 'Risposta B')
        self.f.brain.remember_turn('RISERVATO_GENERALE', 'Risposta generale')
        fixture.switch(fixture.project_a)
        self.reopen()
        prompt = self.f.ask('Perché clown?')
        self.assertIn('Mussolini progetto A', prompt)
        self.assertIn('clown era una metafora', prompt)
        self.assertNotIn('RISERVATO_B', prompt)
        self.assertNotIn('RISERVATO_GENERALE', prompt)

    def test_general_off_and_clear_remove_original_recall(self):
        self.f.brain.remember_turn('Antecedente riservato', self.long_answer())
        self.f.toggle(False)
        self.reopen()
        self.assertNotIn('metafora conclusiva', self.f.ask('Perché clown?'))
        self.f.toggle(True)
        self.f.env['clear_saved_memory']()
        self.reopen()
        self.assertNotIn('metafora conclusiva', self.f.ask('Perché clown?'))

    def test_recent_original_retention_is_bounded_without_erasing_legacy_records(self):
        for i in range(20):
            self.f.brain.remember_turn('Domanda ' + str(i), self.long_answer())
        with sqlite3.connect(self.f.brain.path) as db:
            # Read public record behavior, not proposed table/schema names.
            self.assertEqual(db.execute('SELECT COUNT(*) FROM conversations').fetchone()[0], 20)
        self.reopen()
        prompt = self.f.ask('Perché clown?')
        self.assertIn('Domanda 19', prompt)
        self.assertNotIn('Domanda 0<end_of_turn>', prompt)
        self.assertIn('clown era una metafora', prompt)

    def test_recent_payload_is_pruned_and_old_version_clear_erases_it(self):
        for i in range(20):
            self.f.brain.remember_turn('Domanda '+str(i), 'A' * 18000)
        with sqlite3.connect(self.f.brain.path) as db:
            count, longest = db.execute('SELECT COUNT(*),MAX(length(reply)) FROM recent_dialogue').fetchone()
            self.assertLessEqual(count, 16)
            self.assertLessEqual(longest, 16384)
            # Simulate010: its clear code knows only the original table.
            db.execute('DELETE FROM conversations')
            self.assertEqual(db.execute('SELECT COUNT(*) FROM recent_dialogue').fetchone()[0], 0)

    def test_project_payload_retention_is_per_project_and_telegram_is_excluded(self):
        fixture = self.f.fixture
        w = fixture.workspace
        for ident in (fixture.project_a, fixture.project_b):
            for i in range(20):
                w.add_turn('project', ident, 'Domanda '+str(i), 'A' * 18000)
        self.assertEqual(len(w.dialogue_pairs('project', fixture.project_a, 100)), 16)
        self.assertEqual(len(w.dialogue_pairs('project', fixture.project_b, 100)), 16)
        self.assertFalse(w.add_turn('telegram', '123', 'Non duplicare', 'Testo'))
        with sqlite3.connect(w.path) as db:
            self.assertLessEqual(db.execute('SELECT COUNT(*) FROM recent_dialogue').fetchone()[0], 32)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM messages').fetchone()[0], 40)
            self.assertLessEqual(db.execute('SELECT MAX(length(reply)) FROM recent_dialogue').fetchone()[0], 16384)
            for ident in (fixture.project_a, fixture.project_b):
                questions = [p[0][1] for p in w.dialogue_pairs('project', ident, 100)]
                self.assertEqual(questions[0], 'Domanda 4')
                self.assertEqual(questions[-1], 'Domanda 19')
            db.execute('DELETE FROM messages WHERE scope_id=?', (fixture.project_b,))
            remaining = db.execute('SELECT COUNT(*) FROM recent_dialogue').fetchone()[0]
            self.assertEqual(remaining, 16)
        w.trash_project(fixture.project_a)
        self.assertEqual(w.dialogue_pairs('project', fixture.project_a), ())

    def test_clear_while_restored_turn_waits_for_acceptance_cannot_resurrect_history(self):
        self.f.brain.remember_turn('Antecedente da cancellare', self.long_answer())
        self.reopen()
        fixture = self.f.fixture
        fixture.submit('Perché clown?', typed=True)
        fixture.workers.pop()()
        self.f.env['clear_saved_memory']()
        self.f.env['poll_gemma_trial']()
        self.assertEqual(tuple(fixture.session.history), ())
        self.assertEqual(self.f.brain.stats()[0], 0)
        self.assertNotIn('metafora conclusiva', self.f.ask('Ripartiamo'))

    def test_switch_off_before_acceptance_preserves_live_reply_without_hydrating_archive(self):
        self.f.brain.remember_turn('ARCHIVIO_REVOCATO', self.long_answer())
        self.reopen()
        fixture = self.f.fixture
        fixture.submit('Perché clown?', typed=True)
        fixture.workers.pop()()
        self.f.toggle(False)
        self.f.env['poll_gemma_trial']()
        history = tuple(fixture.session.history)
        self.assertEqual(len(history), 2)
        self.assertNotIn('ARCHIVIO_REVOCATO', str(history))

    def test_clear_during_recent_read_excludes_old_text_from_native_input(self):
        import threading
        from unittest.mock import patch
        self.f.brain.remember_turn('ARCHIVIO_CANCELLATO_DURANTE_LETTURA', self.long_answer())
        self.reopen()
        owner = self.f.env['durable_brain']
        original = owner.dialogue_pairs
        entered, release = threading.Event(), threading.Event()
        def blocked(count):
            result = original(count)
            entered.set()
            if not release.wait(5):
                raise RuntimeError('Controlled reader deadline')
            return result
        fixture = self.f.fixture
        with patch.object(owner, 'dialogue_pairs', side_effect=blocked):
            fixture.submit('Perché clown?', typed=True)
            worker = threading.Thread(target=fixture.workers.pop(), daemon=True)
            worker.start()
            try:
                self.assertTrue(entered.wait(3))
                self.f.env['clear_saved_memory']()
            finally:
                release.set()
                worker.join(5)
            self.assertFalse(worker.is_alive())
        self.f.env['poll_gemma_trial']()
        self.assertNotIn('ARCHIVIO_CANCELLATO_DURANTE_LETTURA', fixture.adapter.prompts[-1])
        self.assertEqual(tuple(fixture.session.history), ())
