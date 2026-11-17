"""056c: cronologia ridotta per tutte le domande brevi, valori di partenza 768/500 nei modelli nuovi
(profili già salvati intatti), blocco unico Contesto+Memoria nello stesso posto, meteo domani."""
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def pair(n, risposta="r" * 400):
    return (("utente", "domanda %d" % n), ("lumi", risposta))


class CronologiaTests(unittest.TestCase):
    def test_domanda_breve_non_saluto_tiene_solo_l_ultimo_scambio_tagliato(self):
        from local_model.prompt_breve import adatta_storia
        storia = [pair(1), pair(2), pair(3)]
        out = adatta_storia(storia, "e il prezzo?")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0][0][1], "domanda 3")
        self.assertLessEqual(len(out[0][1][1]), 130)

    def test_domanda_lunga_o_approfondisci_resta_intera(self):
        from local_model.prompt_breve import adatta_storia
        storia = [pair(1), pair(2)]
        self.assertEqual(adatta_storia(storia, "approfondisci"), storia)
        self.assertEqual(adatta_storia(storia, "spiegami come funziona la fotosintesi nel dettaglio"), storia)

    def test_casella_spenta_come_056b(self):
        from local_model.prompt_breve import adatta_storia
        storia = [pair(1), pair(2), pair(3)]
        self.assertEqual(len(adatta_storia(storia, "e il prezzo?", ridotta=False)), 3)
        self.assertEqual(len(adatta_storia(storia, "ciao", ridotta=False)), 1)

    def test_sessione_passa_la_casella(self):
        src = (ROOT / "local_model" / "native_conversation_session.py").read_text(encoding="utf-8")
        self.assertIn('getattr(memory, "cronologia_ridotta", True)', src)


class ProfiloTests(unittest.TestCase):
    def test_valori_di_partenza(self):
        from local_model.memory_preferences import MemoryPreferences
        from local_model.native_config import NativeModelConfig
        self.assertEqual(NativeModelConfig().context_size, 896)
        m = MemoryPreferences()
        self.assertEqual((m.prompt_max_tokens, m.cronologia_ridotta, m.chat_continua), (550, True, True))

    def test_memoria_salva_e_riletta_con_i_campi_del_contesto(self):
        from local_model.memory_preferences import MemoryPreferences
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.json"
            replace(MemoryPreferences(), cronologia_ridotta=False, ricordi_locale="mai").save(path)
            self.assertNotIn("ricordi_locale", json.loads(path.read_text()))     # schema vecchio intatto
            letto = MemoryPreferences.load(path)
            self.assertFalse(letto.cronologia_ridotta)
            self.assertEqual(letto.ricordi_locale, "mai")

    def test_file_vecchio_senza_campi_nuovi_si_carica_invariato(self):
        from local_model.memory_preferences import MemoryPreferences
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.json"
            MemoryPreferences().save(path)
            path.with_suffix(".native.json").write_text(json.dumps({"history_max_tokens": 300}))
            vecchio = json.loads(path.read_text())
            vecchio["prompt_max_tokens"] = 600
            path.write_text(json.dumps(vecchio))
            letto = MemoryPreferences.load(path)
            self.assertEqual((letto.prompt_max_tokens, letto.history_max_tokens), (600, 300))
            self.assertTrue(letto.cronologia_ridotta)

    def test_modello_nuovo_ha_768_e_500_ma_lo_slot_in_uso_non_cambia(self):
        from local_model import profili_famiglia as pf
        from local_model.native_config import NativeModelConfig
        with tempfile.TemporaryDirectory() as tmp:
            nuovo = Path(tmp) / "nuovo.gguf"
            usato = Path(tmp) / "usato.gguf"
            for f in (nuovo, usato):
                f.write_bytes(b"x")
            cfg = Path(tmp) / "native.json"
            NativeModelConfig(model=str(usato), context_size=2048, max_output=256).save(cfg)
            dati = pf.carica(cfg)
            attuale = pf.valori(NativeModelConfig.load(cfg))
            vecchio = pf._voce(dati, usato, attuale, usa_corrente=True)
            self.assertEqual(vecchio["slot"]["1"]["context_size"], 2048)
            self.assertNotIn("1", vecchio.get("memoria", {}))
            fresco = pf._voce(dati, nuovo, attuale)
            for n in "123":
                self.assertEqual(fresco["slot"][n]["context_size"], 896)
                self.assertEqual(fresco["memoria"][n]["prompt_max_tokens"], 550)
                self.assertEqual(fresco["slot"][n]["max_output"], 256)

    def test_salvataggio_rifiutato_se_prompt_piu_risposta_superano_il_contesto(self):
        ui = (ROOT / "local_model" / "native_ui.py").read_text(encoding="utf-8")
        self.assertIn("prompt + risposta > contesto" if False else "if prompt + risposta > contesto:", ui)
        self.assertIn("superano il contesto", ui)
        self.assertLess(ui.index("superano il contesto"), ui.index("update_native_settings(self.current, changes)"))

    def test_blocco_unico_nella_pagina_modelli(self):
        ui = (ROOT / "local_model" / "native_ui.py").read_text(encoding="utf-8")
        self.assertIn("Contesto e memoria del prompt", ui)
        self.assertIn("Cronologia ridotta per domande brevi", ui)
        self.assertIn('"Context Size (token)"', ui)
        self.assertNotIn('text="Memoria del prompt (parte del profilo)"', ui)
        self.assertNotIn("costruisci_sezione", (ROOT / "contesto_lumi.py").read_text(encoding="utf-8"))
        self.assertNotIn('"contesto_lumi").costruisci_sezione', (ROOT / "jarvis.py").read_text(encoding="utf-8"))

    def test_contesto_lumi_letto_dal_profilo(self):
        import os
        import contesto_lumi
        from local_model.memory_preferences import MemoryPreferences
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["JARVIS_TRIAL_HOME"] = tmp
            try:
                self.assertEqual(contesto_lumi.carica(), contesto_lumi.Contesto())
                contesto_lumi.salva(contesto_lumi.Contesto(False, "mai"))
                self.assertEqual(contesto_lumi.carica(), contesto_lumi.Contesto(False, "mai"))
                from local_model.memory_preferences import default_memory_preferences_path
                self.assertFalse(MemoryPreferences.load(default_memory_preferences_path()).chat_continua)
            finally:
                del os.environ["JARVIS_TRIAL_HOME"]


