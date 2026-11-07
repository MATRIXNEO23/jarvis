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


def transition_probe(manager, files, operation):
    """Bounded reenable/reset and uncommitted-permission scenarios."""
    entered = threading.Event()
    release = threading.Event()
    peer_started = threading.Event()
    errors = []
    values = {}
    reset = files.reset
    save = manager._save

    def delayed_reset(*args, **kwargs):
        if threading.current_thread() is disabler:
            entered.set()
            if not release.wait(8):
                raise AssertionError("Reset gate not released")
        return reset(*args, **kwargs)

    def paused_save(ident, record):
        if not record["enabled"]:
            entered.set()
            if not release.wait(8):
                raise AssertionError("Metadata gate not released")
        return save(ident, record)

    reenable = operation.startswith("reenable")
    if reenable:
        files.reset = delayed_reset
    else:
        manager._save = paused_save

    def disable():
        try:
            manager.set_enabled("accesso_file", False)
        except Exception as exc:
            errors.append("disable: " + type(exc).__name__ + ": " + str(exc))

    def peer_work():
        try:
            peer_started.set()
            if reenable:
                manager.set_enabled("accesso_file", True)
                if operation == "reenable":
                    result = files.execute("request_target", {"operation": "search"})
                    if result.status != "completed":
                        raise AssertionError("Fresh request was rejected")
                    values["fresh_token"] = files._result_token
            else:
                values["permission"] = files.enabled("read")
        except Exception as exc:
            errors.append("peer: " + type(exc).__name__ + ": " + str(exc))

    disabler = threading.Thread(target=disable, daemon=True)
    peer = threading.Thread(target=peer_work, daemon=True)
    disabler.start()
    try:
        if not entered.wait(5):
            raise AssertionError("Lifecycle gate not reached")
        peer.start()
        if not peer_started.wait(5):
            raise AssertionError("Peer did not start")
        peer.join(2 if reenable else 0.3)
        finished_before_release = not peer.is_alive()
    finally:
        release.set()
    disabler.join(3)
    peer.join(3)
    completed = not disabler.is_alive() and not peer.is_alive()
    report = dict(completed=completed, errors=errors,
                  finished_before_release=finished_before_release, **values)
    if completed and not errors:
        report.update(enabled=manager.files_enabled(),
                      pending=files.pending_clarification(),
                      token=files._result_token,
                      result_count=len(files._results),
                      selected=files._selected is not None)
        if operation == "reenable_old":
            report["stale_read"] = files.execute("read", {"target": "1"}).status
    return report


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
    selection = operation.endswith("_selection")
    if selection:
        operation = operation.removesuffix("_selection")
        listed = files.execute("list", {"target": str(folder)})
        chosen = files.execute("select", {"target": "1"})
        if listed.status != "completed" or chosen.status != "completed" or files._selected is None:
            raise AssertionError("The actual listed result and selection were not established")
    else:
        initial = files.execute("request_target", {"operation": "search"})
        if initial.status != "completed" or files.pending_clarification() != ("request", None):
            raise AssertionError("The real unanswered file request was not established")
    old_token = files._result_token
    if operation in ("reenable", "reenable_old", "transaction"):
        report = transition_probe(manager, files, operation)
        report["old_token"] = old_token
        return report

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
    def isolated_transition(self, operation):
        with TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--probe", tmp, operation],
                capture_output=True, text=True, encoding="utf-8", timeout=20, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["errors"], [], report)
            self.assertTrue(report["completed"], report)
            return report

    def test_delayed_disable_reset_does_not_clear_reenabled_request(self):
        report = self.isolated_transition("reenable")
        self.assertTrue(report["finished_before_release"], report)
        self.assertTrue(report["enabled"])
        self.assertEqual(report["pending"], ["request", None])
        self.assertEqual(report["token"], report["fresh_token"])

    def test_permission_read_waits_for_revocation_transaction(self):
        report = self.isolated_transition("transaction")
        self.assertFalse(report["finished_before_release"], report)
        self.assertFalse(report["permission"])
        self.assertFalse(report["enabled"])
        self.assertIsNone(report["pending"])

    def test_reenable_without_fresh_request_never_revives_old_state(self):
        for operation in ("reenable_old", "reenable_old_selection"):
            with self.subTest(operation=operation):
                report = self.isolated_transition(operation)
                self.assertTrue(report["enabled"])
                self.assertIsNone(report["pending"], report)
                self.assertEqual(report["result_count"], 0, report)
                self.assertFalse(report["selected"], report)
                self.assertNotEqual(report["token"], report["old_token"])
                self.assertEqual(report["stale_read"], "rejected")

    def test_reapprove_after_missing_ledger_invalidates_old_selection(self):
        from addon_manager import AddonManager
        from live_capabilities import LiveCapabilityRegistry
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            manager = AddonManager(LiveCapabilityRegistry(), root / "addons")
            manager.install(Path("file_access/AccessoFile.jaddon"))
            files = manager.file_service
            folder = root / "allowed"
            folder.mkdir()
            (folder / "nota.txt").write_text("Vecchio risultato", encoding="utf-8")
            files.policy.configure([(folder, True)])
            manager.set_enabled("accesso_file", True)
            self.assertEqual(files.execute("list", {"target": str(folder)}).status,
                             "completed")
            self.assertEqual(files.execute("select", {"target": "1"}).status,
                             "completed")
            self.assertIsNotNone(files._selected)
            token = files._result_token
            manager._consent_path.unlink()
            manager.set_enabled("accesso_file", True)
            self.assertTrue(manager.files_enabled())
            self.assertEqual(files._results, [])
            self.assertIsNone(files._selected)
            self.assertNotEqual(files._result_token, token)
            self.assertEqual(files.execute("read", {"target": "1"}).status, "rejected")

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

    def test_callbacks_preserve_operation_limits_and_descriptor_copies(self):
        from addon_manager import AddonManager
        from live_capabilities import LiveCapabilityRegistry
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = json.loads(Path("file_access/AccessoFile.jaddon").read_text(encoding="utf-8"))
            manifest["actions"] = manifest["actions"][:2]  # list/search only
            package = root / "restricted.jaddon"
            package.write_text(json.dumps(manifest), encoding="utf-8")
            manager = AddonManager(LiveCapabilityRegistry(), root / "addons")
            manager.install(package)
            manager.set_enabled("accesso_file", True)
            files = manager.file_service
            allowed = root / "allowed"
            allowed.mkdir()
            note = allowed / "nota.txt"
            note.write_text("Privato", encoding="utf-8")
            files.policy.configure([(allowed, True)])
            self.assertTrue(manager.files_enabled())
            for operation in ("list", "search"):
                self.assertTrue(manager.files_enabled(operation))
            for operation in ("read", "open", "locate", "unknown"):
                self.assertFalse(manager.files_enabled(operation))
            descriptions = manager.file_descriptors()
            descriptions[0]["id"] = "addon.accesso_file.leggi"
            descriptions[0]["core_action"] = "files.read"
            self.assertEqual(
                [a["core_action"] for a in manager.file_descriptors()],
                ["files.list", "files.search"])
            self.assertEqual(files.execute("read", {"target": str(note)}).status,
                             "rejected")
            self.assertEqual(note.read_text(encoding="utf-8"), "Privato")
            manager.set_enabled("accesso_file", False)
            self.assertFalse(manager.files_enabled())
            self.assertEqual(manager.file_descriptors(), ())

    def test_unrelated_refresh_keeps_active_pending_request_and_policy(self):
        from addon_manager import AddonManager
        from live_capabilities import LiveCapabilityRegistry
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            manager = AddonManager(LiveCapabilityRegistry(), root / "addons")
            manager.install(Path("file_access/AccessoFile.jaddon"))
            files = manager.file_service
            folder = root / "allowed"
            folder.mkdir()
            files.policy.configure([(folder, True)])
            manager.set_enabled("accesso_file", True)
            files.execute("request_target", {"operation": "search"})
            token = files._result_token
            policy_before = files.policy.path.read_bytes()
            for _ in range(3):
                manager.refresh()
                self.assertEqual(files.pending_clarification(), ("request", None))
                self.assertEqual(files._result_token, token)
            self.assertEqual(files.policy.path.read_bytes(), policy_before)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--probe":
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        print(json.dumps(lifecycle_probe(Path(sys.argv[2]), sys.argv[3])), flush=True)
    else:
        unittest.main()
