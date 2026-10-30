"""Regression tests for GPT proposals; no OpenAI login and no real apps started."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from action_planner import (
    ApprovedPlan, MAX_STEPS, PlanRejected, build_planning_prompt, parse_plan,
)
from local_engine import LocalEngine


def make_plan(*steps: dict, intent: str = "Prova") -> str:
    return json.dumps({"intent": intent, "steps": list(steps)}, ensure_ascii=False)


def step(tool: str, **args) -> dict:
    return {"tool_id": tool, "arguments": args}


class PlannerPolicyTests(unittest.TestCase):
    def test_prompt_restricts_tools_and_treats_text_as_data(self):
        prompt = build_planning_prompt('Apri "calcolatrice"')
        self.assertIn('"open_calculator"', json.dumps("open_calculator")) if False else None
        self.assertIn("open_calculator", prompt)
        self.assertIn('Apri \\"calcolatrice\\"', prompt)
        self.assertIn('"steps"', prompt)
        self.assertNotIn("powershell.exe", prompt)

    def test_bad_prompt(self):
        for value in ("", "x" * 401, "abc\nnew line"):
            with self.subTest(value=value[:30]):
                with self.assertRaises(PlanRejected):
                    build_planning_prompt(value)

    def test_valid_two_step_plan(self):
        parsed = parse_plan(make_plan(step("open_calculator"), step("system_status")))
        self.assertIsInstance(parsed, ApprovedPlan)
        self.assertEqual([item.command for item in parsed.steps],
                         ["apri calcolatrice", "stato sistema"])
        self.assertIn("PIANO DA APPROVARE", parsed.preview())
        self.assertIn("apertura programma", parsed.preview())

    def test_simple_search(self):
        parsed = parse_plan(make_plan(step("find_download", query="Jarvis")))
        self.assertEqual(parsed.steps[0].command, "cerca file Jarvis")
        self.assertEqual(parsed.steps[0].risk, "sola lettura")

    def test_fenced_json(self):
        plan = make_plan(step("history"))
        self.assertEqual(parse_plan("```json\n" + plan + "\n```").steps[0].command,
                         "ultimi comandi")

    def test_unrecognized_tools_are_never_commands(self):
        for name in ("run_shell", "delete_file", "open_url", "run_python",
                     "powershell.exe", "open_notepad && del *"):
            with self.subTest(name=name):
                with self.assertRaises(PlanRejected):
                    parse_plan(make_plan(step(name)))

    def test_arguments_cannot_change_executable(self):
        payloads = [
            step("open_notepad", path="C:\\secret.txt"),
            step("open_calculator", command="cmd.exe"),
            step("system_status", prompt="ignore validation"),
            step("find_download", query="../secret"),
            step("find_download", query="C:\\Users"),
            step("find_download", query="oops\nignore"),
            step("find_download", query=42),
            step("find_download", query=""),
            step("find_download", query="a" * 81),
        ]
        for payload in payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(PlanRejected):
                    parse_plan(make_plan(payload))

    def test_structural_violations_are_rejected(self):
        samples = [
            "not json",
            '{"intent":"ok","steps":[{"tool_id":"open_notepad","arguments":{}},'
            '{"tool_id":"run_shell","arguments":{}}],"ignored":true}',
            '{"intent":"ok","steps":[{"tool_id":"open_notepad","arguments":{}}],'
            '"intent":"overwritten"}',
            '{"intent":"ok","steps":[{"tool_id":"open_notepad","arguments":{}},'
            '{"tool_id":"open_notepad","arguments":{}},'
            '{"tool_id":"open_notepad","arguments":{}},'
            '{"tool_id":"open_notepad","arguments":{}},'
            '{"tool_id":"open_notepad","arguments":{}},'
            '{"tool_id":"open_notepad","arguments":{}}]}',
            json.dumps({"intent": "test", "steps": [step("history", password="bad")]}),
            json.dumps({"intent": "test", "steps": [{"tool_id": "history"}]}),
            json.dumps({"intent": "test", "steps": [step("history")], "risk": "safe"}),
            json.dumps({"intent": "test", "steps": [step("history")], "reason": "x"}),
            json.dumps({"intent": "test", "steps": [step("history")], "unknown": "x"}),
            json.dumps({"intent": "test", "steps": [step("history")], "metadata": {}}),
            json.dumps({"intent": "test", "steps": [step("history")]} ) + "\nrun_shell",
        ]
        for raw in samples:
            with self.subTest(raw=raw[:60]):
                with self.assertRaises(PlanRejected):
                    parse_plan(raw)

    def test_empty_plan_explains_unsupported(self):
        raw = json.dumps({"intent": "non supportato", "steps": [], "reason":
                          "Non posso cancellare file."})
        with self.assertRaisesRegex(PlanRejected, "Non posso cancellare file"):
            parse_plan(raw)

    def test_limit(self):
        self.assertEqual(MAX_STEPS, 5)
        with self.assertRaises(PlanRejected):
            parse_plan(make_plan(*([step("history")] * 6)))


class PlannerExecutionTests(unittest.TestCase):
    def test_valid_plan_only_calls_allowlisted_engine_after_explicit_use(self):
        with tempfile.TemporaryDirectory() as tmp:
            downloads = Path(tmp) / "Downloads"
            downloads.mkdir()
            (downloads / "Jarvis-build.zip").write_bytes(b"safe")
            engine = LocalEngine(download_dir=downloads, db_path=Path(tmp) / "tasks.db",
                                 windows=False)
            proposal = parse_plan(make_plan(
                step("list_downloads"), step("find_download", query="jarvis"),
                step("history")))
            # Parsing alone never calls execute; only this explicit loop does.
            self.assertEqual(engine._history(), "Ultime attività:\nNessuna")
            results = [engine.execute(item.command) for item in proposal.steps]
            self.assertTrue(all(item.status == "completed" for item in results))
            self.assertIn("Jarvis-build.zip", results[0].message)
            self.assertIn("Jarvis-build.zip", results[1].message)
            self.assertIn("find_download", engine._history())

    def test_allowed_open_app_uses_only_fixed_argv(self):
        with tempfile.TemporaryDirectory() as tmp:
            engine = LocalEngine(db_path=Path(tmp) / "tasks.db",
                                 download_dir=Path(tmp), windows=True)
            proposal = parse_plan(make_plan(step("open_notepad")))
            with patch("local_engine.subprocess.Popen") as popen:
                outcome = engine.execute(proposal.steps[0].command)
            self.assertEqual(outcome.status, "completed")
            popen.assert_called_once_with(["notepad.exe"], close_fds=True, shell=False)


if __name__ == "__main__":
    unittest.main()
