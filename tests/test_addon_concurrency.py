"""Windows lock-order regression with real lifecycle, service and disk records.

Each probe has its own process: a reproduced deadlock cannot hang the suite.
Events pause existing callback boundaries; locks/permission checks stay real.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import threading
import unittest


def lifecycle_probe(root: Path, operation: str) -> dict:
    from addon_manager import AddonManager
    from live_capabilities import LiveCapabilityRegistry

    manager = AddonManager(LiveCapabilityRegistry(), root / "addons")
    source = Path("file_access/AccessoFile.jaddon")
    manager.install(source)
    files = manager.file_service
    folder = root / "allowed"
    folder.mkdir()
    sample = folder / "note.txt"
    sample.write_text("Testo da conservare", encoding="utf-8")
    files.policy.configure([(folder, True)])
    manager.set_enabled("accesso_file", True)
    initial = files.execute("request_target", {"operation": "search"})
    if initial.status != "completed" or files.pending_clarification() != ("request", None):
        raise AssertionError("The real unanswered file request was not established")
    old_token = files._result_token

    permission_entered = threading.Event()
    reset_entered = threading.Event()
    errors = []
    observations = []
    enabled = files.enabled
    reset = files.reset

    def paused_enabled(operation=None):
        if threading.current_thread() is reader:
            permission_entered.set()
            if not reset_entered.wait(5):
                raise AssertionError("Lifecycle did not reach service reset")
        return enabled(operation)

    def observed_reset(*args, **kwargs):
        reset_entered.set()
        return reset(*args, **kwargs)

    files.enabled = paused_enabled
    files.reset = observed_reset

    def read_pending():
        try:
            observations.append(files.pending_clarification())
        except Exception as exc:
            errors.append("reader: " + type(exc).__name__ + ": " + str(exc))

    def change_lifecycle():
        try:
            if not permission_entered.wait(5):
                raise AssertionError("File reader did not reach permission callback")
            if operation == "disable":
                manager.set_enabled("accesso_file", False)
            elif operation == "remove":
                manager.remove("accesso_file")
            elif operation == "upgrade":
                manifest = json.loads(source.read_text(encoding="utf-8"))
                manifest["version"] = "0.2.0"
                package = root / "upgrade.jaddon"
                package.write_text(json.dumps(manifest), encoding="utf-8")
                manager.install(package)
            elif operation == "revoke_approval":
                manager._consent_path.unlink()
                manager.refresh()
            else:
                raise AssertionError("Unknown probe operation")
        except Exception as exc:
            errors.append("lifecycle: " + type(exc).__name__ + ": " + str(exc))

    reader = threading.Thread(target=read_pending, daemon=True)
    changer = threading.Thread(target=change_lifecycle, daemon=True)
    reader.start()
    changer.start()
    reader.join(3)
    changer.join(3)
    completed = not reader.is_alive() and not changer.is_alive()
    report = dict(completed=completed, reader_alive=reader.is_alive(),
                  lifecycle_alive=changer.is_alive(), errors=errors,
                  permission_entered=permission_entered.is_set(),
                  reset_entered=reset_entered.is_set())
    if completed and not errors:
        report.update(
            observations=observations,
            enabled=manager.files_enabled(),
            pending=files.pending_clarification(),
            cancelled=files.cancelled.is_set(),
            token_revoked=files._result_token != old_token,
            records=manager.list_installed(),
            stale_read_status=files.execute("read", {"target": "1"}).status,
            data=sample.read_text(encoding="utf-8"),
        )
        if operation != "remove":
            manager.set_enabled("accesso_file", True)
            report.update(reenabled=manager.files_enabled(),
                          pending_after_reenable=files.pending_clarification(),
                          stale_after_reenable=files.execute("read", {"target": "1"}).status)
    return report


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class AddonConcurrencyTests(unittest.TestCase):
    def test_file_clarification_and_lifecycle_finish_without_deadlock(self):
        for operation in ("disable", "remove", "upgrade", "revoke_approval"):
            with self.subTest(operation=operation), TemporaryDirectory() as tmp:
                command = [sys.executable, str(Path(__file__).resolve()),
                           "--probe", tmp, operation]
                completed = subprocess.run(command, capture_output=True, text=True,
                                           encoding="utf-8", timeout=20, check=False)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                report = json.loads(completed.stdout)
                self.assertTrue(report["permission_entered"], report)
                self.assertTrue(report["reset_entered"], report)
                self.assertEqual(report["errors"], [], report)
                self.assertTrue(report["completed"], report)
                self.assertEqual(report["observations"], [None])
                self.assertFalse(report["enabled"])
                self.assertIsNone(report["pending"])
                self.assertTrue(report["cancelled"])
                self.assertTrue(report["token_revoked"])
                self.assertEqual(report["stale_read_status"], "rejected")
                self.assertEqual(report["data"], "Testo da conservare")
                if operation == "remove":
                    self.assertEqual(report["records"], [])
                else:
                    self.assertFalse(report["records"][0]["enabled"])
                    self.assertTrue(report["reenabled"])
                    self.assertIsNone(report["pending_after_reenable"])
                    self.assertEqual(report["stale_after_reenable"], "rejected")
                if operation == "upgrade":
                    self.assertEqual(report["records"][0]["version"], "0.2.0")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--probe":
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        print(json.dumps(lifecycle_probe(Path(sys.argv[2]), sys.argv[3])), flush=True)
    else:
        unittest.main()
