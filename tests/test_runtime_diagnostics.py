"""Read-only runtime observations must not become fake proof or private data."""
import json
from pathlib import Path
import unittest

from runtime_diagnostics import (
    RuntimeEventCounters, RuntimeEvidence, collect_runtime_evidence,
    format_runtime_evidence, safe_runtime_payload,
)
from diagnostic_handoff import build_external_review_prompt, safe_audit_payload
from self_diagnostics import SourceAudit


def capture(counters=None, **changes):
    data = dict(
        gpt_enabled=True, gpt_connected=True, sdk_installed=True,
        node_available=True, bridge_file_present=True, bridge_running=True,
        voice_present=True, voice_mode="conversazione_gpt",
        voice_listening=True, voice_model_present=True,
        local_engine_present=True, local_store_present=True,
        workspace_present=True, workspace_store_present=True,
        counters=counters if counters is not None else RuntimeEventCounters(),
    )
    data.update(changes)
    return collect_runtime_evidence(**data)


class RuntimeEvidenceTests(unittest.TestCase):
    def test_actual_observations_and_no_mutations(self):
        events = RuntimeEventCounters()
        events.record("gpt_failure")
        events.record("local_failure")
        events.record("unrecognized confidential category")
        report = capture(events)
        data = safe_runtime_payload(report)
        self.assertEqual(data["scope"], "current_process_observation_only")
        self.assertEqual(len(data["checks"]), 4)
        self.assertEqual(data["checks"][0], {
            "component": "gpt_link", "state": "ready",
            "evidence": "gpt_connected_observed",
        })
        self.assertEqual(data["incident_counts"]["gpt_failure"], 1)
        self.assertNotIn("unrecognized", str(data))
        self.assertIn("non test funzionali", format_runtime_evidence(report))

    def test_standby_is_not_a_failure_and_audio_not_faked(self):
        standby = capture(voice_mode="standby", voice_listening=False)
        self.assertEqual(standby.checks[1], (
            "voice_input", "idle", "voice_standby"))
        ptt = capture(voice_mode="premi_per_parlare", voice_listening=False)
        self.assertEqual(ptt.checks[1], (
            "voice_input", "idle", "voice_push_to_talk_idle"))
        requested = capture(voice_listening=False)
        self.assertEqual(requested.checks[1], (
            "voice_input", "attention", "mic_not_observed"))

    def test_gpt_is_external_and_idle_not_automatically_faulty(self):
        disconnected = capture(gpt_connected=False, bridge_running=False)
        self.assertEqual(disconnected.checks[0], (
            "gpt_link", "idle", "gpt_not_connected"))
        disabled = capture(gpt_enabled=False, gpt_connected=False)
        self.assertEqual(disabled.checks[0], (
            "gpt_link", "idle", "gpt_disabled"))
        stopped = capture(gpt_connected=True, bridge_running=False)
        self.assertEqual(stopped.checks[0], (
            "gpt_link", "attention", "bridge_not_running"))
        sdk_missing = capture(sdk_installed=False)
        self.assertEqual(sdk_missing.checks[0][2], "sdk_missing")

    def test_probes_do_not_expose_private_text_or_paths(self):
        fake = RuntimeEvidence((
            ("gpt_link", "ready", "C:\\Users\\private\\secret"),
            ("gpt_link", "ready", "gpt_connected_observed"),
            ("project_memory", "ready", "project_store_present"),
            ("private_project", "ready", "project_store_present"),
        ), (("gpt_failure", 1000000),
            ("api_hash_private", 98),
            ("local_failure", -17)))
        data = safe_runtime_payload(fake)
        self.assertEqual(len(data["checks"]), 2)
        self.assertEqual(data["incident_counts"]["gpt_failure"], 99)
        self.assertEqual(data["incident_counts"]["local_failure"], 0)
        for secret in ("C:\\Users", "private_project", "api_hash_private"):
            self.assertNotIn(secret, json.dumps(data))

    def test_external_prompt_only_contains_safe_codes(self):
        events = RuntimeEventCounters()
        events.record("gpt_failure")
        audit = SourceAudit("SECRET USER", "PRIVATE PATH", ())
        evidence = capture(events)
        data = safe_audit_payload(audit, runtime_evidence=evidence)
        self.assertFalse(data["functional_tests_performed"])
        self.assertFalse(data["runtime_logs_read"])
        self.assertEqual(data["observed_runtime"]["incident_counts"]["gpt_failure"], 1)
        prompt = build_external_review_prompt(audit, runtime_evidence=evidence)
        self.assertLessEqual(len(prompt), 4800)
        self.assertIn("gpt_connected_observed", prompt)
        self.assertNotIn("SECRET USER", prompt)
        self.assertNotIn("PRIVATE PATH", prompt)
        self.assertTrue(prompt.endswith("}"))

    def test_consent_and_state_binding_in_ui_source(self):
        src = (Path(__file__).resolve().parent.parent / "jarvis.py").read_text(encoding="utf-8")
        block = src.split("    def offer_external_diagnostic_review() -> bool:", 1)[1]
        block = block.split("    def update_diagnostic_ui()", 1)[0]
        self.assertLess(block.index("messagebox.askyesno("),
                        block.index('run_gpt("ask"'))
        self.assertIn("last_runtime_evidence", block)
        self.assertIn("runtime_events.record", src)
        self.assertIn("snapshot_runtime_evidence()", src)
        self.assertIn("last_runtime_evidence=None", src)
        self.assertIn('last_diagnostic_audit=audit', src)


if __name__ == "__main__":
    unittest.main()
