"""Build the operational ZIP on Windows; development files stay in Git."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile

NAME = 'Jarvis-Accesso-File-0.1.0-20261101'


def build(source: Path, destination: Path) -> Path:
    if os.name != 'nt':
        raise RuntimeError('Package creation/verification must run on Windows.')
    source, destination = Path(source).resolve(), Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    # All root Python modules are operational source, including the trial preparer.
    files = sorted({*source.glob('*.py'), *source.glob('*.bat'), *source.glob('*.ps1'),
                    source/'gpt_bridge.mjs', source/'jarvis_commands.json',
                    source/'LEGGIMI-ACCESSO-FILE.txt',
                    *[p for p in (source/'file_access').iterdir()
                      if p.is_file() and p.suffix in ('.py','.ps1','.jaddon','.md')],
                    source/'examples/addons/DiagnosticaSistema.jaddon'})
    commit = os.environ.get('JARVIS_SOURCE_COMMIT') or subprocess.check_output(
        ['git','rev-parse','HEAD'], cwd=source, text=True).strip()
    archive = destination/(NAME+'.zip')
    manifest = {str(p.relative_to(source)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in files}
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as target:
        for path in files:
            if path.is_symlink() or not path.is_file():
                raise RuntimeError('Operational file missing: '+str(path))
            relative = path.relative_to(source).as_posix()
            entry = zipfile.ZipInfo(NAME+'/'+relative,(2026,11,1,0,0,0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            target.writestr(entry,path.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        target.writestr(NAME+'/VERSIONE.json',json.dumps({
            'version':'0.1.0-candidate','source_commit':commit,'base_commit':
            'b936879a431370d206152be7b089baf587d15499','files':manifest},indent=2))
    with zipfile.ZipFile(archive) as target:
        assert target.testzip() is None
        assert not any('/tests/' in n or '/.github/' in n or '/docs/' in n or '/AGENTS.md' in n
                       or '/Download/' in n or '__pycache__' in n for n in target.namelist())
    details = {'source_commit':commit,'archive':archive.name,'files':len(files)+1,
               'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
               'tested_on':'Windows CI; see workflow for extracted tests', 'runtime_only':True}
    (destination/(NAME+'.json')).write_text(json.dumps(details,indent=2)+'\n',encoding='utf-8')
    print('FILE_ACCESS_PACKAGE='+json.dumps(details))
    return archive


if __name__ == '__main__':
    import sys
    build(Path(__file__).resolve().parents[1],Path(sys.argv[1]))
