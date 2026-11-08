"""Regression contract for conversational Jarvis requests versus executable intents.

Uses an injected native adapter, never Windows actions, accounts, microphones or GGUF.
The decision must happen before sending the action catalog to Gemma.
"""
import unittest

from conversation_router import (
    native_intent_context_for_request,
    parse_native_conversation_intent,
)
from local_model.memory_preferences import MemoryPreferences
from local_model.native_config import NativeModelConfig
from local_model.native_conversation_session import NativeConversationSession


class CapturingAdapter:
    def __init__(self, answer):
        self.answer = answer
        self.calls = []
        self.prepares = 0

    def prepare(self, *, config=None):
        self.prepares += 1

    def call(self, action, *, messages=None, timeout=180, prompt_budget=None):
        from local_model.native_provider import format_gemma_messages
        self.calls.append(format_gemma_messages(messages))
        return {"text": self.answer}

    def stop(self):
        pass


class NativeInformationRoutingTests(unittest.TestCase):
    def test_informational_requests_skip_action_catalog(self):
        for question in (
            "Cos'è un buco nero?",
            "Che cos’è un buco nero?",
            "Cosa è un buco nero?",
            "consigliami una serie TV",
            "Mi consigli una serie TV?",
            "Spiegami cosa sono i buchi neri",
            "Perché una stella collassa?",
            "Come funziona un buco nero?",
            "Ti ricordi della cilena?",
            "Cosa ricordi di lei?",
            "Ricordi la cilena?",
            "Parlami di astronomia",
            "Ciao", "Grazie", "Continua",
            "Se dico apri browser cosa succede?",
            "Non aprire il browser",
            "Dimmi come funziona la calcolatrice",
        ):
            with self.subTest(question=question):
                self.assertIsNone(native_intent_context_for_request(question))

    def test_explicit_actions_keep_catalog_and_allowlist(self):
        for question in (
            "stato sistema",
            "mostrami lo stato del sistema",
            "apri Netflix",
            "Jarvis, apri Netflix",
            "avvia la calcolatrice",
            "mi apri blocco note?",
            "cerca sul PC il file",
            "scrivi nel blocco note",
            "manda un messaggio Telegram a Marco",
            "consigliami una serie TV e apri Netflix",
            "dimmi lo stato del sistema",
        ):
            with self.subTest(question=question):
                context = native_intent_context_for_request(question)
                self.assertIsNotNone(context)
                instructions, allowed = context
                self.assertIn("Rispondi SOLO JSON", instructions)
                self.assertIn("system.status", allowed)

    def test_chat_session_never_authorizes_action_even_for_json_like_text(self):
        for answer in (
            "Un buco nero è una regione dello spazio con gravità intensissima.",
            '{"kind":"capability","action_id":"system.status","arguments":{}}',
        ):
            with self.subTest(answer=answer):
                adapter = CapturingAdapter(answer)
                session = NativeConversationSession(
                    adapter,
                    config_loader=lambda: NativeModelConfig(
                        context_size=1024, max_output=256),
                    memory_loader=MemoryPreferences)
                question = "Cos'è un buco nero?"
                turn = session.prepare_turn(
                    question, intent_context=native_intent_context_for_request(question))
                self.assertIsNone(turn.allowed_actions)
                self.assertFalse(turn.accept_action())
                self.assertNotIn("Rispondi SOLO JSON", adapter.calls[0])
                self.assertNotIn("ID consentiti:", adapter.calls[0])
                self.assertIn(question, adapter.calls[0])
                self.assertEqual(len(adapter.calls), 1)

    def test_command_validation_remains_strict(self):
        intent = parse_native_conversation_intent(
            '{"kind":"capability","action_id":"system.status","arguments":{}}')
        self.assertEqual(intent.kind, "capability")
        from conversation_router import ConversationRejected
        with self.assertRaises(ConversationRejected):
            parse_native_conversation_intent(
                '{"kind":"capability","action_id":"system.status",'
                '"arguments":{"reply":"sorprendimi"}}')


if __name__ == "__main__":
    unittest.main()
