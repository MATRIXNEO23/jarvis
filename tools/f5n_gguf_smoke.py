"""F5N.6 Windows proof: real GGUF load + short generation on the split bundle.

One disposable child process per model (no safe unload exists upstream, so a
model is never replaced inside a process). Uses Jarvis production factory,
initializer and bridge. Gemma runs the real ``NativeGemmaBridge.generate`` and
its watchdog abort; since F5N.7 every family goes through provider.ask with
the template and stop token chosen from the GGUF architecture.
Synthetic prompts only; no personal data, memory or profile is touched.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

FAMILIES = ("gemma2", "qwen25", "qwen3")
LEAK_MARKERS = ("<start_of_turn>", "<end_of_turn>", "<|im_start|>", "<|im_end|>",
                "<think>", "</think>")
QUESTION = "Rispondi con una sola frase: qual è la capitale d'Italia?"


class GgufSmokeError(RuntimeError):
    pass


def worker(build_dir, family, model, output):
    if os.name != "nt":
        raise GgufSmokeError("Windows required")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from local_model.native_config import NativeModelConfig
    from local_model.native_factory import create_native_provider
    from local_model.native_provider import format_gemma_messages

    root = Path(build_dir).resolve(strict=True)
    config = NativeModelConfig(
        dll=str(root / "koboldcpp_noavx2.dll"), model=str(Path(model).resolve(strict=True)),
        threads=2, batch_threads=2, context_size=1024, max_output=48,
        temperature=0.1, top_k=40, top_p=0.9, seed=123)
    provider = create_native_provider(config, upstream_source=root / "koboldcpp.py")
    bridge = provider.bridge
    started = time.monotonic()
    bridge.load()
    load_seconds = round(time.monotonic() - started, 2)
    messages = [{"role": "user", "content": QUESTION}]
    started = time.monotonic()
    # F5N.7 production path for every family: provider formats with the
    # family read from the GGUF header and the bridge uses its stop token.
    text = provider.ask(messages=messages, timeout=300)
    stop, tokens = bridge.last_generation_finish, bridge.last_generation_tokens
    if bridge.family != {"gemma2": "gemma2", "qwen25": "qwen25", "qwen3": "qwen3"}[family]:
        raise GgufSmokeError(f"{family}: detected family {bridge.family}")
    gen_seconds = round(time.monotonic() - started, 2)
    report = {
        "schema": 1, "family": family, "detected_family": bridge.family, "load_seconds_runner": load_seconds,
        "generation_seconds_runner": gen_seconds, "stop": stop, "completion_tokens": tokens,
        "answer": text.strip()[:200],
        "leaked_markers": [m for m in LEAK_MARKERS if m in text],
        "mentions_roma": "roma" in text.lower(),
        "abort_verified": None,
    }
    if family == "gemma2":
        # Production watchdog path: long request, short deadline, must return.
        bridge.update_generation_settings(
            NativeModelConfig(dll=config.dll, model=config.model, context_size=1024,
                              max_output=512, temperature=0.7, top_k=40, top_p=0.9, seed=7))
        started = time.monotonic()
        # Same long request also proves streaming of partial text (020/021).
        from local_model.token_stream import streaming
        chunks, first = [], []
        def collect(text):
            if not first:
                first.append(round(time.monotonic() - started, 2))
            chunks.append(text)
        try:
            with streaming(collect):
                bridge.generate(format_gemma_messages(
                    [{"role": "user", "content": "Scrivi un racconto molto lungo sul mare."}]),
                    timeout=3)
            report["abort_verified"] = False
        except TimeoutError:
            report["abort_verified"] = True
        report["abort_return_seconds_runner"] = round(time.monotonic() - started, 2)
        # 026: fast forwarding, informative. Same long start, different end:
        # the second prompt should reprocess only the new tail.
        fixed = ("Carattere: sei dolce e un po' monella.\nTi chiami Lumi. Rispondi in italiano. "
                 + "Ricorda queste regole di cortesia. " * 25)
        timings = []
        for tail in ("Domanda: che giorno è oggi?", "Domanda: che ore sono adesso?"):
            t0 = time.monotonic()
            try:
                bridge.generate(format_gemma_messages([{"role": "user", "content": fixed + tail}]),
                                timeout=60)
            except Exception:
                pass
            timings.append(round(time.monotonic() - t0, 2))
        report["fast_forward_first_s_runner"], report["fast_forward_second_s_runner"] = timings
        report["stream_chunks"] = len(chunks)
        report["stream_first_seconds_runner"] = first[0] if first else None
        report["stream_sample"] = chunks[-1][:120] if chunks else ""
        report["stream_verified"] = (
            len(chunks) >= 2
            and all(b.startswith(a) for a, b in zip(chunks, chunks[1:]))
            and not any(m in c for c in chunks for m in LEAK_MARKERS))
    report["gguf_load_verified"] = True
    report["model_inference_verified"] = bool(report["answer"]) and not report["leaked_markers"]
    report["pavilion_cpu_verified"] = False
    report["safe_unload_verified"] = False
    Path(output).write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True),
                            encoding="utf-8")


def run_isolated(build_dir, models_dir, output, *, families=FAMILIES, timeout=900,
                 runner=subprocess.run):
    if os.name != "nt":
        raise GgufSmokeError("Windows runner required")
    results, failures = {}, []
    for family in families:
        out = Path(output).resolve().with_name(f"f5n-gguf-{family}.json")
        out.unlink(missing_ok=True)
        command = [sys.executable, "-m", "tools.f5n_gguf_smoke", "--worker",
                   str(Path(build_dir).resolve(strict=True)), family,
                   str(Path(models_dir).resolve(strict=True) / (family + ".gguf")), str(out)]
        try:
            proc = runner(command, capture_output=True, text=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            failures.append(f"{family}: child timed out")
            continue
        if proc.returncode != 0 or not out.is_file():
            failures.append(f"{family}: exit={proc.returncode} {(proc.stderr or '')[-1500:]}")
            continue
        report = json.loads(out.read_text(encoding="utf-8"))
        results[family] = report
        if not report.get("model_inference_verified"):
            failures.append(f"{family}: inference not verified")
        if family == "gemma2" and report.get("abort_verified") is not True:
            failures.append("gemma2: abort not verified")
        if family == "gemma2" and report.get("stream_verified") is not True:
            failures.append("gemma2: streaming not verified")
    Path(output).write_text(json.dumps(results, indent=2, ensure_ascii=False, sort_keys=True),
                            encoding="utf-8")
    if failures:
        print(json.dumps(results, indent=2, ensure_ascii=False, sort_keys=True))
        raise GgufSmokeError("; ".join(failures))
    return results


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--worker", action="store_true")
    p.add_argument("args", nargs="+")
    a = p.parse_args(argv)
    try:
        if a.worker:
            worker(*a.args)
            return 0
        build_dir, models_dir, output = a.args
        result = run_isolated(build_dir, models_dir, output)
    except (GgufSmokeError, OSError, ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        p.exit(2, "F5N.6 GGUF proof failed\n")
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
