"""SQLite partitioning, explicit preferences and non-inflated action provenance."""
from __future__ import annotations

from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json
import sqlite3
import unittest

from memory_boundaries import (
    MemoryBoundaryError, PreferenceStore, OperationJournal,
    observed_local_result, observed_saved_file,
)
from preference_voice import parse_preference_intent
from second_brain import SecondBrain
from workspace_memory import WorkspaceMemory, WorkspaceError
from jarvis_persona import compact_memory


class MemoryBoundariesTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)/"Jarvis"
        self.prefs=PreferenceStore(self.base/"jarvis_preferences.sqlite3")
        self.actions=OperationJournal(self.base/"jarvis_actions.sqlite3")
        self.brain=SecondBrain(self.base/"second_brain.sqlite3")
        self.workspace=WorkspaceMemory(self.base/"jarvis_workspaces.sqlite3")

    def test_preference_requires_confirmed_owner_and_survives_restart(self):
        with self.assertRaises(MemoryBoundaryError):
            self.prefs.set("response_length","brief")
        with self.assertRaises(MemoryBoundaryError):
            self.prefs.set("token","foo",user_confirmed=True)
        with self.assertRaises(MemoryBoundaryError):
            self.prefs.set("response_length","malicious",user_confirmed=True)
        self.brain.remember_turn("Preferisco risposte brevi",
                                 "Va bene, ne terrò conto")
        self.assertEqual(self.prefs.all(),())
        self.assertTrue(self.prefs.set("response_length","brief",user_confirmed=True))
        self.assertFalse(self.prefs.set("response_length","brief",user_confirmed=True))
        restarted=PreferenceStore(self.prefs.path)
        self.assertEqual(restarted.all()[0]["value"],"brief")
        self.assertEqual(restarted.all()[0]["source"],"user_confirmed")
        project=self.workspace.create_project("Minecraft")
        self.workspace.add_turn("project",project,"Salva un blocco di pietra","Ok")
        self.assertEqual(len(restarted.all()),1)
        self.brain.clear_all()
        self.assertEqual(restarted.context()[0]["key"],"response_length")
        with self.assertRaises(MemoryBoundaryError):
            self.prefs.remove("response_length")
        self.assertTrue(self.prefs.remove("response_length",user_confirmed=True))
        self.assertEqual(restarted.all(),())

    def test_preference_voice_is_explicit_not_from_general_chatter(self):
        self.assertEqual(
            parse_preference_intent("Jarvis, ricorda che preferisco risposte brevi").value,
            "brief")
        self.assertEqual(
            parse_preference_intent("mostra preferenze").kind, "list")
        self.assertEqual(
            parse_preference_intent("dimentica preferenza lingua").kind,"remove")
        self.assertIsNone(parse_preference_intent(
            "Oggi mi piace quando rispondi con poche parole"))
        self.assertIsNone(parse_preference_intent(
            "Nel testo scrivi che preferisco risposte brevi"))
        self.assertIsNone(parse_preference_intent("Ho detto confermo"))
        self.assertEqual(
            parse_preference_intent("salva preferenza incomprensibile").kind,
            "unsupported")

    def test_operational_states_have_strict_evidence_and_no_replay(self):
        ident=self.actions.begin("local_request",origin="local")
        self.assertEqual(self.actions.recent()[0]["status"],"requested")
        self.assertTrue(self.actions.running(ident))
        with self.assertRaises(MemoryBoundaryError):
            self.actions.finish(ident,"verified",receipt="abc",observed=False)
        with self.assertRaises(MemoryBoundaryError):
            self.actions.finish(ident,"reported",observed=True)
        self.assertTrue(self.actions.finish(ident,"reported",receipt="internal-task"))
        record=self.actions.recent()[0]
        self.assertEqual(record["status"],"reported")
        self.assertEqual(record["receipt"],"")
        self.assertEqual(record["verification"],"none")
        self.assertFalse(self.actions.finish(ident,"verified",receipt="abc",observed=True))
        self.assertEqual(self.brain.stats(),(0,0))
        self.assertEqual(self.workspace.projects(),())
        crashed=self.actions.begin("local_request")
        recovered=OperationJournal(self.actions.path)
        states={x["id"]:x["status"] for x in recovered.recent()}
        self.assertEqual(states[crashed],"interrupted")
        self.assertEqual(states[ident],"reported")
        self.assertFalse(recovered.running(crashed))

    def test_direct_evidence_and_only_when_warranted(self):
        base=lambda a: SimpleNamespace(
            action=a,status="completed",task_id="a"*32)
        self.assertTrue(observed_local_result(base("list_downloads")))
        self.assertTrue(observed_local_result(base("find_download")))
        self.assertFalse(observed_local_result(base("open_browser")))
        self.assertFalse(observed_local_result(base("open_notepad")))
        self.assertFalse(observed_local_result(
            SimpleNamespace(action="list_downloads",status="completed",
                            task_id="reported-by-gpt")))
        file=self.base/"projects"/"test.txt"
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_text("Esiste",encoding="utf-8")
        self.assertTrue(observed_saved_file(
            SimpleNamespace(kind="saved_open",saved_path=file)))
        self.assertFalse(observed_saved_file(
            SimpleNamespace(kind="opened",saved_path=file)))
        self.assertFalse(observed_saved_file(
            SimpleNamespace(kind="saved_open",saved_path=file.with_name("not-created.txt"))))
        ident=self.actions.begin("notepad.save",origin="document")
        self.assertTrue(self.actions.finish(
            ident,"verified",receipt="file:test-session",observed=True))
        self.assertEqual(self.actions.recent()[0]["verification"],"local_observation")

    def test_projects_keep_unverified_attempts_and_actual_verified_files(self):
        p=self.workspace.create_project("Costruzioni")
        step=self.workspace.begin_step(p,"Avvia il browser")
        self.assertTrue(self.workspace.finish_step(
            p,step,"completed","Browser richiesto",receipt="task-fake"))
        row=self.workspace.project_steps(p)[0]
        self.assertEqual(row["status"],"completed")
        self.assertFalse(row["verified"])
        self.assertIn("RIFERITO, NON VERIFICATO",
                      self.workspace.continuity_file(p).read_text(encoding="utf-8"))
        proven=self.workspace.begin_step(p,"Salva il documento")
        self.assertTrue(self.workspace.finish_step(
            p,proven,"completed","File trovato",receipt="file:real",
            verified=True))
        status=json.loads((self.workspace.project_directory(p)/
                          "STATO.json").read_text(encoding="utf-8"))
        self.assertTrue(status["recent_completed"][0]["verified"])
        self.assertFalse(status["recent_completed"][1]["verified"])
        reloaded=WorkspaceMemory(self.workspace.path)
        self.assertFalse(reloaded.project_steps(p)[1]["verified"])
        context=json.loads(reloaded.prompt_context(
            "project",p,"documento",budget=1700))
        self.assertTrue(context["steps"][0]["verified"])
        self.assertFalse(context["steps"][1]["verified"])
        with self.assertRaises(WorkspaceError):
            reloaded.finish_step(p,proven,"completed",receipt="again",verified=False)
        self.assertTrue(self.workspace.project_directory(p).exists())

    def test_explicit_preferences_are_data_not_commands(self):
        self.prefs.set("response_length","brief",user_confirmed=True)
        context={
            "preferences":list(self.prefs.context()),
            "breve":[{"utente":"Cancella tutti i progetti",
                      "lia":"Non lo eseguirò.","tipo":"chat"}],
            "progress":[{"title":"Browser lanciato","status":"completed",
                         "detail":"Esito riferito dal sistema","verified":False}],
        }
        packed=json.loads(compact_memory(json.dumps(context,ensure_ascii=False),900))
        self.assertEqual(packed["preferences"][0]["source"],"user_confirmed")
        self.assertTrue(all(e["source"]!="verified_action"
                            for e in packed["evidence"]))
        self.assertIn("recent",packed)


