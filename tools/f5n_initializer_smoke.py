"""F5N.5 Windows proof: Jarvis initializer + pinned koboldcpp.py + split bundle.

Runs the production ``initialize_kobold_cpu`` against a build directory that
contains the pinned upstream ``koboldcpp.py`` next to its own DLL bundle, in a
disposable child process. It never calls ``load_model`` or ``generate`` and
loads no GGUF. Host command-line arguments are deliberately present to prove
they do not reach the upstream parser.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

REQUIRED_MODULE_CALLABLES = ("load_model", "generate", "tokenize_ids", "init_library")
REQUIRED_HANDLE_FUNCTIONS = ("load_model", "generate", "abort_generate",
                             "has_finished", "new_token", "get_stream_count")


class InitializerSmokeError(RuntimeError):
    pass


def worker(build_dir, output):
    if os.name != "nt":
        raise InitializerSmokeError("Windows required")
    root = Path(build_dir).resolve(strict=True)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_model.native_initializer import initialize_kobold_cpu

    source = root / "koboldcpp.py"
    dll = root / "koboldcpp_noavx2.dll"
    if not source.is_file() or not dll.is_file():
        raise InitializerSmokeError("koboldcpp.py or koboldcpp_noavx2.dll missing")
    spec = importlib.util.spec_from_file_location("jarvis_native_kobold_pinned", source)
    upstream = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(upstream)
    config = SimpleNamespace(dll=str(dll), threads=2, batch_threads=2, context_size=1024)
    host_argv = [sys.argv[0], "upstream-kobold", "probe-model.gguf"]
    sys.argv = list(host_argv)
    initialize_kobold_cpu(upstream, config, source)
    if sys.argv != host_argv:
        raise InitializerSmokeError("host argv not restored")
    handle = getattr(upstream, "handle", None)
    route = getattr(upstream, "common_backend_handle", None)
    missing_module = [n for n in REQUIRED_MODULE_CALLABLES
                      if not callable(getattr(upstream, n, None))]
    missing_handle = [n for n in REQUIRED_HANDLE_FUNCTIONS
                      if not hasattr(handle, n)]
    common_name = Path(getattr(handle, "_name", "") or "").name.lower()
    result = {
        "schema": 1,
        "libname": getattr(upstream, "libname", None),
        "common_loaded": common_name == "koboldcpp_common.dll",
        "backend_route_loaded": route is not None,
        "args_noavx2": bool(getattr(upstream.args, "noavx2", False)),
        "args_threads": getattr(upstream.args, "threads", None),
        "args_contextsize": getattr(upstream.args, "contextsize", None),
        "missing_module_callables": missing_module,
        "missing_handle_functions": missing_handle,
        "host_argv_isolated": True,
        "jarvis_initializer_verified": False,
        "gguf_load_verified": False,
        "model_inference_verified": False,
        "safe_unload_verified": False,
        "pavilion_cpu_verified": False,
    }
    result["jarvis_initializer_verified"] = (
        result["libname"] == "koboldcpp_noavx2.dll" and result["common_loaded"]
        and result["backend_route_loaded"] and result["args_noavx2"]
        and result["args_threads"] == 2 and result["args_contextsize"] == 1024
        and not missing_module and not missing_handle)
    Path(output).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


def run_isolated(build_dir, output, *, timeout=120, runner=subprocess.run):
    if os.name != "nt":
        raise InitializerSmokeError("Windows runner required")
    out = Path(output).resolve()
    if out.exists():
        out.unlink()
    command = [sys.executable, "-m", "tools.f5n_initializer_smoke", "--worker",
               str(Path(build_dir).resolve(strict=True)), str(out)]
    try:
        proc = runner(command, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise InitializerSmokeError("initializer child timed out") from exc
    if proc.returncode != 0 or not out.is_file():
        raise InitializerSmokeError(
            f"initializer child failed (exit={proc.returncode}): "
            + (proc.stderr or "")[-2500:])
    result = json.loads(out.read_text(encoding="utf-8"))
    if not result.get("jarvis_initializer_verified"):
        raise InitializerSmokeError("initializer not verified: " + json.dumps(result, sort_keys=True))
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--worker", action="store_true")
    p.add_argument("build_dir")
    p.add_argument("output")
    args = p.parse_args(argv)
    try:
        if args.worker:
            worker(args.build_dir, args.output)
            return 0
        result = run_isolated(args.build_dir, args.output)
    except (InitializerSmokeError, OSError, ValueError, AttributeError) as exc:
        p.error("F5N.5 initializer proof failed: " + str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
