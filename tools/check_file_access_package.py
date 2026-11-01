"""Windows smoke of the extracted package, without model, mic or network."""
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
        bundle.extractall(temporary)
    package = next(Path(temporary).iterdir())
    # Separate process and cwd: imports cannot accidentally use checkout modules.
    imports = "import jarvis,addon_manager,local_engine;from file_access.service import FileAccessService;from file_access.ui import FolderSettings;print('EXTRACTED_IMPORTS_OK')"
    subprocess.run([sys.executable,'-c',imports],cwd=package,check=True,timeout=45)
    tests = f"import sys,unittest;sys.path.append({str(source/'tests')!r});suite=unittest.defaultTestLoader.loadTestsFromName('test_file_access');r=unittest.TextTestRunner(verbosity=2).run(suite);sys.exit(not r.wasSuccessful())"
    subprocess.run([sys.executable,'-c',tests],cwd=package,check=True,timeout=180)
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
