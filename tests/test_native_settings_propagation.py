"""JRV-AUD-008: actual settings Save -> session -> native ABI parameters.

Tk, JSON persistence, factory/provider/bridge are real. Native initialization
and inference use the existing controlled ABI; no real DLL/GGUF or account.
"""
from dataclasses import replace
import os
import threading
import tkinter as tk
import unittest
from unittest.mock import patch

import test_native_trial_ownership as ownership
from local_model.native_config import NativeModelConfig
from local_model.memory_preferences import MemoryPreferences, default_memory_preferences_path
from local_model.native_settings import default_native_settings_path
from local_model.native_ui import NativeSettingsWindow


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class NativeSettingsPropagationTests(unittest.TestCase):
    def setUp(self):
        self.harness = ownership.NativeTrialOwnershipTests()
        self.addCleanup(self.harness.doCleanups)
        self.harness.setUp()
        self.session, self.abi = self.harness.session, self.harness.abi
        self.abi.release.set()
        MemoryPreferences(recent_messages=16, prompt_max_tokens=1600).save(
            default_memory_preferences_path())
        self.initialized = []
        def initialize(module, config, source):
            self.initialized.append(config)
            self.abi.initialize(module, config, source)
        self.enterContext(patch("local_model.native_factory.initialize_kobold_cpu",
                                side_effect=initialize))
        self.abort = self.enterContext(patch.object(self.abi, "abort", wraps=self.abi.abort))
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.close_ui)
        self.panel = NativeSettingsWindow(self.root)
        # Join all workers before destroying test-owned Tk objects.
        self.addCleanup(self.harness.finish_workers)

    def close_ui(self):
        self.root.update_idletasks()
        self.root.destroy()

    def save(self, **changes):
        calls, loads = len(self.abi.calls), len(self.abi.loads)
        for key, value in changes.items():
            if key == "personality":
                self.panel.personality.delete("1.0", "end")
                self.panel.personality.insert("1.0", value)
            else:
                self.panel.values[key].set(str(value))
        self.assertTrue(self.panel.save())
        self.assertEqual((len(self.abi.calls), len(self.abi.loads)), (calls, loads),
                         "Save must not infer or load a model")
        return NativeModelConfig.load(default_native_settings_path())

    def assert_parameters(self, config):
        actual = self.abi.calls[-1]
        for key, value in dict(max_context_length=config.context_size,
                               max_length=config.max_output,
                               temperature=config.temperature, top_k=config.top_k,
                               top_p=config.top_p, sampler_seed=config.seed).items():
            self.assertEqual(actual[key], value, key)

    def test_each_saved_sampler_reaches_next_chat_without_reload(self):
        self.session.ask("Prima domanda controllata")
        for key, value in (("max_output", 64), ("temperature", 0.2),
                           ("top_k", 23), ("top_p", 0.6), ("seed", 17)):
            with self.subTest(field=key):
                config = self.save(**{key: value})
                before = len(self.abi.calls)
                self.session.ask("Domanda dopo Salva " + key)
                self.assertEqual(len(self.abi.calls), before + 1)
                self.assert_parameters(config)
                self.assertEqual(len(self.abi.loads), 1)
                self.abort.assert_not_called()
        self.assertIn("Prima domanda controllata", self.abi.calls[-1]["prompt"])

    def test_each_saved_load_setting_reloads_once_and_keeps_history(self):
        self.session.ask("Ricordo del progetto da conservare")
        model = self.harness.root / "second.gguf"
        model.write_bytes(b"fixture: never loaded")
        for index, (key, value) in enumerate((("threads", 3), ("batch_threads", 4),
                                             ("context_size", 4096), ("model", str(model))), 2):
            with self.subTest(field=key):
                config = self.save(**{key: value})
                history = list(self.session.history)
                self.session.ask("Dopo cambio " + key)
                self.assert_parameters(config)
                self.assertEqual(len(self.abi.loads), index)
                self.assertEqual(self.initialized[-1], config)
                self.assertTrue(os.path.samefile(self.abi.loads[-1], config.model))
                self.assertEqual(list(self.session.history)[:len(history)], history)
                self.assertIn("Ricordo del progetto", self.abi.calls[-1]["prompt"])
                self.session.ask_isolated(lambda _: "Richiesta isolata senza cambio")
                self.assertEqual(len(self.abi.loads), index)
        self.harness.assert_serialized()

    def test_saved_settings_apply_to_isolated_and_picker_without_history_changes(self):
        self.session.ask("Nota privata controllata")
        history = list(self.session.history)
        for name, changes, generate in (
            ("isolated", dict(max_output=80, temperature=0.4),
             lambda: self.session.ask_isolated(lambda _: "Messaggio Telegram controllato")),
            ("picker", dict(max_output=72, top_k=29),
             lambda: self.session.pick_program("Film controllato", ("Posta", "Video"))),
        ):
            with self.subTest(flow=name):
                config = self.save(**changes)
                generate()
                self.assert_parameters(config)
                self.assertNotIn("Nota privata", self.abi.calls[-1]["prompt"])
                self.assertEqual(list(self.session.history), history)
                self.assertEqual(len(self.abi.loads), 1)

    def test_saved_personality_keeps_model_and_changes_next_chat_prompt(self):
        self.session.ask("Prima domanda")
        self.save(personality="Tono preciso e breve")
        self.session.ask("Seconda domanda")
        self.assertIn("Tono preciso e breve", self.abi.calls[-1]["prompt"])
        self.assertEqual(len(self.abi.loads), 1)
        self.abort.assert_not_called()

    def test_invalid_ui_value_preserves_saved_bytes_and_working_session(self):
        self.session.ask("Prima domanda")
        original = default_native_settings_path().read_bytes()
        self.panel.values["temperature"].set("nan")
        with patch("local_model.native_ui.messagebox.showerror") as error:
            self.assertFalse(self.panel.save())
            error.assert_called_once()
        self.assertEqual(default_native_settings_path().read_bytes(), original)
        self.session.ask("Dopo errore campi")
        self.assert_parameters(self.harness.config)
        self.assertEqual(len(self.abi.loads), 1)

    def test_invalid_budget_never_generates_then_valid_settings_recover(self):
        self.session.ask("Prima domanda")
        history, calls = list(self.session.history), len(self.abi.calls)
        self.save(context_size=256, max_output=200)
        with self.assertRaises(ValueError):
            self.session.ask("Ciao")
        self.assertEqual(len(self.abi.calls), calls)
        self.assertEqual(list(self.session.history), history)
        config = self.save(max_output=64)
        self.session.ask("Ciao")
        self.assert_parameters(config)
        self.assertEqual(len(self.abi.loads), 2)

    def test_missing_saved_model_never_falls_back_and_recovery_keeps_history(self):
        self.session.ask("Prima domanda")
        history, calls = list(self.session.history), len(self.abi.calls)
        self.save(model=str(self.harness.root / "missing.gguf"))
        with self.assertRaises((OSError, RuntimeError)):
            self.session.ask("Modello mancante")
        self.assertEqual(len(self.abi.calls), calls)
        self.assertEqual(list(self.session.history), history)
        config = self.save(model=self.harness.config.model, max_output=88)
        self.session.ask("Riprendi")
        self.assert_parameters(config)
        self.assertIn("Prima domanda", self.abi.calls[-1]["prompt"])

    def test_normal_chat_keeps_validated_snapshot_if_file_changes_before_prepare(self):
        second = self.harness.root / "saved-later.gguf"
        second.write_bytes(b"fixture: never loaded")
        revised = replace(self.harness.config, model=str(second), max_output=64)
        loader = self.session.config_loader
        def snapshot_then_save():
            snapshot = loader()
            revised.save(default_native_settings_path())
            return snapshot
        self.session.config_loader = snapshot_then_save
        self.session.ask("Richiesta con snapshot")
        self.assert_parameters(self.harness.config)
        self.assertTrue(os.path.samefile(self.abi.loads[-1], self.harness.config.model))
        self.session.config_loader = loader
        self.session.ask("Richiesta successiva")
        self.assert_parameters(revised)
        self.assertEqual(len(self.abi.loads), 2)
        self.assertTrue(os.path.samefile(self.abi.loads[-1], revised.model))

    def test_save_during_inference_updates_only_the_next_queued_request(self):
        self.abi.release.clear()
        errors = []
        def ask(text):
            try:
                self.session.ask(text)
            except Exception as exc:
                errors.append(type(exc).__name__)
        self.harness.make_thread(target=lambda: ask("Richiesta in corso")).start()
        self.assertTrue(self.abi.first_started.wait(2))
        real_lock, waiting = self.session.lock, threading.Event()
        class ObserveLock:
            def __enter__(self):
                waiting.set()
                return real_lock.__enter__()
            def __exit__(self, *args):
                return real_lock.__exit__(*args)
        self.session.lock = ObserveLock()
        self.harness.make_thread(target=lambda: ask("Richiesta in coda")).start()
        self.assertTrue(waiting.wait(2))
        config = self.save(context_size=4096, threads=3, max_output=64, temperature=0.3)
        self.assertEqual(self.abi.calls[0]["max_length"], 128)
        self.assertEqual(len(self.abi.loads), 1)
        self.harness.assert_serialized()
        self.assertEqual(errors, [])
        self.assertEqual(len(self.abi.calls), 2)
        self.assert_parameters(config)
        self.assertEqual(len(self.abi.loads), 2)
        self.assertEqual(self.initialized[-1], config)

    def test_explicit_trial_then_saved_sampler_uses_current_values_without_extra_reload(self):
        self.session.ask("Nota privata")
        config = self.save(threads=3, max_output=96)
        self.session.test_generation(config=config)
        history = list(self.session.history)
        self.assertEqual(len(self.abi.loads), 2)
        self.assertNotIn("Nota privata", self.abi.calls[-1]["prompt"])
        config = self.save(max_output=48, temperature=0.1)
        self.session.ask_isolated(lambda _: "Messaggio dopo prova")
        self.assert_parameters(config)
        self.assertEqual(len(self.abi.loads), 2)
        self.assertEqual(list(self.session.history), history)
