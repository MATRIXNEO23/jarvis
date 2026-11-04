"""Windows CI: verify cancellation of an active native Gemma generation.

Runs in an isolated CI process; no Jarvis UI, no user model state.
"""
import importlib.util
import json
import os
from pathlib import Path
import sys
import threading
import time

from local_model.native_bridge import NativeGemmaBridge
from local_model.native_config import NativeModelConfig
from local_model.native_initializer import initialize_kobold_cpu

if os.name != "nt":
    raise SystemExit("Windows-only native abort proof.")

root = Path(sys.argv[1]).resolve(strict=True)
model = Path(sys.argv[2]).resolve(strict=True)
source = root / "koboldcpp.py"
dll = root / "koboldcpp_noavx2.dll"
spec = importlib.util.spec_from_file_location("jarvis_abort_upstream", source)
upstream = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upstream)
config = NativeModelConfig(
    dll=str(dll), model=str(model), threads=2, batch_threads=2,
    context_size=2048, max_output=512, temperature=0.8, seed=123,
).validate()
bridge = NativeGemmaBridge(
    config, upstream,
    initialize=lambda module, settings: initialize_kobold_cpu(module, settings, source))
bridge.load()

prompt = ("<start_of_turn>user\n"
          "Scrivi una lunga storia in italiano di almeno 1000 parole, senza riassumere. "
          "Continua con molti dettagli e capitoli.<end_of_turn>\n<start_of_turn>model\n")
finished = threading.Event()
outcome = {}

def worker():
    try:
        outcome["answer"] = bridge.generate(prompt, timeout=120)
    except Exception as exc:
        outcome["error"] = type(exc).__name__
        outcome["message"] = str(exc)
    finally:
        finished.set()

thread = threading.Thread(target=worker, daemon=True)
thread.start()
# A request to abort must be made while generation is still active.
time.sleep(0.75)
active_at_abort = not finished.is_set()
if not active_at_abort:
    raise RuntimeError("Generation finished before abort; test inconclusive.")
started = time.monotonic()
bridge.abort()
thread.join(timeout=15)
elapsed = time.monotonic() - started
report = {
    "proof": "real_native_abort_during_generation",
    "active_at_abort": active_at_abort,
    "finished_after_abort": finished.is_set(),
    "abort_wait_seconds": round(elapsed, 3),
    "outcome": outcome,
    "pavilion_verified": False,
    "hard_timeout_verified": False,
}
Path("native-abort-real-report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print("NATIVE_ABORT_REAL_REPORT=" + json.dumps(report, ensure_ascii=False))
if not finished.is_set():
    raise RuntimeError("Native generation did not stop within 15 seconds.")
if "answer" in outcome:
    raise RuntimeError("Aborted generation returned an answer.")
if outcome.get("error") != "RuntimeError":
    raise RuntimeError("Aborted generation did not raise expected cancellation error.")
