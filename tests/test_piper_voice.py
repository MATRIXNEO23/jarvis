"""Natural voices (Piper): verified download, isolated synthesis, fallback, effect."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
import wave

import piper_voice
from offline_tts import OfflineSpeaker


def make_wav(path, samples, rate=22050):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(struct.pack("<%dh" % len(samples), *samples))


class Opener:
    def __init__(self, files):
        self.files = files

    def __call__(self, url, timeout=None):
        return io.BytesIO(self.files[url])


class PiperVoiceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.dir = Path(temp.name)

    def catalog(self, onnx=b"ONNX", meta=b"{}", tamper=False):
        files = {"it_IT-paola-medium.onnx": onnx, "it_IT-paola-medium.onnx.json": meta}
        entries = {n: {"sha256": hashlib.sha256(d).hexdigest(), "bytes": len(d),
                       "url": "https://x/" + n} for n, d in files.items()}
        if tamper:
            entries["it_IT-paola-medium.onnx"]["sha256"] = "0" * 64
        cat = {"voices": {"paola": {"files": entries, "license": "L", "attribution": "A"}}}
        urls = {"https://x/" + n: d for n, d in files.items()}
        urls["https://cat"] = json.dumps(cat).encode()
        return Opener(urls)

    def test_download_verifies_hash_and_lists_voice(self):
        model = piper_voice.download_voice("paola", catalog_url="https://cat",
                                           folder=self.dir, opener=self.catalog())
        self.assertEqual(model.name, "it_IT-paola-medium.onnx")
        self.assertEqual(piper_voice.installed_piper_voices(self.dir), ["Piper: Paola"])
        self.assertEqual(piper_voice.key_from_label("Piper: Paola"), "paola")
        self.assertIsNone(piper_voice.key_from_label("Microsoft Elsa"))

    def test_tampered_download_is_rejected_and_not_installed(self):
        with self.assertRaises(piper_voice.PiperVoiceError):
            piper_voice.download_voice("paola", catalog_url="https://cat", folder=self.dir,
                                       opener=self.catalog(tamper=True))
        self.assertEqual(piper_voice.installed_piper_voices(self.dir), [])
        self.assertFalse(list(self.dir.glob("*.part")))

    def test_synthesis_failure_in_child_raises_clear_error(self):
        piper_voice.download_voice("paola", catalog_url="https://cat",
                                   folder=self.dir, opener=self.catalog())
        def crashing(cmd, **kwargs):
            self.assertEqual(cmd[1:3], ["-m", "piper"])
            return subprocess.CompletedProcess(cmd, 3221225501, "", "illegal instruction")
        with self.assertRaisesRegex(piper_voice.PiperVoiceError, "non disponibile"):
            piper_voice.synthesize("Ciao", "paola", self.dir / "o.wav",
                                   folder=self.dir, runner=crashing)

    def test_envelope_and_effect(self):
        loud = [0] * 2205 + [20000, -20000] * 1102
        make_wav(self.dir / "a.wav", loud)
        env = piper_voice.loudness_envelope(self.dir / "a.wav", fps=10)
        self.assertLess(env[0], 0.1)
        self.assertGreater(max(env), 0.9)
        out = piper_voice.apply_digital_effect(self.dir / "a.wav", self.dir / "b.wav", 0)
        self.assertEqual(out.read_bytes(), (self.dir / "a.wav").read_bytes())

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "numpy not installed")
    def test_digital_effect_keeps_length_and_changes_audio(self):
        make_wav(self.dir / "a.wav", [int(8000 * ((i % 50) / 25 - 1)) for i in range(22050)])
        piper_voice.apply_digital_effect(self.dir / "a.wav", self.dir / "b.wav", 0.3)
        with wave.open(str(self.dir / "b.wav")) as w:
            self.assertEqual(w.getnframes(), 22050)
        self.assertNotEqual((self.dir / "a.wav").read_bytes(), (self.dir / "b.wav").read_bytes())


class SpeakerFallbackTests(unittest.TestCase):
    def test_piper_failure_falls_back_to_windows_voice_and_notifies(self):
        calls, errors = [], []
        speaker = OfflineSpeaker(runner=lambda payload, timeout: calls.append(payload),
                                 notify_error=errors.append)
        def failing(text, key, **kwargs):
            raise piper_voice.PiperVoiceError("Motore Piper non disponibile (codice 1).")
        speaker._piper_speaker = failing
        self.assertTrue(speaker.speak("Ciao Alberto", "Piper: Paola"))
        for _ in range(100):
            if calls:
                break
            import time
            time.sleep(0.02)
        speaker.close()
        self.assertEqual(calls[0]["voice"], "")
        self.assertIn("Voce naturale non disponibile", errors[0])

    def test_piper_success_does_not_use_windows_voice(self):
        calls, spoken = [], []
        speaker = OfflineSpeaker(runner=lambda payload, timeout: calls.append(payload))
        speaker._piper_speaker = lambda text, key, **kw: spoken.append((text, key, kw["effect"]))
        speaker.effect = 0.25
        speaker.speak("Ciao", "Piper: Serena")
        for _ in range(100):
            if spoken:
                break
            import time
            time.sleep(0.02)
        speaker.close()
        self.assertEqual(spoken, [("Ciao", "serena", 0.25)])
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
