"""058: meteo settimana, giorni, parti del giorno, dettagli, domande, riepilogo, completo."""
import json
import unittest
from pathlib import Path

from meteo import commands, dettagli, service

ROOT = Path(__file__).resolve().parents[1]
ORE = ["2026-11-18T%02d:00" % h for h in range(24)]
DATI = {
    "current_weather": {"time": "2026-11-18T14:15", "temperature": 11.4, "windspeed": 17.2,
                        "weathercode": 3, "is_day": 1},
    "hourly": {"time": [("2026-11-%02dT%02d:00" % (18 + g, h)) for g in range(7) for h in range(24)],
               "temperature_2m": [10.0 + (i % 24) / 4 for i in range(168)],
               "relative_humidity_2m": [70] * 168, "precipitation_probability": [45] * 168,
               "weathercode": [61] * 168, "windspeed_10m": [10] * 168},
    "daily": {"time": ["2026-11-%02d" % d for d in range(18, 25)],
              "weathercode": [3, 61, 0, 0, 1, 0, 2], "temperature_2m_max": [12, 11, 14, 15, 16, 13, 12],
              "temperature_2m_min": [5, 6, 3, 2, 4, 6, 5],
              "precipitation_probability_max": [20, 80, 5, 0, 10, 30, 40],
              "sunrise": ["2026-11-18T06:58"] * 7, "sunset": ["2026-11-18T16:52"] * 7},
}


def _servizio(dati=DATI):
    return service.ServizioMeteo(lambda: True, citta=lambda: {"nome": "Roma", "lat": 1.0, "lon": 2.0},
                                 get=lambda url: dati)


class ComandiTests(unittest.TestCase):
    def test_comandi_esistenti_restano(self):
        self.assertEqual(commands.parse_command("che tempo fa"), ("meteo", None))
        self.assertEqual(commands.parse_command("che tempo fa a Roma"), ("meteo", "Roma"))
        self.assertEqual(commands.parse_command("meteo a Milano"), ("meteo", "Milano"))
        self.assertEqual(commands.parse_command("meteo domani"), ("domani", None))

    def test_settimana(self):
        self.assertEqual(commands.parse_command("meteo settimana"), ("settimana", None))
        self.assertEqual(commands.parse_command("che tempo farà questa settimana a Roma"),
                         ("settimana", "Roma"))

    def test_giorno_e_parte_del_giorno(self):
        self.assertEqual(commands.parse_command("che tempo farà sabato"), ("giorno:sabato", None))
        self.assertEqual(commands.parse_command("meteo giovedì"), ("giorno:giovedì", None))
        self.assertEqual(commands.parse_command("meteo weekend"), ("giorno:weekend", None))
        self.assertEqual(commands.parse_command("meteo stasera"), ("parte:stasera", None))
        self.assertEqual(commands.parse_command("meteo stanotte a Roma"), ("parte:stanotte", "Roma"))
        self.assertEqual(commands.parse_command("meteo domattina"), ("parte:domattina", None))

    def test_dettagli_domande_e_riepilogo(self):
        self.assertEqual(commands.parse_command("temperatura adesso"), ("dettaglio:temperatura adesso", None))
        self.assertEqual(commands.parse_command("vento"), ("dettaglio:vento", None))
        self.assertEqual(commands.parse_command("umidità"), ("dettaglio:umidità", None))
        self.assertEqual(commands.parse_command("alba e tramonto"), ("dettaglio:alba e tramonto", None))
        self.assertEqual(commands.parse_command("pioverà domani?"), ("domanda:pioggia_domani", None))
        self.assertEqual(commands.parse_command("serve l'ombrello?"), ("domanda:ombrello", None))
        self.assertEqual(commands.parse_command("fa freddo?"), ("domanda:freddo", None))
        self.assertEqual(commands.parse_command("buongiorno Lumi"), ("riepilogo", None))
        self.assertEqual(commands.parse_command("com'è la giornata"), ("riepilogo", None))
        self.assertIsNone(commands.parse_command("buongiorno"))

    def test_completo(self):
        self.assertEqual(commands.parse_command("meteo completo"), ("completo:tutto", None))
        self.assertEqual(commands.parse_command("dettagli meteo"), ("completo:tutto", None))
        self.assertEqual(commands.parse_command("meteo completo a Roma"), ("completo:tutto", "Roma"))

    def test_escluse_restano_ricerche(self):
        self.assertIsNone(commands.parse_command("meteo online"))
        self.assertIsNone(commands.parse_command("com'è il clima a Tokyo in primavera"))


