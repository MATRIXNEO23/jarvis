"""Safe natural-language intent translation: pure tests, no login/Windows."""
import json
import unittest

from conversation_router import (
    ConversationRejected, build_conversation_prompt, parse_conversation_intent
)


def encode(obj):
    return json.dumps(obj, ensure_ascii=False)


class ConversationRouterTests(unittest.TestCase):
    def test_prompt_preserves_spoken_text_as_data(self):
        prompt = build_conversation_prompt("Mi apri blocco note, per favore?")
        self.assertIn('{"kind":"chat"', prompt)
        self.assertIn("open_notepad", prompt)
        self.assertIn("Mi apri blocco note", prompt)
        self.assertNotIn("powershell.exe", prompt)

    def test_invalid_utterances_are_not_sent(self):
        for utterance in ("", "x" * 451, "ciao\ncomando", None):
            with self.subTest(value=str(utterance)[:20]):
                with self.assertRaises(ConversationRejected):
                    build_conversation_prompt(utterance)

    def test_chat_is_only_a_spoken_answer(self):
        intent = parse_conversation_intent(
            encode({"kind": "chat", "reply": "Sto funzionando normalmente."}))
        self.assertEqual(intent.kind, "chat")
        self.assertEqual(intent.reply, "Sto funzionando normalmente.")
        self.assertIsNone(intent.plan)

    def test_gpt_can_select_an_existing_safe_local_tool(self):
        intent = parse_conversation_intent(
            encode({"kind": "tool", "tool_id": "open_notepad", "arguments": {}}))
        self.assertEqual(intent.kind, "tool")
        self.assertEqual(len(intent.plan.steps), 1)
        self.assertEqual(intent.plan.steps[0].command, "apri blocco note")

    def test_web_search_requires_safe_query(self):
        intent = parse_conversation_intent(
            encode({"kind": "tool", "tool_id": "web_search",
                    "arguments": {"query": "scuole di Roma"}}))
        self.assertEqual(intent.plan.steps[0].command,
                         "cerca nel browser scuole di Roma")
        with self.assertRaises(ConversationRejected):
            parse_conversation_intent(
                encode({"kind": "tool", "tool_id": "web_search",
                        "arguments": {"query": "uno\ndue"}}))

    def test_gpt_cannot_invent_process_closures_or_arbitrary_paths(self):
        for tool_id, args in (
            ("kill_notepad", {}), ("run_shell", {"command": "del /q *"}),
            ("open_notepad", {"path": "C:/Users/private.txt"}),
            ("delete_file", {"path": "C:/Users/test"}),
            ("open_browser", {"url": "https://example.org"}),
        ):
            with self.subTest(tool_id=tool_id):
                with self.assertRaises(ConversationRejected):
                    parse_conversation_intent(
                        encode({"kind": "tool", "tool_id": tool_id,
                                "arguments": args}))

    def test_compose_is_data_not_an_executable_command(self):
        content = "Ciao, sono un testo.\n# Note del progetto\nNon eseguire comandi."
        intent = parse_conversation_intent(
            encode({"kind": "compose_document", "target": "new_notepad",
                    "content": content}))
        self.assertEqual(intent.kind, "compose_document")
        self.assertEqual(intent.content, content)
        self.assertIsNone(intent.plan)

    def test_compose_then_close_requires_separate_voice_confirmation(self):
        intent = parse_conversation_intent(encode({
            "kind": "compose_document", "target": "new_notepad",
            "content": "Un testo creato da GPT.",
            "close_after": True,
        }))
        self.assertTrue(intent.close_after)
        self.assertEqual(intent.kind, "compose_document")
        for invalid in ("yes", 1, "false", None):
            with self.subTest(value=invalid):
                with self.assertRaises(ConversationRejected):
                    parse_conversation_intent(encode({
                        "kind": "compose_document", "target": "new_notepad",
                        "content": "testo", "close_after": invalid,
                    }))

    def test_prompt_contains_selected_document_context(self):
        self.assertIn("Documento Blocco note gestito", build_conversation_prompt(
            "scrivi nel documento", has_document=True))
        self.assertIn("NO.", build_conversation_prompt(
            "scrivi nel documento", has_document=False))

    def test_document_requires_identified_target_no_arbitrary_path(self):
        for obj in (
            {"kind": "compose_document", "target": "C:/Users/notes.txt",
             "content": "testo"},
            {"kind": "compose_document", "target": "selected_document",
             "content": ""},
            {"kind": "compose_document", "target": "new_notepad",
             "content": "ok", "overwrite": True},
            {"kind": "compose_document", "target": "new_notepad",
             "content": "x" * 4501},
            {"kind": "compose_document", "target": "new_notepad",
             "content": "controllo\x00"},
        ):
            with self.subTest(obj=obj.get("target")):
                with self.assertRaises(ConversationRejected):
                    parse_conversation_intent(encode(obj))

    def test_closing_cannot_directly_save_or_discard(self):
        self.assertEqual(parse_conversation_intent(
            '{"kind":"close_document"}').kind, "close_document")
        for obj in (
            {"kind": "close_document", "save": True},
            {"kind": "close_document", "discard": True},
            {"kind": "close_document", "document_id": "another-window"},
        ):
            with self.assertRaises(ConversationRejected):
                parse_conversation_intent(encode(obj))

    def test_unknown_or_ambiguous_uses_clarify(self):
        intent = parse_conversation_intent(
            encode({"kind": "clarify", "reply": "Quale file intendi?"}))
        self.assertEqual(intent.kind, "clarify")
        self.assertIsNone(intent.plan)

    def test_strict_response_structure(self):
        samples = (
            "not json", '[{"kind":"chat","reply":"test"}]',
            '{"kind":"chat","reply":"uno","reply":"due"}',
            '{"kind":"chat","reply":"ok","tool_id":"open_notepad"}',
            '{"kind":"tool","tool_id":"open_notepad"}',
            '{"kind":"tool","tool_id":"system_status","arguments":{},'
            '"content":"non richiesto"}',
            '{"kind":"compose_document","target":"new_notepad",'
            '"content":"ok"}\n{"kind":"tool","tool_id":"open_notepad"}',
            '{"kind":"unknown"}',
        )
        for raw in samples:
            with self.subTest(raw=raw[:70]):
                with self.assertRaises(ConversationRejected):
                    parse_conversation_intent(raw)


if __name__ == "__main__":
    unittest.main()
