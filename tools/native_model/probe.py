"""Windows native DLL smoke probe: does NOT load or download a model."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import sys

if os.name != 'nt':
    raise SystemExit('Native proof must run on Windows.')
path=Path(sys.argv[1]).resolve(strict=True)
with os.add_dll_directory(str(path.parent)):
    dll=ctypes.CDLL(str(path))
    exports=['load_model','generate','abort_generate','token_count',
             'get_last_eval_time','get_last_process_time','get_last_token_count']
    for name in exports:
        getattr(dll,name)
    dll.get_last_token_count.argtypes=[]
    dll.get_last_token_count.restype=ctypes.c_int
    count=dll.get_last_token_count()
    if count != 0:
        raise RuntimeError('Unexpected initial generation state: '+str(count))
print(json.dumps({'proof':'native_load_and_export_call_only','inference_verified':False,
    'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'bytes':path.stat().st_size,'exports':exports,'initial_token_count':count}))
