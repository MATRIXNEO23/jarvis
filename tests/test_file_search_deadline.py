"""Windows service integration: one virtual budget, real temporary policy/files."""
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_file_access as access_tests


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@unittest.skipUnless(os.name == 'nt', 'Windows-only user requirement')
class SearchDeadlineTests(unittest.TestCase):
    def setUp(self):
        access_tests.FileAccessTests.setUp(self)
        self.clock = Clock()
        self.enterContext(patch('file_access.service.time.monotonic', self.clock))
        # Isolate Known Folders from the runner profile, not policy checks.
        self.enterContext(patch('file_access.service.known_folder', side_effect=OSError('fixture')))

    def roots(self, count=3, *, empty=False):
        directories = [self.docs] if not empty else []
        for number in range(count - len(directories)):
            folder = self.root / ('Radice-' + str(number))
            folder.mkdir()
            directories.append(folder)
        self.files.policy.configure([(p, True) for p in directories] + [(self.hidden, False)])
        return [Path(r['path']) for r in self.files.policy.valid_roots() if r['allow']]

    def native(self, callback):
        from file_access.windows import indexed_candidates
        self.files.index = indexed_candidates
        return self.enterContext(patch('file_access.windows.subprocess.run', side_effect=callback))

    @staticmethod
    def reply(paths=()):
        return SimpleNamespace(returncode=0, stdout=json.dumps({'status': 'ok', 'paths': [str(p) for p in paths]}))

    def search(self, query='assente', **arguments):
        return self.files.execute('search', {'query': query, **arguments})

    def assert_partial(self, result):
        self.assertEqual(result.status, 'completed', result.message)
        self.assertEqual(result.listing['coverage']['stop_reason'], 'time_limit')
        self.assertIn('Ricerca parziale', result.listing['summary'])
        self.assertNotIn('Ricerca conclusa', result.message)

    def test_many_slow_roots_share_ten_seconds_and_never_start_a_fresh_scan(self):
        roots = self.roots(4)
        waits, queried = [], []
        def slow(argv, **kw):
            self.assertFalse(kw['shell'])
            payload = json.loads(kw['input'])
            self.assertEqual(payload['query'], 'assente')
            queried.append(Path(payload['root']))
            waits.append(kw['timeout'])
            self.clock.advance(kw['timeout'])
            raise subprocess.TimeoutExpired(argv, kw['timeout'])
        self.native(slow)
        with patch('file_access.service.os.scandir', side_effect=AssertionError('Budget exhausted')):
            result = self.search()
        self.assertEqual(waits, [8, 2])
        self.assertEqual(queried, roots[:2])
        self.assertEqual(self.clock.now, 1010)
        self.assertEqual(result.listing['coverage']['index_queried'], 2)
        self.assertEqual(result.listing['coverage']['scanned'], 0)
        self.assert_partial(result)

    def test_short_budget_is_passed_to_the_existing_windows_wrapper(self):
        self.roots()
        self.files.max_seconds = 0.5
        def slow(argv, **kw):
            self.clock.advance(kw['timeout'])
            raise subprocess.TimeoutExpired(argv, kw['timeout'])
        run = self.native(slow)
        result = self.search()
        self.assertEqual([c.kwargs['timeout'] for c in run.call_args_list], [0.5])
        self.assert_partial(result)

    def test_fast_queries_keep_eight_second_cap_and_real_fallback(self):
        self.roots(2)
        def fast(argv, **kw):
            self.clock.advance(0.1)
            return self.reply()
        run = self.native(fast)
        result = self.search('preventivo')
        self.assertEqual(result.status, 'completed', result.message)
        self.assertEqual([c.kwargs['timeout'] for c in run.call_args_list], [8, 8])
        self.assertEqual(result.listing['coverage']['stop_reason'], 'complete')
        self.assertFalse(result.listing['coverage']['index_results_only'])
        self.assertGreater(result.listing['coverage']['scanned'], 0)
        self.assertTrue(os.path.samefile(self.files._results[0], self.a))

    def test_index_hit_survives_deadline_and_remains_readable_by_number(self):
        self.roots()
        calls = []
        def index(argv, **kw):
            calls.append(kw['timeout'])
            self.clock.advance(3 if len(calls) == 1 else kw['timeout'])
            return self.reply([self.a] if len(calls) == 1 else [])
        self.native(index)
        with patch('file_access.service.os.scandir', side_effect=AssertionError('Indexed hits need no scan')):
            result = self.search('preventivo')
        self.assertEqual(calls, [8, 7])
        self.assert_partial(result)
        self.assertTrue(result.listing['coverage']['index_results_only'])
        self.assertTrue(os.path.samefile(self.files._results[0], self.a))
        read = self.files.execute('read', {'target': '1'})
        self.assertEqual(read.status, 'completed', read.message)
        self.assertEqual(read.preview, 'Testo reale di esempio')

    def test_result_returned_at_exact_deadline_is_kept_with_partial_coverage(self):
        self.roots()
        def index(argv, **kw):
            self.clock.advance(10)
            return self.reply([self.a])
        run = self.native(index)
        result = self.search('preventivo')
        self.assertEqual(run.call_count, 1)
        self.assertEqual(len(result.listing['items']), 1)
        self.assert_partial(result)

    def test_partial_index_still_filters_excluded_and_outside_paths(self):
        self.roots()
        outside = self.root / 'assente-esterno.txt'
        outside.write_text('outside fixture', encoding='utf-8')
        hidden = self.hidden / 'assente-privato.txt'
        hidden.write_text('private fixture', encoding='utf-8')
        def index(argv, **kw):
            self.clock.advance(10)
            return self.reply([outside, hidden])
        run = self.native(index)
        result = self.search()
        self.assertEqual(run.call_count, 1)
        self.assert_partial(result)
        self.assertEqual(result.listing['items'], ())
        self.assertNotIn(outside.name, result.message)
        self.assertNotIn(hidden.name, result.message)

    def test_fallback_uses_only_time_left_after_index_and_checks_before_entries(self):
        self.roots(2)
        def index(argv, **kw):
            self.clock.advance(4)
            return self.reply()
        run = self.native(index)
        native_scan = os.scandir
        def scan(path):
            self.clock.advance(2)
            return native_scan(path)
        with patch('file_access.service.os.scandir', side_effect=scan) as walked:
            result = self.search()
        self.assertEqual([c.kwargs['timeout'] for c in run.call_args_list], [8, 6])
        self.assertEqual(walked.call_count, 1)
        self.assertEqual(result.listing['coverage']['scanned'], 0)
        self.assert_partial(result)

    def test_empty_directories_cannot_start_another_walk_after_deadline(self):
        self.roots(3, empty=True)
        self.files.index = lambda query, root: ([], 'Indice vuoto della fixture')
        native_scan = os.scandir
        def scan(path):
            self.clock.advance(10)
            return native_scan(path)
        with patch('file_access.service.os.scandir', side_effect=scan) as walked:
            result = self.search()
        self.assertEqual(walked.call_count, 1)
        self.assertEqual(result.listing['coverage']['scanned'], 0)
        self.assert_partial(result)

    def test_progress_can_consume_budget_before_first_index_or_walk(self):
        self.roots()
        def progress(snapshot):
            if snapshot['stage'] == 'Interrogo indice Windows':
                self.clock.advance(10)
        self.files.progress = progress
        run = self.native(lambda *a, **kw: self.reply())
        with patch('file_access.service.os.scandir', side_effect=AssertionError('No time remaining')):
            result = self.search()
        self.assertEqual(run.call_count, 0)
        self.assert_partial(result)

    def test_legacy_two_argument_callback_is_called_once_per_root(self):
        roots = self.roots(2)
        called = []
        def legacy(query, root):
            called.append((query, root))
            self.clock.advance(1)
            return ([self.a] if len(called) == 1 else []), 'Fixture legacy'
        self.files.index = legacy
        result = self.search('preventivo')
        self.assertEqual(called, [('preventivo', p) for p in roots])
        self.assertEqual(result.listing['coverage']['stop_reason'], 'index_coverage')
        self.assertTrue(os.path.samefile(self.files._results[0], self.a))

    def test_slow_legacy_callback_stops_later_queries_without_losing_valid_hit(self):
        self.roots()
        called = []
        def legacy(query, root):
            called.append(root)
            self.clock.advance(11)
            return [self.a], 'Non cooperativo, già terminato'
        self.files.index = legacy
        result = self.search('preventivo')
        self.assertEqual(len(called), 1)
        self.assert_partial(result)
        self.assertEqual(len(result.listing['items']), 1)

    def test_callback_internal_type_error_is_not_retried(self):
        self.roots()
        calls = []
        def broken(query, root, **options):
            calls.append((query, root, options))
            raise TypeError('Internal adapter defect, not an unsupported argument')
        self.files.index = broken
        with self.assertRaisesRegex(TypeError, 'Internal adapter defect'):
            self.search()
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][2], {})

    def test_fallback_hit_is_kept_when_budget_expires_before_next_entry(self):
        self.roots(1)
        second = self.docs / 'secondo.txt'
        second.write_text('fixture', encoding='utf-8')
        with os.scandir(self.docs) as entries:
            by_name = {entry.name: entry for entry in entries}
        def index(query, root):
            self.clock.advance(6)
            return [], 'Indice vuoto della fixture'
        self.files.index = index
        clock = self.clock
        first_entry, next_entry = by_name[self.a.name], by_name[second.name]
        class Walk:
            def __enter__(self):
                def entries():
                    yield first_entry
                    clock.advance(4)
                    yield next_entry
                return entries()
            def __exit__(self, *args):
                return False
        with patch('file_access.service.os.scandir', return_value=Walk()) as walked:
            result = self.search('preventivo')
        self.assertEqual(walked.call_count, 1)
        self.assertEqual(result.listing['coverage']['scanned'], 1)
        self.assert_partial(result)
        self.assertFalse(result.listing['coverage']['index_results_only'])
        self.assertTrue(os.path.samefile(self.files._results[0], self.a))
        read = self.files.execute('read', {'target': '1'})
        self.assertEqual(read.status, 'completed', read.message)
        self.assertEqual(read.preview, 'Testo reale di esempio')

    def test_cancel_at_deadline_discards_late_index_hits(self):
        self.roots()
        def index(argv, **kw):
            self.clock.advance(10)
            self.files.cancelled.set()
            return self.reply([self.a])
        run = self.native(index)
        result = self.search('preventivo')
        self.assertEqual(run.call_count, 1)
        self.assertEqual(result.status, 'rejected')
        self.assertIsNone(result.listing)
        self.assertEqual(self.files._results, [])

    def test_revocation_at_deadline_discards_late_index_hits(self):
        self.roots()
        def index(argv, **kw):
            self.clock.advance(10)
            self.manager.set_enabled('accesso_file', False)
            return self.reply([self.a])
        run = self.native(index)
        result = self.search('preventivo')
        self.assertEqual(run.call_count, 1)
        self.assertEqual(result.status, 'rejected')
        self.assertEqual(self.files._results, [])

    def test_next_explicit_search_gets_new_budget_without_resetting_profile(self):
        self.roots(2)
        before = self.files.policy.path.read_bytes()
        def slow(argv, **kw):
            self.clock.advance(kw['timeout'])
            raise subprocess.TimeoutExpired(argv, kw['timeout'])
        run = self.native(slow)
        self.assert_partial(self.search())
        self.assertEqual([c.kwargs['timeout'] for c in run.call_args_list], [8, 2])
        run.side_effect = lambda *a, **kw: self.reply([self.a])
        run.reset_mock()
        result = self.search('preventivo')
        self.assertEqual(result.status, 'completed', result.message)
        self.assertEqual([c.kwargs['timeout'] for c in run.call_args_list], [8, 8])
        self.assertEqual(result.listing['coverage']['stop_reason'], 'index_coverage')
        self.assertEqual(self.files.policy.path.read_bytes(), before)

    def test_reincluded_child_remains_queryable_after_excluded_parent(self):
        child = self.hidden / 'Consentito'
        child.mkdir()
        target = child / 'preventivo.txt'
        target.write_text('allowed fixture', encoding='utf-8')
        self.files.policy.configure([(self.docs, True), (self.hidden, False), (child, True)])
        calls = []
        def index(argv, **kw):
            root = Path(json.loads(kw['input'])['root'])
            calls.append(root)
            return self.reply([target] if os.path.samefile(root, child) else [])
        self.native(index)
        result = self.search('preventivo')
        self.assertEqual(len(calls), 2)
        self.assertTrue(any(os.path.samefile(p, child) for p in calls))
        self.assertTrue(os.path.samefile(self.files._results[0], target))
        self.assertEqual(result.listing['coverage']['stop_reason'], 'index_coverage')
