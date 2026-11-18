"""058 (04:10): un servizio online saltato non è più silenzioso. Riga in chat/console/lumi_errori,
ultimo errore nella tendina e in lumi_online; ordine e ripiego invariati; mai la chiave."""
import tempfile
import unittest
import urllib.error
from pathlib import Path

import servizi_online as so

ROOT = Path(__file__).resolve().parents[1]
SEGRETO = "AIza-SEGRETISSIMA"


def _post(falliscono):
    def post(url, key, body, timeout):
        for nome, codice in falliscono.items():
            if nome in url:
                raise urllib.error.HTTPError(url, codice, "x", {}, None)
        return {"choices": [{"message": {"content": "ok da " + url.split("/")[2]}}]}
    return post


class ErroriOnlineTests(unittest.TestCase):
    def setUp(self):
        self.keys = so.Chiavi(Path(tempfile.mkdtemp()) / "k.keys", protect=lambda v, e: v[::-1])
        self.keys.salva("gemini", SEGRETO)
        self.keys.salva("groq", "gsk")
        self.righe = []
        self.salvato = dict(so.AVVISO)
        so.AVVISO["scrivi"] = self.righe.append
        so.ULTIMO_ERRORE.clear()
        self.settings = {"ordine": ["gemini", "groq"], "attivi": ["gemini", "groq"], "modelli": {},
                         "limiti": {}, "usa_sempre": False, "proponi_lunghe": True}

    def tearDown(self):
        so.AVVISO.update(self.salvato)
        so.ULTIMO_ERRORE.clear()

    def chiedi(self, falliscono):
        return so.chiedi(so.messaggi("ciao"), settings=self.settings, keys=self.keys,
                         post=_post(falliscono))

    def test_la_riga_dice_chi_e_stato_saltato_e_chi_ha_risposto(self):
        name, text = self.chiedi({"generativelanguage": 401})
        self.assertEqual(name, "Groq")                           # ordine e ripiego invariati
        self.assertEqual(len(self.righe), 1)
        riga = self.righe[0]
        self.assertIn("Google Gemini non ha risposto (chiave non valida)", riga)
        self.assertIn("ho usato Groq", riga)
        self.assertTrue(riga.startswith("ONLINE / ERRORE >"))      # arriva anche in lumi_errori
        self.assertNotIn(SEGRETO, riga)

    def test_l_ultimo_errore_resta_finche_il_servizio_non_risponde(self):
        self.chiedi({"generativelanguage": 429})
        self.assertEqual(so.ULTIMO_ERRORE["gemini"], "quota finita o troppe richieste")
        self.assertNotIn("groq", so.ULTIMO_ERRORE)
        self.chiedi({})
        self.assertNotIn("gemini", so.ULTIMO_ERRORE)

    def test_nessuna_riga_se_risponde_il_primo(self):
        name, _ = self.chiedi({})
        self.assertEqual(name, "Google Gemini")
        self.assertEqual(self.righe, [])

    def test_manca_la_chiave_e_un_servizio_saltato(self):
        self.keys.salva("gemini", "")
        name, _ = self.chiedi({})
        self.assertEqual(name, "Groq")
        self.assertEqual(so.ULTIMO_ERRORE["gemini"], "manca la chiave")
        self.assertIn("manca la chiave", self.righe[0])

    def test_se_nessuno_risponde_restano_i_motivi_e_nessun_avviso(self):
        name, reasons = self.chiedi({"generativelanguage": 401, "groq": 429})
        self.assertIsNone(name)
        self.assertEqual(len(reasons), 2)
        self.assertEqual(self.righe, [])
        self.assertEqual(set(so.ULTIMO_ERRORE), {"gemini", "groq"})

    def test_anche_chiama_con_gli_strumenti_avvisa(self):
        servizio, nome, _msg = so.chiama(so.messaggi("ciao"), settings=self.settings, keys=self.keys,
                                         post=_post({"generativelanguage": 403}))
        self.assertEqual(servizio, "groq")
        self.assertIn("accesso negato", self.righe[0])

    def test_un_errore_nell_avviso_non_ferma_la_risposta(self):
        def rompe(_):
            raise RuntimeError("x")
        so.AVVISO["scrivi"] = rompe
        self.assertEqual(self.chiedi({"generativelanguage": 401})[0], "Groq")

    def test_cablaggio_chat_tendina_e_diagnostica(self):
        jarvis = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        self.assertIn('AVVISO["scrivi"] = lambda text: root.after(0, lambda: write_line(text))', jarvis)
        menu = (ROOT / "menu_tendine.py").read_text(encoding="utf-8")
        self.assertIn("ULTIMO_ERRORE.get(service_id)", menu)
        self.assertIn('"#f2a33a"', menu)
        diag = (ROOT / "diagnostica_claude" / "strumenti.py").read_text(encoding="utf-8")
        self.assertIn('"ultimo_errore": servizi_online.ULTIMO_ERRORE.get(ident)', diag)
        from chat_testo import classify
        self.assertEqual(classify("ONLINE / ERRORE > Google Gemini non ha risposto", None)[0], "errore")


if __name__ == "__main__":
    unittest.main()
