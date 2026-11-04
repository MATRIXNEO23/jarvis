"""Development proof: use pinned upstream Python mapping with its DLL directly.

No launcher, HTTP server, account or Windows action. This is not the Jarvis
runtime adapter; it isolates native inference before that adapter is written.
"""
import ast
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

if os.name != 'nt':
    raise SystemExit('Windows-only inference proof.')
root=Path(sys.argv[1]).resolve()
model=Path(sys.argv[2]).resolve(strict=True)
source=root/'koboldcpp.py'
spec=importlib.util.spec_from_file_location('jarvis_upstream_proof',source)
k=importlib.util.module_from_spec(spec)
spec.loader.exec_module(k)
# Reuse the original argument defaults without calling main(), which starts
# the launcher/server. The source revision is pinned by the workflow.
tree=ast.parse(source.read_text(encoding='utf-8'))
block=next(n for n in reversed(tree.body) if isinstance(n,ast.If)
           and isinstance(n.test,ast.Compare) and isinstance(n.test.left,ast.Name)
           and n.test.left.id=='__name__')
last=block.body[-1]
if not (isinstance(last,ast.Expr) and isinstance(last.value,ast.Call)
        and isinstance(last.value.func,ast.Name) and last.value.func.id=='main'):
    raise RuntimeError('Upstream argument initialization changed.')
exec(compile(ast.Module(body=block.body[:-1],type_ignores=[]),str(source),'exec'),k.__dict__)
k.args=k.parser.parse_args(['--usecpu','--noavx2','--gpulayers','0',
    '--threads','2','--blasthreads','2','--contextsize','2048','--quiet'])
k.maxctx=2048
k.args.usemmap=True
k.args.ropeconfig=[0.0,10000.0]
# Keep source/dll folder private to the proof; no executable or web server.
k.init_library()
started=time.perf_counter()
if not k.load_model(str(model)):
    raise RuntimeError('Native model load failed.')
load_seconds=time.perf_counter()-started
results=[]
for request in ['Saluta brevemente in italiano.','Quanto fa due più due? Rispondi brevemente.']:
    prompt='<start_of_turn>user\n'+request+'<end_of_turn>\n<start_of_turn>model\n'
    started=time.perf_counter()
    result=k.generate({'prompt':prompt,'max_context_length':2048,'max_length':32,
                       'temperature':0.1,'top_k':100,'top_p':0.9,'sampler_seed':123,
                       'stop_sequence':['<end_of_turn>']})
    elapsed=time.perf_counter()-started
    if result['status']!=1 or not result['text'].strip():
        raise RuntimeError('Native generation failed or returned empty text.')
    results.append({'request':request,'text':result['text'],'seconds':elapsed,
                    'prompt_tokens':result['prompt_tokens'],
                    'completion_tokens':result['completion_tokens']})
report={'proof':'native_Gemma_two_turns_one_model_load','load_seconds':load_seconds,
        'results':results,'pavilion_verified':False,'performance_parity_verified':False,
        'jarvis_integration_verified':False}
Path('native-gemma-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('NATIVE_GEMMA_REPORT='+json.dumps(report,ensure_ascii=False))
