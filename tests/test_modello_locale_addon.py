"""Modello locale come add-on incluso (build 044): acceso di serie, spento = niente modello."""
import json
import unittest
from pathlib import Path

import model_gate
from addon_manager import AddonError, validate_manifest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "local_model" / "ModelloLocale.jaddon"


class ModelAddonTests(unittest.TestCase):
    def tearDown(self):
        model_gate.register_addon(lambda: True)
        model_gate.set_local(True)
        model_gate.set_enabled(True)

    def test_manifest_valid_and_identity_protected(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        validate_manifest(data)
        data["id"] = "altro"
        with self.assertRaises(AddonError):
            validate_manifest(data)

    def test_addon_off_blocks_only_the_local_brain(self):
        self.assertTrue(model_gate.local_enabled())
        model_gate.register_addon(lambda: False)
        self.assertFalse(model_gate.local_enabled())
        self.assertTrue(model_gate.enabled())                 # MODELLO/GPT non toccati
        self.assertIn("Gestisci add-on", model_gate.refused_local("ciao"))
        self.assertIn("Gestisci add-on", model_gate.set_local(True))
        model_gate.register_addon(lambda: True)
        self.assertTrue(model_gate.local_enabled())

    def test_bundled_install_starts_enabled(self):
        source = (ROOT / "jarvis.py").read_text(encoding="utf-8")
        self.assertIn('("modello_locale", "local_model", "ModelloLocale.jaddon")', source)
        self.assertIn('addon_manager.set_enabled("modello_locale", True)', source)
        self.assertIn("register_addon(", source)


if __name__ == "__main__":
    unittest.main()
