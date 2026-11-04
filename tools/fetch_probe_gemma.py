"""Fetch a public GGUF for CI only; verify against publisher metadata."""
import hashlib
import json
from pathlib import Path
import urllib.request
repo='bartowski/gemma-2-2b-it-GGUF'
name='gemma-2-2b-it-Q4_K_M.gguf'
with urllib.request.urlopen('https://huggingface.co/api/models/'+repo+'?blobs=true',timeout=30) as response:
    data=json.load(response)
revision=data['sha']
item=next(x for x in data['siblings'] if x['rfilename']==name)
expected=item['lfs']['sha256']
size=item['lfs']['size']
if len(revision)!=40 or len(expected)!=64 or not 1000000000<size<2200000000:
    raise RuntimeError('Unexpected publisher metadata.')
path=Path('probe-model.gguf')
h=hashlib.sha256();count=0
with urllib.request.urlopen('https://huggingface.co/'+repo+'/resolve/'+revision+'/'+name,timeout=90) as response, path.open('wb') as out:
    while True:
        chunk=response.read(1024*1024)
        if not chunk: break
        count+=len(chunk)
        if count>size: raise RuntimeError('GGUF exceeds publisher size.')
        h.update(chunk);out.write(chunk)
if count!=size or h.hexdigest()!=expected:
    raise RuntimeError('GGUF integrity mismatch.')
Path('probe-model-source.json').write_text(json.dumps({'repository':repo,'revision':revision,'file':name,
    'sha256':expected,'bytes':size,'matches_user_file':'not_verified'},indent=2),encoding='utf-8')
print('CI GGUF verified: '+expected)
