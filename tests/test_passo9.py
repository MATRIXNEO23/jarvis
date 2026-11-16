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
        # 16/11: mouse, finestre e programmi si possono provare; ciò che non si annulla no.
        for text in ("che ore sono", "imposta un timer di 5 minuti", "chi sei", "apri chrome",
                     "clicca su Invia", "mostra i numeri", "minimizza", "cancellalo",
                     "cerca file preventivo"):
            self.assertTrue(ponte.comando_permesso(text), text)
        for text in ("elimina il file", "spegni il pc", "riavvia il computer", "sposta la cartella",
                     "cancella il file prova", "manda un messaggio a Marco", "invia a Marco ciao", ""):
            self.assertFalse(ponte.comando_permesso(text), text)

    def test_ponte_e_server_mcp_dal_vivo(self):
        self.bridge.avvia()
        ponte.registra("errore", "qualcosa non va")
        ask = lambda op, args: server_mcp.chiedi_al_ponte(op, args, path=self.path)
        self.assertEqual(ask("stato", {})["stato"], {"stato": "attesa"})
        self.assertIn("qualcosa non va", ask("errori", {})["righe"][-1])
        self.assertEqual(ask("log_motore", {"righe": 2})["righe"], ["b", "c"])
        self.assertFalse(ask("prova_comando", {"testo": "spegni il pc"})["ok"])
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

    def test_strumenti_nuovi_impostazioni_addon_ricordi_chat(self):
        from types import SimpleNamespace
        from diagnostica_claude import strumenti

        class Nav:
            current = ("Voce", "Voci")

            def voci(self):
                return {"Voce": ["Voci", "La mia voce"], "Add-on": ["Gestisci add-on"]}

            def apri_categoria(self, category):
                self.current = (category, None)

            def mostra(self, category, item):
                self.current = (category, item)

        nav, opened = Nav(), []
        addons = [{"id": "musica", "name": "Musica", "enabled": False}]
        manager = SimpleNamespace(list_installed=lambda: addons)

        def cambia(ident, on):
            addons[0]["enabled"] = on
            return True
        brain = SimpleNamespace(ricordi=lambda q, categoria=None, limit=100: [{"breve": q}])
        store = SimpleNamespace(models=lambda: {"c1": {"online"}})
        elenco = SimpleNamespace(store=store, current=lambda: "c1",
                                 chats=lambda: [SimpleNamespace(id="c1", title="Prova")],
                                 recent=lambda n: [(("user", "ciao"), ("assistant", "ehi"))])
        tools = strumenti.crea(navigazione=lambda: nav, apri_impostazioni=lambda: opened.append(1),
                               addon_manager=lambda: manager, cambia_addon=cambia,
                               cervello=lambda: brain, elenco_chat=lambda: elenco)
        bridge = ponte.Ponte(stato=dict, in_chat=print, prova=print, riavvia_modello=print,
                             run_ui=lambda fn: fn(), path=self.path, extra=tools)
        bridge.avvia()
        try:
            ask = lambda op, args: server_mcp.chiedi_al_ponte(op, args, path=self.path)
            self.assertEqual(ask("impostazioni", {})["voci"]["Voce"], ["Voci", "La mia voce"])
            self.assertEqual(ask("impostazioni", {"categoria": "Voce", "voce": "La mia voce"})["aperta"],
                             ["Voce", "La mia voce"])
            self.assertEqual(opened, [1])
            self.assertFalse(ask("impostazioni", {"categoria": "Boh"})["ok"])
            self.assertEqual(ask("addon", {})["addon"][0]["acceso"], False)
            self.assertEqual(ask("addon", {"id": "musica", "acceso": True})["acceso"], True)
            self.assertEqual(ask("ricordi", {"cerca": "pavilion"})["ricordi"], [{"breve": "pavilion"}])
            chat = ask("chat", {"scambi": 3})
            self.assertEqual(chat["chat"][0]["modelli"], ["online"])
            self.assertEqual(chat["ultimi_scambi"], [{"utente": "ciao", "lumi": "ehi"}])
            names = {t["name"] for t in server_mcp.STRUMENTI}
            self.assertTrue({"lumi_impostazioni", "lumi_addon", "lumi_ricordi", "lumi_chat"} <= names)
        finally:
            bridge.ferma()

    def test_collegamento_vecchio_dice_che_lumi_e_chiusa(self):
        import socket
        free = socket.socket()
        free.bind(("127.0.0.1", 0))
        port = free.getsockname()[1]
        free.close()                              # porta chiusa: nessuno ascolta
        self.path.write_text(json.dumps({"port": port, "token": "x"}), encoding="utf-8")
        reply = server_mcp.chiedi_al_ponte("stato", {}, path=self.path, timeout=2)
        self.assertIn("non è aperta", reply["errore"])

    def test_prova_comando_aspetta_la_risposta(self):
        now = [0.0]

        def sleep(seconds):
            now[0] += seconds
            if abs(now[0] - 0.5) < 0.01:
                ponte.registra("utente", "chi sei")
            if abs(now[0] - 1.0) < 0.01:
                ponte.registra("jarvis", "Sono Lumi.")
        start = ponte.CONTA[0]
        ponte.registra("comando", "Prova del comando: chi sei")
        lines = ponte.aspetta_risposta(start, 30, sleep=sleep, clock=lambda: now[0])
        self.assertTrue(lines[-1].endswith("jarvis: Sono Lumi."))
        self.assertLess(now[0], 5)                    # finisce dopo il silenzio, non a 30 s
        self.assertEqual(ponte.aspetta_risposta(ponte.CONTA[0], 1, sleep=sleep,
                                                clock=lambda: now[0]), [])

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
