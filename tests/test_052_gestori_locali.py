"""052: gestori locali e risposte senza «Lumi».

Prove con trascrizioni simulate e funzioni reali di jarvis.py estratte dal sorgente (AST):
non provano il microfono né l'interfaccia Windows reale.
"""
import ast
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import lumi_comandi
import risposte
from voice_control import WakeWordGate

ROOT = Path(__file__).resolve().parents[1]


def _main_body():
    tree = ast.parse((ROOT / "jarvis.py").read_text(encoding="utf-8"))
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main").body


def _preference_command(env):
    """preference_command reale, con pending_preference come variabile di chiusura."""
    fn = next(n for n in _main_body() if isinstance(n, ast.FunctionDef)
              and n.name == "preference_command")
    outer = ast.parse("def outer():\n    pending_preference = None\n").body[0]
    outer.body.append(ast.parse("def pending():\n    return pending_preference\n").body[0])
    outer.body.append(fn)
    outer.body.append(ast.Return(value=ast.Tuple(
        elts=[ast.Name(id="preference_command", ctx=ast.Load()),
              ast.Name(id="pending", ctx=ast.Load())], ctx=ast.Load())))
    module = ast.fix_missing_locations(ast.Module(body=[outer], type_ignores=[]))
    exec(compile(module, "jarvis-preference-command", "exec"), env)
    return env["outer"]()


class LocalCloseResultsTests(unittest.TestCase):
    def setUp(self):
        self.saved = dict(lumi_comandi._STATE)
        self.calls = []
        lumi_comandi.register({"close_results": lambda: self.calls.append("risultati"),
                               "close": lambda: self.calls.append("LUMI CHIUSA")},
                              lambda: False)

    def tearDown(self):
        lumi_comandi._STATE.update(self.saved)

    def test_short_variants_are_handled_locally_and_never_close_lumi(self):
        for text in ("chiudi i risultati", "Lumi, chiudi i risultati", "chiudi risultati",
                     "chiudi la finestra dei risultati", "chiudi la finestra risultati",
                     "togli i risultati", "nascondi i risultati", "chiudi l'elenco"):
            self.calls.clear()
            self.assertTrue(lumi_comandi.handle_text(text, lambda *_: None, lambda *_: None), text)
            self.assertEqual(self.calls, ["risultati"], text)

    def test_other_close_commands_are_not_taken(self):
        for text in ("chiudi la finestra", "chiudi il browser", "chiudi i programmi"):
            self.assertFalse(lumi_comandi.handle_text(text, lambda *_: None, lambda *_: None), text)
        self.assertEqual(self.calls, [])

    def test_local_handler_runs_before_any_model_in_the_entry_point(self):
        source = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        start = source.index("    def try_timer_command(spoken: str) -> bool:")
        first_call = source[start:start + 700]
        self.assertIn("lumi_handle_text(spoken, write_line, speak_result)", first_call)
        submit = source.index("    def submit_local(", start)
        self.assertIn("try_timer_command(proposed)", source[submit:submit + 900])

    def test_results_window_close_only_destroys_the_results_view(self):
        from file_access.ui import chiudi_risultati
        window = mock.Mock()
        window.winfo_exists.return_value = True
        window.state.return_value = "normal"
        parent = SimpleNamespace(_jarvis_file_results=SimpleNamespace(window=window))
        self.assertTrue(chiudi_risultati(parent))
        window.destroy.assert_called_once()
        self.assertIsNone(parent._jarvis_file_results)
        self.assertFalse(chiudi_risultati(parent))                 # già chiusa: nessun errore
        self.assertFalse(chiudi_risultati(SimpleNamespace()))      # mai aperta


class TiGuidoTests(unittest.TestCase):
    def setUp(self):
        assign = next(n for n in ast.walk(ast.Module(body=_main_body(), type_ignores=[]))
                      if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Attribute)
                      and n.targets[0].attr == "on_handled")
        self.box = mock.Mock()
        self.service = SimpleNamespace(pending=None, current_mode=lambda: "finestre")
        env = {"pc_service": self.service, "pc_help_box": self.box, "pc_overlay": mock.Mock(),
               "root": mock.Mock(), "write_line": lambda *_: None, "speak_result": lambda *_: None}
        self.handler = eval(compile(ast.Expression(body=assign.value), "on_handled", "eval"), env)

    def test_no_offer_while_pc_service_waits_for_yes_no(self):
        self.service.pending = (0, "close|x", False, "Chiudo Blocco note", lambda: "ok")
        self.assertIsNone(self.handler("close"))
        self.box.dopo_comando.assert_not_called()

    def test_offer_available_again_once_the_answer_is_given(self):
        self.service.pending = None
        self.handler("close")
        self.box.dopo_comando.assert_called_once()
        self.assertEqual(self.box.dopo_comando.call_args.args[0], "finestre")
        self.assertEqual(self.box.dopo_comando.call_args.kwargs["action"], "close")


