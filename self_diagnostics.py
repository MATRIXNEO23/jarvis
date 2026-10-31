"""Bounded, offline, read-only JARVIS source inventory and static diagnostics.

Never executes, imports, modifies, uploads or evaluates application sources.
The static audit cannot certify safety or verify runtime correctness.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
import re

_SOURCE_SUFFIXES = frozenset({".py",".bat",".ps1",".mjs"})
_IGNORE = frozenset({".git",".venv","venv","__pycache__","node_modules",
                     "runtime","projects","reports","downloads"})
_MAX_FILES = 140
_MAX_BYTES = 260_000
_MODULE = re.compile(r"[A-Za-z0-9_]{1,72}\.py\Z",re.I)

@dataclass(frozen=True)
class SourceAudit:
    summary: str
    detail: str
    findings: tuple[str,...]

def _source_list(root: Path) -> list[Path]:
    """Only installed source files, and one level of tests; never AppData."""
    files=[]
    for sub in (root,root/"tests"):
        if sub != root and (not sub.is_dir() or sub.is_symlink()):
            continue
        for item in sorted(sub.iterdir(),key=lambda p:p.name.casefold()):
            if (len(files)>=_MAX_FILES or item.is_symlink() or not item.is_file()
                    or item.suffix.casefold() not in _SOURCE_SUFFIXES
                    or any(part.casefold() in _IGNORE for part in item.parts)):
                continue
            files.append(item)
    return files

def diagnostic_request(text: str) -> tuple[str,str] | None:
    """Recognize deliberate local self-analysis requests, not general questions."""
    if not isinstance(text,str) or len(text)>220:
        return None
    phrase=re.sub(r"^(?:(?:ehi|hey|ok)\s+)?jarvis[\s,.:;-]+","",
                  text.strip(" ,.!?;:"),flags=re.I).casefold()
    if re.fullmatch(
            r"(?:dove\s+(?:sono|tieni)\s+(?:i\s+)?tuoi\s+file|"
            r"mostra(?:mi)?\s+(?:i\s+)?tuoi\s+file|"
            r"(?:dove|in\s+quale\s+cartella)\s+(?:si\s+trova|è)\s+jarvis|"
            r"apri\s+la\s+cartella\s+(?:del\s+)?programma)",phrase):
        return ("paths","")
    if re.fullmatch(
            r"(?:analizza|esamina|controlla|verifica|studia)\s+"
            r"(?:(?:il|i)\s+)?(?:tuo\s+)?(?:codice|programma|file|sorgenti)"
            r"(?:\s+(?:di\s+jarvis))?"
            r"|(?:fai|esegui|prepara)\s+(?:una\s+)?"
            r"(?:diagnosi|analisi|revisione)\s+(?:del\s+)?"
            r"(?:tuo\s+)?(?:codice|programma|sorgenti)"
            r"|(?:quali\s+errori|cosa\s+non\s+funziona)\s+"
            r"(?:ci\s+sono\s+)?(?:nel\s+)?(?:tuo\s+)?(?:codice|programma)"
            r"|suggerisci\s+(?:delle\s+)?correzioni\s+(?:al\s+)?(?:tuo\s+)?codice"
            ,phrase):
        return ("overview","")
    module=re.fullmatch(
        r"(?:analizza|esamina|controlla|studia|mostra)\s+"
        r"(?:(?:il\s+)?(?:file|modulo)\s+)?([a-z0-9_]{1,72}\.py)",phrase)
    if module:
        return ("module",module.group(1))
    return None

def inspect_jarvis(*,source_root: Path | None=None,
                   data_root: Path | None=None,
                   module: str="") -> SourceAudit:
    root=(Path(source_root) if source_root is not None
          else Path(__file__).resolve().parent)
    # Pathlib resolve prevents accidentally reporting path traversal.
    root=root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Cartella del programma non disponibile.")
    data=(Path(data_root) if data_root is not None
          else Path.home()/".local"/"share"/"Jarvis")
    if module and not _MODULE.fullmatch(module):
        raise ValueError("Il modulo deve essere un nome Python semplice.")
    files=_source_list(root)
    findings=[]
    modules=[]
    kinds={}
    targets=[]
    for file in files:
        kinds[file.suffix.casefold()]=kinds.get(file.suffix.casefold(),0)+1
        relative=file.relative_to(root).as_posix()
        if module and relative.casefold()!=module.casefold():
            continue
        targets.append((file,relative))
    for file,relative in targets:
        try:
            size=file.stat().st_size
            if size>_MAX_BYTES:
                findings.append(relative+": troppo grande per la verifica statica limitata")
                continue
            if file.suffix.casefold()!=".py":
                continue
            # Syntax check is AST parsing only, NEVER compile/exec/run.
            source=file.read_text(encoding="utf-8")
            tree=ast.parse(source,filename=relative)
            funcs=[x.name for x in tree.body if isinstance(x,(ast.FunctionDef,
                         ast.AsyncFunctionDef,ast.ClassDef))]
            modules.append((relative,tuple(funcs),len(source.splitlines())))
        except (SyntaxError,UnicodeError,OSError) as exc:
            if isinstance(exc,SyntaxError):
                findings.append(relative+": sintassi non valida alla riga "+str(exc.lineno))
            else:
                findings.append(relative+": lettura o codifica non disponibile")
    if module and not targets:
        return SourceAudit("Modulo non trovato nel programma.",
              "Il modulo richiesto non è presente tra i file Python del programma.",
              ("Controlla il nome del modulo; nessun file è stato modificato.",))
    if not module and not files:
        return SourceAudit("Nessun sorgente del programma trovato.",
               "Controlla la cartella di installazione. Nessun file modificato.",
               ("I file del programma non sono disponibili qui.",))
    if module:
        _,names,lines=modules[0] if modules else (module,(),0)
        summary=("Modulo "+module+": "+str(lines)+" righe, "+
                 str(len(names))+" definizioni principali. "+
                 str(len(findings))+" segnalazioni statiche.")
        detail=("Cartella del programma: "+str(root)+"\n"
                "Definizioni: "+(", ".join(names[:18]) if names else
                    "(nessuna definizione leggibile)")
                +("\nUlteriori definizioni omesse." if len(names)>18 else ""))
    else:
        summary=(str(len(files))+" file sorgente individuati: "+
                 ", ".join(ext+" "+str(kinds[ext]) for ext in sorted(kinds))+
                 ". Python verificati staticamente: "+str(len(modules))+
                 ". Segnalazioni: "+str(len(findings))+".")
        important=("jarvis.py","workspace_memory.py","project_voice.py",
                   "managed_documents.py","telegram_bridge.py","gpt_client.py",
                   "voice_control.py")
        found={m[0] for m in modules}
        absent=[p for p in important if p not in found]
        if absent:
            findings.append("Moduli importanti non individuati: "+", ".join(absent))
        detail=("Cartella del programma: "+str(root)+"\n"
                "Cartella dati (se configurata): "+str(data)+"\n"
                "Moduli chiave trovati: "+", ".join(p for p in important if p in found)
                +"\nTest Python rilevati: "+
                str(sum(1 for m in modules if m[0].startswith("tests/test_"))))
    suggestions=(tuple(findings[:8]) if findings else
         ("Nessun errore di sintassi individuato dai controlli statici.",
          "Questo controllo non verifica funzioni in esecuzione, malware o bug logici.",
          "Per proporre patch servono test di riproduzione e revisione del codice qui in chat."))
    return SourceAudit(summary,detail,suggestions)

def format_audit(audit: SourceAudit) -> str:
    return (audit.summary+"\n"+audit.detail+
            "\nOsservazioni:\n- "+"\n- ".join(audit.findings))[:3600]
