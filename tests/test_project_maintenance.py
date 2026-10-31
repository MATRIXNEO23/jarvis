"""Rename/restore project and safe, offline, nonexecuting Jarvis diagnostics."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sqlite3
import unittest

from project_voice import (
    parse_project_voice, project_delete_response, find_existing_project
)
from self_diagnostics import diagnostic_request, inspect_jarvis, format_audit
from workspace_memory import WorkspaceMemory, WorkspaceError


class VoiceMaintenanceTests(unittest.TestCase):
    def test_natural_rename_and_discovery(self):
        cases=(
            ("Jarvis, rinomina il progetto corrente in Colosseo",
             "rename","Colosseo",""),
            ("rinomina il progetto Minecraft in Colosseo",
             "rename","Colosseo","Minecraft"),
            ("cambia il nome del progetto in Filum",
             "rename","Filum",""),
            ("Jarvis, mi puoi rinominare il progetto corrente in Filum",
             "rename","Filum",""),
            ("vorrei cambiare il nome del progetto in Filum",
             "rename","Filum",""),
            ("quali sono i progetti salvati",
             "list","",""),
            ("rinomina progetto","rename","",""),
            ("quali progetti ho salvati?","list","",""),
            ("elenca i progetti salvati","list","",""),
            ("cancella il progetto","trash","",""),
            ("elimina il progetto Minecraft","trash","Minecraft",""),
            ("cestino dei progetti","list_trash","",""),
            ("ripristina progetto Minecraft","restore","Minecraft",""),
        )
        for phrase,action,name,target in cases:
            with self.subTest(phrase=phrase):
                result=parse_project_voice(phrase)
                self.assertIsNotNone(result)
                self.assertEqual((result.action,result.name,result.target),
                                 (action,name,target))
        self.assertIsNone(parse_project_voice(
            "ho sognato di cancellare un progetto"))
        self.assertIsNone(parse_project_voice(
            "se puoi, elimina tutte le cartelle sul computer"))

    def test_trash_confirmation_is_separate_from_intent(self):
        self.assertEqual(project_delete_response("Jarvis confermo"),"confirm")
        self.assertEqual(project_delete_response("annulla"),"cancel")
        for phrase in ("sì","va bene","cancella il progetto", "forse",
                       "conferma di Telegram"):
            with self.subTest(phrase=phrase):
                self.assertIsNone(project_delete_response(phrase))


class DurableProjectMaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"Jarvis"/"jarvis_workspaces.sqlite3"
        self.memory=WorkspaceMemory(self.path)

    def test_rename_preserves_uuid_memory_and_saved_files(self):
        ident=self.memory.create_project("Nome sbagliato")
        self.memory.select_project(ident)
        self.memory.set_summary(ident,"Prova di progetto")
        self.memory.add_turn("project",ident,"Test dell'utente","Risposta")
        ticket=self.memory.begin_step(ident,"Scrivere il progetto")
        self.assertTrue(self.memory.finish_step(
            ident,ticket,"completed","Testato",receipt="local:123"))
        directory=self.memory.project_files_directory(ident)
        saved=directory/"prova.txt"
        saved.write_text("Contenuto da preservare",encoding="utf-8")
        self.assertTrue(self.memory.record_artifact(ident,saved))
        self.assertTrue(self.memory.rename_project(ident,"Nome corretto"))
        self.assertEqual(self.memory.current_project(),ident)
        self.assertEqual(self.memory.project(ident)["name"],"Nome corretto")
        self.assertIn("Nome corretto",(directory.parent/"PROGETTO.txt").read_text(
            encoding="utf-8"))
        self.assertIn("Nome corretto",(directory.parent/"CONTINUITA.md").read_text(
            encoding="utf-8"))
        self.assertIn("Nome corretto",json.loads((directory.parent/"STATO.json").read_text(
            encoding="utf-8"))["name"])
        self.assertEqual(saved.read_text(encoding="utf-8"),
                         "Contenuto da preservare")
        self.assertEqual(self.memory.project_steps(ident)[0]["receipt"],"local:123")
        self.assertEqual(len(self.memory.recent("project",ident,4)),1)
        restart=WorkspaceMemory(self.path)
        self.assertEqual(restart.current_project(),ident)
        self.assertEqual(restart.project(ident)["name"],"Nome corretto")
        self.assertFalse(restart.rename_project(ident,"Nome corretto"))
        with self.assertRaises(WorkspaceError):
            restart.rename_project(ident,"../fuori")

    def test_trash_is_reversible_and_keeps_all_files(self):
        ident=self.memory.create_project("Prova da eliminare")
        self.memory.select_project(ident)
        self.memory.add_turn("project",ident,"Lavoro salvato","Persistente")
        folder=self.memory.project_directory(ident)
        file=self.memory.project_files_directory(ident)/"appunti.txt"
        file.write_text("Non cancellare",encoding="utf-8")
        self.memory.trash_project(ident)
        self.assertTrue(self.memory.project(ident)["trashed"])
        self.assertEqual(self.memory.projects(),())
        self.assertEqual(self.memory.current_project(),None)
        self.assertEqual(self.memory.trashed_projects()[0]["id"],ident)
        self.assertEqual(file.read_text(encoding="utf-8"),"Non cancellare")
        with self.assertRaises(WorkspaceError):
            self.memory.select_project(ident)
        self.assertTrue(folder.is_dir())
        reopened=WorkspaceMemory(self.path)
        self.assertEqual(reopened.trashed_projects()[0]["id"],ident)
        reopened.restore_project(ident)
        self.assertFalse(reopened.project(ident)["trashed"])
        self.assertTrue(reopened.project(ident)["active"])
        self.assertEqual(len(reopened.recent("project",ident,10)),1)
        self.assertEqual(file.read_text(encoding="utf-8"),"Non cancellare")
        self.assertEqual(reopened.trashed_projects(),())

    def test_rename_duplicate_refused_without_losing_original(self):
        p=self.memory.create_project("Alfa")
        q=self.memory.create_project("Beta")
        with self.assertRaises(WorkspaceError):
            self.memory.rename_project(q,"alfa")
        self.assertEqual(self.memory.project(q)["name"],"Beta")
        self.assertEqual(find_existing_project(self.memory.projects(),"Alfa")["id"],p)

    def test_schema_upgrade_preserves_prior_record(self):
        self.memory.create_project("Un progetto precedente")
        with sqlite3.connect(self.path) as db:
            self.assertIn("trashed", [c[1] for c in
                                      db.execute("PRAGMA table_info(projects)")])
        restored=WorkspaceMemory(self.path)
        self.assertEqual(len(restored.projects()),1)


class StaticDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/"program"
        self.root.mkdir()

    def test_utterance_intents_and_no_remote_source_interpretation(self):
        self.assertEqual(diagnostic_request("Jarvis, analizza il tuo codice"),
                         ("overview",""))
        self.assertEqual(diagnostic_request("Jarvis, dove sono i tuoi file"),
                         ("paths",""))
        self.assertEqual(diagnostic_request("analizza workspace_memory.py"),
                         ("module","workspace_memory.py"))
        self.assertIsNone(diagnostic_request(
            "Analizza la password che ho sul computer"))
        self.assertIsNone(diagnostic_request(
            "Modifica da solo il tuo programma e riavvialo"))

    def test_static_inspection_does_not_execute_or_open_secrets(self):
        (self.root/"jarvis.py").write_text(
            'from pathlib import Path\nPath("DANGEROUS").write_text("oops")\n'
            'def main():\n    return 1\n',encoding="utf-8")
        (self.root/"settings.json").write_text(
            '{"api_hash": "SUPERSECRET"}',encoding="utf-8")
        (self.root/"broken.py").write_text("def oops(:",encoding="utf-8")
        result=inspect_jarvis(source_root=self.root,
                              data_root=self.root.parent/"private")
        report=format_audit(result)
        self.assertIn("broken.py",report)
        self.assertIn("sintassi",report)
        self.assertNotIn("SUPERSECRET",report)
        self.assertFalse((self.root/"DANGEROUS").exists())
        single=inspect_jarvis(source_root=self.root,module="jarvis.py")
        self.assertIn("main",single.detail)
        self.assertIn("Modulo jarvis.py",single.summary)
        with self.assertRaises(ValueError):
            inspect_jarvis(source_root=self.root,module="../../settings.json")


if __name__=="__main__":
    unittest.main()
