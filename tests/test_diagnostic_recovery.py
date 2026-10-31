"""The local audit must be observable, bounded and recoverable without GPT."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from diagnostic_session import DiagnosticSession
from self_diagnostics import inspect_jarvis, diagnostic_request


class FakeClock:
    def __init__(self):
        self.value=100.0
    def __call__(self):
        return self.value
    def advance(self,seconds):
        self.value+=seconds


class DiagnosticSessionTests(unittest.TestCase):
    def setUp(self):
        self.clock=FakeClock()
        self.session=DiagnosticSession(clock=self.clock,
                                       stall_seconds=12,timeout_seconds=120)

    def test_visible_progress_and_regular_completion(self):
        run=self.session.start()
        self.assertEqual(run,1)
        self.assertTrue(self.session.active)
        self.assertIsNone(self.session.start())
        self.assertTrue(self.session.progress(run,"inventario",8,8))
        self.assertTrue(self.session.progress(run,"sintassi",3,8))
        snapshot=self.session.snapshot()
        self.assertEqual(snapshot.phase,"sintassi")
        self.assertEqual((snapshot.completed,snapshot.total),(3,8))
        self.assertEqual(snapshot.progress_percent,38)
        self.clock.advance(5)
        self.assertEqual(self.session.check(),"")
        self.assertTrue(self.session.progress(run,"consigli",7,8))
        self.assertEqual(self.session.snapshot().progress_percent,88)
        self.assertTrue(self.session.finish(run,succeeded=True))
        self.assertEqual(self.session.snapshot().phase,"completata")
        self.assertEqual(self.session.snapshot().progress_percent,100)
        self.assertFalse(self.session.active)

    def test_no_progress_triggers_one_warning_then_timeout_unlocks(self):
        old=self.session.start()
        self.clock.advance(13)
        self.assertEqual(self.session.check(),"stalled")
        self.assertEqual(self.session.check(),"")
        self.assertTrue(self.session.active)
        self.clock.advance(107)
        self.assertEqual(self.session.check(),"timeout")
        self.assertFalse(self.session.active)
        self.assertEqual(self.session.snapshot().phase,"tempo esaurito")
        self.assertEqual(self.session.check(),"")
        new=self.session.start()
        self.assertNotEqual(old,new)
        self.assertFalse(self.session.progress(old,"completamento",1,1))
        self.assertFalse(self.session.finish(old,succeeded=True))
        self.assertEqual(self.session.current_id,new)
        self.assertTrue(self.session.finish(new,succeeded=False))
        self.assertEqual(self.session.snapshot().phase,"errore")

    def test_user_cancel_releases_ui_but_does_not_accept_late_results(self):
        old=self.session.start()
        self.assertEqual(self.session.cancel(),old)
        self.assertEqual(self.session.snapshot().phase,"annullata")
        self.assertIsNone(self.session.cancel())
        another=self.session.start()
        self.assertNotEqual(old,another)
        self.assertFalse(self.session.progress(old,"completamento",1,1))
        self.assertFalse(self.session.finish(old,succeeded=True))
        self.assertTrue(self.session.active)
        self.assertTrue(self.session.finish(another,succeeded=True))

    def test_new_progress_resets_stall_warning(self):
        run=self.session.start()
        self.clock.advance(12)
        self.assertEqual(self.session.check(),"stalled")
        self.assertTrue(self.session.progress(run,"sintassi",2,6))
        self.clock.advance(11)
        self.assertEqual(self.session.check(),"")
        self.clock.advance(1)
        self.assertEqual(self.session.check(),"stalled")

    def test_never_accept_invalid_or_unrelated_progress(self):
        run=self.session.start()
        self.assertFalse(self.session.progress(run+1,"sintassi",99,99))
        self.assertFalse(self.session.progress(run,"password",1,1))
        self.assertTrue(self.session.progress(run,"sintassi",99,3))
        self.assertEqual(self.session.snapshot().completed,3)
        self.assertFalse(self.session.finish(run+1,succeeded=True))
        self.assertTrue(self.session.active)


class LocalAuditProgressTests(unittest.TestCase):
    def test_reports_real_phases_with_no_execution(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"jarvis.py").write_text(
                "from pathlib import Path\n"
                "def never_run():\n"
                "    Path('SIDE_EFFECT').write_text('bad')\n",
                encoding="utf-8")
            (root/"tests").mkdir()
            (root/"tests"/"test_basic.py").write_text(
                "def test_ok():\n    assert True\n",encoding="utf-8")
            progress=[]
            audit=inspect_jarvis(source_root=root,
                                 progress=lambda phase,n,total:
                                 progress.append((phase,n,total)))
            self.assertEqual(audit.summary.split(" file sorgente")[0],"2")
            self.assertFalse((root/"SIDE_EFFECT").exists())
            self.assertTrue(progress)
            self.assertIn(("inventario",2,2),progress)
            self.assertIn(("sintassi",2,2),progress)
            self.assertIn(("consigli",2,2),progress)
            self.assertIn(("completamento",1,1),progress)

    def test_recognizes_italian_speech_recognition_variants(self):
        phrases=(
            "Jarvis fai un'auto diagnosi",
            "Jarvis, fammi l'autodiagnosi",
            "Jarvis fai una auto diagnosi",
            "Jarvis esegui una auto-diagnosi del tuo codice",
            "Jarvis, fai un'auto diagnosi del tuo funzionamento e proponi eventuali fix",
            "Jarvis, fai l'autodiagnosi del tuo funzionamento e suggerisci correzioni",
        )
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                self.assertIsNotNone(diagnostic_request(phrase))
        for negative in (
            "Jarvis non fare un'auto diagnosi",
            "Domani fai un'auto diagnosi",
            "Mi hai chiesto di fare un'auto diagnosi",
        ):
            with self.subTest(negative=negative):
                self.assertIsNone(diagnostic_request(negative))

    def test_all_voice_and_button_paths_are_handled_locally(self):
        src=(Path(__file__).resolve().parent.parent/"jarvis.py"
             ).read_text(encoding="utf-8")
        self.assertIn('text="Autodiagnosi Jarvis"',src)
        self.assertIn('diagnostic_status = tk.StringVar',src)
        self.assertIn('diagnostic_percent = tk.IntVar',src)
        # Visual-only change: keep a working cancel button, but use a tiny
        # glyph and show progress only while a diagnosis really runs.
        self.assertIn('diagnostic_row,text="×"',src)
        self.assertIn("diagnostic_row.pack_forget()",src)
        self.assertNotIn("ttk.Progressbar(diagnostic_row",src)
        self.assertIn("diagnostic_cancel_button.configure(command=cancel_diagnostic)",src)
        self.assertIn("diagnostic_session.cancel()",src)
        self.assertIn("diagnostic_session.check()",src)
        heartbeat=src.split("    def diagnostic_heartbeat() -> None:",1)[1]
        heartbeat=heartbeat.split("    def poll() -> None:",1)[0]
        self.assertLess(heartbeat.index("root.after(800,diagnostic_heartbeat)"),
                        heartbeat.index("diagnostic_session.check()"))
        self.assertIn("root.after(800, diagnostic_heartbeat)",src)
        poll=src.split("    def poll() -> None:",1)[1]
        poll=poll.split("    def toggle_hud_microphone() -> None:",1)[0]
        self.assertLess(poll.index("root.after(120, poll)"),
                        poll.index("output_queue.get_nowait()"))
        self.assertIn('elif kind == "self_audit_error":',src)
        self.assertIn("except Exception as exc:",src)
        self.assertIn('run_id,phase,completed,total=data',src)
        self.assertIn('if not diagnostic_session.finish(run_id,succeeded=True):',src)
        voice=src.split('elif kind == "voice_text":',1)[1]
        convo=voice.split('if voice_mode.get() == GPT_CONVERSATION:',1)[1]
        self.assertLess(convo.index("try_self_diagnostic(spoken)"),
                        convo.index('if save_only_waiting:'))
        self.assertLess(convo.index("try_self_diagnostic(spoken)"),
                        convo.index('start_conversation_gpt(spoken)'))


if __name__=="__main__":
    unittest.main()
