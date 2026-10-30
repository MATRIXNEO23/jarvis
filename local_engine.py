"""Jarvis core: explicit local tools, minimal dependencies, no arbitrary shell.

GPT will be a separate planner. Its proposals must pass through this local
executor, which accepts only registered actions with validated arguments.
"""
from __future__ import annotations

import ctypes
import os
from pathlib import Path
import re
import sqlite3
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from settings import default_path


@dataclass(frozen=True)
class TaskResult:
    task_id: str
    action: str
    status: str
    message: str


class LocalEngine:
    """Conservative, sequential executor; never evaluates generated code."""

    def __init__(self, *, download_dir: Path | None = None,
                 db_path: Path | None = None, windows: bool | None = None):
        self.download_dir = Path(download_dir) if download_dir else Path.home() / "Downloads"
        self.db_path = Path(db_path) if db_path else default_path().with_name("tasks.db")
        self.windows = os.name == "nt" if windows is None else windows
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS tasks(
                id TEXT PRIMARY KEY,
                time_utc TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT NOT NULL
            )""")

    @staticmethod
    def available_commands() -> str:
        return (
            "Comandi disponibili:\n"
            "• aiuto\n"
            "• stato sistema\n"
            "• mostra download\n"
            "• cerca file NOME (solo nella cartella Download)\n"
            "• apri blocco note\n"
            "• apri calcolatrice\n"
            "• apri esplora file\n"
            "• apri download\n"
            "• ultimi comandi"
        )

    def _record(self, result: TaskResult) -> TaskResult:
        with sqlite3.connect(self.db_path) as db:
            db.execute("INSERT INTO tasks VALUES (?, ?, ?, ?, ?)", (
                result.task_id, datetime.now(timezone.utc).isoformat(),
                result.action, result.status, result.message[:4000]))
        return result

    def execute(self, request: str) -> TaskResult:
        if not isinstance(request, str) or not request.strip():
            return self._record(TaskResult(uuid4().hex, "validation", "rejected",
                                           "Scrivi un comando prima di inviarlo."))
        if len(request) > 300:
            return self._record(TaskResult(uuid4().hex, "validation", "rejected",
                                           "Comando troppo lungo (massimo 300 caratteri)."))
        cmd = " ".join(request.casefold().split())
        action = "unknown"
        try:
            if cmd in ("aiuto", "comandi", "help"):
                action, message = "help", self.available_commands()
            elif cmd in ("stato", "stato sistema", "controlla sistema"):
                action, message = "system_status", self._system_status()
            elif cmd in ("mostra download", "elenca download", "lista download"):
                action, message = "list_downloads", self._list_downloads()
            elif cmd.startswith("cerca file "):
                action, message = "find_download", self._find_download(cmd[len("cerca file "):])
            elif cmd in ("apri blocco note", "apri notepad"):
                action, message = "open_notepad", self._open_app(["notepad.exe"], "Blocco note")
            elif cmd in ("apri calcolatrice", "apri calc"):
                action, message = "open_calculator", self._open_app(["calc.exe"], "Calcolatrice")
            elif cmd in ("apri esplora file", "apri esplora risorse"):
                action, message = "open_explorer", self._open_app(["explorer.exe"], "Esplora file")
            elif cmd in ("apri download", "apri cartella download"):
                action, message = "open_downloads", self._open_downloads()
            elif cmd in ("ultimi comandi", "cronologia"):
                action, message = "history", self._history()
            else:
                return self._record(TaskResult(uuid4().hex, "unknown", "rejected",
                    "Comando non riconosciuto. Scrivi 'aiuto' per vedere quelli supportati."))
            return self._record(TaskResult(uuid4().hex, action, "completed", message))
        except (OSError, ValueError, sqlite3.Error) as exc:
            return self._record(TaskResult(uuid4().hex, action, "failed",
                                           "Operazione non riuscita: " + str(exc)[:350]))

    def _system_status(self) -> str:
        lines = [f"CPU logiche: {os.cpu_count() or 'non disponibile'}"]
        if self.windows:
            class MemoryStatus(ctypes.Structure):
                _fields_ = [
                    ("length", ctypes.c_ulong), ("memory_load", ctypes.c_ulong),
                    ("total_phys", ctypes.c_ulonglong), ("avail_phys", ctypes.c_ulonglong),
                    ("total_page", ctypes.c_ulonglong), ("avail_page", ctypes.c_ulonglong),
                    ("total_virtual", ctypes.c_ulonglong), ("avail_virtual", ctypes.c_ulonglong),
                    ("avail_extended", ctypes.c_ulonglong)
                ]
            status = MemoryStatus()
            status.length = ctypes.sizeof(MemoryStatus)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                gib = 1024 ** 3
                lines.append(f"RAM: {status.total_phys / gib:.1f} GiB, "
                             f"disponibile {status.avail_phys / gib:.1f} GiB")
            else:
                lines.append("RAM: dati non disponibili")
        return "\n".join(lines)

    def _list_downloads(self) -> str:
        folder = self.download_dir
        if not folder.is_dir():
            raise FileNotFoundError("Cartella Download non trovata.")
        names = sorted((item.name for item in folder.iterdir()), key=str.casefold)
        if not names:
            return "La cartella Download è vuota."
        return "File e cartelle in Download (max 30):\n" + "\n".join(names[:30]) + (
            f"\n... e altri {len(names) - 30} elementi." if len(names) > 30 else "")

    def _find_download(self, query: str) -> str:
        query = query.strip()
        if not query or len(query) > 100 or any(c in query for c in "/\\:*?\"<>|"):
            raise ValueError("Indica un nome di file semplice da cercare.")
        if not self.download_dir.is_dir():
            raise FileNotFoundError("Cartella Download non trovata.")
        matches = []
        scanned = 0
        root = self.download_dir.resolve()
        # No link traversal, and explicit limits protect an old HDD.
        for current, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not (Path(current) / d).is_symlink())
            for filename in sorted(files):
                scanned += 1
                if query in filename.casefold():
                    matches.append(str(Path(current) / filename))
                    if len(matches) >= 20:
                        break
                if scanned >= 3000:
                    break
            if len(matches) >= 20 or scanned >= 3000:
                break
        if not matches:
            return f"Nessun risultato nei primi {scanned} file esaminati."
        return f"Risultati ({len(matches)}, fino a 20):\n" + "\n".join(matches) + (
            "\nRicerca parziale: raggiunto il limite di scansione." if scanned >= 3000 else "")

    def _open_app(self, argv: list[str], label: str) -> str:
        if not self.windows:
            raise OSError("Apertura programmi disponibile solo su Windows.")
        subprocess.Popen(argv, close_fds=True, shell=False)
        return label + " avviato."

    def _open_downloads(self) -> str:
        if not self.download_dir.is_dir():
            raise FileNotFoundError("Cartella Download non trovata.")
        return self._open_app(["explorer.exe", str(self.download_dir)], "Cartella Download")

    def _history(self) -> str:
        with sqlite3.connect(self.db_path) as db:
            rows = db.execute("SELECT action, status FROM tasks ORDER BY rowid DESC LIMIT 10").fetchall()
        return "Ultime attività:\n" + ("\n".join(f"{action}: {status}" for action, status in rows) if rows else "Nessuna")
