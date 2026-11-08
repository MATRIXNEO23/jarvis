"""Jarvis 014 live GGUF comparison on Windows, isolated synthetic inputs only.

Uses the production Gemma session, pinned KoboldCpp and one loaded model.
Reports, but does not extrapolate, runner wall-clock speed and JSON stop reasons.
"""
import json
import os
from pathlib import Path
import platform
import sys
from time import perf_counter

if os.name != "nt":
    raise SystemExit("Windows-only native audit.")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from conversation_router import (
    build_native_intent_context, native_intent_context_for_request,
    parse_native_conversation_intent, ConversationRejected,
)
from local_model.native_config import NativeModelConfig
from local_model.memory_preferences import MemoryPreferences
from local_model.native_chat_adapter import NativeChatAdapter
from local_model.native_conversation_session import NativeConversationSession, NativeChatTurn

def main():
    root = Path(sys.argv[1]).resolve(strict=True)
    model = Path(sys.argv[2]).resolve(strict=True)
    config = NativeModelConfig(
        model=str(model), dll=str(root / "koboldcpp_noavx2.dll"),
        context_size=1024, max_output=256, threads=2, batch_threads=2,
        seed=123, temperature=0.1)
    adapter = NativeChatAdapter(root / "koboldcpp.py")
    adapter.prepare(config=config)
    session = NativeConversationSession(
        adapter, config_loader=lambda: config, memory_loader=MemoryPreferences)
    bridge = adapter.provider.bridge
    k = bridge.upstream
    orig_generate = k.generate
    captures = []

    def intercept(arguments):
        start = perf_counter()
        result = orig_generate(arguments)
        elapsed = perf_counter() - start
        h = k.handle
        captures.append(dict(
            native_generate_wall_seconds=round(elapsed, 4),
            prompt_tokens=result.get("prompt_tokens"),
            completion_tokens=result.get("completion_tokens"),
            stopreason=result.get("stopreason"),
            native_last_input_count=h.get_last_input_count(),
            native_last_output_count=h.get_last_token_count(),
            native_raw_process_ms_per_token=h.get_last_process_time(),
            native_raw_eval_ms_per_token=h.get_last_eval_time()))
        return result

    k.generate = intercept
    pairs = [
        ("Parliamo del cielo notturno.", "Le stelle sono corpi luminosi."),
        ("Un oggetto molto massiccio può deformare lo spazio.", "La gravità è collegata alla massa.")
    ]
    rows = []
    # Identical questions and synthetic memory for the old structured route
    # and the 014 informational route, in alternating order.
    tests = (
        ("old_buco_near", "Cos'è un buco nero?", "legacy", True),
        ("new_buco_near", "Cos'è un buco nero?", "014", True),
        ("new_serie_near", "Consigliami una serie TV", "014", True),
        ("old_serie_near", "Consigliami una serie TV", "legacy", True),
        ("new_buco_warm", "Cos'è un buco nero?", "014", True),
        ("old_buco_warm", "Cos'è un buco nero?", "legacy", True),
        ("command_status", "Dimmi come sta il computer", "014", False),
    )
    try:
        for name, question, mode, with_history in tests:
            session.forget_context()
            if with_history:
                for q, a in pairs:
                    if not NativeChatTurn(session, None, q, a, 0).commit():
                        raise RuntimeError("Could not seed synthetic history.")
            if mode == "legacy":
                intent = build_native_intent_context()
            else:
                intent = native_intent_context_for_request(question)
            if mode == "014" and name.startswith("new_") and intent is not None:
                raise RuntimeError("014 informational path did not select chat.")
            before = len(captures)
            start = perf_counter()
            turn = session.prepare_turn(question, intent_context=intent, timeout=180)
            elapsed = perf_counter() - start
            if len(captures) != before + 1:
                raise RuntimeError("Unexpected number of native generations.")
            raw = captures[-1]
            answer = turn.text
            if not answer or len(answer) > 20000:
                raise RuntimeError("Unexpected empty or oversized model answer.")
            parser_kind = None
            parser_error = None
            if turn.allowed_actions is not None:
                try:
                    parsed = parse_native_conversation_intent(answer, utterance=question)
                    parser_kind = parsed.kind
                except ConversationRejected as exc:
                    parser_error = str(exc)
            row = dict(name=name, mode=mode, question=question, text_preview=answer[:240],
                       reply_chars=len(answer), parser_kind=parser_kind,
                       parser_error=parser_error, native=raw,
                       session_wall_seconds=round(elapsed, 4),
                       finish_reason=turn.finish_reason,
                       context=turn.context_metrics)
            rows.append(row)
            if name.startswith("new_"):
                if turn.allowed_actions is not None or turn.accept_action():
                    raise RuntimeError("Chat response was granted action permission.")
                if any(x in answer.casefold() for x in ('"action_id":"system.status"', '"action_id": "system.status"')):
                    row["quality_warning"] = "The model produced action-looking text, but no action was authorized."
            if raw["prompt_tokens"] and (
                    raw["prompt_tokens"] + config.max_output + 128 > config.context_size):
                raise RuntimeError("Exceeded configured context budget.")
            print("JARVIS014_LIVE_CASE=" + json.dumps(row, ensure_ascii=False), flush=True)
        old_buco = next(x for x in rows if x['name']=='old_buco_near')
        new_buco = next(x for x in rows if x['name']=='new_buco_near')
        old_serie = next(x for x in rows if x['name']=='old_serie_near')
        new_serie = next(x for x in rows if x['name']=='new_serie_near')
        if not (new_buco["native"]["prompt_tokens"] < old_buco["native"]["prompt_tokens"]
                and new_serie["native"]["prompt_tokens"] < old_serie["native"]["prompt_tokens"]):
            raise RuntimeError("014 did not reduce actual input tokens for natural chat.")
        if next(x for x in rows if x['name']=='command_status')["parser_kind"] not in (
                "capability","chat","clarify",None):
            raise RuntimeError("Unexpected command schema.")
        report = dict(source_commit=os.environ.get("GITHUB_SHA","unknown"),
                      model_source=json.loads(Path("probe-model-source.json").read_text()),
                      windows_runner=platform.platform(), config={
                          "context_size":1024,"max_output":256,"seed":123,
                          "temperature":0.1,"threads":2,"batch_threads":2},
                      cases=rows, reduction_tokens={
                          "buco":old_buco["native"]["prompt_tokens"]-new_buco["native"]["prompt_tokens"],
                          "serie":old_serie["native"]["prompt_tokens"]-new_serie["native"]["prompt_tokens"]},
                      limitations=["Windows runner != user's i3-2100; never extrapolate wall time.",
                                   "The CI GGUF comes from a verified public source; not verified identical to user's model.",
                                   "One loaded model, sequential tests with caching effects; not an isolated CPU performance benchmark.",
                                   "Model answers are diagnostic samples, not a proof of general conversational coherence.",
                                   "Raw per-token backend averages are not reliable total prefill durations under prefix cache reuse."])
        Path("jarvis014-live-native-report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print("JARVIS014_LIVE_SUMMARY=" + json.dumps({
            "reduction_tokens":report["reduction_tokens"],
            "case_count":len(rows),
            "parser_errors":[x["name"] for x in rows if x["parser_error"]]}, ensure_ascii=False),flush=True)
    finally:
        k.generate = orig_generate
        adapter.stop()

if __name__ == "__main__":
    main()
