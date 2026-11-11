"""Ogni add-on incluso nel pacchetto deve superare la validazione del gestore:
la 036 ha mostrato che un .jaddon rifiutato (descrizione troppo lunga) spariva
senza errore. Questa prova blocca la regressione prima della build."""
import json
import unittest
from pathlib import Path

from addon_manager import validate_manifest

ROOT = Path(__file__).resolve().parents[1]


class BundledAddonTests(unittest.TestCase):
    def test_every_bundled_jaddon_is_valid(self):
        files = sorted(p for p in ROOT.glob("*/*.jaddon") if "tests" not in p.parts)
        self.assertGreaterEqual(len(files), 5)
        for path in files:
            with self.subTest(addon=path.name):
                validate_manifest(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