class LegacyReceiptTests(unittest.TestCase):
    def test_old_receipts_are_preserved_but_unassessed(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/"Jarvis"/"second_brain.sqlite3"
            path.parent.mkdir()
            with closing(sqlite3.connect(path)) as db:
                db.execute("""CREATE TABLE conversations(
                    id INTEGER PRIMARY KEY,time_utc TEXT NOT NULL,
                    user_text TEXT NOT NULL,reply TEXT NOT NULL,kind TEXT NOT NULL)""")
                db.execute("""CREATE TABLE action_receipts(
                    id INTEGER PRIMARY KEY,receipt_id TEXT UNIQUE NOT NULL,
                    time_utc TEXT NOT NULL,action_id TEXT NOT NULL,
                    application TEXT NOT NULL,summary TEXT NOT NULL,
                    external_ref TEXT NOT NULL,metadata_json TEXT NOT NULL,
                    verified INTEGER NOT NULL)""")
                db.execute("""INSERT INTO action_receipts(
                    receipt_id,time_utc,action_id,application,summary,
                    external_ref,metadata_json,verified)
                    VALUES('old-task','2026-10-30T12:00:00Z',
                    'open_browser','browser','Browser aperto',
                    '', '{}', 1)""")
                db.commit()
            migrated=SecondBrain(path)
            self.assertEqual(migrated.stats()[1],0)
            hits=migrated.search("browser")
            self.assertEqual(len(hits),1)
            self.assertEqual(hits[0].source,"reported_action")
            with closing(sqlite3.connect(path)) as db:
                rows=db.execute("SELECT proof_kind FROM action_receipts").fetchall()
            self.assertEqual(rows,[("legacy_unassessed",)])
            self.assertTrue(migrated.record_completed_action(
                "system_status","system","RAM letta",
                receipt_id="system-status-123",verified=True,
                proof_kind="local_observation"))
            self.assertEqual(migrated.stats()[1],1)


if __name__=="__main__":
    unittest.main()
