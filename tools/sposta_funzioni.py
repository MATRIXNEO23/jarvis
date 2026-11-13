"""Sposta funzioni annidate di main() (jarvis.py) in un modulo, con il codice invariato.

Uso: python tools/sposta_funzioni.py <modulo.py> <titolo> nome1 nome2 ...   (oppure --analizza)
Regole (docs/PIANO-DIVISIONE-JARVIS.md): solo funzioni dirette di main() senza nonlocal/global,
senza decoratori, non estratte dai test, senza nomi di main() nei valori predefiniti. I nomi di
main() che usano diventano d.nome (lumi_contesto.Vivo: valore sempre attuale).
"""
from __future__ import annotations

import ast
import builtins
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# --anche-test: sposta anche funzioni lette dai test tramite l'estrattore comune
# (tests/test_activity_status.py → callback), che cerca pure nei moduli spostati.
ANCHE_TEST = "--anche-test" in sys.argv
if ANCHE_TEST:
    sys.argv.remove("--anche-test")
JARVIS = ROOT / "jarvis.py"


def _load():
    src = JARVIS.read_text(encoding="utf-8")
    tree = ast.parse(src)
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    return src, tree, main


def _main_names(main):
    names = set()
    for st in main.body:
        if isinstance(st, (ast.FunctionDef, ast.ClassDef)):
            names.add(st.name)
            continue
        for x in ast.walk(st):
            if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Store):
                names.add(x.id)
            elif isinstance(x, (ast.Import, ast.ImportFrom)):
                for a in x.names:
                    names.add((a.asname or a.name).split(".")[0])
            elif isinstance(x, ast.arg):
                pass
    return names


def _module_names(tree):
    names = set()
    for st in tree.body:
        if isinstance(st, (ast.Import, ast.ImportFrom)):
            for a in st.names:
                names.add((a.asname or a.name).split(".")[0])
        elif isinstance(st, (ast.FunctionDef, ast.ClassDef)):
            names.add(st.name)
        elif isinstance(st, ast.Assign):
            for t in st.targets:
                for x in ast.walk(t):
                    if isinstance(x, ast.Name):
                        names.add(x.id)
    return names


def _test_pinned():
    pinned = set()
    for path in (ROOT / "tests").glob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        # Qualunque test che nomina la funzione tra virgolette o la ridefinisce: molti
        # estraggono funzioni da main() tramite helper comuni, senza scrivere «jarvis.py».
        if True:
            pinned.update(re.findall(r"""['"]([A-Za-z_][A-Za-z0-9_]*)['"]""", text))
            pinned.update(re.findall(r"def ([A-Za-z_][A-Za-z0-9_]*)\(", text))
    return pinned


def _locals(fn):
    local = {a.arg for a in ast.walk(fn) if isinstance(a, ast.arg)}
    for x in ast.walk(fn):
        if isinstance(x, ast.Name) and isinstance(x.ctx, (ast.Store, ast.Del)):
            local.add(x.id)
        elif isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and x is not fn:
            local.add(x.name)
        elif isinstance(x, (ast.Import, ast.ImportFrom)):
            for a in x.names:
                local.add((a.asname or a.name).split(".")[0])
        elif isinstance(x, ast.ExceptHandler) and x.name:
            local.add(x.name)
    return local


def analizza(names=None):
    src, tree, main = _load()
    mainnames, modnames, pinned = _main_names(main), _module_names(tree), _test_pinned()
    funcs = [n for n in main.body if isinstance(n, ast.FunctionDef)]
    result = {}
    for fn in funcs:
        if names is not None and fn.name not in names:
            continue
        why = []
        if fn.name in pinned and not ANCHE_TEST:
            why.append("usata dai test su jarvis.py")
        if fn.decorator_list:
            why.append("decoratore")
        if any(isinstance(x, (ast.Nonlocal, ast.Global)) for x in ast.walk(fn)):
            why.append("nonlocal/global")
        local = _locals(fn)
        deps, unknown = set(), set()
        for x in ast.walk(fn):
            if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load) and x.id not in local:
                if x.id in mainnames:
                    deps.add(x.id)
                elif x.id not in modnames and not hasattr(builtins, x.id):
                    unknown.add(x.id)
        if deps & local:
            why.append("nome sia locale sia di main: " + ",".join(sorted(deps & local)))
        defaults = [d for x in ast.walk(fn) if isinstance(x, (ast.FunctionDef, ast.Lambda))
                    for d in x.args.defaults + [k for k in x.args.kw_defaults if k is not None]]
        if any(isinstance(y, ast.Name) and y.id in mainnames for d in defaults for y in ast.walk(d)):
            why.append("nomi di main nei valori predefiniti")
        if unknown:
            why.append("nomi sconosciuti: " + ",".join(sorted(unknown)))
        result[fn.name] = (fn, sorted(deps - {fn.name}), why)
    return src, tree, main, result


