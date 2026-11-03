"""Windows program evidence: real shortcuts/registry, controlled profiles and ingress."""
import json
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

import test_file_access as file_tests
import test_file_refinement as flow_tests
from file_access.windows import installed_locations, program_location
from conversation_router import parse_conversation_intent


@unittest.skipUnless(os.name=='nt','Windows-only user requirement')
class ProgramLocationTests(unittest.TestCase):
    setUp = file_tests.FileAccessTests.setUp
    callback = flow_tests.FileRefinementTests.callback
    receive = flow_tests.FileRefinementTests.receive
    environment = flow_tests.FileRefinementTests.environment

    @classmethod
    def setUpClass(cls):
        flow_tests.FileRefinementTests.setUpClass.__func__(cls)

    def native_shortcut_rows(self, name, target, root=None):
        root=root or self.docs/'Links'
        root.mkdir(exist_ok=True)
        link=root/(name+'.lnk')
        decoy=self.docs/'Dati separati'; decoy.mkdir(exist_ok=True)
        quote=lambda p:str(p).replace("'","''")
        script=Path('file_access/windows_shell.ps1').resolve()
        harness=self.root/('shortcut-'+uuid4().hex+'.ps1')
        harness.write_text(
            "$script:realWsh = New-Object -ComObject WScript.Shell\n"
            "$link = $script:realWsh.CreateShortcut('"+quote(link)+"')\n"
            "$link.TargetPath = '"+quote(target)+"'\n"
            "$link.WorkingDirectory = '"+quote(decoy)+"'\n"
            "$link.Arguments = '--data-dir decoy'\n$link.Save()\n"
            "$script:folders = [pscustomobject]@{}\n"
            "$script:folders | Add-Member ScriptMethod Item { param($name) if ($name -eq 'Desktop') { '"+quote(root)+"' } else { '' } }\n"
            "$script:wrapper = [pscustomobject]@{SpecialFolders=$script:folders}\n"
            "$script:wrapper | Add-Member ScriptMethod CreateShortcut { param($path) $script:realWsh.CreateShortcut($path) }\n"
            "function New-Object { param([string]$ComObject) if ($ComObject -eq 'WScript.Shell') { $script:wrapper } else { throw 'Unexpected COM' } }\n"
            "function Get-StartApps { @() }\n"
            "function Get-AppxPackage { throw 'Store unavailable in controlled fixture' }\n"
            ". '"+quote(script)+"'\n",encoding='utf-8-sig')
        powershell=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
        run=subprocess.run([str(powershell),'-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(harness)],
            input=json.dumps({'operation':'installed','query':name}),capture_output=True,
            text=True,encoding='utf-8',timeout=15,cwd=os.environ['SystemRoot'])
        self.assertEqual(run.returncode,0,run.stderr)
        result=json.loads(run.stdout.lstrip('\ufeff'))
        self.assertEqual(result['status'],'ok',result)
        self.assertTrue(link.is_file())
        return result['rows']

    def test_real_shortcut_name_finds_opaque_directory_and_voice_open_once(self):
        name='JarvisFixture'+uuid4().hex[:8]
        opaque=self.docs/'vendor-4391'; opaque.mkdir()
        exe=opaque/'engine.exe'; exe.write_bytes(b'MZ controlled fixture, never executed')
        rows=self.native_shortcut_rows(name,exe)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['source'],'shortcut')
        self.assertTrue(os.path.samefile(rows[0]['path'],exe))
        self.files.index=Mock(side_effect=AssertionError('No name scan needed for native evidence'))
        env,workers=self.environment()
        with patch('file_access.windows.shell_query',return_value={'status':'ok','rows':rows}):
            env['output_queue'].put(('voice_text','Jarvis dove è installato '+name))
            self.receive('voice_text',env)
            workers.pop(0)()
            with patch('file_access.ui.show_results'):
                self.receive('local',env)
        self.assertEqual(len(self.files._results),1)
        self.assertTrue(os.path.samefile(self.files._results[0],opaque))
        self.assertNotEqual(self.files._results[0].name,name)
        env['service'].call.assert_not_called()
        env['try_file_command']('apri cartella 1')
        with patch('subprocess.Popen') as launch:
            workers.pop(0)()
            self.receive('local',env)
        self.assertEqual(launch.call_count,1)
        self.assertTrue(os.path.samefile(launch.call_args.args[0][1],opaque))
        env['service'].call.assert_not_called()

    def test_native_shortcut_adapts_to_two_different_profile_roots(self):
        for suffix in ('utente-A','altro-profilo-B'):
            profile=self.docs/suffix; profile.mkdir()
            exe=profile/'opaque.exe'; exe.write_bytes(b'MZ fixture')
            rows=self.native_shortcut_rows('Friendly App',exe,profile/'Desktop')
            with patch('file_access.windows.shell_query',return_value={'status':'ok','rows':rows}):
                found=installed_locations('Friendly App')
            self.assertEqual(len(found),1)
            self.assertTrue(os.path.samefile(found[0][0],profile))
            self.assertIn('Collegamento Windows',found[0][1])

    def test_real_hkcu_app_paths_finds_executable_with_different_name(self):
        import winreg
        name='JarvisRegistry'+uuid4().hex
        key_path=r'Software\Microsoft\Windows\CurrentVersion\App Paths'+'\\'+name+'.exe'
        opaque=self.docs/'opaque-registry'; opaque.mkdir()
        exe=opaque/'different.exe'; exe.write_bytes(b'MZ fixture')
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,key_path,0,winreg.KEY_WRITE|winreg.KEY_WOW64_64KEY) as key:
            winreg.SetValueEx(key,'',0,winreg.REG_SZ,'"'+str(exe)+'"')
        self.addCleanup(winreg.DeleteKeyEx,winreg.HKEY_CURRENT_USER,key_path,winreg.KEY_WOW64_64KEY)
        with patch('file_access.windows.shell_query',return_value={'status':'ok','rows':[]}):
            found=installed_locations(name)
        self.assertEqual(len(found),1)
        self.assertTrue(os.path.samefile(found[0][0],opaque))
        self.assertEqual(found[0][1],'App Paths Windows: '+name)

    def test_precise_friendly_name_wins_over_similar_programs_without_model(self):
        first=self.docs/'A'; first.mkdir()
        second=self.docs/'B'; second.mkdir()
        rows=[(first,'App Paths Windows: Example'),(first,'Collegamento Windows: Example'),
              (second,'Registrazione Windows: Example Tools')]
        self.files.index=Mock(side_effect=AssertionError('No scan'))
        with patch('file_access.service.installed_locations',return_value=rows):
            result=self.engine.execute("dov’è installato Example?")
        self.assertEqual(result.status,'completed',result.message)
        self.assertEqual(len(self.files._results),1)
        self.assertTrue(os.path.samefile(self.files._results[0],first))
        self.assertNotIn('Quale applicazione',result.message)
        self.assertNotIn('refinement',result.file_listing)

    def test_distinct_programs_ask_and_keep_locate_goal(self):
        first=self.docs/'A'; first.mkdir()
        second=self.docs/'B'; second.mkdir()
        with patch('file_access.service.installed_locations',return_value=[
                (first,'App Paths Windows: Example One'),(second,'Collegamento Windows: Example Two')]):
            result=self.engine.execute('trovami la cartella del programma Example')
        self.assertIn('Quale applicazione',result.message)
        self.assertEqual(self.files.parse_command('Example Two'),('locate',{'query':'Example Two'}))

    def test_supported_natural_requests_reuse_locate_not_literal_folder_search(self):
        for phrase in ("dov'è installato Example",'dove è installata Example?',
                       'dove si trova il programma Example',
                       'trovami la cartella del programma Example',
                       'cerca la cartella dell’applicazione Example'):
            self.assertEqual(self.files.parse_command(phrase),('locate',{'query':'Example'}),phrase)
        self.assertIsNone(self.files.parse_command('dove si trova il mio progetto'))
        self.assertIsNone(self.files.parse_command("dov'è installato"))
        self.assertIsNone(self.files.parse_command('dove si trova il programma'))

    def test_model_portable_user_path_resolves_locally_for_two_profiles(self):
        for name in ('Profile-A','Profile-B'):
            profile=self.docs/name; profile.mkdir()
            target=profile/'OpaqueDirectory'; target.mkdir()
            intent=parse_conversation_intent(json.dumps(dict(kind='capability',
                action_id='addon.accesso_file.apri',arguments={'target':'%APPDATA%\\OpaqueDirectory','kind':'folder'})),
                addon_resolver=self.manager.resolve)
            with patch('file_access.windows.known_folder',return_value=profile),patch('subprocess.Popen') as launch:
                cap=intent.capability
                result=self.engine.execute_file(cap.file_operation,dict(cap.file_arguments))
            self.assertEqual(result.status,'completed',result.message)
            self.assertTrue(os.path.samefile(launch.call_args.args[0][1],target))

    def test_known_folder_mapping_and_policy_apply_to_portable_hints(self):
        for token,folder in (('APPDATA','appdata'),('LOCALAPPDATA','appdata locale'),('USERPROFILE','profilo')):
            with patch('file_access.windows.known_folder',return_value=self.docs) as known:
                self.assertTrue(os.path.samefile(self.files._target('%'+token+'%'),self.docs))
                known.assert_called_once_with(folder)
        with patch('file_access.windows.known_folder',return_value=self.hidden),patch('subprocess.Popen') as launch:
            result=self.engine.execute_file('open',{'target':'%APPDATA%','kind':'folder'})
        self.assertEqual(result.status,'rejected')
        launch.assert_not_called()
        for tail in ('..\\Privato','\\root','D:\\other'):
            with self.assertRaises(ValueError):
                self.files._target('%APPDATA%\\'+tail)

    def test_registered_paths_with_commas_are_not_truncated_or_executed(self):
        folder=self.docs/'Vendor, Inc'; folder.mkdir()
        exe=folder/'program.exe'; exe.write_bytes(b'MZ fixture')
        for raw in ('"'+str(exe)+'",0',str(exe)+',-12'):
            actual=program_location(raw,icon=True,query='Vendor')
            self.assertIsNotNone(actual)
            self.assertTrue(os.path.samefile(actual,folder))
        self.assertTrue(os.path.samefile(program_location(str(folder)),folder))
        self.assertIsNone(program_location(str(exe)+' --arg',executable=True))

    def test_shortcut_hosts_network_and_stale_targets_are_not_installations(self):
        host=self.docs/'javaw.exe'; host.write_bytes(b'MZ fixture')
        self.assertIsNone(program_location(str(host),executable=True,query='Minecraft'))
        self.assertIsNone(program_location(str(self.docs/'missing.exe'),executable=True))
        self.assertIsNone(program_location(r'\\server\share\app.exe',executable=True))
        self.assertIsNone(program_location('https://example.com/app.exe',executable=True))
        with patch('file_access.windows.shell_query',return_value={'status':'ok','rows':[
                {'path':str(host),'name':'Minecraft','source':'shortcut'}]}):
            self.assertEqual(installed_locations('Minecraft'),[])

    def test_local_evidence_is_still_filtered_and_rechecked_before_open(self):
        excluded=self.hidden/'engine.exe'; excluded.write_bytes(b'MZ fixture')
        with patch('file_access.windows.shell_query',return_value={'status':'ok','rows':[
                {'path':str(excluded),'name':'Unique App','source':'shortcut'}]}):
            result=self.engine.execute_file('locate',{'query':'Unique App'})
        self.assertEqual(result.file_listing['items'],())
        folder=self.docs/'Allowed'; folder.mkdir()
        with patch('file_access.service.installed_locations',return_value=[(folder,'App Paths Windows: Allowed')]):
            self.engine.execute_file('locate',{'query':'Allowed'})
        self.files.policy.configure([(self.docs,True),(folder,False)])
        with patch('subprocess.Popen') as launch:
            result=self.engine.execute_file('open',{'target':'1'})
        self.assertEqual(result.status,'rejected')
        launch.assert_not_called()


if __name__=='__main__':
    unittest.main()

