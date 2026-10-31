"""Only opt-in, scrubbed local diagnostic evidence may reach external GPT."""
import json
from pathlib import Path
import unittest

from diagnostic_handoff import (build_external_review_prompt,
                                is_external_review_request,
                                safe_audit_payload,wants_external_advice)
from self_diagnostics import SourceAudit
from source_review import Improvement


def sample_audit():
    return SourceAudit(
        "C:\\Users\\private\\Jarvis; trovato password=donotshare",
        "Cartella C:\\Users\\private\\Jarvis e Telegram API_HASH=secret",
        ("passphrase old-value",),
        (Improvement(
            "alta", "source_review.py", 56,
            "Una chiamata usa shell=True.",
            "Verificare se una shell è indispensabile.",
            "Revisionare i parametri in un test isolato."
        ),)
    )


class DiagnosticHandoffTests(unittest.TestCase):
    def test_explicit_review_request_without_guessing_other_chat(self):
        for text in (
            "Jarvis, valuta la diagnosi con GPT",
            "valuta l'autodiagnosi con ChatGPT",
            "analizza il rapporto usando il modello esterno",
            "Jarvis, esamina la diagnosi tramite gpt",
        ):
            with self.subTest(text=text):
                self.assertTrue(is_external_review_request(text))
        for text in (
            "Non valutare la diagnosi con GPT",
            "Domani valuta la diagnosi con GPT",
            "Sposta i documenti e valuta la diagnosi con GPT",
            "Fammi un saluto",
        ):
            with self.subTest(text=text):
                self.assertFalse(is_external_review_request(text))
        self.assertTrue(wants_external_advice(
            "fai un'autodiagnosi e proponi eventuali fix"))
        self.assertFalse(wants_external_advice("fai un'autodiagnosi"))

    def test_payload_never_forwards_local_paths_or_private_source(self):
        audit=sample_audit()
        data=safe_audit_payload(audit,{"gpt_bridge":"available",
                                       "voice_engine":"available"})
        self.assertTrue(data["analysis_only"])
        self.assertFalse(data["sources_executed"])
        self.assertFalse(data["runtime_logs_read"])
        self.assertFalse(data["functional_tests_performed"])
        self.assertEqual(data["issues"][0]["file"],"source_review.py")
        self.assertEqual(data["issues"][0]["line"],56)
        self.assertEqual(data["runtime"]["projects"],"not_tested")
        text=build_external_review_prompt(audit)
        for secret in ("C:\\Users", "API_HASH", "donotshare",
                       "old-value", "private", "password="):
            self.assertNotIn(secret,text)
        self.assertIn("non",text.casefold())
        self.assertIn("file",text.casefold())
        self.assertLessEqual(len(text),4800)
        self.assertTrue(text.endswith("}"))
        payload=json.loads(text.split("DATI_DIAGNOSTICI_JSON:\n",1)[1])
        self.assertEqual(payload["issues"][0]["file"],"source_review.py")

    def test_absolute_paths_and_unsafe_filenames_are_not_sent(self):
        bad=SourceAudit("x","y",(),(
            Improvement("media","C:\\Users\\Someone\\Desktop\\secret.py",1,
                        "Funzione lunga", "Separare responsabilità.",
                        "Aggiungere test."),
            Improvement("media","../secrets.py",2,
                        "Modulo complesso", "Revisionare.", "Provare."),
        ))
        payload=safe_audit_payload(bad)
        self.assertEqual([x["file"] for x in payload["issues"]],
                         ["[file non condiviso]","[file non condiviso]"])

    def test_long_reviews_are_bounded_and_no_raw_source(self):
        audit=SourceAudit("x","y",(),tuple(
            Improvement("alta","module_%d.py"%n,n,
                        "Segnale statico molto lungo "+("c"*500),
                        "Suggerimento "+("d"*1200),
                        "Verifica "+("e"*1000))
            for n in range(40)
        ))
        prompt=build_external_review_prompt(audit)
        self.assertLessEqual(len(prompt),4800)
        payload=json.loads(prompt.split("DATI_DIAGNOSTICI_JSON:\n",1)[1])
        self.assertLessEqual(len(payload["issues"]),6)
        self.assertNotIn("d"*300,prompt)
        self.assertIn("nessun comando",prompt.casefold())

    def test_no_gpt_without_consent_and_no_callable_tools_in_report(self):
        # GUI branch is inspected only; not imported or executed in tests.
        src=(Path(__file__).resolve().parent.parent/"jarvis.py"
             ).read_text(encoding="utf-8")
        block=src.split("    def offer_external_diagnostic_review() -> bool:",1)[1]
        block=block.split("    def try_self_diagnostic(",1)[0]
        self.assertIn("messagebox.askyesno(",block)
        self.assertLess(block.index("messagebox.askyesno("),
                        block.index('run_gpt("ask"'))
        self.assertIn("if not approved:",block)
        self.assertIn("build_external_review_prompt(",block)
        self.assertNotIn("submit_local(",block)
        self.assertNotIn("open(",block)
        self.assertIn("if pending_external_review:",src)
        self.assertIn("last_diagnostic_audit=audit",src)


if __name__=="__main__":
    unittest.main()
