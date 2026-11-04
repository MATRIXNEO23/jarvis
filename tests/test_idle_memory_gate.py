import unittest

from local_model.idle_memory_gate import IdleMemoryGate
from local_model.memory_preferences import MemoryPreferences


class IdleGateTests(unittest.TestCase):
    def test_one_minute_idle_and_conversation_priority(self):
        now = [0]
        gate = IdleMemoryGate(MemoryPreferences(), lambda: now[0])
        gate.queue_summary()
        now[0] = 59
        self.assertFalse(gate.ready())
        now[0] = 60
        self.assertTrue(gate.begin())
        self.assertFalse(gate.begin())
        gate.finish(saved=True)
        self.assertFalse(gate.ready())
        gate.queue_summary()
        gate.activity()
        now[0] = 150
        self.assertFalse(gate.ready())
        gate.conversation_finished()
        now[0] = 209
        self.assertFalse(gate.ready())
        now[0] = 210
        self.assertTrue(gate.ready())

    def test_load_and_failed_work(self):
        now = [60]
        gate = IdleMemoryGate(MemoryPreferences(), lambda: now[0])
        gate.last_activity = 0
        gate.queue_summary()
        gate.heavy_load = True
        self.assertFalse(gate.ready())
        gate.heavy_load = False
        self.assertTrue(gate.begin())
        gate.finish(saved=False)
        self.assertTrue(gate.pending)


if __name__ == "__main__":
    unittest.main()
