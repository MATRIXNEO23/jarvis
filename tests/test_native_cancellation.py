"""JRV-AUD-010: real lifecycle/owner code, controlled native ABI (Windows).

No GGUF/DLL inference, user profile or account. Events bound every wait and
cleanup releases/joins all workers, including on the pre-fix Red revision.
"""
import os
from pathlib import Path
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import test_activity_status as callbacks
import test_native_trial_ownership as ownership
from local_model.native_bridge import NativeGemmaBridge
from local_model.native_config import NativeModelConfig


class ObservedLock:
    def __init__(self, lock):
        self.lock = lock
        self.waiting = threading.Event()

    def __enter__(self):
        self.waiting.set()
        return self.lock.__enter__()

    def __exit__(self, *args):
        return self.lock.__exit__(*args)


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class NativeCancellationTests(unittest.TestCase):
    def setUp(self):
        self.harness = ownership.NativeTrialOwnershipTests()
        self.addCleanup(self.harness.doCleanups)
        self.harness.setUp()
        self.session, self.abi = self.harness.session, self.harness.abi

    def worker(self, function):
        result = SimpleNamespace(done=threading.Event(), value=None, error=None)
        def run():
            try:
                result.value = function()
            except Exception as exc:
                result.error = exc
            finally:
                result.done.set()
        result.thread = self.harness.make_thread(target=run, daemon=True)
        result.thread.start()
        return result

    def close(self):
        close = getattr(self.session, "close", None)
        self.assertTrue(callable(close), "Session needs terminal non-inference-lock close")
        close()

    def test_timeout_requests_abort_before_native_generate_returns_and_retry_works(self):
        first = self.worker(lambda: self.session.ask("Scadenza", timeout=0.05))
        self.assertTrue(self.abi.first_started.wait(2))
        self.assertTrue(first.done.wait(1), "Deadline did not request cooperative abort")
        self.assertIsInstance(first.error, TimeoutError)
        self.assertTrue(self.abi.abort_during_generation)
        self.assertEqual(list(self.session.history), [])
        self.assertEqual(self.session.ask("Riprova"), "Risposta locale controllata")
        self.assertEqual(len(self.abi.loads), 1)
        self.assertEqual(len(self.abi.calls), 2)
        self.assertEqual(len(self.session.history), 2)

    def test_stop_requests_abort_before_waiting_for_inference_and_recovers(self):
        first = self.worker(lambda: self.session.ask("Da annullare"))
        self.assertTrue(self.abi.first_started.wait(2))
        stop = self.worker(self.session.stop)
        self.assertTrue(stop.done.wait(1), "stop waited for generation before abort")
        self.assertIsNone(stop.error)
        self.assertTrue(first.done.wait(1))
        self.assertIsInstance(first.error, RuntimeError)
        self.assertTrue(self.abi.abort_during_generation)
        self.assertFalse(self.session.prepared)
        self.assertEqual(list(self.session.history), [])
        self.session.ask("Riprendi")
        self.assertEqual(len(self.abi.loads), 2)
        self.assertEqual(len(self.session.history), 2)

    def test_noncooperative_native_call_keeps_reload_serialized_after_deadline(self):
        aborted = threading.Event()
        self.enterContext(patch.object(self.abi, "abort", side_effect=aborted.set))
        first = self.worker(lambda: self.session.ask("Non cooperativa", timeout=0.05))
        self.assertTrue(self.abi.first_started.wait(2))
        observed = ObservedLock(self.session.lock)
        self.session.lock = observed
        second = self.worker(lambda: self.session.test_generation(config=self.harness.config))
        self.assertTrue(observed.waiting.wait(2))
        self.assertTrue(aborted.wait(1), "No abort at deadline")
        self.assertFalse(first.done.is_set(), "Must not pretend native C already finished")
        self.assertFalse(second.done.is_set())
        self.assertEqual(len(self.abi.loads), 1)
        self.assertEqual(len(self.abi.calls), 1)
        self.abi.release.set()
        self.assertTrue(first.done.wait(2))
        self.assertIsInstance(first.error, TimeoutError)
        self.assertTrue(second.done.wait(2))
        self.assertIsNone(second.error)
        self.assertEqual(self.abi.maximum, 1)
        self.assertFalse(self.abi.initialize_during_generation)
        self.assertEqual(list(self.session.history), [])

    def test_close_revokes_active_and_every_queued_entrypoint_without_reloading(self):
        first = self.worker(lambda: self.session.ask("Attiva"))
        self.assertTrue(self.abi.first_started.wait(2))
        aborted = threading.Event()
        self.enterContext(patch.object(self.abi, "abort", side_effect=aborted.set))
        observed = ObservedLock(self.session.lock)
        self.session.lock = observed
        waiting = []
        for request in (
            lambda: self.session.ask("In coda"),
            lambda: self.session.prepare_turn("Differita"),
            lambda: self.session.ask_isolated(lambda _: "Telegram"),
            lambda: self.session.pick_program("Video", ("Video",)),
            lambda: self.session.test_generation(config=self.harness.config),
        ):
            observed.waiting.clear()
            waiting.append(self.worker(request))
            self.assertTrue(observed.waiting.wait(2))
        closer = self.worker(self.close)
        self.assertTrue(closer.done.wait(1), "close must not wait for inference lock")
        self.assertIsNone(closer.error)
        self.assertTrue(aborted.is_set())
        self.assertFalse(first.done.is_set())
        self.abi.release.set()
        for request in [first] + waiting:
            self.assertTrue(request.done.wait(2))
            self.assertIsInstance(request.error, RuntimeError)
        self.assertEqual(len(self.abi.calls), 1)
        self.assertEqual(len(self.abi.loads), 1)
        self.assertEqual(list(self.session.history), [])
        self.assertFalse(self.session.prepared)

    def test_close_during_model_load_never_enters_generate_or_calls_loading_abi_abort(self):
        loading, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)
        self.addCleanup(self.harness.finish_workers)
        original = self.abi.load
        def load(path):
            loading.set()
            if not release.wait(3):
                raise RuntimeError("Fixture load gate timed out")
            return original(path)
        self.enterContext(patch.object(self.abi, "load", side_effect=load))
        abort = self.enterContext(patch.object(self.abi, "abort", wraps=self.abi.abort))
        first = self.worker(lambda: self.session.ask("Load da annullare"))
        try:
            self.assertTrue(loading.wait(2))
            self.close()
            abort.assert_not_called()
        finally:
            release.set()
        self.assertTrue(first.done.wait(2))
        self.assertIsInstance(first.error, RuntimeError)
        self.assertEqual(self.abi.calls, [])
        self.assertEqual(list(self.session.history), [])
        self.assertFalse(self.session.prepared)

    def test_close_while_provider_is_being_created_never_loads_after_publication(self):
        creating, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)
        from local_model import native_chat_adapter
        factory = native_chat_adapter.create_native_provider
        def create(*args, **kwargs):
            provider = factory(*args, **kwargs)
            creating.set()
            if not release.wait(3):
                raise RuntimeError("Fixture factory gate timed out")
            return provider
        self.enterContext(patch.object(native_chat_adapter, "create_native_provider", side_effect=create))
        first = self.worker(lambda: self.session.ask("Prepare da annullare"))
        try:
            self.assertTrue(creating.wait(2))
            self.close()
        finally:
            release.set()
        self.assertTrue(first.done.wait(2))
        self.assertIsInstance(first.error, RuntimeError)
        self.assertEqual(self.abi.calls, [])
        self.assertEqual(self.abi.loads, [])
        self.assertFalse(self.session.prepared)
        self.assertIsNone(self.session.adapter.provider)

    def test_terminal_close_prevents_new_requests_and_preserves_accepted_history(self):
        self.abi.release.set()
        self.session.ask("Accettata")
        history = list(self.session.history)
        self.close()
        for request in (
            lambda: self.session.ask("Dopo close"),
            lambda: self.session.prepare_turn("Dopo close"),
            lambda: self.session.ask_isolated(lambda _: "Telegram"),
            lambda: self.session.pick_program("Video", ("Video",)),
            lambda: self.session.test_generation(config=self.harness.config),
        ):
            with self.assertRaises(RuntimeError):
                request()
        self.assertEqual(list(self.session.history), history)
        self.assertEqual(len(self.abi.calls), 1)
        self.assertEqual(len(self.abi.loads), 1)

    def test_stop_revokes_unaccepted_turn_but_keeps_accepted_history(self):
        self.abi.release.set()
        self.session.ask("Accettata")
        history = list(self.session.history)
        turn = self.session.prepare_turn("Non ancora accettata")
        self.session.stop()
        self.assertFalse(turn.commit(), "stop must revoke answers waiting for UI acceptance")
        self.assertEqual(list(self.session.history), history)
        self.session.ask("Nuova")
        self.assertFalse(turn.commit())
        self.assertEqual(len(self.session.history), 4)

    def test_close_revokes_unaccepted_turn(self):
        self.abi.release.set()
        turn = self.session.prepare_turn("Differita")
        self.close()
        self.assertFalse(turn.commit())
        self.assertEqual(list(self.session.history), [])

    def test_expired_timer_callback_cannot_abort_next_generation(self):
        self.abi.release.set()
        timers = []
        class Timer:
            def __init__(self, interval, function):
                self.function = function
                self.joined = self.cancelled = False
                timers.append(self)
            def start(self): pass
            def cancel(self): self.cancelled = True
            def join(self): self.joined = True
        with patch("local_model.native_bridge.threading.Timer", Timer):
            self.session.ask("Prima")
            self.assertEqual(len(timers), 1, "No generation watchdog registered")
            self.assertTrue(timers[0].cancelled)
            self.assertTrue(timers[0].joined)
            def memory(_):
                timers[0].function()  # Delayed scheduling after cancel.
                return ""
            abort = self.enterContext(patch.object(self.abi, "abort", wraps=self.abi.abort))
            self.session.ask("Seconda", memory_context=memory)
            abort.assert_not_called()
            self.assertEqual(len(self.abi.calls), 2)

    def test_abort_exception_at_deadline_returns_timeout_and_allows_retry(self):
        original_generate = self.abi.generate
        def generate(args):
            answer = original_generate(args)
            return answer
        self.enterContext(patch.object(self.abi, "generate", side_effect=generate))
        aborted = threading.Event()
        def abort():
            aborted.set()
            self.abi.release.set()
            raise RuntimeError("Controlled abort failure")
        self.enterContext(patch.object(self.abi, "abort", side_effect=abort))
        first = self.worker(lambda: self.session.ask("Timeout errore", timeout=0.05))
        self.assertTrue(aborted.wait(1), "Deadline must reach abort, even if abort fails")
        self.assertTrue(first.done.wait(2))
        self.assertIsInstance(first.error, TimeoutError)
        self.assertEqual(list(self.session.history), [])
        self.session.ask("Recupero")
        self.assertEqual(len(self.abi.calls), 2)

    def test_bridge_rejects_nonfinite_or_boolean_timeouts_before_native_call(self):
        upstream = Mock()
        bridge = NativeGemmaBridge(NativeModelConfig(), upstream)
        bridge._loaded = True
        for value in (True, False, float("nan"), float("inf"), -1, 0):
            with self.subTest(value=value), self.assertRaises(ValueError):
                bridge.generate("Domanda", timeout=value)
        upstream.generate.assert_not_called()


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class NativeOwnerShutdownTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        callbacks.ActivityStatusTests.setUpClass()

    def env(self, session):
        env = dict(closing=False, gemma_session=[session], gemma_session_lock=threading.Lock(),
                   gemma_source=[str(Path(__file__))], Path=Path,
                   addon_manager=None, telegram_bridge=None,
                   planner_abort_event=Mock(), doc_dialog=Mock(), dictation=Mock(),
                   wake_gate=Mock(), voice=Mock(), telegram_gpt_ready=Mock(),
                   speaker=Mock(), hud=Mock(), alarm=Mock(), timer=Mock(), root=Mock(),
                   service=Mock(), write_line=Mock(),
                   threading=SimpleNamespace(Thread=lambda **_: SimpleNamespace(start=Mock())))
        harness = callbacks.ActivityStatusTests()
        harness.callback("close", env)
        harness.callback("get_gemma_session", env)
        return env

    def test_owner_close_cancels_existing_session_and_still_closes_other_services(self):
        session = Mock()
        env = self.env(session)
        env["close"]()
        session.close.assert_called_once_with()
        env["root"].destroy.assert_called_once_with()
        env["voice"].close.assert_called_once_with()
        env["speaker"].close.assert_called_once_with()

    def test_close_does_not_create_native_session_and_getter_rejects_after_close(self):
        env = self.env(None)
        with patch("local_model.native_chat_adapter.NativeChatAdapter") as adapter:
            env["close"]()
            with self.assertRaises(RuntimeError):
                env["get_gemma_session"]()
            adapter.assert_not_called()
        self.assertIsNone(env["gemma_session"][0])

    def test_existing_session_getter_is_also_rejected_after_close(self):
        env = self.env(Mock())
        env["close"]()
        with self.assertRaises(RuntimeError):
            env["get_gemma_session"]()

    def test_native_abort_error_does_not_prevent_window_shutdown(self):
        session = Mock()
        session.close.side_effect = RuntimeError("Controlled abort failure")
        env = self.env(session)
        env["close"]()
        session.close.assert_called_once_with()
        env["root"].destroy.assert_called_once_with()
        self.assertTrue(env["closing"])
        env["write_line"].assert_called_once()


if __name__ == "__main__":
    unittest.main()
