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
from unittest.mock import Mock, patch

from local_model.online_permissions import OnlinePermissionPolicy, authorize_online_request
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
                env, workers, _ = self.harness.environment(permissions=False)
                run = self.harness.callback("run_gpt", env)
                self.assertFalse(run(action, prompt="Dati di prova", consent_granted=True))
                self.assertEqual(workers, [])
                env["service"].call.assert_not_called()
                env["messagebox"].askyesno.assert_not_called()

    def test_saved_allowed_avoids_dialog_and_revocation_before_worker_blocks_send(self):
        self.policy(**{"chat.conversation": "allowed"})
        env, workers, _ = self.harness.environment(permissions=False)
        run = self.harness.callback("run_gpt", env)
        self.assertTrue(run("ask", prompt="Dati di prova"))
        env["messagebox"].askyesno.assert_not_called()
        self.policy(**{"chat.conversation": "never"})
        workers.pop()()
        env["service"].call.assert_not_called()

    def test_telegram_session_consent_cannot_override_saved_never(self):
        self.policy(**{"telegram.compose": "never"})
        env, _, _ = self.harness.environment(permissions=False)
        env.update(Future=Future, TelegramBridge=object, GPTUnavailable=RuntimeError)
        env["telegram_gpt_ready"].set()
        env["set_telegram_gpt_session"](True)
        bridge = SimpleNamespace(is_enabled=lambda: True)
        ask = self.harness.callback("ask_telegram_gpt", env)
        self.assertEqual(ask("Messaggio di prova", bridge), "")
        env["service"].call.assert_not_called()
        self.assertTrue(env["output_queue"].empty())

    def test_missing_or_corrupt_policy_blocks_without_asking(self):
        for contents in (None, "{", '{"version":1,"rules":{"chat.conversation":[]}}'):
            with self.subTest(contents=contents):
                if contents is not None:
                    self.path.parent.mkdir(parents=True, exist_ok=True)
                    self.path.write_text(contents, encoding="utf-8")
                env, workers, _ = self.harness.environment(permissions=False)
                self.assertFalse(self.harness.callback("run_gpt", env)("ask", prompt="Prova"))
                self.assertEqual(workers, [])
                env["messagebox"].askyesno.assert_not_called()

    def test_permission_is_scoped_and_not_sent_as_model_data(self):
        self.policy(**{"chat.conversation": "allowed", "files.explain": "never"})
        env, workers, _ = self.harness.environment(permissions=False)
        run = self.harness.callback("run_gpt", env)
        self.assertFalse(run("ask", prompt="Anteprima", capability="files.explain"))
        self.assertTrue(run("ask", prompt="Domanda"))
        workers.pop()()
        env["service"].call.assert_called_once()
        arguments = env["service"].call.call_args.kwargs
        self.assertEqual(arguments["prompt"], "Domanda")
        self.assertNotIn("capability", arguments)
        self.assertNotIn("permission", arguments)
        self.assertTrue(arguments["authorize_send"]())

    def test_allowed_telegram_sends_once_without_session_dialog_and_discards_revoked_reply(self):
        self.policy(**{"telegram.compose": "allowed"})
        env, _, _ = self.harness.environment(permissions=False)
        env.update(Future=Future, TelegramBridge=object, GPTUnavailable=RuntimeError)
        env["telegram_gpt_ready"].set()
        bridge = SimpleNamespace(is_enabled=lambda: True)
        ask = self.harness.callback("ask_telegram_gpt", env)

        def send(*args, authorize_send, **kwargs):
            self.assertTrue(authorize_send())
            self.policy(**{"telegram.compose": "never"})
            self.assertFalse(authorize_send())
            return {"text": "Risposta superata"}

        env["service"].call.side_effect = send
        self.assertEqual(ask("Prova", bridge), "")
        env["service"].call.assert_called_once()
        self.assertTrue(env["output_queue"].empty())

    def test_grants_are_revocable_and_do_not_modify_saved_preferences(self):
        self.policy(**{"chat.conversation": "ask"})
        original = self.path.read_bytes()
        confirm = Mock(return_value=True)
        grant = authorize_online_request("chat.conversation", confirm=confirm)
        self.assertIsNotNone(grant)
        self.assertTrue(grant())
        confirm.assert_called_once()
        self.assertEqual(self.path.read_bytes(), original)
        self.policy(**{"chat.conversation": "allowed"})
        self.assertFalse(grant(), "Changing mode must invalidate the old request")
        confirm.reset_mock()
        grant = authorize_online_request("chat.conversation", confirm=confirm)
        self.assertTrue(grant())
        confirm.assert_not_called()
        self.policy(**{"chat.conversation": "ask"})
        self.assertFalse(grant(), "A new ask rule needs a fresh confirmation")

    def test_revocation_in_consent_dialog_prevents_grant(self):
        self.policy(**{"chat.conversation": "ask"})
        def confirm():
            self.policy(**{"chat.conversation": "never"})
            return True
        self.assertIsNone(authorize_online_request("chat.conversation", confirm=confirm))

    def test_account_status_is_separate_from_inference_permission(self):
        self.policy(**{"chat.conversation": "never"})
        env, workers, _ = self.harness.environment(permissions=False)
        self.assertTrue(self.harness.callback("run_gpt", env)("status"))
        workers.pop()()
        self.assertEqual(env["service"].call.call_args.args, ("status",))
        env["messagebox"].askyesno.assert_not_called()

    def test_policy_revoked_during_bridge_start_prevents_pipe_write(self):
        import io
        from gpt_client import GPTClient, GPTUnavailable
        self.policy(**{"chat.conversation": "allowed"})
        grant = authorize_online_request("chat.conversation")
        client = GPTClient()
        pipe = io.StringIO()
        client._process = SimpleNamespace(poll=lambda: None, stdin=pipe)
        with patch.object(client, "start", side_effect=lambda: self.policy(
                **{"chat.conversation": "never"})):
            with self.assertRaises(GPTUnavailable):
                client.call("ask", prompt="Non trasmettere", authorize_send=grant)
        self.assertEqual(pipe.getvalue(), "")

    def test_external_diagnostic_callback_obeys_its_own_policy(self):
        from diagnostic_handoff import build_external_review_prompt, summarize_operation_outcomes
        from self_diagnostics import SourceAudit
        import sqlite3
        for mode, answer, sends, dialogs in (
                ("never", True, 0, 0), ("ask", False, 0, 1),
                ("ask", True, 1, 1), ("allowed", True, 1, 0)):
            with self.subTest(mode=mode, answer=answer):
                self.policy(**{"chat.conversation": "allowed", "diagnostics.review": mode})
                env, workers, _ = self.harness.environment(permissions=False)
                env.update(
                    last_diagnostic_audit=SourceAudit("Sintesi", "Dettagli", ()),
                    last_runtime_evidence=None, workspace=None, operation_ledger=None,
                    build_external_review_prompt=build_external_review_prompt,
                    summarize_operation_outcomes=summarize_operation_outcomes,
                    sqlite3=sqlite3, MemoryBoundaryError=ValueError)
                env["messagebox"].askyesno.return_value = answer
                self.harness.callback("run_gpt", env)
                self.harness.callback("offer_external_diagnostic_review", env)()
                self.assertEqual(len(workers), sends)
                self.assertEqual(env["messagebox"].askyesno.call_count, dialogs)
                for worker in workers:
                    worker()
                self.assertEqual(env["service"].call.call_count, sends)

    def test_planner_checks_saved_policy_and_revocation_before_worker(self):
        import threading
        import tkinter as tk
        import planner_ui

        self.policy(**{"planner.create": "allowed"})
        root = tk.Tk()
        root.withdraw()
        self.addCleanup(root.destroy)
        workers = []
        service, confirm = Mock(), Mock(return_value=True)
        def thread(*, target, **kwargs):
            return SimpleNamespace(start=lambda: workers.append(target))
        with patch.object(planner_ui.threading, "Thread", side_effect=thread):
            planner_ui.open_planner(
                root, service, Mock(), lambda: True, threading.Lock(), threading.Event(),
                confirm_inference=lambda detail: authorize_online_request(
                    "planner.create", confirm=confirm),
                consent_generation=lambda: 1)
            window = root._jarvis_planner_window
            def widgets(widget):
                for child in widget.winfo_children():
                    yield child
                    yield from widgets(child)
            entry = next(w for w in widgets(window) if w.winfo_class() == "TEntry")
            entry.insert(0, "Controlla la RAM")
            create = next(w for w in widgets(window)
                          if w.winfo_class() == "TButton" and w.cget("text") == "Crea piano con GPT")
            create.invoke()
        self.assertEqual(len(workers), 1)
        confirm.assert_not_called()
        self.policy(**{"planner.create": "never"})
        workers.pop()()
        service.call.assert_not_called()
