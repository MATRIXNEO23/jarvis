"""Prova CI (Windows): LumiControl.exe legge davvero gli elementi di una finestra Tk
e il Controllo PC trova la finestra, ci passa e clicca il pulsante tramite Windows."""
from __future__ import annotations

import sys
import time
import tkinter as tk
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main(out_dir: str) -> int:
    import shutil
    target = ROOT / "controllo_pc" / "uia_bin"
    target.mkdir(parents=True, exist_ok=True)
    for path in Path(out_dir).iterdir():
        if path.is_file():
            shutil.copy2(path, target / path.name)
    from controllo_pc import windows
    from controllo_pc.service import ControlService, list_elements
    import subprocess
    # Finestra di prova in un altro processo (Lumi esclude le proprie finestre).
    script = ("import tkinter as tk\nr=tk.Tk();r.title('Prova Lumi Controllo')\n"
              "e=tk.Entry(r);e.pack()\n"
              "tk.Button(r,text='Saluta',command=lambda:(print('CLICCATO',e.get(),flush=True),"
              "r.after(300,r.destroy))).pack()\nr.after(20000,r.destroy)\nr.mainloop()\n")
    proc = subprocess.Popen([sys.executable, "-c", script], stdout=subprocess.PIPE, text=True)
    try:
        hwnd = None
        for _ in range(50):
            found = [w for w in windows.open_windows() if w["title"] == "Prova Lumi Controllo"]
            if found:
                hwnd = found[0]["hwnd"]
                break
            time.sleep(0.2)
        assert hwnd, "finestra di prova non trovata in open_windows()"
        items = list_elements(hwnd)
        print("elementi:", items)
        assert any(i["type"] == "Button" and i["name"] == "Saluta" for i in items), items
        service = ControlService(lambda: True, ROOT / "uia-proof-data")
        service.settings["confirm_times"] = 0
        print(service.handle("switch", {"window": "prova lumi"}))
        print(service.handle("click", {"target": "Saluta", "window": "prova lumi"}))
        out, _ = proc.communicate(timeout=15)
        print("finestra di prova:", out.strip())
        assert "CLICCATO" in out, "il clic non è arrivato al pulsante"
        print("UIA PROOF OK")
        return 0
    finally:
        if proc.poll() is None:
            proc.kill()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
