"""Voci Edge online: etichette, labiale dai tempi delle parole, frase preparata."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import edge_voice


class EdgeVoiceTests(unittest.TestCase):
    def test_labels_round_trip(self):
        label = edge_voice.voice_label("isabella")
        self.assertEqual(label, "Edge: Isabella (online)")
        self.assertEqual(edge_voice.key_from_label(label), "isabella")
        self.assertIsNone(edge_voice.key_from_label("Piper: Paola"))

    def test_envelope_moves_only_on_words(self):
        env = edge_voice.envelope_from_marks([[0.0, 0.4], [1.0, 0.3]], fps=10)
        self.assertTrue(any(v > .3 for v in env[:4]))
        self.assertEqual(env[6], 0.0)          # pausa tra le parole: bocca chiusa
        self.assertTrue(any(v > .3 for v in env[10:13]))

    def test_next_sentence_prepared_once_and_files_removed(self):
        made, played = [], []
        with tempfile.TemporaryDirectory() as folder, \
                patch("piper_voice._audio_dir", return_value=Path(folder)):
            def synth(text, voice, path):
                made.append(text)
                path.write_bytes(b"ID3")
                return [[0.0, 0.2]]
            envelopes = []
            edge_voice.speak_with_edge("Prima.", "elsa", synth=synth, player=played.append,
                                       on_envelope=envelopes.append, upcoming="Seconda.")
            edge_voice.speak_with_edge("Seconda.", "elsa", synth=synth, player=played.append)
            self.assertEqual(sorted(made), ["Prima.", "Seconda."])
            self.assertEqual(len(played), 2)
            self.assertTrue(envelopes and envelopes[0])
            self.assertFalse(any(Path(p).exists() for p in played))

    def test_failure_raises_edge_error_for_windows_fallback(self):
        def broken(text, voice, path):
            raise edge_voice.EdgeVoiceError("rete assente")
        with tempfile.TemporaryDirectory() as folder, \
                patch("piper_voice._audio_dir", return_value=Path(folder)):
            with self.assertRaises(edge_voice.EdgeVoiceError):
                edge_voice.speak_with_edge("Ciao.", "diego", synth=broken, player=lambda p: None)


class SpeakerEdgeFallbackTests(unittest.TestCase):
    def test_edge_error_falls_back_to_windows_voice(self):
        from offline_tts import OfflineSpeaker
        errors, payloads = [], []
        speaker = OfflineSpeaker(notify_error=errors.append,
                                 runner=lambda payload, timeout: payloads.append(payload))
        def failing(*a, **k):
            raise edge_voice.EdgeVoiceError("rete assente")
        speaker._edge_speaker = failing
        self.assertTrue(speaker.speak("Ciao a tutti.", "Edge: Elsa (online)"))
        for _ in range(50):
            if payloads:
                break
            import time
            time.sleep(0.05)
        speaker.close()
        self.assertTrue(errors and "Edge" in errors[0])
        self.assertEqual(payloads[0]["voice"], "")


if __name__ == "__main__":
    unittest.main()
