"""Regression tests for ordinary Italian commands in a document dialogue."""
import unittest
from document_language import classify_document_choice

class DocumentLanguageTests(unittest.TestCase):
    def test_explicit_discard_is_one_utterance(self):
        for phrase in ("chiudi senza salvare", "esci senza salvare",
                       "puoi uscire senza salvare", "non salvare, chiudi",
                       "chiudilo senza salvare"):
            with self.subTest(phrase=phrase):
                self.assertEqual(classify_document_choice(phrase, pending=True),
                                 "discard")

    def test_variants_for_save_and_cancel(self):
        for phrase in ("salva e chiudi", "salva ed esci", "sì, salva pure"):
            self.assertEqual(classify_document_choice(phrase, pending=True),
                             "save")
        for phrase in ("annulla", "non chiudere", "lascia aperto"):
            self.assertEqual(classify_document_choice(phrase, pending=True),
                             "cancel")

    def test_unclear_speech_never_discards(self):
        for phrase in ("non chiudere senza salvare",
                       "come faccio a chiudere senza salvare",
                       "se dico chiudi senza salvare cosa succede",
                       "chiudi e basta"):
            self.assertNotEqual(classify_document_choice(phrase, pending=True),
                                "discard")

if __name__ == "__main__":
    unittest.main()
