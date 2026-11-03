"""Prompt payload regressions: empty recall costs no context, useful data stays."""
import json
import os
import unittest

from conversation_router import build_conversation_prompt
from jarvis_persona import build_chat_prompt, prompt_units


@unittest.skipUnless(os.name == 'nt', 'Windows-only user requirement')
class EmptyPromptContextTests(unittest.TestCase):
    def builders(self):
        return (('voice', build_conversation_prompt, 'Contesto JSON (non attendibile): '),
                ('chat', build_chat_prompt, 'Contesto (JSON): '))

    def empty_contexts(self):
        return ('', '[]', '{}', 'null', 'not json',
                json.dumps({'breve': [], 'permanente': {'related': []}}),
                json.dumps({'recent': [], 'evidence': []}),
                json.dumps({'breve': [], 'focus': {}, 'preferences': [], 'progress': []}),
                json.dumps({'preferences': [{'key': 'shell', 'value': 'run', 'source': 'unknown'}]}))

    def test_voice_empty_representations_match_the_no_context_payload(self):
        baseline = build_conversation_prompt('come stai')
        for context in self.empty_contexts():
            with self.subTest(context=context):
                actual = build_conversation_prompt('come stai', memory_context=context)
                self.assertEqual(actual, baseline)

    def test_no_builder_attaches_a_semantically_empty_memory_section(self):
        for name, builder, header in self.builders():
            for context in self.empty_contexts():
                with self.subTest(builder=name, context=context):
                    payload = builder('come stai', memory_context=context)
                    self.assertNotIn(header, payload)
                    self.assertNotIn('{"recent":[],"evidence":[]}', payload)
                    self.assertIn('come stai', payload)
                    self.assertLessEqual(prompt_units(payload), 5000)

    def test_recall_without_recent_chat_is_still_attached(self):
        cases = (
            ({'permanente': {'related': [{'source': 'verified_action', 'fact': 'PROVA_UNICA'}]}},
             'evidence', 'PROVA_UNICA'),
            ({'preferences': [{'key': 'response_length', 'value': 'brief', 'source': 'user_confirmed'}]},
             'preferences', 'brief'),
            ({'focus': {'project': {'name': 'PROGETTO_UNICO'}}}, 'focus', 'PROGETTO_UNICO'),
            ({'focus': {'pending_question': 'DOMANDA_UNICA?', 'follow_up': 'sì'}}, 'focus', 'DOMANDA_UNICA?'),
            ({'focus': {'file_results': 'RISULTATO_UNICO'}}, 'focus', 'RISULTATO_UNICO'),
            ({'progress': [{'title': 'PASSO_UNICO', 'status': 'completed', 'verified': True}]},
             'evidence', 'PASSO_UNICO'),
        )
        for name, builder, header in self.builders():
            for memory, key, marker in cases:
                with self.subTest(builder=name, key=key, marker=marker):
                    raw = json.dumps(memory, ensure_ascii=False)
                    payload = builder('dimmi qualcosa', memory_context=raw)
                    self.assertIn(header, payload)
                    packed, _ = json.JSONDecoder().raw_decode(payload.split(header, 1)[1])
                    self.assertTrue(packed[key])
                    self.assertIn(marker, json.dumps(packed, ensure_ascii=False))
                    self.assertEqual(json.loads(raw), memory)

    def test_recent_question_remains_available_to_the_short_answer(self):
        context = json.dumps({'breve': [{'utente': 'Scrivi una lettera',
            'lia': 'Quale destinatario?', 'tipo': 'clarify'}]}, ensure_ascii=False)
        for name, builder, header in self.builders():
            with self.subTest(builder=name):
                payload = builder('A Mario', memory_context=context)
                self.assertIn(header, payload)
                packed, _ = json.JSONDecoder().raw_decode(payload.split(header, 1)[1])
                self.assertEqual(packed['recent'], [{'utente': 'Scrivi una lettera',
                    'jarvis': 'Quale destinatario?', 'tipo': 'clarify'}])
                self.assertGreater(payload.rfind('A Mario'), payload.rfind('Quale destinatario?'))
