"""Windows-only dependency recovery, never an application/package build."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import warnings
import zipfile
import urllib.request


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
                # Same pinned upstream source supplied by checkout in the four
                # workflows; test its real bytes through the helper's ABI guard.
                url = ("https://raw.githubusercontent.com/LostRuins/koboldcpp/"
                       "7e0eb2dc4a23f1a0fc42a7660ad43be7a4b9e759/koboldcpp.py")
                with urllib.request.urlopen(url, timeout=45) as response:
                    upstream = response.read(2 * 1024 * 1024 + 1)
                self.assertLessEqual(len(upstream), 2 * 1024 * 1024)
                self.assertEqual(hashlib.sha256(upstream.replace(b"\r\n", b"\n")).hexdigest(),
                                 "17e234e20c410e770858a58bfe5b3a84f15374e8ed462e2b884faeb653369d96")
                (target / "koboldcpp.py").write_bytes(upstream)
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
            print("NATIVE_ENGINE_REFERENCE_PROBE=" + json.dumps(proof, sort_keys=True))

    def setUp(self):
        # Imports are local to the additional integrity cases: the initial
        # recovery proof remains runnable before the helper is implemented.
        self.temp = self.enterContext(TemporaryDirectory())
        self.root = Path(self.temp)

    def fixture(self, entries=None):
        from tools.native_model import restore_engine as restorer
        self.restorer = restorer
        data = b"verified-native-fixture"
        member = "Jarvis-Gemma/native_engine/koboldcpp_noavx2.dll"
        archive = self.root / "reference.zip"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)  # intentional duplicate fixture
            with zipfile.ZipFile(archive, "w") as output:
                for name, content in (entries if entries is not None else
                                      [(member, data), ("unrelated.txt", b"never extract")]):
                    output.writestr(name, content)
        reference = dict(schema_version=1, repository="MATRIXNEO23/jarvis",
            git_commit="f147b1a5faa977e8e4aefe21c9799465a7a8e990",
            archive_path="Download/reference.zip", archive_bytes=archive.stat().st_size,
            archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
            dll_member=member, dll_bytes=len(data), dll_sha256=hashlib.sha256(data).hexdigest(),
            upstream_commit="7e0eb2dc4a23f1a0fc42a7660ad43be7a4b9e759",
            upstream_python_sha256=hashlib.sha256(b"pass\n").hexdigest())
        return archive, reference, data

    def test_archive_selective_restore_and_idempotent_reuse(self):
        archive, reference, data = self.fixture()
        target = self.root / "engine"
        dll = self.restorer.restore_engine(target, archive=archive, reference=reference)
        self.assertEqual(dll.read_bytes(), data)
        self.assertEqual([p.name for p in target.iterdir()], ["koboldcpp_noavx2.dll"])
        before = (dll.stat().st_ino, dll.stat().st_mtime_ns)
        again = self.restorer.restore_engine(target, archive=archive, reference=reference)
        self.assertTrue(os.path.samefile(dll, again))
        self.assertEqual((dll.stat().st_ino, dll.stat().st_mtime_ns), before)

    def test_corrupt_archive_does_not_touch_existing_files(self):
        archive, reference, _ = self.fixture()
        archive.write_bytes(archive.read_bytes()[:-1] + b"!")
        target = self.root / "engine"
        target.mkdir()
        old = target / "koboldcpp_noavx2.dll"
        old.write_bytes(b"old version must stay")
        saved = target / "user-settings.json"
        saved.write_bytes(b"preserved")
        with self.assertRaises(self.restorer.NativeReferenceError):
            self.restorer.restore_engine(target, archive=archive, reference=reference)
        self.assertEqual(old.read_bytes(), b"old version must stay")
        self.assertEqual(saved.read_bytes(), b"preserved")

    def test_missing_duplicate_wrong_size_or_hash_member_is_rejected(self):
        member = "Jarvis-Gemma/native_engine/koboldcpp_noavx2.dll"
        data = b"verified-native-fixture"
        cases = [[("other.dll", data)], [(member, data), (member, data)],
                 [(member, b"short")], [(member, b"x" * len(data))]]
        for number, entries in enumerate(cases):
            with self.subTest(case=number):
                archive, reference, _ = self.fixture(entries)
                target = self.root / str(number)
                with self.assertRaises(self.restorer.NativeReferenceError):
                    self.restorer.restore_engine(target, archive=archive, reference=reference)
                self.assertFalse((target / "koboldcpp_noavx2.dll").exists())
                self.assertFalse(list(target.glob(".native-engine-*")))

    def test_existing_different_dll_is_never_overwritten(self):
        archive, reference, _ = self.fixture()
        target = self.root / "engine"
        target.mkdir()
        dll = target / "koboldcpp_noavx2.dll"
        dll.write_bytes(b"keep this existing file")
        with self.assertRaises(self.restorer.NativeReferenceError):
            self.restorer.restore_engine(target, archive=archive, reference=reference)
        self.assertEqual(dll.read_bytes(), b"keep this existing file")
        self.assertFalse(list(target.glob(".native-engine-*")))

    def test_upstream_source_identity_accepts_crlf_and_rejects_changed_code(self):
        archive, reference, data = self.fixture()
        for number, source in enumerate((b"pass\r\n", b"different_code()\n")):
            with self.subTest(source=number):
                target = self.root / str(number)
                target.mkdir()
                script = target / "koboldcpp.py"
                script.write_bytes(source)
                if number == 0:
                    result = self.restorer.restore_engine(target, archive=archive, reference=reference)
                    self.assertEqual(result.read_bytes(), data)
                else:
                    with self.assertRaises(self.restorer.NativeReferenceError):
                        self.restorer.restore_engine(target, archive=archive, reference=reference)
                    self.assertFalse((target / "koboldcpp_noavx2.dll").exists())
                self.assertEqual(script.read_bytes(), source)

    def test_download_integrity_failure_leaves_no_dll(self):
        archive, reference, _ = self.fixture()
        valid = archive.read_bytes()
        for number, payload in enumerate((valid[:-1], valid + b"!", b"!" + valid[1:])):
            with self.subTest(payload=number):
                target = self.root / str(number)
                with patch.object(self.restorer.urllib.request, "urlopen",
                                  return_value=io.BytesIO(payload)):
                    with self.assertRaises(self.restorer.NativeReferenceError):
                        self.restorer.restore_engine(target, reference=reference)
                self.assertFalse((target / "koboldcpp_noavx2.dll").exists())

    def test_manifest_rejects_floating_revision_or_unsafe_paths(self):
        _, reference, _ = self.fixture()
        cases = [("git_commit", "main"), ("archive_path", "../reference.zip"),
                 ("dll_member", "../../koboldcpp_noavx2.dll"), ("dll_sha256", "invalid")]
        for key, value in cases:
            with self.subTest(field=key):
                path = self.root / "invalid.json"
                path.write_text(json.dumps({**reference, key: value}), encoding="utf-8")
                with self.assertRaises(self.restorer.NativeReferenceError):
                    self.restorer.load_reference(path)

