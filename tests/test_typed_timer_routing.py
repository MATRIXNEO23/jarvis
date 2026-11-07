"""Real console/timer callbacks; no model, microphone or user profiles."""
import ast
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from jarvis_timer import parse_timer_command
from sveglia.service import parse_command, next_alarm
from datetime import datetime

@unittest.skipUnless(os.name == 'nt', 'Windows-only project')
class TypedTimerTests(unittest.TestCase):
    def environment(self, text):
        main = next(n for n in ast.parse(Path('jarvis.py').read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name=='main')
        nodes=[n for n in main.body if isinstance(n,ast.FunctionDef) and n.name in ('try_timer_command','send_console_input')]
        request=SimpleNamespace(value=text)
        request.get=lambda:request.value
        request.set=lambda v:setattr(request,'value',v)
        env=dict(request=request,reconcile_document_session=Mock(),try_telegram_voice_send=lambda _:False,
            save_only_waiting=False,doc_dialog=SimpleNamespace(phase='idle'),parse_simple_save=lambda _:None,
            pending_project_name=False,pending_project_rename_id=None,pending_project_trash_id=None,
            try_file_command=lambda _:False,project_voice_command=lambda _:False,preference_command=lambda _:False,
            handle_project_reference=lambda _:False,handle_unanchored_short_reply=lambda _:False,
            try_self_diagnostic=lambda _:False,maybe_queue_telegram_note=lambda _:False,
            parse_alarm_clock_command=parse_command,parse_timer_command=parse_timer_command,
            timer=Mock(),alarm=Mock(),write_line=Mock(),speak_result=Mock(),
            submit_gemma_trial=Mock(),gpt_enabled=SimpleNamespace(get=lambda:False),active_gpt=False,submit_local=Mock())
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'actual-console-timer','exec'),env)
        return env

    def test_typed_timer_starts_once_without_gemma_or_generic_fallback(self):
        for text in ('imposta timer 6 minuti','imposta timer sei minuti','avvia un timer da sei minuti'):
            with self.subTest(text=text):
                e=self.environment(text);e['send_console_input']()
                e['timer'].start.assert_called_once_with(360)
                e['submit_gemma_trial'].assert_not_called();e['submit_local'].assert_not_called()
                self.assertEqual(e['request'].value,'')

    def test_spoken_duration_and_existing_controls(self):
        for text,seconds in [('timer sei minuti',360),('timer un minuto',60),('timer due ore e trenta minuti',9000)]:
            self.assertEqual(parse_timer_command(text).seconds,seconds)
        self.assertIsNone(parse_timer_command('timer -sei minuti'))
        self.assertEqual(parse_timer_command('pausa timer').action,'pause')
        self.assertEqual(parse_timer_command('timer').action,'open')

    def test_alarm_morning_words_resolve_without_model(self):
        e=self.environment('metti sveglia alle sette e trenta di mattina');e['send_console_input']()
        e['alarm'].arm.assert_called_once_with('sette e trenta di mattina')
        self.assertEqual(next_alarm('sette e trenta di mattina',datetime(2026,11,7,6)),datetime(2026,11,7,7,30))
        e['submit_gemma_trial'].assert_not_called()
