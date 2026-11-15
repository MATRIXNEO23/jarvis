"""Ponte locale tra Lumi e il server MCP (add-on «Diagnostica per Claude», passo 9).

Solo 127.0.0.1, chiave casuale per ogni avvio, una richiesta JSON per riga. Le azioni
sono solo dentro Lumi; i comandi che toccano il resto del PC vengono rifiutati.
"""
from __future__ import annotations

import collections
import json
import os
import re
import secrets
import socket
import threading
import time
from pathlib import Path

RIGHE = collections.deque(maxlen=400)       # (ora, ruolo, testo) dalla console di Lumi
MAX_RICHIESTA = 64 * 1024

# Parole che toccano il PC fuori da Lumi: rifiutate per «prova_comando».
_VIETATI = re.compile(
    r"\b(?:apri|avvia|lancia|chiudi|termina|uccidi|spegni|riavvia\s+il\s+(?:pc|computer)|"
    r"elimina|cancella|sposta|rinomina|copia|scrivi|digita|premi|clicca|clic|doppio\s+clic|"
    r"mouse|finestr\w*|griglia|numeri|scorri|ingrandisci|minimizza|riduci|passa\s+a|"
    r"invia|manda|telegram|file|cartell\w*|download|programm\w*)\b", re.I)


def registra(role: str, text: str) -> None:
    """Chiamata da write_line: costa un append, niente Tk."""
    RIGHE.append((time.strftime("%H:%M:%S"), role, str(text)[:2000]))


def percorso_porta() -> Path:
    local = os.environ.get("LOCALAPPDATA") or str(Path.home())
    return Path(local) / "Jarvis" / "diagnostica_claude.json"


def comando_permesso(text: str) -> bool:
    if not isinstance(text, str) or not text.strip() or len(text) > 300:
        return False
    if _VIETATI.search(text):
        return False
    try:
        from controllo_pc.commands import parse_command
        if parse_command(text) is not None:
            return False
    except ImportError:
        pass
    return True


class Ponte:
    """Server del ponte. callbacks: stato() -> dict, in_chat(testo), prova(testo),
    riavvia_modello(). Le ultime tre vengono eseguite sul thread di Tk (run_ui)."""

    def __init__(self, *, stato, in_chat, prova, riavvia_modello, run_ui, log_motore=None,
                 path: Path | None = None, extra=None):
        self.stato = stato
        self.in_chat = in_chat
        self.prova = prova
        self.riavvia_modello = riavvia_modello
        self.run_ui = run_ui
        self.log_motore = log_motore
        # op -> funzione(args) -> dict, eseguita sul thread di Tk e attesa (strumenti nuovi).
        self.extra = dict(extra or {})
        self.path = path or percorso_porta()
        self.token = ""
        self.sock = None
        self.thread = None

    @property
    def attivo(self) -> bool:
        return self.sock is not None

    def avvia(self) -> int:
        if self.sock is not None:
            return self.sock.getsockname()[1]
        self.token = secrets.token_hex(24)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 0))
        sock.listen(4)
        self.sock = sock
        port = sock.getsockname()[1]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps({"port": port, "token": self.token, "pid": os.getpid()}),
                        encoding="utf-8")
        os.replace(temp, self.path)
        self.thread = threading.Thread(target=self._loop, daemon=True, name="lumi-ponte-claude")
        self.thread.start()
        return port

    def ferma(self) -> None:
        sock, self.sock = self.sock, None
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass
        try:
            self.path.unlink()
        except OSError:
            pass

    def _loop(self):
        sock = self.sock
        while sock is not None and self.sock is sock:
            try:
                conn, _addr = sock.accept()
            except OSError:
                return
            threading.Thread(target=self._serve, args=(conn,), daemon=True).start()

    def _serve(self, conn):
        with conn:
            conn.settimeout(10)
            data = b""
            try:
                while b"\n" not in data and len(data) < MAX_RICHIESTA:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                reply = self.gestisci(json.loads(data.split(b"\n", 1)[0].decode("utf-8")))
            except (OSError, ValueError, UnicodeError):
                reply = {"ok": False, "errore": "richiesta non valida"}
            try:
                conn.sendall(json.dumps(reply, ensure_ascii=True).encode("ascii") + b"\n")
            except OSError:
                pass

    def gestisci(self, request: dict) -> dict:
        if not isinstance(request, dict) or not secrets.compare_digest(
                str(request.get("token", "")), self.token or "-"):
            return {"ok": False, "errore": "chiave non valida"}
        op, args = request.get("op"), request.get("args") or {}
        count = max(1, min(int(args.get("righe", 60) or 60), 400)) if isinstance(args, dict) else 60
        if op == "stato":
            return {"ok": True, "stato": self.stato()}
        if op == "console":
            return {"ok": True, "righe": ["%s %s: %s" % r for r in list(RIGHE)[-count:]]}
        if op == "errori":
            return {"ok": True, "righe": ["%s %s" % (r[0], r[2]) for r in RIGHE if r[1] == "errore"][-count:]}
        if op == "log_motore":
            text = self.log_motore() if self.log_motore else ""
            return {"ok": True, "righe": text.splitlines()[-count:]}
        text = str(args.get("testo", "")) if isinstance(args, dict) else ""
        if op == "scrivi_in_chat":
            if not text.strip():
                return {"ok": False, "errore": "testo vuoto"}
            self.run_ui(lambda: self.in_chat(text[:1000]))
            return {"ok": True}
        if op == "prova_comando":
            if not comando_permesso(text):
                return {"ok": False, "errore": "comando non permesso: solo comandi dentro Lumi "
                                               "(niente Controllo PC, programmi, file)"}
            self.run_ui(lambda: self.prova(text))
            return {"ok": True, "nota": "comando inviato; leggi la console per l'esito"}
        if op == "riavvia_modello":
            self.run_ui(self.riavvia_modello)
            return {"ok": True}
        if op in self.extra:
            return self._sul_thread_ui(lambda: self.extra[op](args if isinstance(args, dict) else {}))
        return {"ok": False, "errore": "operazione sconosciuta"}

    def _sul_thread_ui(self, fn, timeout: float = 10.0) -> dict:
        """Esegue fn sul thread di Tk e aspetta il risultato (i widget si toccano solo lì)."""
        done = threading.Event()
        box = {}

        def run():
            try:
                box["value"] = fn()
            except Exception as exc:          # l'errore va a Claude, Lumi resta in piedi
                box["value"] = {"ok": False, "errore": type(exc).__name__ + ": " + str(exc)[:200]}
            finally:
                done.set()
        self.run_ui(run)
        if not done.wait(timeout):
            return {"ok": False, "errore": "Lumi non ha risposto in tempo (finestra occupata?)"}
        value = box.get("value")
        return value if isinstance(value, dict) else {"ok": True, "valore": value}
