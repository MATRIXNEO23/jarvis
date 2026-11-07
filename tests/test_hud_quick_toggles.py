"""Windows native Tk quick controls using real application setting callbacks.

Files and SecondBrain SQLite are temporary and real. GPT transport, microphone
hardware and thread scheduling are controlled: no account or live audio.
"""
import ast
import copy
import os
from pathlib import Path
import sqlite3
import tempfile
import threading
from types import SimpleNamespace
import unittest

from test_activity_status import GlobalCallbacks


@unittest.skipUnless(os.name == 'nt', 'Windows-only user requirement')
class HeaderQuickControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = next(n for n in ast.parse(Path('jarvis.py').read_text(encoding='utf-8')).body
                        if isinstance(n, ast.FunctionDef) and n.name == 'main')

    def setUp(self):
        import tkinter as tk
        from animated_hud import JarvisHUD
        self.tk = tk
        self.root = tk.Tk()
        self.root.withdraw()
        self.hud = JarvisHUD(self.root, lambda: None)
        self.temp = tempfile.TemporaryDirectory(prefix='jarvis-header-')
        self.addCleanup(self.temp.cleanup)
        self.stream = False
        self.requests, self.modes, self.errors, self.stops = [], [], [], []

    def tearDown(self):
        self.hud.close()
        self.root.update_idletasks()
        self.root.destroy()

    def callback(self, name, env):
        node = copy.deepcopy(next(n for n in self.main.body
            if isinstance(n, ast.FunctionDef) and n.name == name))
        node = GlobalCallbacks().visit(node)
        exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                     'real-' + name, 'exec'), env)
        return env[name]

    def wire(self):
        for name in ('mic_toggle_button', 'gpt_toggle_button', 'memory_toggle_button'):
            self.assertIsInstance(getattr(self.hud, name, None), self.tk.Button,
                                  'The header must provide a usable ' + name)
        from tkinter import ttk
        from settings import load_settings, save_settings
        from second_brain import SecondBrain
        from adaptive_voice import SpeechCorrections, SpeechCorrectionError
        from voice_control import STANDBY, GPT_CONVERSATION, PUSH_TO_TALK
        from conversation_memory import ConversationMemory
        folder = Path(self.temp.name)
        self.settings_path = folder / 'settings.json'
        settings = load_settings(self.settings_path)
        settings.update(gpt_enabled=True, memory_enabled=True)
        save_settings(settings, self.settings_path)
        self.brain_path = folder / 'brain.sqlite3'
        brain = SecondBrain(self.brain_path)
        brain.remember_turn('Un ricordo da conservare', 'Il dato resta nel profilo')
        memory = ConversationMemory()
        memory.remember('Stiamo parlando di una cartella', 'Vuoi elencarla?', 'clarify')
        env = dict(root=self.root, hud=self.hud, settings=settings,
            gpt_enabled=self.tk.BooleanVar(value=True), active_gpt=True,
            memory_enabled=self.tk.BooleanVar(value=True),
            voice_mode=self.tk.StringVar(value=GPT_CONVERSATION),
            STANDBY=STANDBY, GPT_CONVERSATION=GPT_CONVERSATION, PUSH_TO_TALK=PUSH_TO_TALK,
            gpt_status=self.tk.StringVar(), memory_status=self.tk.StringVar(),
            conversation_epoch=3, pending_conversation={}, conversation_memory=memory,
            doc_dialog=SimpleNamespace(revoke_pending=lambda: None),
            planner_abort_event=threading.Event(), telegram_gpt_ready=threading.Event(),
            telegram_gpt_session_token=None,
            telegram_gpt_session_choice=self.tk.BooleanVar(value=False),
            refresh_buttons=lambda: None,
            run_gpt=lambda action: self.requests.append(action),
            service=SimpleNamespace(stop=lambda: self.stops.append('stop')),
            threading=SimpleNamespace(Thread=lambda *, target, **kw: SimpleNamespace(start=target)),
            save_settings=lambda data: save_settings(data, self.settings_path),
            messagebox=SimpleNamespace(showerror=lambda *a, **kw: self.errors.append(a)),
            durable_brain=brain, speech_lexicon=SpeechCorrections(brain.path),
            SecondBrain=lambda: SecondBrain(self.brain_path),
            SpeechCorrections=SpeechCorrections, SpeechCorrectionError=SpeechCorrectionError,
            sqlite3=sqlite3, change_voice_mode=lambda: self.modes.append(env['voice_mode'].get()),
            speaker=SimpleNamespace(is_speaking=lambda: False),
            voice=SimpleNamespace(is_user_speaking=lambda: False, is_listening=lambda: self.stream),
            busy_gpt=False, busy_local=False, document_busy=False, gpt_request_action='',
            gemma_session=[None], gemma_trial_busy=[False],
            engine=SimpleNamespace(file_access=None), orbit_nodes_cache=())
        env["telegram_gpt_ready"].set()
        for name in ('memory_status_refresh', 'set_telegram_gpt_session', 'toggle_gpt', 'toggle_memory', 'toggle_hud_microphone'):
            self.callback(name, env)
        env['gpt_toggle'] = ttk.Checkbutton(self.root, variable=env['gpt_enabled'],
                                          command=env['toggle_gpt'])
        env['memory_toggle'] = ttk.Checkbutton(self.root, variable=env['memory_enabled'],
                                             command=env['toggle_memory'])
        env['hud_mic_button'] = self.tk.Button(self.root, command=env['toggle_hud_microphone'])
        for method in ('set_quick_toggle_handlers', 'set_state_provider'):
            call = next(n for n in self.main.body if isinstance(n, ast.Expr)
                and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute)
                and isinstance(n.value.func.value, ast.Name)
                and n.value.func.value.id == 'hud' and n.value.func.attr == method)
            exec(compile(ast.fix_missing_locations(ast.Module(body=[copy.deepcopy(call)],
                type_ignores=[])), 'real-hud-binding-' + method, 'exec'), env)
        self.env = env
        return env

    def refresh(self):
        self.hud._advance()
        self.root.update_idletasks()

    def test_header_clicks_change_settings_once_and_keep_saved_memories(self):
        env = self.wire()
        from second_brain import SecondBrain
        from settings import load_settings
        before = SecondBrain(self.brain_path).stats()
        for button in (self.hud.mic_toggle_button, self.hud.gpt_toggle_button,
                       self.hud.memory_toggle_button):
            button.invoke()
        self.refresh()
        self.assertEqual(env['voice_mode'].get(), env['STANDBY'])
        self.assertFalse(env['gpt_enabled'].get())
        self.assertFalse(env['active_gpt'])
        self.assertFalse(env["telegram_gpt_ready"].is_set())
        self.assertFalse(env['memory_enabled'].get())
        self.assertEqual(self.stops, ['stop'])
        self.assertEqual(self.modes, [env['STANDBY']])
        saved = load_settings(self.settings_path)
        self.assertFalse(saved['gpt_enabled'])
        self.assertFalse(saved['memory_enabled'])
        self.assertEqual(SecondBrain(self.brain_path).stats(), before)
        self.assertEqual(len(env['conversation_memory']), 1)
        self.assertIn('OFF', self.hud.mic_toggle_button.cget('text'))
        self.assertIn('OFF', self.hud.gpt_toggle_button.cget('text'))
        self.assertIn('OFF', self.hud.memory_toggle_button.cget('text'))
        for button in (self.hud.mic_toggle_button, self.hud.gpt_toggle_button,
                       self.hud.memory_toggle_button):
            button.invoke()
        self.refresh()
        self.assertEqual(env['voice_mode'].get(), env['GPT_CONVERSATION'])
        self.assertTrue(env['gpt_enabled'].get())
        self.assertTrue(env['memory_enabled'].get())
        self.assertEqual(self.requests, ['status'])
        self.assertEqual(SecondBrain(self.brain_path).stats(), before)

    def test_settings_and_header_share_state_without_false_live_status(self):
        env = self.wire()
        env['active_gpt'] = False
        env['voice_mode'].set(env['PUSH_TO_TALK'])
        self.refresh()
        self.assertIn('NON CONNESSO', self.hud.gpt_toggle_button.cget('text'))
        self.assertIn('PTT', self.hud.mic_toggle_button.cget('text'))
        env['gpt_toggle'].invoke()
        env['memory_toggle'].invoke()
        self.refresh()
        self.assertIn('OFF', self.hud.gpt_toggle_button.cget('text'))
        self.assertIn('OFF', self.hud.memory_toggle_button.cget('text'))
        env['voice_mode'].set(env['GPT_CONVERSATION'])
        self.refresh()
        self.assertIn('NON ATTIVO', self.hud.mic_toggle_button.cget('text'))
        self.stream = True
        env['active_gpt'] = True
        env['gpt_enabled'].set(True)
        self.refresh()
        self.assertEqual(self.hud.mic_toggle_button.cget('text'), 'MIC ATTIVO')
        self.assertEqual(self.hud.gpt_toggle_button.cget('text'), 'GPT ON')

    def test_save_failure_restores_setting_and_header(self):
        env = self.wire()
        def fail_save(_data):
            raise OSError('controlled disk failure')
        env['save_settings'] = fail_save
        self.hud.gpt_toggle_button.invoke()
        self.hud.memory_toggle_button.invoke()
        self.refresh()
        self.assertTrue(env['gpt_enabled'].get())
        self.assertTrue(env['memory_enabled'].get())
        self.assertTrue(env['settings']['gpt_enabled'])
        self.assertTrue(env['settings']['memory_enabled'])
        self.assertTrue(env['active_gpt'])
        self.assertEqual(self.hud.gpt_toggle_button.cget('text'), 'GPT ON')
        self.assertEqual(self.hud.memory_toggle_button.cget('text'), 'MEMORIA ON')
        self.assertFalse(self.stops)
        self.assertFalse(self.requests)
        self.assertTrue(self.errors)


if __name__ == '__main__':
    unittest.main()
