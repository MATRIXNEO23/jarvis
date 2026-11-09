"""Build and verify the F5 test candidate ZIP (split KoboldCpp no-AVX2 bundle).

Windows only. Selects tracked runtime files with the same rules as the 014
builder, adds the pinned upstream ``koboldcpp.py`` with only the DLLs the
no-AVX2 route loads, the upstream licence, a notice and ``VERSIONE.json``
(SHA-256 of every file). Existing builds are untouched. The profile name is
unchanged (Jarvis-Gemma-Trial) so settings, chats and memory are preserved.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import zipfile

UPSTREAM_COMMIT = "6d2fedf8624e5f05926af3191f9efdcb13c4133c"
ENGINE_FILES = ("koboldcpp.py", "koboldcpp_common.dll", "koboldcpp_noavx2.dll",
                "backend_routes/koboldcpp_noavx2/koboldcpp_backend.dll", "LICENSE.md")
OPERATIONAL_GUIDES = frozenset({"docs/VOCE_OFFLINE.md", "docs/RECUPERO-IMPOSTAZIONI.md",
                                "file_access/LEGGIMI.md", "program_apps/LEGGIMI.md"})
STAMP = (2026, 11, 9, 0, 0, 0)


def include(p):
    parts = p.parts
    if not parts:
        return False
    if p.as_posix() in OPERATIONAL_GUIDES:
        return True
    if parts[0] in {".github", "tests", "tools", "docs", "Download", "upstream-kobold",
                    "koboldcpp-src", "probe-models", "dist", ".agents", "superpowers"}:
        return False
    if p.name in {"AGENTS.md", "RECUPERO.md", ".gitignore", "lumi_originale.png"}:
        return False
    if p.suffix.lower() in {".md", ".yml", ".yaml", ".toml"} and p.name != "README.md":
        return False
    return True


def notice(label):
    return f"""LUMI {label} - BUILD DI PROVA (motore KoboldCpp integrato, no-AVX2)
