"""Prepare the isolated Gemma Windows trial package from tracked runtime files."""
from pathlib import Path
import hashlib, os, subprocess, zipfile

root=Path(".")
ui=root/"local_model/native_ui.py"
s=ui.read_text(encoding="utf-8")
assert 'def test_model(self):' not in s
s=s.replace("import tkinter as tk\n", "import tkinter as tk\nimport threading\nfrom pathlib import Path\n",1)
s=s.replace('self.status = tk.StringVar(value="Modello disattivato finché non viene attivato esplicitamente.")','self.status = tk.StringVar(value="Salva il GGUF, poi premi Prova generazione. Nessun invio online.")')
s=s.replace('ttk.Button(buttons, text="Salva", command=self.save).pack(side="left")','ttk.Button(buttons, text="Salva", command=self.save).pack(side="left")\n        self.test_button = ttk.Button(buttons, text="Prova generazione", command=self.test_model)\n        self.test_button.pack(side="left", padx=6)')
s += '''
    def test_model(self):
        """Run one real native generation without using GPT online."""
        try:
            if not self.save():
                return
            if not self.current.model or not Path(self.current.model).is_file():
                raise ValueError("Seleziona prima un file GGUF esistente.")
            self.test_button.configure(state="disabled")
            self.status.set("Caricamento DLL e GGUF in corso...")
            def worker():
                try:
                    from .native_chat_adapter import NativeChatAdapter
                    from .native_conversation_session import NativeConversationSession
                    source = Path(__file__).resolve().parent.parent / "native_engine" / "koboldcpp.py"
                    session = NativeConversationSession(NativeChatAdapter(source))
                    try:
                        answer = session.ask("Presentati con una breve frase.", timeout=180)
                    finally:
                        session.stop()
                    result = "TEST RIUSCITO. Risposta: " + str(answer)[:200]
                except Exception as exc:
                    result = "TEST FALLITO: " + str(exc)[:300]
                def finish():
                    if self.window.winfo_exists():
                        self.status.set(result)
                        self.test_button.configure(state="normal")
                try:
                    self.window.after(0, finish)
                except RuntimeError:
                    pass
            threading.Thread(target=worker, daemon=True, name="jarvis-gemma-test").start()
        except (OSError, ValueError, TypeError) as exc:
            self.status.set("TEST FALLITO: " + str(exc))
'''
ui.write_text(s,encoding="utf-8")
factory=root/"local_model/native_factory.py"
s=factory.read_text(encoding="utf-8")
s=s.replace("import importlib.util\n","import importlib.util\nfrom dataclasses import replace\n",1)
s=s.replace("    source = Path(upstream_source).resolve(strict=True)","    if not config.dll:\n        bundled = Path(__file__).resolve().parent.parent / 'native_engine' / 'koboldcpp_noavx2.dll'\n        if not bundled.is_file():\n            raise FileNotFoundError('DLL KoboldCpp inclusa non trovata: ' + str(bundled))\n        config = replace(config, dll=str(bundled))\n    source = Path(upstream_source).resolve(strict=True)",1)
factory.write_text(s,encoding="utf-8")
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
