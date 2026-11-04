"""Windows CI: exercise the actual bridge with the pinned native DLL and GGUF."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

from local_model.native_bridge import NativeGemmaBridge
from local_model.native_config import NativeModelConfig
from local_model.native_initializer import initialize_kobold_cpu

if os.name != "nt":
    raise SystemExit("Windows-only native proof.")

root = Path(sys.argv[1]).resolve(strict=True)
model = Path(sys.argv[2]).resolve(strict=True)
source = root / "koboldcpp.py"
dll = root / "koboldcpp_noavx2.dll"
if not source.is_file() or not dll.is_file():
    raise RuntimeError("Pinned native upstream files missing.")
spec = importlib.util.spec_from_file_location("jarvis_native_upstream", source)
upstream = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upstream)
config = NativeModelConfig(
    dll=str(dll), model=str(model), threads=2, batch_threads=2,
    context_size=2048, max_output=32, temperature=0.1, seed=123,
).validate()
bridge = NativeGemmaBridge(
    config, upstream,
    initialize=lambda module, settings: initialize_kobold_cpu(
        module, settings, source))
start = time.perf_counter()
bridge.load()
load_seconds = time.perf_counter() - start
responses = []
for question in ("Saluta brevemente in italiano.", "Quanto fa due più due? Rispondi brevemente."):
    prompt = "<start_of_turn>user\n" + question + "<end_of_turn>\n<start_of_turn>model\n"
    start = time.perf_counter()
    answer = bridge.generate(prompt, timeout=120)
    responses.append({"question": question, "answer": answer,
                      "seconds": time.perf_counter() - start})
abort_supported = callable(getattr(getattr(upstream, "handle", None), "abort_generate", None))
if not abort_supported:
    raise RuntimeError("Native DLL abort ABI missing.")
report = {"proof": "native_bridge_real_dll_two_generations",
          "native_abort_abi_present": abort_supported,
          "load_seconds": load_seconds, "responses": responses,
          "pavilion_verified": False, "jarvis_ui_verified": False,
          "performance_parity_verified": False}
Path("native-bridge-real-report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print("NATIVE_BRIDGE_REAL_REPORT=" + json.dumps(report, ensure_ascii=False))
