"""Motore del modello in un processo separato: stesso contratto di NativeChatAdapter.

Il figlio vero (`_child`) gira in un processo Python reale con un adattatore finto al posto
della DLL: si provano protocollo, streaming, conteggio token, errori, cambio modello (nuovo
processo) e chiusura (processo terminato), senza modello pesante.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from local_model import motore_processo
from local_model.native_config import NativeModelConfig
from local_model.token_stream import streaming

ROOT = Path(__file__).resolve().parents[1]
FAKE_CHILD = r'''
import os, sys
import local_model.native_chat_adapter as real
class Fake:
    def __init__(self, source): self.config = None
    def prepare(self, *, config=None): self.config = config
    def context_token_counter(self): return lambda text: len(text.split())
    def call(self, action, *, timeout=120, prompt_budget=None, **arguments):
        from local_model.token_stream import current
        if arguments.get("prompt") == "errore": raise ValueError("Prompt oltre il budget")
        cb = current()
        if cb: cb("Cia"); cb("Ciao")
        print("rumore del motore C")            # deve finire nel registro, non nel protocollo
        return {"text": "Ciao da " + str(os.getpid()) + " " + self.config.model,
                "finish_reason": "stop", "completion_tokens": 2}
    def stop(self): pass
real.NativeChatAdapter = Fake
from local_model.motore_processo import _child
_child("sorgente")
'''


class EngineProcessTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.models = []
        for name in ("a.gguf", "b.gguf"):
            path = Path(folder.name) / name
            path.write_bytes(b"x")
            self.models.append(str(path))
        patcher = mock.patch.object(motore_processo, "_settings_path",
                                    lambda: Path(folder.name) / "motore.json")
        patcher.start()
        self.addCleanup(patcher.stop)
        self.adapter = motore_processo.ProcessChatAdapter(
            "sorgente", command=[sys.executable, "-u", "-c", FAKE_CHILD])
        self.addCleanup(self.adapter.stop)

    def config(self, model):
        return NativeModelConfig(model=model)

    def test_ask_streams_counts_and_switches_model_without_restarting_lumi(self):
        with mock.patch.object(NativeModelConfig, "validate", lambda self: None):
            self.adapter.prepare(config=self.config(self.models[0]))
            first = self.adapter._proc.pid
            self.assertEqual(self.adapter.context_token_counter()("uno due tre"), 3)
            chunks = []
            with streaming(chunks.append):
                result = self.adapter.call("ask", prompt="ciao", timeout=5)
            self.assertEqual(chunks, ["Cia", "Ciao"])
            self.assertTrue(result["text"].endswith("a.gguf"))
            # Testo con un carattere «rotto» (surrogato) e accenti: errore visto sul Pavilion
            # («'utf-8' codec can't encode character '\udc8d'»), ora deve passare.
            self.assertIn("Ciao", self.adapter.call("ask", prompt="perché \udc8d così", timeout=5)["text"])
            with self.assertRaises(ValueError):
                self.adapter.call("ask", prompt="errore", timeout=5)
            self.adapter.prepare(config=self.config(self.models[1]))   # cambio modello
            self.assertNotEqual(self.adapter._proc.pid, first)
            self.assertTrue(self.adapter.call("ask", prompt="ciao", timeout=5)["text"].endswith("b.gguf"))

    def test_stop_ends_the_process_and_crash_is_reported(self):
        with mock.patch.object(NativeModelConfig, "validate", lambda self: None):
            self.adapter.prepare(config=self.config(self.models[0]))
            proc = self.adapter._proc
            self.adapter.stop()
            self.assertIsNotNone(proc.poll())                   # memoria liberata: processo chiuso
            self.adapter.prepare(config=self.config(self.models[0]))
            self.adapter._proc.kill()
            self.adapter._proc.wait()
            with self.assertRaises(motore_processo.EngineStopped):
                self.adapter.call("ask", prompt="ciao", timeout=5)

    def test_choice_defaults_to_engine_inside_lumi(self):
        self.assertFalse(motore_processo.separate_enabled())
        from local_model.native_chat_adapter import NativeChatAdapter
        self.assertIsInstance(motore_processo.adattatore("x"), NativeChatAdapter)
        motore_processo.set_separate(True)
        self.assertIsInstance(motore_processo.adattatore("x"), motore_processo.ProcessChatAdapter)


if __name__ == "__main__":
    unittest.main()
