"""Offline regression tests for Telegram's bounded per-contact local history."""
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from telegram_bridge import TelegramBridge, TelegramBridgeError
from workspace_memory import WorkspaceMemory


def fake_voice(text,folder,voice=""):
    output=Path(folder)/"outgoing.ogg"
    output.write_bytes(b"fake")
    return output


class FakeClient:
    def __init__(self,fail=False):
        self.sent=[]
        self.fail=fail

    async def send_file(self,peer,path,voice_note=False):
        if self.fail:
            raise OSError("network failed")
        self.sent.append((peer,voice_note))
        return SimpleNamespace(id=4000+len(self.sent))


class HistoryTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/"Jarvis"/"jarvis_workspaces.sqlite3"
        self.db=WorkspaceMemory(self.path)

    def test_limit_50_and_peer_isolation_after_restart(self):
        for number in range(1,61):
            self.db.telegram_event(123,"incoming",number,"text",f"messaggio {number}")
        self.db.telegram_event(456,"incoming",101,"text","messaggio separato")
        self.assertEqual(len(self.db.telegram_activity(123,limit=100)),50)
        self.assertEqual(self.db.telegram_activity(123)[0]["text"],"messaggio 60")
        self.assertNotIn("messaggio 1",
                         [x["text"] for x in self.db.telegram_activity(123)])
        restarted=WorkspaceMemory(self.path)
        self.assertEqual(len(restarted.telegram_activity(123,limit=100)),50)
        self.assertEqual(restarted.telegram_counts(456)["received"],1)

    def test_context_exactly_four_previous_events_no_historical_search(self):
        for n in range(1,9):
            direction="incoming" if n%2 else "outgoing"
            self.db.telegram_event(123,direction,n,"text",f"msg-{n}")
        result=self.db.telegram_recent_context(123,7)
        self.assertIn("msg-6",result)
        self.assertIn("msg-3",result)
        self.assertNotIn("msg-2",result)
        self.assertNotIn("msg-7",result)
        self.assertNotIn("msg-8",result)
        self.assertEqual(result.count('"da"'),4)
        self.assertNotIn("segreto",result)
        self.assertEqual(self.db.add_turn("telegram","123","test","test"),False)

    def test_export_full_text_and_clear_only_selected_history(self):
        self.db.telegram_event(123,"incoming",1,"text","Un testo completo con dettagli")
        self.db.telegram_event(456,"incoming",2,"text","Non cancellare")
        self.db.note_for_contact(123,"Prossimo promemoria")
        self.db.telegram_mark_introduced(123)
        path=self.db.telegram_export_history(123,"Contatto Uno")
        self.assertTrue(path.exists())
        self.assertIn("Un testo completo con dettagli",path.read_text(encoding="utf-8"))
        self.db.telegram_clear_history(123)
        self.assertFalse(path.exists())
        self.assertEqual(self.db.telegram_counts(123)["received"],0)
        self.assertEqual(self.db.telegram_counts(456)["received"],1)
        self.assertTrue(self.db.pending_for_contact(123))
        self.assertFalse(self.db.telegram_needs_introduction(123))

    def test_migration_backups_old_history_once_and_sets_legacy_intro(self):
        # Simulate a pre-retention version of the real SQLite database.
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute("DELETE FROM workspace_session WHERE key='telegram_retention_50_v1'")
            for n in range(1,65):
                conn.execute("""INSERT INTO telegram_events(
                    peer_id,direction,message_id,kind,text,time_utc)
                    VALUES(?,?,?,?,?,?)""",
                    (123,"outgoing" if n==1 else "incoming",
                     n,"voice",("Sono Jarvis, l'assistente di Alberto" if n==1 else f"old {n}"),"2026-10-31T12:00:00+00:00"))
            conn.execute("""INSERT INTO messages(
                scope,scope_id,user_text,reply,kind,time_utc)
                VALUES('telegram','123','old','duplicate','chat','2026-10-31')""")
            conn.commit()
        migrated=WorkspaceMemory(self.path)
        self.assertEqual(len(migrated.telegram_activity(123,limit=100)),50)
        self.assertFalse(migrated.telegram_needs_introduction(123))
        with closing(sqlite3.connect(self.path)) as conn:
            count=conn.execute("SELECT COUNT(*) FROM messages "
                               "WHERE scope='telegram'").fetchone()[0]
        self.assertEqual(count,0)
        backup=self.path.with_name(self.path.stem+".pre-telegram-50.sqlite3")
        self.assertTrue(backup.exists())
        with closing(sqlite3.connect(backup)) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM telegram_events "
                                          "WHERE peer_id=123").fetchone()[0],64)
        WorkspaceMemory(self.path)
        self.assertEqual(len(migrated.telegram_activity(123,limit=100)),50)

    def test_manual_owner_voice_does_not_count_as_introduction(self):
        self.db.telegram_event(234,"outgoing",9,"voice","Messaggio dettato da Alberto")
        self.assertTrue(self.db.telegram_needs_introduction(234))
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute("DELETE FROM workspace_session WHERE key='telegram_retention_50_v1'")
            conn.commit()
        self.assertTrue(WorkspaceMemory(self.path).telegram_needs_introduction(234))

    def test_full_telegram_text_retained_but_context_is_short(self):
        content="X"*1200
        self.db.telegram_event(123,"incoming",1,"text",content)
        self.db.telegram_event(123,"incoming",2,"text","nuovo")
        self.assertEqual(len(self.db.telegram_activity(123)[-1]["text"]),1200)
        context=self.db.telegram_recent_context(123,2)
        self.assertLess(len(context),250)

    def test_other_scopes_unaffected(self):
        project=self.db.create_project("Mio progetto")
        self.db.add_turn("project",project,"progetto","persistente")
        self.db.add_turn("general","general","ciao","salve")
        self.db.telegram_event(123,"incoming",1,"text","ciao")
        self.db.telegram_clear_history(123)
        self.assertEqual(len(self.db.recent("project",project)),1)
        self.assertEqual(len(self.db.recent("general","general")),1)


