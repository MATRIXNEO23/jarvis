"""Windows filesystem and actual Jarvis callbacks; controlled model replies only."""
import ast
import copy
import json
import os
from pathlib import Path
import queue
import sqlite3
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import test_file_access as file_access_tests
from test_activity_status import Value, GlobalCallbacks
from conversation_router import build_conversation_prompt, parse_conversation_intent, ConversationRejected
from dialogue_focus import is_ambiguous_short_reply
from local_engine import TaskResult
from local_model.chat_transport import ChatTransport
from voice_control import GPT_CONVERSATION, STANDBY, WakeWordGate
from live_capabilities import snapshot_capabilities, capability_status_prompt


@unittest.skipUnless(os.name == 'nt', 'Windows-only user requirement')
class FileRefinementTests(unittest.TestCase):
    setUp = file_access_tests.FileAccessTests.setUp

    @classmethod
    def setUpClass(cls):
        tree=ast.parse(Path('jarvis.py').read_text(encoding='utf-8'))
        cls.main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        cls.poll=next(n for n in cls.main.body if isinstance(n,ast.FunctionDef) and n.name=='poll')

    def callback(self,name,env):
        node=copy.deepcopy(next(n for n in self.main.body if isinstance(n,ast.FunctionDef) and n.name==name))
        node=GlobalCallbacks().visit(node)
        exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),name,'exec'),env)
        return env[name]

    def receive(self,kind,env):
        event=env['output_queue'].get_nowait()
        self.assertEqual(event[0],kind)
        branch=next(n for n in ast.walk(self.poll) if isinstance(n,ast.If)
                    and isinstance(n.test,ast.Compare) and isinstance(n.test.left,ast.Name)
                    and n.test.left.id=='kind' and isinstance(n.test.comparators[0],ast.Constant)
                    and n.test.comparators[0].value==kind)
        # Keep the actual poll's continue semantics, with one queued event.
        wrapper=ast.For(target=ast.Name(id='_event',ctx=ast.Store()),
                        iter=ast.Tuple(elts=[ast.Constant(1)],ctx=ast.Load()),
                        body=copy.deepcopy(branch.body),orelse=[])
        env['data']=list(event[1:])
        exec(compile(ast.fix_missing_locations(ast.Module(body=[wrapper],type_ignores=[])),
                     'real-poll-'+kind,'exec'),env)

    def environment(self):
        workers=[]
        def thread(*,target,**kwargs):
            return SimpleNamespace(start=lambda:workers.append(target))
        env=dict(busy_gpt=False,busy_local=False,closing=False,active_gpt=True,
            gpt_enabled=Value(True),gpt_request_action='',gpt_status=Value(''),
            addon_manager=self.manager,engine=self.engine,active_project_id=None,
            documents=SimpleNamespace(current=None),conversation_epoch=7,
            voice_mode=Value(GPT_CONVERSATION),GPT_CONVERSATION=GPT_CONVERSATION,STANDBY=STANDBY,
            speaker=SimpleNamespace(is_audible=lambda:False),speech_lexicon=None,
            memory_enabled=Value(True),last_voice_sample=Value(''),wake_gate=WakeWordGate(),
            refresh_buttons=Mock(),write_line=Mock(),speak_result=Mock(),
            remember_exchange=Mock(),remember_completed_action=Mock(),
            observed_local_result=lambda r:False,runtime_events=Mock(),
            request=Value(''),try_timer_command=lambda _:False,
            begin_project_work=lambda *a:None,finish_project_work=Mock(),
            project_local_ticket=None,local_operation_id=None,operation_ledger=Mock(),
            MemoryBoundaryError=RuntimeError,sqlite3=sqlite3,TaskResult=TaskResult,
            local_execution_lock=threading.Lock(),last_user_for_action='',
            threading=SimpleNamespace(Thread=thread),output_queue=queue.Queue(),service=Mock(),
            current_capability_snapshot=lambda _:dict(telegram_voice_send=False),
            capability_status_prompt=lambda _: 'File attivi; web non disponibile.',
            active_addon_actions=lambda:tuple(dict(id=a['id'],example=a['example'])
                                             for a in self.manager.active_actions()),
            build_conversation_prompt=build_conversation_prompt,
            parse_conversation_intent=parse_conversation_intent,ConversationRejected=ConversationRejected,
            is_ambiguous_short_reply=is_ambiguous_short_reply,announce_document=Mock(),root=None)
        env['chat_transport'] = ChatTransport(env['service'], native=None)
        for name in ('run_gpt','start_file_refinement','accept_file_refinement','submit_local','try_file_command','submit_gpt'):
            self.callback(name,env)
        return env,workers

    def empty(self,operation='search',**args):
        args=args or {'query':'nome pronunciato'}
        result=self.engine.execute_file(operation,args)
        self.assertEqual(result.status,'completed',result.message)
        token=result.file_listing['refinement']
        return token

    def response(self,env,token,operation='cerca',arguments=None,**override):
        reply=dict(kind='capability',action_id='addon.accesso_file.'+operation,
                   arguments=arguments or {'query':'preventivo'})
        reply.update(override)
        env['service'].call.return_value={'text':json.dumps(reply,ensure_ascii=False)}
        env['start_file_refinement'](token,'cerca file nome pronunciato')

    def test_precise_local_request_and_success_never_calls_model(self):
        for channel in ('voice','text'):
            with self.subTest(channel=channel):
                env,workers=self.environment()
                if channel=='voice':
                    env['output_queue'].put(('voice_text','Jarvis cerca file preventivo'))
                    self.receive('voice_text',env)
                else:
                    env['request'].set('cerca file preventivo')
                    env['submit_gpt']()
                workers.pop(0)()
                with patch('file_access.ui.show_results'):
                    self.receive('local',env)
                self.assertFalse(workers)
                env['service'].call.assert_not_called()
                self.assertEqual(len(self.files._results),1)
                self.assertTrue(os.path.samefile(self.a,self.files._results[0]))
                env['speak_result'].assert_not_called()

    def test_empty_to_actual_worker_model_and_local_result_without_clicks(self):
        env,workers=self.environment()
        env['service'].call.return_value={'text':json.dumps(dict(kind='capability',
            action_id='addon.accesso_file.cerca',arguments={'query':'preventivo'}))}
        env['try_file_command']('cerca file nome pronunciato')
        workers.pop(0)()
        with patch('file_access.ui.show_results'):
            self.receive('local',env)
        self.assertTrue(env['busy_gpt'])
        workers.pop(0)()
        self.receive('conversation_ok',env)
        workers.pop(0)()
        with patch('file_access.ui.show_results'):
            self.receive('local',env)
        self.assertEqual(env['service'].call.call_count,1)
        self.assertFalse(workers)
        self.assertEqual(len(self.files._results),1)
        self.assertTrue(os.path.samefile(self.a,self.files._results[0]))
        self.assertNotIn('file_refinement',env['service'].call.call_args.kwargs)
        env['speak_result'].assert_not_called()

    def test_second_empty_result_does_not_retry_or_claim_global_absence(self):
        token=self.empty()
        self.files.refinement_context(token,'cerca file nome pronunciato')
        result=self.engine.execute_file('search',{'query':'ancora assente'},token)
        self.assertEqual(result.file_listing['items'],())
        self.assertNotIn('refinement',result.file_listing)
        self.assertIn('ambito effettivamente',result.message)
        self.assertIsNone(self.files.refinement_context(token,'ripeti'))

    def test_search_scope_and_folder_read_constraints_cannot_change(self):
        token=self.empty('search',query='assente',scope=str(self.docs))
        self.files.refinement_context(token,'cerca file assente')
        with self.assertRaises(ValueError):
            self.files.refinement_arguments(token,'search',{'query':'preventivo','scope':str(self.root)})
        checked=self.files.refinement_arguments(token,'search',{'query':'preventivo'})
        self.assertEqual(checked['scope'],str(self.docs))
        token=self.empty('open',target='cartella inesistente',kind='folder')
        self.files.refinement_context(token,'apri cartella inesistente')
        result=self.engine.execute_file('open',{'target':str(self.a),'kind':'file'},token)
        self.assertEqual(result.status,'rejected')
        result=self.engine.execute_file('open',{'target':str(self.a)},token)
        self.assertEqual(result.status,'rejected')
        self.assertIn('non una cartella',result.message)

    def test_locate_clarification_retains_original_goal_in_followup_prompt(self):
        with patch('file_access.service.installed_locations',return_value=[]):
            token=self.empty('locate',query='Minecraft')
        env,workers=self.environment()
        live=snapshot_capabilities(settings={},has_document=False,telegram_credentials=False,
            telegram_voice_dependencies=False,registry=self.manager.registry,telethon_installed=False)
        status=capability_status_prompt(live)
        self.assertIn('telegram_vocale',status)
        self.assertLessEqual(len(status),850)
        env['capability_status_prompt']=lambda _:status
        self.response(env,token,kind='clarify',reply='Java oppure Bedrock?')
        # Only chat/clarify fields are permitted in the real protocol.
        env['service'].call.return_value={'text':json.dumps(dict(kind='clarify',reply='Java oppure Bedrock?'))}
        workers.pop(0)()
        self.receive('conversation_ok',env)
        self.assertTrue(env['try_file_command']('Bedrock'))
        workers.pop(0)()
        prompt=env['service'].call.call_args.kwargs['prompt']
        self.assertIn('Minecraft',prompt)
        self.assertIn('Bedrock',prompt)
        self.assertIn('Java oppure Bedrock',prompt)
        self.assertIn('"operation":"locate"',prompt)
        self.assertLessEqual(len(prompt),5000)
        self.assertIn('addon.accesso_file.localizza',prompt)

    def test_real_runtime_snapshot_empty_lookup_reaches_model_and_verified_result(self):
        env,workers=self.environment()
        live=snapshot_capabilities(settings={},has_document=False,telegram_credentials=False,
            telegram_voice_dependencies=False,registry=self.manager.registry,telethon_installed=False)
        env['capability_status_prompt']=lambda _:capability_status_prompt(live)
        env['service'].call.return_value={'text':json.dumps(dict(kind='capability',
            action_id='addon.accesso_file.cerca',arguments={'query':'preventivo'}))}
        env['try_file_command']('cerca file nome pronunciato')
        workers.pop(0)()
        with patch('file_access.ui.show_results'):
            self.receive('local',env)
        self.assertTrue(env['busy_gpt'],str(env['write_line'].call_args_list))
        workers.pop(0)()
        prompt=env['service'].call.call_args.kwargs['prompt']
        self.assertLessEqual(len(prompt.encode('utf-16-le'))//2,5000)
        self.assertIn('addon.accesso_file.cerca',prompt)
        self.receive('conversation_ok',env)
        workers.pop(0)()
        with patch('file_access.ui.show_results'):
            self.receive('local',env)
        self.assertEqual(env['service'].call.call_count,1)
        self.assertTrue(os.path.samefile(self.a,self.files._results[0]))
        self.assertFalse(workers)

    def test_missing_search_name_asks_then_searches_authorized_folder_without_gpt(self):
        self.engine.download_dir=self.root/'Downloads'
        self.engine.download_dir.mkdir()
        for channel in ('voice','text'):
            env,workers=self.environment()
            if channel=='voice':
                env['output_queue'].put(('voice_text','Jarvis cercami un file'))
                self.receive('voice_text',env)
            else:
                env['request'].set('cercami un file')
                env['submit_gpt']()
            workers.pop(0)()
            self.receive('local',env)
            self.assertIn('Quale file',str(env['write_line'].call_args_list))
            self.assertFalse(workers)
            env['try_file_command']('preventivo')
            workers.pop(0)()
            with patch('file_access.ui.show_results'):
                self.receive('local',env)
            self.assertTrue(os.path.samefile(self.a,self.files._results[0]))
            self.assertFalse(workers)
            env['service'].call.assert_not_called()
        help_text=self.engine.execute('aiuto').message
        self.assertIn('nelle cartelle autorizzate',help_text)
        self.assertNotIn('solo nella cartella Download',help_text)
        self.manager.set_enabled('accesso_file',False)
        self.assertIn('solo nella cartella Download',self.engine.execute('aiuto').message)

    def test_bare_search_browser_proposal_asks_scope_in_voice_and_text_poll(self):
        for channel in ('conversation','typed_conversation'):
            env,workers=self.environment()
            env['output_queue'].put(('conversation_ok',7,None,'cerca Netflix',
                {'text':json.dumps(dict(kind='capability',action_id='browser.search',
                    arguments={'query':'Netflix'}))},channel))
            with patch('webbrowser.open') as browser:
                self.receive('conversation_ok',env)
            browser.assert_not_called()
            self.assertFalse(workers)
            said=env['speak_result'].call_args.args[0]
            self.assertIn('PC',said)
            env['remember_exchange'].assert_called_once_with('cerca Netflix',said,'clarify')
            # The existing dialogue memory carries the original request and
            # question into the user's next natural-language clarification.
            history=json.dumps({'breve':[{'utente':'cerca Netflix','jarvis':said}]})
            live=snapshot_capabilities(settings={},has_document=False,telegram_credentials=False,
                telegram_voice_dependencies=False,registry=self.manager.registry,telethon_installed=False)
            prompt=build_conversation_prompt('sul PC',memory_context=history,
                runtime_info=capability_status_prompt(live),addon_actions=self.manager.active_actions())
            self.assertIn('Netflix',prompt)
            self.assertIn(said,prompt)
            self.assertIn('addon.accesso_file.localizza',prompt)
            self.assertLessEqual(len(prompt.encode('utf-16-le'))//2,5000)

    def test_model_cannot_turn_locate_into_open_search_or_browser(self):
        with patch('file_access.service.installed_locations',return_value=[]):
            token=self.empty('locate',query='Minecraft')
        env,workers=self.environment()
        env['start_file_refinement'](token,'trovami cartella installazione Minecraft')
        for aid,args in [('addon.accesso_file.cerca',{'query':'salvataggi'}),
                         ('addon.accesso_file.apri',{'target':str(self.docs)}),
                         ('browser.search',{'query':'Minecraft'})]:
            intent=parse_conversation_intent(json.dumps(dict(kind='capability',action_id=aid,arguments=args)),
                                              addon_resolver=self.manager.resolve)
            self.assertFalse(env['accept_file_refinement'](token,intent))
        self.assertEqual(len(workers),1)

    def test_nonexistent_and_revoked_paths_rejected_before_effect(self):
        for target in (str(self.root/'non-esiste'),str(self.hidden)):
            token=self.empty('open',target='cartella assente',kind='folder')
            self.files.refinement_context(token,'apri cartella assente')
            with patch('subprocess.Popen') as launch:
                result=self.engine.execute_file('open',{'target':target},token)
            self.assertEqual(result.status,'rejected')
            launch.assert_not_called()

    def test_replay_cancel_expiry_and_policy_change_never_execute(self):
        for mode in ('cancel','expiry','policy','replacement','disabled'):
            with self.subTest(mode=mode):
                self.manager.set_enabled('accesso_file',True)
                token=self.empty()
                self.files.refinement_context(token,'cerca file assente')
                if mode=='cancel': self.files.reset()
                elif mode=='expiry': self.files._expires=0
                elif mode=='policy': self.files.policy.configure([(self.docs,True),(self.hidden,False)])
                elif mode=='replacement': self.engine.execute_file('search',{'query':'preventivo'})
                else: self.manager.set_enabled('accesso_file',False)
                self.assertEqual(self.engine.execute_file('search',{'query':'preventivo'},token).status,'rejected')
        self.manager.set_enabled('accesso_file',True)
        token=self.empty()
        self.files.refinement_context(token,'cerca file assente')
        self.assertEqual(self.engine.execute_file('search',{'query':'preventivo'},token).status,'completed')
        self.assertEqual(self.engine.execute_file('search',{'query':'preventivo'},token).status,'rejected')

    def test_unavailable_timeout_and_stale_model_response_do_not_act(self):
        token=self.empty()
        env,workers=self.environment()
        env['active_gpt']=False
        self.assertFalse(env['start_file_refinement'](token,'cerca file assente'))
        self.assertFalse(workers)
        env['active_gpt']=True
        self.response(env,token)
        env['service'].call.side_effect=TimeoutError('Tempo GPT scaduto')
        workers.pop(0)()
        self.receive('conversation_error',env)
        self.assertFalse(env['busy_gpt'])
        self.assertIn('Tempo GPT scaduto',str(env['write_line'].call_args_list))
        token=self.empty()
        env,workers=self.environment()
        self.response(env,token)
        self.files.reset('altro-progetto')
        workers.pop(0)()
        self.receive('conversation_ok',env)
        self.assertFalse(workers)
        self.assertFalse(env['busy_local'])

    def test_read_failure_and_explorer_missing_child_do_not_ask_model(self):
        self.files.index=lambda *a: ([], 'Fallback controllato')
        with patch('file_access.service.os.scandir',side_effect=PermissionError('negato')):
            result=self.engine.execute_file('search',{'query':'assente'})
        self.assertNotIn('refinement',result.file_listing)
        view={'status':'ok','path':str(self.docs),'hwnd':123,'items':[]}
        with patch('file_access.service.explorer_view',return_value=view):
            result=self.engine.execute_file('open',{'target':'figlio assente','scope':'current'})
        self.assertEqual(result.status,'rejected')
        self.assertIsNone(result.file_listing)

    def test_partial_search_keeps_coverage_and_unrelated_request_revokes_model(self):
        self.files.max_entries=1
        token=self.empty('search',query='mai-presente')
        info=self.files.refinement_context(token,'cerca file mai-presente')
        self.assertTrue(info['partial'])
        env,_=self.environment()
        self.assertFalse(env['try_file_command']('perché parliamo di questa cartella?'))
        self.assertFalse(self.files.refinement_live(token))

    def test_invalid_reply_and_old_epoch_do_not_submit_an_action(self):
        for case in ('invalid','old_epoch'):
            with self.subTest(case=case):
                token=self.empty()
                env,workers=self.environment()
                self.response(env,token)
                if case=='invalid':
                    env['service'].call.return_value={'text':'not JSON'}
                workers.pop(0)()
                if case=='old_epoch':
                    env['conversation_epoch']+=1
                self.receive('conversation_ok',env)
                self.assertFalse(workers)
                self.assertFalse(env['busy_local'])

    def test_refined_folder_open_is_verified_once_and_replay_is_rejected(self):
        folder=self.docs/'NomeReale'; folder.mkdir()
        token=self.empty('open',target='nome pronunciato',kind='folder')
        env,workers=self.environment()
        self.response(env,token,operation='apri',arguments={'target':str(folder)})
        workers.pop(0)()
        self.receive('conversation_ok',env)
        with patch('subprocess.Popen') as launch:
            workers.pop(0)()
            self.receive('local',env)
            replay=self.engine.execute_file('open',{'target':str(folder)},token)
        self.assertEqual(launch.call_count,1)
        self.assertTrue(os.path.samefile(launch.call_args.args[0][1],folder))
        self.assertEqual(replay.status,'rejected')


if __name__=='__main__':
    unittest.main()

