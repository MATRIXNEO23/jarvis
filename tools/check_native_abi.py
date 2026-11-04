"""Compare upstream ctypes layouts with native C++ header, on Windows only."""
import ast
import ctypes
import json
import os
from pathlib import Path
import subprocess
import sys

if os.name != 'nt':
    raise SystemExit('Windows-only ABI verification.')
root=Path(sys.argv[1]).resolve()
source=(root/'koboldcpp.py').read_text(encoding='utf-8')
tree=ast.parse(source)
names={'logit_bias','load_model_inputs','generation_inputs','generation_outputs','token_count_outputs'}
constants={'sampler_order_max','tensor_split_max','overridekv_max'}
namespace={'ctypes':ctypes}
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(n,ast.Name) and n.id in constants for n in node.targets):
        for n in node.targets:
            if isinstance(n,ast.Name) and n.id in constants:
                namespace[n.id]=ast.literal_eval(node.value)
    if isinstance(node,ast.ClassDef) and node.name in names:
        # Only pinned upstream data structure declarations, no launcher import.
        exec(compile(ast.Module(body=[node],type_ignores=[]),'upstream-abi','exec'),namespace)
python_layout={}
lines=['#include <string>','#include <vector>','#include "expose.h"','#include <cstddef>','#include <cstdio>','int main(){']
for name in sorted(names):
    cls=namespace[name]
    python_layout[name+'.sizeof']=ctypes.sizeof(cls)
    lines.append('printf("'+name+'.sizeof %zu\\n",sizeof('+name+'));')
    for field,*_ in cls._fields_:
        key=name+'.'+field
        python_layout[key]=getattr(cls,field).offset
        lines.append('printf("'+key+' %zu\\n",offsetof('+name+','+field+'));')
lines.append('return 0;}')
cpp=root/'jarvis_abi_probe.cpp';exe=root/'jarvis_abi_probe.exe'
cpp.write_text('\n'.join(lines),encoding='utf-8')
subprocess.run(['g++','-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True,timeout=60)
raw=subprocess.check_output([str(exe)],text=True,timeout=15)
native={key:int(value) for key,value in (line.split() for line in raw.splitlines())}
if native!=python_layout:
    raise RuntimeError('Native/Python ABI mismatch: '+str({k:(python_layout[k],native.get(k)) for k in python_layout if python_layout[k]!=native.get(k)}))
print(json.dumps({'abi_fields_checked':len(native),'layout_match':True,'inference_verified':False}))
