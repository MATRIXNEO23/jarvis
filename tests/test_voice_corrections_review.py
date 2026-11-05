"""V01: real correction UI, SQLite and voice callbacks on Windows.

Transcripts are controlled inputs. These tests do not exercise a microphone,
Vosk acoustic recognition, a live GPT account, or Pavilion performance.
"""
import ast
import copy
import json
import os
from pathlib import Path
import queue
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import Mock, patch

from adaptive_voice import SpeechCorrections, SpeechCorrectionError
from desktop_dictation import dictation_voice_action
from second_brain import SecondBrain
from settings import default_path, load_settings, save_settings
from voice_control import (CONTINUOUS, GPT_CONVERSATION, PUSH_TO_TALK,
                           STANDBY, WakeWordGate, speech_to_local_command)
from test_activity_status import GlobalCallbacks, Value


@unittest.skipUnless(os.name == "nt", "Windows-only user requirement")
class VoiceCorrectionReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tree = ast.parse(Path("jarvis.py").read_text(encoding="utf-8"))
        cls.main = next(n for n in tree.body
                        if isinstance(n, ast.FunctionDef) and n.name == "main")
        cls.poll = next(n for n in cls.main.body
                        if isinstance(n, ast.FunctionDef) and n.name == "poll")

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.profile = Path(self.temp.name) / "trial"
        self.environ = patch.dict(os.environ, {
            "LOCALAPPDATA": str(Path(self.temp.name) / "local"),
            "JARVIS_TRIAL_HOME": str(self.profile),
        })
        self.environ.start()
        self.addCleanup(self.environ.stop)
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.close_root)
        self.words = SpeechCorrections()
        self.env = dict(
            root=self.root, tk=tk, ttk=ttk, messagebox=Mock(),
            speech_lexicon=self.words, SpeechCorrections=SpeechCorrections,
            SpeechCorrectionError=SpeechCorrectionError, sqlite3=sqlite3,
            memory_enabled=tk.BooleanVar(master=self.root, value=True),
            last_voice_sample=tk.StringVar(master=self.root,
                                           value="apri blocco moto"),
            write_line=Mock(), memory_status_refresh=Mock(),
            SecondBrain=SecondBrain, durable_brain=SecondBrain(self.words.path),
            settings={**load_settings(), "memory_enabled": True},
            save_settings=save_settings,
        )

    def close_root(self):
        # Drain pending ttk theme events before destroying their interpreter.
        # Otherwise the next test's Tk instance can receive stale events.
        self.root.update_idletasks()
        self.root.destroy()

    def callback(self, name):
        node = copy.deepcopy(next(n for n in self.main.body
                                  if isinstance(n, ast.FunctionDef)
                                  and n.name == name))
        node = GlobalCallbacks().visit(node)
        module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
        exec(compile(module, "actual-jarvis-" + name, "exec"), self.env)
        return self.env[name]

    def popup(self):
        self.callback("show_voice_corrections")()
        self.root.update_idletasks()
        return next(w for w in self.root.winfo_children()
                    if isinstance(w, tk.Toplevel))

    def descendants(self, widget):
        for child in widget.winfo_children():
            yield child
            yield from self.descendants(child)

    def button(self, popup, label):
        return next(w for w in self.descendants(popup)
                    if isinstance(w, ttk.Button) and w.cget("text") == label)

    def status(self, popup):
        return " ".join(str(self.root.getvar(w.cget("textvariable")))
                        for w in self.descendants(popup)
                        if isinstance(w, ttk.Label) and w.cget("textvariable"))

    def enter_correction(self, popup, text="apri blocco note"):
        entries = [w for w in self.descendants(popup) if isinstance(w, ttk.Entry)]
        self.assertEqual(entries[0].get(), "apri blocco moto")
        entries[1].insert(0, text)
        self.button(popup, "Conferma correzione").invoke()

    def test_real_popup_saves_rule_and_new_process_loads_it(self):
        popup = self.popup()
        self.enter_correction(popup)
        self.assertIn("Imparato:", self.status(popup))
        child = subprocess.run([
            sys.executable, "-c",
            "import json,sys; from pathlib import Path; "
            "from adaptive_voice import SpeechCorrections; "
            "w=SpeechCorrections(Path(sys.argv[1])); "
            "print(json.dumps([w.count(),w.correct('apri blocco moto')]))",
            str(self.words.path),
        ], check=True, capture_output=True, text=True, timeout=20)
        self.assertEqual(json.loads(child.stdout), [1, "apri blocco note"])

    def test_popup_does_not_claim_success_when_database_write_fails(self):
        popup = self.popup()
        with patch.object(self.words, "learn_phrase",
                          side_effect=sqlite3.OperationalError("controlled write failure")):
            self.enter_correction(popup)
        self.assertIn("Correzione non salvata:", self.status(popup))
        self.assertNotIn("Imparato:", self.status(popup))
        self.env["write_line"].assert_not_called()
        self.assertEqual(SpeechCorrections(self.words.path).count(), 0)

    def test_popup_rejects_a_change_of_action(self):
        popup = self.popup()
        self.enter_correction(popup, "chiudi blocco note")
        self.assertIn("Correzione non salvata:", self.status(popup))
        self.assertEqual(self.words.count(), 0)

    def test_disabled_memory_prevents_popup_and_rule_creation(self):
        self.env["memory_enabled"].set(False)
        self.callback("show_voice_corrections")()
        self.env["messagebox"].showinfo.assert_called_once()
        self.assertFalse(self.root.winfo_children())
        self.assertEqual(self.words.count(), 0)

    def test_turning_memory_off_after_opening_popup_prevents_save(self):
        popup = self.popup()
        self.env["memory_enabled"].set(False)
        self.enter_correction(popup)
        self.assertIn("non salvo correzioni", self.status(popup))
        self.assertEqual(self.words.count(), 0)

    def test_reset_requires_confirmation_and_preserves_other_memories(self):
        self.words.add("blocco moto", "blocco note", user_confirmed=True)
        brain = self.env["durable_brain"]
        brain.remember_turn("Frase controllata", "Risposta controllata")
        previous_stats = brain.stats()
        popup = self.popup()
        self.env["messagebox"].askyesno.return_value = False
        self.button(popup, "Azzera correzioni").invoke()
        self.assertEqual(self.words.count(), 1)
        self.env["messagebox"].askyesno.return_value = True
        self.button(popup, "Azzera correzioni").invoke()
        self.assertEqual(SpeechCorrections(self.words.path).count(), 0)
        self.assertEqual(brain.stats(), previous_stats)

    def test_memory_toggle_disables_rules_without_erasing_and_reloads_them(self):
        self.words.add("blocco moto", "blocco note", user_confirmed=True)
        toggle = self.callback("toggle_memory")
        self.env["memory_enabled"].set(False)
        toggle()
        self.assertIsNone(self.env["speech_lexicon"])
        self.assertFalse(load_settings()["memory_enabled"])
        self.assertEqual(SpeechCorrections(self.words.path).count(), 1)
        self.env["memory_enabled"].set(True)
        toggle()
        self.assertTrue(load_settings()["memory_enabled"])
        self.assertEqual(self.env["speech_lexicon"].correct("apri blocco moto"),
                         "apri blocco note")

    def test_failed_memory_preference_save_preserves_active_lexicon(self):
        self.words.add("blocco moto", "blocco note", user_confirmed=True)
        self.env["save_settings"] = Mock(side_effect=OSError("controlled save failure"))
        self.env["memory_enabled"].set(False)
        self.callback("toggle_memory")()
        self.assertTrue(self.env["memory_enabled"].get())
        self.assertTrue(self.env["settings"]["memory_enabled"])
        self.assertIs(self.env["speech_lexicon"], self.words)

    def test_normal_and_trial_profile_corrections_remain_separate(self):
        with patch.dict(os.environ, {"JARVIS_TRIAL_HOME": ""}):
            normal = SpeechCorrections()
            normal.add("blocco moto", "blocco note", user_confirmed=True)
            original_path = default_path()
            original_bytes = normal.path.read_bytes()
        self.assertNotEqual(self.words.path, normal.path)
        self.words.add("scolle", "scuole", user_confirmed=True)
        self.assertEqual(self.words.correct("blocco moto"), "blocco moto")
        self.assertEqual(normal.correct("scolle"), "scolle")
        self.assertEqual(normal.path.read_bytes(), original_bytes)
        self.assertNotEqual(default_path(), original_path)

    def receive_voice(self, text):
        branch = next(n for n in ast.walk(self.poll)
                      if isinstance(n, ast.If) and isinstance(n.test, ast.Compare)
                      and isinstance(n.test.left, ast.Name) and n.test.left.id == "kind"
                      and isinstance(n.test.comparators[0], ast.Constant)
                      and n.test.comparators[0].value == "voice_text")
        wrapper = ast.For(target=ast.Name(id="_event", ctx=ast.Store()),
                          iter=ast.Tuple(elts=[ast.Constant(1)], ctx=ast.Load()),
                          body=copy.deepcopy(branch.body), orelse=[])
        self.env["data"] = [text]
        module = ast.fix_missing_locations(ast.Module(body=[wrapper], type_ignores=[]))
        exec(compile(module, "actual-voice-text-callback", "exec"), self.env)

    def voice_environment(self, mode=GPT_CONVERSATION, memory=True):
        self.env.update(
            engine=SimpleNamespace(program_apps=None),
            voice_mode=Value(mode), memory_enabled=Value(memory),
            STANDBY=STANDBY, GPT_CONVERSATION=GPT_CONVERSATION,
            CONTINUOUS=CONTINUOUS, speaker=SimpleNamespace(is_audible=lambda: False),
            wake_gate=WakeWordGate(), dictation=SimpleNamespace(enabled=False),
            dictation_voice_action=dictation_voice_action,
            telegram_voice_dialog=SimpleNamespace(pending=False), addon_manager=None,
            try_file_command=Mock(return_value=False),
            try_timer_command=Mock(return_value=False),
            try_self_diagnostic=Mock(return_value=False),
            try_telegram_voice_send=Mock(return_value=False), save_only_waiting=False,
            doc_dialog=SimpleNamespace(phase="idle"), document_busy=False,
            parse_simple_save=lambda _: None, classify_document_choice=lambda *a, **k: None,
            project_voice_command=lambda _: False, preference_command=lambda _: False,
            handle_project_reference=lambda _: False,
            handle_unanchored_short_reply=lambda _: False,
            maybe_queue_telegram_note=lambda _: False,
            speech_to_local_command=speech_to_local_command, busy_local=False,
            gpt_enabled=Value(True), active_gpt=True, busy_gpt=False,
            gemma_trial_busy=[False],
            start_conversation_gpt=Mock(), submit_local=Mock(),
        )

    def test_corrected_transcript_reaches_actual_file_dispatch_in_each_listening_mode(self):
        self.words.add("blocco moto", "blocco note", user_confirmed=True)
        for mode in (GPT_CONVERSATION, PUSH_TO_TALK, CONTINUOUS):
            with self.subTest(mode=mode):
                self.voice_environment(mode)
                self.env["try_file_command"].return_value = True
                self.receive_voice("ehi jarvis cerca file blocco moto")
                expected = ("cerca file blocco note" if mode in (CONTINUOUS, GPT_CONVERSATION)
                            else "ehi jarvis cerca file blocco note")
                self.env["try_file_command"].assert_called_once_with(expected)
                self.assertEqual(self.env["last_voice_sample"].get(),
                                 "ehi jarvis cerca file blocco moto")
                self.env["start_conversation_gpt"].assert_not_called()

    def test_corrected_local_command_is_dispatched_once_without_gpt(self):
        self.words.add("brouser", "browser", user_confirmed=True)
        self.voice_environment()
        self.receive_voice("Jarvis apri brouser")
        self.env["submit_local"].assert_called_once_with(
            message_override="apri browser", source_utterance="apri browser")
        self.env["start_conversation_gpt"].assert_not_called()

    def test_unresolved_corrected_text_reaches_gpt_once_without_changing_mode(self):
        self.words.add("blocco moto", "blocco note", user_confirmed=True)
        self.voice_environment()
        self.receive_voice("Jarvis mi racconti di blocco moto")
        self.env["start_conversation_gpt"].assert_called_once_with(
            "mi racconti di blocco note")
        self.env["submit_local"].assert_not_called()
        self.assertEqual(self.env["voice_mode"].get(), GPT_CONVERSATION)

    def test_disabled_memory_passes_raw_text_and_standby_discards_input(self):
        self.words.add("blocco moto", "blocco note", user_confirmed=True)
        self.voice_environment(memory=False)
        self.env["try_file_command"].return_value = True
        self.receive_voice("Jarvis cerca file blocco moto")
        self.env["try_file_command"].assert_called_once_with("cerca file blocco moto")
        self.voice_environment(STANDBY)
        self.receive_voice("cerca file blocco moto")
        self.env["try_file_command"].assert_not_called()
        self.env["start_conversation_gpt"].assert_not_called()
        self.env["submit_local"].assert_not_called()


if __name__ == "__main__":
    unittest.main()