class RispostaTests(unittest.TestCase):
    def test_settimana_voce_breve_e_sette_giorni_nella_finestra(self):
        voce, elenco = _servizio({"daily": DATI["daily"]}).risposta_settimana()
        self.assertIn("Roma", voce)
        self.assertLess(len(voce), 220)
        self.assertEqual(len(elenco["items"]), 7)

    def test_giorno_weekend(self):
        testo, elenco = _servizio().risposta_estesa("giorno:weekend")
        self.assertIn("Sabato 21", testo)
        self.assertIn("Domenica 22", testo)
        self.assertIsNone(elenco)

    def test_parte_del_giorno_e_dettagli(self):
        self.assertIn("Stasera a Roma", _servizio().risposta_estesa("parte:stasera")[0])
        self.assertIn("11 gradi", _servizio().risposta_estesa("dettaglio:temperatura adesso")[0])
        self.assertIn("17 chilometri", _servizio().risposta_estesa("dettaglio:vento")[0])
        self.assertIn("70 per cento", _servizio().risposta_estesa("dettaglio:umidità")[0])
        self.assertIn("06:58", _servizio().risposta_estesa("dettaglio:alba e tramonto")[0])

    def test_domande(self):
        self.assertTrue(_servizio().risposta_estesa("domanda:pioggia_domani")[0].startswith("Sì"))
        self.assertTrue(_servizio().risposta_estesa("domanda:ombrello")[0].startswith("Sì"))
        self.assertTrue(_servizio().risposta_estesa("domanda:freddo")[0].startswith("Sì"))
        self.assertTrue(_servizio().risposta_estesa("domanda:caldo")[0].startswith("No"))

    def test_riepilogo_con_data_e_consiglio(self):
        testo = _servizio().risposta_estesa("riepilogo")[0]
        self.assertIn("mercoledì 18 novembre", testo)
        self.assertIn("minima 5 e massima 12", testo)
        self.assertIn("giacca", testo)

    def test_completo_breve_a_voce_e_tutto_nella_finestra(self):
        voce, elenco = _servizio().risposta_estesa("completo:tutto")
        self.assertLess(len(voce), 330)
        etichette = [riga[0] for riga in elenco["items"]]   # 059: colonne Dato, Valore
        for voce_attesa in ("Vento", "Umidità", "Alba", "Tramonto", "Probabilità di pioggia"):
            self.assertIn(voce_attesa, etichette)

    def test_dati_incompleti_dicono_l_errore(self):
        with self.assertRaises(service.ErroreMeteo):
            _servizio({"current_weather": {}}).risposta_estesa("dettaglio:vento")


class AiutoERegistroTests(unittest.TestCase):
    def test_aiuto_e_personalizzazione(self):
        help_text = (ROOT / "local_help.py").read_text(encoding="utf-8")
        self.assertIn("COME USARE IL METEO", help_text)
        self.assertIn("meteo settimana", help_text)
        self.assertIn("meteo completo", help_text)
        import command_aliases as ca
        self.assertIn("Meteo", ca.BASE_SECTIONS)
        self.assertEqual(ca.ADDON_SECTIONS["meteo"], "Meteo")
        comandi = ca.catalog()["Meteo"]
        for frase in ("che tempo fa", "che tempo fa a {testo}", "meteo a {testo}", "meteo domani",
                      "meteo settimana", "meteo weekend", "buongiorno Lumi", "meteo completo"):
            self.assertIn(frase, comandi)
            self.assertTrue(ca.describe(frase), frase)

    def test_registro_capacita(self):
        data = json.loads((ROOT / "meteo" / "Meteo.jaddon").read_text(encoding="utf-8"))
        ids = {a["id"] for a in data["actions"]}
        self.assertTrue({"addon.meteo.settimana", "addon.meteo.dettagli", "addon.meteo.riepilogo"} <= ids)
        self.assertLessEqual(len(data["actions"]), 5)
        text = (ROOT / "addon_manager.py").read_text(encoding="utf-8")
        for nome in ("settimana", "dettagli", "riepilogo"):
            self.assertIn("addon.meteo." + nome, text)


if __name__ == "__main__":
    unittest.main()
