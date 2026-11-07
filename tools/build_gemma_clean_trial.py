"""Prepare the isolated Gemma Windows trial package from tracked runtime files."""
from pathlib import Path
import hashlib, os, subprocess, zipfile

root=Path(".")
launcher=root/"avvia_jarvis.bat"
s=launcher.read_text(encoding="utf-8")
s=s.replace("Jarvis-AccessoFile-Trial","Jarvis-Gemma-Trial").replace("JARVIS // ACCESSO FILE","JARVIS // GEMMA")
launcher.write_text(s,encoding="utf-8")
readme="""JARVIS GEMMA - PROVA ISOLATA
1. Estrai in una cartella nuova, senza sovrascrivere Jarvis stabile.
2. Avvia avvia_jarvis.bat con Python 3.11/3.12 x64 e dipendenze installate.
3. In Impostazioni > GPT e memoria > Configura Gemma locale seleziona il tuo GGUF.
4. Premi Salva, poi Prova generazione: verra mostrata la risposta o l'errore.
5. DLL CPU no-AVX2 inclusa, non serve koboldcpp.exe.
Il GGUF non e incluso. FunctionGemma 270M non e ancora verificato su Pavilion.
"""
entries=[Path(os.fsdecode(p)) for p in subprocess.check_output(["git","ls-files","-z"]).split(b"\0") if p]
def include(p):
    parts=p.parts
    if not parts: return False
    if parts[0] in {".github","tests","tools","docs","Download","upstream-kobold"}: return False
    if p.name in {"AGENTS.md","RECUPERO.md"}: return False
    if p.suffix.lower() in {".md",".yml",".yaml",".toml"} and p.name!="README.md": return False
    return p.is_file() and not p.is_symlink()
entries=[p for p in entries if include(p)]
mandatory={"jarvis.py","avvia_jarvis.bat","local_model/native_ui.py","local_model/native_factory.py"}
assert mandatory.issubset({p.as_posix() for p in entries})
native=root/"upstream-kobold"
assert (native/"koboldcpp.py").is_file()
assert (native/"koboldcpp_noavx2.dll").is_file()
name="Jarvis-Gemma-PROVA-CORRETTA.zip"
with zipfile.ZipFile(name,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in entries:
        z.write(p,"Jarvis-Gemma/"+p.as_posix())
    for n in ("koboldcpp.py","koboldcpp_noavx2.dll"):
        z.write(native/n,"Jarvis-Gemma/native_engine/"+n)
    z.writestr("Jarvis-Gemma/LEGGIMI-GEMMA-TEST.txt",readme)
with zipfile.ZipFile(name) as z:
    assert z.testzip() is None
    assert len(z.namelist()) < 180
print(name,Path(name).stat().st_size,hashlib.sha256(Path(name).read_bytes()).hexdigest())
