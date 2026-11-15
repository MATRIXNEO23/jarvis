import io
import json
import tempfile
import unittest
import urllib.error
import zipfile
from pathlib import Path

import chat_elenco
import chat_import
import github_lettura
import lumi_comandi
from diagnostica_claude import ponte, server_mcp
from diagnostica_claude.ui import configurazione_claude
from local_model.chat_sessions import ChatSessionStore

CHATGPT = [{"title": "Ricetta", "current_node": "c", "mapping": {
    "r": {"message": None, "parent": None},
    "a": {"message": {"author": {"role": "user"}, "content": {"parts": ["Come faccio la pasta?"]}}, "parent": "r"},
    "b": {"message": {"author": {"role": "assistant"}, "content": {"parts": ["Acqua e sale."]}}, "parent": "a"},
    "x": {"message": {"author": {"role": "assistant"}, "content": {"parts": ["ramo scartato"]}}, "parent": "a"},
    "c": {"message": {"author": {"role": "user"}, "content": {"parts": ["E poi?"]}}, "parent": "b"}}}]
CLAUDE = [{"name": "Viaggio", "chat_messages": [
    {"sender": "human", "text": "Dove vado?"}, {"sender": "assistant", "text": "A Roma."},
    {"sender": "human", "text": "Quando?"}, {"sender": "assistant", "text": ""},
    {"sender": "assistant", "content": [{"type": "text", "text": "In primavera."}]}]}]


class ImportTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.dir = Path(self.folder.name)

    def tearDown(self):
        chat_elenco._CURRENT["elenco"] = None
        self.folder.cleanup()

    def test_chatgpt_segue_il_ramo_scelto(self):
        self.assertEqual(chat_import.scambi(CHATGPT[0]), [("Come faccio la pasta?", "Acqua e sale.")])
        self.assertEqual(chat_import.titolo(CHATGPT[0]), "Ricetta")

    def test_claude_e_zip(self):
        path = self.dir / "export.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("dati/conversations.json", json.dumps(CLAUDE))
        conversations = chat_import.carica(path)
        self.assertEqual(chat_import.scambi(conversations[0]),
                         [("Dove vado?", "A Roma."), ("Quando?", "In primavera.")])

    def test_file_non_valido(self):
        bad = self.dir / "x.json"
        bad.write_text("{rotto", encoding="utf-8")
        with self.assertRaises(chat_import.ImportError_):
            chat_import.carica(bad)

    def test_importa_nell_elenco_del_progetto(self):
        path = self.dir / "conversations.json"
        path.write_text(json.dumps(CLAUDE + CHATGPT), encoding="utf-8")
        store = ChatSessionStore(self.dir / "chat.sqlite3")
        notes, shown = [], []
        elenco = chat_elenco.ElencoChat(store, lambda: None, lambda t, p: shown.append((t, p)),
                                        notify=notes.append)
        self.assertTrue(elenco.importa(path, lambda items: items[0]))
        self.assertIn("Importata «Viaggio» (2 scambi)", notes[-1])
        self.assertEqual(shown[-1][0], "Viaggio")
        self.assertEqual(len(shown[-1][1]), 2)
        self.assertFalse(elenco.importa(path, lambda items: None))


class GitHubTest(unittest.TestCase):
    def test_frasi(self):
        self.assertEqual(github_lettura.parse("i miei repository"), ("repos", None))
        self.assertEqual(github_lettura.parse("Lumi, issue aperte di jarvis"), ("issues", "jarvis"))
        self.assertEqual(github_lettura.parse("ultimi commit di matrixneo23/jarvis"),
                         ("commits", "matrixneo23/jarvis"))
        self.assertIsNone(github_lettura.parse("apri chrome"))

    def test_risposte(self):
        def get(path, token):
            if path.startswith("/user/repos"):
                return [{"name": "jarvis", "full_name": "me/jarvis", "private": True}]
            if "/issues" in path:
                return [{"number": 3, "title": "Bug voce"}, {"number": 4, "title": "PR", "pull_request": {}}]
            if "/commits" in path:
                return [{"sha": "abcdef123", "commit": {"message": "Passo 9\n\ndettagli"}}]
            raise AssertionError(path)
        self.assertIn("me/jarvis  (privato)", github_lettura.esegui("repos", None, "t", get))
        issues = github_lettura.esegui("issues", "Jarvis", "t", get)
        self.assertIn("#3 Bug voce", issues)
        self.assertNotIn("PR", issues)
        self.assertIn("abcdef1 Passo 9", github_lettura.esegui("commits", "me/jarvis", "t", get))
        self.assertIn("serve la chiave", github_lettura.esegui("repos", None, "", get))

    def test_errori_comprensibili(self):
        def get(path, token):
            raise urllib.error.HTTPError("u", 401, "x", {}, io.BytesIO(b""))
        self.assertEqual(github_lettura.esegui("commits", "a/b", "t", get), "Chiave GitHub non valida.")

    def test_configurazione(self):
        with tempfile.TemporaryDirectory() as folder:
            config = github_lettura.Configurazione(Path(folder), protect=lambda v, e: v[::-1])
            self.assertFalse(config.attivo)
            config.salva_token("ghp_x")
            self.assertNotIn("ghp_x", (Path(folder) / "github.json").read_text(encoding="utf-8"))
            self.assertEqual(config.token(), "ghp_x")
            config.imposta_attivo(True)
            self.assertTrue(github_lettura.Configurazione(Path(folder), protect=lambda v, e: v[::-1]).attivo)

    def test_comando_arriva_all_add_on(self):
        calls = []
        lumi_comandi.register({"github": lambda spoken: calls.append(spoken) or True}, lambda: False)
        try:
            self.assertTrue(lumi_comandi.handle_text("i miei repository", lambda t: None, lambda t: None))
        finally:
            lumi_comandi._STATE.update(actions=None, pending=None)
        self.assertEqual(calls, ["i miei repository"])


class DiagnosticaTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / "porta.json"
        self.ui = []
        self.bridge = ponte.Ponte(stato=lambda: {"stato": "attesa"}, in_chat=self.ui.append,
                                  prova=lambda t: self.ui.append("prova:" + t),
                                  riavvia_modello=lambda: self.ui.append("riavvio"),
                                  run_ui=lambda fn: fn(), log_motore=lambda: "a\nb\nc",
                                  path=self.path)

    def tearDown(self):
        self.bridge.ferma()
        self.folder.cleanup()

    def test_comandi_permessi(self):
        for text in ("che ore sono", "imposta un timer di 5 minuti", "chi sei"):
            self.assertTrue(ponte.comando_permesso(text), text)
        for text in ("apri chrome", "clicca su Invia", "mostra i numeri", "elimina il file",
                     "spegni il pc", "minimizza", ""):
            self.assertFalse(ponte.comando_permesso(text), text)

    def test_ponte_e_server_mcp_dal_vivo(self):
        self.bridge.avvia()
        ponte.registra("errore", "qualcosa non va")
        ask = lambda op, args: server_mcp.chiedi_al_ponte(op, args, path=self.path)
        self.assertEqual(ask("stato", {})["stato"], {"stato": "attesa"})
        self.assertIn("qualcosa non va", ask("errori", {})["righe"][-1])
        self.assertEqual(ask("log_motore", {"righe": 2})["righe"], ["b", "c"])
        self.assertFalse(ask("prova_comando", {"testo": "apri chrome"})["ok"])
        self.assertTrue(ask("prova_comando", {"testo": "che ore sono"})["ok"])
        self.assertTrue(ask("scrivi_in_chat", {"testo": "ciao"})["ok"])
        self.assertEqual(self.ui, ["prova:che ore sono", "ciao"])
        info = json.loads(self.path.read_text(encoding="utf-8"))
        info["token"] = "sbagliato"
        self.path.write_text(json.dumps(info), encoding="utf-8")
        self.assertEqual(ask("stato", {})["errore"], "chiave non valida")
        self.bridge.ferma()
        self.assertFalse(self.path.exists())
        self.assertIn("spento", ask("stato", {})["errore"])

    def test_protocollo_mcp(self):
        init = server_mcp.gestisci({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                    "params": {"protocolVersion": "2025-06-18"}})
        self.assertEqual(init["result"]["capabilities"], {"tools": {}})
        self.assertIsNone(server_mcp.gestisci({"jsonrpc": "2.0", "method": "notifications/initialized"}))
        tools = server_mcp.gestisci({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
        self.assertEqual(len(tools), len(server_mcp.STRUMENTI))
        call = server_mcp.gestisci({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                                    "params": {"name": "lumi_console", "arguments": {"righe": 5}}},
                                   ask=lambda op, args: {"ok": True, "righe": [op, args["righe"]]})
        self.assertFalse(call["result"]["isError"])
        self.assertIn("console", call["result"]["content"][0]["text"])
        self.assertIn("error", server_mcp.gestisci({"jsonrpc": "2.0", "id": 4, "method": "boh"}))
        out = io.StringIO()
        server_mcp.main(io.StringIO('{"jsonrpc":"2.0","id":9,"method":"ping"}\n'), out)
        self.assertEqual(json.loads(out.getvalue())["result"], {})

    def test_configurazione_per_claude(self):
        config = json.loads(configurazione_claude("C:/Python/python.exe"))
        server = config["mcpServers"]["lumi-diagnostica"]
        self.assertEqual(server["command"], "C:/Python/python.exe")
        self.assertTrue(server["args"][0].endswith("server_mcp.py"))


if __name__ == "__main__":
    unittest.main()
