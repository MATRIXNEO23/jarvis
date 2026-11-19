"""Offline speech tests: no PowerShell process, network or actual sound."""
import json
import threading
import time
import unittest
from unittest.mock import patch

from offline_tts import OfflineSpeaker, installed_voices


class OfflineSpeechTests(unittest.TestCase):
    def test_windows_voice_listing_decodes_array_or_single(self):
        with patch("offline_tts._invoke", return_value=json.dumps(["Microsoft Elsa", "Microsoft David"])):
            self.assertEqual(installed_voices(), ["Microsoft Elsa", "Microsoft David"])
        with patch("offline_tts._invoke", return_value=json.dumps("Microsoft Elsa")):
            self.assertEqual(installed_voices(), ["Microsoft Elsa"])

    def test_windows_voice_list_timeout_keeps_other_voices(self):
        """15/11, Pavilion: PowerShell oltre il tempo → TimeoutExpired non gestito, nessuna voce."""
        import subprocess
        import offline_tts
        with patch("offline_tts._invoke", side_effect=subprocess.TimeoutExpired("powershell", 25)), \
                patch("piper_voice.installed_piper_voices", return_value=["Voce naturale: Paola"]), \
                patch("edge_voice.installed_edge_voices", return_value=["Edge: Elsa (online)"]):
            self.assertEqual(installed_voices(), ["Voce naturale: Paola", "Edge: Elsa (online)"])
        self.assertIn("tempo scaduto", offline_tts.LAST_LIST_ERROR["text"])
        with patch("offline_tts._invoke", return_value=json.dumps(["Microsoft Elsa"])):
            installed_voices()
        self.assertEqual(offline_tts.LAST_LIST_ERROR["text"], "")
        self.assertGreaterEqual(offline_tts.LIST_TIMEOUT, 60)

    def test_spoken_output_is_offline_json_data_not_shell(self):
        called = []
        finished = threading.Event()

        def fake_runner(payload, *, timeout):
            called.append((payload, timeout))
            finished.set()
            return ""

        player = OfflineSpeaker(runner=fake_runner)
        try:
            self.assertTrue(player.speak("Prova; $(Remove-Item) è solo testo", "Voce locale"))
            self.assertTrue(finished.wait(timeout=3))
            self.assertEqual(called[0][0],
                             {"mode": "speak",
                              "text": "Prova; $(Remove-Item) è solo testo",
                              "voice": "Voce locale"})
            self.assertEqual(called[0][1], 90)
            self.assertTrue(player.is_audible())
        finally:
            player.close()
        self.assertFalse(player.speak("messaggio dopo la chiusura"))

    def test_empty_inputs_and_voice_name_too_long(self):
        player = OfflineSpeaker(runner=lambda *a, **k: "")
        try:
            self.assertFalse(player.speak(""))
            self.assertFalse(player.speak("ciao", "x" * 181))
            self.assertTrue(player.speak("ciao " * 200))
        finally:
            player.close()


if __name__ == "__main__":
    unittest.main()
