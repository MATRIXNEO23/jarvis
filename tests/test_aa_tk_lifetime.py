"""JRV-AUD-022: collect closed, real Tk fixture graphs on a worker in a child.

Each child contains a potential Tcl fatal; the parent never owns those widgets.
The diagnostic precedes assertions so evidence survives an unrelated suite abort.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


_PROBE = r'''
import faulthandler,gc,io,json,sys,threading,unittest,weakref
from pathlib import Path
from unittest.mock import patch
faulthandler.enable()
sys.path.insert(0,str(Path.cwd()/'tests'))
gc.disable()
print('TK_PROBE_MAIN='+str(threading.get_ident()),flush=True)
import tkinter as tk
from animated_hud import JarvisHUD
original_init=JarvisHUD.__init__
images=weakref.WeakSet()
created=[0]
def tracked_init(self,*args,**kwargs):
    original_init(self,*args,**kwargs)
    # A real image leaf adds no owner cycle and avoids dependence on the
    # asynchronous raster cache becoming ready during a short UI fixture.
    self._lifetime_probe_image=tk.PhotoImage(master=self.parent,width=1,height=1)
    images.add(self._lifetime_probe_image)
    created[0]+=1
with patch('animated_hud.NetworkTelemetry.request',return_value=None), patch.object(JarvisHUD,'__init__',tracked_init):
    suite=unittest.defaultTestLoader.loadTestsFromName(sys.argv[1])
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    if not result.wasSuccessful() or result.testsRun!=1 or result.skipped:
        print(stream.getvalue(),file=sys.stderr,flush=True)
        sys.exit(2)
    print('TK_PROBE_FIXTURE_OK',flush=True)
    print('TK_PROBE_IMAGES='+json.dumps(dict(created=created[0],before_worker=len(images))),flush=True)
    if not created[0]:
        sys.exit(4)
    done=threading.Event()
    def collect():
        print('TK_PROBE_WORKER='+str(threading.get_ident()),flush=True)
        gc.collect()
        done.set()
    worker=threading.Thread(target=collect,daemon=True)
    worker.start()
    worker.join(25)
    if not done.is_set():
        print('TK_PROBE_WORKER_TIMEOUT',file=sys.stderr,flush=True)
        sys.exit(3)
    if images:
        print('TK_PROBE_IMAGES_RETAINED',file=sys.stderr,flush=True)
        sys.exit(5)
print('TK_PROBE_COMPLETE',flush=True)
'''


def report_probe(case, returncode, stdout, stderr):
    def tail(value, limit):
        if isinstance(value, bytes):
            value = value.decode('utf-8', errors='replace')
        return (value or '')[-limit:]
    print('TK_LIFETIME_PROBE='+json.dumps(dict(fixture=case,returncode=returncode,
        stdout=tail(stdout,1200),stderr=tail(stderr,4000)),ensure_ascii=True),flush=True)


@unittest.skipUnless(os.name == 'nt', 'Windows-only project requirement')
class TkFixtureLifetimeTests(unittest.TestCase):
    def test_closed_ui_fixtures_are_retired_before_foreign_worker_gc(self):
        cases = (
            'test_activity_status.ActivityStatusTests.test_existing_tk_status_row_follows_real_phases_and_voice_priority',
            'test_animated_hud.AnimatedHUDGeometryTests.test_reference_hud_widgets_when_tk_display_available',
            'test_hud_quick_toggles.HeaderQuickControlTests.test_settings_and_header_share_state_without_false_live_status',
            'test_native_hud_activity.NativeHudActivityTests.test_real_tk_status_shows_native_reasoning_and_keeps_voice_priority',
        )
        for case in cases:
            with self.subTest(fixture=case), tempfile.TemporaryDirectory(prefix='jarvis-tk-gc-') as temporary:
                environment = dict(os.environ, JARVIS_TRIAL_HOME=str(Path(temporary) / 'profile'),
                                   PYTHONDONTWRITEBYTECODE='1')
                try:
                    run = subprocess.run([sys.executable, '-c', _PROBE, case],
                        stdin=subprocess.DEVNULL, capture_output=True, text=True,
                        encoding='utf-8', errors='replace', timeout=45, env=environment,
                        cwd=os.getcwd(), creationflags=subprocess.CREATE_NO_WINDOW)
                except subprocess.TimeoutExpired as error:
                    report_probe(case, 'timeout', error.stdout, error.stderr)
                    raise
                report_probe(case, run.returncode, run.stdout, run.stderr)
                self.assertIn('TK_PROBE_FIXTURE_OK', run.stdout, 'UI fixture must really pass before GC')
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertIn('TK_PROBE_COMPLETE', run.stdout)
                self.assertIn('TK_PROBE_IMAGES=', run.stdout)
                self.assertNotIn('main thread is not in main loop', run.stderr)
                self.assertNotIn('Tcl_AsyncDelete', run.stderr)
                self.assertNotIn('Exception ignored', run.stderr)
