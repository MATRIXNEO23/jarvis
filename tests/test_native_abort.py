"""Native abort and timeout contract tests (Windows)."""
import os
import threading
import time
import unittest
from local_model.native_bridge import NativeGemmaBridge
from local_model.native_config import NativeModelConfig
from local_model.native_provider import NativeLocalProvider


class FakeUpstream:
    def __init__(self):
        self.started = threading.Event()
        self.released = threading.Event()
        self.aborted = 0
    def generate(self, args):
        self.started.set()
        self.released.wait(3)
        return {"status": 1, "text": "late"}
    def abort_generate(self):
        self.aborted += 1
        self.released.set()


@unittest.skipUnless(os.name == "nt", "Windows-only")
class AbortContractTests(unittest.TestCase):
    def test_stop_requests_abort_during_generation(self):
        fake = FakeUpstream()
        bridge = NativeGemmaBridge(NativeModelConfig(), fake, initialize=lambda *_: None)
        bridge._loaded = True
        provider = NativeLocalProvider(bridge)
        errors = []
        thread = threading.Thread(target=lambda: self._run(provider, errors))
        thread.start()
        self.assertTrue(fake.started.wait(2))
        provider.stop()
        thread.join(3)
        self.assertFalse(thread.is_alive())
        self.assertEqual(fake.aborted, 1)
        self.assertTrue(errors)
        self.assertIsInstance(errors[0], RuntimeError)

    @staticmethod
    def _run(provider, errors):
        try:
            provider.ask(prompt="ciao")
        except Exception as exc:
            errors.append(exc)

    def test_late_result_is_not_returned(self):
        fake = FakeUpstream()
        bridge = NativeGemmaBridge(NativeModelConfig(), fake, initialize=lambda *_: None)
        bridge._loaded = True
        fake.released.set()
        original = fake.generate
        def delayed(args):
            time.sleep(0.02)
            return original(args)
        fake.generate = delayed
        with self.assertRaises(TimeoutError):
            bridge.generate("ciao", timeout=0.001)


if __name__ == "__main__":
    unittest.main()
