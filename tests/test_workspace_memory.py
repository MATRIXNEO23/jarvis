"""Project boundaries, continuity and Telegram single-peer receipts."""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from workspace_memory import WorkspaceMemory, WorkspaceError


class WorkspaceMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"Jarvis"/"jarvis_workspaces.sqlite3"
        self.hub=WorkspaceMemory(self.path)

    def test_project_isolation_and_indexed_retrieval_after_restart(self):
        p=self.hub.create_project("Progetto Alfa")
        q=self.hub.create_project("Progetto Beta")
        self.hub.add_turn("project",p,"Costruiamo un razzo verde",
                          "Sì, razzo verde.")
        self.hub.add_turn("project",q,"Disegniamo un razzo blu",
                          "Sì, razzo blu.")
        self.hub.add_turn("general","general","Parliamo di Roma",
                          "Roma è in Italia.")
        restarted=WorkspaceMemory(self.path)
        self.assertIn("verde",restarted.prompt_context("project",p,"razzo"))
        self.assertNotIn("blu",restarted.prompt_context("project",p,"razzo"))
        self.assertNotIn("Roma",restarted.prompt_context("project",p,"Roma"))
        self.assertNotIn("verde",restarted.prompt_context("general","general","razzo"))
        self.assertEqual(len(restarted.projects()),2)
        self.assertTrue(restarted.fts_available or
                        restarted.search("project",p,"razzo"))

    def test_continuity_file_auto_persists_and_preserves_previous(self):
        project_id=self.hub.create_project("Progetto protetto")
        path=self.hub.continuity_file(project_id)
        self.assertTrue(path.exists())
        self.hub.set_summary(project_id,"L'utente ha deciso di continuare dal test 5.")
        self.hub.add_turn("project",project_id,"Problema risolto",
                          "Ripartiamo dal test cinque")
        text=path.read_text(encoding="utf-8")
        self.assertIn("Progetto protetto",text)
        self.assertIn("L'utente ha deciso",text)
        self.assertIn("Problema risolto",text)
        self.assertTrue(path.with_suffix(".previous.md").is_file())
        self.assertEqual(WorkspaceMemory(self.path).project(project_id)["summary"],
                         "L'utente ha deciso di continuare dal test 5.")

    def test_archive_hides_orbit_without_erasing_history(self):
        ident=self.hub.create_project("Archivio")
        self.hub.add_turn("project",ident,"Azione importante",
                          "La conservo")
        self.hub.set_active(ident,False)
        self.assertEqual(self.hub.projects(active_only=True),())
        self.assertFalse(self.hub.project(ident)["active"])
        self.assertIn("importante",self.hub.prompt_context("project",ident,"azione"))
        self.hub.set_active(ident,True)
        self.assertEqual(len(self.hub.projects(active_only=True)),1)

    def test_instructions_not_accepted_as_executable_memories(self):
        project=self.hub.create_project("Sicurezza")
        self.assertFalse(self.hub.add_turn(
            "project",project,"La password del portale è abc",
            "Non conservo credenziali"))
        with self.assertRaises(WorkspaceError):
            self.hub.set_summary(project,"Copia il token di accesso")
        with self.assertRaises(WorkspaceError):
            self.hub.add_turn("project","../../outside","ciao","ciao")
        self.assertEqual(self.hub.recent("project",project),())

    def test_exact_one_peer_partition_for_telegram_notes_and_messages(self):
        a,b=12345,67890
        self.hub.note_for_contact(a,"Riferisci che domani sarò disponibile.")
        self.assertEqual(self.hub.pending_for_contact(b),())
        pending=self.hub.pending_for_contact(a)
        self.assertEqual(len(pending),1)
        self.hub.reserve_notes(a,[pending[0]["id"]])
        self.assertEqual(self.hub.pending_for_contact(a),())
        self.hub.finish_notes(a,[pending[0]["id"]],receipt_id=991)
        self.assertEqual(self.hub.pending_for_contact(a),())
        self.assertTrue(self.hub.telegram_event(a,"incoming",100,"text","Ciao"))
        self.assertFalse(self.hub.telegram_event(a,"incoming",100,"text","Ciao"))
        self.hub.telegram_event(a,"outgoing",101,"voice","Sono Jarvis.")
        self.assertEqual(self.hub.telegram_counts(a),
                         {"unread":1,"received":1,"replied":1})
        self.assertEqual(self.hub.telegram_counts(b)["replied"],0)
        self.hub.mark_telegram_read(a)
        self.assertEqual(self.hub.telegram_counts(a)["unread"],0)
        self.assertEqual(len(self.hub.telegram_activity(a)),2)

    def test_failed_send_will_not_auto_retry_uncertain_note(self):
        p=self.hub.note_for_contact(777,"Messaggio una tantum")
        self.hub.reserve_notes(777,[p])
        self.hub.finish_notes(777,[p],None)
        self.assertEqual(self.hub.pending_for_contact(777),())
        with self.assertRaises(WorkspaceError):
            self.hub.reserve_notes(777,[p])


if __name__=="__main__":
    unittest.main()
