import os
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

import lumi_comandi
import pulizia_dati
from pulizia_dati import FileInfo, PuliziaWindow, file_in, leggibile


class FunzioniTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        (self.root / "audio").mkdir()
        (self.root / "audio" / "voce.wav").write_bytes(b"x" * 2048)
        (self.root / "registro.log").write_bytes(b"y" * 10)
        (self.root / "jarvis_chat_sessions.sqlite3").write_bytes(b"z" * 100)

    def tearDown(self):
        self.folder.cleanup()

    def test_file_dai_piu_grandi_e_segni(self):
        files = file_in(self.root)
        self.assertEqual([f.path.name for f in files], ["jarvis_chat_sessions.sqlite3", "registro.log"])
        self.assertTrue(files[0].importante)
        self.assertFalse(files[1].importante)
        self.assertTrue(file_in(self.root / "audio")[0].audio)
        self.assertEqual(pulizia_dati.dimensione(self.root), 2048 + 10 + 100)

    def test_importanti(self):
        for name in ("models/vosk/a.txt", "settings.json", "x.gguf", "telegram/s.txt"):
            self.assertTrue(FileInfo(Path("C:/d") / name, 1, 0).importante, name)
        self.assertFalse(FileInfo(Path("C:/d/voce.mp3"), 1, 0).importante)

    def test_leggibile(self):
        self.assertEqual(leggibile(10), "10 B")
        self.assertEqual(leggibile(2048), "2.0 KB")

    def test_cestino_vero_su_windows(self):
        if os.name != "nt":
            self.skipTest("Cestino solo su Windows")
        target = self.root / "registro.log"
        self.assertTrue(pulizia_dati.al_cestino([target]))
        self.assertFalse(target.exists())

    def test_comando_vocale(self):
        self.assertEqual(lumi_comandi.parse("pulizia dati"), "data_cleanup")
        self.assertEqual(lumi_comandi.parse("Lumi, libera spazio"), "data_cleanup")


class FinestraTest(unittest.TestCase):
    def setUp(self):
        try:
            self.tk = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: %s" % exc)
        self.tk.withdraw()
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        (self.root / "a.wav").write_bytes(b"a" * 300)
        (self.root / "b.log").write_bytes(b"b" * 200)
        (self.root / "memoria.sqlite3").write_bytes(b"c" * 100)
        self.notes = []
        with patch.object(pulizia_dati, "radici", lambda: [("Dati di Lumi", self.root)]):
            self.win = PuliziaWindow(self.tk, notify=self.notes.append,
                                     play_audio=lambda p: None)
        self.win.mostra(self.root)

    def tearDown(self):
        self.win.chiudi()
        self.tk.destroy()
        self.folder.cleanup()

    def test_seleziona_e_deseleziona(self):
        self.win.seleziona_tutto()
        self.assertEqual(len(self.win.checked), 3)
        self.win._spunta(str(self.root / "a.wav"))
        self.assertEqual(len(self.win.checked), 2)
        self.win.deseleziona_tutto()
        self.assertEqual(self.win.checked, set())

    def test_niente_senza_conferma_e_doppia_conferma_per_importanti(self):
        moved = []
        self.win.seleziona_tutto()
        with patch.object(pulizia_dati, "al_cestino", lambda paths: moved.extend(paths) or True):
            self.assertFalse(self.win.elimina(confirm=lambda *a: False))
            self.assertEqual(moved, [])
            answers = iter([True, False])               # sì al primo, no ai file ⚠
            self.assertFalse(self.win.elimina(confirm=lambda *a: next(answers)))
            self.assertEqual(moved, [])
            self.win.deseleziona_tutto()
            self.win._spunta(str(self.root / "b.log"))
            self.assertTrue(self.win.elimina(confirm=lambda *a: True))
        self.assertEqual([p.name for p in moved], ["b.log"])
        self.assertIn("PULIZIA >", self.notes[-1])

    def test_ascolta_solo_audio(self):
        self.win.list.focus(str(self.root / "b.log"))
        self.win.ascolta()
        self.assertIn("audio", self.win.status.get())


if __name__ == "__main__":
    unittest.main()
