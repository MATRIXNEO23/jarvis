import unittest
from local_model.chat_transport import ChatTransport


class Fake:
    def __init__(self, answer):
        self.answer = answer
        self.calls = []

    def call(self, action, *, timeout=120, **kwargs):
        self.calls.append((action, kwargs))
        if isinstance(self.answer, Exception):
            raise self.answer
        return self.answer


class TransportTests(unittest.TestCase):
    def test_native_call_never_contacts_online(self):
        online = Fake({"text": "online"})
        native = Fake({"text": "native"})
        transport = ChatTransport(online, native)
        self.assertEqual(transport.call("ask", use_native=True, prompt="ciao")["text"], "native")
        self.assertEqual(online.calls, [])

    def test_native_failure_never_falls_back(self):
        online = Fake({"text": "online"})
        transport = ChatTransport(online, Fake(RuntimeError("native failed")))
        with self.assertRaises(RuntimeError):
            transport.call("ask", use_native=True, prompt="ciao")
        self.assertEqual(online.calls, [])

    def test_online_account_actions_unchanged(self):
        online = Fake({"status": "connected"})
        transport = ChatTransport(online, Fake({}))
        self.assertEqual(transport.call("status"), {"status": "connected"})
        self.assertEqual(online.calls[0][0], "status")

    def test_native_account_actions_rejected(self):
        online = Fake({})
        transport = ChatTransport(online, Fake({}))
        with self.assertRaises(ValueError):
            transport.call("sign_in", use_native=True)
        self.assertEqual(online.calls, [])


if __name__ == "__main__":
    unittest.main()
