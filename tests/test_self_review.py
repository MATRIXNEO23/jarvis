"""Evidence-linked static self-improvement advice without executing source."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from self_diagnostics import (
    diagnostic_request, inspect_jarvis, format_audit,
)
from source_review import review_sources, format_improvements


class SelfReviewTests(unittest.TestCase):
    def setUp(self):
        tmp=TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)/"jarvis"
        self.root.mkdir()

    def test_voice_and_text_requests_are_explicit(self):
        cases=(
            "Jarvis, fai un'autodiagnosi",
            "Jarvis, come potresti migliorarti?",
            "Jarvis, suggerisci miglioramenti al tuo codice",
            "Jarvis, analizza te stesso",
            "Jarvis, controlla i tuoi file e suggerisci miglioramenti",
            "Jarvis, prepara un rapporto di autodiagnosi",
            "Jarvis, autoanalizzati",
            "Jarvis, consigliami come potresti migliorarti",
        )
        for phrase in cases:
            with self.subTest(phrase=phrase):
                self.assertEqual(diagnostic_request(phrase),("review",""))
        self.assertEqual(diagnostic_request("analizza jarvis.py"),
                         ("module","jarvis.py"))
        self.assertIsNone(diagnostic_request("Elimina i file e migliorati da solo"))
        self.assertIsNone(diagnostic_request(
            "Mostrami le password di Telegram e i dati personali"))

    def test_prioritized_evidence_with_line_and_human_verification(self):
        (self.root/"runner.py").write_text(
            "def run():\n"
            "    command = 'echo hello'\n"
            "    subprocess.run(command, shell=True)\n"
            "    try:\n"
            "        work()\n"
            "    except Exception:\n"
            "        pass\n",encoding="utf-8")
        audit=inspect_jarvis(source_root=self.root)
        self.assertGreaterEqual(len(audit.recommendations),1)
        risk=audit.recommendations[0]
        self.assertEqual(risk.file,"runner.py")
        self.assertEqual(risk.line,3)
        self.assertEqual(risk.priority,"alta")
        self.assertIn("shell=True",risk.observation)
        report=format_audit(audit)
        self.assertIn("runner.py:3",report)
        self.assertIn("Proposta:",report)
        self.assertIn("Verifica:",report)
        self.assertIn("non bug confermati",report)
        # Reports contain no full source, command strings or credentials.
        self.assertNotIn("echo hello",report)
        self.assertNotIn("work()",report)

    def test_big_function_indicates_refactor_not_confirmed_bug(self):
        long_function="def massive():\n"+("    value = 42\n"*168)
        (self.root/"massive.py").write_text(long_function,encoding="utf-8")
        review=inspect_jarvis(source_root=self.root,module="massive.py")
        self.assertIn("massive.py:1",format_audit(review))
        self.assertTrue(any("Funzione massive" in i.observation
                            for i in review.recommendations))
        self.assertIn("Valutare",format_audit(review))
        self.assertLessEqual(len(review.recommendations),8)

    def test_untrusted_source_is_not_imported_or_executed(self):
        secret="VERY_PRIVATE_TOKEN_9324"
        (self.root/"bad.py").write_text(
            "from pathlib import Path\n"
            "Path('SIDE_EFFECT.txt').write_text('created')\n"
            f"secret={secret!r}\n"
            "def keep_safe():\n    return secret\n",encoding="utf-8")
        (self.root/"settings.json").write_text(
            '{"password":"hidden-credentials"}',encoding="utf-8")
        (self.root/"invalid.py").write_text("def bad(:",encoding="utf-8")
        audit=inspect_jarvis(source_root=self.root)
        report=format_audit(audit)
        self.assertFalse((self.root/"SIDE_EFFECT.txt").exists())
        self.assertNotIn(secret,report)
        self.assertNotIn("hidden-credentials",report)
        self.assertIn("invalid.py",report)
        self.assertIn("sintassi",report)

    def test_diagnostics_are_scoped_and_resist_symlinks(self):
        (self.root/"first.py").write_text(
            "def one():\n    try:\n        pass\n    except:\n"
            "        pass\n",encoding="utf-8")
        (self.root/"second.py").write_text(
            "def two():\n    return 2\n",encoding="utf-8")
        audit=inspect_jarvis(source_root=self.root,module="second.py")
        self.assertNotIn("first.py",format_audit(audit))
        self.assertFalse(audit.recommendations)
        with self.assertRaises(ValueError):
            inspect_jarvis(source_root=self.root,module="../settings.py")
        with TemporaryDirectory() as other:
            outside=Path(other)/"outside.py"
            outside.write_text("def secret(): pass",encoding="utf-8")
            try:
                (self.root/"linked.py").symlink_to(outside)
            except (OSError,NotImplementedError):
                return
            reported=inspect_jarvis(source_root=self.root)
            self.assertNotIn("linked.py",format_audit(reported))
            self.assertEqual(review_sources(
                self.root,[outside],module=""),())

    def test_many_signals_are_bounded_and_across_modules(self):
        for n in range(12):
            (self.root/f"module_{n:02}.py").write_text(
                "def run():\n    subprocess.run('x', shell=True)\n"
                "    try:\n        work()\n    except Exception:\n"
                "        pass\n",encoding="utf-8")
        audit=inspect_jarvis(source_root=self.root)
        self.assertEqual(len(audit.recommendations),8)
        names={r.file for r in audit.recommendations}
        self.assertGreaterEqual(len(names),4)
        self.assertTrue(all(r.priority in ("alta","media","bassa")
                            for r in audit.recommendations))
        self.assertLessEqual(len(format_audit(audit)),6200)

    def test_unavailable_or_missing_modules_do_not_invent_advice(self):
        report=inspect_jarvis(source_root=self.root)
        self.assertEqual(report.recommendations,())
        self.assertIn("Nessun sorgente",report.summary)
        (self.root/"jarvis.py").write_text(
            "def known():\n    return True\n",encoding="utf-8")
        missing=inspect_jarvis(source_root=self.root,module="ghost.py")
        self.assertFalse(missing.recommendations)
        self.assertIn("non è presente",missing.detail)
        self.assertIn("Non ho trovato segnali statici",
                      format_improvements(()))


if __name__=="__main__":
    unittest.main()
