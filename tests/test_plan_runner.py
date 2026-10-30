"""Plan execution stops at step boundaries when authorization is revoked."""
import unittest
from threading import Event, Lock
from types import SimpleNamespace

from action_planner import parse_plan
from plan_runner import run_approved_plan

PLAN = '{"intent":"controllo","steps":[' + ','.join(
    '{"tool_id":"system_status","arguments":{}}' for _ in range(3)
) + ']}'

class FakeEngine:
    def __init__(self, after_first=None, failing=False):
        self.calls = []
        self.after_first = after_first
        self.failing = failing

    def execute(self, command):
        self.calls.append(command)
        if len(self.calls) == 1 and self.after_first is not None:
            self.after_first()
        return SimpleNamespace(
            status="failed" if self.failing else "completed", message="risposta"
        )

class PlanRunnerTests(unittest.TestCase):
    def run_case(self, *, abort_before=False, cancel_before=False,
                 abort_after_first=False, cancel_after_first=False,
                 failing=False):
        abort, cancel = Event(), Event()
        if abort_before:
            abort.set()
        if cancel_before:
            cancel.set()
        def first():
            if abort_after_first:
                abort.set()
            if cancel_after_first:
                cancel.set()
        engine = FakeEngine(after_first=first, failing=failing)
        events = []
        run_approved_plan(parse_plan(PLAN), engine, Lock(), cancel, abort, events.append)
        return engine.calls, events

    def test_three_steps_only_when_authorized(self):
        calls, events = self.run_case()
        self.assertEqual(len(calls), 3)
        self.assertEqual(events[-1], ("finished", "completato"))

    def test_shutdown_before_first_step(self):
        calls, events = self.run_case(abort_before=True)
        self.assertEqual(calls, [])
        self.assertIn("interrotto", events[-1][1])

    def test_revocation_after_first_step_stops_remaining(self):
        calls, events = self.run_case(abort_after_first=True)
        self.assertEqual(len(calls), 1)
        self.assertIn("interrotto", events[-1][1])

    def test_user_cancellation_stops_remaining(self):
        calls, events = self.run_case(cancel_after_first=True)
        self.assertEqual(len(calls), 1)
        self.assertIn("interrotto", events[-1][1])

    def test_failure_stops_remaining(self):
        calls, events = self.run_case(failing=True)
        self.assertEqual(len(calls), 1)
        self.assertIn("fermato", events[-1][1])

if __name__ == "__main__":
    unittest.main()
