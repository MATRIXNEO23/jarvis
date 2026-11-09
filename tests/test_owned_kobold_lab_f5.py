"""F5.3b.2 hermetic lab controller tests; no process, network or GGUF."""
import unittest
from unittest.mock import Mock

from local_model.kobold_server_canary import KoboldCanaryError
from local_model.owned_kobold_lab_f5 import OwnedKoboldLab, LabServerError


def owner(*, responses, running=True, port_free=True):
    process = Mock(blocked=False)
    process.start.return_value = 101
    # Before spawn no owned process exists; only after start may it run.
    process.is_running.side_effect = lambda: bool(process.start.called and running)
    process.stop.return_value = True
    canary = Mock()
    canary.probe.side_effect = responses
    ticks = iter(range(100))
    return OwnedKoboldLab(process=process, canary=canary,
                          port_check=lambda port: port_free,
                          clock=lambda: next(ticks),
                          pause=lambda _: None), process, canary


class TestOwnedKoboldLabF53b2(unittest.TestCase):
    def test_ready_only_after_identity_verified(self):
        lab, process, canary = owner(
            responses=[KoboldCanaryError("not ready"), "Qwen-Test"])
        self.assertEqual(lab.start(["approved.exe"], expected_model="Qwen-Test"), 101)
        self.assertTrue(lab.ready)
        self.assertEqual(canary.probe.call_count, 2)
        self.assertTrue(lab.stop())
        self.assertFalse(lab.ready)
        process.stop.assert_called_once()

    def test_preexisting_server_blocks_spawning(self):
        lab, process, _ = owner(responses=[], port_free=False)
        with self.assertRaises(LabServerError):
            lab.start(["approved.exe"], expected_model="Qwen-Test")
        process.start.assert_not_called()

    def test_identity_mismatch_stops_owned_process(self):
        lab, process, _ = owner(responses=["Wrong-GGUF"])
        with self.assertRaisesRegex(LabServerError, "mismatch"):
            lab.start(["approved.exe"], expected_model="Qwen-Test")
        process.stop.assert_called_once()
        self.assertFalse(lab.ready)
        self.assertIsNone(lab._expected)

    def test_missing_server_times_out_and_releases(self):
        lab, process, canary = owner(
            responses=[KoboldCanaryError("not ready")] * 30)
        with self.assertRaises(LabServerError):
            lab.start(["approved.exe"], expected_model="Qwen-Test", timeout=3)
        process.stop.assert_called_once()
        self.assertFalse(lab.ready)

    def test_unverified_release_blocks_further_start(self):
        lab, process, _ = owner(responses=["Mismatch"])
        from local_model.owned_process_f5 import OwnedProcessError
        process.stop.side_effect = OwnedProcessError("can't stop")
        process.blocked = True
        with self.assertRaisesRegex(LabServerError, "unverified"):
            lab.start(["approved.exe"], expected_model="Qwen-Test")
        with self.assertRaises(LabServerError):
            lab.start(["approved.exe"], expected_model="Qwen-Test")
        self.assertEqual(process.start.call_count, 1)

    def test_bad_identity_and_timeout_never_launch(self):
        lab, process, _ = owner(responses=[])
        for name, timeout in (("", 3), ("Qwen", 0), ("Qwen", float("nan")),
                              ("Qwen", float("inf"))):
            with self.subTest(name=name, timeout=timeout), self.assertRaises(LabServerError):
                lab.start(["approved.exe"], expected_model=name, timeout=timeout)
        process.start.assert_not_called()

    def test_foreign_probe_error_cannot_leak(self):
        lab, process, canary = owner(responses=[ValueError("private information")])
        with self.assertRaises(LabServerError) as context:
            lab.start(["approved.exe"], expected_model="Qwen")
        self.assertNotIn("private information", str(context.exception))
        process.stop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
