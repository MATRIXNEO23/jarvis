"""Native Windows metadata and actual shell acceptance; no account/audio."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch


@unittest.skipUnless(os.name=='nt','Windows-only user requirement')
class NativeProgramTests(unittest.TestCase):
    def test_real_inventory_reports_coverage_and_unique_current_user_identities(self):
        from program_apps.native import discover
        apps,warnings=discover()
        self.assertIsInstance(warnings,list)
        self.assertEqual(len({app.id for app in apps}),len(apps))
        self.assertTrue(apps or warnings,'An empty source must explain its coverage')
        self.assertTrue(all(app.kind in ('exe','lnk','shell','store') for app in apps))
        print('PROGRAM_APPS_NATIVE_PROBE='+json.dumps(dict(apps=len(apps),
            store_entries=sum(app.kind=='store' for app in apps),warnings=warnings,
            store_targets=[app.target for app in apps if app.kind=='store'],
            successful_store_activation_verified=False,personal_desktop_verified=False)))

    def test_cancelled_native_inventory_returns_without_replacing_data(self):
        from program_apps.native import discover
        event=threading.Event();event.set()
        with self.assertRaisesRegex(OSError,'annullato'):
            discover(event)

    def test_real_shell_link_with_arguments_is_accepted_and_changed_link_is_rejected(self):
        from program_apps.native import manual_entry,launch
        with tempfile.TemporaryDirectory(prefix='jarvis-native-app-') as temp:
            root=Path(temp);link=root/'Comando prova µ.lnk';marker=root/'started.txt'
            request=dict(link=str(link),target=str(Path(os.environ['SystemRoot'])/'System32/cmd.exe'),
                         arguments='/d /c echo native-ok>"'+str(marker)+'"')
            script="$d=[Console]::In.ReadToEnd()|ConvertFrom-Json;$w=New-Object -ComObject WScript.Shell;$s=$w.CreateShortcut($d.link);$s.TargetPath=$d.target;$s.Arguments=$d.arguments;$s.WindowStyle=7;$s.Save()"
            subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',script],
                           input=json.dumps(request),text=True,check=True,capture_output=True,timeout=20)
            app=manual_entry(link)
            self.assertIn('accettata da Windows',launch(app))
            # This temporary child must really execute, not merely return an API success.
            import time
            deadline=time.monotonic()+8
            while not marker.exists() and time.monotonic()<deadline:
                time.sleep(.05)
            self.assertEqual(marker.read_text().strip(),'native-ok')
            link.write_bytes(link.read_bytes()+b'changed')
            with self.assertRaisesRegex(OSError,'cambiato'):
                launch(app)

    def test_launch_message_keeps_shell_acceptance_process_and_window_distinct(self):
        from program_apps.native import entry, launch
        app = entry('App di prova', 'store', 'JarvisTestPackage_123456!App')
        for pid, visible in ((0, None), (123, None), (123, False), (123, True)):
            with self.subTest(pid=pid, visible=visible):
                with patch('program_apps.native._activate_store', return_value=pid), \
                     patch('program_apps.native._foreground_process_window', return_value=visible) as observe:
                    message = launch(app)
                self.assertIn('accettata da Windows', message)
                self.assertEqual('PID 123' in message, bool(pid))
                self.assertEqual('Finestra in primo piano' in message, visible is True)
                self.assertEqual('Finestra individuata' in message, visible is False)
                if pid:
                    observe.assert_called_once_with(pid)
                else:
                    observe.assert_not_called()

    def test_visible_window_probe_observes_own_titled_tk_window(self):
        import tkinter as tk
        from program_apps.native import _find_process_window
        root = tk.Tk()
        self.addCleanup(root.destroy)
        root.title('Lumi native launch observation')
        root.update()
        self.assertTrue(_find_process_window(os.getpid()))

    def test_foreground_waits_for_late_window_and_uses_only_its_handle(self):
        from program_apps.native import _foreground_process_window
        with patch("program_apps.native._find_process_window", side_effect=[None, 42]) as find, \
             patch("program_apps.native.bring_window_forward", return_value=True) as activate, \
             patch("program_apps.native.time.sleep"):
            self.assertTrue(_foreground_process_window(123))
            self.assertEqual(find.call_count, 2)
            activate.assert_called_once_with(42)

    def test_store_activation_invalid_identity_reports_native_failure(self):
        from program_apps.native import entry,launch
        # Exercise the actual COM boundary without launching a personal app.
        with self.assertRaises(OSError):
            launch(entry('Lumi missing app','store','JarvisMissingPackage_123456!NoApp'))

    @unittest.skipUnless(os.environ.get('CI')=='true','Live activation restricted to isolated CI')
    def test_available_known_store_app_activation_in_isolated_runner(self):
        from program_apps.native import discover,_activate_store
        apps,warnings=discover()
        candidates=[app for app in apps if app.kind=='store' and app.target.startswith(
            ('Microsoft.WindowsCalculator_','Microsoft.WindowsTerminal_','Microsoft.WindowsNotepad_',
             'windows.immersivecontrolpanel_'))]
        if not candidates:
            self.skipTest('Runner has no known disposable Store app; successful Store activation remains unverified')
        app=candidates[0]
        pid=_activate_store(app.target)
        self.assertGreater(pid,0)
        print('PROGRAM_APPS_STORE_ACTIVATION='+json.dumps(dict(aumid=app.target,
            process_id=pid,api_accepted=True,window_visible_verified=False)))
        # Close only the process returned for this explicit activation in the
        # disposable runner; no discovery/termination of personal app processes.
        subprocess.run(['taskkill','/PID',str(pid),'/T'],capture_output=True,timeout=15)
