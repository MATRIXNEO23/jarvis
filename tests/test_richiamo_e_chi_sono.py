import unittest

import frasi_lumi
import richiamo
import scheda_lumi

PAIRS = [("apri chrome", "fatto"), ("che tempo fa", "non lo so"), ("metti musica", "ok"),
         ("parliamo di cucina", "volentieri"), ("una ricetta col riso", "risotto")]


class RichiamoTest(unittest.TestCase):
    def setUp(self):
        richiamo.ULTIMI.clear()

    def tearDown(self):
        richiamo.ULTIMI.clear()

    def test_anche_i_comandi_risolti_da_lumi(self):
        for text in ("apri chrome", "ricordati che ho un gatto", "chi sei?",
                     "cosa ti ho detto prima?"):
            richiamo.registra(text)
        written, _ = richiamo.rispondi("cosa ti ho detto prima?", PAIRS)
        self.assertEqual(written, "Prima mi hai detto: «chi sei?».")
        richiamo.registra("cosa ti ho detto 3 messaggi fa?")     # anche la domanda di prima conta
        written, _ = richiamo.rispondi("cosa ti ho detto 3 messaggi fa?", PAIRS)
        self.assertIn("ricordati che ho un gatto", written)

    def test_ricordi_pertinenti_arrivano_a_gemma(self):
        import json
        import contesto_lumi
        raw = json.dumps({"ricordi": ["Il mio gatto si chiama Fuffi"], "recent": [{"user": "x"}]})
        kept = json.loads(contesto_lumi.filtra_ricordi(raw, "pertinenti"))
        self.assertEqual(kept, {"ricordi": ["Il mio gatto si chiama Fuffi"]})

    def test_capisce_le_domande(self):
        self.assertEqual(richiamo.capisci("cosa ti ho detto prima?"), ("ultimo", 1))
        self.assertEqual(richiamo.capisci("Lumi, cosa ti ho chiesto poco fa"), ("ultimo", 1))
        self.assertEqual(richiamo.capisci("cosa ti avevo chiesto 3 turni fa?"), ("ultimo", 3))
        self.assertEqual(richiamo.capisci("che cosa ti ho detto cinque messaggi fa"), ("ultimo", 5))
        self.assertEqual(richiamo.capisci("cosa ti ho detto prima di questo argomento?"),
                         ("argomento", 0))
        for text in ("cosa ti ho detto di fare con il file", "apri chrome", "cosa hai detto prima"):
            self.assertIsNone(richiamo.capisci(text), text)

    def test_risposte_esatte_dalla_cronologia(self):
        written, said = richiamo.rispondi("cosa ti ho detto prima?", PAIRS)
        self.assertEqual(written, "Prima mi hai detto: «una ricetta col riso».")
        self.assertEqual(said, written)
        written, _ = richiamo.rispondi("cosa ti ho chiesto 5 turni fa", PAIRS)
        self.assertIn("apri chrome", written)
        written, _ = richiamo.rispondi("cosa ti ho chiesto 9 turni fa", PAIRS)
        self.assertIn("solo 5", written)
        written, said = richiamo.rispondi("cosa ti ho detto prima di questo argomento", PAIRS)
        self.assertIn("1) «metti musica»", written)          # elenco solo scritto
        self.assertNotIn("«", said)
        self.assertIn("non mi hai ancora detto", richiamo.rispondi("cosa ti ho detto prima", [])[0])
        self.assertIsNone(richiamo.rispondi("apri chrome", PAIRS))


class ChiSonoTest(unittest.TestCase):
    def tearDown(self):
        scheda_lumi.FONTE["fatti"] = None

    def test_chi_sei_frasi_configurabili(self):
        for text in ("chi sei?", "Lumi, come ti chiami", "presentati"):
            self.assertTrue(scheda_lumi.chi_sei(text), text)
        self.assertFalse(scheda_lumi.chi_sei("chi sei tu per dirmi questo, spiegami come funzioni"))
        default = frasi_lumi._defaults("chi_sono")
        self.assertGreaterEqual(len(default), 5)
        self.assertTrue(all("Lumi" in p for p in default))
        self.assertIn(scheda_lumi.risposta_propria("chi sei?"), default)

    def test_cosa_sai_fare_senza_elenco_con_le_cose_accese(self):
        scheda_lumi.FONTE["fatti"] = lambda: {"ids": ("musica", "programmi_app"), "online": False}
        reply = scheda_lumi.risposta_propria("cosa puoi fare?")
        self.assertIn("aprire e chiudere i programmi e mettere la musica", reply)
        self.assertNotIn("\n", reply)
        self.assertNotIn("Telegram", reply)
        scheda_lumi.FONTE["fatti"] = lambda: {"ids": (), "servizi_online": True}
        self.assertIn("servizi online", scheda_lumi.risposta_propria("che cosa sai fare"))
        self.assertEqual(scheda_lumi.risposta_propria("apri chrome"), "")

    def test_scheda_breve_per_gemma(self):
        info = scheda_lumi.fatti(addons=["Musica", "Controllo PC"], local_model="C:/m/gemma-2-2b.gguf",
                                 local_on=True, online=False)
        text = scheda_lumi.scheda_breve(info)
        self.assertLessEqual(len(text), 400)
        for part in ("Lumi", "Alberto", "gemma-2-2b.gguf", "Musica", "GPT: non collegato"):
            self.assertIn(part, text)

    def test_comandi_resta_l_elenco(self):
        self.assertFalse(scheda_lumi.cosa_sai_fare("comandi"))
        self.assertFalse(scheda_lumi.cosa_sai_fare("aiuto"))


if __name__ == "__main__":
    unittest.main()
