"""Voice adaptation uses no audio, large model or cloud connection."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from adaptive_voice import SpeechCorrections, SpeechCorrectionError
from voice_control import speech_to_local_command, WakeWordGate


class VoiceCorrectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "Jarvis" / "second_brain.sqlite3"
        self.words = SpeechCorrections(self.db)

    def test_user_confirmed_correction_survives_restart(self):
        with self.assertRaises(SpeechCorrectionError):
            self.words.add("blocco moto", "blocco note")
        self.words.add("blocco moto", "blocco note", user_confirmed=True)
        self.assertEqual(self.words.count(), 1)
        new_session = SpeechCorrections(self.db)
        self.assertEqual(
            new_session.correct("ehi jarvis apri blocco moto"),
            "ehi jarvis apri blocco note")
        gate = WakeWordGate()
        route, text = gate.route(new_session.correct(
            "ehi jarvis apri blocco moto"))
        self.assertEqual((route, speech_to_local_command(text)),
                         ("command", "apri blocco note"))

    def test_correct_full_phrase_learns_only_misheard_application_name(self):
        source, target = self.words.learn_phrase(
            "apri blocco moto", "apri blocco note", user_confirmed=True)
        self.assertEqual((source, target), ("blocco moto", "blocco note"))
        self.assertEqual(self.words.correct("ehi jarvis apri blocco moto"),
                         "ehi jarvis apri blocco note")
        self.assertEqual(self.words.correct("ho una moto"), "ho una moto")

    def test_full_phrase_cannot_change_negations_or_verbs(self):
        examples = (
            ("chiudi senza salvare", "chiudi salvare"),
            ("apri blocco moto", "chiudi blocco note"),
            ("ehi jarvis apri il browser", "ehi lia apri il browser"),
        )
        for heard, intended in examples:
            with self.subTest(heard=heard, intended=intended):
                with self.assertRaises(SpeechCorrectionError):
                    self.words.learn_phrase(heard, intended, user_confirmed=True)

    def test_existing_recognized_words_not_damaged(self):
        self.words.add("blocco moto", "blocco note", user_confirmed=True)
        self.assertEqual(
            self.words.correct("Voglio blocco moto, non blocco motociclista"),
            "Voglio blocco note, non blocco motociclista")
        self.assertEqual(self.words.correct("motocicletta"), "motocicletta")

    def test_no_command_confirmation_negation_or_wake_rewrite(self):
        unsafe = (
            ("non", "salva"), ("chiudi", "apri"),
            ("salva", "cancella"), ("ehi", "jarvis"),
            ("blocco moto", "chiudi senza salvare"),
            ("blocco moto", "jarvis"),
            ("non salvare", "salva"), ("apri note", "blocco note"),
            ("password", "documenti"), ("download", "non salvare"),
            ("blocco-note", "blocco note"), ("blocco note", "C:/users"),
            ("un errore", "vai a capo\ninvia"),
        )
        for a, b in unsafe:
            with self.subTest(a=a, b=b):
                with self.assertRaises(SpeechCorrectionError):
                    self.words.add(a, b, user_confirmed=True)
        self.assertEqual(self.words.count(), 0)

    def test_is_not_general_command_or_shell_learning(self):
        self.words.add("scolle", "scuole", user_confirmed=True)
        text = self.words.correct("apri cmd exe")
        self.assertEqual(text, "apri cmd exe")
        self.assertIsNone(speech_to_local_command(text))
        self.assertEqual(self.words.correct("invia il pagamento"), "invia il pagamento")

    def test_replacement_is_one_pass_even_with_overlapping_rules(self):
        self.words.add("moto", "note", user_confirmed=True)
        self.words.add("blocco moto", "blocco note", user_confirmed=True)
        self.assertEqual(self.words.correct("blocco moto"), "blocco note")
        self.assertEqual(self.words.correct("blocco moto moto"), "blocco note note")

    def test_exact_persistent_erasure_and_no_action_replay(self):
        self.words.add("blocco moto", "blocco note", user_confirmed=True)
        self.words.clear()
        another = SpeechCorrections(self.db)
        self.assertEqual(another.count(), 0)
        self.assertEqual(another.correct("blocco moto"), "blocco moto")
        with sqlite3.connect(self.db) as db:
            rows = db.execute("SELECT COUNT(*) FROM speech_corrections").fetchone()[0]
        self.assertEqual(rows, 0)

    def test_bounded_personal_dictionary(self):
        for i in range(80):
            # Alphabetic, non-executable vocabulary.
            value = chr(ord("a") + (i % 26)) * (i // 26 + 1) + "voce"
            self.words.add(value, "vocabolario", user_confirmed=True)
        self.assertEqual(self.words.count(), 80)
        with self.assertRaises(SpeechCorrectionError):
            self.words.add("novanta", "voce", user_confirmed=True)
        self.assertEqual(self.words.count(), 80)


if __name__ == "__main__":
    unittest.main()
