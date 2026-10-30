"""Installer validation: no network and no microphone involved."""
import tempfile
import unittest
import zipfile
from pathlib import Path

from installa_modello_voce import unpack_model
from voice_control import MODEL_NAME


class VoiceInstallerTests(unittest.TestCase):
    def make_archive(self, folder, files):
        archive = folder / "model.zip"
        with zipfile.ZipFile(archive, "w") as zf:
            for path, data in files.items():
                zf.writestr(path, data)
        return archive

    def test_installs_official_layout(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            archive = self.make_archive(folder, {MODEL_NAME + "/am/final.mdl": b"test"})
            model = unpack_model(archive, folder)
            self.assertEqual((model / "am/final.mdl").read_bytes(), b"test")
            self.assertEqual(unpack_model(archive, folder), model)

    def test_blocks_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            archive = self.make_archive(folder, {
                MODEL_NAME + "/../../escape": b"bad",
                MODEL_NAME + "/am/final.mdl": b"test",
            })
            with self.assertRaises(ValueError):
                unpack_model(archive, folder)
            self.assertFalse((folder / "escape").exists())

    def test_rejects_model_missing_files(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            archive = self.make_archive(folder, {MODEL_NAME + "/README": b"not model"})
            with self.assertRaises(ValueError):
                unpack_model(archive, folder)
            self.assertFalse((folder / MODEL_NAME).exists())


if __name__ == "__main__":
    unittest.main()
