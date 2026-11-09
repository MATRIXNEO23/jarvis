"""ARCH-01 F2 RED: isolated Lumi chat UI and local-only history sources.

UI uses a temporary DB and no audio, no external API and no GGUF.
"""
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from tkinter import ttk

from local_model.chat_context import make_chat_history_reader
from local_model.chat_sessions import ChatSessionStore
from local_model.chat_ui import ChatSessionsPanel


class ScopedGemmaReaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "chats.sqlite3"
        self.store = ChatSessionStore(self.path)

    def test_only_selected_chat_supplies_history_and_never_global_memory(self):
        a = self.store.create_chat("A")
        b = self.store.create_chat("B")
        self.store.append_exchange(a.id, "Ricorda il telescopio", "Il telescopio")
        self.store.append_exchange(b.id, "Ricorda il violino", "Il violino")
        reader = make_chat_history_reader(self.store, a.id)
        self.assertEqual(reader(250), "")
        self.assertEqual(reader.recent_pairs(3),
                         ((("user", "Ricorda il telescopio"), ("assistant", "Il telescopio")),))
        self.assertNotIn("violino", str(reader.recent_pairs(3)))
        self.assertIsNone(getattr(reader, "memory_owner", None))

    def test_project_reader_cannot_see_general_or_other_project(self):
        general = self.store.create_chat("Generale")
        p = "a" * 32
        scoped = self.store.create_chat("Progetto", project_id=p)
        self.store.append_exchange(general.id, "Globale", "Segreto")
        self.store.append_exchange(scoped.id, "Progetto", "Specifico", project_id=p)
        reader = make_chat_history_reader(self.store, scoped.id, project_id=p)
        self.assertEqual(reader.recent_pairs(4)[0][0][1], "Progetto")
        with self.assertRaises(ValueError):
            make_chat_history_reader(self.store, general.id, project_id=p)


