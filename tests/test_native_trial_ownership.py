"""Actual generated trial UI + factory/bridge/session, controlled native ABI.

Only UI transform is applied to a temporary source copy: no ZIP/build or DLL
is produced or loaded. The fake ABI records overlapping native entry/abort.
"""
from __future__ import annotations

import ast
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import threading
from types import ModuleType, SimpleNamespace
from dataclasses import replace
import unittest
from unittest.mock import patch

from local_model.native_config import NativeModelConfig
from local_model.native_chat_adapter import NativeChatAdapter
from local_model.native_conversation_session import NativeConversationSession
from local_model.native_settings import default_native_settings_path


class ControlledABI:
    def __init__(self):
        self.lock = threading.Lock()
        self.first_started = threading.Event()
        self.second_started = threading.Event()
        self.release = threading.Event()
        self.active = 0
        self.maximum = 0
        self.calls = []
        self.loads = []
        self.initialize_during_generation = False
        self.abort_during_generation = False

    def initialize(self, *_):
        with self.lock:
            self.initialize_during_generation |= self.active > 0

    def load(self, model):
        with self.lock:
            self.loads.append(model)
            self.initialize_during_generation |= self.active > 0
        return True

    def generate(self, arguments):
        with self.lock:
            number = len(self.calls)
            self.calls.append(dict(arguments))
            self.active += 1
            self.maximum = max(self.maximum, self.active)
        try:
            if number == 0:
                self.first_started.set()
                if not self.release.wait(5):
                    raise RuntimeError("Test ABI release gate timed out")
            else:
                self.second_started.set()
            return {"status": 1, "text": "Risposta locale controllata"}
        finally:
            with self.lock:
                self.active -= 1

    def abort(self):
        with self.lock:
            self.abort_during_generation |= self.active > 0
        self.release.set()


