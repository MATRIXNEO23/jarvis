"""JRV-AUD-011, Windows-only: actual callbacks/client/Node bridge, no account.

The Node bridge loads a tiny fake SDK in a temporary LOCALAPPDATA. Its connected
state and inference are simulated explicitly; no OAuth/network/DPAPI is used.
"""
import io
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import test_activity_status as callbacks
from gpt_client import GPTClient, GPTUnavailable


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class GPTTimeoutOwnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        callbacks.ActivityStatusTests.setUpClass()

    def env(self):
        harness = callbacks.ActivityStatusTests()
        self.addCleanup(harness.doCleanups)
        env, workers, _ = harness.environment()
        run = harness.callback("run_gpt", env)
        return harness, env, workers, run

    def test_all_inference_channels_use_180_seconds_and_send_once(self):
        for action in ("ask", "conversation", "typed_conversation"):
            with self.subTest(action=action):
                _, env, workers, run = self.env()
                self.assertTrue(run(action, prompt="Domanda controllata", epoch=7, utterance="Domanda"))
                self.assertEqual(len(workers), 1)
                workers.pop()()
                env["service"].call.assert_called_once()
                args, kwargs = env["service"].call.call_args
                self.assertEqual(args, ("ask",))
                self.assertEqual(kwargs["timeout"], 180)
                self.assertNotIn("epoch", kwargs)
                self.assertTrue(kwargs["authorize_send"]())

    def test_virtual_39_41_179_181_second_responses_have_the_same_boundary(self):
        for action in ("ask", "conversation", "typed_conversation"):
            for duration in (39, 41, 179, 181):
                with self.subTest(action=action, virtual_seconds=duration):
                    _, env, workers, run = self.env()
                    def call(_action, *, timeout, **_):
                        if duration > timeout:
                            raise GPTUnavailable("Controlled request timeout")
                        return {"text": "Risposta controllata"}
                    env["service"].call.side_effect = call
                    self.assertTrue(run(action, prompt="Domanda", epoch=7, utterance="Domanda"))
                    workers.pop()()
                    event = env["output_queue"].get_nowait()
                    expected = ("gpt_" if action == "ask" else "conversation_")
                    self.assertEqual(event[0], expected + ("error" if duration > 180 else "ok"))
                    env["service"].call.assert_called_once()
                    self.assertFalse(workers)
                    self.assertTrue(env["output_queue"].empty())

    def test_account_operations_keep_existing_timeouts(self):
        for action, timeout in (("sign_in", 600), ("status", 40),
                                ("models", 40), ("disconnect", 40)):
            with self.subTest(action=action):
                _, env, workers, run = self.env()
                self.assertTrue(run(action))
                workers.pop()()
                env["service"].call.assert_called_once_with(action, timeout=timeout)

    def test_busy_request_has_no_duplicate_or_automatic_retry_after_timeout(self):
        harness, env, workers, run = self.env()
        env["service"].call.side_effect = GPTUnavailable("Controlled timeout")
        self.assertTrue(run("typed_conversation", prompt="Una richiesta", epoch=7, utterance="Domanda"))
        self.assertFalse(run("typed_conversation", prompt="Duplicata", epoch=7))
        self.assertEqual(len(workers), 1)
        workers.pop()()
        harness.receive("conversation_error", env)
        self.assertFalse(env["busy_gpt"])
        self.assertFalse(workers)
        env["service"].call.assert_called_once()
        self.assertTrue(env["output_queue"].empty())

    def test_obsolete_structured_reply_cannot_execute_or_enter_memory(self):
        harness, env, workers, run = self.env()
        env["service"].call.return_value = {"text": '{"kind":"chat","message":"Vecchia risposta"}'}
        self.assertTrue(run("typed_conversation", prompt="Domanda", epoch=7, utterance="Domanda"))
        workers.pop()()
        env["conversation_epoch"] += 1
        harness.receive("conversation_ok", env)
        env["write_line"].assert_not_called()
        env["speak_result"].assert_not_called()
        env["remember_exchange"].assert_not_called()
        env["service"].call.assert_called_once()


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class GPTTimeoutClientTests(unittest.TestCase):
    def setUp(self):
        self.lines = queue.Queue()
        self.writes = []
        self.on_write = None
        self.fail_cancel = False
        self.client = GPTClient()
        def write(value):
            item = json.loads(value)
            if item["action"] == "cancel_request" and self.fail_cancel:
                raise OSError("Controlled cancel pipe failure")
            self.writes.append(item)
            if self.on_write:
                self.on_write(item)
            return len(value)
        class Lines:
            def __iter__(_self): return _self
            def __next__(_self):
                item = self.lines.get(timeout=5)
                if item is None: raise StopIteration
                return json.dumps(item) + "\n"
        self.proc = SimpleNamespace(poll=lambda: None, stdout=Lines(),
                                    stdin=SimpleNamespace(write=write, flush=lambda: None))
        self.client._process = self.proc
        self.start = self.enterContext(patch.object(self.client, "start"))
        self.reader = threading.Thread(target=self.client._read_loop, args=(self.proc,), daemon=True)
        self.reader.start()
        self.addCleanup(self.finish_reader)

    def finish_reader(self):
        self.lines.put(None)
        self.reader.join(3)
        self.assertFalse(self.reader.is_alive())

    def expire(self, action="ask"):
        with self.assertRaises(GPTUnavailable) as caught:
            self.client.call(action, timeout=0.02, **({"prompt": "wait"} if action == "ask" else {}))
        return caught.exception

    def test_timeout_sends_one_targeted_cancel_without_pending_or_starting_again(self):
        self.expire()
        self.assertEqual([w["action"] for w in self.writes], ["ask", "cancel_request"])
        self.assertEqual(self.writes[1]["request_id"], self.writes[0]["id"])
        self.assertGreater(self.writes[1]["id"], self.writes[0]["id"])
        self.assertEqual(self.client._pending, {})
        self.start.assert_called_once_with()

    def test_late_answer_and_cancel_ack_cannot_satisfy_the_next_request(self):
        self.expire()
        original = self.writes[0]["id"]
        controls = [w for w in self.writes if w["action"] == "cancel_request"]
        self.assertEqual(len(controls), 1)
        def respond(item):
            self.lines.put({"id": original, "ok": True, "result": {"text": "OLD"}})
            self.lines.put({"id": controls[0]["id"], "ok": True, "result": {"cancelled": True}})
            self.lines.put({"id": item["id"], "ok": True, "result": {"text": "NEW"}})
        self.on_write = respond
        result = self.client.call("ask", prompt="new", timeout=2)
        self.assertEqual(result, {"text": "NEW"})
        self.assertEqual([w["action"] for w in self.writes], ["ask", "cancel_request", "ask"])
        self.assertGreater(self.writes[-1]["id"], controls[0]["id"])
        self.assertEqual(self.client._pending, {})
        self.assertTrue(self.client.events.empty())

    def test_cancel_pipe_failure_keeps_timeout_and_does_not_restart_or_retry(self):
        self.fail_cancel = True
        error = self.expire()
        self.assertIn("limite", str(error))
        self.assertEqual([w["action"] for w in self.writes], ["ask"])
        self.assertEqual(self.client._pending, {})
        self.start.assert_called_once_with()

    def test_noninference_timeout_does_not_send_cancel_or_start_again(self):
        self.expire("status")
        self.assertEqual([w["action"] for w in self.writes], ["status"])
        self.assertEqual(self.client._pending, {})
        self.start.assert_called_once_with()


