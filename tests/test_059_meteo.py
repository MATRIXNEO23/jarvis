"""059 (C3): meteo di qualsiasi giorno entro 16 giorni e qualsiasi luogo, anche combinati;
probabilità di pioggia in tutte le frasi; colonne proprie; oltre i 16 giorni Lumi lo dice."""
import unittest
from datetime import date, timedelta

from meteo import dettagli
from meteo.commands import parse_command
from meteo.service import ErroreMeteo, ServizioMeteo, elenco_settimana, frase, frase_domani, settimana

OGGI = date(2026, 11, 18)


def dati16(prob=40):
    giorni = [(OGGI + timedelta(days=i)).isoformat() for i in range(16)]
    return {"current_weather": {"time": giorni[0] + "T10:00", "temperature": 12, "windspeed": 5,
                                "weathercode": 61},
            "hourly": {"time": [], "temperature_2m": [], "relative_humidity_2m": [],
                       "precipitation_probability": [], "weathercode": []},
            "daily": {"time": giorni, "weathercode": [61] * 16, "temperature_2m_max": [15.0] * 16,
                      "temperature_2m_min": [8.0] * 16, "precipitation_probability_max": [prob] * 16,
                      "sunrise": [g + "T07:00" for g in giorni], "sunset": [g + "T17:00" for g in giorni]}}


class FrasiTest(unittest.TestCase):
    def test_combinazioni(self):
        casi = {
            "meteo giovedì a Roma": ("giorno:giovedì", "Roma"),
            "meteo sabato": ("giorno:sabato", None),
            "meteo il 25": ("data:#25", None),
            "meteo il 25 dicembre a Torino": ("data:#25/12", "Torino"),
            "meteo tra 3 giorni": ("data:+3", None),
            "meteo tra una settimana a Napoli": ("data:+7", "Napoli"),
            "meteo dopodomani a Milano": ("data:+2", "Milano"),
            "che tempo farà dopodomani": ("data:+2", None),
            "meteo domani a Roma": ("domani", "Roma"),
            "meteo settimana": ("settimana", None),
            "meteo Roma": ("meteo", "Roma"),
        }
        for frase_, atteso in casi.items():
            self.assertEqual(parse_command(frase_), atteso, frase_)

    def test_resta_il_limite_di_120_caratteri(self):
        self.assertIsNone(parse_command("meteo " + "a" * 130))

    def test_online_e_clima_restano_esclusi(self):
        self.assertIsNone(parse_command("cerca online meteo dopodomani"))
        self.assertIsNone(parse_command("com'è il clima a Tokyo in primavera"))


class RispostaTest(unittest.TestCase):
    def setUp(self):
        self.dati = dati16()

    def test_dopodomani_tra_giorni_e_data(self):
        self.assertIn("Venerdì 20", dettagli.per_data("Roma", self.dati, "+2"))   # 20/11/2026 è venerdì
        self.assertIn("probabilità di pioggia 40 per cento", dettagli.per_data("Roma", self.dati, "+3"))
        self.assertIn("Mercoledì 25", dettagli.per_data("Roma", self.dati, "#25"))
        self.assertIn("Venerdì 4", dettagli.per_data("Roma", self.dati, "#4/12"))

    def test_oltre_16_giorni_lo_dice(self):
        with self.assertRaises(dettagli.OltreLimite) as ctx:
            dettagli.per_data("Roma", self.dati, "+16")
        self.assertIn("16 giorni", str(ctx.exception))
        with self.assertRaises(dettagli.OltreLimite):
            dettagli.per_data("Roma", self.dati, "#25/12")

    def test_giorno_della_settimana_con_pioggia(self):
        self.assertIn("probabilità di pioggia", dettagli.giorno("Roma", self.dati, "giovedì"))

    def test_servizio_fino_alla_voce(self):
        def get(url):
            if "geocoding" in url:
                return {"results": [{"name": "Roma", "latitude": 41.9, "longitude": 12.5}]}
            self.assertIn("forecast_days=16", url)
            return self.dati
        servizio = ServizioMeteo(lambda: True, get=get)
        frase_, elenco = servizio.risposta_estesa("data:+2", "Roma")
        self.assertIn("pioggia 40 per cento", frase_)
        self.assertIsNone(elenco)
        with self.assertRaises(ErroreMeteo) as ctx:
            servizio.risposta_estesa("data:+20", "Roma")
        self.assertIn("16 giorni", str(ctx.exception))

    def test_tutte_le_frasi_hanno_la_pioggia(self):
        self.assertIn("probabilità di pioggia 30 per cento", frase("Roma", 12, 61, True, 30))
        self.assertIn("probabilità di pioggia 30 per cento", frase_domani("Roma", 15, 8, 61, 30))
        self.assertNotIn("pioggia 0", frase("Roma", 12, 0, True, None))      # dato mancante: nessun invento

    def test_attuale_e_domani_chiedono_la_probabilita(self):
        from meteo import service
        self.assertIn("precipitation_probability_max", service.PREVISIONE)
        self.assertIn("precipitation_probability_max", service.PREVISIONE_DOMANI)
        self.assertIn("precipitation_probability_max", service.PREVISIONE_SETTIMANA)
        self.assertIn("forecast_days=16", service.PREVISIONE_COMPLETA)

    def test_settimana_frase_e_colonne(self):
        def get(url):
            d = dati16()["daily"]
            return {"daily": {k: v[:7] for k, v in d.items()}}
        giorni = settimana(41.9, 12.5, get)
        elenco = elenco_settimana("Roma", giorni)
        self.assertEqual([c[0] for c in elenco["colonne"]],
                         ["Giorno", "Cielo", "Minima", "Massima", "Pioggia %"])
        self.assertTrue(all(len(riga) == 5 for riga in elenco["items"]))
        self.assertEqual(elenco["items"][0][4], "40 %")
        from meteo.service import frase_settimana
        self.assertIn("probabilità di pioggia fino al 40 per cento", frase_settimana("Roma", giorni))

    def test_aiuto_personalizzazione_e_registro(self):
        import json
        from pathlib import Path
        import command_aliases as ca
        root = Path(__file__).resolve().parents[1]
        aiuto = (root / "local_help.py").read_text(encoding="utf-8")
        for testo in ("meteo giovedì a Roma", "meteo il 25", "meteo tra 3 giorni", "dopodomani a Milano", "16 giorni"):
            self.assertIn(testo, aiuto)
        for comando in ("meteo dopodomani", "meteo giovedì a {testo}", "meteo il 25", "meteo tra 3 giorni"):
            self.assertIn(comando, ca.catalog()["Meteo"])
            self.assertTrue(ca.describe(comando), comando)
        data = json.loads((root / "meteo" / "Meteo.jaddon").read_text(encoding="utf-8"))
        self.assertEqual(data["version"], "1.2.0")
        self.assertIn("tra 3 giorni", json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
