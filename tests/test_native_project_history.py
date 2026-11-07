"""JRV-AUD-002: real owner callbacks and local session, controlled inference.

Windows-only project requirement. Uses a temporary workspace, captured prompts
and explicitly scheduled workers; no DLL, GGUF, account or microphone.
"""
from collections import deque
import json
import os
from pathlib import Path
import queue
import re
import sqlite3
import time
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

import test_activity_status as callbacks
from conversation_memory import ConversationMemory
from local_model.chat_transport import ChatTransport
from local_model.memory_preferences import MemoryPreferences
from local_model.native_config import NativeModelConfig
from local_model.native_conversation_session import NativeConversationSession
from workspace_memory import WorkspaceMemory, WorkspaceError
from second_brain import BrainError


class CapturedAdapter:
    def __init__(self):
        self.prompts = []
        self.prepares = 0
        self.on_reply = None

    def prepare(self, *, config=None):
        self.prepares += 1

    def call(self, action, *, prompt, timeout):
        self.prompts.append(prompt)
        if self.on_reply is not None:
            callback, self.on_reply = self.on_reply, None
            callback()
        return {"text": "Risposta locale " + str(len(self.prompts))}


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class NativeProjectHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        callbacks.ActivityStatusTests.setUpClass()

    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        folder = Path(temporary.name)
        source = folder / "koboldcpp.py"
        source.write_text("# Controlled source path; never imported by this test.\n", encoding="utf-8")
        self.workspace = WorkspaceMemory(folder / "workspace.sqlite3")
        self.project_a = self.workspace.create_project("Progetto A")
        self.project_b = self.workspace.create_project("Progetto B")
        self.adapter = CapturedAdapter()
        self.session = NativeConversationSession(
            self.adapter,
            config_loader=lambda: NativeModelConfig(context_size=2048, max_output=128),
            memory_loader=lambda: MemoryPreferences(prompt_max_tokens=1200))
        self.workers = []
        self.online = Mock()
        self.env = dict(
            closing=False, gemma_trial_busy=[False], gemma_source=[str(source)],
            gemma_recent_reply=[None], gemma_button=Mock(), write_line=Mock(),
            speak_result=Mock(), conversation_epoch=7, active_project_id=None,
            get_gemma_session=lambda: self.session,
            gemma_trial_queue=queue.Queue(), queue=queue, re=re, time=time, Path=Path,
            threading=SimpleNamespace(Thread=lambda *, target, **kwargs:
                                      SimpleNamespace(start=lambda: self.workers.append(target))),
            chat_transport=ChatTransport(self.online, native=None),
            root=SimpleNamespace(after=Mock()), workspace=self.workspace,
            busy_gpt=False, busy_local=False, document_busy=False,
            documents=SimpleNamespace(current=None), doc_dialog=SimpleNamespace(phase="idle"),
            addon_manager=None, active_context_label=callbacks.Value("Generale"),
            workspace_status=callbacks.Value(""), sqlite3=sqlite3, WorkspaceError=WorkspaceError,
            conversation_memory=ConversationMemory(), pending_conversation=deque(),
            pending_project_reference=Mock(), pending_preference=None,
            json=json, memory_enabled=callbacks.Value(False), durable_brain=None,
            gemma_memory_revision=0, gemma_session=[self.session], BrainError=BrainError,
            memory_status=callbacks.Value(""), memory_status_refresh=Mock())
        self.harness = callbacks.ActivityStatusTests()
        for name in ("switch_context", "native_memory_request", "remember_exchange",
                     "submit_gemma_voice", "poll_gemma_trial"):
            self.harness.callback(name, self.env)

    def switch(self, project):
        self.assertTrue(self.env["switch_context"](project))

    def submit(self, text, *, typed=False):
        self.assertTrue(self.env["submit_gemma_voice"](text, typed=typed))
        self.assertEqual(len(self.workers), 1)

    def finish(self):
        self.workers.pop()()
        self.env["poll_gemma_trial"]()

    def ask(self, text, *, typed=False):
        self.submit(text, typed=typed)
        self.finish()
        return self.adapter.prompts[-1]

    def test_projects_and_general_chat_recall_only_their_own_turns(self):
        self.switch(self.project_a)
        self.ask("RISERVATO_A: il colore è rosso", typed=True)
        self.switch(None)
        general = self.ask("RISERVATO_GENERALE: il colore è verde")
        self.assertNotIn("RISERVATO_A", general)
        self.switch(self.project_b)
        second = self.ask("RISERVATO_B: il colore è blu")
        self.assertNotIn("RISERVATO_A", second)
        self.assertNotIn("RISERVATO_GENERALE", second)
        self.switch(self.project_a)
        first = self.ask("Qual era il colore?", typed=True)
        self.assertIn("RISERVATO_A", first)
        self.assertNotIn("RISERVATO_B", first)
        self.assertNotIn("RISERVATO_GENERALE", first)
        self.assertEqual(self.adapter.prepares, 1)
        self.online.call.assert_not_called()

    def test_revoked_queued_reply_never_enters_history_for_voice_or_text(self):
        self.switch(self.project_a)
        for typed in (False, True):
            with self.subTest(typed=typed):
                self.submit("NON_CONSERVARE_QUESTO_TURNO", typed=typed)
                self.workers.pop()()  # Reply exists, but UI has not accepted it.
                self.env["conversation_epoch"] += 1  # Mode/permission revocation.
                self.env["write_line"].reset_mock()
                self.env["speak_result"].reset_mock()
                self.env["poll_gemma_trial"]()
                self.env["write_line"].assert_not_called()
                self.env["speak_result"].assert_not_called()
                prompt = self.ask("Domanda successiva", typed=typed)
                self.assertNotIn("NON_CONSERVARE_QUESTO_TURNO", prompt)

    def test_change_project_and_return_during_generation_revokes_the_turn(self):
        self.switch(self.project_a)
        def change_and_return():
            self.switch(self.project_b)
            self.switch(self.project_a)
        self.adapter.on_reply = change_and_return
        self.ask("RISPOSTA_ORMAI_REVOCATA")
        self.assertNotIn("RISPOSTA_ORMAI_REVOCATA", self.ask("Nuova domanda"))
        self.assertEqual(self.adapter.prepares, 1)

    def test_worker_keeps_dispatch_context_when_project_changes_before_start(self):
        self.switch(self.project_a)
        self.ask("NOTA_DI_A")
        self.switch(self.project_b)
        self.ask("NOTA_DI_B")
        self.switch(self.project_a)
        self.submit("Domanda destinata ad A")
        self.switch(self.project_b)
        self.finish()
        prompt = self.adapter.prompts[-1]
        self.assertIn("NOTA_DI_A", prompt)
        self.assertNotIn("NOTA_DI_B", prompt)

    def test_local_chat_preserves_existing_records_and_appends_accepted_project_turns(self):
        self.workspace.add_turn("project", self.project_a, "Ricordo su disco", "Risposta su disco")
        before = self.workspace.recent("project", self.project_a)
        self.switch(self.project_a)
        self.ask("Scambio breve locale")
        self.switch(self.project_b)
        self.ask("Altro scambio")
        after = self.workspace.recent("project", self.project_a)
        self.assertEqual(after[:len(before)], before)
        self.assertEqual(len(after), len(before) + 1)
        self.assertEqual(len(self.workspace.recent("project", self.project_b)), 1)
        self.assertEqual(self.adapter.prepares, 1)

    def test_prepared_reply_is_remembered_only_after_single_acceptance(self):
        turn = self.session.prepare_turn("Ancora da accettare", context_id=self.project_a)
        self.session.prepare_turn("Altra domanda", context_id=self.project_a)
        self.assertNotIn("Ancora da accettare", self.adapter.prompts[-1])
        self.assertTrue(turn.commit())
        self.assertFalse(turn.commit())
        self.session.prepare_turn("Domanda finale", context_id=self.project_a)
        self.assertEqual(self.adapter.prompts[-1].count("Utente: Ancora da accettare"), 1)

    def test_total_history_budget_remains_shared_between_projects(self):
        contexts = [format(i, "032x") for i in range(16)]
        for index, context in enumerate(contexts):
            self.session.ask("Nota univoca " + str(index), context_id=context)
        self.session.prepare_turn("Che ricordi?", context_id=contexts[0])
        self.assertIn("Utente: Nota univoca 0", self.adapter.prompts[-1])
        self.session.ask("Nuovo scambio generale")
        self.session.prepare_turn("Che ricordi?", context_id=contexts[0])
        self.assertNotIn("Utente: Nota univoca 0", self.adapter.prompts[-1])
        self.assertNotIn("Nuovo scambio generale", self.adapter.prompts[-1])
        self.assertEqual(self.adapter.prepares, 1)

    def test_isolated_telegram_and_picker_do_not_use_or_change_project_recall(self):
        self.session.ask("Nota privata A", context_id=self.project_a)
        self.session.ask("Nota privata B", context_id=self.project_b)
        self.session.ask_isolated(lambda budget: "Solo il contatto Telegram")
        self.assertEqual(self.adapter.prompts[-1], "Solo il contatto Telegram")
        self.session.pick_program("Scrivere una nota", ("Editor", "Posta"))
        self.assertNotIn("Nota privata", self.adapter.prompts[-1])
        self.session.prepare_turn("Domanda di A", context_id=self.project_a)
        self.assertIn("Nota privata A", self.adapter.prompts[-1])
        self.assertNotIn("Nota privata B", self.adapter.prompts[-1])
        self.assertNotIn("Solo il contatto Telegram", self.adapter.prompts[-1])
        self.assertNotIn("Scrivere una nota", self.adapter.prompts[-1])

    def test_poll_acceptance_does_not_wait_for_native_generation_lock(self):
        import threading
        self.switch(self.project_a)
        turn = self.session.prepare_turn("Turno pronto", context_id=self.project_a)
        self.env["gemma_trial_queue"].put(("ok", turn, self.env["conversation_epoch"]))
        self.env["gemma_trial_busy"][0] = True
        entered, release, accepted = threading.Event(), threading.Event(), threading.Event()
        errors = []
        def hold_backend():
            entered.set()
            if not release.wait(10):
                raise RuntimeError("Test backend was not released")
        self.adapter.on_reply = hold_backend
        def generate():
            try:
                self.session.ask_isolated(lambda budget: "Inferenza in corso")
            except Exception as exc:
                errors.append(exc)
        def commit():
            try:
                self.env["poll_gemma_trial"]()
            except Exception as exc:
                errors.append(exc)
            finally:
                accepted.set()
        inference = threading.Thread(target=generate, daemon=True)
        metadata = threading.Thread(target=commit, daemon=True)
        inference.start()
        try:
            self.assertTrue(entered.wait(3))
            metadata.start()
            self.assertTrue(accepted.wait(3), "UI history acceptance waited for native inference")
        finally:
            release.set()
            inference.join(5)
            if metadata.ident is not None:
                metadata.join(5)
        self.assertFalse(inference.is_alive())
        self.assertFalse(metadata.is_alive())
        self.assertEqual(errors, [])
        self.env["speak_result"].assert_called_once_with(turn.text)
        self.assertFalse(self.env["gemma_trial_busy"][0])

    def test_invalid_context_never_loads_model(self):
        for context in ("", "../project", "name", 42):
            with self.subTest(context=context), self.assertRaises(ValueError):
                self.session.prepare_turn("Domanda", context_id=context)
        self.assertEqual(self.adapter.prepares, 0)
        self.assertEqual(self.adapter.prompts, [])

    def test_poll_rejects_mismatched_context_even_if_epoch_matches(self):
        self.switch(self.project_a)
        self.submit("Domanda di A")
        self.workers.pop()()
        # Defensive boundary check, independently of the regular epoch change.
        self.env["active_project_id"] = self.project_b
        self.env["poll_gemma_trial"]()
        self.env["active_project_id"] = self.project_a
        self.assertNotIn("Domanda di A", self.ask("Nuova domanda"))

    def test_app_followup_uses_only_an_accepted_voice_or_typed_turn(self):
        provider = SimpleNamespace(
            available=lambda: True,
            entries=lambda: [dict(id="netflix", name="Netflix", enabled=True, available=True)])
        submit_local = Mock()
        self.env.update(engine=SimpleNamespace(program_apps=provider),
                        save_only_waiting=False, pending_project_name=False,
                        pending_project_rename_id=None, pending_project_trash_id=None,
                        submit_local=submit_local)
        followup = self.harness.callback("try_gemma_app_followup", self.env)
        self.switch(self.project_a)
        for typed in (False, True):
            with self.subTest(typed=typed):
                self.ask("Vorrei guardare Netflix", typed=typed)
                self.assertTrue(followup("me lo apri?"))
                submit_local.assert_called_once_with(
                    message_override="me lo apri?", source_utterance="me lo apri?",
                    addon_action_id="addon.programmi_app.avvia",
                    program_call=("suggest_id", {"query": "netflix"}))
                submit_local.reset_mock()
                self.submit("Vorrei guardare Netflix", typed=typed)
                self.workers.pop()()
                self.env["conversation_epoch"] += 1
                self.env["poll_gemma_trial"]()
                self.assertIsNone(self.env["gemma_recent_reply"][0])
                self.assertFalse(followup("me lo apri?"))
                submit_local.assert_not_called()
