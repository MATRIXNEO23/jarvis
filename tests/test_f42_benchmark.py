"""F4.2 RED: benchmark data must be honest, private and manually gated."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from io import StringIO

from tools.f42_benchmark import (
    EXAMPLE, BenchmarkError, analyze, make_template, run_server_trial, main,
    validate_measurement,
)


def row(**updates):
    base = {
        "engine": "kobold-original",
        "scenario": "prima",
        "model": "gemma2-2b-it-Q4_K_M.gguf",
        "context_size": 1024, "max_output": 256,
        "threads": 2, "blas_threads": 2,
        "sampler": "standard-t0.7",
        "cache_state": "cold",
        "prompt_sha256": "a" * 64,
        "prompt_tokens": 300, "processed_tokens": 300,
        "generated_tokens": 50,
        "process_seconds": 30.0, "generation_seconds": 12.0,
        "total_seconds": 43.0,
        "ram_mb": 2200.0, "quality_ok": True,
    }
    base.update(updates)
    return base


class BenchmarkDataTests(unittest.TestCase):
    def test_template_contains_no_prompt_or_real_private_data(self):
        example = make_template()
        self.assertEqual(example["version"], 1)
        self.assertEqual(len(example["measurements"]), 4)
        self.assertTrue(all(item["prompt_sha256"] is None
                            for item in example["measurements"]))
        self.assertNotIn("prompt_text", json.dumps(example))
        self.assertNotIn("answer", json.dumps(example))
        self.assertTrue(all(item["quality_ok"] is None
                            for item in example["measurements"]))

    def test_reject_prompts_and_extra_fields_without_repeating_secret(self):
        for extra in [{"prompt": "MY_PRIVATE_SECRET"},
                      {"response": "MY_PRIVATE_SECRET"},
                      {"api_key": "MY_PRIVATE_SECRET"}]:
            with self.subTest(extra=list(extra)):
                bad = row(**extra)
                with self.assertRaises(BenchmarkError) as error:
                    validate_measurement(bad)
                self.assertNotIn("MY_PRIVATE_SECRET", str(error.exception))

    def test_invalid_metrics_and_fingerprint_rejected(self):
        variants = [
            {"engine": "other"},
            {"scenario": "other"},
            {"total_seconds": -1},
            {"total_seconds": True},
            {"processed_tokens": -1},
            {"generation_seconds": float("nan")},
            {"ram_mb": -4},
            {"prompt_sha256": "xyz"},
            {"threads": 0},
            {"cache_state": "maybe"},
            {"quality_ok": "yes"},
        ]
        for variant in variants:
            with self.subTest(variant=variant):
                with self.assertRaises(BenchmarkError):
                    validate_measurement(row(**variant))

    def test_processing_and_generation_rates_are_independent(self):
        result = analyze({"version": 1, "measurements": [row()]})
        stats = result["rows"][0]
        self.assertAlmostEqual(stats["processed_tps"], 10.0)
        self.assertAlmostEqual(stats["generated_tps"], 50 / 12)
        self.assertEqual(stats["total_seconds"], 43.0)
        self.assertIsNone(stats.get("relative_speedup"))

    def test_nonmatching_prompt_and_sampler_are_inconclusive(self):
        a = row(engine="kobold-original")
        b = row(engine="jarvis-console-brain-off",
                prompt_sha256="b" * 64, sampler="different",
                total_seconds=70.0)
        result = analyze({"version": 1, "measurements": [a, b]})
        self.assertEqual(len(result["comparisons"]), 1)
        self.assertFalse(result["comparisons"][0]["controlled"])
        self.assertIn("prompt", result["comparisons"][0]["reasons"])
        self.assertIn("sampler", result["comparisons"][0]["reasons"])

    def test_complete_matches_allow_controlled_comparison_but_require_quality(self):
        a = row(engine="kobold-original", total_seconds=35.0)
        b = row(engine="jarvis-console-brain-off", total_seconds=70.0)
        report = analyze({"version": 1, "measurements": [a, b]})
        self.assertTrue(report["comparisons"][0]["controlled"])
        self.assertAlmostEqual(report["comparisons"][0]["time_ratio"], 2.0)
        report = analyze({"version": 1, "measurements": [a, dict(b, quality_ok=None)]})
        self.assertFalse(report["comparisons"][0]["controlled"])
        self.assertIn("qualita", report["comparisons"][0]["reasons"])

    def test_missing_and_unavailable_metrics_never_become_fake_numbers(self):
        a = row(engine="kobold-original", prompt_tokens=None,
                processed_tokens=None, process_seconds=None,
                generated_tokens=None, generation_seconds=None, ram_mb=None,
                prompt_sha256=None)
        result = analyze({"version": 1, "measurements": [a]})
        self.assertIsNone(result["rows"][0]["processed_tps"])
        self.assertIsNone(result["rows"][0]["generated_tps"])
        self.assertIsNone(result["rows"][0]["prompt_sha256"])


class FakeCanary:
    def __init__(self, *, total_gens=(7, 8), queue=0):
        self.calls = []
        self.gens = list(total_gens)
        self.queue = queue

    def probe(self):
        self.calls.append(("probe",))
        return "Gemma2"

    def perf(self):
        self.calls.append(("perf",))
        return {
            "total_gens": self.gens.pop(0),
            "queue": self.queue,
            "last_process": 8.1,
            "last_eval": 5.1,
            "last_token_count": 70,
        }

    def generate(self, prompt, **kwargs):
        self.calls.append(("generate", len(prompt), kwargs))
        return "Testo generato, mai memorizzato."


class BenchmarkRunnerTests(unittest.TestCase):
    def test_server_runner_uses_only_synthetic_prompts_and_retains_no_text(self):
        canary = FakeCanary()
        ticks = iter([100.0, 114.2])
        result = run_server_trial(
            canary, expected_model="Gemma2",
            clock=lambda: next(ticks), scenario="prima")
        self.assertEqual(result["total_seconds"], 14.2)
        self.assertEqual(result["process_seconds"], 8.1)
        self.assertEqual(result["generation_seconds"], 5.1)
        self.assertIsNone(result["processed_tokens"])
        self.assertIsNone(result["generated_tokens"])
        self.assertEqual(result["perf_last_token_count_raw"], 70)
        self.assertEqual(result["engine"], "kobold-original")
        self.assertTrue(result["prompt_sha256"])
        self.assertNotIn("Testo generato", json.dumps(result))
        self.assertEqual(
            [call[0] for call in canary.calls],
            ["probe", "perf", "generate", "perf"])

    def test_busy_or_other_generation_invalidates_benchmark(self):
        for canary in [FakeCanary(queue=1), FakeCanary(total_gens=(3, 6))]:
            with self.subTest(case=canary.gens):
                with self.assertRaises(BenchmarkError):
                    run_server_trial(
                        canary, expected_model="Gemma2",
                        clock=lambda: 10, scenario="prima")

    def test_model_mismatch_prevents_generation(self):
        canary = FakeCanary()
        with self.assertRaises(BenchmarkError):
            run_server_trial(
                canary, expected_model="Another",
                clock=lambda: 10, scenario="prima")
        self.assertNotIn("generate", [x[0] for x in canary.calls])

    def test_cli_template_and_compare_do_not_connect(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "measurements.json"
            p.write_text(json.dumps({"version": 1, "measurements": [
                row(), row(engine="jarvis-console-brain-off", total_seconds=52)]}),
                encoding="utf-8")
            with patch("sys.stdout", new_callable=StringIO) as output:
                self.assertEqual(main(["template"]), 0)
                self.assertIn('"version": 1', output.getvalue())
            with patch("sys.stdout", new_callable=StringIO) as output:
                self.assertEqual(main(["compare", str(p)]), 0)
                self.assertIn("Comparabilita", output.getvalue())

    def test_cli_run_requires_explicit_flag_and_does_not_connect(self):
        with patch("tools.f42_benchmark.KoboldServerCanary") as factory:
            with self.assertRaises(SystemExit):
                main(["server", "--model", "Gemma2"])
            factory.assert_not_called()

    def test_no_output_file_without_explicit_user_path(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "private.json"
            with patch("tools.f42_benchmark.KoboldServerCanary") as factory:
                factory.return_value = FakeCanary()
                ticks = iter([10, 20])
                with patch("tools.f42_benchmark.time.perf_counter",
                           side_effect=lambda: next(ticks)):
                    with patch("sys.stdout", new_callable=StringIO):
                        self.assertEqual(
                            main(["server", "--model", "Gemma2",
                                  "--allow-generation"]), 0)
            self.assertFalse(p.exists())


if __name__ == "__main__":
    unittest.main()
