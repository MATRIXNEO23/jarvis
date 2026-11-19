"""Velocità, tonalità e volume: limiti, parametri per Edge/SAPI, effetto su WAV."""
import tempfile
import unittest
import wave
from pathlib import Path

import piper_voice
import voice_style


def make_wav(path, samples, rate=22050):
    import array
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(array.array("h", samples).tobytes())


class VoiceStyleTests(unittest.TestCase):
    def tearDown(self):
        voice_style.update(rate=0, pitch=0, volume=100)

    def test_limits_and_service_parameters(self):
        style = voice_style.update(rate=80, pitch=-20, volume=5)
        self.assertEqual(style, {"rate": 50, "pitch": -20, "volume": 10})
        self.assertEqual(voice_style.edge_params(),
                         {"rate": "+50%", "volume": "-90%", "pitch": "-10Hz"})
        self.assertEqual(voice_style.sapi_params(), {"rate": 10, "volume": 10, "pitch": -20})

    def test_pitch_resample_and_volume_on_wav(self):
        with tempfile.TemporaryDirectory() as folder:
            src, out = Path(folder) / "a.wav", Path(folder) / "b.wav"
            make_wav(src, [10000] * 2205)
            piper_voice.apply_pitch_volume(src, out, 1.25, 0.5)
            with wave.open(str(out)) as w:
                frames = w.getnframes()
                import array
                data = array.array("h", w.readframes(frames))
            self.assertEqual(frames, int(2205 / 1.25))     # più acuta = ricampionata
            self.assertTrue(all(abs(v - 5000) <= 1 for v in data))   # metà volume

    def test_neutral_style_keeps_audio_identical(self):
        with tempfile.TemporaryDirectory() as folder:
            src, out = Path(folder) / "a.wav", Path(folder) / "b.wav"
            make_wav(src, [100, -100] * 100)
            piper_voice.apply_pitch_volume(src, out, 1.0, 1.0)
            self.assertEqual(src.read_bytes(), out.read_bytes())


if __name__ == "__main__":
    unittest.main()
