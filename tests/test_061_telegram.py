"""061 punto 3: Telegram offline di serie, «Risposte online» per contatto, invio diretto dalla chat aperta."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import settings as settings_module
import telegram_vista as tv

ROOT = Path(__file__).resolve().parents[1]


class ImpostazioniTest(unittest.TestCase):
    def test_spenta_di_serie_e_salvata_per_contatto(self):
        with tempfile.TemporaryDirectory() as cartella:
            path = Path(cartella) / "settings.json"
            self.assertNotIn("telegram_online_contacts", settings_module.load_settings(path))
            dati = dict(settings_module.load_settings(path), telegram_online_contacts=[22, 11, 11, -3, "x"])
            settings_module.save_settings(dati, path)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["telegram_online_contacts"], [11, 22])
            self.assertEqual(settings_module.load_settings(path)["telegram_online_contacts"], [11, 22])


class InvioDirettoTest(unittest.TestCase):
    def vista(self, invio):
        v = object.__new__(tv.Telegram)
        v.aperta = {"id": 7, "name": "Mario"}
        v.send_voice = invio
        v.root = SimpleNamespace(after=lambda *a: None)
        return v

    def test_con_la_chat_aperta_il_messaggio_parte_subito(self):
        invii = []
        v = self.vista(lambda *a: invii.append(a) or True)
        self.assertIsNotNone(v.contatto_aperto("✈ Mario"))
        self.assertTrue(v.invia_diretto("  ciao Mario  "))
        self.assertEqual(invii, [(7, "Mario", "ciao Mario")])

    def test_con_un_altro_titolo_non_e_aperta(self):
        v = self.vista(lambda *a: True)
        self.assertIsNone(v.contatto_aperto("Nuova chat"))
        self.assertIsNone(v.contatto_aperto("✈ Anna"))

    def test_il_vecchio_invia_messaggio_non_c_e_piu(self):
        src = (ROOT / "telegram_vista.py").read_text(encoding="utf-8")
        self.assertNotIn("Manda un vocale", src)
        self.assertNotIn("def scrivi", src)
        self.assertNotIn("ask_text", src)
        self.assertTrue(callable(getattr(tv.Telegram, "invia_diretto", None)))

    def test_invio_dalla_casella_prima_di_ogni_altra_cosa(self):
        src = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        invio = src[src.index("    def send_console_input("):]
        self.assertLess(invio.index("telegram_view.invia_diretto(message)"), invio.index('"richiamo").registra'))


class RisposteOnlineTest(unittest.TestCase):
    def test_di_serie_offline_e_online_solo_per_i_contatti_spuntati(self):
        src = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        corpo = src[src.index("    def ask_telegram_reply("):]
        corpo = corpo[:corpo.index("    def resolve_telegram_gpt_consent")]
        self.assertIn('peer_id in settings.get("telegram_online_contacts", ())', corpo)
        self.assertLess(corpo.index("telegram_online_contacts"), corpo.index("get_gemma_session()"))
        self.assertNotIn("gpt_enabled", corpo)

    def test_online_usa_la_lista_dei_servizi_spuntati(self):
        src = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        corpo = src[src.index("    def ask_telegram_online("):src.index("    def ask_telegram_reply(")]
        self.assertIn("so.disponibili()", corpo)
        self.assertIn("so.chiedi(", corpo)

    def test_la_spunta_e_nella_tendina_per_contatto(self):
        src = (ROOT / "telegram_vista.py").read_text(encoding="utf-8")
        self.assertIn('text="Risposte online"', src)
        self.assertIn("set_online", src)


if __name__ == "__main__":
    unittest.main()