class PreferenceConfirmationTests(unittest.TestCase):
    def setUp(self):
        import sqlite3
        from dialogue_focus import normalized_utterance
        from memory_boundaries import MemoryBoundaryError, PreferenceStore
        from preference_voice import parse_preference_intent
        risposte.done()
        self.addCleanup(risposte.done)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "preferenze.sqlite3"
        self.lines, self.spoken = [], []
        env = {"normalized_utterance": normalized_utterance,
               "parse_preference_intent": parse_preference_intent,
               "preference_store": PreferenceStore(self.db), "sqlite3": sqlite3,
               "MemoryBoundaryError": MemoryBoundaryError,
               "write_line": self.lines.append, "speak_result": self.spoken.append}
        self.store = env["preference_store"]
        self.command, self.pending = _preference_command(env)

    def saved(self):
        return {p["key"]: p["value"] for p in self.store.all()}

    def test_yes_confirms_and_saves_in_the_database(self):
        self.assertTrue(self.command("Lumi, ricordati che preferisco risposte brevi"))
        self.assertIsNotNone(self.pending())
        self.assertIn("risposte brevi", self.lines[-1])           # parole semplici, non la chiave
        self.assertNotIn("response_length", self.lines[-1])
        self.assertEqual(self.saved(), {})                         # niente salvato prima del sì
        self.assertTrue(risposte.waiting())                        # il «sì» vale senza «Lumi»
        self.assertTrue(self.command("sì"))
        self.assertIsNone(self.pending())
        self.assertEqual(self.saved(), {"response_length": "brief"})
        # Dopo un nuovo avvio (nuovo oggetto sullo stesso file) la scelta c'è ancora.
        from memory_boundaries import PreferenceStore
        self.assertEqual(PreferenceStore(self.db).all()[0]["value"], "brief")

    def test_no_cancels_without_saving(self):
        self.command("ricorda che preferisco il testo")
        self.assertTrue(self.command("no"))
        self.assertIsNone(self.pending())
        self.assertEqual(self.saved(), {})
        self.assertIn("non salvata", self.lines[-1])
        self.assertFalse(self.command("sì"))                       # il consenso è già chiuso
        self.assertEqual(self.saved(), {})

    def test_new_request_replaces_the_old_consent(self):
        self.command("ricorda che preferisco risposte brevi")
        self.command("ricorda che preferisco risposte in inglese")
        self.command("sì")
        self.assertEqual(self.saved(), {"language": "en"})


class NumberedChoiceTests(unittest.TestCase):
    def setUp(self):
        risposte.done()
        risposte.choice_done()
        self.addCleanup(risposte.choice_done)
        self.addCleanup(risposte.done)
        self.chosen, self.cancelled = [], []

    def expect(self, count=3, seconds=60.0):
        risposte.expect_choice(count, self.chosen.append,
                               on_cancel=lambda: self.cancelled.append(True), seconds=seconds)

    def test_numbers_words_and_ordinals_choose_without_lumi(self):
        for text, number in (("2", 2), ("uno", 1), ("il secondo", 2), ("il 3", 3),
                             ("numero tre", 3), ("Lumi, due", 2)):
            self.chosen.clear()
            self.expect()
            self.assertTrue(risposte.answer_choice(text), text)
            self.assertEqual(self.chosen, [number], text)
            self.assertFalse(risposte.choice_waiting())            # una scelta sola

    def test_out_of_range_other_words_and_stop_are_not_taken(self):
        self.expect(count=2)
        for text in ("il terzo", "5", "apri il browser", "stop", "fermati"):
            self.assertFalse(risposte.answer_choice(text), text)
        self.assertEqual(self.chosen, [])
        self.assertTrue(risposte.choice_waiting())

    def test_no_cancels_and_expiry_ends_the_choice(self):
        self.expect()
        self.assertTrue(risposte.answer_choice("no"))
        self.assertEqual((self.chosen, self.cancelled), ([], [True]))
        self.expect(seconds=-1.0)
        self.assertFalse(risposte.choice_waiting())
        self.assertFalse(risposte.answer_choice("2"))
        self.assertEqual(self.chosen, [])

    def test_voice_gate_lets_the_number_through_only_while_waiting(self):
        gate = WakeWordGate(clock=lambda: 100.0)
        self.assertEqual(gate.route("il secondo", require_name=True), ("ignored", ""))
        self.expect()
        self.assertEqual(gate.route("il secondo", require_name=True), ("command", "il 2"))
        self.assertEqual(gate.route("quattro", require_name=True), ("ignored", ""))
        self.assertEqual(gate.route("no", require_name=True), ("command", "no"))
        self.assertIn("due", risposte.grammar())

    def test_choice_reaches_the_local_handler_before_any_other_command(self):
        saved = dict(lumi_comandi._STATE)
        self.addCleanup(lumi_comandi._STATE.update, saved)
        lumi_comandi.register({}, lambda: False)
        self.expect()
        self.assertTrue(lumi_comandi.handle_text("il 2", lambda *_: None, lambda *_: None))
        self.assertEqual(self.chosen, [2])


if __name__ == "__main__":
    unittest.main()