def sposta(module_rel, title, names):
    src, tree, main, info = analizza(set(names))
    lines = src.splitlines(keepends=True)
    blocked = {n: w for n, (_, _, w) in info.items() if w}
    if blocked or set(names) - set(info):
        raise SystemExit("Non spostabili: %r mancanti: %r" % (blocked, sorted(set(names) - set(info))))
    order = [n for n in (f.name for f in main.body if isinstance(f, ast.FunctionDef)) if n in names]
    moved = set(order)
    deps = sorted({d for n in order for d in info[n][1]} - moved)
    chunks = []
    for name in order:
        fn = info[name][0]
        start, end = fn.lineno - 1, fn.end_lineno
        seg = list(lines[start:end])
        local = _locals(fn)
        reps = [(x.lineno - 1 - start, x.col_offset, x.id) for x in ast.walk(fn)
                if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load)
                and x.id in deps and x.id not in local]
        for li, col, dep in sorted(reps, reverse=True):
            assert seg[li][col:col + len(dep)] == dep, (name, seg[li])
            seg[li] = seg[li][:col] + "d." + dep + seg[li][col + len(dep):]
        chunks.append((start, end, "".join(seg)))
    imports = "".join("".join(lines[st.lineno - 1:st.end_lineno]) for st in tree.body
                      if isinstance(st, (ast.Import, ast.ImportFrom))
                      and not (isinstance(st, ast.ImportFrom) and st.module == "__future__"))
    module = (f'"""{title}\n\nSpostato da jarvis.py con il codice invariato (docs/PIANO-DIVISIONE-JARVIS.md):\n'
              f'i nomi di main() arrivano da `d` (lumi_contesto.Vivo), sempre col valore attuale.\n"""\n'
              f"from __future__ import annotations\n\n{imports}\nNOMI = {tuple(order)!r}\n\n\n"
              f"def installa(d):\n"
              f'    """Crea le funzioni per questa esecuzione di Lumi; restituisce {{nome: funzione}}."""\n'
              + "".join(c[2] for c in chunks)
              + "    funzioni = locals()\n    return {nome: funzioni[nome] for nome in NOMI}\n")
    target = ROOT / module_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(module, encoding="utf-8")
    dotted = module_rel[:-3].replace("/", ".")
    alias = "_" + dotted.replace(".", "_")
    getters = ",\n        ".join(f"{d}=lambda: {d}" for d in deps)
    install = (f"    # {title}: spostato in {module_rel} (divisione di jarvis.py).\n"
               f"    from {dotted} import installa as {alias}_installa\n"
               f"    {alias} = {alias}_installa(__import__(\"lumi_contesto\").Vivo(\n        {getters}))\n"
               f"    ({', '.join(order)},) = (\n        {alias}[n] for n in {alias}_installa.__globals__['NOMI'])\n")
    out, prev = [], 0
    for i, (s0, e0, _) in enumerate(chunks):
        out.append("".join(lines[prev:s0]))
        if i == 0:
            out.append(install)
        prev = e0
    out.append("".join(lines[prev:]))
    JARVIS.write_text("".join(out), encoding="utf-8")
    print(f"spostate {len(order)} funzioni, {sum(c[1]-c[0] for c in chunks)} righe → {module_rel}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--analizza"]:
        _, _, _, info = analizza()
        ok = {n: info[n] for n in info if not info[n][2]}
        print("spostabili", len(ok), sum(f.end_lineno - f.lineno + 1 for f, _, _ in ok.values()))
        for n, (f, deps, why) in sorted(info.items(), key=lambda kv: -(kv[1][0].end_lineno - kv[1][0].lineno)):
            print(f"{f.end_lineno - f.lineno + 1:5} {n:40} {'OK' if not why else '; '.join(why)[:90]}")
    else:
        sposta(sys.argv[1], sys.argv[2], sys.argv[3:])
