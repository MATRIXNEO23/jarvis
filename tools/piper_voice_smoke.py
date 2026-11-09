"""Windows CI proof: download Paola from the repository catalog and synthesize.

Real engine (piper-tts) and real voice files; the runner CPU has AVX2, so this
does NOT prove the Pavilion (no AVX2) can run the engine.
"""
import json
from pathlib import Path
import sys
import tempfile
import time
import wave

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import piper_voice  # noqa: E402

with tempfile.TemporaryDirectory() as temp:
    folder = Path(temp) / "voci"
    started = time.monotonic()
    piper_voice.download_voice("paola", folder=folder)
    download_s = round(time.monotonic() - started, 1)
    out = {}
    def keep(path):
        with wave.open(str(path)) as w:
            out["seconds_audio"] = round(w.getnframes() / w.getframerate(), 2)
    envelope = []
    started = time.monotonic()
    piper_voice.speak_with_piper("Ciao Alberto, sono Lumi. Ho aperto Netflix per te.",
                                 "paola", effect=0.25, folder=folder,
                                 on_envelope=envelope.extend, player=keep)
    # Second sentence: persistent engine (model already loaded) + prefetch.
    started = time.monotonic()
    piper_voice.prepare("Seconda frase pronta in anticipo.", "paola", effect=0.25, folder=folder)
    piper_voice.speak_with_piper("Seconda frase pronta in anticipo.", "paola", effect=0.25,
                                 folder=folder, player=keep)
    out["second_sentence_seconds_runner"] = round(time.monotonic() - started, 2)
    out["persistent_worker"] = bool(piper_voice._WORKERS)
    piper_voice.shutdown_workers()
    out.update(download_seconds=download_s, synth_seconds_runner=round(time.monotonic() - started, 2),
               envelope_frames=len(envelope), engine_available=piper_voice.engine_available())
    print(json.dumps(out))
    assert out["seconds_audio"] > 1.0 and len(envelope) > 10, out
    assert out["persistent_worker"], out
    print("PIPER_VOICE_SMOKE_OK")
