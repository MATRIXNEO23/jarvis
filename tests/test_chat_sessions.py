"""ARCH-01 F1: independent, explicit, durable chat instances.

This suite must not touch the real Jarvis profile, model, Second Brain or
workspace DB. Uses a temporary SQLite file on each test.
"""
import tempfile
import threading
import unittest
from pathlib import Path

from local_model.chat_sessions import ChatSessionError, ChatSessionStore


class ChatSessionStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "new_chat_sessions.sqlite3"
        self.assertFalse(self.path.exists())
        self.store = ChatSessionStore(self.path)

    def test_store_created_only_by_explicit_initialization(self):
        self.assertTrue(self.path.is_file())
        self.assertEqual(self.store.list_chats(), ())
        self.assertIsNone(self.store.active_chat())

    def test_new_switch_reopen_and_complete_exchange_isolation(self):
        first = self.store.create_chat("Astronomia", activate=True)
        second = self.store.create_chat("Serie TV")
        self.assertRegex(first.id, r"^[a-f0-9]{32}$")
        self.assertNotEqual(first.id, second.id)
        self.assertEqual(self.store.active_chat(), first.id)
        self.store.append_exchange(first.id, "Che cos'è un buco nero?", "Una regione dello spazio.")
        self.store.append_exchange(second.id, "Consigliami una serie", "Una serie sci-fi.")
        self.assertEqual(
            self.store.recent_pairs(first.id),
            ((("user", "Che cos'è un buco nero?"),
              ("assistant", "Una regione dello spazio.")),))
        self.assertEqual(
            self.store.recent_pairs(second.id),
            ((("user", "Consigliami una serie"),
              ("assistant", "Una serie sci-fi.")),))
        self.store.select_chat(second.id)
        self.assertEqual(self.store.active_chat(), second.id)
        reopened = ChatSessionStore(self.path)
        self.assertEqual(reopened.active_chat(), second.id)
        self.assertEqual(reopened.recent_pairs(first.id), self.store.recent_pairs(first.id))
        self.assertEqual([c.id for c in reopened.list_chats()], [second.id, first.id])

    def test_project_scopes_never_bleed_into_general_or_other_project(self):
        a = "a" * 32
        b = "b" * 32
        general = self.store.create_chat("Generale", activate=True)
        project_a = self.store.create_chat("Progetto A", project_id=a, activate=True)
        project_b = self.store.create_chat("Progetto B", project_id=b, activate=True)
        self.assertEqual(self.store.active_chat(), general.id)
        self.assertEqual(self.store.active_chat(project_id=a), project_a.id)
        self.assertEqual(self.store.active_chat(project_id=b), project_b.id)
        self.assertEqual([c.id for c in self.store.list_chats()], [general.id])
        self.assertEqual([c.id for c in self.store.list_chats(project_id=a)], [project_a.id])
        self.assertEqual([c.id for c in self.store.list_chats(project_id=b)], [project_b.id])
        with self.assertRaises(ChatSessionError):
            self.store.select_chat(project_a.id)
        with self.assertRaises(ChatSessionError):
            self.store.append_exchange(project_a.id, "Leak?", "No.")
        with self.assertRaises(ChatSessionError):
            self.store.recent_pairs(project_a.id, project_id=b)
        with self.assertRaises(ChatSessionError):
            self.store.rename_chat(project_a.id, "Sbagliato", project_id=b)
        self.assertEqual(self.store.active_chat(), general.id)

    def test_rename_persistent_and_no_implicit_delete_or_clear(self):
        chat = self.store.create_chat("  Nuova   chat  ")
        self.assertEqual(self.store.get_chat(chat.id).title, "Nuova chat")
        self.store.append_exchange(chat.id, "Uno", "Due")
        self.store.rename_chat(chat.id, "Titolo aggiornato")
        saved = ChatSessionStore(self.path)
        self.assertEqual(saved.get_chat(chat.id).title, "Titolo aggiornato")
        self.assertEqual(len(saved.recent_pairs(chat.id)), 1)
        self.assertFalse(hasattr(saved, "delete_chat"))
        self.assertFalse(hasattr(saved, "clear_all"))

    def test_invalid_inputs_fail_closed_and_do_not_create_partial_exchange(self):
        chat = self.store.create_chat()
        invalids = [
            lambda: self.store.create_chat(""),
            lambda: self.store.create_chat("x" * 101),
            lambda: self.store.create_chat("Bad", project_id="wrong"),
            lambda: self.store.append_exchange(chat.id, "", "ok"),
            lambda: self.store.append_exchange(chat.id, "only question", ""),
            lambda: self.store.append_exchange(chat.id, "x" * 16385, "ok"),
            lambda: self.store.select_chat("unknown"),
            lambda: self.store.recent_pairs(chat.id, count=0),
            lambda: self.store.rename_chat(chat.id, "\n"),
        ]
        for operation in invalids:
            with self.subTest(operation=operation):
                with self.assertRaises((ChatSessionError, ValueError)):
                    operation()
        self.assertEqual(self.store.recent_pairs(chat.id), ())
        self.assertEqual(len(self.store.list_chats()), 1)

    def test_sql_injection_is_data_not_code(self):
        chat = self.store.create_chat("'); DROP TABLE chat_sessions; --")
        phrase = "'); DROP TABLE chat_exchanges; --"
        self.store.append_exchange(chat.id, phrase, phrase)
        self.assertEqual(self.store.recent_pairs(chat.id)[0][0][1], phrase)
        self.assertEqual(len(ChatSessionStore(self.path).list_chats()), 1)

    def test_retrieval_is_bounded_but_history_not_erased(self):
        chat = self.store.create_chat()
        for n in range(18):
            self.store.append_exchange(chat.id, "Q" + str(n), "A" + str(n))
        recent = self.store.recent_pairs(chat.id, count=3)
        self.assertEqual([pair[0][1] for pair in recent], ["Q15", "Q16", "Q17"])
        self.assertEqual(len(self.store.recent_pairs(chat.id, count=32)), 18)

    def test_concurrent_writers_are_serialized_and_preserve_all_exchanges(self):
        chat = self.store.create_chat()
        failures = []

        def writer(index):
            try:
                for n in range(5):
                    self.store.append_exchange(chat.id, f"Q{index}-{n}", f"A{index}-{n}")
            except Exception as exc:
                failures.append(exc)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=5)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertFalse(failures)
        pairs = self.store.recent_pairs(chat.id, count=32)
        self.assertEqual(len(pairs), 20)
        self.assertEqual(len({pair[0][1] for pair in pairs}), 20)

    def test_second_brain_and_legacy_profile_are_not_touched(self):
        brain = self.root / "second_brain.sqlite3"
        profile = self.root / "native.json"
        brain.write_bytes(b"PRIVATE_BRAIN_DATA")
        profile.write_bytes(b"PRIVATE_MODEL_SETTINGS")
        chat = self.store.create_chat()
        self.store.append_exchange(chat.id, "Test", "Risposta")
        self.assertEqual(brain.read_bytes(), b"PRIVATE_BRAIN_DATA")
        self.assertEqual(profile.read_bytes(), b"PRIVATE_MODEL_SETTINGS")


if __name__ == "__main__":
    unittest.main()
