"""9/11 chat leggera passo 1: action catalog only when the sentence hints at an action."""
import unittest

from conversation_router import native_intent_context_for_request as context_for


class NativeCatalogCueTests(unittest.TestCase):
    def test_plain_conversation_gets_no_catalog(self):
        for text in ("Ciao, come va la giornata?", "Mi sento stanco oggi",
                     "Che tempo fa a Roma?", "Raccontami una barzelletta",
                     "Lumi, grazie mille"):
            with self.subTest(text=text):
                self.assertIsNone(context_for(text))

    def test_action_hints_keep_the_catalog(self):
        for text in ("Vorrei vedere un film", "apri netflix",
                     "Lumi, metti un po' di musica", "Quanto è occupata la RAM?",
                     "Scrivi un messaggio a Mio Tim", "imposta un timer di 5 minuti",
                     "cerca il file della tesi", "Controlla lo stato del PC",
                     "Dimmi come sta il computer"):
            with self.subTest(text=text):
                self.assertIsNotNone(context_for(text))

    def test_attached_document_keeps_the_catalog(self):
        self.assertIsNotNone(context_for("riassumilo", has_document=True))


if __name__ == "__main__":
    unittest.main()
