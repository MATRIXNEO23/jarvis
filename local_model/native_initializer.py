"""Initialize pinned upstream KoboldCpp CPU DLL without its server/launcher.

This adapter uses the exact upstream argument setup validated by the native
Gemma proof. Upstream revision must be pinned and verified by the caller.
"""
import ast
from pathlib import Path


def initialize_kobold_cpu(upstream, config, source_path):
    source = Path(source_path)
    if not source.is_file():
        raise RuntimeError("Sorgente ABI upstream non disponibile.")
    if not Path(config.dll).is_file():
        raise RuntimeError("DLL nativa non disponibile.")
    # The upstream script owns the ctypes definitions and argument parser.
    # Reuse its pinned setup but never execute main() (HTTP/launcher).
    tree = ast.parse(source.read_text(encoding="utf-8"))
    block = next((n for n in reversed(tree.body)
                  if isinstance(n, ast.If)
                  and isinstance(n.test, ast.Compare)
                  and isinstance(n.test.left, ast.Name)
                  and n.test.left.id == "__name__"), None)
    if block is None or not block.body:
        raise RuntimeError("Struttura upstream non compatibile.")
    last = block.body[-1]
    if not (isinstance(last, ast.Expr) and isinstance(last.value, ast.Call)
            and isinstance(last.value.func, ast.Name)
            and last.value.func.id == "main"):
        raise RuntimeError("Inizializzazione upstream cambiata.")
    # The upstream proof uses this initialization path; no server is started.
    exec(compile(ast.Module(body=block.body[:-1], type_ignores=[]),
                 str(source), "exec"), upstream.__dict__)
    if not hasattr(upstream, "parser"):
        raise RuntimeError("Parser upstream non inizializzato dopo il bootstrap.")
    args = upstream.parser.parse_args([
        "--usecpu", "--noavx2", "--gpulayers", "0",
        "--threads", str(config.threads),
        "--blasthreads", str(config.batch_threads),
        "--contextsize", str(config.context_size), "--quiet",
    ])
    args.usemmap = True
    args.ropeconfig = [0.0, 10000.0]
    upstream.args = args
    upstream.maxctx = config.context_size
    upstream.init_library()
