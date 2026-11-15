import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import classificatore
import frasi_lumi
import la_mia_voce
from adaptive_voice import SpeechCorrections
from classificatore import Classificatore


class CorrezioniTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.lexicon = SpeechCorrections(Path(self.folder.name) / "brain.sqlite3")

    def tearDown(self):
        self.folder.cleanup()

    def test_elenco_e_rimuovi(self):
        self.lexicon.learn_phrase("apri blocco moto", "apri blocco note", user_confirmed=True)
        self.assertEqual(self.lexicon.elenco(), [("blocco moto", "blocco note")])
        self.assertEqual(self.lexicon.correct("blocco moto"), "blocco note")
        self.assertTrue(self.lexicon.rimuovi("blocco moto"))
        self.assertEqual(self.lexicon.elenco(), [])
        self.assertEqual(self.lexicon.correct("blocco moto"), "blocco moto")

    def test_niente_correzioni_che_confondono_un_altro_comando(self):
        session = la_mia_voce.Session(lexicon=self.lexicon, phrases=["sì", "sei", "sette"])
        outcome = session.hear("sei")                        # atteso «sì», capito «sei»
        self.assertIn("non imparo per non confondere", outcome)
        self.assertEqual(self.lexicon.elenco(), [])
        outcome = session.hear("sei")                        # atteso «sei»
        self.assertEqual(outcome, "Capito bene.")


class LetterePerseTest(unittest.TestCase):
    def test_trova_la_s_persa_spesso(self):
        results = [("scorri giù", "corri giù", ""), ("sasso", "aso", ""), ("sette", "ette", ""),
                   ("uno", "uno", "")]
        self.assertEqual(la_mia_voce.lettere_perse(results), ["s"])
        self.assertEqual(la_mia_voce.lettere_perse(results[:2]), [])

    def test_lettere_facoltative_nel_confronto(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(la_mia_voce, "_path", lambda: Path(folder) / "voce.json"):
                la_mia_voce.salva_facoltative(["s", "x"])
                self.assertEqual(la_mia_voce.facoltative(), "s")
                self.assertEqual(la_mia_voce.senza_facoltative("Scorri giù"), "corri giù")
                from controllo_pc.service import _sounds_like
                self.assertEqual(_sounds_like("stranger things", "tranger thing"), 1.0)

    def test_parlato_dal_vivo_solo_con_la_finestra(self):
        seen = []
        la_mia_voce.PARZIALE["ascolta"] = seen.append
        try:
            la_mia_voce.parziale("scorri")
        finally:
            la_mia_voce.PARZIALE["ascolta"] = None
        la_mia_voce.parziale("altro")
        self.assertEqual(seen, ["scorri"])


class ClassificatoreTest(unittest.TestCase):
    EXAMPLES = ["aprimi blocco note", "scorri a destra fino al prossimo film",
                "imposta la sveglia alle sette e mezza", "mostra i numeri e poi clicca sul quinto"]

    def test_indovina_solo_se_simile_e_chiaro(self):
        c = Classificatore(self.EXAMPLES)
        guess = c.indovina("imposta sveglia alle sette e mezzo")
        self.assertEqual(guess[0], "imposta la sveglia alle sette e mezza")
        self.assertIsNone(c.indovina("raccontami una storia sui draghi"))
        self.assertIsNone(c.indovina("aprimi blocco note"))          # già un comando esatto
        self.assertIsNone(c.indovina("ciao"))

    def test_spento_di_serie(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(la_mia_voce, "_path", lambda: Path(folder) / "voce.json"):
                self.assertFalse(classificatore.attivo())
                self.assertIsNone(classificatore.indovina("imposta sveglia alle sette e mezzo"))
                classificatore.imposta(True)
                self.assertTrue(classificatore.attivo())
                classificatore._ISTANZA["c"] = Classificatore(self.EXAMPLES)
                try:
                    self.assertIsNotNone(classificatore.indovina("imposta sveglia alle sette e mezzo"))
                finally:
                    classificatore._ISTANZA["c"] = None

    def test_esempi_dal_catalogo(self):
        self.assertTrue(any("Blocco note" in e for e in classificatore.esempi()))


class FrasiVarieTest(unittest.TestCase):
    def test_nuove_domande_variano_e_chiedono_si_o_no(self):
        for key in ("proponi_online", "togli_riquadro"):
            said = [frasi_lumi.say(key, {"added": {}, "removed": {}}) for _ in range(6)]
            self.assertTrue(all(a != b for a, b in zip(said, said[1:])), key)
            self.assertTrue(all("sì o no" in s for s in said), key)
        self.assertTrue(frasi_lumi.say("fermo", {"added": {}, "removed": {}}))


if __name__ == "__main__":
    unittest.main()
