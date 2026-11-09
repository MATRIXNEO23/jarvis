"""Capability catalog security and schema: pure tests, never start Windows."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from capability_registry import (
    CapabilityRejected, capability_prompt, load_catalog, resolve_capability,
)


class CapabilityRegistryTests(unittest.TestCase):
    def test_all_described_actions_have_a_reviewed_implementation(self):
        entries = load_catalog()
        names = {entry["id"] for entry in entries}
        self.assertEqual(len(entries), len(names))
        self.assertIn("notepad.close", names)
        self.assertIn("explorer.drive_c", names)
        self.assertIn("browser.search", names)
        self.assertNotIn("shell.run", names)

    def test_contextual_prompt_hides_notepad_close_without_document(self):
        self.assertNotIn('"id":"notepad.close"', capability_prompt(has_document=False))
        self.assertIn('"id":"notepad.close"', capability_prompt(has_document=True))
        self.assertIn("chiudimi Blocco note", capability_prompt(has_document=True))

    def test_local_bindings_use_existing_planner_allowlist(self):
        test_cases = (
            ("explorer.drive_c", {}, "apri disco locale c"),
            ("explorer.downloads", {}, "apri download"),
            ("calculator.open", {}, "apri calcolatrice"),
            ("system.status", {}, "stato sistema"),
            ("browser.search", {"query": "Roma antica"},
             "cerca nel browser Roma antica"),
            ("downloads.find", {"query": "Jarvis"}, "cerca file Lumi"),
        )
        for name, args, expected in test_cases:
            with self.subTest(name=name):
                proposal = resolve_capability(name, args)
                self.assertEqual(proposal.handler, "local")
                self.assertEqual(proposal.plan.steps[0].command, expected)

    def test_only_owned_notepad_can_be_closed(self):
        with self.assertRaises(CapabilityRejected):
            resolve_capability("notepad.close", {})
        closed = resolve_capability("notepad.close", {}, has_document=True)
        self.assertEqual(closed.handler, "document_close")
        self.assertIsNone(closed.plan)
        for args in ({"force": True}, {"discard": True},
                     {"process": "notepad.exe"}, {"save": False}):
            with self.subTest(args=args):
                with self.assertRaises(CapabilityRejected):
                    resolve_capability("notepad.close", args, has_document=True)

    def test_document_writing_requires_safe_target(self):
        sample = {"target": "selected_document", "content": "Testo originale"}
        with self.assertRaises(CapabilityRejected):
            resolve_capability("notepad.write", sample, has_document=False)
        answer = resolve_capability("notepad.write", sample, has_document=True)
        self.assertEqual(answer.content, sample["content"])
        self.assertEqual(answer.target, "selected_document")
        with self.assertRaises(CapabilityRejected):
            resolve_capability("notepad.write", {
                "target": "C:/Users/Documenti",
                "content": "Testo"}, has_document=True)

    def test_unknown_ids_or_unexpected_arguments_cannot_run(self):
        checks = (
            ("shell.run", {"command": "echo hi"}),
            ("notepad.force_close", {}),
            ("explorer.drive_c", {"path": "C:/Windows"}),
            ("browser.open", {"url": "https://example.net"}),
            ("calculator.open", {"executable": "cmd.exe"}),
            ("downloads.find", {"query": "../private"}),
            ("browser.search", {"query": "linea\nseconda"}),
            ("notepad.write", {"target": "new_notepad",
                               "content": "x" * 4501}),
        )
        for ident, args in checks:
            with self.subTest(ident=ident):
                with self.assertRaises(CapabilityRejected):
                    resolve_capability(ident, args)

    def test_json_file_cannot_grant_a_new_executable_action(self):
        with TemporaryDirectory() as folder:
            file = Path(folder) / "catalog.json"
            original = json.loads(
                Path(__file__).resolve().parents[1].joinpath(
                    "jarvis_commands.json").read_text(encoding="utf-8"))
            file.write_text(json.dumps(original), encoding="utf-8")
            self.assertEqual(len(load_catalog(file)), len(original["actions"]))
            original["actions"][0]["id"] = "shell.run"
            file.write_text(json.dumps(original), encoding="utf-8")
            with self.assertRaises(CapabilityRejected):
                load_catalog(file)
            original["actions"][0]["id"] = "notepad.open"
            original["actions"][1]["id"] = "notepad.open"
            file.write_text(json.dumps(original), encoding="utf-8")
            with self.assertRaises(CapabilityRejected):
                load_catalog(file)


if __name__ == "__main__":
    unittest.main()
