"""Cancellazione a sezioni: solo DB e cartelle temporanee, mai dati reali."""
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

import cancella_memoria as cm
import command_aliases
from local_model.chat_sessions import ChatSessionStore
from second_brain import SecondBrain

P1 = "a" * 32


class FakeWorkspace:
    def __init__(self, base):
        self.items = {P1: "Lavoro"}
        self.base = Path(base)
        (self.base / P1).mkdir()

    def projects(self, limit=200):
        return [{"id": k, "name": v} for k, v in self.items.items()]

    def trash_project(self, ident):
        self.items.pop(ident)

    def project_directory(self, ident):
        return self.base / ident


class CancellaMemoriaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.path = root / "brain.sqlite3"
        self.brain = SecondBrain(self.path)
        self.store = ChatSessionStore(root / "chat.sqlite3")
        (root / "projects").mkdir()
        self.ws = FakeWorkspace(root / "projects")
        self.brain.remember_turn("Che tempo fa?", "Sole.")
        self.generale = self.brain.salva_ricordo("Mi chiamo Alberto")
        self.progetto = self.brain.salva_ricordo("La casa è blu", project_id=P1)
        self.store.create_chat("Chat di progetto", project_id=P1)
        self.cestino = []

    def conta(self, tabella):
        with closing(sqlite3.connect(self.path)) as db:
            return db.execute("SELECT COUNT(*) FROM " + tabella).fetchone()[0]

    def fts(self):
        with closing(sqlite3.connect(self.path)) as db:
            return db.execute("SELECT COUNT(*) FROM ricordi_fts WHERE ricordi_fts MATCH 'Alberto'"
                              ).fetchone()[0]

    def esegui(self, sezione):
        return cm.esegui(sezione, self.brain, self.ws, self.store,
                         trash_folders=self.cestino.extend)

    def test_chat_lascia_ricordi_e_progetti(self):
        self.esegui("chat")
        self.assertEqual(self.brain.stats(), (0, 0))
        self.assertEqual(self.conta("ricordi"), 2)
        self.assertEqual(len(self.ws.items), 1)

    def test_ricordi_toglie_tabella_e_indice(self):
        self.assertEqual(self.fts(), 1)
        self.esegui("ricordi")
        self.assertEqual(self.conta("ricordi"), 0)
        self.assertEqual(self.fts(), 0)
        self.assertEqual(self.brain.stats()[0], 1)           # la chat resta
        self.assertEqual(len(self.ws.items), 1)
        self.assertEqual(SecondBrain(self.path).ricordi(), [])   # anche dopo il riavvio

    def test_progetti_con_chat_ricordi_e_cartella(self):
        self.esegui("progetti")
        self.assertEqual(self.ws.items, {})
        self.assertEqual(self.store.list_chats(project_id=P1), ())
        self.assertEqual(self.conta("ricordi"), 1)           # resta solo quello generale
        self.assertEqual(self.cestino, [self.ws.base / P1])
        self.assertEqual(self.brain.stats()[0], 1)

    def test_tutto(self):
        self.esegui("tutto")
        self.assertEqual(self.brain.stats(), (0, 0))
        self.assertEqual(self.conta("ricordi"), 0)
        self.assertEqual(self.ws.items, {})

    def test_sezione_sconosciuta(self):
        with self.assertRaises(ValueError):
            self.esegui("altro")

    def test_frasi_a_voce(self):
        casi = {"cancella i ricordi": "ricordi", "Lumi, cancella tutti i ricordi": "ricordi",
                "cancella le chat": "chat", "elimina le conversazioni": "chat",
                "cancella i progetti": "progetti", "cancella tutto": "tutto",
                "svuota la memoria": "tutto"}
        for frase, sezione in casi.items():
            self.assertEqual(cm.parse(frase), sezione, frase)
        for frase in ("cancella il ricordo", "cancellalo", "cancella il file tutto.txt",
                      "ricordi di ieri", ""):
            self.assertIsNone(cm.parse(frase), frase)

    def test_messaggi_semplici_e_catalogo(self):
        for sezione in cm.SEZIONI:
            self.assertIn("Di' sì o no", cm.domanda(sezione))
        self.assertIn("ricordi", cm.domanda("ricordi"))
        self.assertIn("Cestino", cm.domanda("progetti"))
        elenco = command_aliases.catalog(None, music=False, pc=False)["Memoria"]
        self.assertEqual(elenco, [cm.COMANDI[s] for s in cm.SEZIONI])
        for comando in elenco:
            self.assertTrue(command_aliases.describe(comando))
            self.assertIsNotNone(cm.parse(comando))


if __name__ == "__main__":
    unittest.main()
