"""Windows-only dependency recovery, never an application/package build."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


REPO = Path(__file__).resolve().parents[1]
DLL_SHA256 = "ac834f409855bd7e12a0f0c0ffc8601a663b036b2403d74af4b6b3d3afd49bba"


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class NativeEngineReferenceTests(unittest.TestCase):
    def test_clean_dependency_recovery_without_actions_artifact(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "upstream-kobold"
            target.mkdir()
            helper = REPO / "tools/native_model/restore_engine.py"
            # Baseline has no self-contained acquisition path. Leave its
            # clean destination untouched to expose that missing capability;
            # do not fake an expired API response or claim today's build fails.
            if helper.is_file():
                env = dict(os.environ)
                env.pop("ACTIONS_RUNTIME_TOKEN", None)
                result = subprocess.run(
                    [sys.executable, str(helper), "--destination", str(target)],
                    cwd=REPO, env=env, capture_output=True, text=True,
                    encoding="utf-8", timeout=180, check=False)
                self.assertEqual(result.returncode, 0, result.stderr)
            dll = target / "koboldcpp_noavx2.dll"
            self.assertTrue(dll.is_file(),
                            "Clean checkout cannot recover the pinned DLL without the temporary Actions artifact")
            self.assertEqual(dll.stat().st_size, 19_010_560)
            self.assertEqual(hashlib.sha256(dll.read_bytes()).hexdigest(), DLL_SHA256)
            # Existing native probe loads/calls exports only, no GGUF or server.
            result = subprocess.run(
                [sys.executable, str(REPO / "tools/native_model/probe.py"), str(dll)],
                cwd=REPO, capture_output=True, text=True, encoding="utf-8",
                timeout=30, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            proof = json.loads(result.stdout)
            self.assertEqual(proof["sha256"], DLL_SHA256)
            self.assertEqual(proof["initial_token_count"], 0)
            self.assertFalse(proof["inference_verified"])

