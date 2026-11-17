"""054: quota stimata e interruttore ricerca (profili e modelli: vedi test_055_modelli)."""
import ast
import struct
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import servizi_ricerca as sr
from local_model import miei_modelli, profili_famiglia as pf, scelta_modello
from local_model.native_config import NativeModelConfig

ROOT = Path(__file__).resolve().parents[1]


def gguf(path: Path, arch: str = "", size: int = 100) -> Path:
    body = b"GGUF" + b"\0" * 12
    if arch:
        body += b"general.architecture" + struct.pack("<IQ", 8, len(arch)) + arch.encode()
    path.write_bytes(body + b"x" * size)
    return path


class QuotaAndSwitchTests(unittest.TestCase):
    def test_estimated_quota_from_local_counters(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "uso.json"
            for _ in range(3):
                sr.quota.registra("tavily", oggi="2026-11-17", path=path)
            sr.quota.registra("tavily", oggi="2026-11-18", path=path)
            info = sr.quota.stato("tavily", 1000, oggi="2026-11-18", path=path)
            self.assertEqual((info["oggi"], info["mese"]), (1, 4))
            self.assertAlmostEqual(info["usato"], 0.004)
            self.assertIn("rilevate", info["testo"])
            self.assertTrue(info["stima"])
            # nuovo mese: i contatori ripartono
            self.assertEqual(sr.quota.stato("tavily", 1000, oggi="2026-12-01", path=path)["mese"], 0)
            # limite ignoto: niente percentuale, solo conteggi
            self.assertIsNone(sr.quota.stato("tavily", 0, oggi="2026-11-18", path=path)["usato"])
            # soglie dei colori come nei servizi online
            for _ in range(900):
                sr.quota.registra("tavily", oggi="2026-11-18", path=path)
            self.assertEqual(sr.quota.stato("tavily", 1000, oggi="2026-11-18", path=path)["colore"],
                             sr.quota.ROSSO)

    def test_search_switch_is_saved_and_blocks_cerca_online(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "servizi_ricerca.json"
            self.assertTrue(sr.ricerca_accesa(path))
            self.assertFalse(sr.imposta_accesa(False, path))
            self.assertFalse(sr.ricerca_accesa(path))
            self.assertTrue(sr.imposta_accesa(True, path))
        source = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        self.assertIn("RICERCA OFF > ", source)
        self.assertIn('hud.add_quick_button("ricerca", "RICERCA ▾", lambda: None, after="model")', source)


if __name__ == "__main__":
    unittest.main()
