"""Windows TTS lifecycle with real owned child/pipes, silent Python helper.

The fixed PowerShell argv is intercepted at Popen, replacing only the child
program with a temporary deterministic fixture. No SAPI sound or user data.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from offline_tts import OfflineSpeaker, installed_voices


@unittest.skipUnless(os.name == 'nt', 'Windows-only project requirement')
class TtsProcessLifecycleTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='jarvis-tts-owned-')
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name).resolve()
        self.helper = self.folder / 'silent_helper.py'
        self.helper.write_text(
            'import json,sys,time\nfrom pathlib import Path\n'
            'data=json.loads(sys.stdin.buffer.read().decode("utf-8"))\n'
            'Path(sys.argv[1]).write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")\n'
            'if sys.argv[2]=="hold": time.sleep(15)\n'
            'if sys.argv[2]=="fail": sys.exit(3)\n'
            'if data["mode"]=="list": print(json.dumps(["Fixture Voce"]))\n',
            encoding='utf-8')
        self.real_popen = subprocess.Popen
        self.children, self.others, self.players, self.launches = [], [], [], []
        self.mode = 'hold'
        self.pause_publication = False
        self.short_timeout = False
        self.fail_launch = False
        self.created, self.resume = threading.Event(), threading.Event()
        self.enterContext(patch('offline_tts.subprocess.Popen', side_effect=self.launch))
        self.addCleanup(self.cleanup)

    @staticmethod
    def wait_for(predicate, timeout=3):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return True
            threading.Event().wait(0.01)
        return bool(predicate())

    def launch(self, argv, **options):
        self.launches.append((argv, dict(options)))
        if self.fail_launch:
            raise OSError('Controlled process creation failure')
        marker = self.folder / ('payload-' + str(len(self.children)) + '.json')
        child_type = self.real_popen
        if self.short_timeout:
            class ShortProcess(child_type):
                def communicate(self, input=None, timeout=None):
                    return super().communicate(input=input, timeout=0.15 if timeout is not None else None)
            child_type = ShortProcess
        child = child_type([sys.executable, '-u', str(self.helper), str(marker), self.mode], **options)
        child.marker = marker
        self.children.append(child)
        self.created.set()
        if self.pause_publication and not self.resume.wait(5):
            child.terminate()
            raise OSError('Fixture publication gate timed out')
        return child

    def player(self, **options):
        errors = []
        player = OfflineSpeaker(notify_error=errors.append, **options)
        self.players.append(player)
        return player, errors

    def active(self, text='Voce temporanea', **options):
        player, errors = self.player(**options)
        self.assertTrue(player.speak(text, 'Voce fixture'))
        self.assertTrue(self.created.wait(3), 'No helper was created')
        child = self.children[0]
        self.assertTrue(self.wait_for(child.marker.exists, 5), 'Helper did not consume JSON')
        self.assertTrue(player.is_speaking())
        return player, child, errors

    def joined(self, player):
        worker = player._worker
        if worker is not None:
            worker.join(3)
            self.assertFalse(worker.is_alive(), 'TTS worker survived close')

    def assert_pipes_closed(self, child):
        self.assertIsNotNone(child.poll(), 'Owned child survived cleanup')
        for stream in (child.stdin, child.stdout, child.stderr):
            if stream is not None:
                self.assertTrue(stream.closed)

    def cleanup(self):
        self.resume.set()
        for player in self.players:
            player.close()
        # Release even on the pre-fix Red path; never leak test children.
        for child in self.children + self.others:
            if child.poll() is None:
                child.terminate()
            child.wait(5)
        for player in self.players:
            self.joined(player)
        for child in self.others:
            for stream in (child.stdin, child.stdout, child.stderr):
                if stream is not None:
                    stream.close()

    def test_close_stops_the_active_default_helper_and_releases_its_pipes(self):
        player, child, errors = self.active()
        player.close()
        self.assertTrue(self.wait_for(lambda: child.poll() is not None, 2), 'close left native helper alive')
        self.joined(player)
        self.assert_pipes_closed(child)
        self.assertFalse(player.is_speaking())
        self.assertTrue(player.is_audible(), 'Preserve anti-echo cooldown after interrupted speech')
        self.assertEqual(errors, [])
        self.assertFalse(player.speak('Dopo chiusura'))

    def test_close_discards_pending_chunks_and_queued_messages(self):
        player, child, errors = self.active('Parola con spazio. ' * 140)
        self.assertTrue(player.speak('Secondo messaggio in coda'))
        self.assertTrue(player.speak('Terzo messaggio in coda'))
        payload = json.loads(child.marker.read_text(encoding='utf-8'))
        self.assertLessEqual(len(payload['text']), 600)
        player.close()
        self.joined(player)
        self.assertEqual(len(self.children), 1)
        self.assert_pipes_closed(child)
        self.assertEqual(errors, [])

    def test_close_before_process_publication_prevents_sending_speech_text(self):
        self.pause_publication = True
        player, errors = self.player()
        self.assertTrue(player.speak('Non inviare al helper dopo close'))
        self.assertTrue(self.created.wait(3))
        child = self.children[0]
        player.close()
        self.resume.set()
        self.joined(player)
        self.assertIsNotNone(child.poll())
        self.assertFalse(child.marker.exists(), 'Closed owner still delivered speech payload')
        self.assert_pipes_closed(child)
        self.assertEqual(errors, [])

    def test_repeated_close_does_not_terminate_the_same_live_handle_twice(self):
        player, child, errors = self.active()
        with patch.object(child, 'terminate', wraps=child.terminate) as terminate:
            player.close()
            player.close()
            self.joined(player)
        self.assertEqual(terminate.call_count, 1)
        self.assert_pipes_closed(child)
        self.assertEqual(errors, [])

    def test_already_completed_helper_can_be_closed_without_another_termination(self):
        self.mode = 'exit'
        player, errors = self.player()
        self.assertTrue(player.speak('Completa'))
        self.assertTrue(self.created.wait(3))
        child = self.children[0]
        self.assertTrue(self.wait_for(lambda: child.poll() is not None))
        self.assertTrue(self.wait_for(lambda: not player.is_speaking()))
        with patch.object(child, 'terminate', wraps=child.terminate) as terminate:
            player.close()
            self.joined(player)
        terminate.assert_not_called()
        self.assert_pipes_closed(child)
        self.assertEqual(errors, [])

    def test_close_does_not_touch_an_independent_process(self):
        other = self.real_popen([sys.executable, '-c', 'import time; time.sleep(20)'],
                                creationflags=subprocess.CREATE_NO_WINDOW)
        self.others.append(other)
        player, child, _ = self.active()
        player.close()
        self.joined(player)
        self.assertIsNone(other.poll(), 'A process not owned by the speaker was touched')
        self.assertIsNotNone(child.poll())

    def test_payload_stays_json_on_stdin_with_fixed_powershell_argv_and_cwd(self):
        text = 'Città; $(Remove-Item) & "quote" è soltanto testo'
        player, child, _ = self.active(text)
        argv, options = self.launches[0]
        system_root = os.environ['SystemRoot']
        self.assertEqual(Path(argv[0]), Path(system_root) / 'System32/WindowsPowerShell/v1.0/powershell.exe')
        self.assertIn('-EncodedCommand', argv)
        self.assertNotIn(text, ' '.join(argv))
        self.assertFalse(options.get('shell', False))
        self.assertEqual(options['cwd'], system_root)
        self.assertEqual(json.loads(child.marker.read_text(encoding='utf-8')),
                         {'mode': 'speak', 'text': text, 'voice': 'Voce fixture'})
        player.close()
        self.joined(player)

    def test_helper_timeout_keeps_existing_finite_cleanup_and_error_feedback(self):
        self.short_timeout = True
        player, errors = self.player()
        self.assertTrue(player.speak('Scadenza helper'))
        self.assertTrue(self.created.wait(3))
        child = self.children[0]
        self.assertTrue(self.wait_for(lambda: bool(errors), 3))
        self.assertTrue(self.wait_for(lambda: not player.is_speaking()))
        player.close()
        self.joined(player)
        self.assert_pipes_closed(child)
        self.assertEqual(len(errors), 1)

    def test_nonzero_helper_exit_reports_one_error_and_releases_resources(self):
        self.mode = 'fail'
        player, errors = self.player()
        self.assertTrue(player.speak('Errore helper'))
        self.assertTrue(self.created.wait(3))
        self.assertTrue(self.wait_for(lambda: bool(errors)))
        self.assertTrue(self.wait_for(lambda: not player.is_speaking()))
        player.close()
        self.joined(player)
        self.assertEqual(len(errors), 1)
        self.assert_pipes_closed(self.children[0])

    def test_process_creation_failure_does_not_leave_busy_or_break_close(self):
        self.fail_launch = True
        player, errors = self.player()
        self.assertTrue(player.speak('Errore avvio'))
        self.assertTrue(self.wait_for(lambda: bool(errors)))
        self.assertTrue(self.wait_for(lambda: not player.is_speaking()))
        player.close()
        self.joined(player)
        self.assertEqual(self.children, [])
        self.assertEqual(len(errors), 1)

    def test_custom_two_argument_runner_remains_compatible_and_is_not_force_stopped(self):
        entered, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)
        calls = []
        def runner(payload, *, timeout):
            calls.append((payload, timeout))
            entered.set()
            if not release.wait(5):
                raise OSError('Fixture custom runner release timed out')
            return ''
        player, errors = self.player(runner=runner)
        self.assertTrue(player.speak('Runner custom', 'Fixture'))
        self.assertTrue(entered.wait(2))
        player.close()
        self.assertTrue(player.is_speaking(), 'Do not claim uncooperative callable already exited')
        release.set()
        self.joined(player)
        self.assertEqual(calls, [({'mode': 'speak', 'text': 'Runner custom', 'voice': 'Fixture'}, 90)])
        self.assertFalse(player.is_speaking())
        self.assertTrue(player.is_audible())
        self.assertEqual(self.children, [])
        self.assertEqual(errors, [])

    def test_installed_voices_keeps_existing_finite_runner_contract(self):
        self.mode = 'exit'
        self.assertEqual(installed_voices(), ['Fixture Voce'])
        self.assertEqual(json.loads(self.children[0].marker.read_text(encoding='utf-8')), {'mode': 'list'})
        self.assert_pipes_closed(self.children[0])

    def test_idle_close_never_launches_a_process(self):
        player, errors = self.player()
        player.close()
        player.close()
        self.assertFalse(player.speak('Non parte'))
        self.assertEqual(self.launches, [])
        self.assertEqual(errors, [])
