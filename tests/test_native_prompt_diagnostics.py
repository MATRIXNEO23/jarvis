"""Jarvis 015: request-local prompt provenance never changes execution or storage."""
import unittest

from conversation_router import build_native_intent_context
from local_model.memory_preferences import MemoryPreferences
from local_model.native_config import NativeModelConfig
from local_model.native_conversation_session import NativeConversationSession
from test_native_conversation_session import FakeAdapter


class TokenAdapter(FakeAdapter):
    def __init__(self):
        super().__init__()
        self.tokenized = []

    def context_token_counter(self):
        def count(value):
            self.tokenized.append(value)
            return (len(value) + 3) // 4 + 1
        return count


class PromptDiagnosticTests(unittest.TestCase):
    def make_session(self, adapter=None):
        adapter = adapter or FakeAdapter()
        session = NativeConversationSession(
            adapter,
            config_loader=lambda: NativeModelConfig(
                context_size=2048, max_output=256,
                personality="Ironia secca"),
            memory_loader=lambda: MemoryPreferences(history_max_tokens=250))
        return session, adapter

    def test_default_disabled_has_no_prompt_capture_and_no_extra_work(self):
        session, adapter = self.make_session(TokenAdapter())
        turn = session.prepare_turn("Cos'è un buco nero?")
        self.assertEqual(turn.text, "risposta 1")
        self.assertIsNone(session.prompt_diagnostic())
        self.assertEqual(len(adapter.calls), 1)
        self.assertFalse(hasattr(turn, "prompt_diagnostic"))
        self.assertIn("Ironia secca", adapter.calls[0])
        self.assertNotIn("DIAGNOSTICA", adapter.calls[0])

    def test_exact_prompt_is_retained_only_after_manual_arm(self):
        session, adapter = self.make_session(TokenAdapter())
        session.ask("Parliamo della serie TV.")
        original = adapter.calls[-1]
        session.arm_prompt_diagnostic()
        self.assertIsNone(session.prompt_diagnostic())
        self.assertEqual(len(adapter.calls), 1)
        session.ask("Puoi approfondire?")
        captured = session.prompt_diagnostic()
        self.assertIsNotNone(captured)
        self.assertIn(adapter.calls[-1], captured)
        self.assertIn("Istruzioni / catalogo", captured)
        self.assertIn("NativeModelConfig.personality", captured)
        self.assertIn("Cronologia #1 utente", captured)
        self.assertIn("Cronologia #1 Gemma", captured)
        self.assertIn("Domanda corrente", captured)
        self.assertIn("format_gemma_messages", captured)
        self.assertIn("Context Size: 2048", captured)
        self.assertIn("Limite cronologia+ricordi: 250", captured)
        self.assertIn("token isolati", captured)
        self.assertEqual(len(adapter.calls), 2)
        self.assertEqual(adapter.calls[0], original)
        # Only one request is captured; later requests keep the last report.
        session.ask("Grazie")
        self.assertEqual(session.prompt_diagnostic(), captured)
        session.clear_prompt_diagnostic()
        self.assertIsNone(session.prompt_diagnostic())

    def test_structured_routing_shows_catalog_origin_without_executing(self):
        session, adapter = self.make_session()
        session.arm_prompt_diagnostic()
        turn = session.prepare_turn(
            "Apri il programma", intent_context=build_native_intent_context())
        report = session.prompt_diagnostic()
        self.assertIsNotNone(report)
        self.assertIn("JSON / azioni validate", report)
        self.assertIn("conversation_router.build_native_intent_context", report)
        self.assertIn("Rispondi SOLO JSON", report)
        self.assertIn(adapter.calls[-1], report)
        self.assertIsNotNone(turn.allowed_actions)
        self.assertEqual(len(adapter.calls), 1)

    def test_recall_source_visible_and_report_not_inserted_in_history(self):
        session, adapter = self.make_session(TokenAdapter())
        session.arm_prompt_diagnostic()
        turn = session.prepare_turn(
            "Cosa ricordi di lei?",
            memory_context=lambda budget: '{"tema":"serie TV"}')
        report = session.prompt_diagnostic()
        self.assertIn("jarvis.native_memory_request: Second Brain", report)
        self.assertIn('{"tema":"serie TV"}', report)
        self.assertEqual(len(adapter.calls), 1)
        self.assertTrue(turn.commit())
        self.assertNotIn("DIAGNOSTICA PROMPT", str(list(session.history)))
        self.assertNotIn("DIAGNOSTICA PROMPT", adapter.calls[-1])

    def test_f2_chat_recall_is_not_misidentified_as_second_brain(self):
        import tempfile
        from pathlib import Path
        from local_model.chat_sessions import ChatSessionStore
        from local_model.chat_context import make_chat_history_reader

        with tempfile.TemporaryDirectory() as folder:
            store = ChatSessionStore(Path(folder) / "separate.sqlite3")
            first = store.create_chat("Astronomia")
            second = store.create_chat("Musica")
            store.append_exchange(first.id, "Parliamo di Orione", "Orione è una costellazione")
            store.append_exchange(second.id, "Parliamo di Mozart", "Mozart è compositore")
            session, adapter = self.make_session(TokenAdapter())
            session.arm_prompt_diagnostic()
            session.ask("Che mi dicevi?", context_id=first.id,
                        memory_context=make_chat_history_reader(store, first.id))
            report = session.prompt_diagnostic()
            self.assertIn("ChatSessionsStore.recent_pairs: istanza isolata", report)
            self.assertIn("Nessuno: Chat locali F2", report)
            self.assertIn("Orione", report)
            self.assertNotIn("Mozart", report)
            self.assertNotIn("jarvis.native_memory_request: progetto", report)
            self.assertNotIn("jarvis.native_memory_request: Second Brain", report)
            self.assertIn(adapter.calls[-1], report)
            session.close()

    def test_manual_capture_does_not_change_exact_generated_prompt(self):
        import tempfile
        from pathlib import Path
        from local_model.chat_sessions import ChatSessionStore
        from local_model.chat_context import make_chat_history_reader

        with tempfile.TemporaryDirectory() as folder:
            store = ChatSessionStore(Path(folder) / "same.sqlite3")
            chat = store.create_chat("Prova")
            store.append_exchange(chat.id, "Lo spazio", "La galassia")
            reader = make_chat_history_reader(store, chat.id)
            first, adapter_first = self.make_session(TokenAdapter())
            second, adapter_second = self.make_session(TokenAdapter())
            first.ask("Approfondisci la galassia", context_id=chat.id,
                      memory_context=reader)
            second.arm_prompt_diagnostic()
            second.ask("Approfondisci la galassia", context_id=chat.id,
                       memory_context=reader)
            self.assertEqual(adapter_first.calls, adapter_second.calls)
            self.assertEqual(len(adapter_first.calls), 1)
            self.assertIn(adapter_second.calls[-1], second.prompt_diagnostic())
            first.close()
            second.close()

    def test_discard_during_inference_revokes_inflight_capture(self):
        session, adapter = self.make_session()
        original = adapter.call

        def discard_then_answer(*args, **kwargs):
            session.clear_prompt_diagnostic()
            return original(*args, **kwargs)

        adapter.call = discard_then_answer
        session.arm_prompt_diagnostic()
        self.assertEqual(session.ask("Messaggio da non conservare nel report"),
                         "risposta 1")
        self.assertIsNone(session.prompt_diagnostic())
        self.assertEqual(len(adapter.calls), 1)

    def test_clear_stop_close_do_not_keep_private_prompt(self):
        session, _ = self.make_session()
        session.arm_prompt_diagnostic()
        session.ask("Messaggio riservato")
        self.assertIn("Messaggio riservato", session.prompt_diagnostic())
        session.stop()
        self.assertIsNone(session.prompt_diagnostic())
        session.arm_prompt_diagnostic()
        session.clear_prompt_diagnostic()
        session.ask("Messaggio dopo scarto")
        self.assertIsNone(session.prompt_diagnostic())
        session.close()
        with self.assertRaises(RuntimeError):
            session.arm_prompt_diagnostic()

    def test_isolated_requests_do_not_consume_prompt_capture(self):
        session, adapter = self.make_session()
        session.arm_prompt_diagnostic()
        session.ask_isolated(lambda budget: "Test isolato")
        self.assertIsNone(session.prompt_diagnostic())
        session.ask("Domanda utente")
        report = session.prompt_diagnostic()
        self.assertIn("Domanda utente", report)
        self.assertNotIn("Test isolato", report)
        self.assertEqual(len(adapter.calls), 2)


    def test_failed_generation_keeps_capture_armed_for_next_question(self):
        # Review bug 5 (9/11): capture was consumed even when generation failed.
        class FailingOnce(TokenAdapter):
            def call(self, *args, **kwargs):
                if not getattr(self, "failed", False):
                    self.failed = True
                    raise RuntimeError("Controlled native failure")
                return super().call(*args, **kwargs)
        session, adapter = self.make_session(FailingOnce())
        session.arm_prompt_diagnostic()
        with self.assertRaises(RuntimeError):
            session.prepare_turn("Prima domanda")
        self.assertIsNone(session.prompt_diagnostic())
        session.prepare_turn("Seconda domanda")
        self.assertIn("Seconda domanda", session.prompt_diagnostic())


if __name__ == "__main__":
    unittest.main()
