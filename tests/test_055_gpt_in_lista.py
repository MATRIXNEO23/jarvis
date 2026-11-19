"""055 (decisione 17/11 05:05): GPT dal browser è una voce della lista dei servizi online,
con spunta e posizione; niente «Uso GPT?»; il locale è l'ultimo ripiego."""
import ast
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from online import servizi_online as so
ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "jarvis.py").read_text(encoding="utf-8")
GPT = "chatgpt_account"


def _post(chiamate):
    def post(url, key, body, timeout):
        chiamate.append(url)
        return {"choices": [{"message": {"content": "risposta " + url.split("/")[2]}}]}
    return post


class GptNellaListaTests(unittest.TestCase):
    def setUp(self):
        self.saved = dict(so.ACCOUNT)
        self.gpt = []
        self.http = []
        self.keys = so.Chiavi(Path(tempfile.mkdtemp()) / "k.keys", protect=lambda v, e: v[::-1])
        self.keys.salva("gemini", "g")
        self.keys.salva("groq", "q")
        self.collegato(True)

    def tearDown(self):
        so.ACCOUNT.update(self.saved)

    def collegato(self, ok):
        so.ACCOUNT.update(chiedi=lambda text, timeout: self.gpt.append(text) or "risposta GPT",
                          pronto=lambda: ok)

    def chiedi(self, ordine, attivi):
        settings = {"ordine": ordine, "attivi": attivi, "modelli": {}, "limiti": {},
                    "usa_sempre": False, "proponi_lunghe": True}
        return so.chiedi(so.messaggi("ciao"), settings=settings, keys=self.keys, post=_post(self.http))

    def test_gpt_in_cima_risponde_per_primo(self):
        name, text = self.chiedi([GPT, "gemini", "groq"], [GPT, "gemini", "groq"])
        self.assertEqual((name, text), ("ChatGPT dal browser", "risposta GPT"))
        self.assertEqual(self.http, [])

    def test_gpt_in_fondo_risponde_solo_dopo_gli_altri(self):
        name, _ = self.chiedi(["gemini", "groq", GPT], [GPT, "gemini", "groq"])
        self.assertEqual(name, so.PER_ID["gemini"].nome)
        self.assertEqual(self.gpt, [])
        # se gli altri falliscono, tocca a GPT
        def rotto(url, key, body, timeout):
            raise OSError("giù")
        settings = {"ordine": ["gemini", "groq", GPT], "attivi": [GPT, "gemini", "groq"],
                    "modelli": {}, "limiti": {}, "usa_sempre": False, "proponi_lunghe": True}
        name, text = so.chiedi(so.messaggi("ciao"), settings=settings, keys=self.keys, post=rotto)
        self.assertEqual((name, text), ("ChatGPT dal browser", "risposta GPT"))

    def test_gpt_senza_spunta_non_viene_mai_usato(self):
        name, _ = self.chiedi([GPT, "gemini", "groq"], ["gemini", "groq"])
        self.assertEqual(name, so.PER_ID["gemini"].nome)
        self.assertEqual(self.gpt, [])
        name, reasons = self.chiedi([GPT], [])
        self.assertIsNone(name)
        self.assertEqual(self.gpt, [])

    def test_gpt_non_collegato_passa_al_successivo(self):
        self.collegato(False)
        name, _ = self.chiedi([GPT, "gemini", "groq"], [GPT, "gemini", "groq"])
        self.assertEqual(name, so.PER_ID["gemini"].nome)
        self.assertEqual(self.gpt, [])

    def test_gpt_non_collegato_e_nessun_altro_da_il_motivo(self):
        self.collegato(False)
        name, reasons = self.chiedi([GPT], [GPT])
        self.assertIsNone(name)
        self.assertIn("collegamento GPT", "; ".join(reasons))

    def test_disponibili_conta_gpt_solo_se_spuntato_e_collegato(self):
        base = {"ordine": [GPT], "modelli": {}, "limiti": {}, "usa_sempre": False, "proponi_lunghe": True}
        self.assertTrue(so.disponibili(dict(base, attivi=[GPT]), self.keys))
        self.assertFalse(so.disponibili(dict(base, attivi=[]), self.keys))
        self.collegato(False)
        self.assertFalse(so.disponibili(dict(base, attivi=[GPT]), self.keys))

    def test_codice_va_sempre_online(self):
        self.assertTrue(so.richiesta_codice("scrivimi uno script Python"))
        self.assertFalse(so.richiesta_codice("che tempo fa"))

    def test_diagnostica_online_mostra_gpt_nella_lista(self):
        from diagnostica_claude import strumenti
        source = (ROOT / "diagnostica_claude" / "strumenti.py").read_text(encoding="utf-8")
        for campo in ('"gpt_collegato"', '"posizione"', '"tipo"'):
            self.assertIn(campo, source)
        self.assertIn(GPT, [s.id for s in so.SERVIZI])
        self.assertTrue(hasattr(strumenti, "__file__"))


