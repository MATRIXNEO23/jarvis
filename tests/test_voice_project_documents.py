"""Voice-first projects and contextual non-destructive Notepad saves."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from managed_documents import ManagedDocuments
from project_documents import (
    parse_simple_save,project_save_destination,suggested_filename,
)
from project_voice import (
    parse_project_voice,find_existing_project,safe_project_name,
)
from workspace_memory import WorkspaceMemory
from notepad_controller import NotepadSession


class FakeNotepadBridge:
    def __init__(self):
        self.notes={}
        self.closed=[]
        self.counter=0

    def open_blank(self):
        self.counter+=1
        ident="jarvis-note-"+str(self.counter)
        session=NotepadSession(ident,100+self.counter,200+self.counter,
                              300+self.counter,object())
        self.notes[ident]=""
        return session

    def read(self,note):
        return self.notes[note.ident]

    def write(self,note,text):
        self.notes[note.ident]=text

    def close(self,note,*,discard_confirmed):
        assert discard_confirmed
        self.closed.append(note.ident)
        del self.notes[note.ident]


class ProjectVoiceTests(unittest.TestCase):
    def test_create_and_open_by_voice_without_gpt(self):
        for phrase in (
                "Jarvis, crea un progetto chiamato Minecraft",
                "creami un nuovo progetto Minecraft",
                "vorrei creare un progetto chiamato Minecraft"):
            with self.subTest(phrase=phrase):
                action=parse_project_voice(phrase)
                self.assertEqual(action.action,"create")
                self.assertEqual(action.name,"Minecraft")
        self.assertEqual(parse_project_voice("crea un progetto").name,"")
        self.assertEqual(parse_project_voice(
            "Ehi Jarvis apri il progetto Minecraft").action,"open")
        self.assertEqual(parse_project_voice(
            "torniamo alla conversazione generale").action,"general")
        self.assertEqual(parse_project_voice(
            "quali sono i progetti attivi").action,"list")
        self.assertEqual(parse_project_voice(
            "apri la cartella del progetto").action,"folder")
        self.assertIsNone(parse_project_voice("crea un racconto su Minecraft"))
        self.assertIsNone(parse_project_voice("mi chiedi di creare un progetto?"))

    def test_ambiguous_names_are_not_silently_selected(self):
        with self.assertRaises(ValueError):
            safe_project_name("../../secret")
        with self.assertRaises(ValueError):
            safe_project_name("password segreta")
        items=[{"id":"one","name":"Minecraft"},{"id":"two","name":"MINECRAFT"}]
        with self.assertRaises(ValueError):
            find_existing_project(items,"minecraft")
        self.assertIsNone(find_existing_project(items,"Filum"))


class ProjectDocumentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace=WorkspaceMemory(
            Path(self.tmp.name)/"Jarvis"/"jarvis_workspaces.sqlite3")
        self.project_id=self.workspace.create_project("Minecraft")

    def test_new_project_has_separate_workspace_and_work_files(self):
        folder=self.workspace.project_directory(self.project_id)
        files=self.workspace.project_files_directory(self.project_id)
        self.assertEqual(folder.parent.name,"projects")
        self.assertEqual(files,folder/"files")
        self.assertTrue((folder/"PROGETTO.txt").is_file())
        self.assertIn("Minecraft",(folder/"PROGETTO.txt").read_text(encoding="utf-8"))
        self.assertTrue((folder/"CONTINUITA.md").is_file())

    def test_filename_from_real_request_not_random_or_fixed(self):
        self.assertEqual(
            suggested_filename("scrivi un testo sulla costruzione del Colosseo",
                               "Minecraft"),"costruzione-colosseo.txt")
        self.assertEqual(
            suggested_filename("","Minecraft"),"appunti-minecraft.txt")
        self.assertEqual(
            suggested_filename("","Minecraft",explicit_name="mia nota"),
            "mia nota.txt")
        with self.assertRaises(ValueError):
            suggested_filename("","Minecraft",explicit_name="../privato")

    def test_save_then_save_new_version_without_overwriting(self):
        bridge=FakeNotepadBridge()
        document=ManagedDocuments(bridge)
        doc=document.compose("Prima versione", "new_notepad")
        destination=project_save_destination(
            self.workspace,self.project_id,"scrivi un testo sulla costruzione")
        self.assertEqual(destination.parent,
                         self.workspace.project_files_directory(self.project_id))
        saved=document.save_only(doc.document_id,destination)
        self.assertEqual(saved.kind,"saved_open")
        self.assertIsNotNone(document.current)
        self.assertEqual(saved.saved_path.read_text(encoding="utf-8"),
                         "Prima versione")
        self.assertIn("già salvato",
                      document.save_only(doc.document_id,destination).message)
        bridge.notes[doc.document_id]="Seconda versione"
        updated=project_save_destination(
            self.workspace,self.project_id,"scrivi un testo sulla costruzione")
        self.assertNotEqual(updated,destination)
        saved2=document.save_only(doc.document_id,updated)
        self.assertEqual(saved2.kind,"saved_open")
        self.assertEqual(destination.read_text(encoding="utf-8"),"Prima versione")
        self.assertEqual(updated.read_text(encoding="utf-8"),"Seconda versione")
        self.assertFalse(bridge.closed)
        self.assertTrue(self.workspace.record_artifact(self.project_id,updated))
        self.assertIn(updated.name,(self.workspace.project_directory(
            self.project_id)/"ARTIFATTI.md").read_text(encoding="utf-8"))

    def test_save_words_do_not_close_and_do_not_parse_unrelated_commands(self):
        self.assertEqual(parse_simple_save("Jarvis salva"),"")
        self.assertEqual(parse_simple_save("salva il documento"),"")
        self.assertEqual(parse_simple_save("salva come testo delle idee"),"testo delle idee")
        self.assertIsNone(parse_simple_save("salva e chiudi"))
        self.assertIsNone(parse_simple_save("quando devo salvare?"))
        self.assertIsNone(parse_simple_save("chiudi senza salvare"))


if __name__=="__main__":
    unittest.main()
