"""Bounded, offline, read-only LUMI source inventory and static diagnostics.

Never executes, imports, modifies, uploads or evaluates application sources.
The static audit cannot certify safety or verify runtime correctness.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Callable
import re
import stat

from source_review import (
    Improvement, format_improvements, review_sources,
    SOURCE_EXCLUDED_DIRECTORIES, _source_metadata, _hidden_source_directory,
)

_SOURCE_SUFFIXES = frozenset({".py",".bat",".ps1",".mjs"})
_RUNTIME_FOLDERS = ("local_model", "file_access", "program_apps", "sveglia", "musica", "controllo_pc", "telegram_addon", "componenti", "controllo_comune", "lumi_parti")
_MAX_FILES = 240
_MAX_DIRECTORIES = 140
_MAX_BYTES = 260_000
_MODULE = re.compile(r"[A-Za-z0-9_]{1,72}\.py\Z",re.I)

# Explicit multi-clause requests must reach local inspection rather than GPT.
# The allowed tail is intentionally narrow: avoid interpreting quotations,
# negated instructions or arbitrary discussion of diagnostics as commands.
_SELF_REVIEW_COMPOUND = re.compile(
    r"^(?:(?:puoi|potresti)\s+)?"
    r"(?:(?:fai|fammi|fatti|esegui|effettua|prepara|avvia|fare)\s+"
    r"(?:(?:un|una|un['’])\s*)?(?:auto[\s-]?diagnosi|diagnosi)"
    r"|(?:autoanalizza|analizza|controlla|verifica|esamina|studia)\s+"
    r"(?:(?:i|il|lo)\s+)?(?:(?:tuoi|tuo)\s+)?"
    r"(?:funzionamento|codice|programma|file|sorgenti))"
    r"(?:\s+(?:del|della|dei|delle|sul|sui|di)\s+"
    r"(?:(?:tuo|tuoi|tua|tue)\s+)?"
    r"(?:funzionamento|codice|programma|file|sorgenti|funzioni|moduli|lumi))?"
    r"(?:\s+e\s+(?:"
    r"(?:proponi|suggerisci|dimmi|indicami|consigliami)\s+"
    r"(?:(?:eventuali|possibili|dei|delle|qualche)\s+)*"
    r"(?:fix|correzioni|miglioramenti|soluzioni|problemi)"
    r"|(?:suggerisci|dimmi|indicami|consigliami)\s+"
    r"come\s+(?:migliorare|migliorarti|correggere\s+gli\s+errori)"
    r"))?$",re.I,
)

@dataclass(frozen=True)
class SourceAudit:
    summary: str
    detail: str
    findings: tuple[str,...]
    recommendations: tuple[Improvement,...] = ()

def _source_list(root: Path, *, data_root=None, notices=None) -> list[Path]:
    """Bounded approved code only, then direct test files; never profile data."""
    root = Path(root).resolve(strict=True)
    data = Path(data_root).resolve() if data_root is not None else None
    files = []
    directories = 0

    def note(message):
        if notices is not None and message not in notices:
            notices.append(message)

    if data is not None and root.is_relative_to(data):
        note("Inventario escluso: la cartella del programma è nella cartella dati.")
        return files

    def allowed(path):
        physical = path.resolve(strict=True)
        return physical.is_relative_to(root) and not (
            data is not None and physical.is_relative_to(data))

    def walk(start, recursive):
        nonlocal directories
        pending = [start]
        while pending and len(files) < _MAX_FILES:
            if directories >= _MAX_DIRECTORIES:
                note("Inventario limitato a 140 directory di codice; copertura parziale.")
                return
            directory = pending.pop()
            try:
                info = _source_metadata(directory)
                if (info is None or not stat.S_ISDIR(info.st_mode)
                        or (directory != root and _hidden_source_directory(info))
                        or not allowed(directory)):
                    continue
            except FileNotFoundError:
                continue  # An optional runtime folder need not be installed.
            except OSError:
                note(directory.relative_to(root).as_posix() + ": cartella non disponibile.")
                continue
            directories += 1
            try:
                entries = sorted(directory.iterdir(), key=lambda p: p.name.casefold())
            except OSError:
                note(directory.relative_to(root).as_posix() + ": cartella non disponibile.")
                continue
            children = []
            for item in entries:
                if len(files) >= _MAX_FILES:
                    break
                if item.name.startswith("."):
                    continue
                try:
                    info = _source_metadata(item)
                    if info is None:
                        continue
                    if stat.S_ISDIR(info.st_mode):
                        if (recursive and item.name.casefold() not in SOURCE_EXCLUDED_DIRECTORIES
                                and not _hidden_source_directory(info) and allowed(item)):
                            children.append(item)
                    elif (stat.S_ISREG(info.st_mode)
                          and item.suffix.casefold() in _SOURCE_SUFFIXES and allowed(item)):
                        files.append(item)
                except OSError:
                    note(item.relative_to(root).as_posix() + ": sorgente non disponibile.")
            pending.extend(reversed(children))

    walk(root, False)
    for folder in _RUNTIME_FOLDERS:
        walk(root / folder, True)
    walk(root / "tests", False)
    if len(files) >= _MAX_FILES:
        note("Inventario limitato a 240 file; priorità ai moduli runtime, poi ai test.")
    return files

def diagnostic_request(text: str) -> tuple[str,str] | None:
    """Recognize deliberate local self-analysis requests, not general questions."""
    if not isinstance(text,str) or len(text)>450:
        return None
    phrase=re.sub(r"^(?:(?:ehi|hey|ok)\s+)?lumi[\s,.:;-]+","",
                  text.strip(" ,.!?;:"),flags=re.I).casefold()
    phrase=" ".join(phrase.split())
    if re.fullmatch(r"(?:(?:apri|mostra|avvia)\s+(?:la\s+)?)?"
                    r"(?:diagnostica|diagnosi|stato)\s+(?:dei\s+)?servizi", phrase):
        return ("services", "")
    # Vosk commonly separates auto/diagnosi or inserts an article.
    # Normalize these precise forms, not arbitrary speech about diagnosis.
    phrase=re.sub(r"\bauto[\s-]+diagnos[ie]\b","autodiagnosi",phrase)
    phrase=re.sub(r"\bauto[\s-]+analisi\b","autoanalisi",phrase)
    phrase=re.sub(r"\b(?:l['’]|una?\s+)autodiagnosi\b",
                  "un'autodiagnosi",phrase)
    if re.fullmatch(
            r"(?:dove\s+(?:sono|tieni)\s+(?:i\s+)?tuoi\s+file|"
            r"mostra(?:mi)?\s+(?:i\s+)?tuoi\s+file|"
            r"(?:dove|in\s+quale\s+cartella)\s+(?:si\s+trova|è)\s+lumi|"
            r"apri\s+la\s+cartella\s+(?:del\s+)?programma)",phrase):
        return ("paths","")
    if re.fullmatch(
            r"(?:autoanalizzati|autovalutati|"
            r"fai(?:mi)?\s+(?:un[ao]?\s+|un['’])?autodiagnosi|"
            r"(?:fai|prepara|esegui)\s+(?:un[ao]?\s+|un['’])?"
            r"(?:rapporto\s+di\s+)?autodiagnosi|"
            r"(?:analizza|esamina|studia)\s+(?:te\s+stesso|te\s+stessa)|"
            r"(?:come\s+(?:potresti|puoi|pensi\s+di)\s+migliorarti)|"
            r"(?:(?:dimmi|suggerisci|consigliami)\s+come\s+"
            r"(?:potresti|puoi)\s+migliorarti)|"
            r"(?:quali\s+(?:parti|aspetti)\s+(?:del\s+tuo\s+codice\s+)?"
            r"(?:puoi|potresti)\s+migliorare)|"
            r"(?:suggerisci|proponi|consiglia(?:mi)?)\s+"
            r"(?:(?:dei|delle|possibili)\s+)?migliorament[io]"
            r"(?:\s+(?:al\s+tuo\s+codice|per\s+te\s+stesso))?|"
            r"(?:controlla|analizza|esamina)\s+(?:i\s+)?tuoi\s+file"
            r"\s+e\s+(?:proponi|suggerisci)\s+miglioramenti)",phrase):
        return ("review","")
    if re.fullmatch(
            r"(?:analizza|esamina|controlla|verifica|studia)\s+"
            r"(?:(?:il|i)\s+)?(?:tuo\s+)?(?:codice|programma|file|sorgenti)"
            r"(?:\s+(?:di\s+lumi))?"
            r"|(?:fai|esegui|prepara)\s+(?:una\s+)?"
            r"(?:diagnosi|analisi|revisione)\s+(?:del\s+)?"
            r"(?:tuo\s+)?(?:codice|programma|sorgenti)"
            r"|(?:quali\s+errori|cosa\s+non\s+funziona)\s+"
            r"(?:ci\s+sono\s+)?(?:nel\s+)?(?:tuo\s+)?(?:codice|programma)"
            r"|suggerisci\s+(?:delle\s+)?correzioni\s+(?:al\s+)?(?:tuo\s+)?codice"
            ,phrase):
        return ("overview","")
    # Keep legacy simple commands ('analizza il tuo codice') stable.
    # Only new compound forms need the extended review intent.
    if _SELF_REVIEW_COMPOUND.fullmatch(phrase):
        return ("review","")
    module=re.fullmatch(
        r"(?:analizza|esamina|controlla|studia|mostra)\s+"
        r"(?:(?:il\s+)?(?:file|modulo)\s+)?([a-z0-9_]{1,72}\.py)",phrase)
    if module:
        return ("module",module.group(1))
    return None

def inspect_jarvis(*,source_root: Path | None=None,
                   data_root: Path | None=None,
                   module: str="",
                   progress: Callable[[str,int,int],None] | None = None
                   ) -> SourceAudit:
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
    inventory_notes=[]
    files=_source_list(root,data_root=data,notices=inventory_notes)
    coverage=[message for message in inventory_notes if message.startswith("Inventario ")]
    coverage_detail=("\nCopertura dell'inventario: " + " ".join(coverage)) if coverage else ""
    if progress is not None:
        progress("inventario",len(files),len(files))
    findings=list(inventory_notes)
    modules=[]
    kinds={}
    targets=[]
    for file in files:
        kinds[file.suffix.casefold()]=kinds.get(file.suffix.casefold(),0)+1
        relative=file.relative_to(root).as_posix()
        if module and relative.casefold()!=module.casefold():
            continue
        targets.append((file,relative))
    for index,(file,relative) in enumerate(targets,1):
        if progress is not None:
            progress("sintassi",index-1,len(targets))
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
    if progress is not None:
        progress("sintassi",len(targets),len(targets))
    if module and not targets:
        return SourceAudit("Modulo non trovato nell'inventario.",
              "Il controllo non ha individuato il modulo richiesto tra i sorgenti accessibili."
              + coverage_detail,
              ("Controlla il nome e i limiti del controllo; nessun file è stato modificato.",))
    if not module and not files:
        return SourceAudit("Nessun sorgente del programma trovato.",
               "Controlla la cartella di installazione. Nessun file modificato." + coverage_detail,
               tuple(inventory_notes) or ("I file del programma non sono disponibili qui.",))
    recommendations=review_sources(root,files,module=module,
                                    max_bytes=_MAX_BYTES,progress=progress)
    if progress is not None:
        progress("completamento",1,1)
    if module:
        _,names,lines=modules[0] if modules else (module,(),0)
        summary=("Modulo "+module+": "+str(lines)+" righe, "+
                 str(len(names))+" definizioni principali. "+
                 str(len(findings))+" problemi di lettura o sintassi, "+
                 str(len(recommendations))+" miglioramenti da valutare.")
        detail=("Cartella del programma: "+str(root)+"\n"
                "Definizioni: "+(", ".join(names[:18]) if names else
                    "(nessuna definizione leggibile)")
                +("\nUlteriori definizioni omesse." if len(names)>18 else ""))
    else:
        summary=(str(len(files))+" file sorgente individuati: "+
                 ", ".join(ext+" "+str(kinds[ext]) for ext in sorted(kinds))+
                 ". Python verificati staticamente: "+str(len(modules))+
                 ". Segnalazioni statiche: "+str(len(findings))+
                 ". Miglioramenti da valutare: "+str(len(recommendations))+".")
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
    # Coverage must remain visible even when twelve earlier I/O findings fill
    # the compact observations list; never imply a complete inventory.
    detail += coverage_detail
    suggestions=(tuple(findings[:12]) if findings else
         ("Nessun errore di sintassi individuato dai controlli statici.",
          "Questo controllo non verifica funzioni in esecuzione, malware o bug logici.",
          "Per proporre patch servono test di riproduzione e revisione del codice qui in chat."))
    return SourceAudit(summary,detail,suggestions,recommendations)

def format_audit(audit: SourceAudit) -> str:
    return (audit.summary+"\n"+audit.detail+
            "\nOsservazioni:\n- "+"\n- ".join(audit.findings)+
            "\n\n"+format_improvements(audit.recommendations))[:6200]