def generated_ui(root):
    target = root / "local_model" / "native_ui.py"
    target.parent.mkdir()
    target.write_text(Path("local_model/native_ui.py").read_text(encoding="utf-8"),
                      encoding="utf-8")
    tree = ast.parse(Path("tools/build_gemma_clean_trial.py").read_text(encoding="utf-8"))
    prefix = []
    started = False
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names = [n.id for n in node.targets if isinstance(n, ast.Name)]
            if "factory" in names:
                break
            if "ui" in names:
                started = True
        if started:
            prefix.append(node)
    if not prefix:
        raise AssertionError("Trial UI transform not found")
    exec(compile(ast.Module(body=prefix, type_ignores=[]), "trial-ui-transform", "exec"),
         {"root": root, "Path": Path})
    module = ModuleType("local_model._ownership_trial")
    module.__file__ = str(target)
    module.__package__ = "local_model"
    exec(compile(target.read_text(encoding="utf-8"), str(target), "exec"), module.__dict__)
    return module


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class NativeTrialOwnershipTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.enterContext(patch.dict(os.environ, {"JARVIS_TRIAL_HOME": str(self.root / "profile")}))
        engine = self.root / "native_engine"
        engine.mkdir()
        source = engine / "koboldcpp.py"
        source.write_text(
            'from sys import modules\n'
            'state = modules["_jarvis_trial_test_abi"].state\n'
            'handle = type("Handle", (), {"abort_generate": lambda self: state.abort()})()\n'
            'def load_model(path): return state.load(path)\n'
            'def generate(arguments): return state.generate(arguments)\n', encoding="utf-8")
        model = self.root / "test.gguf"
        model.write_bytes(b"fixture: never loaded")
        dll = engine / "koboldcpp_noavx2.dll"
        dll.write_bytes(b"fixture: never loaded")
        self.config = NativeModelConfig(model=str(model), dll=str(dll),
                                        context_size=2048, max_output=128)
        self.config.save(default_native_settings_path())
        self.abi = ControlledABI()
        marker = ModuleType("_jarvis_trial_test_abi")
        marker.state = self.abi
        self.enterContext(patch.dict(sys.modules, {marker.__name__: marker}))
        self.enterContext(patch("local_model.native_factory.initialize_kobold_cpu",
                                side_effect=self.abi.initialize))
        self.session = NativeConversationSession(NativeChatAdapter(source))
        self.module = generated_ui(self.root)
        self.threads = []
        self.original_thread = threading.Thread
        self.enterContext(patch.object(self.module.threading, "Thread", side_effect=self.make_thread))
        self.callbacks = []
        self.addCleanup(self.finish_workers)

    def make_thread(self, *args, **kwargs):
        worker = self.original_thread(*args, **kwargs)
        self.threads.append(worker)
        return worker

    def finish_workers(self):
        self.abi.release.set()
        for worker in self.threads:
            worker.join(5)
            self.assertFalse(worker.is_alive(), "Native test worker did not finish")
        while self.callbacks:
            self.callbacks.pop(0)()

    def window(self):
        panel = self.module.NativeSettingsWindow.__new__(self.module.NativeSettingsWindow)
        panel.current = self.config
        panel.get_session = lambda: self.session
        panel.save = lambda: True
        panel.status_value = ""
        panel.status = SimpleNamespace(set=lambda value: setattr(panel, "status_value", value))
        panel.test_button = SimpleNamespace(configure=lambda **_: None)
        panel.window = SimpleNamespace(
            after=lambda _, callback: self.callbacks.append(callback),
            winfo_exists=lambda: True)
        return panel

    def assert_serialized(self):
        self.finish_workers()
        self.assertEqual((self.abi.maximum, self.abi.initialize_during_generation,
                          self.abi.abort_during_generation), (1, False, False),
                         "Native peak concurrency, reload overlap, abort overlap")

    def test_chat_and_generated_settings_trial_share_native_owner(self):
        errors = []
        def chat():
            try:
                self.session.ask("Domanda chat")
            except Exception as exc:
                errors.append(type(exc).__name__)
        worker = self.make_thread(target=chat)
        worker.start()
        self.assertTrue(self.abi.first_started.wait(2))
        panel = self.window()
        panel.test_model()
        self.abi.second_started.wait(1)
        self.assert_serialized()
        self.assertEqual(errors, [])
        self.assertTrue(panel.status_value.startswith("TEST RIUSCITO"), panel.status_value)

    def test_two_generated_settings_trials_share_native_owner(self):
        first, second = self.window(), self.window()
        first.test_model()
        self.assertTrue(self.abi.first_started.wait(2))
        second.test_model()
        self.abi.second_started.wait(1)
        self.assert_serialized()
        self.assertTrue(first.status_value.startswith("TEST RIUSCITO"), first.status_value)
        self.assertTrue(second.status_value.startswith("TEST RIUSCITO"), second.status_value)

    def test_trial_is_isolated_and_leaves_backend_ready_for_chat(self):
        self.abi.release.set()
        self.config = replace(self.config, personality="Ironia secca controllata")
        self.config.save(default_native_settings_path())
        self.session.ask("RISERVATO_CHAT: non includere nella prova")
        history = list(self.session.history)
        answer = self.session.test_generation(config=self.config)
        self.assertEqual(answer, "Risposta locale controllata")
        self.assertNotIn("RISERVATO_CHAT", self.abi.calls[-1]["prompt"])
        self.assertIn("Ironia secca controllata", self.abi.calls[-1]["prompt"])
        self.assertEqual(list(self.session.history), history)
        self.assertEqual(len(self.abi.loads), 2)
        self.session.ask("Riprendi la chat")
        self.assertEqual(len(self.abi.loads), 2, "Chat should reuse the tested loaded model")
        self.assertIn("RISERVATO_CHAT", self.abi.calls[-1]["prompt"])

    def test_trial_applies_new_saved_model_and_inference_settings(self):
        self.abi.release.set()
        self.session.ask("Prima configurazione")
        model = self.root / "second.gguf"
        model.write_bytes(b"second fixture: never loaded")
        revised = replace(self.config, model=str(model), threads=3,
                          max_output=160, temperature=0.3)
        revised.save(default_native_settings_path())
        self.session.test_generation(config=revised)
        self.assertEqual(self.abi.loads, [self.config.model, revised.model])
        self.assertEqual(self.abi.calls[-1]["max_length"], 160)
        self.assertEqual(self.abi.calls[-1]["temperature"], 0.3)
        self.session.ask_isolated(lambda _: "Telegram dopo la prova")
        self.assertEqual(len(self.abi.loads), 2)
        self.assertEqual(self.abi.calls[-1]["max_length"], 160)

    def test_stale_trial_cannot_replace_current_backend(self):
        self.abi.release.set()
        self.session.ask("Prima configurazione")
        revised = replace(self.config, personality="Nuovo stile")
        revised.save(default_native_settings_path())
        with self.assertRaises(ValueError):
            self.session.test_generation(config=self.config)
        self.assertEqual(len(self.abi.loads), 1)
        self.assertEqual(len(self.abi.calls), 1)
        self.session.ask("Continua")
        self.assertEqual(len(self.abi.loads), 1)
        self.assertIn("Nuovo stile", self.abi.calls[-1]["prompt"])

    def test_failed_trial_does_not_stop_subsequent_chat(self):
        self.abi.release.set()
        self.session.ask("Chat precedente")
        history = list(self.session.history)
        with patch.object(self.abi, "generate", side_effect=RuntimeError("Controlled ABI failure")):
            with self.assertRaises(RuntimeError):
                self.session.test_generation(config=self.config)
        self.assertEqual(list(self.session.history), history)
        self.assertEqual(self.session.ask("Continua dopo errore"),
                         "Risposta locale controllata")
        self.assertEqual(len(self.abi.loads), 2)

    def test_telegram_waits_for_trial_without_history_changes(self):
        panel = self.window()
        panel.test_model()
        self.assertTrue(self.abi.first_started.wait(2))
        replies = []
        errors = []
        def telegram():
            try:
                replies.append(self.session.ask_isolated(lambda _: "Telegram isolato"))
            except Exception as exc:
                errors.append(type(exc).__name__)
        self.make_thread(target=telegram).start()
        self.abi.second_started.wait(1)
        self.assert_serialized()
        self.assertEqual(errors, [])
        self.assertEqual(replies, ["Risposta locale controllata"])
        self.assertEqual(list(self.session.history), [])
        self.assertEqual(len(self.abi.loads), 1)

    def test_generated_trial_without_owner_never_loads_a_backend(self):
        panel = self.window()
        panel.get_session = None
        panel.test_model()
        self.finish_workers()
        self.assertTrue(panel.status_value.startswith("TEST FALLITO"), panel.status_value)
        self.assertEqual(self.abi.loads, [])
        self.assertEqual(self.abi.calls, [])