FAKE_SDK = r"""
const emit = value => process.stdout.write(JSON.stringify({event:'test_stage', ...value})+'\n');
const mode = process.env.JARVIS_TEST_CANCEL_MODE || 'stream';
export function createChatGPT() {
  let sessions = 0;
  const connected = {status:'connected', sharing:true};
  return {
    async getSession() {
      if (++sessions > 1) {
        emit({stage:'session'});
        if (mode === 'session') await new Promise(resolve => setTimeout(resolve, 200));
      }
      return connected;
    },
    async listModels(options = {}) {
      const signal = options.signal;
      emit({stage:'models', hasSignal: !!signal});
      if (mode === 'models') await wait(signal, 'models');
      return [{slug:'controlled', name:'Controlled SDK'}];
    },
    async streamResponse({input, signal}) {
      emit({stage:'stream', prompt:input, hasSignal: !!signal});
      if (input.startsWith('wait')) await wait(signal, input);
      if (input === 'late') {
        signal?.addEventListener('abort', () => emit({stage:'aborted', prompt:input}), {once:true});
        await new Promise(resolve => setTimeout(resolve, 200)); // Deliberately ignore abort.
      }
      return {text:'answer:' + input};
    },
    cancelSignIn() {},
    async disconnect() { return {status:'disconnected'}; }
  };
}
function wait(signal, prompt) {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) return reject(new Error('controlled cancellation'));
    signal?.addEventListener('abort', () => {
      emit({stage:'aborted', prompt});
      reject(new Error('controlled cancellation'));
    }, {once:true});
  });
}
"""


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class GPTTimeoutNodeBridgeTests(unittest.TestCase):
    def bridge(self, mode="stream"):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node22 required by Windows CI/project")
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        home = Path(temporary.name)
        sdk = home / "Jarvis/runtime/siwc/packages/local/dist"
        sdk.mkdir(parents=True)
        (sdk / "package.json").write_text('{"type":"module"}', encoding="utf-8")
        (sdk / "index.js").write_text(FAKE_SDK, encoding="utf-8")
        env = dict(os.environ, LOCALAPPDATA=str(home), JARVIS_TEST_CANCEL_MODE=mode)
        self.proc = subprocess.Popen([node, str(Path("gpt_bridge.mjs").resolve())],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8", env=env,
            creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        self.packets = queue.Queue()
        self.messages = []
        def read():
            for line in self.proc.stdout:
                self.packets.put(json.loads(line))
        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()
        self.addCleanup(self.finish_bridge)
        self.until(lambda p: p.get("event") == "ready")

    def finish_bridge(self):
        if self.proc.poll() is None:
            self.proc.terminate()
        self.proc.wait(timeout=3)
        self.proc.stdin.close()
        self.reader.join(3)
        self.assertFalse(self.reader.is_alive())
        self.proc.stdout.close()

    def send(self, ident, action, **arguments):
        self.proc.stdin.write(json.dumps(dict(id=ident, action=action, **arguments)) + "\n")
        self.proc.stdin.flush()

    def until(self, predicate):
        # Preserve all records for assertions even when a response arrives
        # while waiting for the cancellation acknowledgement, or vice versa.
        for record in self.messages:
            if predicate(record):
                return record
        while True:
            record = self.packets.get(timeout=3)
            self.messages.append(record)
            if predicate(record):
                return record

    def response(self, ident):
        return self.until(lambda p: p.get("id") == ident)

    def stage(self, stage, **fields):
        return self.until(lambda p: p.get("stage") == stage and
                          all(p.get(k) == v for k,v in fields.items()))

    def test_cancel_one_stream_keeps_concurrent_request_and_client_usable(self):
        self.bridge()
        self.send(1,"ask",prompt="wait-one")
        stage = self.stage("stream",prompt="wait-one")
        self.assertTrue(stage["hasSignal"])
        self.send(2,"ask",prompt="fast-two")
        self.send(3,"cancel_request",request_id=1)
        self.assertEqual(self.response(3).get("result"), {"cancelled":True})
        self.assertFalse(self.response(1)["ok"])
        self.assertEqual(self.response(2).get("result",{}).get("text"), "answer:fast-two")
        self.send(4,"ask",prompt="fast-three")
        self.assertTrue(self.response(4)["ok"])
        self.assertEqual(sum(m.get("stage")=="stream" for m in self.messages),3)

    def test_cancel_during_model_lookup_prevents_stream_request(self):
        self.bridge("models")
        self.send(1,"ask",prompt="wait-models")
        self.assertTrue(self.stage("models")["hasSignal"])
        self.send(2,"cancel_request",request_id=1)
        self.assertEqual(self.response(2).get("result"), {"cancelled":True})
        self.assertFalse(self.response(1)["ok"])
        self.assertFalse(any(m.get("stage")=="stream" for m in self.messages))

    def test_cancel_during_uncancellable_session_lookup_prevents_models_and_stream(self):
        self.bridge("session")
        self.send(1,"ask",prompt="wait-session")
        self.stage("session")
        self.send(2,"cancel_request",request_id=1)
        self.assertEqual(self.response(2).get("result"), {"cancelled":True})
        self.assertFalse(self.response(1)["ok"])
        self.assertFalse(any(m.get("stage") in ("models","stream") for m in self.messages))

    def test_unknown_cancel_does_not_abort_an_unrelated_request(self):
        self.bridge()
        self.send(1,"ask",prompt="wait-one")
        self.stage("stream",prompt="wait-one")
        self.send(9,"cancel_request",request_id=8)
        self.assertEqual(self.response(9).get("result"), {"cancelled":False})
        self.send(10,"ask",prompt="fast")
        self.assertTrue(self.response(10)["ok"])
        self.assertFalse(any(m.get("stage")=="aborted" for m in self.messages))
        self.send(11,"cancel_request",request_id=1)
        self.assertFalse(self.response(1)["ok"])

    def test_completed_request_is_removed_from_cancel_map(self):
        self.bridge()
        self.send(1,"ask",prompt="fast")
        self.assertTrue(self.response(1)["ok"])
        self.send(2,"cancel_request",request_id=1)
        self.assertEqual(self.response(2).get("result"), {"cancelled":False})

    def test_sdk_ignoring_abort_cannot_return_late_success(self):
        self.bridge()
        self.send(1,"ask",prompt="late")
        self.stage("stream",prompt="late")
        self.send(2,"cancel_request",request_id=1)
        self.assertEqual(self.response(2).get("result"), {"cancelled":True})
        self.assertFalse(self.response(1)["ok"])

    def test_shutdown_aborts_pending_streams_and_exits_without_retry(self):
        self.bridge()
        for ident in (1,2):
            self.send(ident,"ask",prompt="wait-"+str(ident))
            self.stage("stream",prompt="wait-"+str(ident))
        self.send(3,"shutdown")
        self.assertTrue(self.response(3)["ok"])
        self.assertFalse(self.response(1)["ok"])
        self.assertFalse(self.response(2)["ok"])
        self.proc.wait(timeout=3)
        self.assertEqual(self.proc.returncode,0)
        self.assertEqual(sum(m.get("stage")=="stream" for m in self.messages),2)

    def test_invalid_cancel_identifiers_are_rejected_without_cancelling_stream(self):
        self.bridge()
        self.send(1,"ask",prompt="wait-one")
        self.stage("stream",prompt="wait-one")
        for ident, target in enumerate((True,0,-1,"1",1.5,99),2):
            self.send(ident,"cancel_request",request_id=target)
            self.assertFalse(self.response(ident)["ok"])
        self.assertFalse(any(m.get("stage")=="aborted" for m in self.messages))
        self.send(20,"cancel_request",request_id=1)
        self.assertFalse(self.response(1)["ok"])


if __name__ == "__main__":
    unittest.main()
