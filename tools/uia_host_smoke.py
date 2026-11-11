"""Prova CI (Windows): LumiControl.exe legge davvero gli elementi di una finestra Tk
e il Controllo PC trova la finestra, ci passa e clicca il pulsante tramite Windows."""
from __future__ import annotations

import sys
import time
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
    # Finestra di prova WinForms in un altro processo: dichiara a Windows i nomi
    # dei controlli (Tk no: i suoi pulsanti risultano senza nome a UI Automation).
    import os
    import tempfile
    marker = Path(tempfile.gettempdir()) / "lumi_uia_click.txt"
    marker.unlink(missing_ok=True)
    ps = (
        "Add-Type -AssemblyName System.Windows.Forms;"
        "$f=New-Object Windows.Forms.Form;$f.Text='Prova Lumi Controllo';$f.Width=360;$f.Height=200;"
        "$t=New-Object Windows.Forms.TextBox;$t.AccessibleName='Cerca';$t.Top=10;$t.Left=10;$t.Width=200;"
        "$b=New-Object Windows.Forms.Button;$b.Text='Saluta';$b.Top=60;$b.Left=10;"
        f"$b.Add_Click({{Set-Content -Path '{marker}' -Value ('CLICCATO '+$t.Text);$f.Close()}});"
        "$f.Controls.Add($t);$f.Controls.Add($b);"
        "$k=New-Object Windows.Forms.Timer;$k.Interval=40000;$k.Add_Tick({$f.Close()});$k.Start();"
        "[void]$f.ShowDialog()")
    proc = subprocess.Popen(["powershell", "-NoProfile", "-STA", "-Command", ps])
    try:
        hwnd = None
        for _ in range(100):
            found = [w for w in windows.open_windows() if w["title"] == "Prova Lumi Controllo"]
            if found:
                hwnd = found[0]["hwnd"]
                break
            time.sleep(0.2)
        assert hwnd, "finestra di prova non trovata in open_windows()"
        items = list_elements(hwnd)
        print("elementi:", items)
        assert any(i["type"] == "Button" and i["name"] == "Saluta" for i in items), items
        assert any(i["type"] == "Edit" and i["name"] == "Cerca" for i in items), items
        service = ControlService(lambda: True, ROOT / "uia-proof-data")
        service.settings["confirm_times"] = 0
        print(service.handle("switch", {"window": "prova lumi"}))
        print(service.handle("type_in", {"text": "ciao Lumi", "target": "Cerca",
                                          "window": "prova lumi"}))
        print(service.handle("click", {"target": "Saluta", "window": "prova lumi"}))
        for _ in range(50):
            if marker.exists():
                break
            time.sleep(0.2)
        text = marker.read_text(encoding="utf-8", errors="replace").strip() if marker.exists() else ""
        print("finestra di prova:", text)
        assert text.startswith("CLICCATO"), "il clic non è arrivato al pulsante"
        assert "ciao Lumi" in text, "il testo non è stato scritto nel campo Cerca"
        print("UIA PROOF OK")
        return 0
    finally:
        if proc.poll() is None:
            proc.kill()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