class CatenaSenzaDomandaTests(unittest.TestCase):
    def test_nessuna_domanda_uso_gpt_ne_finestra_si_no(self):
        for vecchio in ("offer_gpt", "resume_gpt", "send_to_gpt", '"gpt_yes"', '"gpt_no"',
                        '"gpt_offer"', "Uso GPT"):
            self.assertNotIn(vecchio, SRC)
        online = (ROOT / "local_model" / "conversazione_lumi.py").read_text(encoding="utf-8")
        self.assertNotIn("online_gpt", online)
        tree = ast.parse(SRC)
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        chain = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == "conversation_chain")
        names = {n.id for n in ast.walk(chain) if isinstance(n, ast.Name)}
        names |= {n.attr for n in ast.walk(chain) if isinstance(n, ast.Attribute)}
        for vietato in ("messagebox", "askyesno", "chiedi", "confirm_gpt_inference"):
            self.assertNotIn(vietato, names)

    def test_la_catena_prova_la_lista_poi_il_locale(self):
        tree = ast.parse(SRC)
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        chain = ast.get_source_segment(SRC, next(
            n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == "conversation_chain"))
        self.assertLess(chain.index('route="online"'), chain.index("local_after_gpt("))


class PulsantiFinestraTests(unittest.TestCase):
    def test_pulsanti_sopra_l_ingranaggio_e_non_accanto(self):
        chrome = (ROOT / "window_chrome.py").read_text(encoding="utf-8")
        hud = (ROOT / "animated_hud.py").read_text(encoding="utf-8")
        self.assertIn("_jarvis_window_corner", chrome)
        self.assertIn('buttons.pack(side="top", anchor="e", before=anchor)', chrome)
        self.assertIn("_jarvis_window_corner", hud)
        self.assertIn("corner,text=\"⚙\"", hud.replace("\n            ", ""))
        self.assertIn('self.gear.pack(side="top"', hud)


if __name__ == "__main__":
    unittest.main()


class ConfigurazioneCodexTests(unittest.TestCase):
    def test_blocco_toml_con_stessi_command_e_args_in_apici_singoli(self):
        from diagnostica_claude import ui
        import json
        py = r"C:\Python\python.exe"
        toml = ui.configurazione_codex(py)
        claude = json.loads(ui.configurazione_claude(py))["mcpServers"]["lumi-diagnostica"]
        lines = toml.splitlines()
        self.assertEqual(lines[0], "[mcp_servers.lumi-diagnostica]")
        self.assertEqual(lines[1], "command = '%s'" % claude["command"])
        self.assertEqual(lines[2], "args = ['%s']" % claude["args"][0])
        self.assertIn("startup_timeout_sec = 30", lines)
        self.assertIn("tool_timeout_sec = 120", lines)

    def test_pulsante_riga_di_testo_e_percorso_del_profilo(self):
        from diagnostica_claude import ui
        source = (ROOT / "diagnostica_claude" / "ui.py").read_text(encoding="utf-8")
        self.assertIn("Copia configurazione per Codex", source)
        self.assertIn("ISTRUZIONI-PROVE-CODEX.md", source)
        self.assertEqual(ui.percorso_codex(), Path.home() / ".codex" / "config.toml")
        doc = (ROOT / "docs" / "audit" / "ISTRUZIONI-PROVE-CODEX.md").read_text(encoding="utf-8")
        self.assertIn("Copia configurazione per Codex", doc)
