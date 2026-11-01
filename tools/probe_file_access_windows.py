"""Native feasibility check: Windows only; fixtures live in a temporary folder."""
import json
import os
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from file_access.windows import known_folder, volume_identity, resolved_path, indexed_candidates

if os.name != 'nt':
    raise SystemExit('This probe must run on Windows, not Linux.')
report = {'platform': sys.platform, 'python': sys.version.split()[0]}
for name in ('profilo', 'documenti', 'download', 'appdata', 'windows'):
    path = known_folder(name)
    assert path.is_absolute(), name
    report[name] = 'resolved by Windows'
with tempfile.TemporaryDirectory(prefix='jarvis-probe-') as temporary:
    root = Path(temporary)
    sample = root/'campione-à.txt'
    sample.write_text('Prova controllata', encoding='utf-8')
    assert resolved_path(sample).samefile(sample)
    assert volume_identity(sample) == volume_identity(root)
    results, reason = indexed_candidates('campione', root)
    report['native_path_and_volume'] = 'passed'
    report['search'] = reason
    report['index_results'] = len(results)
    report['index_available'] = reason.startswith('Indice Windows interrogato')
print('FILE_ACCESS_NATIVE_PROBE='+json.dumps(report, ensure_ascii=True))
