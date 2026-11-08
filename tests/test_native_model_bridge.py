"""Windows-only tests for the isolated native inference bridge, fake ABI only."""
import os
from pathlib import Path
import tempfile
import unittest
from local_model.native_bridge import NativeGemmaBridge
from local_model.native_config import NativeModelConfig


class FakeUpstream:
    def __init__(self):
        self.loads = 0
        self.calls = []
    def load_model(self, path):
        self.loads += 1
        return True
    def generate(self, arguments):
        self.calls.append(arguments)
        return {"status": 1, "text": "Ciao!"}


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class NativeBridgeTests(unittest.TestCase):
    def test_load_once_and_generate_with_config(self):
        with tempfile.TemporaryDirectory() as folder:
            dll = Path(folder) / "engine.dll"
            model = Path(folder) / "model.gguf"
            dll.write_bytes(b"test-only")
            model.write_bytes(b"test-only")
            c = NativeModelConfig(dll=str(dll), model=str(model),
                                  context_size=4096, max_output=256,
                                  temperature=0.4, seed=12)
            fake = FakeUpstream()
            initialized = []
            bridge = NativeGemmaBridge(c, fake, initialize=lambda upstream, config: initialized.append(config))
            bridge.load()
            bridge.load()
            self.assertEqual(fake.loads, 1)
            self.assertEqual(initialized, [c])
            self.assertEqual(bridge.generate("Saluta"), "Ciao!")
            self.assertEqual(fake.calls[0]["max_context_length"], 4096)
            self.assertEqual(fake.calls[0]["max_length"], 256)
            self.assertEqual(fake.calls[0]["sampler_seed"], 12)

    def test_stopreason_is_exposed_only_as_diagnostic_metadata(self):
        with tempfile.TemporaryDirectory() as folder:
            dll = Path(folder) / "engine.dll"
            model = Path(folder) / "model.gguf"
            dll.write_bytes(b"test-only")
            model.write_bytes(b"test-only")
            fake = FakeUpstream()
            bridge = NativeGemmaBridge(NativeModelConfig(
                dll=str(dll), model=str(model)), fake,
                initialize=lambda upstream, config: None)
            bridge.load()
            def cut(arguments):
                return {"status": 1, "text": '{"kind":"capability",',
                        "stopreason": 0, "completion_tokens": 128}
            fake.generate = cut
            self.assertEqual(bridge.generate("un comando"), '{"kind":"capability",')
            self.assertEqual(bridge.last_generation_finish, "length")
            self.assertEqual(bridge.last_generation_tokens, 128)
            fake.generate = lambda arguments: {
                "status": 1, "text": "Fine.", "stopreason": 1,
                "completion_tokens": 12}
            self.assertEqual(bridge.generate("risposta breve"), "Fine.")
            self.assertEqual(bridge.last_generation_finish, "stop")
            self.assertEqual(bridge.last_generation_tokens, 12)

    def test_missing_initializer_prevents_native_load(self):
        with tempfile.TemporaryDirectory() as folder:
            dll = Path(folder) / "engine.dll"
            model = Path(folder) / "model.gguf"
            dll.write_bytes(b"test-only")
            model.write_bytes(b"test-only")
            fake = FakeUpstream()
            bridge = NativeGemmaBridge(NativeModelConfig(
                dll=str(dll), model=str(model)), fake)
            with self.assertRaises(RuntimeError):
                bridge.load()
            self.assertEqual(fake.loads, 0)

    def test_missing_model_prevents_load(self):
        bridge = NativeGemmaBridge(NativeModelConfig(model="missing.gguf",
                                      dll="missing.dll"), FakeUpstream())
        with self.assertRaises(RuntimeError):
            bridge.load()

    def test_generate_requires_loaded_model(self):
        bridge = NativeGemmaBridge(NativeModelConfig(), FakeUpstream())
        with self.assertRaises(RuntimeError):
            bridge.generate("ciao")


if __name__ == "__main__":
    unittest.main()
