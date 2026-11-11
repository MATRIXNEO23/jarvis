import tempfile
import unittest
from pathlib import Path

import intent_normalizer as n

CATALOG = ["imposta timer {testo}", "pausa timer", "ferma timer", "quanto manca al timer",
           "metti {testo}", "ferma la musica", "pausa", "metti la playlist {testo}",
           "stato sistema", "elenca download", "passa a {testo}", "che ore sono"]


class UnderstandTests(unittest.TestCase):
    def test_synonyms_and_fillers_give_exact_command(self):
        u = lambda t, on=True: n.understand(t, CATALOG, model_on=on, extra={})
        self.assertEqual(u("Lumi, per favore attiva un timer di 5 minuti"),
                         ("esatto", "imposta timer 5 minuti"))
        self.assertEqual(u("fai partire il timer da 10 secondi"), ("esatto", "imposta timer 10 secondi"))
        self.assertEqual(u("stoppa la musica"), ("esatto", "ferma la musica"))
        self.assertEqual(u("metti in pausa"), ("esatto", "pausa"))
        self.assertEqual(u("puoi mostrare i download?"), ("esatto", "elenca download"))
        self.assertEqual(u("avvia la playlist Rock"), ("esatto", "metti la playlist rock"))

    def test_single_verb_commands_never_taken_by_synonym(self):
        self.assertIsNone(n.understand("avvia il computer", CATALOG, extra={}))
        self.assertIsNone(n.understand("attiva la modalità aereo", CATALOG, extra={}))

    def test_asks_also_with_model_on_but_stricter(self):
        self.assertIsNone(n.understand("stato del sistema di casa mia oggi pomeriggio", CATALOG,
                                       model_on=True, extra={}))
        self.assertEqual(n.understand("stato sistemi", CATALOG, model_on=True, extra={})[:2],
                         ("simile", "stato sistema"))
        result = n.understand("stato sistemi", CATALOG, model_on=False, extra={})
        self.assertEqual(result[:2], ("simile", "stato sistema"))
        self.assertIsNone(n.understand("raccontami una storia", CATALOG, model_on=False, extra={}))

    def test_yes_no_answer_and_runtime(self):
        ran, lines = [], []
        n.register(ran.append, lambda: CATALOG, lines.append)
        from model_gate import set_enabled
        try:
            set_enabled(False)
            self.assertTrue(n.before_model("stato sistemi"))
            self.assertIn("«stato sistema»", lines[-1])
            self.assertTrue(n.before_model("sì"))
            self.assertEqual(ran, ["stato sistema"])
            self.assertTrue(n.before_model("stato sistemi"))
            self.assertTrue(n.before_model("no"))
            self.assertEqual(ran, ["stato sistema"])
            set_enabled(True)
            self.assertTrue(n.before_model("stoppa la musica"))
            self.assertEqual(ran[-1], "ferma la musica")
            self.assertFalse(n.before_model("raccontami una barzelletta"))   # va al modello
            sent = []
            n.register(ran.append, lambda: CATALOG, lines.append, to_model=sent.append)
            self.assertTrue(n.before_model("stato sistemi"))                  # modello acceso: chiede
            self.assertTrue(n.before_model("no"))
            self.assertEqual(sent, ["stato sistemi"])                         # «no» → al modello
        finally:
            set_enabled(True)
            n.register(None, None, None)

    def test_personal_synonyms_saved(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "synonyms.json"
            n.save_extra({"spara": "imposta"}, path)
            extra = n.load_extra(path)
            self.assertEqual(n.understand("spara un timer di 3 minuti", CATALOG, extra=extra),
                             ("esatto", "imposta timer 3 minuti"))


if __name__ == "__main__":
    unittest.main()