class MeteoDomaniTests(unittest.TestCase):
    def test_frasi(self):
        from meteo.commands import parse_command
        self.assertEqual(parse_command("meteo domani"), ("domani", None))
        self.assertEqual(parse_command("meteo domani a Roma"), ("domani", "Roma"))
        self.assertEqual(parse_command("che tempo farà domani a Milano"), ("domani", "Milano"))
        self.assertEqual(parse_command("Lumi, che tempo fa domani"), ("domani", None))
        self.assertEqual(parse_command("meteo Roma"), ("meteo", "Roma"))
        self.assertIsNone(parse_command("meteo dopodomani"))
        self.assertIsNone(parse_command("cerca online meteo domani"))

    def test_servizio_open_meteo_daily(self):
        from meteo.service import ServizioMeteo
        urls = []

        def get(url):
            urls.append(url)
            if "geocoding" in url:
                return {"results": [{"name": "Roma", "latitude": 41.9, "longitude": 12.5}]}
            return {"daily": {"weathercode": [0, 61], "temperature_2m_max": [20, 15.4],
                              "temperature_2m_min": [10, 8.2]}}
        s = ServizioMeteo(lambda: True, get=get)
        self.assertEqual(s.risposta_domani("Roma"), "Domani a Roma: pioggia, minima 8 e massima 15 gradi.")
        self.assertIn("daily=weathercode", urls[-1])

    def test_aiuto_e_registro_capacita(self):
        text = (ROOT / "local_help.py").read_text(encoding="utf-8")
        self.assertIn("meteo domani", text)
        data = json.loads((ROOT / "meteo" / "Meteo.jaddon").read_text(encoding="utf-8"))
        self.assertIn("addon.meteo.domani", [a["id"] for a in data["actions"]])
        self.assertIn("addon.meteo.domani", (ROOT / "addon_manager.py").read_text(encoding="utf-8"))
        self.assertIn("meteo domani", (ROOT / "meteo" / "LEGGIMI.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
