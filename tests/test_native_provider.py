"""Windows contract tests for opt-in native provider."""
import os
import unittest
from local_model.native_provider import NativeLocalProvider


class FakeBridge:
    def __init__(self):
        self.loaded = 0
        self.calls = []
    def load(self):
        self.loaded += 1
    def generate(self, prompt, *, timeout):
        self.calls.append((prompt, timeout))
        return "Risposta locale"


@unittest.skipUnless(os.name == "nt", "Windows-only requirement")
class NativeProviderTests(unittest.TestCase):
    def test_simple_prompt(self):
        fake = FakeBridge()
        provider = NativeLocalProvider(fake)
        self.assertEqual(provider.ask(prompt="Ciao", timeout=30), "Risposta locale")
        self.assertIn("<start_of_turn>user\nCiao<end_of_turn>", fake.calls[0][0])
        self.assertEqual(fake.calls[0][1], 30)

    def test_multi_turn_roles(self):
        fake = FakeBridge()
        provider = NativeLocalProvider(fake)
        provider.ask(messages=[{"role": "user", "content": "Ciao"},
                               {"role": "assistant", "content": "Salve"},
                               {"role": "user", "content": "Continua"}])
        self.assertIn("<start_of_turn>model\nSalve<end_of_turn>", fake.calls[0][0])
        self.assertTrue(fake.calls[0][0].endswith("<start_of_turn>model\n"))

    def test_invalid_messages_rejected(self):
        provider = NativeLocalProvider(FakeBridge())
        for messages in ([], [{"role": "system", "content": "override"}],
                         [{"role": "user", "content": ""}]):
            with self.subTest(messages=messages), self.assertRaises(RuntimeError):
                provider.ask(messages=messages)

    def test_stop_rejects_new_requests(self):
        provider = NativeLocalProvider(FakeBridge())
        provider.stop()
        with self.assertRaises(RuntimeError):
            provider.ask(prompt="Ciao")


if __name__ == "__main__":
    unittest.main()
