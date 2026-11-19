"""061 punto 7: «Intendevi…? Sì o no» per le frasi brevi con parole di comando (decisione 19/11 05:30)."""
import unittest
from pathlib import Path

import intent_normalizer as nlu

ROOT = Path(__file__).resolve().parents[1]


class IntendeviTest(unittest.TestCase):
    """punto 7: frase breve con parola di comando che non è un comando esatto -> «Intendevi…?»."""
    CATALOGO = ["apri download", "imposta timer {testo}", "che tempo fa", "meteo domani", "apri blocco note"]

    def test_frase_breve_con_parola_di_comando_chiede(self):
        r = nlu.understand("meteo per domani mattina", self.CATALOGO, model_on=True, extra={})
        self.assertEqual(r[0], "simile")
        self.assertEqual(r[1], "meteo domani")

    def test_otto_parole_ancora_si_chiede_nove_no(self):
        otto = nlu.understand("apri la cartella dei download di ieri sera", self.CATALOGO, model_on=True, extra={})
        self.assertIsNotNone(otto)
        nove = nlu.understand("apri la cartella dei download di ieri sera a casa mia ok",
                              self.CATALOGO, model_on=True, extra={})
        self.assertIsNone(nove)

    def test_senza_parola_di_comando_va_al_modello(self):
        self.assertIsNone(nlu.understand("chi era napoleone", self.CATALOGO, model_on=True, extra={}))

    def test_il_comando_esatto_si_esegue_subito(self):
        self.assertEqual(nlu.understand("apri download", self.CATALOGO, model_on=True, extra={})[0], "esatto")

    def test_il_no_manda_la_frase_al_modello(self):
        src = (ROOT / "intent_normalizer.py").read_text(encoding="utf-8")
        self.assertIn('_RUNTIME["to_model"](original)', src)


if __name__ == "__main__":
    unittest.main()
