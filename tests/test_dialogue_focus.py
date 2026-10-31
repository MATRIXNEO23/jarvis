"""Focused tests for short answers, project deixis and one clarification."""
import json
import unittest

from conversation_memory import ConversationMemory
from conversation_router import build_conversation_prompt, parse_conversation_intent
from dialogue_focus import (
    PendingProjectReference,focus_hint,is_short_followup,
    is_unusable_project_name,mentions_current_project,
    needs_project_clarification,single_question,
)
from jarvis_persona import build_chat_prompt,compact_memory
from project_voice import parse_project_voice,safe_project_name


class BriefReplyTests(unittest.TestCase):
    def test_short_answer_attaches_only_to_real_latest_question(self):
        memory=ConversationMemory()
        self.assertEqual(memory.last_question(),"")
        memory.remember("Vogliamo iniziare?","Quale progetto vuoi aprire?","clarify")
        focus=focus_hint("Sì",last_question=memory.last_question())
        self.assertEqual(focus["pending_question"],"Quale progetto vuoi aprire?")
        self.assertEqual(focus["follow_up"],"Sì")
        memory.remember("Minecraft","Ho trovato il progetto.","action")
        self.assertEqual(memory.last_question(),"")
        self.assertNotIn("pending_question",
                         focus_hint("Sì",last_question=memory.last_question()))

    def test_chat_question_and_replies_do_not_create_authorization(self):
        memory=ConversationMemory()
        memory.remember("Che facciamo?","Quale argomento vuoi approfondire?","chat")
        self.assertTrue(is_short_followup("Quello"))
        self.assertTrue(is_short_followup("Minecraft"))
        self.assertEqual(focus_hint("Quello",last_question=memory.last_question())[
                         "pending_question"],"Quale argomento vuoi approfondire?")
        memory.clear()
        self.assertEqual(memory.last_question(),"")
        self.assertNotIn("pending_question",focus_hint("Quello"))
        self.assertEqual(single_question("Quale file intendi? In quale cartella?"),
                         "Quale file intendi?")
        self.assertEqual(parse_conversation_intent(json.dumps({
            "kind":"clarify",
            "reply":"Quale file intendi? E quale cartella?"})).reply,
            "Quale file intendi?")

    def test_yes_no_are_not_valid_project_names(self):
        for answer in ("sì","no","okay","quello","questa","non lo so"):
            with self.subTest(answer=answer):
                self.assertTrue(is_unusable_project_name(answer))
                with self.assertRaises(ValueError):
                    safe_project_name(answer)
        self.assertEqual(safe_project_name("Minecraft Builder"),"Minecraft Builder")


class ProjectReferenceTests(unittest.TestCase):
    def test_current_project_is_real_scope_not_guessed_name(self):
        selected=focus_hint("Cosa abbiamo fatto su questo progetto?",
                            active_project_name="Minecraft Builder")
        self.assertEqual(selected["project"]["name"],"Minecraft Builder")
        self.assertNotIn("pending_question",selected)
        self.assertTrue(mentions_current_project(
            "Parlami di questo progetto"))
        self.assertTrue(needs_project_clarification(
            "Come procede questo progetto?",project_selected=False))
        self.assertFalse(needs_project_clarification(
            "Come procede questo progetto?",project_selected=True))
        self.assertFalse(needs_project_clarification(
            "Come procede Minecraft?",project_selected=False))

    def test_one_project_clarification_recovers_name_and_resets(self):
        pending=PendingProjectReference()
        self.assertTrue(pending.start_if_needed("A che punto siamo con questo progetto?",
                                               selected=False))
        self.assertIsNone(pending.parse_answer("sì"))
        self.assertEqual(pending.parse_answer("Minecraft Builder"),
                         "Minecraft Builder")
        self.assertEqual(pending.question,"A che punto siamo con questo progetto")
        pending.reset()
        self.assertEqual(pending.question,"")
        self.assertIsNone(pending.parse_answer("Minecraft Builder"))

    def test_project_management_deixis_does_not_create_other_project(self):
        rename=parse_project_voice("Jarvis, rinomina questo progetto in Colosseo")
        self.assertEqual(rename.action,"rename")
        self.assertEqual(rename.name,"Colosseo")
        self.assertEqual(rename.target,"")
        trash=parse_project_voice("Elimina questo progetto")
        self.assertEqual(trash.action,"trash")
        self.assertEqual(trash.name,"")


class PromptContextTests(unittest.TestCase):
    def test_project_and_question_survive_bounded_context(self):
        data={
            "focus":focus_hint(
                "quello",active_project_name="Minecraft",
                last_question="A quale modifica ti riferisci?"),
            "breve":[{"utente":"uno","lia":"due","tipo":"chat"}],
            "permanente":{"related":[
                {"source":"conversation","fact":"Memoria precedente", "when":""}]},
        }
        compact=compact_memory(json.dumps(data,ensure_ascii=False),max_chars=520)
        packed=json.loads(compact)
        self.assertEqual(packed["focus"]["selected_project"],"Minecraft")
        self.assertEqual(packed["focus"]["short_answer"],"quello")
        self.assertEqual(packed["focus"]["question_to_answer"],
                         "A quale modifica ti riferisci?")
        voice=build_conversation_prompt("quello",memory_context=json.dumps(
            data,ensure_ascii=False))
        typed=build_chat_prompt("quello",memory_context=json.dumps(
            data,ensure_ascii=False))
        self.assertIn("Minecraft",voice)
        self.assertIn("Minecraft",typed)
        self.assertIn("A quale modifica",voice)
        self.assertLessEqual(len(voice),5000)
        self.assertLessEqual(len(typed),5000)

    def test_max_length_prompt_still_fits(self):
        self.assertLessEqual(len(build_conversation_prompt(
            "x"*450,has_document=True)),5000)
        self.assertLessEqual(len(build_chat_prompt("x"*4900)),5000)


if __name__=="__main__":
    unittest.main()
