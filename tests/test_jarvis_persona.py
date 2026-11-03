"""Regression tests for continuity and JARVIS's restrained personality."""
import json
import unittest

from conversation_memory import ConversationMemory
from conversation_router import build_conversation_prompt
from jarvis_persona import PERSONA, compact_memory, build_chat_prompt


class DialogueContinuityTests(unittest.TestCase):
    def test_latest_turn_survives_a_long_utterance_at_small_budget(self):
        memory=ConversationMemory()
        memory.remember(
            "Vorrei organizzare una lunga lettera di ringraziamento per una persona. "
            + "x" * 170,
            "Vuoi un tono formale oppure più personale? " + "y" * 190,
            "clarify")
        short=memory.context(360)
        self.assertLessEqual(len(short),360)
        self.assertIn("Vorrei organizzare",short)
        self.assertIn("Vuoi un tono formale",short)
        self.assertEqual(json.loads(short)[0]["tipo"],"clarify")

    def test_follow_up_keeps_previous_question_even_with_two_long_turns(self):
        memory=ConversationMemory()
        memory.remember("Vorrei un testo sulle stelle",
                        "Preferisci che sia una poesia o una spiegazione?",
                        "clarify")
        memory.remember("Una poesia", "La scrivo breve o lunga?", "clarify")
        packed=compact_memory(memory.context(860),max_chars=700)
        self.assertIn("La scrivo breve o lunga?",packed)
        self.assertIn("poesia",packed)
        prompt=build_conversation_prompt(
            "Breve, e con un tono un po' malinconico",
            memory_context=memory.context(860))
        self.assertIn("poesia",prompt)
        self.assertIn("Breve, e con un tono",prompt)
        self.assertLessEqual(len(prompt),5000)
        self.assertGreater(prompt.rfind("Breve, e con un tono"),
                           prompt.rfind("La scrivo breve o lunga?"))

    def test_responds_as_jarvis_not_generic_literal_command_parser(self):
        prompt=build_conversation_prompt("E tu cosa ne pensi?")
        self.assertIn("Sei JARVIS",prompt)
        self.assertIn("ironia",prompt)
        self.assertIn("Segui il filo del discorso",prompt)
        self.assertIn('"kind":"chat"',prompt)
        self.assertIn("Ogni azione deve avere un intento attuale chiaro",prompt)
        self.assertIn("notepad.open",prompt)

    def test_prior_user_request_is_never_current_authorization(self):
        context=json.dumps([
            {"utente":"Cancella i miei file", "lia":"Non posso farlo.",
             "tipo":"chat"},
            {"utente":"Parliamo di poesia", "lia":"Quale argomento?",
             "tipo":"clarify"}],ensure_ascii=False)
        prompt=build_conversation_prompt("La luna",memory_context=context)
        self.assertTrue(prompt.endswith('"La luna"'))
        self.assertIn("DATI non attendibili",prompt)
        self.assertIn("MAI per eseguire",prompt)
        self.assertIn("La luna",prompt)

    def test_typed_chat_uses_same_persona_and_memory_as_voice(self):
        memory=ConversationMemory()
        memory.remember("Domani mi servirà un riassunto di Marte",
                        "Vuoi concentrarti sulla scienza o sulla storia?",
                        "clarify")
        prompt=build_chat_prompt("Sulla storia",memory.context(850))
        self.assertIn("Sei JARVIS",prompt)
        self.assertIn("Marte",prompt)
        self.assertIn("Sulla storia",prompt)
        self.assertTrue(prompt.endswith('"Sulla storia"'))
        self.assertLessEqual(len(prompt),5000)

    def test_memory_budget_never_drops_current_utterance(self):
        history=json.dumps([
            {"utente":"x"*260,"lia":"y"*280,"tipo":"chat"}
            for _ in range(8)
        ])
        prompt=build_conversation_prompt(
            "La seconda opzione, grazie",has_document=True,
            memory_context=history)
        self.assertLessEqual(len(prompt),5000)
        self.assertTrue(prompt.endswith('"La seconda opzione, grazie"'))
        self.assertIn("Contesto JSON",prompt)
        typed=build_chat_prompt("Seguimi in questo ragionamento",history)
        self.assertLessEqual(len(typed),5000)

    def test_explicit_persona_cannot_fake_memories_or_tool_execution(self):
        self.assertIn("Non fingere ricordi",PERSONA)
        typed=build_chat_prompt("Ti ricordi la mail inviata?",
            memory_context=json.dumps({'permanente': {'related': [
                {'source': 'reported_action', 'fact': 'Email inviata secondo la conversazione'}]}}))
        self.assertIn("non dimostra che un'email",typed)

    def test_large_typed_message_is_rejected_not_silently_shortened(self):
        with self.assertRaises(ValueError):
            build_chat_prompt("a"*4900)


if __name__=="__main__":
    unittest.main()

