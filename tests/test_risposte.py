import unittest

import model_gate
import risposte
from voice_control import WakeWordGate


class AnswerTests(unittest.TestCase):
    def setUp(self):
        risposte.done()               # altri test possono aver lasciato una domanda aperta

    def tearDown(self):
        risposte.done()

    def test_variants_only_as_answers(self):
        for text in ("sì", "Lumi, sì", "s", "se", "ci", "certo", "va bene"):
            self.assertTrue(risposte.is_yes(text), text)
        for text in ("no", "non", "nò", "annulla", "lascia stare"):
            self.assertTrue(risposte.is_no(text), text)
        self.assertFalse(risposte.is_answer("apri il browser"))
        self.assertIn("[unk]", risposte.GRAMMAR)

    def test_answer_without_name_only_while_waiting(self):
        gate = WakeWordGate(clock=lambda: 100.0)
        self.assertEqual(gate.route("se", require_name=True), ("ignored", ""))
        risposte.expect_answer(seconds=10, speech_text="Chiudo la finestra?")
        self.assertTrue(risposte.waiting())
        self.assertEqual(gate.route("se", require_name=True), ("command", "se"))
        self.assertFalse(risposte.waiting())                     # una risposta sola
        self.assertEqual(gate.route("no", require_name=True), ("ignored", ""))
        risposte.expect_answer(seconds=10)
        self.assertEqual(gate.route("apri il browser", require_name=True), ("ignored", ""))

    def test_local_brain_switch(self):
        try:
            self.assertTrue(model_gate.local_enabled())
            self.assertIn("spento", model_gate.set_local(False))
            self.assertFalse(model_gate.local_enabled())
            self.assertIn("CERVELLO LOCALE SPENTO", model_gate.refused_local("ciao"))
            self.assertTrue(model_gate.enabled())                # MODELLO resta ON (GPT libero)
            model_gate.set_enabled(False)
            self.assertIn("MODELLO OFF", model_gate.refused_local("ciao"))
            self.assertIn("MODELLO è OFF", model_gate.set_local(True))
        finally:
            model_gate.set_enabled(True)
            model_gate.set_local(True)


if __name__ == "__main__":
    unittest.main()
