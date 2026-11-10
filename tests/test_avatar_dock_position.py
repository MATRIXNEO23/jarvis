import tempfile
import unittest
from pathlib import Path

from lumi_avatar import clamp_dock, load_dock_position, save_dock_position


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


if __name__ == "__main__":
    unittest.main()
