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
