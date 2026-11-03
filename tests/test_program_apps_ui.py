"""Actual Tk settings with real temporary service, no personal app launches."""
import os
import time
import unittest
import test_program_apps_service as service_tests


@unittest.skipUnless(os.name=='nt','Windows-only user requirement')
class ProgramUITests(unittest.TestCase):
    add=service_tests.ProgramServiceTests.add
    save=service_tests.ProgramServiceTests.save

    def setUp(self):
        service_tests.ProgramServiceTests.setUp(self)
        import tkinter as tk
        from program_apps.ui import ProgramSettings
        self.root_ui=tk.Tk();self.root_ui.withdraw()
        self.ui=ProgramSettings(self.root_ui,self.apps)
        self.ui.window.withdraw()
        self.root_ui.update()

    def tearDown(self):
        self.ui.close()
        self.root_ui.destroy()

    def test_settings_save_phrase_and_checkbox_change_real_permissions(self):
        self.ui.table.selection_set(self.mail);self.ui.select()
        self.ui.phrase.set('portami alla posta')
        self.assertTrue(self.ui.save())
        self.assertEqual(self.engine.execute('portami alla posta').status,'completed')
        self.ui.toggle_selected()
        self.assertTrue(self.ui.save())
        self.assertEqual(self.engine.execute('portami alla posta').status,'rejected')

    def test_collision_shows_error_and_does_not_replace_last_working_settings(self):
        before=self.apps.path.read_bytes()
        self.ui.table.selection_set(self.game);self.ui.select()
        self.ui.phrase.set('avvia la posta')
        self.assertFalse(self.ui.save())
        self.assertIn('Non salvato',self.ui.status.get())
        self.assertEqual(self.apps.path.read_bytes(),before)

    def test_filter_above_twenty_and_cancelled_discovery_keep_saved_rows(self):
        from program_apps.native import entry
        self.apps.discoverer=lambda event:([entry('App '+str(i),'store',f'Fixture_{i}!App') for i in range(40)],[])
        self.apps.refresh_catalog();self.ui.reload()
        self.assertEqual(len(self.ui.table.get_children()),42)
        self.ui.filter.set('Posta µ');self.root_ui.update()
        self.assertEqual(len(self.ui.table.get_children()),1)
        def wait(event):
            event.wait(2)
            raise OSError('Aggiornamento annullato')
        self.apps.discoverer=wait
        self.ui.refresh();self.ui.cancelled.set()
        self.assertEqual(str(self.ui.phrase_entry.cget('state')),'disabled')
        selected=self.ui._selected
        before=dict(self.ui.rows)
        self.ui.toggle_selected()
        self.assertEqual(self.ui.rows,before)
        self.assertFalse(self.ui.save())
        end=time.monotonic()+3
        while self.ui._working and time.monotonic()<end:
            self.root_ui.update();time.sleep(.02)
        self.assertFalse(self.ui._working)
        self.assertIn('annullato',self.ui.status.get())
        self.assertEqual(len(self.apps.entries()),42)
