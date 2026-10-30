"""Safe local-engine regression tests; no external network or Windows launch."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from local_engine import LocalEngine


class LocalEngineTests(TestCase):
    def setUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.downloads = base / "Downloads"
        self.downloads.mkdir()
        self.engine = LocalEngine(download_dir=self.downloads, db_path=base / "tasks.db", windows=False)

    def test_help_and_history(self):
        first = self.engine.execute("aiuto")
        self.assertEqual(first.status, "completed")
        self.assertIn("stato sistema", first.message)
        self.assertIn("help", self.engine.execute("ultimi comandi").message)

    def test_rejects_unlisted_and_shell_commands(self):
        for cmd in ("del C:\\Windows", "python -c print(1)", "apri powershell", ""):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.engine.execute(cmd).status, "rejected")

    def test_list_and_find_downloads(self):
        (self.downloads / "documento prova.txt").write_text("ciao", encoding="utf-8")
        self.assertIn("documento prova.txt", self.engine.execute("mostra download").message)
        found = self.engine.execute("cerca file prova")
        self.assertEqual(found.status, "completed")
        self.assertIn("documento prova.txt", found.message)

    def test_no_symlink_walk(self):
        target = Path(self.temp.name) / "private"
        target.mkdir()
        (target / "segreto.txt").write_text("test", encoding="utf-8")
        link = self.downloads / "link"
        try:
            link.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink unavailable")
        self.assertNotIn("segreto.txt", self.engine.execute("cerca file segreto").message)

    def test_search_rejects_path_syntax(self):
        self.assertEqual(self.engine.execute("cerca file ../segreto").status, "failed")

    def test_open_apps_only_on_windows(self):
        self.assertEqual(self.engine.execute("apri blocco note").status, "failed")

    def test_open_app_uses_fixed_argv_no_shell(self):
        self.engine.windows = True
        with patch("local_engine.subprocess.Popen") as popen:
            result = self.engine.execute("apri blocco note")
        self.assertEqual(result.status, "completed")
        popen.assert_called_once_with(["notepad.exe"], close_fds=True, shell=False)
