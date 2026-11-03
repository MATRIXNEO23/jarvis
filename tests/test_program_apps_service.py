"""Real profiles, manager, engine and language; native launch alone controlled."""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch


@unittest.skipUnless(os.name=='nt','Windows-only user requirement')
class ProgramServiceTests(unittest.TestCase):
    def setUp(self):
        from addon_manager import AddonManager
        from live_capabilities import LiveCapabilityRegistry
        from local_engine import LocalEngine
        self.temp=tempfile.TemporaryDirectory(prefix='jarvis-apps-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.manager=AddonManager(LiveCapabilityRegistry(),self.root/'addons')
        self.manager.install(Path('program_apps/ProgrammiApp.jaddon'))
        self.manager.set_enabled('programmi_app',True)
        self.apps=self.manager.program_service
        self.launched=[]
        self.apps.launcher=lambda app:self.launched.append(app.id) or 'Richiesta accettata.'
        self.engine=LocalEngine(db_path=self.root/'tasks.db')
        self.engine.program_apps=self.apps
        self.mail=self.add('Posta µ')
        self.game=self.add('Gioco difficile')
        self.save({self.mail:'apri la posta',self.game:'avvia il mio gioco'})

    def add(self,name):
        file=self.root/(name+'.exe')
        shutil.copyfile(sys.executable,file)
        return self.apps.add_manual(file)

    def save(self, phrases, enabled=True):
        self.apps.save_preferences({key:dict(enabled=enabled,phrase=value) for key,value in phrases.items()})

    def test_variants_and_custom_phrase_share_local_identity_and_persist(self):
        for phrase in ['apri la posta','avvia la posta','Lancia la posta!','puoi aprire la posta?',
                       'avvia Posta µ','apri il mio gioco','lancia il mio gioco']:
            result=self.engine.execute(phrase)
            self.assertEqual(result.status,'completed',result.message)
        self.assertEqual(self.launched,[self.mail]*5+[self.game]*2)
        from program_apps.service import ProgramService
        restored=ProgramService(self.apps.folder,lambda:True,launcher=self.apps.launcher)
        self.assertEqual(restored.parse_command('avvia la posta'),('launch',{'query':'posta'}))
        self.assertIn('apri la posta',restored.commands())

    def test_negations_questions_and_reserved_document_commands_never_launch_app(self):
        for phrase in ['non aprire la posta','evita di avviare la posta','come aprire la posta?',
                       'Netflix funziona?','apri cartella posta','apri blocco note']:
            self.assertIsNone(self.apps.parse_command(phrase))
        self.assertFalse(self.launched)
        for phrase in ['apri blocco note','avvia calcolatrice','non avviare Netflix',
                       'attiva dettatura','disattiva dettatura','manda un messaggio a Mario',
                       'salva','salva e chiudi','scarta le modifiche']:
            with self.assertRaises(ValueError):
                self.save({self.mail:phrase})

    def test_conflicting_alias_or_existing_name_is_rejected_without_losing_saved_preferences(self):
        before=self.apps.path.read_bytes()
        for phrases in [{self.mail:'apri la posta',self.game:'avvia la posta'},
                        {self.mail:'avvia Gioco difficile'}]:
            with self.assertRaises(ValueError):
                self.save(phrases)
            self.assertEqual(self.apps.path.read_bytes(),before)
        self.assertEqual(self.engine.execute('avvia la posta').status,'completed')

    def test_failed_atomic_save_preserves_disk_memory_and_permissions(self):
        before=self.apps.path.read_bytes()
        with patch('program_apps.service.os.replace',side_effect=OSError('disk unavailable')):
            with self.assertRaises(OSError):
                self.save({self.mail:''},enabled=False)
        self.assertEqual(self.apps.path.read_bytes(),before)
        self.assertEqual(self.engine.execute('apri la posta').status,'completed')

    def test_pending_name_number_consumes_once_revocation_and_expiry(self):
        second=self.add('Posta alternativa')
        self.save({self.mail:'',second:''})
        result=self.engine.execute('avvia Posta')
        self.assertTrue(result.program_listing)
        token=result.program_listing['token']
        self.assertFalse(self.launched)
        chosen=self.engine.execute_program('select',{'query':'2','token':token})
        self.assertEqual(chosen.status,'completed',chosen.message)
        self.assertEqual(len(self.launched),1)
        self.assertEqual(self.engine.execute_program('select',{'query':'2','token':token}).status,'rejected')
        token=self.engine.execute('avvia Posta').program_listing['token']
        self.save({self.mail:'',second:''},enabled=False)
        self.assertEqual(self.engine.execute_program('select',{'query':'1','token':token}).status,'rejected')
        self.save({self.mail:'',second:''})
        self.apps.clock=lambda:0
        token=self.engine.execute('avvia Posta').program_listing['token']
        self.apps.clock=lambda:121
        self.assertEqual(self.engine.execute_program('select',{'query':'1','token':token}).status,'rejected')

    def test_addon_disabled_and_permission_revoked_before_execution_block(self):
        parsed=self.apps.parse_command('apri la posta')
        self.manager.set_enabled('programmi_app',False)
        self.assertEqual(self.engine.execute_program(*parsed).status,'rejected')
        self.assertFalse(self.launched)
        self.manager.set_enabled('programmi_app',True)
        self.save({self.mail:'apri la posta'},enabled=False)
        self.assertEqual(self.engine.execute_program(*parsed).status,'rejected')
        self.assertFalse(self.launched)

    def test_catalog_above_twenty_preserves_selections_and_partial_failure(self):
        from program_apps.native import entry
        found=[entry('Applicazione '+str(i),'store','JarvisFixture_'+str(i)+'!App') for i in range(45)]
        self.apps.discoverer=lambda event:(found,[])
        rows=self.apps.refresh_catalog()
        self.assertEqual(len(rows),47)
        self.assertEqual(sum(row['enabled'] for row in rows),2)
        self.apps.discoverer=lambda event:([],['Start non disponibile: copertura incompleta.'])
        self.apps.refresh_catalog()
        self.assertEqual(len(self.apps.entries()),47)
        self.assertTrue(self.apps.warnings)
        self.assertEqual(self.engine.execute('avvia la posta').status,'completed')
        before=self.apps.path.read_bytes()
        def fail(event):raise OSError('source timeout')
        self.apps.discoverer=fail
        with self.assertRaises(OSError):self.apps.refresh_catalog()
        self.assertEqual(self.apps.path.read_bytes(),before)

    def test_changed_manual_executable_requires_new_selection(self):
        app=self.apps._apps[self.mail]
        Path(app.target).write_bytes(b'changed executable')
        self.apps.add_manual(app.target)
        self.assertEqual(self.engine.execute('avvia la posta').status,'rejected')
        self.assertFalse(self.launched)

    def test_new_topic_and_context_revoke_pending_choice(self):
        second=self.add('Posta alternativa')
        self.save({self.mail:'',second:''})
        token=self.engine.execute('avvia Posta').program_listing['token']
        self.assertIsNone(self.apps.parse_command('stato sistema'))
        self.assertEqual(self.engine.execute_program('select',{'query':'1','token':token}).status,'rejected')
        token=self.engine.execute('avvia Posta').program_listing['token']
        self.assertIsNone(self.apps.parse_command('che ore sono?'))
        self.assertEqual(self.engine.execute_program('select',{'query':'1','token':token}).status,'rejected')
        token=self.engine.execute('avvia Posta').program_listing['token']
        self.apps.reset('other-project')
        self.assertEqual(self.engine.execute_program('select',{'query':'1','token':token}).status,'rejected')

    def test_free_custom_phrase_is_local_and_original_name_still_works(self):
        self.save({self.mail:'controlliamo la posta'})
        for phrase in ['controlliamo la posta','avvia Posta µ']:
            self.assertEqual(self.engine.execute(phrase).status,'completed')
        self.assertEqual(self.launched,[self.mail,self.mail])

    def test_unique_partial_name_requires_choice_instead_of_launching(self):
        self.save({self.game:''})
        result=self.engine.execute('avvia difficile')
        self.assertTrue(result.program_listing)
        self.assertFalse(self.launched)
        token=result.program_listing['token']
        self.assertEqual(self.engine.execute_program('select',{'query':'1','token':token}).status,'completed')
        self.assertEqual(self.launched,[self.game])

    def test_unselected_exact_name_does_not_launch_another_similar_selected_app(self):
        other=self.add('Posta')
        self.save({self.mail:'',other:''},enabled=False)
        self.apps.save_preferences({self.mail:dict(enabled=True,phrase=''),
                                   other:dict(enabled=False,phrase='')})
        result=self.engine.execute('avvia Posta')
        self.assertEqual(result.status,'rejected')
        self.assertFalse(self.launched)

    def test_partial_unselected_inventory_entry_does_not_steal_other_open_requests(self):
        self.add('Finestra secondaria')
        self.assertIsNone(self.apps.parse_command('apri Finestra'))
        self.assertFalse(self.launched)

    def test_project_parser_does_not_reserve_normal_app_launch_or_raise_on_paths(self):
        from program_apps.service import protected
        self.assertFalse(protected('apri Netflix'))
        self.assertFalse(protected('apri la posta'))
        self.assertTrue(protected('apri il progetto Netflix'))
        self.assertTrue(protected('riprendi Netflix'))
        self.assertIsNone(self.apps.parse_command('apri C:\\Cartella con spazi'))
        self.assertIsNone(self.apps.parse_command('apri '+'parola '*40))
