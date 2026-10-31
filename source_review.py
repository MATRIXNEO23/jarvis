"""Bounded, offline and read-only static suggestions for JARVIS source code.

All observations are heuristics. This module NEVER imports or executes the
files it inspects, runs tests, accesses personal data or makes network calls.
It does not claim that a possible risk is a confirmed bug or vulnerability.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Callable


@dataclass(frozen=True)
class Improvement:
    priority: str
    file: str
    line: int
    observation: str
    suggestion: str
    check: str
    certainty: str = "segnale statico"


_SEVERITY = {"alta": 0, "media": 1, "bassa": 2}
_MAX_RECOMMENDATIONS = 8
_MIN_LARGE_FUNCTION = 150
_MIN_COMPLEX_BRANCHES = 25
_MIN_LARGE_MODULE = 850


def _is_silent_exception(handler: ast.ExceptHandler) -> bool:
    """Catch-and-ignore is a review signal, not proof of faulty behavior."""
    if handler.type is None:
        return len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass)
    if isinstance(handler.type, ast.Name) and handler.type.id in (
            "Exception", "BaseException"):
        return len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass)
    return False


def _shell_true_call(node: ast.Call) -> bool:
    return any(keyword.arg == "shell"
               and isinstance(keyword.value, ast.Constant)
               and keyword.value.value is True for keyword in node.keywords)


def _priority(record: Improvement):
    return (_SEVERITY.get(record.priority, 9),
            record.file.casefold(), record.line, record.observation)


def review_sources(source_root: Path, files: list[Path], *,
                   module: str = "", max_bytes: int = 260_000,
                   progress: Callable[[str,int,int],None] | None = None
                   ) -> tuple[Improvement, ...]:
    """Produce evidence-linked suggestions from bounded AST only.

    Callers supply an already validated root and list of regular source
    files. This function rechecks containment and symlinks independently.
    It purposely does not read .json, .env, credentials, databases, logs or
    user documents. It does not print source lines or string literals.
    """
    root = Path(source_root).resolve(strict=True)
    candidates: list[Improvement] = []
    inspected = 0
    tests_found = 0

    scan=files[:140]
    total=len(scan)
    for index,file in enumerate(scan,1):
        if progress is not None:
            progress("consigli",index-1,total)
        if file.suffix.casefold() != ".py" or file.is_symlink():
            continue
        try:
            relative = file.relative_to(root).as_posix()
        except ValueError:
            continue
        if module and relative.casefold() != module.casefold():
            continue
        if any(part in (".venv", "__pycache__", ".git", "venv", "projects",
                         "runtime") for part in Path(relative).parts[:-1]):
            continue
        if file.stat().st_size > max_bytes:
            continue
        try:
            tree = ast.parse(file.read_text(encoding="utf-8"),
                             filename=relative)
        except (SyntaxError, OSError, UnicodeError):
            # Syntax and I/O errors are reported by self_diagnostics itself.
            continue
        inspected += 1
        is_test = relative.startswith("tests/test_")
        if is_test:
            tests_found += 1
        functions = [node for node in ast.walk(tree)
                     if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        n_lines = max((getattr(node, "end_lineno", 1) for node in tree.body),
                      default=0)
        if not is_test and not module and n_lines >= _MIN_LARGE_MODULE:
            candidates.append(Improvement(
                "media", relative, 1,
                f"Modulo particolarmente esteso ({n_lines} righe).",
                "Valutare una suddivisione in componenti più piccoli, "
                "mantenendo interfacce e compatibilità esistenti.",
                "Eseguire i test di regressione delle funzionalità coinvolte."))

        for function in functions:
            if is_test:
                continue
            line = getattr(function, "lineno", 0)
            end = getattr(function, "end_lineno", line)
            length = end - line + 1
            if length >= _MIN_LARGE_FUNCTION:
                candidates.append(Improvement(
                    "media", relative, line,
                    f"Funzione {function.name} lunga {length} righe.",
                    "Valutare l'estrazione di responsabilità distinte "
                    "in funzioni più piccole, senza cambiare il comportamento.",
                    "Aggiungere casi di prova prima di rifattorizzare."))
            branches = sum(isinstance(node, (ast.If, ast.For, ast.While,
                                           ast.Try, ast.IfExp, ast.Match))
                           for node in ast.walk(function))
            if branches >= _MIN_COMPLEX_BRANCHES:
                candidates.append(Improvement(
                    "media", relative, line,
                    f"Funzione {function.name} contiene {branches} "
                    "punti di diramazione o gestione eccezioni.",
                    "Considerare test sui percorsi alternativi e separazione "
                    "delle responsabilità più complesse.",
                    "Verificare anche casi d'errore, annullamento e riavvio."))

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and _is_silent_exception(node):
                candidates.append(Improvement(
                    "media", relative, node.lineno,
                    "Gestione di eccezione che potrebbe ignorare l'errore.",
                    "Verificare se è corretto ignorarlo oppure registrare "
                    "l'errore in modo controllato, senza dati sensibili.",
                    "Simulare il fallimento in un test isolato."))
            if isinstance(node, ast.Call) and _shell_true_call(node):
                # Static signal only: never assert injection vulnerability.
                candidates.append(Improvement(
                    "alta", relative, node.lineno,
                    "Una chiamata usa shell=True.",
                    "Esaminare se una shell è indispensabile; valutare "
                    "argomenti strutturati e dati non influenzabili dall'utente.",
                    "Revisionare i parametri e provare input non attendibili "
                    "in un test isolato."))

    if progress is not None:
        progress("consigli",total,total)
    if inspected and not module and tests_found == 0:
        candidates.append(Improvement(
            "media", "tests/", 0,
            "Non risultano file test Python nella cartella esaminata.",
            "Aggiungere test locali che coprano i flussi critici.",
            "Provare creazione documenti, riavvio e recupero progetti."))

    # Unique, ordered, bounded; all signals require a human review.
    dedup: dict[tuple[str, int, str], Improvement] = {}
    for item in candidates:
        dedup[(item.file, item.line, item.observation)] = item
    result=[]
    count_by_file={}
    # Favor several independent actionable areas, not eight observations
    # from one very long function in jarvis.py.
    for item in sorted(dedup.values(), key=_priority):
        if count_by_file.get(item.file,0)>=2:
            continue
        result.append(item)
        count_by_file[item.file]=count_by_file.get(item.file,0)+1
        if len(result)==_MAX_RECOMMENDATIONS:
            break
    return tuple(result)


def format_improvements(items: tuple[Improvement, ...]) -> str:
    if not items:
        return ("Non ho trovato segnali statici che giustifichino una "
                "modifica precisa. Questo non dimostra che il programma sia "
                "privo di problemi: per i bug funzionali servono test reali.")
    result = ["Possibili miglioramenti, da verificare prima di modificare:"]
    for index, item in enumerate(items, 1):
        where = item.file + (":" + str(item.line) if item.line else "")
        result.append(
            f"{index}. Priorità {item.priority} — {where}\n"
            f"   Osservazione: {item.observation}\n"
            f"   Proposta: {item.suggestion}\n"
            f"   Verifica: {item.check}")
    result.append("Sono ipotesi basate su analisi statica, non bug confermati. "
                  "Nessun file è stato modificato o eseguito.")
    return "\n".join(result)
