"""052 punto 5: script e codice vanno sempre ai servizi online, mai a Gemma."""
import ast
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from online import servizi_online
ROOT = Path(__file__).resolve().parents[1]


def _submit_gemma_voice(d):
    source = (ROOT / "local_model" / "conversazione_lumi.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(source))
              if isinstance(n, ast.FunctionDef) and n.name == "submit_gemma_voice")
    env = {"d": d, "re": __import__("re"), "get_gemma_session": mock.Mock(
        side_effect=AssertionError("Gemma non deve partire per il codice"))}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "submit_gemma_voice", "exec"), env)
    return env["submit_gemma_voice"]


class CodeRequestTests(unittest.TestCase):
    def test_detects_code_requests_and_ignores_other_writing(self):
        for text in ("scrivi uno script python che rinomina i file",
                     "Lumi, scrivimi del codice per ordinare una lista",
                     "fammi un programma in powershell", "crea un nuovo script",
                     "scrivi una funzione che somma due numeri"):
            self.assertTrue(servizi_online.richiesta_codice(text), text)
        for text in ("scrivi una lettera a mia madre", "apri il programma", "che tempo fa",
                     "spiegami cos'è uno script"):
            self.assertFalse(servizi_online.richiesta_codice(text), text)

    def test_without_online_service_lumi_answers_briefly_and_never_uses_gemma(self):
        lines, spoken = [], []
        d = SimpleNamespace(closing=False, gemma_trial_busy=[False],
                            write_line=lines.append, speak_result=spoken.append)
        submit = _submit_gemma_voice(d)
        with mock.patch("intent_normalizer.before_model", return_value=False), \
                mock.patch("richiamo.risposta_di_lumi", return_value=None), \
                mock.patch.object(servizi_online, "percorso", lambda s, r=None: ("locale", s)), \
                mock.patch.object(servizi_online, "disponibili", return_value=False):
            self.assertTrue(submit("scrivi uno script python che rinomina i file", typed=True))
        self.assertEqual(len(spoken), 1)
        self.assertIn("serve un servizio online", spoken[0])
        self.assertTrue(any(line.startswith("ONLINE >") for line in lines))

    def test_failed_online_for_code_does_not_fall_back_to_local_model(self):
        source = (ROOT / "local_model" / "conversazione_lumi.py").read_text(encoding="utf-8")
        self.assertIn('if not local_ok or __import__("online").servizi_online.richiesta_codice(spoken):',
                      source)


if __name__ == "__main__":
    unittest.main()
