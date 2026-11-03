"""Real console/voice shared callback and model gateway; transport controlled."""
import ast
import copy
import json
import os
from pathlib import Path
from types import SimpleNamespace
import unittest

from test_program_apps_service import ProgramServiceTests
from test_activity_status import GlobalCallbacks


@unittest.skipUnless(os.name=='nt','Windows-only user requirement')
class ProgramIntegrationTests(unittest.TestCase):
    setUp=ProgramServiceTests.setUp
    add=ProgramServiceTests.add
    save=ProgramServiceTests.save

    def environment(self):
        tree=ast.parse(Path('jarvis.py').read_text(encoding='utf-8'))
        main=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='main')
        self.received=[]
        self.spoken=[]
        request=SimpleNamespace(value='',get=lambda:request.value,set=lambda value:setattr(request,'value',value))
        def submit(**kwargs):
            self.assertEqual(kwargs['addon_action_id'],'addon.programmi_app.avvia')
            self.assertTrue(self.manager.is_active(kwargs['addon_action_id']))
            self.received.append(self.engine.execute_program(*kwargs['program_call']))
        env=dict(engine=self.engine,addon_manager=self.manager,save_only_waiting=False,
            document_busy=False,doc_dialog=SimpleNamespace(phase='idle'),
            pending_project_name=False,pending_project_rename_id=None,pending_project_trash_id=None,
            active_project_id=None,busy_local=False,write_line=lambda text:None,submit_local=submit,
            request=request,reconcile_document_session=lambda **kw:None,
            try_telegram_voice_send=lambda text:False,parse_simple_save=lambda text:None)
        for name in ('try_program_command','try_file_command','send_console_input'):
            node=copy.deepcopy(next(n for n in main.body if isinstance(n,ast.FunctionDef) and n.name==name))
            node=GlobalCallbacks().visit(node)
            exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),
                         'real-app-callback','exec'),env)
        return main,env

    def test_console_and_transcribed_voice_use_actual_shared_callback_without_model(self):
        main,env=self.environment()
        env['request'].set('puoi avviare la posta?')
        env['send_console_input']()
        self.assertEqual(env['request'].get(),'')
        self.assertTrue(env['try_file_command']('lancia il mio gioco'))
        self.assertEqual(self.launched,[self.mail,self.game])
        self.assertEqual(len(self.received),2)

    def test_pending_program_choice_keeps_context_through_shared_callback(self):
        second=self.add('Posta alternativa');self.save({self.mail:'',second:''})
        main,env=self.environment()
        self.assertTrue(env['try_file_command']('apri Posta'))
        self.assertIsNotNone(self.received[-1].program_listing)
        self.assertIn('Posta',self.apps.context_hint())
        self.assertTrue(env['try_file_command']('Posta alternativa'))
        self.assertEqual(self.launched,[second])

    def test_document_decision_and_project_dialog_have_priority(self):
        main,env=self.environment()
        for key,value in [('save_only_waiting',True),('document_busy',True),('pending_project_name',True)]:
            env[key]=value
            self.assertFalse(env['try_program_command']('apri la posta'))
            env[key]=False
        env['doc_dialog'].phase='awaiting_close'
        self.assertFalse(env['try_program_command']('apri la posta'))
        self.assertFalse(self.launched)

    def test_model_fallback_uses_actual_router_manager_and_dispatch_branch(self):
        from conversation_router import build_conversation_prompt,parse_conversation_intent
        from jarvis_persona import prompt_units
        main,env=self.environment()
        phrase='fammi partire la posta'
        prompt=build_conversation_prompt(phrase,addon_actions=self.manager.active_actions())
        self.assertLessEqual(prompt_units(prompt),5000)
        self.assertIn('arguments.query',prompt)
        intent=parse_conversation_intent(json.dumps(dict(kind='capability',action_id='addon.programmi_app.avvia',
            arguments={'query':'posta'})),addon_resolver=self.manager.resolve,utterance=phrase)
        branch=next(n for n in ast.walk(main) if isinstance(n,ast.If)
                    and isinstance(n.test,ast.Compare) and isinstance(n.test.left,ast.Attribute)
                    and n.test.left.attr=='handler' and any(isinstance(c,ast.Constant) and c.value=='program_apps' for c in n.test.comparators))
        code=compile(ast.fix_missing_locations(ast.Module(body=copy.deepcopy(branch.body),type_ignores=[])),
                     'real-model-app-dispatch','exec')
        env.update(cap=intent.capability,original_phrase=phrase,speak_result=self.spoken.append)
        exec(code,env)
        self.assertEqual(self.launched,[self.mail])
        env['original_phrase']='non aprire la posta'
        exec(code,env)
        self.assertEqual(self.launched,[self.mail])
        self.assertTrue(self.spoken)
        with self.assertRaises(ValueError):
            parse_conversation_intent(json.dumps(dict(kind='capability',action_id='addon.programmi_app.avvia',
                arguments={'query':'posta','target':'cmd.exe'})),addon_resolver=self.manager.resolve)
