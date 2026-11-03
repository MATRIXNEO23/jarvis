"""Windows filesystem: index ordering, scope and bounded fallback behavior."""
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import test_file_access as access_tests


@unittest.skipUnless(os.name == 'nt', 'Windows-only user requirement')
class IndexPriorityTests(unittest.TestCase):
    setUp = access_tests.FileAccessTests.setUp

    def two_roots(self):
        other = self.root / 'Seconda'
        other.mkdir()
        self.files.policy.configure([(self.docs, True), (self.hidden, False), (other, True)])
        roots = [Path(r['path']) for r in self.files.policy.valid_roots() if r['allow']]
        return roots

    def test_later_root_is_queried_before_direct_scan_can_consume_budget(self):
        roots = self.two_roots()
        target = roots[1] / 'cercato.txt'
        target.write_text('fixture', encoding='utf-8')
        queried = []
        def index(query, root):
            self.assertEqual(query, 'cercato')
            queried.append(root)
            return ([target] if os.path.samefile(root, roots[1]) else []), 'Indice controllato'
        self.files.index = index
        self.files.max_entries = 1
        result = self.engine.execute_file('search', {'query': 'cercato'})
        self.assertEqual(result.status, 'completed', result.message)
        self.assertEqual(len(queried), 2)
        self.assertEqual(len(self.files._results), 1)
        self.assertTrue(os.path.samefile(target, self.files._results[0]))

    def test_positive_index_result_does_not_launch_direct_scan_or_claim_full_coverage(self):
        target = self.docs / 'cercato'
        target.mkdir()
        self.files.index = lambda *args: ([target], 'Indice interrogato; copertura non completa.')
        native_scan = os.scandir
        scanned = []
        def scan(path):
            scanned.append(path)
            return native_scan(path)
        with patch('file_access.service.os.scandir', side_effect=scan):
            result = self.engine.execute_file('search', {'query': 'cercato'})
        self.assertEqual(result.status, 'completed', result.message)
        self.assertEqual(scanned, [])
        self.assertEqual(result.file_listing['coverage']['scanned'], 0)
        self.assertIn('copertura non completa', result.file_listing['summary'])
        self.assertTrue(os.path.samefile(self.files._results[0], target))

    def test_empty_index_keeps_real_fallback_and_reports_its_limits(self):
        self.files.max_entries = 1
        queried = []
        self.files.index = lambda query,root: (queried.append(root) or [], 'Indice non disponibile nel campione.')
        result = self.engine.execute_file('search', {'query': 'assente'})
        self.assertEqual(result.status, 'completed', result.message)
        self.assertTrue(queried)
        self.assertEqual(result.file_listing['coverage']['stop_reason'], 'entry_limit')
        self.assertIn('Ricerca parziale', result.message)
        self.assertGreater(result.file_listing['coverage']['scanned'], 0)

    def test_locate_preserves_index_feedback_alongside_installation_feedback(self):
        target = self.docs / 'cercato'
        target.mkdir()
        self.files.index = lambda *args: ([target], 'Indice del campione interrogato.')
        with patch('file_access.service.installed_locations', return_value=[]):
            result = self.engine.execute_file('locate', {'query': 'cercato'})
        self.assertEqual(result.status, 'completed', result.message)
        self.assertIn('registrazioni/collegamenti', result.message)
        self.assertIn('Indice del campione interrogato', result.message)

    def test_revocation_during_index_phase_discards_hits_and_stops(self):
        roots = self.two_roots()
        queried = []
        def index(query,root):
            queried.append(root)
            self.manager.set_enabled('accesso_file', False)
            return [self.a], 'Risposta arrivata dopo revoca.'
        self.files.index = index
        result = self.engine.execute_file('search', {'query': 'preventivo'})
        self.assertEqual(result.status, 'rejected')
        self.assertEqual(len(queried), 1)
        self.assertFalse(self.files._results)

    def test_overlapping_roots_do_not_report_a_limit_for_duplicate_or_excluded_hits(self):
        nested = self.docs / 'Archivio'
        nested.mkdir()
        self.files.policy.configure([(self.docs, True), (nested, True), (self.hidden, False)])
        hits = []
        for number in range(20):
            path = nested / ('cercato-'+str(number)+'.txt')
            path.write_text('fixture', encoding='utf-8')
            hits.append(path)
        excluded = self.hidden / 'cercato-nascosto.txt'
        excluded.write_text('private fixture', encoding='utf-8')
        self.files.index = lambda *args: (hits+[excluded], 'Indice controllato')
        result = self.engine.execute_file('search', {'query':'cercato'})
        self.assertEqual(result.status, 'completed', result.message)
        self.assertEqual(len(self.files._results), 20)
        self.assertEqual(result.file_listing['coverage']['index_queried'], 2)
        self.assertFalse(result.file_listing['coverage']['index_limited'])
        extra = nested / 'cercato-extra.txt'
        extra.write_text('fixture', encoding='utf-8')
        hits.append(extra)
        result = self.engine.execute_file('search', {'query':'cercato'})
        self.assertEqual(len(self.files._results), 20)
        self.assertTrue(result.file_listing['coverage']['index_limited'])