Estrai in una cartella NUOVA e avvia soltanto avvia_lumi.bat.
Non sovrascrivere ne cancellare la versione 014: resta quella stabile.
Profilo dati invariato (Jarvis-Gemma-Trial): impostazioni, chat e memoria restano.
Modelli GGUF non inclusi: seleziona il tuo (Gemma 2, Qwen2.5 o Qwen3) nelle impostazioni.
La famiglia del modello e riconosciuta dal file GGUF.
Cambio di modello, contesto o thread: salva e RIAVVIA Lumi (nessun ricaricamento a caldo).
Motore: KoboldCpp {UPSTREAM_COMMIT} compilato con w64devkit, licenza AGPL-3.0
(native_engine/LICENSE.md; sorgente: https://github.com/LostRuins/koboldcpp/tree/{UPSTREAM_COMMIT}).
Da collaudare sul Pavilion: velocita, RAM, voce, account. Nessuna garanzia di prestazioni.
"""


def git_files():
    out = subprocess.check_output(["git", "ls-files", "-z"])
    return [Path(os.fsdecode(p)) for p in out.split(b"\0") if p]


def build(engine_dir, number, out_dir, piper_dir=None):
    label = f"{number:03d}"
    root = f"Lumi-{label}/"
    engine = Path(engine_dir)
    entries = {}
    for p in git_files():
        if include(p) and p.is_file() and not p.is_symlink():
            data = p.read_bytes()
            if p.as_posix() == "avvia_lumi.bat":
                text = data.decode("utf-8").replace("Jarvis-AccessoFile-Trial", "Jarvis-Gemma-Trial")
                data = text.replace("LUMI // ACCESSO FILE", f"LUMI // {label}").encode("utf-8")
            entries[p.as_posix()] = data
    for name in ENGINE_FILES:
        entries["native_engine/" + name] = (engine / name).read_bytes()
    if piper_dir:
        # Slim Piper engine (tools/fetch_piper_engine.py): voice without installs.
        piper_root = Path(piper_dir)
        for path in sorted(piper_root.rglob("*")):
            if path.is_file():
                entries["voce_engine/piper/" + path.relative_to(piper_root).as_posix()] = path.read_bytes()
        if "voce_engine/piper/piper.exe" not in entries:
            raise SystemExit("piper.exe missing from --piper-engine")
    entries[f"LEGGIMI-BUILD-{label}.txt"] = notice(label).encode("utf-8")
    mandatory = {"jarvis.py", "avvia_lumi.bat", "local_model/chat_templates.py",
                 "local_model/native_factory.py"} | OPERATIONAL_GUIDES
    missing = mandatory - set(entries)
    if missing:
        raise SystemExit("Missing mandatory files: " + ", ".join(sorted(missing)))
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    version = dict(schema_version=1, build_number=number, build_label=label,
                   source_commit=source, upstream_koboldcpp_commit=UPSTREAM_COMMIT,
                   package_root=root.rstrip("/"), status="test_candidate_pc_pending",
                   files={n: hashlib.sha256(d).hexdigest() for n, d in sorted(entries.items())})
    entries["VERSIONE.json"] = (json.dumps(version, indent=2, sort_keys=True) + "\n").encode()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in sorted(entries):
            info = zipfile.ZipInfo(root + name, STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, entries[name])
    out = Path(out_dir) / f"Lumi-{label}-PROVA.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(buffer.getvalue())
    details = dict(file=out.name, bytes=out.stat().st_size,
                   sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
                   files=len(entries), source_commit=source)
    out.with_suffix(".json").write_text(json.dumps(details, indent=2), encoding="utf-8")
    return out, details


def run(args, cwd, profile, timeout=300):
    env = dict(os.environ, JARVIS_TRIAL_HOME=str(profile), PYTHONUTF8="1")
    proc = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)
    if proc.returncode != 0:
        raise SystemExit(f"FAILED {args[:3]}\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}")
    return proc.stdout


BOOT = '''import os,tkinter as tk,traceback
errors=[]
from settings import load_settings,save_settings
settings=load_settings();settings.update(auto_listen=False,gpt_enabled=False,telegram_enabled=False,tts_enabled=False)
save_settings(settings)
original=tk.Tk
class SmokeTk(original):
 def __init__(self,*a,**k):
  original.__init__(self,*a,**k)
  def callback_error(exc,value,tb):
   errors.append(str(value));traceback.print_exception(exc,value,tb)
  self.report_callback_exception=callback_error
  self.after(1500,lambda:self.tk.call(self.protocol('WM_DELETE_WINDOW')))
tk.Tk=SmokeTk
import jarvis
jarvis.main()
assert not errors,'Tk callback errors: '+repr(errors)
print('CLEAN_EXTRACTED_UI_BOOT_AND_CLOSE_OK')
'''


def verify(archive, model, tools_root):
    archive = Path(archive)
    details = json.loads(archive.with_suffix(".json").read_text(encoding="utf-8"))
    assert details["sha256"] == hashlib.sha256(archive.read_bytes()).hexdigest()
    report = {}
    with tempfile.TemporaryDirectory(prefix="jarvis-f5-candidate-") as temp:
        temp = Path(temp)
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            for info in z.infolist():
                name = PurePosixPath(info.filename)
                assert not name.is_absolute() and ".." not in name.parts and "\\" not in info.filename
            z.extractall(temp)
        package = next(temp.iterdir())
        version = json.loads((package / "VERSIONE.json").read_text(encoding="utf-8"))
        actual = {p.relative_to(package).as_posix() for p in package.rglob("*") if p.is_file()}
        assert actual == set(version["files"]) | {"VERSIONE.json"}, sorted(actual ^ set(version["files"]))
        for name, expected in version["files"].items():
            assert hashlib.sha256((package / name).read_bytes()).hexdigest() == expected, name
        assert not (package / "tests").exists() and not (package / "tools").exists()
        assert "Jarvis-Gemma-Trial" in (package / "avvia_lumi.bat").read_text(encoding="utf-8")
        profile = temp / "isolated-profile"
        report["imports"] = run([sys.executable, "-I", "-c",
            "import sys;sys.path.insert(0,'.');import jarvis,local_engine;"
            "from local_model import native_ui,native_factory,chat_templates;"
            "print('CLEAN_EXTRACTED_IMPORTS_OK')"], package, profile).strip()[-60:]
        engine = package / "native_engine"
        # Real engine proofs on the EXTRACTED package (tools stay outside it).
        env_tools = [sys.executable, "-m"]
        report["initializer"] = json.loads(run(env_tools + ["tools.f5n_initializer_smoke",
            str(engine), str(temp / "init.json")], tools_root, profile))["jarvis_initializer_verified"]
        report["boot"] = run([sys.executable, "-c", BOOT], package, profile).strip()[-45:]
        if model:
            out = run([sys.executable, "-c",
                "import sys,json;sys.path.insert(0,'.');"
                "from local_model.native_config import NativeModelConfig;"
                "from local_model.native_factory import create_native_provider;"
                f"c=NativeModelConfig(model=r'{Path(model).resolve()}',context_size=1024,max_output=32,"
                "threads=2,batch_threads=2,temperature=0.1,seed=123);"
                "p=create_native_provider(c,upstream_source='native_engine/koboldcpp.py');"
                "t=p.ask(prompt='Rispondi con una parola: capitale d Italia?',timeout=300);"
                "print(json.dumps({'answer':t.strip()[:80],'family':p.bridge.family}))"],
                package, profile, timeout=900)
            report["packaged_generation"] = json.loads(out.strip().splitlines()[-1])
        if (package / "voce_engine" / "piper" / "piper.exe").is_file():
            # Bundled voice engine on the EXTRACTED package: Paola from the
            # repository catalog, persistent piper.exe worker, effect, envelope.
            out = run([sys.executable, "-I", "-c",
                "import sys,json,time,wave;sys.path.insert(0,'.');import piper_voice as v;"
                "from pathlib import Path;"
                "f=Path(sys.argv[1]);v.download_voice('paola',folder=f);"
                "env=[];info={};"
                "keep=lambda p:info.update(s=wave.open(str(p)).getnframes());"
                "t=time.monotonic();"
                "v.speak_with_piper('Ciao, sono Lumi. Prova della voce inclusa.','paola',effect=0.25,"
                "folder=f,on_envelope=env.extend,player=keep);"
                "a=round(time.monotonic()-t,2);t=time.monotonic();"
                "v.speak_with_piper('Seconda frase, modello gia caricato.','paola',effect=0.25,"
                "folder=f,player=keep);b=round(time.monotonic()-t,2);"
                "used=any('piper.exe' in k for k in v._WORKERS);v.shutdown_workers();"
                "print(json.dumps({'bundled_exe':used,'frames':info.get('s',0),'envelope':len(env),"
                "'first_s_runner':a,'second_s_runner':b}))", str(profile / "voci")],
                package, profile, timeout=600)
            voice = json.loads(out.strip().splitlines()[-1])
            assert voice["bundled_exe"] and voice["frames"] > 0 and voice["envelope"] > 10, voice
            report["packaged_voice"] = voice
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("engine_dir")
    p.add_argument("--number", type=int, default=15)
    p.add_argument("--out", default="dist")
    p.add_argument("--model", help="GGUF used for the packaged generation proof")
    p.add_argument("--piper-engine", help="slim Piper folder from tools/fetch_piper_engine.py")
    a = p.parse_args(argv)
    if os.name != "nt":
        raise SystemExit("Windows only.")
    archive, details = build(a.engine_dir, a.number, a.out, a.piper_engine)
    report = verify(archive, a.model, Path(__file__).resolve().parents[1])
    details["verification"] = report
    archive.with_suffix(".json").write_text(json.dumps(details, indent=2, ensure_ascii=False),
                                            encoding="utf-8")
    print(json.dumps(details, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
