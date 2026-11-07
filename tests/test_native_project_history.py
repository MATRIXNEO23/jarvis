"""JRV-AUD-002: real owner callbacks and local session, controlled inference.

Windows-only project requirement. Uses a temporary workspace, captured prompts
and explicitly scheduled workers; no DLL, GGUF, account or microphone.
"""
from collections import deque
import copy
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


class CapturedAdapter:
    def __init__(self):
        self.prompts = []
        self.prepares = 0
        self.on_reply = None

    def prepare(self):
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
            pending_project_reference=Mock(), pending_preference=None)
        self.harness = callbacks.ActivityStatusTests()
        for name in ("switch_context", "submit_gemma_voice", "poll_gemma_trial"):
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

    def test_local_chat_keeps_existing_persistent_project_records_untouched(self):
        self.workspace.add_turn("project", self.project_a, "Ricordo su disco", "Risposta su disco")
        before = self.workspace.recent("project", self.project_a)
        self.switch(self.project_a)
        self.ask("Scambio breve locale")
        self.switch(self.project_b)
        self.ask("Altro scambio")
        self.assertEqual(self.workspace.recent("project", self.project_a), before)
        self.assertEqual(self.adapter.prepares, 1)
