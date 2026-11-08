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

    def test_natural_combined_requests_never_fall_back_to_gpt(self):
        # Regression from the real Windows test: user asked for an
        # autodiagnosis *and* possible fixes, but GPT replied that it could
        # not read Jarvis's code or logs. The local AST reviewer can.
        direct=(
            "Jarvis, fai un'autodiagnosi del tuo funzionamento e proponi eventuali fix",
            "Jarvis, fatti un'autodiagnosi del tuo funzionamento e proponi eventuali fix",
            "Esegui una diagnosi del tuo codice e suggerisci possibili correzioni",
            "Jarvis, analizza il tuo funzionamento e proponi dei miglioramenti",
            "Jarvis, controlla i tuoi file e suggerisci eventuali fix",
            "Jarvis, puoi fare un'autodiagnosi del tuo funzionamento e suggerisci soluzioni?",
            "Jarvis, fai un'autodiagnosi del tuo funzionamento e proponi eventuali fix.",
        )
        for request in direct:
            with self.subTest(request=request):
                self.assertEqual(diagnostic_request(request),("review",""))
        unrelated=(
            "Non fare un'autodiagnosi",
            "Domani fai un'autodiagnosi",
            "Mi hai detto che avevi fatto un'autodiagnosi",
            "Jarvis, elimina i file e fai un'autodiagnosi",
            "Jarvis, come va? Non ho accesso al codice e ai log",
        )
        for request in unrelated:
            with self.subTest(request=request):
                self.assertIsNone(diagnostic_request(request))

    def test_model_entrypoints_keep_explicit_local_diagnostics_first(self):
        # Inspect the GUI source, do not import it or start Tk/GPT.
        source=(Path(__file__).resolve().parent.parent/"jarvis.py"
                ).read_text(encoding="utf-8")
        start=source.split("    def start_conversation_gpt(spoken: str) -> None:",1)[1]
        start=start.split("    def toggle_gpt(",1)[0]
        self.assertLess(start.index("try_self_diagnostic(spoken)"),
                        start.index("submit_gemma_voice(spoken)"))
        self.assertLess(start.index("try_self_diagnostic(spoken)"), start.index("run_gpt("))
        ask=source.split("    def submit_gpt() -> None:",1)[1]
        ask=ask.split("    def poll() -> None:",1)[0]
        self.assertLess(ask.index("try_self_diagnostic(message)"),
                        ask.index('run_gpt("ask"'))
        self.assertLess(ask.index("try_self_diagnostic(message)"),
                        ask.index("not gpt_enabled.get()"))
        self.assertIn('text="Autodiagnosi Jarvis"',source)
        self.assertIn("diagnostic_button.configure(",source)
        self.assertIn("command=lambda: try_self_diagnostic(",source)
        self.assertIn('if try_self_diagnostic(message):',source)

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
        self.assertFalse((self.root/"ghost.py").exists())
        self.assertIn("sorgenti accessibili",missing.detail)
        self.assertIn("inventario",missing.summary)
        self.assertIn("Non ho trovato segnali statici",
                      format_improvements(()))


if __name__=="__main__":
    unittest.main()
