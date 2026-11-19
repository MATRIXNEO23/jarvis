"""Nota vocale Telegram con la voce scelta in Lumi, e ripiego sulla voce Windows."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import telegram_voice


class VoiceSourceTests(unittest.TestCase):
    def test_edge_label_is_not_passed_to_sapi(self):
        calls = []
        with tempfile.TemporaryDirectory() as folder, \
                patch("edge_voice.synthesize", lambda text, key, out: Path(out).write_bytes(b"ID3") or []), \
                patch.object(telegram_voice, "_sapi_to_wav", lambda *a: calls.append(a)):
            source = telegram_voice._speech_source("Ciao", Path(folder), "Edge: Elsa (online)")
        self.assertEqual(source.suffix, ".mp3")
        self.assertEqual(calls, [])

    def test_broken_natural_voice_falls_back_to_default_windows_voice(self):
        calls = []
        def sapi(text, wav, voice):
            calls.append(voice)
            Path(wav).write_bytes(b"RIFF")
        def broken(*a, **k):
            raise RuntimeError("motore assente")
        with tempfile.TemporaryDirectory() as folder, \
                patch("piper_voice.synthesize", broken), \
                patch.object(telegram_voice, "_sapi_to_wav", sapi):
            source = telegram_voice._speech_source("Ciao", Path(folder), "Piper: Paola")
        self.assertEqual(calls, [""])
        self.assertEqual(source.suffix, ".wav")

    def test_unknown_windows_voice_retries_default(self):
        calls = []
        def sapi(text, wav, voice):
            calls.append(voice)
            if voice:
                raise telegram_voice.TelegramVoiceError("voce non trovata")
            Path(wav).write_bytes(b"RIFF")
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(telegram_voice, "_sapi_to_wav", sapi):
            telegram_voice._speech_source("Ciao", Path(folder), "Microsoft Inesistente")
        self.assertEqual(calls, ["Microsoft Inesistente", ""])


if __name__ == "__main__":
    unittest.main()
