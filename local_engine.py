"""Jarvis core: explicit local tools, minimal dependencies, no arbitrary shell.

GPT will be a separate planner. Its proposals must pass through this local
executor, which accepts only registered actions with validated arguments.
"""
from __future__ import annotations

import ctypes
from contextlib import contextmanager
from heapq import nsmallest
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import webbrowser
from urllib.parse import urlencode
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
    preview: str = ""
    preview_path: str = ""
    explain: bool = False
    spoken_message: str | None = None
    file_listing: dict | None = None
    program_listing: dict | None = None


class LocalEngine:
    """Conservative, sequential executor; never evaluates generated code."""

    def __init__(self, *, download_dir: Path | None = None,
                 db_path: Path | None = None, windows: bool | None = None):
        self.file_access = None
        self.program_apps = None
        self.file_access_blocked = False
        self.download_dir = Path(download_dir) if download_dir else Path.home() / "Downloads"
        self.db_path = Path(db_path) if db_path else default_path().with_name("tasks.db")
        self.windows = os.name == "nt" if windows is None else windows
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS tasks(
                id TEXT PRIMARY KEY,
                time_utc TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT NOT NULL
            )""")

    @contextmanager
    def _connection(self):
        # sqlite3.Connection.__exit__ does not close the file handle.
        # Explicit close matters on Windows, especially during tests/backups.
        db = sqlite3.connect(self.db_path)
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def available_commands(*, files_enabled: bool = False) -> str:
        return (
            "Comandi disponibili:\n"
            "• aiuto\n"
            "• stato sistema\n"
            "• apri / mostra download (apre la cartella)\n"
            "• elenca download (elenco esplicito)\n"
            + ("• cerca file NOME (nelle cartelle autorizzate)\n" if files_enabled else
               "• cerca file NOME (solo nella cartella Download)\n") +
            "• apri blocco note\n"
            "• apri calcolatrice\n"
            "• apri esplora file\n"
            "• apri disco locale C\n"
            "• apri download\n"
            "• apri / avvia / lancia browser (predefinito Windows)\n"
            "• cerca nel browser TESTO\n"
            "• ultimi comandi"
        )

    def _record(self, result: TaskResult) -> TaskResult:
        with self._connection() as db:
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
        from voice_control import speech_to_local_command
        request = speech_to_local_command(request) or request
        if " ".join(request.casefold().strip(" .!?").split()) in ("aiuto","comandi","help","cosa puoi fare","cosa sai fare"):
            extra = ("\n"+self.file_access.commands()) if self.file_access is not None else ""
            if self.program_apps is not None:
                extra += '\n'+self.program_apps.commands()
            return self._record(TaskResult(uuid4().hex,"help","completed",self.available_commands(
                files_enabled=bool(self.file_access is not None and self.file_access.available()))+extra))
        if self.file_access_blocked and request.casefold().startswith(
                ("cerca file ","mostra download","elenca download","apri download","apri disco locale c")):
            return self._record(TaskResult(uuid4().hex,"files","rejected",
                "Accesso file incompleto: reinstalla la cartella file_access dal pacchetto e riavvia Jarvis."))
        if self.program_apps is not None:
            parsed = self.program_apps.parse_command(request)
            if parsed is not None:
                return self.execute_program(*parsed)
        if self.file_access is not None and self.file_access.enabled():
            parsed = self.file_access.parse_command(request)
            if parsed is not None:
                return self.execute_file(*parsed)
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
            elif cmd in ("apri disco locale c", "apri unità c", "apri unita c"):
                action, message = "open_drive_c", self._open_drive_c()
            elif cmd in ("apri download", "apri cartella download"):
                action, message = "open_downloads", self._open_downloads()
            elif cmd in ("apri browser", "apri il browser", "apri browser predefinito"):
                action, message = "open_browser", self._open_browser()
            elif cmd.startswith("cerca nel browser ") or cmd.startswith("cerca su internet "):
                prefix = "cerca nel browser " if cmd.startswith("cerca nel browser ") else "cerca su internet "
                action, message = "web_search", self._browser_search(cmd[len(prefix):])
            elif cmd in ("ultimi comandi", "cronologia"):
                action, message = "history", self._history()
            else:
                return self._record(TaskResult(uuid4().hex, "unknown", "rejected",
                    "Comando non riconosciuto. Scrivi 'aiuto' per vedere quelli supportati."))
            return self._record(TaskResult(uuid4().hex, action, "completed", message))
        except (OSError, ValueError, sqlite3.Error) as exc:
            return self._record(TaskResult(uuid4().hex, action, "failed",
                                           "Operazione non riuscita: " + str(exc)[:350]))

    def execute_program(self, operation, arguments):
        if self.program_apps is None:
            return self._record(TaskResult(uuid4().hex,'program_apps','rejected',
                'Programmi e app non disponibile: reinstalla program_apps dal pacchetto completo.'))
        result = self.program_apps.execute(operation,arguments)
        return self._record(TaskResult(uuid4().hex,'program_apps',result.status,
            result.message,spoken_message=result.message,program_listing=result.listing))

    def execute_file(self, operation, arguments, refinement_token=None):
        if self.file_access is None:
            return self._record(TaskResult(uuid4().hex,"files","rejected",
                "Accesso file non disponibile: reinstalla il pacchetto completo."))
        result=(self.file_access.execute(operation,arguments,refinement_token=refinement_token)
                if refinement_token is not None else self.file_access.execute(operation,arguments))
        return self._record(TaskResult(uuid4().hex,"files_"+operation,result.status,
            result.message,result.preview,result.preview_path,result.explain,
            self.file_access.spoken_reply(operation,result),result.listing))

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
        total=0
        def entries():
            nonlocal total
            for item in folder.iterdir():
                total+=1
                yield item.name
        # Large download directories must not be fully materialized in RAM.
        names=nsmallest(30,entries(),key=str.casefold)
        if not names:
            return "La cartella Download è vuota."
        return "File e cartelle in Download (max 30):\n" + "\n".join(names) + (
            f"\n... e altri {total - 30} elementi." if total > 30 else "")

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
        from program_apps.native import describe_program_launch
        process = subprocess.Popen(argv, close_fds=True, shell=False)
        return describe_program_launch(label, process.pid)

    def _open_drive_c(self) -> str:
        # Fixed Windows Explorer destination. No GPT-provided paths or shell.
        return self._open_app(["explorer.exe", "C:\\"], "Disco locale C")

    def _open_downloads(self) -> str:
        if not self.download_dir.is_dir():
            raise FileNotFoundError("Cartella Download non trovata.")
        return self._open_app(["explorer.exe", str(self.download_dir)], "Cartella Download")

    def _open_browser(self) -> str:
        if not self.windows:
            raise OSError("Apertura browser disponibile solo su Windows.")
        # Open a fixed homepage using the user's registered default browser.
        if not webbrowser.open("https://www.google.com/", new=2):
            raise OSError("Impossibile aprire il browser predefinito.")
        return "Browser predefinito aperto."

    def _browser_search(self, query: str) -> str:
        if not self.windows:
            raise OSError("Ricerca nel browser disponibile solo su Windows.")
        # A search query is always data, never a URL or a shell command.
        query = " ".join(query.split())
        if not query or len(query) > 160 or any(ord(c) < 32 for c in query):
            raise ValueError("Termine di ricerca non valido (max 160 caratteri).")
        url = "https://www.google.com/search?" + urlencode({"q": query})
        if not webbrowser.open(url, new=2):
            raise OSError("Impossibile aprire il browser predefinito.")
        return "Ricerca aperta nel browser."

    def _history(self) -> str:
        with self._connection() as db:
            rows = db.execute("SELECT action, status FROM tasks ORDER BY rowid DESC LIMIT 10").fetchall()
        return "Ultime attività:\n" + ("\n".join(f"{action}: {status}" for action, status in rows) if rows else "Nessuna")

