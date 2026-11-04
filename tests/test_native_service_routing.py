"""Service routing tests with an opt-in native provider, Windows only."""
import os
import unittest
from local_model.native_provider import NativeLocalProvider
from local_model.service import ModelService
from gpt_client import GPTUnavailable


class FakeBridge:
    def __init__(self):
        self.prompts = []
    def load(self):
        pass
    def generate(self, prompt, *, timeout):
        self.prompts.append(prompt)
        return "Risposta nativa"


class FakeOnline:
    def __init__(self):
        self.calls = []
    def call(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return "Online"
    def stop(self):
        pass


@unittest.skipUnless(os.name == "nt", "Windows-only requirement")
class NativeServiceRoutingTests(unittest.TestCase):
    def test_native_answer_never_calls_online(self):
        online = FakeOnline()
        bridge = FakeBridge()
        service = ModelService(online, NativeLocalProvider(bridge),
                               local_enabled=True, online_enabled=True,
                               consent=lambda **kw: False)
        result = service.call("ask", prompt="Salve")
        self.assertEqual(result, "Risposta nativa")
        self.assertEqual(len(bridge.prompts), 1)
        self.assertEqual(online.calls, [])

    def test_local_disabled_and_online_disabled_denies_request(self):
        online = FakeOnline()
        service = ModelService(online, NativeLocalProvider(FakeBridge()),
                               local_enabled=False, online_enabled=False)
        with self.assertRaises(GPTUnavailable):
            service.call("ask", prompt="Salve")
        self.assertEqual(online.calls, [])

    def test_online_fallback_requires_consent(self):
        class FailingBridge(FakeBridge):
            def generate(self, prompt, *, timeout):
                raise RuntimeError("native failed")
        online = FakeOnline()
        service = ModelService(online, NativeLocalProvider(FailingBridge()),
                               local_enabled=True, online_enabled=True,
                               consent=lambda **kw: False)
        with self.assertRaises(GPTUnavailable):
            service.call("ask", prompt="Privato")
        self.assertEqual(online.calls, [])


if __name__ == "__main__":
    unittest.main()
