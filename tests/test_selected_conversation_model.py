"""Regression: GPT selection must reach online routing, not local inference."""
import ast
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


@unittest.skipUnless(os.name == 'nt', 'Windows-only project requirement')
class SelectedConversationModelTests(unittest.TestCase):
    def test_voice_gpt_selection_does_not_start_gemma(self):
        tree = ast.parse(Path('jarvis.py').read_text(encoding='utf-8'))
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
        callback = next(n for n in main.body if isinstance(n, ast.FunctionDef)
                        and n.name == 'start_conversation_gpt')
        gemma = Mock(return_value=True)
        online = Mock(return_value=True)
        env = dict(closing=False, voice_mode=SimpleNamespace(get=lambda: 'conversation'),
                   GPT_CONVERSATION='conversation', CONTINUOUS='continuous',
                   gpt_enabled=SimpleNamespace(get=lambda: True), active_gpt=True,
                   busy_gpt=False, try_self_diagnostic=Mock(return_value=False),
                   submit_gemma_voice=gemma, run_gpt=online)
        exec(compile(ast.Module(body=[callback], type_ignores=[]), 'real-voice-router', 'exec'), env)
        env['start_conversation_gpt']('Parliamo della giornata')
        gemma.assert_not_called()
        online.assert_called_once()
