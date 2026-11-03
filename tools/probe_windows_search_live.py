"""Live Windows Search proof, exclusively in an ephemeral GitHub-hosted Windows runner.

Uses Jarvis's actual indexed_candidates adapter. No scope changes, global reindex,
extra index, external login or fallback counted as an index success.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from file_access.windows import indexed_candidates, known_folder, long_path

SERVICE_STATE = r"""
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false)
$s=Get-CimInstance Win32_Service -Filter "Name='WSearch'"
if ($null -eq $s) { throw 'WSearch is not installed' }
@{start_mode=$s.StartMode;running=[bool]$s.Started} | ConvertTo-Json -Compress
"""
START_SERVICE = r"""
$ErrorActionPreference='Stop'
$s=Get-Service WSearch
if ($s.StartType -eq 'Disabled') { Set-Service WSearch -StartupType Manual }
Start-Service WSearch
(Get-Service WSearch).WaitForStatus('Running',[TimeSpan]::FromSeconds(25))
"""
STOP_SERVICE = r"""
$ErrorActionPreference='Stop'
Stop-Service WSearch -ErrorAction Stop
(Get-Service WSearch).WaitForStatus('Stopped',[TimeSpan]::FromSeconds(25))
"""
DISABLE_SERVICE = r"""
$ErrorActionPreference='Stop'
Set-Service WSearch -StartupType Disabled
"""


def native(script):
    executable = Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
    result = subprocess.run(
        [str(executable), '-NoProfile', '-NonInteractive', '-Command', script],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        timeout=35, shell=False, creationflags=0x08000000,
        cwd=os.environ['SystemRoot'])
    if result.returncode:
        raise RuntimeError('Windows service operation failed: '+result.stderr.strip()[-1500:])
    return result.stdout.lstrip('\ufeff').strip()


def main():
    if (sys.argv[1:] != ['--ci-only'] or os.name != 'nt'
            or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('RUNNER_OS') != 'Windows'
            or os.environ.get('RUNNER_ENVIRONMENT') != 'github-hosted'):
        raise SystemExit('Live service setup is restricted to a GitHub-hosted Windows CI runner.')

    report = {'native_index_verified': False, 'runtime_adapter': 'indexed_candidates',
              'scope_changes': False, 'global_reindex': False,
              'personal_pc_verified': False, 'checks': {}}
    original = None
    temporary = None
    documents = None
    created_documents = False
    stage = 'observe_service'
    deadline = 0.0

    def announce(value):
        nonlocal stage
        stage = value
        print('WINDOWS_SEARCH_LIVE_STAGE='+value, flush=True)

    def query(text, root):
        paths, reason = indexed_candidates(text, root)
        if not reason.startswith('Indice Windows interrogato'):
            return None
        return paths

    def wait_for(label, predicate):
        announce(label)
        while time.monotonic() < deadline:
            if predicate():
                report['checks'][label] = 'passed'
                return
            time.sleep(1)
        raise AssertionError('Native indexing deadline reached during '+label)

    def has_path(paths, wanted):
        return paths is not None and any(
            os.path.normcase(str(p)) == os.path.normcase(str(wanted))
            or (p.exists() and wanted.exists() and p.samefile(wanted)) for p in paths)

    try:
        original = json.loads(native(SERVICE_STATE))
        report['initial_service'] = original
        announce('start_service_in_ci')
        native(START_SERVICE)
        deadline = time.monotonic()+150
        documents = long_path(known_folder('documenti'))
        created_documents = not documents.exists()
        documents.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix='jarvis-index-live-', dir=documents)
        home = long_path(Path(temporary.name))
        root, other = home/'included-query', home/'other-query'
        root.mkdir()
        other.mkdir()
        token = 'jarvis'+uuid.uuid4().hex
        first, second = token+'-first', token+'-renamed'

        wait_for('available_empty_query', lambda: query(first, root) == [])
        sample = root/(first+'.txt')
        sample.write_text('Controlled native Windows Search fixture.', encoding='utf-8')
        wait_for('created_file_found', lambda: has_path(query(first, root), sample))
        if query(first, other) != []:
            raise AssertionError('Query scope leaked a result from another directory')
        report['checks']['other_scope_empty'] = 'passed'

        renamed = sample.with_name(second+'.txt')
        sample.rename(renamed)

        def rename_visible():
            return has_path(query(second, root), renamed) and query(first, root) == []

        wait_for('rename_observed', rename_visible)
        renamed.unlink()
        wait_for('deletion_observed', lambda: query(second, root) == [])

        # Exercise the same SQL/provider with an actual directory, not a file
        # or a mocked index result. This distinguishes folder support from
        # application orchestration and the scope on the user's own PC.
        folder_name = token+'-folder'
        folder = root/folder_name
        folder.mkdir()
        wait_for('created_folder_found', lambda: has_path(query(folder_name, root), folder))
        if query(folder_name, other) != []:
            raise AssertionError('Folder query escaped the requested scope')
        report['checks']['folder_other_scope_empty'] = 'passed'
        folder.rmdir()
        wait_for('folder_deletion_observed', lambda: query(folder_name, root) == [])
        report['native_index_verified'] = True
    except Exception as exc:
        report['failure_stage'] = stage
        report['failure_type'] = type(exc).__name__
        report['failure'] = str(exc)
    finally:
        if original is not None:
            try:
                if not original['running']:
                    native(STOP_SERVICE)
                if original['start_mode'] == 'Disabled':
                    native(DISABLE_SERVICE)
                restored = json.loads(native(SERVICE_STATE))
                if restored != original:
                    raise AssertionError('WSearch service state was not restored')
                report['service_restored'] = True
            except Exception as exc:
                report['service_restored'] = False
                report['restoration_failure'] = str(exc)
        if temporary is not None:
            try:
                temporary.cleanup()
                report['fixture_removed'] = True
            except Exception as exc:
                report['fixture_removed'] = False
                report['cleanup_failure'] = str(exc)
        if created_documents and documents is not None:
            try:
                documents.rmdir()
            except OSError:
                # Never remove unrelated contents created by another runner component.
                pass
    print('WINDOWS_SEARCH_LIVE_PROBE='+json.dumps(report, ensure_ascii=True), flush=True)
    return 0 if (report['native_index_verified'] and report.get('service_restored')
                 and report.get('fixture_removed')) else 1


if __name__ == '__main__':
    raise SystemExit(main())
