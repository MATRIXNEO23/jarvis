"""Packaging source parity and future workflow gates, without an app build."""
import base64
import builtins
from contextlib import chdir
from dataclasses import replace
import os
import shutil
from pathlib import Path
import subprocess
import tempfile
import textwrap
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import test_native_trial_ownership as ownership


def build_workflow_script():
    source = Path('.github/workflows/gemma-windows-test-package.yml').read_text(encoding='utf-8')
    section = source.split('      - name: Build and validate clean ZIP\n', 1)[1]
    block = section.split('        run: |\n', 1)[1].split('      - name:', 1)[0]
    return textwrap.dedent(block)


@unittest.skipUnless(os.name == 'nt', 'Windows-only project requirement')
class PackageSourceParityTests(unittest.TestCase):
    def test_builder_failure_before_archive_does_not_mutate_verified_python(self):
        builder = Path('tools/build_gemma_clean_trial.py').read_text(encoding='utf-8')
        names = ('jarvis.py', 'avvia_jarvis.bat', 'local_model/native_ui.py', 'local_model/native_factory.py')
        sources = {name: Path(name).read_bytes() for name in names}
        archive = Mock(side_effect=RuntimeError('An application archive must never be created by this test'))
        git = SimpleNamespace(check_output=Mock(return_value=b'\0'.join(n.encode() for n in names)+b'\0'))
        original_import = builtins.__import__
        def imported(name, *args, **kwargs):
            if name == 'subprocess':
                return git
            if name == 'zipfile':
                return SimpleNamespace(ZipFile=archive, ZIP_DEFLATED=8)
            return original_import(name, *args, **kwargs)
        with tempfile.TemporaryDirectory(prefix='jarvis-package-parity-') as temporary:
            root = Path(temporary)
            for name, data in sources.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            with chdir(root), self.assertRaises(AssertionError):
                # Real builder, isolated inputs; deliberately absent native
                # files stop it before ZIP. Import stubs affect only this exec.
                exec(compile(builder, 'actual-builder-no-native-assets', 'exec'),
                     {'__builtins__': dict(vars(builtins), __import__=imported)})
            archive.assert_not_called()
            git.check_output.assert_called_once_with(['git', 'ls-files', '-z'])
            self.assertFalse((root / 'Jarvis-Gemma-PROVA-CORRETTA.zip').exists())
            for name in names:
                if name.endswith('.py'):
                    self.assertEqual((root / name).read_bytes(), sources[name], name)

    def workflow(self, *, mutate=False, builder_exit=0, compile_exit=0, target='sample.py'):
        block = build_workflow_script()
        stub = r'''
[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false)
function python {
    if ($args[0] -eq 'tools/build_gemma_clean_trial.py') {
        Write-Output 'FIXTURE_BUILDER'
        if ($env:JRV_AUD012_MUTATE -eq '1') {
            [IO.File]::WriteAllText((Join-Path $PWD $env:JRV_AUD012_TARGET), "changed fixture`n")
        }
        $global:LASTEXITCODE=[int]$env:JRV_AUD012_EXIT
    } else {
        Write-Output 'FIXTURE_OTHER_PYTHON'
        if ($args[0] -eq '-m' -and $args[1] -eq 'py_compile') {
            Write-Output 'FIXTURE_COMPILE'
            $global:LASTEXITCODE=[int]$env:JRV_AUD012_COMPILE_EXIT
        } else {
            Write-Output 'FIXTURE_UNITTEST'
            $global:LASTEXITCODE=0
        }
    }
}
'''
        script = stub + '\ntry {\n' + block + '\n} catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }\n'
        with tempfile.TemporaryDirectory(prefix='jarvis-package-workflow-') as temporary:
            root = Path(temporary).resolve()
            (root / 'sample.py').write_text('x = 1\n', encoding='utf-8')
            (root / 'sample.mjs').write_text('export const x = 1;\n', encoding='utf-8')
            (root / 'sample.ps1').write_text('$x = 1\n', encoding='utf-8')
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True, capture_output=True)
            subprocess.run(['git', '-C', str(root), 'add', '--', 'sample.py', 'sample.mjs', 'sample.ps1'], check=True, capture_output=True)
            powershell = shutil.which('pwsh')
            self.assertIsNotNone(powershell, 'This workflow contract requires the CI pwsh host')
            encoded = base64.b64encode(script.encode('utf-16-le')).decode('ascii')
            run = subprocess.run([str(powershell), '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded],
                capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30,
                cwd=root, creationflags=subprocess.CREATE_NO_WINDOW,
                env=dict(os.environ, JRV_AUD012_MUTATE='1' if mutate else '0', JRV_AUD012_EXIT=str(builder_exit),
                         JRV_AUD012_COMPILE_EXIT=str(compile_exit), JRV_AUD012_TARGET=target))
        self.assertIn('FIXTURE_BUILDER', run.stdout, run.stderr)
        return run

    def test_workflow_accepts_unchanged_verified_scripts(self):
        run = self.workflow()
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn('FIXTURE_OTHER_PYTHON', run.stdout)

    def test_workflow_rejects_builder_mutation_of_verified_script(self):
        for target in ('sample.py', 'sample.mjs', 'sample.ps1'):
            with self.subTest(target=target):
                run = self.workflow(mutate=True, target=target)
                self.assertNotEqual(run.returncode, 0, 'Workflow accepted altered tested source')
                self.assertIn(target, run.stderr)

    def test_workflow_stops_on_builder_failure_before_other_python_commands(self):
        run = self.workflow(builder_exit=7)
        self.assertNotEqual(run.returncode, 0, 'Later commands hid the builder failure')
        self.assertIn('build', run.stderr.lower())
        self.assertNotIn('FIXTURE_OTHER_PYTHON', run.stdout)

    def test_workflow_stops_on_compile_failure_before_successful_unittest(self):
        run = self.workflow(compile_exit=9)
        self.assertNotEqual(run.returncode, 0, 'Unittest hid a compile failure')
        self.assertIn('FIXTURE_COMPILE', run.stdout)
        self.assertNotIn('FIXTURE_UNITTEST', run.stdout)


@unittest.skipUnless(os.name == 'nt', 'Windows-only project requirement')
class NativeSourcePackageBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.harness = ownership.NativeTrialOwnershipTests()
        self.addCleanup(self.harness.doCleanups)
        self.harness.setUp()
        self.harness.abi.release.set()

    def test_unmodified_source_ui_can_run_the_existing_packaged_trial(self):
        from local_model import native_ui
        method = getattr(native_ui.NativeSettingsWindow, 'test_model', None)
        self.assertTrue(callable(method), 'Trial behavior exists only after builder mutation')
        panel = self.harness.window()
        with patch.object(native_ui, 'threading', SimpleNamespace(Thread=self.harness.make_thread)):
            method(panel)
            self.harness.finish_workers()
        self.assertTrue(panel.status_value.startswith('TEST RIUSCITO'), panel.status_value)
        self.assertEqual(len(self.harness.abi.calls), 1)
        self.assertEqual(list(self.harness.session.history), [])

    def test_unmodified_source_factory_supports_existing_bundled_dll_contract(self):
        target = self.harness.root / 'local_model/native_factory.py'
        target.write_bytes(Path('local_model/native_factory.py').read_bytes())
        module = ModuleType('local_model._source_parity_factory')
        module.__file__, module.__package__ = str(target), 'local_model'
        exec(compile(target.read_text(encoding='utf-8'), str(target), 'exec'), module.__dict__)
        config = replace(self.harness.config, dll='')
        with patch.object(module, 'initialize_kobold_cpu', side_effect=self.harness.abi.initialize):
            provider = module.create_native_provider(config, upstream_source=self.harness.root / 'native_engine/koboldcpp.py')
            try:
                self.assertEqual(provider.ask(prompt='Ciao'), 'Risposta locale controllata')
                self.assertTrue(os.path.samefile(provider.bridge.config.dll, self.harness.config.dll))
            finally:
                provider.stop()
