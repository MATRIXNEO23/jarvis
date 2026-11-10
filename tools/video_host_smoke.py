"""Windows CI: il riquadro video (LumiVideo.exe, WebView2) parte dentro una
finestra Tk, carica la pagina del lettore e riceve comandi. Prova reale del
componente; l'audio e YouTube veri restano da provare sul PC."""
import json
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
import wave


def main(out_dir: str) -> int:
    exe = Path(out_dir) / "LumiVideo.exe"
    assert exe.is_file(), exe
    root = tk.Tk()
    root.geometry("320x240+0+0")
    frame = tk.Frame(root, bg="black")
    frame.pack(fill="both", expand=True)
    root.update()
    events: queue.Queue = queue.Queue()
    with tempfile.TemporaryDirectory() as temp:
        sample = Path(temp) / "prova.wav"
        with wave.open(str(sample), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(22050)
            w.writeframes(b"\x00\x10" * 22050)
        proc = subprocess.Popen([str(exe), str(frame.winfo_id()), str(Path(temp) / "wv2")],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                                encoding="utf-8")
        threading.Thread(target=lambda: [events.put(line.strip()) for line in proc.stdout],
                         daemon=True).start()
        seen, started = [], time.monotonic()
        sent = False
        while time.monotonic() - started < 60:
            root.update()
            try:
                line = events.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                seen.append(json.loads(line))
            except ValueError:
                continue
            kinds = {e.get("ev") for e in seen}
            if "page" in kinds and not sent:
                proc.stdin.write(json.dumps({"cmd": "volume", "value": 40}) + "\n")
                proc.stdin.write(json.dumps({"cmd": "file", "path": str(sample)}) + "\n")
                proc.stdin.flush()
                sent = True
            if sent and ("state" in kinds or "error" in kinds) and time.monotonic() - started > 3:
                break
        try:
            proc.stdin.write(json.dumps({"cmd": "quit"}) + "\n")
            proc.stdin.flush()
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        root.destroy()
    kinds = [e.get("ev") for e in seen]
    print(json.dumps({"events": seen[:12], "seconds": round(time.monotonic() - started, 1)}))
    assert "ready" in kinds and "page" in kinds, kinds
    assert not any(e.get("code") == "webview2" for e in seen), seen
    print("VIDEO_HOST_SMOKE_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
