"""Verify actual extracted runtime; test-only support is never shipped."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile

if os.name != 'nt':
    raise SystemExit('Only Windows package verification is authorized.')

SOURCE = Path(__file__).resolve().parents[1]
ARCHIVE = SOURCE / 'dist/Jarvis-006.zip'
DLL_SHA = 'ac834f409855bd7e12a0f0c0ffc8601a663b036b2403d74af4b6b3d3afd49bba'
GUIDES = {'docs/VOCE_OFFLINE.md', 'docs/RECUPERO-IMPOSTAZIONI.md',
          'file_access/LEGGIMI.md', 'program_apps/LEGGIMI.md'}
EXTRA = {'native_engine/koboldcpp.py', 'native_engine/koboldcpp_noavx2.dll',
         'LEGGIMI-GEMMA-TEST.txt', 'LEGGIMI-BUILD-006.txt'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args, cwd, timeout=120):
    subprocess.run(args, cwd=cwd, check=True, timeout=timeout,
        env=dict(os.environ, JARVIS_TRIAL_HOME=str(cwd.parent/'isolated-profile')))


def main():
    details = json.loads(ARCHIVE.with_suffix('.json').read_text(encoding='utf-8'))
    assert details['source_commit'] == os.environ['GITHUB_SHA']
    assert details['build_number'] == 6 and details['build_label'] == '006'
    assert details['bytes'] == ARCHIVE.stat().st_size and details['sha256'] == digest(ARCHIVE)
    source_tests = sum(1 for _ in (SOURCE/'tests').glob('test_*.py'))
    with tempfile.TemporaryDirectory(prefix='jarvis006-package-') as temporary:
        root = Path(temporary)
        with zipfile.ZipFile(ARCHIVE) as bundle:
            assert bundle.testzip() is None
            names = bundle.namelist()
            assert len(names) == len(set(names)) == details['files']
            for info in bundle.infolist():
                name = PurePosixPath(info.filename)
                assert name.parts[0] == 'Jarvis-Gemma' and not name.is_absolute()
                assert '..' not in name.parts and '\\' not in info.filename
                assert not stat.S_ISLNK(info.external_attr >> 16)
                assert info.date_time == (2026, 11, 7, 0, 0, 0)
            bundle.extractall(root)
        package = root / 'Jarvis-Gemma'
        version = json.loads((package/'VERSIONE.json').read_text(encoding='utf-8'))
        manifest = version['files']
        assert version['source_commit'] == details['source_commit'] and version['build_number'] == 6
        actual = {p.relative_to(package).as_posix() for p in package.rglob('*') if p.is_file()}
        assert actual == set(manifest) | {'VERSIONE.json'}
        assert GUIDES <= actual
        assert sorted(p.name for p in package.glob('avvia*.bat')) == ['avvia_jarvis.bat']
        assert 'Jarvis-Gemma-Trial' in (package/'avvia_jarvis.bat').read_text(encoding='utf-8')
        for name, expected in manifest.items():
            assert digest(package/name) == expected, name
            p = PurePosixPath(name)
            assert p.parts[0] not in {'tests', 'tools', '.github', 'Download', 'upstream-kobold'}
            assert p.name not in {'AGENTS.md', 'RECUPERO.md'}
            if p.parts[0] == 'docs':
                assert name in GUIDES, name
            if name not in EXTRA:
                assert (SOURCE/name).is_file(), name
                assert (package/name).read_bytes() == (SOURCE/name).read_bytes(), name
        assert digest(package/'native_engine/koboldcpp_noavx2.dll') == DLL_SHA
        assert (package/'native_engine/koboldcpp.py').read_bytes() == (SOURCE/'upstream-kobold/koboldcpp.py').read_bytes()
        for name in GUIDES:
            for link in re.findall(r'(?<!!)\[[^\]]*\]\(([^\s)]+)\)', (package/name).read_text(encoding='utf-8')):
                if '://' not in link and not link.startswith('#'):
                    assert ((package/name).parent/link.split('#', 1)[0]).exists(), (name, link)
        assert not (package/'tests').exists() and not (package/'tools').exists()
        # Clean package: no source directory in sys.path/cwd or helper overlays.
        run([sys.executable, '-c',
            "import jarvis,addon_manager,local_engine,offline_tts;"
            "from file_access.service import FileAccessService;"
            "from program_apps.service import ProgramService;"
            "from local_model import native_ui,native_factory;"
            "assert callable(native_ui.NativeSettingsWindow.test_model);"
            "import ctypes;ctypes.WinDLL(r'native_engine/koboldcpp_noavx2.dll');"
            "print('CLEAN_EXTRACTED_IMPORTS_NATIVE_DLL_OK')"], package)
        boot = '''import tempfile,os,tkinter as tk,traceback
errors=[]
from settings import load_settings,save_settings
with tempfile.TemporaryDirectory(prefix='jarvis006-profile-') as profile:
 os.environ['JARVIS_TRIAL_HOME']=profile
 settings=load_settings();settings.update(auto_listen=False,gpt_enabled=False,telegram_enabled=False,tts_enabled=False)
 save_settings(settings)
 original=tk.Tk
 class SmokeTk(original):
  def __init__(self,*args,**kwargs):
   original.__init__(self,*args,**kwargs)
   root=self
   def callback_error(exc,value,tb):
    errors.append(str(value))
    traceback.print_exception(exc,value,tb)
   root.report_callback_exception=callback_error
   root.after(1500,lambda:root.tk.call(root.protocol('WM_DELETE_WINDOW')))
 tk.Tk=SmokeTk
 import jarvis
 jarvis.main()
 assert not errors, 'Tk callback errors: '+repr(errors)
 print('CLEAN_EXTRACTED_UI_BOOT_AND_CLOSE_OK')
'''
        # Negative acceptance control: the same smoke must reject a real Tk
        # callback exception instead of mistaking normal process exit for success.
        negative = boot.replace('   root.after(1500,',
            '   root.after(50,lambda:1/0)\n   root.after(1500,')
        rejected = subprocess.run([sys.executable, '-c', negative], cwd=package,
            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60,
            env=dict(os.environ, JARVIS_TRIAL_HOME=str(root/'isolated-negative-profile')))
        assert rejected.returncode != 0 and 'Tk callback errors:' in rejected.stderr
        assert 'division by zero' in rejected.stderr
        print('EXPECTED_CALLBACK_REJECTION_OK', flush=True)
        run([sys.executable, '-c', boot], package, timeout=60)
        print('CLEAN_PACKAGE_MANIFEST_GUIDES_PARITY_AND_UI_OK', flush=True)
        # The full suite includes build-tool/workflow tests. Overlay only its
        # explicit development supports AFTER clean-package acceptance. No
        # operational .py/.mjs/.ps1 is copied from the source checkout.
        for support in ['tests', 'tools', '.github']:
            shutil.copytree(SOURCE/support, package/support, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for doc in (SOURCE/'docs').rglob('*'):
            if doc.is_file() and doc.suffix in {'.md', '.json'}:
                target = package/doc.relative_to(SOURCE)
                if not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(doc, target)
        run(['git', 'init', '--quiet'], package)
        run(['git', 'add', '--all'], package)
        result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
            cwd=package, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600,
            env=dict(os.environ, JARVIS_TRIAL_HOME=str(root/'isolated-suite-profile')))
        log = result.stdout+'\n'+result.stderr
        (SOURCE/'dist/extracted-tests.log').write_text(log, encoding='utf-8')
        print(log, flush=True)
        assert result.returncode == 0, 'Extracted-runtime regression suite failed'
        count = re.search(r'Ran (\d+) tests in', log)
        assert count and int(count.group(1)) == 911, 'Unexpected extracted test count'
        assert not re.search(r'\b(?:FAILED|skipped=)\b', log)
        for name, expected in manifest.items():
            assert digest(package/name) == expected, 'Test mutated operational file: '+name
    evidence = dict(source_commit=details['source_commit'], archive=details['archive'],
        sha256=details['sha256'], manifest_files=details['files'],
        clean_imports_native_dll=True, clean_ui_boot_close=True,
        injected_tk_callback_exception_rejected=True,
        required_guides_and_relative_links=True, operational_source_parity=True,
        full_extracted_runtime_suite=911, test_modules=source_tests,
        test_only_overlays=['tests', 'tools', '.github', 'nonoperative docs'],
        overlays_shipped=False, runtime_files_copied_from_checkout=False,
        hardware_windows10_microphone_accounts_gguf='not tested')
    (SOURCE/'dist/Jarvis-006-validation.json').write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')
    print('VERIFIED_BUILD006='+json.dumps(evidence))


if __name__ == '__main__':
    main()
