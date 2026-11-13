import tempfile
import unittest
from pathlib import Path

from lumi_avatar import (clamp_dock, load_dock_position, load_dock_positions, marquee,
                         save_dock_position)


class DockPositionTests(unittest.TestCase):
    def test_position_saved_and_kept_above_taskbar(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "avatar-dock.json"
            self.assertIsNone(load_dock_position(path))
            save_dock_position(path, 300, 400)
            self.assertEqual(load_dock_position(path), (300, 400))
            path.write_text('{"x": "a", "y": 1}', encoding="utf-8")
            self.assertIsNone(load_dock_position(path))
        area = (0, 0, 1280, 680)                        # barra delle applicazioni sotto 680
        self.assertEqual(clamp_dock(1200, 600, 179, 190, area), (1101, 490))
        self.assertEqual(clamp_dock(-50, -50, 179, 190, area), (0, 0))
        self.assertEqual(clamp_dock(500, 300, 179, 190, area), (500, 300))


    def test_avatar_and_player_positions_saved_separately(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "avatar-dock.json"
            save_dock_position(path, 900, 480)
            save_dock_position(path, 700, 600, "player")
            save_dock_position(path, 950, 470)              # sposto solo l'avatar
            self.assertEqual(load_dock_positions(path),
                             {"avatar": (950, 470), "player": (700, 600)})

    def test_marquee_scrolls_only_long_titles(self):
        self.assertEqual(marquee("Corto", 5, 24), "Corto")
        long = "rob, Finley - ZERO DIFFERENZE (Official Video)"
        self.assertEqual(len(marquee(long, 3, 24)), 24)
        self.assertNotEqual(marquee(long, 0, 24), marquee(long, 1, 24))


if __name__ == "__main__":
    unittest.main()


class DockOptionsTests(unittest.TestCase):
    def test_options_saved_with_positions(self):
        from lumi_avatar import load_dock_options, save_dock_options
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "avatar-dock.json"
            self.assertEqual(load_dock_options(path), {"show": True, "idle": 30})
            save_dock_position(path, 10, 20)
            save_dock_options(path, False, 45)
            save_dock_position(path, 11, 21, "player")
            self.assertEqual(load_dock_options(path), {"show": False, "idle": 45})
            self.assertEqual(load_dock_positions(path), {"avatar": (10, 20), "player": (11, 21)})
