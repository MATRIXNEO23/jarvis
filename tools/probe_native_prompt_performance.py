"""Windows-only audit of the unmodified production native conversation path.

Synthetic fixtures only. No UI, account, actions, archive I/O or shipped policy
changes. Timings are nested: selection includes some tokenizer work, and native
generation includes its own tokenization. Do not add all reported durations.
"""
import json
import os
from pathlib import Path
import platform
import sys
from time import perf_counter

if os.name != "nt":
    raise SystemExit("Windows-only native performance audit.")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from conversation_router import build_native_intent_context
from local_model import context_window
from local_model.memory_preferences import MemoryPreferences
from local_model.native_chat_adapter import NativeChatAdapter
from local_model.native_config import NativeModelConfig
from local_model.native_conversation_session import NativeChatTurn, NativeConversationSession


def main():
    root = Path(sys.argv[1]).resolve()
    config = NativeModelConfig(
        model=str(Path(sys.argv[2]).resolve(strict=True)),
        dll=str(root / "koboldcpp_noavx2.dll"), context_size=1024,
        max_output=128, threads=2, batch_threads=2, seed=123, temperature=0.1)
    adapter = NativeChatAdapter(root / "koboldcpp.py")
    adapter.prepare(config=config)
    k = adapter.provider.bridge.upstream
    original_load, original_generate = k.load_model, k.generate
    original_tokenize = k.tokenize_ids
    original_select = context_window.select_recent_pairs
    current = None
    generating = False
    previous_prompt = None
    total_loads = 0

    def load(model):
        nonlocal total_loads
        total_loads += 1
        started = perf_counter()
        try:
            return original_load(model)
        finally:
            current["model_loads"] += 1
            current["model_load_seconds"] += perf_counter() - started

    def tokenize(prompt, special):
        started = perf_counter()
        try:
            return original_tokenize(prompt, special)
        finally:
            phase = "during_generate" if generating else "before_generate"
            row = current["tokenizer"][phase]
            row["calls"] += 1
            row["seconds"] += perf_counter() - started

    def select(*args, **kwargs):
        current["selection_during_generate"] += int(generating)
        started = perf_counter()
        try:
            return original_select(*args, **kwargs)
        finally:
            current["selection_seconds_including_counts"] += perf_counter() - started

    def generate(arguments):
        nonlocal generating, previous_prompt
        if generating:
            raise RuntimeError("Unexpected concurrent native generation.")
        generating = True
        current["generations"] += 1
        started = perf_counter()
        try:
            result = original_generate(arguments)
        finally:
            current["native_generate_seconds"] = perf_counter() - started
            generating = False
        current["prompt_tokens"] = result["prompt_tokens"]
        current["completion_tokens"] = result["completion_tokens"]
        # Use the pinned upstream's /api/extra/perf conversion. This is native
        # telemetry, not an assertion that all input tokens were reprocessed.
        h = k.handle
        inputs, outputs = h.get_last_input_count(), h.get_last_token_count()
        current["backend"] = dict(
            last_input_count=inputs, last_token_count=outputs,
            process_seconds=h.get_last_process_time() * inputs * 0.001,
            eval_seconds=h.get_last_eval_time() * outputs * 0.001)
        # Analysis tokenization is explicitly excluded from the request timing
        # and tokenizer counters; performed only after the production call.
        current["_prompt"] = arguments["prompt"]
        return result

    k.load_model, k.generate, k.tokenize_ids = load, generate, tokenize
    context_window.select_recent_pairs = select
    catalog = build_native_intent_context()
    fixtures = [
        ("Sto riordinando il magazzino: da dove comincio?",
         "Comincia dagli scaffali a sinistra. Separa gli utensili dai documenti, "
         "conserva le etichette e lascia libero il passaggio davanti alla porta. "
         "Puoi preparare tre scatole distinte e controllare il contenuto prima di spostarle."),
        ("La scatola blu contiene documenti, quella rossa gli utensili.",
         "Tieni la scatola blu sullo scaffale alto e la rossa vicino al banco. "
         "Scrivi sulle etichette cosa contengono, così ritroverai tutto senza aprirle. "
         "I documenti devono rimanere asciutti e separati dagli oggetti da lavoro."),
        ("Ho messo la scatola blu sopra il banco. Cosa faccio dopo?",
         "Controlla prima la scatola blu dei documenti sopra il banco. "
         "Dividi le fatture dalle istruzioni, mantieni l’ordine delle date e "
         "prepara una cartellina per ogni gruppo. Alla fine rimettila sullo scaffale alto.")]
    question = "Di quale scatola stiamo parlando? Rispondi con una sola frase."
    rows = []
    session = NativeConversationSession(
        adapter, config_loader=lambda: config, memory_loader=MemoryPreferences)

    def run(name, history, *, intent=catalog, recall=None):
        nonlocal current, previous_prompt
        # Keep the real session/provider warm. Only reset synthetic RAM history;
        # never clear or reload the native engine/cache between audit cases.
        session.forget_context()
        # Accepted synthetic fixtures use the production commit path. We do not
        # accept generated answers, so repeated cases have identical inputs.
        for user, answer in history:
            if not NativeChatTurn(session, None, user, answer, 0).commit():
                raise RuntimeError("Could not seed synthetic history.")
        current = dict(case=name, model_loads=0, model_load_seconds=0,
                       generations=0, selection_during_generate=0,
                       selection_seconds_including_counts=0, memory_read_seconds=0,
                       tokenizer={phase: dict(calls=0, seconds=0)
                                  for phase in ("before_generate", "during_generate")})

        def reader(budget):
            started = perf_counter()
            try:
                return recall[:budget]
            finally:
                current["memory_read_seconds"] += perf_counter() - started

        started = perf_counter()
        turn = session.prepare_turn(question, intent_context=intent,
                                    memory_context=reader if recall is not None else None)
        current["prepare_turn_seconds"] = perf_counter() - started
        current["context"] = turn.context_metrics
        prompt = current.pop("_prompt")
        tokens = original_tokenize(prompt, True)
        prefix = 0
        if previous_prompt is not None:
            for left, right in zip(previous_prompt, tokens):
                if left != right:
                    break
                prefix += 1
        current["common_prefix_with_previous_request_tokens"] = prefix
        current["identical_to_previous_request"] = previous_prompt == tokens
        previous_prompt = tokens
        if (current["generations"] != 1 or current["selection_during_generate"]
                or len(tokens) != current["prompt_tokens"]
                or len(tokens) != turn.context_metrics["input_size"]
                or len(tokens) + config.max_output + 128 > config.context_size):
            raise RuntimeError("Production inference count, phase or budget mismatch.")
        rows.append(current)
        print("NATIVE_PROMPT_PERFORMANCE_CASE=" + json.dumps(current), flush=True)

    try:
        run("catalog_three_pairs_cold", fixtures)
        run("catalog_three_pairs_identical_warm", fixtures)
        run("catalog_latest_pair_warm", fixtures[-1:])
        run("plain_latest_pair_control_warm", fixtures[-1:], intent=None)
        run("archive_A_warm", fixtures[-1:], recall='{"project":"magazzino A"}')
        run("archive_A_identical_warm", fixtures[-1:], recall='{"project":"magazzino A"}')
        run("archive_B_warm", fixtures[-1:], recall='{"project":"magazzino B"}')
        run("oversized_latest_pair_warm", [(fixtures[-1][0], fixtures[-1][1] * 20)])
        if total_loads != 1 or not rows[1]["identical_to_previous_request"]:
            raise RuntimeError("Unexpected reload or unstable identical fixture.")
        if not rows[-1]["context"].get("extracted"):
            raise RuntimeError("Oversized fixture did not exercise extraction.")
        report = dict(audit="Jarvis_012_native_prompt_performance", cases=rows,
                      model_loads=total_loads, platform=platform.platform(),
                      source_commit=os.environ.get("AUDIT_SOURCE_SHA", "unspecified"),
                      model_source=json.loads(Path("probe-model-source.json").read_text()),
                      limits=["Windows runner is not Pavilion; no extrapolated latency.",
                              "Native path only; no Telegram queue, DB/fsync, UI or TTS.",
                              "Nested timings must not be added.",
                              "Fixed order, synthetic uncommitted repetitions; not a dialogue quality test."])
        Path("native-prompt-performance-report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print("NATIVE_PROMPT_PERFORMANCE=" + json.dumps(report), flush=True)
    finally:
        k.load_model, k.generate, k.tokenize_ids = original_load, original_generate, original_tokenize
        context_window.select_recent_pairs = original_select
        adapter.stop()


if __name__ == "__main__":
    main()