class IntroductionTests(unittest.IsolatedAsyncioTestCase):
    async def test_intro_once_even_after_restart_and_no_duplicate_turn_store(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"jarvis_workspaces.sqlite3"
            db=WorkspaceMemory(path)
            bridge=TelegramBridge(db,123,"Amico",
                                  lambda p:"Ciao, sono Jarvis, l'assistente di Alberto. Tutto bene!",
                                  lambda x:None)
            bridge._enabled.set()
            client=FakeClient()
            with patch("telegram_bridge.make_telegram_voice",fake_voice):
                for n in (1,2):
                    event=SimpleNamespace(sender_id=123,
                        message=SimpleNamespace(id=n,voice=False,message="Ciao"))
                    bridge._last_sent[123]=0.0
                    await bridge._handle(client,object(),event)
            outgoing=[x["text"] for x in db.telegram_activity(123,limit=50)
                      if x["direction"]=="outgoing"]
            self.assertEqual(len(outgoing),2)
            self.assertEqual(sum("sono Jarvis" in s for s in outgoing),1)
            self.assertFalse(WorkspaceMemory(path).telegram_needs_introduction(123))
            with closing(sqlite3.connect(path)) as conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM messages "
                                              "WHERE scope='telegram'").fetchone()[0],0)

    async def test_failed_send_does_not_mark_introduced(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=WorkspaceMemory(Path(tmp)/"db.sqlite3")
            bridge=TelegramBridge(db,123,"Amico",lambda p:"Risposta",
                                  lambda x:None)
            bridge._enabled.set()
            event=SimpleNamespace(sender_id=123,
                message=SimpleNamespace(id=1,voice=False,message="Ciao"))
            with patch("telegram_bridge.make_telegram_voice",fake_voice):
                with self.assertRaises(TelegramBridgeError):
                    await bridge._handle(FakeClient(fail=True),object(),event)
            self.assertTrue(db.telegram_needs_introduction(123))


if __name__=="__main__":
    unittest.main()
