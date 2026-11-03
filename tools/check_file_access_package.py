"""Windows smoke of the extracted package, without model, mic or network."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

if os.name != 'nt':
    raise SystemExit('Only Windows verification is authorized.')
archive = Path(sys.argv[1]).resolve()
source = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='jarvis-package-') as temporary:
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert all(entry.date_time == (2026,11,3,0,0,0) for entry in bundle.infolist())
        bundle.extractall(temporary)
    package = next(Path(temporary).iterdir())
    version=json.loads((package/'VERSIONE.json').read_text())
    assert version['build_number'] == 4 and version['build_label'] == '004'
    assert package.name == 'Jarvis-004' and archive.name == 'Jarvis-004.zip'
    if os.environ.get('GITHUB_SHA'):
        assert version['source_commit'] == os.environ['GITHUB_SHA']
    manifest=version['files']
    actual={p.relative_to(package).as_posix() for p in package.rglob('*') if p.is_file()}
    assert actual == set(manifest) | {'VERSIONE.json'}, 'Unexpected or missing operational files'
    for relative,digest in manifest.items():
        assert hashlib.sha256((package/relative).read_bytes()).hexdigest()==digest, relative
    assert sorted(p.name for p in package.glob('avvia*.bat'))==['avvia_jarvis.bat']
    app_files={'program_apps/'+name for name in ('__init__.py','native.py','service.py',
        'ui.py','windows_apps.ps1','ProgrammiApp.jaddon','LEGGIMI.md')}
    assert app_files <= actual, 'Incomplete Programmi e app add-on'
    app_manifest=json.loads((package/'program_apps/ProgrammiApp.jaddon').read_text(encoding='utf-8'))
    assert app_manifest['id']=='programmi_app'
    assert any(action['core_action']=='apps.launch' for action in app_manifest['actions'])
    print('EXTRACTED_MANIFEST_AND_SINGLE_LAUNCHER_OK')
    # Separate process and cwd: imports cannot accidentally use checkout modules.
    imports = "import jarvis,addon_manager,local_engine;from file_access.service import FileAccessService;from file_access.ui import FolderSettings;from program_apps.service import ProgramService;from program_apps.ui import ProgramSettings;print('EXTRACTED_IMPORTS_OK')"
    subprocess.run([sys.executable,'-c',imports],cwd=package,check=True,timeout=45)
    tests = f"import sys,unittest;sys.path.append({str(source/'tests')!r});suite=unittest.defaultTestLoader.loadTestsFromNames(['test_file_access','test_activity_status','test_file_refinement','test_program_locations','test_file_context_delivery','test_pending_file_context','test_file_index_priority','test_file_search_phrase','test_voice_corrections_review','test_hud_quick_toggles','test_program_apps','test_program_apps_native','test_program_apps_service','test_program_apps_ui','test_program_apps_integration']);r=unittest.TextTestRunner(verbosity=2).run(suite);sys.exit(not r.wasSuccessful())"
    subprocess.run([sys.executable,'-c',tests],cwd=package,check=True,timeout=300)
    # Exercise the real UI startup and its normal close callback with all live
    # services switched off only in this disposable test profile.
    boot = '''import tempfile,os,tkinter as tk
from settings import load_settings,save_settings
with tempfile.TemporaryDirectory() as profile:
 os.environ['JARVIS_TRIAL_HOME']=profile
 settings=load_settings();settings.update(auto_listen=False,gpt_enabled=False,telegram_enabled=False,tts_enabled=False)
 save_settings(settings)
 original=tk.Tk
 def create(*args,**kwargs):
  root=original(*args,**kwargs)
  root.after(1500,lambda:root.tk.call(root.protocol('WM_DELETE_WINDOW')))
  return root
 tk.Tk=create
 import jarvis
 jarvis.main()
 print('EXTRACTED_UI_BOOT_AND_CLOSE_OK')
'''
    subprocess.run([sys.executable,'-c',boot],cwd=package,check=True,timeout=45)
print('EXTRACTED_PACKAGE_CHECKS_OK')

# Rebuild with a different wall clock: VERSIONE must be deterministic too.
from unittest.mock import patch
from build_file_access import build
with tempfile.TemporaryDirectory(prefix='jarvis-rebuild-') as rebuilt:
    with patch('zipfile.time.localtime',return_value=(2030,1,2,3,4,6,0,2,-1)):
        second=build(source,Path(rebuilt))
    assert second.read_bytes()==archive.read_bytes(), 'Rebuilding the same source changed archive bytes'
print('REPRODUCIBLE_PACKAGE_DIFFERENT_CLOCK_OK')
