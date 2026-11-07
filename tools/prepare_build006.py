"""Number the existing Gemma package without changing its operational scripts."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import zipfile

if os.name != 'nt':
    raise SystemExit('Build006 must run on Windows.')

NUMBER = int(os.environ.get('JARVIS_BUILD_NUMBER', '6'))
assert 6 <= NUMBER <= 999
LABEL = f'{NUMBER:03d}'
ROOT = 'Jarvis-Gemma/'
STAMP = (2026, 11, 7, 0, 0, 0)
ARCHIVE = Path('Jarvis-Gemma-PROVA-CORRETTA.zip')
OUT = Path(f'dist/Jarvis-{LABEL}.zip')
NOTICE = f'''JARVIS {LABEL} - CANDIDATA CON CORREZIONI AUDIT
Estrai in una cartella nuova e avvia soltanto avvia_jarvis.bat.
Il launcher conserva il profilo Jarvis-Gemma-Trial delle candidate Gemma.
Non eliminare o sovrascrivere la cartella e i dati della versione precedente.
Il modello GGUF non e incluso: seleziona il tuo nelle impostazioni Gemma.
Python 3.11/3.12 x64 e dipendenze devono essere gia predisposti.
Controlla le guide voce/recupero nelle cartelle docs, file_access e program_apps.
Sono ancora da collaudare Windows10/i3-2100, audio, account e GGUF reali.
L'indice file autonomo non e implementato; resta Windows Search con fallback.
GPT e Telegram usano account reali solo quando attivati e autorizzati.
'''


def snapshot():
    with zipfile.ZipFile(ARCHIVE) as source:
        assert source.testzip() is None
        names = source.namelist()
        assert len(names) == len(set(names))
        for name in names:
            assert name.startswith(ROOT) and '\\' not in name
            assert '..' not in PurePosixPath(name).parts
        entries = {name[len(ROOT):]: source.read(name) for name in names}
    entries[f'LEGGIMI-BUILD-{LABEL}.txt'] = NOTICE.encode('utf-8')
    return entries


def packed(entries, source_sha):
    manifest = {name: hashlib.sha256(data).hexdigest()
                for name, data in sorted(entries.items())}
    version = dict(schema_version=1, build_number=NUMBER, build_label=LABEL,
        source_commit=source_sha, package_root=ROOT.rstrip('/'),
        date='2026-11-07', status='candidate_pc_test_pending', files=manifest,
        residual_issues=['JRV-AUD-016', 'JRV-AUD-023'])
    contents = dict(entries)
    contents['VERSIONE.json'] = (json.dumps(version, indent=2, sort_keys=True)+'\n').encode()
    import io
    result = io.BytesIO()
    with zipfile.ZipFile(result, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for name, data in sorted(contents.items()):
            info = zipfile.ZipInfo(ROOT+name, STAMP)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(info, data, compresslevel=6)
    return result.getvalue(), version


def main():
    source_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    assert source_sha == os.environ['GITHUB_SHA'], 'Checkout differs from workflow source'
    first, version = packed(snapshot(), source_sha)
    scripts = subprocess.check_output(['git', 'ls-files', '-z', '--', '*.py', '*.mjs', '*.ps1']).split(b'\0')
    hashes = {os.fsdecode(p): hashlib.sha256(Path(os.fsdecode(p)).read_bytes()).hexdigest()
              for p in scripts if p}
    # Re-run the actual builder with a different ZIP wall clock. Normalize only
    # container metadata; all operational file contents must remain identical.
    subprocess.run([sys.executable, '-c',
        "import runpy,zipfile;zipfile.time.localtime=lambda *a:(2030,1,2,3,4,6,0,2,-1);"
        "runpy.run_path('tools/build_gemma_clean_trial.py',run_name='__main__')"], check=True)
    second, second_version = packed(snapshot(), source_sha)
    assert first == second and version == second_version, 'Package is not reproducible'
    for path, digest in hashes.items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, path
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(first)
    details = dict(schema_version=1, build_number=NUMBER, build_label=LABEL,
        archive=OUT.name, package_root=ROOT.rstrip('/'), source_commit=source_sha,
        sha256=hashlib.sha256(first).hexdigest(), bytes=len(first),
        files=len(version['files'])+1, date='2026-11-07',
        status='candidate_pc_test_pending', reproducible_different_clock=True,
        residual_issues=version['residual_issues'])
    OUT.with_suffix('.json').write_text(json.dumps(details, indent=2)+'\n', encoding='utf-8')
    print('PREPARED_BUILD006='+json.dumps(details))


if __name__ == '__main__':
    main()
