"""F5N.7: family from GGUF header, per-family template/stop, one native load per process."""
from pathlib import Path
import struct
import tempfile
import unittest

from local_model.chat_templates import (
    ModelFamilyError, format_messages, gguf_architecture, model_family, stop_sequence)
from local_model.native_bridge import NativeGemmaBridge, NativeRestartRequired
from local_model.native_config import NativeModelConfig
from local_model.native_provider import NativeLocalProvider


def _s(text):
    data = text.encode("utf-8")
    return struct.pack("<Q", len(data)) + data


def fake_gguf(path, arch, *, before=()):
    """Minimal GGUF v3 header; ``before`` adds KVs preceding the architecture."""
    kvs = list(before) + [_s("general.architecture") + struct.pack("<I", 8) + _s(arch)]
    path.write_bytes(b"GGUF" + struct.pack("<IQQ", 3, 0, len(kvs)) + b"".join(kvs))
    return path


class FakeUpstream:
    def __init__(self):
        self.loads, self.calls = [], []

    def load_model(self, path):
        self.loads.append(path)
        return True

    def generate(self, args):
        self.calls.append(args)
        return {"status": 1, "stopreason": 1, "text": "Roma.", "completion_tokens": 2}


class ChatTemplateTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.dll = self.root / "koboldcpp_noavx2.dll"
        self.dll.write_bytes(b"MZ")

    def bridge(self, arch):
        model = fake_gguf(self.root / (arch + ".gguf"), arch)
        config = NativeModelConfig(dll=str(self.dll), model=str(model))
        return NativeGemmaBridge(config, FakeUpstream(), initialize=lambda u, c: None)

    def test_architecture_read_after_other_keys(self):
        array = (_s("tokenizer.ggml.scores") + struct.pack("<IIQ", 9, 6, 3)
                 + struct.pack("<3f", 0.1, 0.2, 0.3))
        path = fake_gguf(self.root / "m.gguf", "qwen3",
                         before=[_s("general.name") + struct.pack("<I", 8) + _s("Qwen3"), array])
        self.assertEqual(gguf_architecture(path), "qwen3")
        self.assertEqual(model_family(str(path)), "qwen3")

    def test_family_mapping_and_default(self):
        for arch, family in (("gemma2", "gemma2"), ("gemma3", "gemma2"),
                             ("qwen2", "qwen25"), ("qwen3", "qwen3")):
            self.assertEqual(model_family(str(fake_gguf(self.root / (arch + ".gguf"), arch))), family)
        self.assertEqual(model_family(""), "gemma2")
        with self.assertRaises(ModelFamilyError):
            model_family(str(fake_gguf(self.root / "llama.gguf", "llama")))
        bad = self.root / "bad.gguf"
        bad.write_bytes(b"fixture: never loaded")
        self.assertEqual(model_family(str(bad)), "gemma2")
        with self.assertRaises(ModelFamilyError):
            gguf_architecture(bad)

    def test_formats_and_stops(self):
        messages = [{"role": "user", "content": "Ciao"}]
        self.assertTrue(format_messages(messages, "gemma2").endswith("<start_of_turn>model\n"))
        self.assertIn("You are Qwen", format_messages(messages, "qwen25"))
        self.assertTrue(format_messages(messages, "qwen3").endswith("<think>\n\n</think>\n\n"))
        self.assertEqual(stop_sequence("gemma2"), ["<end_of_turn>"])
        self.assertEqual(stop_sequence("qwen3"), ["<|im_end|>"])

    def test_bridge_and_provider_use_family_of_loaded_model(self):
        bridge = self.bridge("qwen3")
        provider = NativeLocalProvider(bridge)
        self.assertEqual(provider.ask(prompt="Capitale?"), "Roma.")
        call = bridge.upstream.calls[-1]
        self.assertEqual(call["stop_sequence"], ["<|im_end|>"])
        self.assertTrue(call["prompt"].startswith("<|im_start|>user\nCapitale?"))

    def test_gemma_unchanged(self):
        bridge = self.bridge("gemma2")
        NativeLocalProvider(bridge).ask(prompt="Ciao")
        call = bridge.upstream.calls[-1]
        self.assertEqual(call["stop_sequence"], ["<end_of_turn>"])
        self.assertEqual(call["prompt"], "<start_of_turn>user\nCiao<end_of_turn>\n<start_of_turn>model\n")

    def test_second_native_load_same_dll_refused(self):
        first = self.bridge("gemma2")
        first.load()
        first.load()  # idempotent on the loaded bridge
        second = self.bridge("qwen2")
        with self.assertRaises(NativeRestartRequired):
            second.load()
        self.assertEqual(second.upstream.loads, [])


if __name__ == "__main__":
    unittest.main()
