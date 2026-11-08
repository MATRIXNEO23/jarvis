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


if __name__ == "__main__":
    unittest.main()
