import sys
import tempfile
import unittest
from pathlib import Path

from componenti import catalog


class CatalogTests(unittest.TestCase):
    def test_every_component_has_check_link_and_install_command(self):
        ids = set()
        for item in catalog.COMPONENTS:
            with self.subTest(component=item["id"]):
                self.assertNotIn(item["id"], ids)
                ids.add(item["id"])
                self.assertTrue(item["link"].startswith("https://"))
                self.assertIsInstance(catalog.is_installed(item), bool)
                commands = catalog.install_commands(item)
                self.assertTrue(commands)
                for command in commands:
                    self.assertIsInstance(command, list)       # mai stringhe per la shell
                    for part in command:
                        if part.endswith((".py", ".ps1")):
                            self.assertTrue(Path(part).is_file(), part)
        for key in catalog.API_KEYS:
            self.assertTrue(key["link"].startswith("https://"))

    def test_pip_uses_lumi_python_for_current_user(self):
        command = catalog.install_commands(catalog.by_id("telethon"))[0]
        self.assertEqual(command[:5], [sys.executable, "-m", "pip", "install", "--user"])
        self.assertEqual(catalog.install_commands(catalog.by_id("webview2"))[0][:4],
                         ["winget", "install", "--id", "Microsoft.EdgeWebView2Runtime"])

    def test_per_addon_requirements(self):
        self.assertEqual({c["id"] for c in catalog.for_addon("telegram")}, {"telethon", "ffmpeg"})
        self.assertEqual({c["id"] for c in catalog.for_addon("musica")}, {"webview2"})
        self.assertEqual([k["id"] for k in catalog.keys_for_addon("musica")], ["youtube_key"])
        self.assertEqual(catalog.for_addon("controllo_pc"), [])

    def test_editable_links_saved_and_restored(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "componenti.json"
            item = catalog.by_id("ffmpeg")
            self.assertIn("https://", catalog.set_link("ffmpeg", "http://non-sicuro", path))
            self.assertEqual(catalog.set_link("ffmpeg", "https://esempio.it/ffmpeg", path), "Link salvato.")
            self.assertEqual(catalog.link_for(item, catalog.load_state(path)), "https://esempio.it/ffmpeg")
            catalog.set_link("ffmpeg", "", path)
            self.assertEqual(catalog.link_for(item, catalog.load_state(path)), item["link"])
            self.assertFalse(catalog.load_state(path)["wizard_shown"])


if __name__ == "__main__":
    unittest.main()
