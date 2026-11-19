"""Lettore audio: la posizione reale arriva al labiale; fine audio = -1."""
import os
import unittest
from pathlib import Path
from unittest.mock import patch

import audio_player


@unittest.skipUnless(os.name == "nt", "Windows MCI")
class AudioPlayerTests(unittest.TestCase):
    def test_reports_real_position_then_end(self):
        modes = iter(["playing", "playing", "stopped"])
        positions = iter(["100", "250", "300"])
        commands = []

        def fake_mci(command):
            commands.append(command.split()[0])
            if command.endswith(" mode"):
                return 0, next(modes)
            if command.endswith(" position"):
                return 0, next(positions)
            return 0, ""

        seen = []
        with patch.object(audio_player, "_mci", fake_mci), \
                patch.object(audio_player, "POSITION_LISTENER", seen.append):
            audio_player.play(Path("C:/x/voce.mp3"))
        self.assertEqual(seen[:2], [0.1, 0.25])
        self.assertEqual(seen[-1], -1.0)
        self.assertEqual(commands[0], "open")
        self.assertEqual(commands[-1], "close")

    def test_mp3_that_cannot_open_raises(self):
        with patch.object(audio_player, "_mci", lambda c: (263, "")):
            with self.assertRaises(OSError):
                audio_player.play(Path("C:/x/voce.mp3"))


if __name__ == "__main__":
    unittest.main()
