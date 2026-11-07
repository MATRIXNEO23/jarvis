"""JRV-AUD-001: saved owner policy at the real application entry points.

Windows callbacks, temporary profiles and controlled worker/pipe boundaries.
No model, account, microphone or live Telegram messages are used.
"""
from concurrent.futures import Future
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from local_model.online_permissions import OnlinePermissionPolicy
import test_activity_status as callbacks


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class SavedPolicyIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        callbacks.ActivityStatusTests.setUpClass()

    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.profile = Path(temporary.name)
        environ = patch.dict(os.environ, {"JARVIS_TRIAL_HOME": str(self.profile)})
        environ.start()
        self.addCleanup(environ.stop)
        self.path = self.profile / "addon-data/modello_locale/online-permissions.json"
        self.harness = callbacks.ActivityStatusTests()

    def policy(self, **rules):
        OnlinePermissionPolicy(rules).save(self.path)

    def test_saved_never_blocks_console_even_with_previous_confirmation(self):
        self.policy(**{"chat.conversation": "never"})
        for action in ("ask", "conversation", "typed_conversation"):
            with self.subTest(action=action):
                env, workers, _ = self.harness.environment()
                run = self.harness.callback("run_gpt", env)
                self.assertFalse(run(action, prompt="Dati di prova", consent_granted=True))
                self.assertEqual(workers, [])
                env["service"].call.assert_not_called()
                env["messagebox"].askyesno.assert_not_called()

    def test_saved_allowed_avoids_dialog_and_revocation_before_worker_blocks_send(self):
        self.policy(**{"chat.conversation": "allowed"})
        env, workers, _ = self.harness.environment()
        run = self.harness.callback("run_gpt", env)
        self.assertTrue(run("ask", prompt="Dati di prova"))
        env["messagebox"].askyesno.assert_not_called()
        self.policy(**{"chat.conversation": "never"})
        workers.pop()()
        env["service"].call.assert_not_called()

    def test_telegram_session_consent_cannot_override_saved_never(self):
        self.policy(**{"telegram.compose": "never"})
        env, _, _ = self.harness.environment()
        env.update(Future=Future, TelegramBridge=object, GPTUnavailable=RuntimeError)
        env["telegram_gpt_ready"].set()
        env["set_telegram_gpt_session"](True)
        bridge = SimpleNamespace(is_enabled=lambda: True)
        ask = self.harness.callback("ask_telegram_gpt", env)
        self.assertEqual(ask("Messaggio di prova", bridge), "")
        env["service"].call.assert_not_called()
        self.assertTrue(env["output_queue"].empty())
