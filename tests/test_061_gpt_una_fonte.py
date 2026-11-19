"""061 punto 1: GPT ha UNA sola fonte, la spunta «ChatGPT dal browser» nella lista Online.
Anti-richiamo: nel codice non deve restare niente del vecchio interruttore gpt_enabled."""
import json
import socket
import ssl
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

from online import servizi_online as so
import settings as settings_module

ROOT = Path(__file__).resolve().parents[1]
VIETATI = ("gpt_enabled", "toggle_gpt", "gpt_toggle", "Abilita collegamento ChatGPT")


def sorgenti():
    for path in ROOT.rglob("*"):
        parti = set(path.relative_to(ROOT).parts)
        if parti & {"tests", "docs", ".git", "__pycache__", "dist", "audit", "node_modules"}:
            continue
        if path.suffix in (".py", ".json", ".mjs", ".bat", ".ps1", ".yml") or path.name == "LEGGIMI.md":
            yield path


class AntiRichiamoTest(unittest.TestCase):
    def test_nessun_richiamo_al_vecchio_interruttore(self):
        trovati = []
        for path in sorgenti():
            testo = path.read_text(encoding="utf-8", errors="ignore")
            for parola in VIETATI:
                if parola in testo:
                    trovati.append((str(path.relative_to(ROOT)), parola))
        self.assertEqual(trovati, [])

    def test_le_impostazioni_non_hanno_piu_il_campo_e_ignorano_quello_vecchio(self):
        self.assertNotIn("gpt_enabled", settings_module.DEFAULTS)
        with tempfile.TemporaryDirectory() as cartella:
            path = Path(cartella) / "settings.json"
            path.write_text('{"gpt_enabled": true, "auto_listen": false}', encoding="utf-8")
            letto = settings_module.load_settings(path)
            self.assertNotIn("gpt_enabled", letto)
            settings_module.save_settings(letto, path)
            self.assertNotIn("gpt_enabled", json.loads(path.read_text(encoding="utf-8")))


class SpuntaTest(unittest.TestCase):
    def test_spuntato_segue_il_file_della_lista(self):
        with tempfile.TemporaryDirectory() as cartella:
            path = Path(cartella) / "servizi_online.json"
            self.assertFalse(so.spuntato("chatgpt_account", path))
            so.salva_impostazioni(dict(so.carica_impostazioni(path), attivi=["chatgpt_account"]), path)
            self.assertTrue(so.spuntato("chatgpt_account", path))
            self.assertEqual(so.spuntati(path), ("chatgpt_account",))
            so.salva_impostazioni(dict(so.carica_impostazioni(path), attivi=[]), path)
            self.assertFalse(so.spuntato("chatgpt_account", path))

    def test_il_piano_usa_il_primo_servizio_spuntato(self):
        with mock.patch.object(so, "chiedi", return_value=("Mistral", '{"steps": []}')) as chiedi:
            risposta = so.PonteTesto().call("ask", prompt="pianifica", timeout=5, authorize_send=lambda: True)
        self.assertEqual(risposta["text"], '{"steps": []}')
        self.assertEqual(chiedi.call_args.args[0][0]["content"], "pianifica")

    def test_il_piano_si_ferma_se_l_autorizzazione_e_revocata(self):
        with mock.patch.object(so, "chiedi") as chiedi:
            with self.assertRaises(PermissionError):
                so.PonteTesto().call("ask", prompt="x", authorize_send=lambda: False)
        chiedi.assert_not_called()

    def test_il_piano_riporta_i_motivi_se_nessuno_risponde(self):
        with mock.patch.object(so, "chiedi", return_value=(None, ["Groq: chiave non valida"])):
            with self.assertRaises(RuntimeError):
                so.PonteTesto().call("ask", prompt="x")

    def test_collegare_il_ponte_non_dipende_dalla_spunta(self):
        src = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        run = src[src.index("    def run_gpt("):]
        run = run[:run.index("from model_gate")]
        self.assertIn('action in ("ask", "conversation", "typed_conversation")', run)
        self.assertIn("gpt_spuntato()", run)
        self.assertNotIn("def toggle_gpt", src)

    def test_la_diagnostica_dice_i_servizi_spuntati_non_un_modello_selezionato(self):
        src = (ROOT / "runtime_diagnostics.py").read_text(encoding="utf-8")
        self.assertIn("Servizi online spuntati", src)
        self.assertNotIn("Modello selezionato", src)


class FasiErroreTest(unittest.TestCase):
    """061 punto 4: gli errori dei servizi dicono sempre la fase."""

    def test_fasi(self):
        self.assertEqual(so.fase_errore(urllib.error.URLError(socket.gaierror(11001, "x"))), "DNS")
        self.assertEqual(so.fase_errore(urllib.error.URLError(ssl.SSLError("CERTIFICATE_VERIFY_FAILED"))), "TLS")
        self.assertEqual(so.fase_errore(TimeoutError()), "connessione")
        self.assertEqual(so.fase_errore(urllib.error.HTTPError("u", 429, "m", {}, None)), "risposta")
        self.assertEqual(so.fase_errore(so.ServizioErrore("vuota")), "risposta")

    def test_ogni_motivo_porta_la_fase(self):
        for exc in (urllib.error.HTTPError("u", 401, "m", {}, None), TimeoutError(),
                    urllib.error.URLError(socket.gaierror(1, "x")), so.ServizioErrore("vuota"), ValueError("x")):
            self.assertIn("(fase: ", so._motivo(exc))

    def test_prova_servizio_ferma_al_dns(self):
        with mock.patch.object(so, "prova_rete", return_value=(False, "si ferma al DNS (h non si trova): x")):
            bene, testo = so.prova_servizio("groq", settings=so.carica_impostazioni(Path("/nessuno.json")))
        self.assertFalse(bene)
        self.assertIn("DNS", testo)

    def test_la_diagnostica_ha_lo_strumento_di_prova(self):
        from diagnostica_claude import server_mcp, strumenti
        self.assertIn("lumi_prova_servizio", server_mcp.PER_NOME)
        self.assertEqual(server_mcp.PER_NOME["lumi_prova_servizio"]["op"], "prova_servizio")
        src = Path(strumenti.__file__).read_text(encoding="utf-8")
        self.assertIn('"prova_servizio": prova_servizio', src)

    def test_la_prova_parte_in_background(self):
        with mock.patch.object(so, "prova_servizio", return_value=(True, "ok")):
            primo = so.avvia_prova("groq")
        self.assertIn("in_corso", primo)
        self.assertFalse(so.avvia_prova("non_esiste")["ok"])


class TemaTest(unittest.TestCase):
    def test_il_tema_vale_per_ogni_finestra(self):
        src = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        self.assertIn('root.option_add("*" + _classe + ".background", BG)', src)
        self.assertIn('style.configure("Treeview", background=PANEL', src)
        self.assertIn('("Toplevel", "Frame")', src)


if __name__ == "__main__":
    unittest.main()
