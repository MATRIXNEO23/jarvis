"""Voce bloccata con Netflix: il lettore non deve aspettare 10 minuti (build 042)."""
import os
import unittest
from unittest import mock

import audio_player


class StallTests(unittest.TestCase):
    def test_stuck_output_raises_audio_busy_quickly(self):
        clock = [0.0]

        def fake_mci(command):
            if command.startswith("status") and command.endswith("length"):
                return 0, "2000"
            if command.endswith("mode"):
                return 0, "playing"             # MCI dice «sto suonando»…
            if command.endswith("position"):
                return 0, "0"                   # …ma la posizione non avanza
            return 0, ""

        def fake_sleep(seconds):
            clock[0] += 0.5

        with mock.patch.object(audio_player, "_mci", fake_mci), \
                mock.patch.object(audio_player.os, "name", "nt"), \
                mock.patch.object(audio_player.time, "monotonic", lambda: clock[0]), \
                mock.patch.object(audio_player.time, "sleep", fake_sleep):
            with self.assertRaises(audio_player.AudioBusyError):
                audio_player.play(os.devnull)
        self.assertLess(clock[0], 5.0)


if __name__ == "__main__":
    unittest.main()
