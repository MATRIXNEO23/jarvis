"""Chat unica (scelta A, 15/11): archivio per progetto, nuovo/rinomina/elimina, salvataggio."""
import tempfile
import unittest
from pathlib import Path

import chat_elenco
from local_model.chat_sessions import ChatSessionStore

PROJECT = "a" * 32


class ChatListTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.project = [None]
        self.shown = []
        self.store = ChatSessionStore(Path(folder.name) / "chat.sqlite3")
        self.elenco = chat_elenco.ElencoChat(self.store, lambda: self.project[0],
                                             lambda title, pairs: self.shown.append((title, list(pairs))))
        self.addCleanup(lambda: chat_elenco._CURRENT.update(elenco=None))

    def test_first_exchange_creates_chat_and_saves_any_model(self):
        self.assertTrue(chat_elenco.registra_scambio("ciao locale", "risposta Gemma"))
        self.assertTrue(chat_elenco.registra_scambio("e adesso GPT?", "risposta GPT"))
        current = self.elenco.current()
        self.assertEqual(self.store.list_chats()[0].title, "ciao locale")
        self.assertEqual([q for q, _ in self.store.display_pairs(current)], ["ciao locale", "e adesso GPT?"])
        self.assertIn("e adesso GPT?", str(chat_elenco.contesto_recente(1)))

    def test_projects_have_their_own_chats(self):
        chat_elenco.registra_scambio("generale", "ok")
        self.project[0] = PROJECT
        chat_elenco.progetto_cambiato()
        self.assertEqual(self.shown[-1], ("Nuova chat", []))       # nessuna chat nel progetto
        chat_elenco.registra_scambio("nel progetto", "ok")
        self.assertEqual(len(self.store.list_chats(project_id=PROJECT)), 1)
        self.assertEqual(len(self.store.list_chats()), 1)

    def test_new_rename_select_delete(self):
        first = self.elenco.new_chat()
        chat_elenco.registra_scambio("uno", "1")
        second = self.elenco.new_chat()
        self.assertEqual(self.elenco.current(), second)
        self.assertTrue(self.elenco.rename(first, "Ricette"))
        self.assertTrue(self.elenco.select(first))
        self.assertEqual(self.shown[-1], ("Ricette", [("uno", "1")]))
        self.assertTrue(self.elenco.delete(first))
        self.assertEqual([c.id for c in self.elenco.chats()], [second])
        self.assertEqual(self.elenco.current(), second)

    def test_empty_exchanges_are_not_saved(self):
        self.assertFalse(chat_elenco.registra_scambio("  ", "x"))
        self.assertEqual(list(self.elenco.chats()), [])


if __name__ == "__main__":
    unittest.main()
