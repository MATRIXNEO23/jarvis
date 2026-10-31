"""Durable, incremental project continuity; no live GPT, Telegram or audio."""
import json
from pathlib import Path
import tempfile
import unittest

from workspace_memory import WorkspaceError, WorkspaceMemory


class AutomaticContinuityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dbpath = Path(self.temp.name) / "Jarvis" / "jarvis_workspaces.sqlite3"
        self.memory = WorkspaceMemory(self.dbpath)

    def test_project_creates_operational_files_without_manual_save(self):
        ident = self.memory.create_project("Cantiere Minecraft")
        folder = self.memory.continuity_file(ident).parent
        for name in ("CONTINUITA.md", "STATO.json", "PASSI.md",
                     "ARTIFATTI.md", "EVENTI.jsonl"):
            self.assertTrue((folder / name).is_file(), name)
        self.assertTrue((folder / "files").is_dir())
        state = json.loads((folder / "STATO.json").read_text(encoding="utf-8"))
        self.assertEqual(state["project_id"], ident)
        self.assertFalse(state["unfinished"])

    def test_each_step_is_recorded_and_verified_immediately(self):
        ident = self.memory.create_project("Mod")
        ticket = self.memory.begin_step(ident, "Compilazione mod", source="local")
        state = json.loads((self.memory.continuity_file(ident).parent /
                            "STATO.json").read_text(encoding="utf-8"))
        self.assertEqual(state["unfinished"][0]["status"], "running")
        self.assertTrue(self.memory.finish_step(
            ident, ticket, "completed", "Compilazione terminata", receipt="task:42"))
        self.assertFalse(self.memory.finish_step(
            ident, ticket, "completed", "Duplicato", receipt="task:42"))
        continuity = self.memory.continuity_file(ident).read_text(encoding="utf-8")
        self.assertIn("[COMPLETED] Compilazione mod", continuity)
        self.assertIn("Compilazione terminata", continuity)
        self.assertEqual(self.memory.project_steps(ident)[0]["receipt"], "task:42")
        events = (self.memory.continuity_file(ident).parent /
                  "EVENTI.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual([json.loads(x)["status"] for x in events],
                         ["running", "completed"])

    def test_cannot_claim_success_without_receipt(self):
        ident = self.memory.create_project("Verifica")
        ticket = self.memory.begin_step(ident, "Test da fare")
        with self.assertRaises(WorkspaceError):
            self.memory.finish_step(ident, ticket, "completed", "Fatto")
        self.assertEqual(self.memory.project_steps(ident)[0]["status"], "running")

    def test_restart_marks_unresolved_as_interrupted_not_completed(self):
        ident = self.memory.create_project("Interruzione")
        first = self.memory.begin_step(ident, "Passo già autorizzato", planned=True)
        second = self.memory.begin_step(ident, "Passo in esecuzione")
        reopened = WorkspaceMemory(self.dbpath)
        states = {x["id"]: x["status"] for x in reopened.project_steps(ident)}
        self.assertEqual(states[first], "interrupted")
        self.assertEqual(states[second], "interrupted")
        self.assertFalse(reopened.finish_step(
            ident, second, "completed", "Passo mai verificato", receipt="fake"))
        self.assertIn("interrupted", (reopened.continuity_file(ident).parent /
                                      "PASSI.md").read_text(encoding="utf-8"))

    def test_isolates_project_operations_and_conversation(self):
        p = self.memory.create_project("Alfa")
        q = self.memory.create_project("Beta")
        ticket = self.memory.begin_step(p, "Correggere un bug", source="planner",
                                        planned=True)
        self.memory.add_turn("project", p, "Stiamo correggendo", "In prova")
        self.memory.add_turn("project", q, "Preparare grafica", "Da eseguire")
        self.memory.finish_step(p, ticket, "failed", "Test non passato")
        self.assertEqual(self.memory.project_steps(q), ())
        self.assertNotIn("Correggere un bug", self.memory.prompt_context(
            "project", q, "bug", budget=1600))
        self.assertIn("failed", self.memory.prompt_context(
            "project", p, "bug", budget=1600))
        self.assertIn("grafica", self.memory.prompt_context(
            "project", q, "grafica", budget=1600))

    def test_register_only_existing_file_and_rebuild_stale_snapshot(self):
        ident = self.memory.create_project("Documenti")
        candidate = Path(self.temp.name) / "report.txt"
        with self.assertRaises(FileNotFoundError):
            self.memory.record_artifact(ident, candidate)
        candidate.write_text("Esito verificato", encoding="utf-8")
        self.assertTrue(self.memory.record_artifact(ident, candidate))
        self.assertFalse(self.memory.record_artifact(ident, candidate))
        artifacts = (self.memory.continuity_file(ident).parent /
                     "ARTIFATTI.md").read_text(encoding="utf-8")
        self.assertIn("report.txt", artifacts)
        state_path = self.memory.continuity_file(ident).parent / "STATO.json"
        state_path.write_text('{"schema_version":0}', encoding="utf-8")
        recovered = WorkspaceMemory(self.dbpath)
        self.assertEqual(json.loads(state_path.read_text(encoding="utf-8"))[
            "schema_version"], 1)
        self.assertIn("report.txt", recovered.continuity_file(ident).read_text(
            encoding="utf-8"))

    def test_secret_does_not_enter_project_journal(self):
        ident = self.memory.create_project("Privato")
        with self.assertRaises(WorkspaceError):
            self.memory.begin_step(ident, "Salva password segreta")
        self.assertEqual(self.memory.project_steps(ident), ())


if __name__ == "__main__":
    unittest.main()
