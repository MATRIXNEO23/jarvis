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
        self.assertGreaterEqual(clock[0], audio_player.START_GRACE)   # 15/11: attesa iniziale
        self.assertLess(clock[0], audio_player.START_GRACE + 2)

    def test_slow_start_is_not_a_stall_but_midway_stop_is(self):
        """Voce online: MP3 che parte dopo 5 s non è «bloccato»; fermo a metà sì (3 s)."""
        clock = [0.0]
        positions = iter(["0"] * 10 + ["400", "800"] + ["800"] * 20)

        def fake_mci(command):
            if command.endswith("length"):
                return 0, "5000"
            if command.endswith("mode"):
                return 0, "playing"
            if command.endswith("position"):
                return 0, next(positions, "800")
            return 0, ""

        with mock.patch.object(audio_player, "_mci", fake_mci), \
                mock.patch.object(audio_player.os, "name", "nt"), \
                mock.patch.object(audio_player.time, "monotonic", lambda: clock[0]), \
                mock.patch.object(audio_player.time, "sleep",
                                  lambda s: clock.__setitem__(0, clock[0] + 0.5)):
            with self.assertRaises(audio_player.AudioBusyError):
                audio_player.play(os.devnull)
        # partito a ~5 s (oltre i vecchi 3 s), poi fermo a 800 ms: errore ~3 s dopo
        self.assertGreater(clock[0], 8.0)
        self.assertLess(clock[0], 10.5)


if __name__ == "__main__":
    unittest.main()
