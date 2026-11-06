"""Windows activity UI and actual app callbacks with controlled workers.

Real Tk and app code; no microphone, model, login or user files are used.
"""
import ast
from concurrent.futures import Future
import copy
import os
from pathlib import Path
import queue
import sqlite3
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from local_engine import TaskResult
from local_model.chat_transport import ChatTransport
from voice_control import GPT_CONVERSATION, STANDBY, PUSH_TO_TALK


class Value:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class GlobalCallbacks(ast.NodeTransformer):
    def visit_Nonlocal(self, node):
        return ast.copy_location(ast.Global(names=node.names), node)


@unittest.skipUnless(os.name == "nt", "User requires Windows-only runtime tests")
class ActivityStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tree = ast.parse(Path("jarvis.py").read_text(encoding="utf-8"))
        cls.main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        cls.poll = next(n for n in cls.main.body if isinstance(n, ast.FunctionDef) and n.name == "poll")
        call = next(n for n in ast.walk(cls.main) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute) and n.func.attr == "set_state_provider")
        cls.provider_code = compile(ast.Expression(body=call.args[0]), "real-hud-provider", "eval")

    def environment(self):
        workers = []
        def thread(*, target, **kwargs):
            return SimpleNamespace(start=lambda: workers.append(target))
        env = dict(busy_gpt=False, busy_local=False, document_busy=False,
                   gpt_request_action="", closing=False, active_gpt=True,
                   gpt_enabled=Value(True), memory_enabled=Value(True),
                   speaker=SimpleNamespace(is_speaking=lambda: False),
                   voice=SimpleNamespace(is_user_speaking=lambda: False, is_listening=lambda: False),
                   engine=SimpleNamespace(file_access=None), orbit_nodes_cache=(),
                   refresh_buttons=Mock(), gpt_status=Value("GPT: connesso"),
                   threading=SimpleNamespace(Thread=thread), service=Mock(),
                   output_queue=queue.Queue(), write_line=Mock(), speak_result=Mock(),
                   remember_exchange=Mock(), runtime_events=Mock(),
                   conversation_epoch=7, voice_mode=Value(GPT_CONVERSATION),
                   GPT_CONVERSATION=GPT_CONVERSATION, STANDBY=STANDBY,
                   PUSH_TO_TALK=PUSH_TO_TALK)
        env['chat_transport'] = ChatTransport(env['service'], native=None)
        env.update(root=None, online_consent_pending=False,
                   telegram_gpt_ready=threading.Event(), planner_abort_event=threading.Event(),
                   messagebox=SimpleNamespace(askyesno=Mock(return_value=True)))
        self.callback("confirm_gpt_inference", env)
        return env, workers, eval(self.provider_code, env)

    def callback(self, name, env):
        node = copy.deepcopy(next(n for n in self.main.body
                                  if isinstance(n, ast.FunctionDef) and n.name == name))
        node = GlobalCallbacks().visit(node)
        code = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
        exec(compile(code, "real-"+name, "exec"), env)
        return env[name]

    def receive(self, kind, env):
        actual, *data = env["output_queue"].get_nowait()
        self.assertEqual(actual, kind)
        branch = next(n for n in ast.walk(self.poll) if isinstance(n, ast.If)
                      and isinstance(n.test, ast.Compare) and isinstance(n.test.left, ast.Name)
                      and n.test.left.id == "kind" and isinstance(n.test.comparators[0], ast.Constant)
                      and n.test.comparators[0].value == kind)
        env["data"] = data
        wrapper = ast.For(target=ast.Name(id='_event', ctx=ast.Store()),
                          iter=ast.Tuple(elts=[ast.Constant(1)], ctx=ast.Load()),
                          body=copy.deepcopy(branch.body), orelse=[])
        exec(compile(ast.fix_missing_locations(ast.Module(body=[wrapper], type_ignores=[])),
                     "real-result-"+kind, "exec"), env)

    def test_existing_tk_status_row_follows_real_phases_and_voice_priority(self):
        import tkinter as tk
        from animated_hud import JarvisHUD
        root = tk.Tk()
        root.withdraw()
        hud = JarvisHUD(root, lambda: None)
        state = {}
        hud.set_state_provider(lambda: state)
        try:
            for flags, expected in (
                ({"thinking": True, "reasoning": True}, "JARVIS STA RAGIONANDO"),
                ({"thinking": True, "searching": True}, "RICERCA SUL PC IN CORSO"),
                ({"thinking": True, "reasoning": True, "speaking": True}, "JARVIS STA PARLANDO"),
                ({"thinking": True, "reasoning": True, "listening": True}, "LA TUA VOCE È RILEVATA"),
                ({"thinking": True}, "ELABORAZIONE IN CORSO"),
                ({}, "MICROFONO SPENTO"),
            ):
                state.clear()
                state.update(flags)
                hud._advance()
                root.update_idletasks()
                self.assertIn(expected, hud.chat_info.get())
            self.assertEqual(hud.visual_status.get(), "JARVIS // STANDBY")
        finally:
            hud.close()
            root.destroy()

    def test_real_gpt_start_distinguishes_model_requests_from_session_operations(self):
        for action in ("ask", "conversation", "typed_conversation", "status", "sign_in", "disconnect"):
            with self.subTest(action=action):
                env, workers, provider = self.environment()
                self.callback("run_gpt", env)(action, prompt="Richiesta controllata")
                self.assertTrue(env["busy_gpt"])
                self.assertEqual(provider()["reasoning"], action in ("ask", "conversation", "typed_conversation"))
                self.assertEqual(len(workers), 1)
                env["gpt_enabled"].set(False)
                self.assertFalse(provider()["reasoning"])
                self.assertFalse(provider()["thinking"])

    def test_refused_or_revoked_online_consent_does_not_start_a_worker(self):
        for answer in (False, True):
            with self.subTest(answer=answer):
                env, workers, _ = self.environment()
                def respond(*args, **kwargs):
                    if answer:
                        env["conversation_epoch"] += 1
                    return answer
                env["messagebox"].askyesno.side_effect = respond
                self.assertFalse(self.callback("run_gpt", env)("ask", prompt="Richiesta privata"))
                self.assertFalse(workers)
                self.assertFalse(env["busy_gpt"])
                env["service"].call.assert_not_called()

    def test_revoked_approval_does_not_reach_gpt_transport(self):
        env, workers, _ = self.environment()
        self.assertTrue(self.callback("run_gpt", env)("ask", prompt="Richiesta privata"))
        env["conversation_epoch"] += 1
        workers.pop()()
        env["service"].call.assert_not_called()
        self.assertEqual(env["output_queue"].get_nowait()[0], "gpt_error")

    def test_disconnect_revokes_gpt_workers_before_account_response(self):
        env, workers, _ = self.environment()
        env["telegram_gpt_ready"].set()
        self.assertTrue(self.callback("run_gpt", env)("disconnect"))
        self.assertEqual(env["conversation_epoch"], 8)
        self.assertFalse(env["active_gpt"])
        self.assertFalse(env["telegram_gpt_ready"].is_set())
        self.assertTrue(env["planner_abort_event"].is_set())
        self.assertEqual(len(workers), 1)

    def test_telegram_consent_starts_no_online_call_on_denial_or_revocation(self):
        for decision in ("deny", "revoke", "allow", "timeout"):
            with self.subTest(decision=decision):
                env, _, _ = self.environment()
                ready = threading.Event()
                ready.set()
                bridge = SimpleNamespace(is_enabled=lambda: True)
                env.update(Future=Future, TelegramBridge=object, telegram_bridge=bridge,
                           telegram_gpt_ready=ready,
                           GPTUnavailable=RuntimeError)
                resolve = self.callback("resolve_telegram_gpt_consent", env)
                env["messagebox"].askyesno.return_value = decision == "allow"
                env["service"].call.return_value = {"text": "Risposta"}
                def post(event):
                    _, candidate, approval = event
                    if decision == "revoke":
                        ready.clear()
                    resolve(candidate, approval)
                env["output_queue"] = SimpleNamespace(put=post)
                ask = self.callback("ask_telegram_gpt", env)
                if decision == "timeout":
                    # A cancelled request is ignored by the UI callback.
                    approval = Future()
                    approval.cancel()
                    resolve(bridge, approval)
                    env["messagebox"].askyesno.assert_not_called()
                    continue
                reply = ask("Messaggio privato", bridge)
                self.assertEqual(reply, "Risposta" if decision == "allow" else "")
                self.assertEqual(env["service"].call.call_count, int(decision == "allow"))

    def test_telegram_uses_gemma_only_when_gpt_is_unavailable(self):
        from telegram_bridge import telegram_assistant_prompt, telegram_local_prompt
        env, _, _ = self.environment()
        ready = env["telegram_gpt_ready"]
        bridge = SimpleNamespace(is_enabled=Mock(return_value=True))
        session = Mock()
        def ask_local(build_prompt):
            self.assertIn("Ciao", build_prompt(512))
            return "Ciao, come posso aiutarti?"
        session.ask_isolated.side_effect = ask_local
        env.update(get_gemma_session=Mock(return_value=session),
                   ask_telegram_gpt=Mock(return_value=""),
                   telegram_assistant_prompt=telegram_assistant_prompt,
                   telegram_local_prompt=telegram_local_prompt)
        reply = self.callback("ask_telegram_reply", env)
        self.assertEqual(reply("Ciao", "Contesto privato", bridge), "Ciao, come posso aiutarti?")
        env["ask_telegram_gpt"].assert_not_called()

        ready.set()
        self.assertEqual(reply("Ciao", "", bridge), "")
        env["ask_telegram_gpt"].assert_called_once()
        session.ask_isolated.assert_called_once()

    def test_actual_gpt_timeout_clears_phase_and_reports_reason_in_chat(self):
        env, workers, provider = self.environment()
        env["service"].call.side_effect = TimeoutError("Tempo di risposta GPT scaduto")
        self.callback("run_gpt", env)("conversation", prompt="Prova", epoch=7, utterance="Trova la cartella")
        self.assertTrue(provider()["reasoning"])
        workers.pop()()
        self.receive("conversation_error", env)
        self.assertFalse(provider()["reasoning"])
        self.assertFalse(provider()["thinking"])
        self.assertTrue(any("Tempo di risposta GPT scaduto" in str(c)
                            for c in env["write_line"].call_args_list))

    def test_actual_gpt_success_returns_to_idle_without_extra_phase_speech(self):
        env, workers, provider = self.environment()
        env["service"].call.return_value = {"text": "Risposta controllata"}
        self.callback("run_gpt", env)("ask", prompt="Prova")
        self.assertTrue(provider()["reasoning"])
        env["speak_result"].assert_not_called()
        workers.pop()()
        self.receive("gpt_ok", env)
        self.assertFalse(provider()["reasoning"])
        self.assertFalse(provider()["thinking"])
        env["speak_result"].assert_called_once_with("Risposta controllata")

    def test_search_phase_uses_actual_service_progress_and_cancel_state(self):
        env, _, provider = self.environment()
        service = SimpleNamespace(_progress_active=True, cancelled=threading.Event())
        env["engine"].file_access = service
        env["busy_local"] = True
        self.assertTrue(provider()["searching"])
        service.cancelled.set()
        self.assertFalse(provider()["searching"])
        service.cancelled.clear()
        service._progress_active = False
        self.assertFalse(provider()["searching"])
        env["busy_local"] = False
        self.assertFalse(provider()["thinking"])

    def test_actual_local_failure_reports_type_in_chat_and_clears_busy(self):
        env, workers, provider = self.environment()
        env.update(
            try_timer_command=lambda _: False, addon_manager=None,
            request=Value(""), begin_project_work=lambda *a: None,
            finish_project_work=Mock(), project_local_ticket=None, active_project_id=None,
            operation_ledger=Mock(), local_operation_id=None,
            MemoryBoundaryError=RuntimeError, sqlite3=sqlite3,
            local_execution_lock=threading.Lock(), TaskResult=TaskResult,
            last_user_for_action="", observed_local_result=lambda _: False,
            remember_completed_action=Mock())
        env["engine"].execute = Mock(side_effect=PermissionError("PRIVATE_RAW_DETAIL"))
        self.callback("submit_local", env)(message_override="stato sistema")
        self.assertTrue(provider()["thinking"])
        workers.pop()()
        self.receive("local", env)
        text = str(env["write_line"].call_args_list)
        self.assertIn("PermissionError", text)
        self.assertNotIn("PRIVATE_RAW_DETAIL", text)
        self.assertFalse(provider()["thinking"])
        env["speak_result"].assert_not_called()


if __name__ == "__main__":
    unittest.main()
