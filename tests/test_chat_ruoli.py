"""Chi ha scritto ogni messaggio (1A, 15/11): un solo posto, ruolo esplicito o per prefisso."""
import unittest

from chat_testo import classify


class RoleTests(unittest.TestCase):
    def test_prefixes(self):
        self.assertEqual(classify("TU > ciao")[::2], ("utente", "ciao"))
        self.assertEqual(classify("UTENTE / VOCE > ciao")[0], "utente")     # bug del 15/11
        self.assertEqual(classify("LUMI > Eccomi")[::2], ("jarvis", "Eccomi"))
        self.assertEqual(classify("TIMER > Timer di 5 minuti"),
                         ("comando", "▸  TIMER", "Timer di 5 minuti"))
        self.assertEqual(classify("CONTROLLO PC > Fatto")[0], "comando")
        self.assertEqual(classify("DIAGNOSTICA > controllo")[0], "comando")   # risposta all'utente
        self.assertEqual(classify("VOCABOLARIO LIA > testo")[0], "sistema")   # interno
        self.assertEqual(classify("GEMMA / ERRORE > rotto")[0], "errore")
        self.assertEqual(classify("MICROFONO > Voce non disponibile")[0], "errore")
        self.assertEqual(classify("Motore locale occupato: riprova."),
                         ("comando", "▸  LUMI", "Motore locale occupato: riprova."))
        self.assertEqual(classify("errore: qualcosa")[0], "errore")
        self.assertEqual(classify("DOCUMENTO > salvato")[0], "azione")

    def test_explicit_role_wins(self):
        self.assertEqual(classify("qualsiasi testo", "comando")[0], "comando")
        self.assertEqual(classify("TU > ciao", "sistema")[0], "sistema")
        self.assertEqual(classify("x", "inventato")[0], "sistema")


if __name__ == "__main__":
    unittest.main()
