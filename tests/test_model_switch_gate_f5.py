"""F5.3a switch gate contract tests; no model, UI or disk access."""
import unittest

from local_model.model_profiles_f5 import default_profiles
from local_model.model_switch_gate_f5 import ModelSwitchGate, SwitchRejected


class TestModelSwitchGateF53(unittest.TestCase):
    def setUp(self):
        self.gemma, self.qwen = default_profiles()
        self.gate = ModelSwitchGate(self.gemma)

    def start(self):
        return self.gate.begin(self.qwen, busy=False, backend_ready=True,
                               chat_template_verified=True)

    def test_rejects_busy_and_unverified_qwen(self):
        for checks in (
            {"busy": True, "backend_ready": True, "chat_template_verified": True},
            {"busy": False, "backend_ready": False, "chat_template_verified": True},
            {"busy": False, "backend_ready": True, "chat_template_verified": False},
        ):
            with self.subTest(checks=checks), self.assertRaises(SwitchRejected):
                self.gate.begin(self.qwen, **checks)
            self.assertEqual(self.gate.snapshot().active_profile_id, "gemma-default")

    def test_cannot_switch_without_confirmed_release_and_target_start(self):
        ticket = self.start()
        with self.assertRaises(SwitchRejected):
            self.gate.commit(ticket)
        with self.assertRaises(SwitchRejected):
            self.gate.confirm_target_ready(ticket, ready=True)
        with self.assertRaises(SwitchRejected):
            self.gate.confirm_released(ticket, released=False)
        self.assertTrue(self.gate.snapshot().blocked)
        self.gate.confirm_released(ticket, released=True)
        with self.assertRaises(SwitchRejected):
            self.gate.commit(ticket)
        with self.assertRaises(SwitchRejected):
            self.gate.confirm_target_ready(ticket, ready=False)
        self.gate.confirm_target_ready(ticket, ready=True)
        self.assertEqual(self.gate.commit(ticket).active_profile_id, "qwen-local")

    def test_no_parallel_or_stale_switch(self):
        ticket = self.start()
        with self.assertRaises(SwitchRejected):
            self.start()
        with self.assertRaises(SwitchRejected):
            self.gate.confirm_released(ticket + 1, released=True)
        self.gate.cancel_before_release(ticket)
        self.assertFalse(self.gate.snapshot().blocked)
        self.assertEqual(self.gate.snapshot().active_profile_id, "gemma-default")

    def test_no_rollback_without_reinitializing_old_model(self):
        ticket = self.start()
        self.gate.confirm_released(ticket, released=True)
        with self.assertRaises(SwitchRejected):
            self.gate.cancel_before_release(ticket)
        self.assertEqual(self.gate.snapshot().active_profile_id, "gemma-default")
        with self.assertRaises(SwitchRejected):
            self.gate.begin(self.qwen, busy=False, backend_ready=True,
                            chat_template_verified=True)


if __name__ == "__main__":
    unittest.main()