class NativeScopedHistoryTests(unittest.TestCase):
    def test_jarvis_native_gemma_reuses_only_selected_chat_context(self):
        from local_model.memory_preferences import MemoryPreferences
        from local_model.native_config import NativeModelConfig
        from local_model.native_conversation_session import NativeConversationSession
        from test_native_conversation_session import FakeAdapter

        class CountingAdapter(FakeAdapter):
            def context_token_counter(self):
                return lambda text: max(1, (len(text) + 3) // 4)

        with tempfile.TemporaryDirectory() as temp:
            store = ChatSessionStore(Path(temp) / "scoped.sqlite3")
            alpha = store.create_chat("Stelle")
            beta = store.create_chat("Musica")
            adapter = CountingAdapter()
            def new_session():
                return NativeConversationSession(
                    adapter,
                    config_loader=lambda: NativeModelConfig(
                        context_size=1024, max_output=256),
                    memory_loader=lambda: MemoryPreferences(
                        recent_messages=8, history_max_tokens=250))
            session = new_session()
            reader_a = make_chat_history_reader(store, alpha.id)
            reader_b = make_chat_history_reader(store, beta.id)
            answer_a = session.ask("La stella Arturo", context_id=alpha.id,
                                   memory_context=reader_a)
            store.append_exchange(alpha.id, "La stella Arturo", answer_a)
            answer_b = session.ask("Il violino Stradivari", context_id=beta.id,
                                   memory_context=reader_b)
            store.append_exchange(beta.id, "Il violino Stradivari", answer_b)
            session.ask("Approfondisci Arturo", context_id=alpha.id,
                        memory_context=reader_a)
            self.assertIn("La stella Arturo", adapter.calls[-1])
            self.assertNotIn("Stradivari", adapter.calls[-1])
            # With new Gemma owner, recovery reads only that chat from SQLite.
            session.close()
            adapter = CountingAdapter()
            session = new_session()
            reopened = ChatSessionStore(Path(temp) / "scoped.sqlite3")
            session.ask("Cosa dicevamo di Arturo?", context_id=alpha.id,
                        memory_context=make_chat_history_reader(reopened, alpha.id))
            self.assertIn("La stella Arturo", adapter.calls[-1])
            self.assertNotIn("Stradivari", adapter.calls[-1])
            self.assertNotIn("Ricordi salvati", adapter.calls[-1])
            self.assertEqual(len(adapter.calls), 1)
            session.close()


    def test_partially_evicted_chat_history_is_restored_from_archive(self):
        # Review bug 2 (9/11): shared RAM buffer (16 rows) evicted part of a
        # chat after using another one; the archive must fill the gap.
        from local_model.memory_preferences import MemoryPreferences
        from local_model.native_config import NativeModelConfig
        from local_model.native_conversation_session import NativeConversationSession
        from test_native_conversation_session import FakeAdapter

        class CountingAdapter(FakeAdapter):
            def context_token_counter(self):
                return lambda text: max(1, (len(text) + 3) // 4)

        with tempfile.TemporaryDirectory() as temp:
            store = ChatSessionStore(Path(temp) / "evict.sqlite3")
            alpha, beta = store.create_chat("A"), store.create_chat("B")
            adapter = CountingAdapter()
            session = NativeConversationSession(
                adapter,
                config_loader=lambda: NativeModelConfig(context_size=4096, max_output=256),
                memory_loader=lambda: MemoryPreferences(
                    recent_messages=8, history_max_tokens=600))
            reader_a = make_chat_history_reader(store, alpha.id)
            reader_b = make_chat_history_reader(store, beta.id)
            for n in range(4):
                q = f"Alfa{n}"
                store.append_exchange(alpha.id, q, session.ask(q, context_id=alpha.id,
                                                               memory_context=reader_a))
            for n in range(13):
                q = f"Beta{n}"
                store.append_exchange(beta.id, q, session.ask(q, context_id=beta.id,
                                                              memory_context=reader_b))
            session.ask("Riprendi alfa", context_id=alpha.id, memory_context=reader_a)
            for n in range(4):
                self.assertIn(f"Alfa{n}", adapter.calls[-1])
            self.assertNotIn("Beta", adapter.calls[-1])
            session.close()


class ChatPanelTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: " + str(exc))
        self.root.withdraw()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(self.root.destroy)
        self.path = Path(self.tmp.name) / "sessioni.sqlite3"
        self.scope = [None]
        self.can_change = [True]
        self.changes = []
        self.settings_calls = []
        self.panel = ChatSessionsPanel(
            self.root, store_path=self.path,
            get_project_id=lambda: self.scope[0],
            can_change=lambda: self.can_change[0],
            on_change=lambda old, new: self.changes.append((old, new)),
            on_settings=lambda: self.settings_calls.append(True))
        self.panel.frame.pack(fill="both", expand=True)

    def test_ui_is_lazy_and_first_open_creates_only_one_chat(self):
        self.assertFalse(self.path.exists())
        self.assertIsNone(self.panel.current_target())
        self.assertTrue(self.panel.activate())
        self.assertTrue(self.path.exists())
        first = self.panel.current_target()
        self.assertRegex(first[0], "^[a-f0-9]{32}$")
        self.assertIsNone(first[1])
        self.assertEqual(len(self.panel.store.list_chats()), 1)
        self.assertTrue(self.panel.activate())
        self.assertEqual(self.panel.current_target(), first)
        self.assertEqual(len(self.panel.store.list_chats()), 1)

    def test_new_select_rename_persist_then_reopen(self):
        self.panel.activate()
        first = self.panel.current_target()[0]
        self.panel.persist_answer(first, "Buco nero", "Stella collassata.")
        second = self.panel.create_new()
        self.panel.rename_current(" Serie TV ")
        self.panel.persist_answer(second, "Cosa guardare?", "Sci-fi")
        self.assertIn("Sci-fi", self.panel.view.get("1.0", "end"))
        self.assertNotIn("Stella collassata", self.panel.view.get("1.0", "end"))
        self.panel.select(first)
        self.assertIn("Stella collassata", self.panel.view.get("1.0", "end"))
        self.assertNotIn("Sci-fi", self.panel.view.get("1.0", "end"))
        self.assertEqual(ChatSessionStore(self.path).get_chat(second).title, "Serie TV")
        self.assertEqual(len(ChatSessionStore(self.path).recent_pairs(first)), 1)
        self.assertEqual(len(ChatSessionStore(self.path).recent_pairs(second)), 1)

    def test_busy_switch_prohibited_and_selection_unchanged(self):
        self.panel.activate()
        first = self.panel.current_target()[0]
        self.can_change[0] = False
        self.assertIsNone(self.panel.create_new())
        self.assertEqual(self.panel.current_target()[0], first)
        self.assertEqual(len(self.panel.store.list_chats()), 1)

    def test_project_scope_and_general_are_independent(self):
        self.panel.activate()
        general = self.panel.current_target()[0]
        self.scope[0] = "b" * 32
        self.panel.scope_changed()
        project = self.panel.current_target()
        self.assertNotEqual(general, project[0])
        self.assertEqual(project[1], self.scope[0])
        self.panel.persist_answer(project[0], "Nel progetto", "Esclusivo", project_id=project[1])
        self.scope[0] = None
        self.panel.scope_changed()
        self.assertEqual(self.panel.current_target()[0], general)
        self.assertNotIn("Esclusivo", self.panel.view.get("1.0", "end"))
        self.assertEqual(len(self.panel.store.list_chats()), 1)
        self.assertEqual(len(self.panel.store.list_chats(project_id="b"*32)), 1)

    def test_settings_button_does_not_load_model(self):
        self.panel.activate()
        self.panel.settings_button.invoke()
        self.assertEqual(self.settings_calls, [True])


    def test_sidebar_autotitle_and_full_history_after_reopen(self):
        # 9/11 request: ChatGPT-style list, full transcript after restart.
        self.panel.activate()
        first = self.panel.current_target()[0]
        for n in range(40):
            self.panel.persist_answer(first, f"Domanda {n} sul mare", f"Risposta {n}")
        self.assertEqual(self.panel.store.get_chat(first).title, "Domanda 0 sul mare")
        second = self.panel.create_new()
        self.panel.persist_answer(second, "Ricetta della carbonara", "Guanciale.")
        titles = list(self.panel.chat_list.get(0, "end"))
        self.assertEqual(titles[0], "Ricetta della carbonara")
        self.assertIn("Domanda 0 sul mare", titles)
        # Restart: new panel on the same file shows the whole transcript.
        reopened = ChatSessionsPanel(
            self.root, store_path=self.path, get_project_id=lambda: None,
            can_change=lambda: True, on_change=lambda old, new: None,
            on_settings=lambda: None)
        self.assertTrue(reopened.activate())
        reopened.chat_list.selection_clear(0, "end")
        reopened.chat_list.selection_set(titles.index("Domanda 0 sul mare"))
        reopened._on_list_select()
        text = reopened.view.get("1.0", "end")
        self.assertIn("Domanda 0 sul mare", text)
        self.assertIn("Risposta 39", text)
        self.assertNotIn("GEMMA", text)
        self.assertIn("LUMI", text)
        self.assertFalse(reopened.toggle_sidebar())
        self.assertFalse(reopened.sidebar.winfo_manager())
        self.assertTrue(reopened.toggle_sidebar())
        self.assertEqual(reopened.sidebar.winfo_manager(), "pack")


    def test_failed_save_is_retried_in_order_on_next_answer(self):
        # Review bug 3 (9/11): no silent loss of an unsaved exchange.
        import sqlite3
        from unittest import mock
        self.panel.activate()
        chat = self.panel.current_target()[0]
        original = self.panel.store.append_exchange
        with mock.patch.object(self.panel.store, "append_exchange",
                               side_effect=sqlite3.OperationalError("locked")):
            with self.assertRaises(sqlite3.Error):
                self.panel.persist_answer(chat, "Prima", "Uno")
        self.assertEqual(self.panel.pending_count, 1)
        self.panel.persist_answer(chat, "Seconda", "Due")
        self.assertEqual(self.panel.pending_count, 0)
        self.assertEqual([p[0][1] for p in self.panel.store.recent_pairs(chat)],
                         ["Prima", "Seconda"])
        self.assertIs(self.panel.store.append_exchange.__func__, original.__func__)


if __name__ == "__main__":
    unittest.main()
