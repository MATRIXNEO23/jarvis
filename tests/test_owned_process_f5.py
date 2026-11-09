"""No GGUF or real executable: model child lifecycle contract on Windows CI."""
import subprocess
import unittest
from unittest.mock import Mock

from local_model.owned_process_f5 import OwnedModelProcess, OwnedProcessError


class TestOwnedProcessF53b(unittest.TestCase):
    def test_launch_and_confirm_exit(self):
        child = Mock(pid=1234)
        child.poll.side_effect = [None, None]
        spawn = Mock(return_value=child)
        owner = OwnedModelProcess(spawn=spawn)
        self.assertEqual(owner.start(["C:/app/koboldcpp.exe", "--help"]), 1234)
        self.assertTrue(owner.is_running())
        with self.assertRaises(OwnedProcessError):
            owner.start(["another.exe"])
        self.assertTrue(owner.stop(timeout=3))
        child.terminate.assert_called_once()
        child.wait.assert_called_once_with(timeout=3)
        self.assertFalse(owner.blocked)
        self.assertTrue(owner.stop())
        spawn.assert_called_once()
        self.assertFalse(spawn.call_args.kwargs["shell"])

    def test_stopped_child_can_release(self):
        child = Mock(pid=10)
        child.poll.return_value = 0
        owner = OwnedModelProcess(spawn=Mock(return_value=child))
        owner.start(["local.exe"])
        self.assertTrue(owner.stop())
        child.terminate.assert_not_called()
        child.wait.assert_called_once()

    def test_timeout_blocks_restart(self):
        child = Mock(pid=222)
        child.poll.return_value = None
        child.wait.side_effect = subprocess.TimeoutExpired("model", 1)
        spawn = Mock(return_value=child)
        owner = OwnedModelProcess(spawn=spawn)
        owner.start(["local.exe"])
        with self.assertRaises(OwnedProcessError):
            owner.stop(timeout=1)
        self.assertTrue(owner.blocked)
        with self.assertRaises(OwnedProcessError):
            owner.start(["other.exe"])
        child.wait.side_effect = None
        self.assertTrue(owner.stop())
        owner.start(["other.exe"])
        self.assertEqual(spawn.call_count, 2)

    def test_never_launch_invalid_command_or_shell(self):
        spawn = Mock()
        owner = OwnedModelProcess(spawn=spawn)
        for command in ([], ["bad\x00cmd"], ["fine", ""], "free text", ["ok", 2]):
            with self.subTest(command=command), self.assertRaises(OwnedProcessError):
                owner.start(command)
        spawn.assert_not_called()

    def test_failed_spawn_does_not_claim_running(self):
        owner = OwnedModelProcess(spawn=Mock(side_effect=OSError("private path")))
        with self.assertRaises(OwnedProcessError) as cm:
            owner.start(["local.exe"])
        self.assertNotIn("private path", str(cm.exception))
        self.assertFalse(owner.blocked)
        self.assertFalse(owner.is_running())

    def test_timeout_validation(self):
        owner = OwnedModelProcess()
        for value in (float("nan"), float("inf"), True, 0, -1, 121):
            with self.subTest(value=value), self.assertRaises(OwnedProcessError):
                owner.stop(timeout=value)


if __name__ == "__main__":
    unittest.main()
