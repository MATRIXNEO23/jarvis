"""056b: la memoria del prompt sta nel profilo del modello; memory.json resta il file letto."""
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from local_model import profili_famiglia as pf
from local_model.memory_preferences import MemoryPreferences
from local_model.native_config import NativeModelConfig


class MemoriaNelProfiloTests(unittest.TestCase):
    def test_salva_e_riapplica(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            gguf = tmp / "m.gguf"
            gguf.write_bytes(b"x")
            cfg = tmp / "native.json"
            NativeModelConfig(model=str(gguf)).save(cfg)
            MemoryPreferences(recent_messages=6, history_max_tokens=300).save(tmp / "memory.json")
            pf.salva_in_slot(gguf, 2, cfg)
            data = json.loads((tmp / "profili.json").read_text(encoding="utf-8"))
            saved = data["modelli"][pf.chiave(gguf)]["memoria"]["2"]
            self.assertEqual((saved["recent_messages"], saved["history_max_tokens"]), (6, 300))
            MemoryPreferences().save(tmp / "memory.json")
            pf.scegli_slot(gguf, 2, cfg)
            loaded = MemoryPreferences.load(tmp / "memory.json")
            self.assertEqual((loaded.recent_messages, loaded.history_max_tokens), (6, 300))

    def test_pagina_modelli_senza_finestre(self):
        root = Path(__file__).resolve().parents[1]
        ui = (root / "local_model" / "native_ui.py").read_text(encoding="utf-8")
        self.assertIn("embed", ui)
        self.assertNotIn("Gemma locale - configurazione", ui)
        m = (root / "local_model" / "miei_modelli.py").read_text(encoding="utf-8")
        self.assertEqual(m.count("Salva in questo profilo"), 0)


if __name__ == "__main__":
    unittest.main()
