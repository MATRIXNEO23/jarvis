import os
import unittest
from unittest.mock import Mock
import test_typed_timer_routing as timer_fixture

@unittest.skipUnless(os.name=='nt','Windows only')
class LocalHelpTests(unittest.TestCase):
    def test_help_is_local_even_with_gemma_and_pending_document(self):
        harness=timer_fixture.TypedTimerTests();self.addCleanup(harness.doCleanups)
        for word in ('aiuto','help','comandi','cosa puoi fare'):
            e=harness.environment(word)
            e['doc_dialog'].phase='awaiting_close'
            e['handle_document_confirmation']=Mock()
            e['show_help']=Mock()
            e['send_console_input']()
            e['show_help'].assert_called_once_with()
            e['submit_gemma_trial'].assert_not_called()
            e['handle_document_confirmation'].assert_not_called()
            self.assertEqual(e['request'].value,'')

    def ui(self):
        import gc
        import tempfile
        from pathlib import Path
        import tkinter as tk
        from local_engine import LocalEngine
        folder=Path(self.enterContext(tempfile.TemporaryDirectory(prefix='local-help-')))
        root=tk.Tk();root.geometry('250x90')
        engine=LocalEngine(download_dir=folder/'Downloads',db_path=folder/'tasks.db',windows=False)
        def cleanup():
            root.destroy()
            gc.collect()
        self.addCleanup(cleanup)
        return root,engine

    def test_real_help_is_read_only_reused_and_reopens_after_close(self):
        from local_help import open_help
        root,engine=self.ui()
        first=open_help(root,engine);root.update()
        self.assertIn('Timer e sveglia',first.pages)
        self.assertIn('stato sistema',first.pages['Comandi locali'].get('1.0','end'))
        self.assertTrue(all(text.cget('state')=='disabled' for text in first.pages.values()))
        self.assertIs(open_help(root,engine),first)
        first.close();root.update()
        self.assertIsNone(root._jarvis_help_window)
        second=open_help(root,engine);root.update()
        self.assertIsNot(second,first)
        self.assertTrue(second.winfo_exists())

    def test_help_refreshes_existing_file_and_application_catalogs(self):
        from types import SimpleNamespace
        from local_help import open_help
        root,engine=self.ui()
        engine.file_access=SimpleNamespace(available=lambda:True,commands=lambda:'Cartella consentita: Prova')
        engine.program_apps=SimpleNamespace(commands=lambda:'Applicazione autorizzata: Calcolatrice')
        window=open_help(root,engine);root.update()
        self.assertIn('cartelle autorizzate',window.pages['Comandi locali'].get('1.0','end'))
        self.assertIn('Calcolatrice',window.pages['File e app'].get('1.0','end'))
        engine.file_access.available=lambda:False
        engine.file_access.commands=lambda:'Accesso disattivato'
        engine.program_apps.commands=lambda:''
        self.assertIs(open_help(root,engine),window)
        self.assertIn('solo nella cartella Download',window.pages['Comandi locali'].get('1.0','end'))
        self.assertNotIn('Calcolatrice',window.pages['File e app'].get('1.0','end'))

    def test_real_keyboard_shortcuts_open_help_focus_chat_and_close_only_help(self):
        import ast
        import tkinter as tk
        from pathlib import Path
        from local_help import bind_help_shortcuts
        root,engine=self.ui();settings=tk.Toplevel(root);settings.withdraw()
        entry=tk.Entry(root);entry.pack()
        main=next(n for n in ast.parse(Path('jarvis.py').read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name=='main')
        callbacks=[n for n in main.body if isinstance(n,ast.FunctionDef) and n.name in ('show_help','focus_command_box')]
        self.assertEqual(len(callbacks),2)
        env=dict(root=root,engine=engine,input_box=entry)
        exec(compile(ast.Module(body=callbacks,type_ignores=[]),'real-help-keyboard','exec'),env)
        bind_help_shortcuts(root,settings,env['show_help'],env['focus_command_box'])
        root.update();root.focus_force();root.update();root.event_generate('<F1>');root.update()
        window=root._jarvis_help_window
        self.assertTrue(window.winfo_exists())
        window.focus_force();root.update();window.event_generate('<Escape>');root.update()
        self.assertIsNone(root._jarvis_help_window)
        root.focus_force();root.update();root.event_generate('<Control-l>');root.update()
        self.assertIs(root.focus_get(),entry)
        self.assertTrue(root.winfo_exists())
