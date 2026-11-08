"""F4.2: opt-in, privacy-preserving KoboldCpp/Jarvis performance benchmark.

No runtime Jarvis import. No model or service is started automatically.
'template' and 'compare' work entirely offline. 'probe' reads only local
KoboldCpp, and 'server' sends a SYNTHETIC prompt only when an explicit
--allow-generation flag has been provided. Does not store prompt or output.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import sys
import time

from local_model.kobold_server_canary import KoboldServerCanary, KoboldCanaryError
from local_model.native_provider import format_gemma_messages


class BenchmarkError(ValueError):
    """An invalid or non-comparable measurement (never includes input text)."""


ENGINES = frozenset((
    "kobold-original", "jarvis-console-brain-on",
    "jarvis-console-brain-off", "jarvis-chat-isolated",
))
SCENARIOS = frozenset(("prima", "approfondimento"))
CACHE_STATES = frozenset(("cold", "warm", "unknown"))

_FIELDS = frozenset((
    "engine", "scenario", "model", "context_size", "max_output",
    "threads", "blas_threads", "sampler", "cache_state",
    "prompt_sha256", "prompt_tokens", "processed_tokens",
    "generated_tokens", "process_seconds", "generation_seconds",
    "total_seconds", "ram_mb", "quality_ok",
    "perf_last_token_count_raw",
))
_REQUIRED = _FIELDS - {"perf_last_token_count_raw"}
_FINGERPRINT = re.compile(r"[a-f0-9]{64}\Z")


def _template_row(engine, scenario):
    return {
        "engine": engine, "scenario": scenario,
        "model": "INSERISCI_ID_GGUF",
        "context_size": 1024, "max_output": 256,
        "threads": 2, "blas_threads": 2,
        "sampler": "unknown", "cache_state": "unknown",
        "prompt_sha256": None,
        "prompt_tokens": None, "processed_tokens": None,
        "generated_tokens": None,
        "process_seconds": None, "generation_seconds": None,
        "total_seconds": None, "ram_mb": None, "quality_ok": None,
    }


def make_template():
    """Printable, empty observation sheet; never contains a real prompt."""
    return {
        "version": 1,
        "measurements": [
            _template_row("kobold-original", "prima"),
            _template_row("jarvis-console-brain-off", "prima"),
            _template_row("jarvis-console-brain-on", "prima"),
            _template_row("jarvis-chat-isolated", "prima"),
        ],
    }


EXAMPLE = make_template()


def _num(value, *, allow_none=False, positive=False, integer=False):
    if allow_none and value is None:
        return
    if integer:
        if type(value) is not int:
            raise BenchmarkError("Contatore numerico non valido.")
    else:
        if type(value) not in (int, float) or not math.isfinite(value):
            raise BenchmarkError("Misurazione numerica non valida.")
    if (positive and value <= 0) or (not positive and value < 0):
        raise BenchmarkError("Misurazione fuori intervallo.")


def validate_measurement(value):
    """Reject unexpected fields so prompts, answers and secrets cannot leak."""
    if type(value) is not dict or not _REQUIRED.issubset(value) or (
            value.keys() - _FIELDS):
        raise BenchmarkError(
            "Schema benchmark non valido. Inserire solo i campi previsti.")
    result = dict(value)
    if result["engine"] not in ENGINES or result["scenario"] not in SCENARIOS:
        raise BenchmarkError("Motore o scenario non consentito.")
    for name in ("model", "sampler"):
        v = result[name]
        if type(v) is not str or not 1 <= len(v) <= 128 or (
                any(ord(ch) < 32 for ch in v)):
            raise BenchmarkError("Configurazione modello non valida.")
    if result["cache_state"] not in CACHE_STATES:
        raise BenchmarkError("Stato cache non valido.")
    for key in ("context_size", "max_output", "threads", "blas_threads"):
        _num(result[key], integer=True, positive=True)
    if result["max_output"] >= result["context_size"]:
        raise BenchmarkError("Budget context/output non valido.")
    digest = result["prompt_sha256"]
    if digest is not None and (
            type(digest) is not str or not _FINGERPRINT.fullmatch(digest)):
        raise BenchmarkError("Impronta prompt non valida.")
    for key in ("prompt_tokens", "processed_tokens", "generated_tokens",
                "perf_last_token_count_raw"):
        if key in result:
            _num(result[key], allow_none=True, integer=True)
    for key in ("process_seconds", "generation_seconds", "ram_mb"):
        _num(result[key], allow_none=True)
    _num(result["total_seconds"], positive=True)
    if result["quality_ok"] is not None and type(result["quality_ok"]) is not bool:
        raise BenchmarkError("Qualita risposta non valida.")
    return result


def _rate(tokens, seconds):
    if tokens is None or seconds is None or seconds <= 0:
        return None
    return round(tokens / seconds, 3)


def analyze(dataset):
    """Compare without inventing token counts or assuming equivalent prompts."""
    if type(dataset) is not dict or set(dataset) != {"version", "measurements"}:
        raise BenchmarkError("Documento benchmark non valido.")
    if type(dataset["version"]) is not int or dataset["version"] != 1:
        raise BenchmarkError("Versione benchmark non supportata.")
    rows = dataset["measurements"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= 100:
        raise BenchmarkError("Numero misurazioni fuori intervallo.")
    validated = [validate_measurement(v) for v in rows]
    output = []
    for item in validated:
        metrics = dict(item)
        metrics["processed_tps"] = _rate(
            item["processed_tokens"], item["process_seconds"])
        metrics["generated_tps"] = _rate(
            item["generated_tokens"], item["generation_seconds"])
        output.append(metrics)
    comparisons = []
    for left, right in itertools.combinations(validated, 2):
        if left["engine"] == right["engine"] or (
                left["scenario"] != right["scenario"]):
            continue
        reasons = []
        for key in ("model", "context_size", "max_output",
                    "threads", "blas_threads", "cache_state"):
            if left[key] != right[key]:
                reasons.append(key)
        if (left["sampler"] == "unknown" or right["sampler"] == "unknown"
                or left["sampler"] != right["sampler"]):
            reasons.append("sampler")
        if (not left["prompt_sha256"] or not right["prompt_sha256"]
                or left["prompt_sha256"] != right["prompt_sha256"]):
            reasons.append("prompt")
        if left["quality_ok"] is not True or right["quality_ok"] is not True:
            reasons.append("qualita")
        comparisons.append({
            "engines": [left["engine"], right["engine"]],
            "scenario": left["scenario"],
            "controlled": not reasons,
            "reasons": reasons,
            "time_ratio": round(
                left["total_seconds"] / right["total_seconds"], 3),
        })
    return {"rows": output, "comparisons": comparisons}


_USER_FIRST = "Spiega in due frasi che cos'è un buco nero."
_USER_FOLLOWUP = (
    "Approfondisci la spiegazione precedente in tre frasi senza ripeterla."
)


def _synthetic_prompt(scenario, *, prior_answer=None):
    if scenario not in SCENARIOS:
        raise BenchmarkError("Scenario benchmark non consentito.")
    msgs = [{"role": "user", "content": _USER_FIRST}]
    if scenario == "approfondimento":
        if type(prior_answer) is not str or not prior_answer.strip():
            raise BenchmarkError("Manca la risposta precedente per il follow-up.")
        msgs.extend([
            {"role": "assistant", "content": prior_answer},
            {"role": "user", "content": _USER_FOLLOWUP},
        ])
    return format_gemma_messages(msgs)


def _perf_number(data, key, *, integer=False):
    if not isinstance(data, dict):
        return None
    x = data.get(key)
    if type(x) not in ((int,) if integer else (int, float)):
        return None
    if not integer and not math.isfinite(x):
        return None
    if x < 0:
        return None
    return x


def run_server_trial(canary, *, expected_model, scenario="prima",
                     clock=time.perf_counter, prior_answer=None,
                     answer_sink=None):
    """One explicit synthetic generation; return metrics ONLY, never text.

    /api/extra/perf last_token_count is kept RAW because its interpretation
    can vary. Never claim it is "processed_tokens" or "generated_tokens".
    """
    prompt = _synthetic_prompt(scenario, prior_answer=prior_answer)
    model = canary.probe()
    if model != expected_model:
        raise BenchmarkError("Modello del server diverso: prova annullata.")
    before = canary.perf()
    queue = _perf_number(before, "queue", integer=True)
    if queue is not None and queue > 0:
        raise BenchmarkError("Server occupato: misura non confrontabile.")
    initial = _perf_number(before, "total_gens", integer=True)
    start = clock()
    answer = canary.generate(
        prompt, expected_model=expected_model,
        max_context_length=1024, max_length=256,
        stop_sequence=("<end_of_turn>",), timeout=240)
    end = clock()
    after = canary.perf()
    final = _perf_number(after, "total_gens", integer=True)
    if initial is not None and final is not None and final != initial + 1:
        raise BenchmarkError(
            "Un'altra generazione potrebbe avere alterato i dati di prestazione.")
    if answer_sink is not None:
        answer_sink.append(answer)
    result = {
        "engine": "kobold-original",
        "scenario": scenario,
        "model": expected_model,
        "context_size": 1024, "max_output": 256,
        "threads": 2, "blas_threads": 2,
        # Must be filled from the actual KoboldCpp launcher configuration
        # before making a quality/speed claim against Jarvis.
        "sampler": "unknown",
        "cache_state": "unknown",
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "prompt_tokens": None,
        "processed_tokens": None,
        "generated_tokens": None,
        "process_seconds": _perf_number(after, "last_process"),
        "generation_seconds": _perf_number(after, "last_eval"),
        "total_seconds": round(end - start, 3),
        "ram_mb": None,
        "quality_ok": None,
        "perf_last_token_count_raw": _perf_number(
            after, "last_token_count", integer=True),
    }
    # The server may omit native timings. Missing values stay null.
    return validate_measurement(result)


def _format_summary(report):
    lines = [
        "F4.2 — Misure senza prompt o risposte",
        "Motore | Scenario | Totale(s) | Process(tok/s) | Genera(tok/s)",
    ]
    for row in report["rows"]:
        def show(x):
            return "n.d." if x is None else str(x)
        lines.append(
            row["engine"] + " | " + row["scenario"]
            + " | " + show(row["total_seconds"])
            + " | " + show(row["processed_tps"])
            + " | " + show(row["generated_tps"]))
    lines.append("Comparabilita: condizioni equivalenti SOLO se tutte verificate.")
    for c in report["comparisons"]:
        label = ("CONTROLLED" if c["controlled"]
                 else "NON CONFRONTABILE: " + ",".join(c["reasons"]))
        lines.append(c["engines"][0] + " vs " + c["engines"][1]
                     + " | " + c["scenario"] + " | " + label
                     + " | rapporto tempi: " + str(c["time_ratio"]))
    if not report["comparisons"]:
        lines.append("Nessun confronto fra due motori nello stesso scenario.")
    return "\n".join(lines)


def _read_dataset(path):
    try:
        p = Path(path)
        if p.stat().st_size > 256000:
            raise BenchmarkError("File misurazioni troppo grande.")
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        if isinstance(exc, BenchmarkError):
            raise
        raise BenchmarkError("Impossibile leggere il file misurazioni.") from None


def _write_exclusive(path, payload):
    try:
        with Path(path).open("x", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    except OSError:
        raise BenchmarkError(
            "File di destinazione non disponibile o gia esistente.") from None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="F4.2: confronto locale Gemma senza dati privati")
    cmd = parser.add_subparsers(dest="command", required=True)
    cmd.add_parser("template", help="Stampa schema JSON senza dati personali")
    p_compare = cmd.add_parser("compare", help="Analizza misure JSON raccolte")
    p_compare.add_argument("file")
    p_probe = cmd.add_parser("probe", help="Sola lettura del server locale")
    p_probe.add_argument("--url", default="http://127.0.0.1:5001")
    p_run = cmd.add_parser(
        "server", help="Una o due generazioni SINTETICHE sul server LOCALE")
    p_run.add_argument("--url", default="http://127.0.0.1:5001")
    p_run.add_argument("--model", required=True,
                       help="Nome esatto restituito dal comando probe")
    p_run.add_argument("--allow-generation", required=True, action="store_true",
                       help="Confermo invio prompt sintetico al server locale")
    p_run.add_argument("--turns", type=int, choices=(1, 2), default=1)
    p_run.add_argument("--output", default=None,
                       help="Salva SOLO metriche JSON, mai testi; non sovrascrive")
    args = parser.parse_args(argv)
    try:
        if args.command == "template":
            print(json.dumps(make_template(), indent=2, ensure_ascii=False))
            return 0
        if args.command == "compare":
            print(_format_summary(analyze(_read_dataset(args.file))))
            return 0
        canary = KoboldServerCanary(args.url)
        if args.command == "probe":
            print("Modello locale: " + canary.probe())
            print("Nessuna generazione eseguita.")
            return 0
        rows = []
        answers = []
        rows.append(run_server_trial(
            canary, expected_model=args.model, answer_sink=answers))
        if args.turns == 2:
            rows.append(run_server_trial(
                canary, expected_model=args.model, scenario="approfondimento",
                prior_answer=answers[0]))
        # Never include the answers in the result, nor print them.
        dataset = {"version": 1, "measurements": rows}
        if args.output:
            _write_exclusive(args.output, dataset)
        print(_format_summary(analyze(dataset)))
        print("Conteggi /perf last_token_count lasciati RAW, non confusi con "
              "token Processed/Generated.")
        return 0
    except (BenchmarkError, KoboldCanaryError):
        print("Prova non eseguita o misure non valide. Nessun dato privato stampato.",
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
