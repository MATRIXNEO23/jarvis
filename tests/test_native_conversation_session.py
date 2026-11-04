import unittest
from local_model.memory_preferences import MemoryPreferences
from local_model.native_config import NativeModelConfig
from local_model.native_conversation_session import NativeConversationSession


class FakeAdapter:
    def __init__(self, fail=False):
        self.calls = []
        self.prepares = 0
        self.stops = 0
        self.fail = fail

    def prepare(self):
        self.prepares += 1

    def call(self, action, *, prompt, timeout):
        self.calls.append(prompt)
        if self.fail:
            raise RuntimeError("offline failure")
        return {"text": "risposta " + str(len(self.calls))}

    def stop(self):
        self.stops += 1


class SessionTests(unittest.TestCase):
    def make_session(self, adapter):
        return NativeConversationSession(
            adapter, config_loader=lambda: NativeModelConfig(
                context_size=512, max_output=128),
            memory_loader=lambda: MemoryPreferences(recent_messages=8))

    def test_reuses_loaded_model_and_history(self):
        adapter = FakeAdapter()
        session = self.make_session(adapter)
        self.assertEqual(session.ask("ciao"), "risposta 1")
        self.assertEqual(session.ask("come va"), "risposta 2")
        self.assertEqual(adapter.prepares, 1)
        self.assertIn("Utente: ciao", adapter.calls[1])
        self.assertIn("Jarvis: risposta 1", adapter.calls[1])
        session.stop()
        self.assertEqual(adapter.stops, 1)

    def test_failure_does_not_save_turn_or_contact_online(self):
        adapter = FakeAdapter(fail=True)
        session = self.make_session(adapter)
        with self.assertRaises(RuntimeError):
            session.ask("ciao")
        self.assertEqual(len(session.history), 0)

    def test_question_role_cannot_be_silently_dropped(self):
        adapter = FakeAdapter()
        session = self.make_session(adapter)
        # Budget is 256 characters; the question alone fits but
        # its mandatory 'Utente: ' prefix does not.
        with self.assertRaises(ValueError):
            session.ask("x" * 250)
        self.assertEqual(adapter.prepares, 0)
        self.assertEqual(adapter.calls, [])

    def test_over_budget_rejected_before_model_load(self):
        adapter = FakeAdapter()
        session = self.make_session(adapter)
        with self.assertRaises(ValueError):
            session.ask("x" * 257)
        self.assertEqual(adapter.prepares, 0)


if __name__ == "__main__":
    unittest.main()
