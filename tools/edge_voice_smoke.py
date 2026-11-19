"""Windows CI: real Edge online voice (edge-tts) through Lumi's worker.

Informative only (network service outside our control): the workflow step
is continue-on-error, Lumi falls back to the Windows voice on failure.
"""
import json
from pathlib import Path
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import edge_voice  # noqa: E402

with tempfile.TemporaryDirectory() as temp:
    out = Path(temp) / "edge.mp3"
    started = time.monotonic()
    marks = edge_voice.synthesize("Ciao, sono Lumi con la voce di Elsa.", "elsa", out)
    first = round(time.monotonic() - started, 2)
    started = time.monotonic()
    edge_voice.synthesize("Seconda frase.", "isabella", Path(temp) / "b.mp3")
    second = round(time.monotonic() - started, 2)
    size = out.stat().st_size
    edge_voice.shutdown_worker()
    report = {"mp3_bytes": size, "word_marks": len(marks), "first_s_runner": first,
              "second_s_runner": second,
              "envelope_frames": len(edge_voice.envelope_from_marks(marks))}
    print(json.dumps(report))
    assert size > 2000 and marks, report
    print("EDGE_VOICE_SMOKE_OK")
