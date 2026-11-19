"""Pulizia dei dati su disco (passo 6, 15/11).

Finestra con le cartelle dei dati di Lumi e lo spazio usato; a destra i file della
cartella scelta con una casella ciascuno, «Seleziona tutto» / «Deseleziona tutto»,
«Ascolta» per gli audio, «Apri cartella» e «Sposta nel Cestino».
- Si cancella solo ciò che l'utente spunta, dopo conferma; i file vanno nel Cestino di
  Windows (si possono recuperare), mai cancellati direttamente.
- File importanti (archivi di chat e memoria, impostazioni, modelli, credenziali) sono
  segnati «⚠» e chiedono una seconda conferma che dice cosa si perde.
- Cartelle: dati di Lumi (%LOCALAPPDATA%\\Jarvis) e audio temporanei della voce
  (%TEMP%\\lumi-voice-*).
"""
from __future__ import annotations

import glob
import os
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path

AUDIO = {".wav", ".mp3", ".ogg"}
IMPORTANTI = {".sqlite3", ".sqlite", ".db", ".json", ".gguf", ".bin", ".onnx", ".dpapi",
              ".key", ".session"}
MAX_FILE = 5000


@dataclass(frozen=True)
class FileInfo:
    path: Path
    size: int
    mtime: float

    @property
    def audio(self) -> bool:
        return self.path.suffix.lower() in AUDIO

    @property
    def importante(self) -> bool:
        low = self.path.suffix.lower()
        parts = {p.casefold() for p in self.path.parts}
        return (low in IMPORTANTI or "models" in parts or "telegram" in parts
                or self.path.name.casefold().startswith(("settings", "secret")))


def radici() -> list[tuple[str, Path]]:
    from settings import default_path
    roots = [("Dati di Lumi", default_path().parent)]
    for folder in sorted(glob.glob(os.path.join(tempfile.gettempdir(), "lumi-voice-*"))):
        roots.append(("Audio temporanei della voce", Path(folder)))
    return [(label, path) for label, path in roots if path.is_dir()]


def dimensione(folder: Path, limit: int = 50_000) -> int:
    total, seen = 0, 0
    for base, _dirs, files in os.walk(folder):
        for name in files:
            seen += 1
            if seen > limit:
                return total
            try:
                total += os.path.getsize(os.path.join(base, name))
            except OSError:
                pass
    return total


def file_in(folder: Path) -> list[FileInfo]:
    """File della cartella (non delle sottocartelle), dai più grandi."""
    items = []
    try:
        entries = list(os.scandir(folder))
    except OSError:
        return []
    for entry in entries[:MAX_FILE]:
        try:
            if entry.is_file(follow_symlinks=False):
                stat = entry.stat()
                items.append(FileInfo(Path(entry.path), stat.st_size, stat.st_mtime))
        except OSError:
            pass
    return sorted(items, key=lambda item: item.size, reverse=True)


def sottocartelle(folder: Path) -> list[Path]:
    try:
        return sorted((Path(e.path) for e in os.scandir(folder)
                       if e.is_dir(follow_symlinks=False)), key=lambda p: p.name.casefold())
    except OSError:
        return []


def leggibile(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return ("%d %s" % (size, unit)) if unit == "B" else ("%.1f %s" % (size, unit))
        size /= 1024
    return str(size)


def al_cestino(paths) -> bool:
    """Sposta nel Cestino di Windows (recuperabile). False se non riesce."""
    paths = [str(Path(p)) for p in paths]
    if not paths:
        return True
    if os.name != "nt":
        return False
    import ctypes
    from ctypes import wintypes

    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [("hwnd", wintypes.HWND), ("wFunc", wintypes.UINT),
                    ("pFrom", wintypes.LPCWSTR), ("pTo", wintypes.LPCWSTR),
                    ("fFlags", ctypes.c_uint16), ("fAnyOperationsAborted", wintypes.BOOL),
                    ("hNameMappings", ctypes.c_void_p), ("lpszProgressTitle", wintypes.LPCWSTR)]

    FO_DELETE, FOF_SILENT, FOF_NOCONFIRMATION, FOF_ALLOWUNDO, FOF_NOERRORUI = 3, 4, 16, 64, 1024
    op = SHFILEOPSTRUCTW(None, FO_DELETE, "\0".join(paths) + "\0\0", None,
                         FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT | FOF_NOERRORUI,
                         False, None, None)
    result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
    return result == 0 and not op.fAnyOperationsAborted


class PuliziaWindow:
    def __init__(self, parent, *, notify, play_audio=None, stop_audio=None):
        import tkinter as tk
        from tkinter import ttk
        self.tk, self.ttk = tk, ttk
        self.notify = notify
        self.play_audio = play_audio
        self.stop_audio = stop_audio
        self.checked: set[str] = set()
        self.files: dict[str, FileInfo] = {}
        self.folder: Path | None = None
        self.playing = False
        self.window = tk.Toplevel(parent)
        self.window.title("Lumi // Pulizia dati")
        self.window.geometry("860x520")
        self.window.protocol("WM_DELETE_WINDOW", self.chiudi)
        top = ttk.Frame(self.window, padding=10)
        top.pack(fill="both", expand=True)
        ttk.Label(top, wraplength=820, text=(
            "Spunta i file da togliere: vanno nel Cestino di Windows, da lì si possono "
            "recuperare. ⚠ = archivi di chat e memoria, impostazioni, modelli: chiede una "
            "conferma in più.")).pack(anchor="w", pady=(0, 6))
        panes = ttk.PanedWindow(top, orient="horizontal")
        panes.pack(fill="both", expand=True)
        left = ttk.Frame(panes)
        right = ttk.Frame(panes)
        panes.add(left, weight=1)
        panes.add(right, weight=3)
        self.folders = ttk.Treeview(left, columns=("size",), show="tree headings", height=16)
        self.folders.heading("#0", text="Cartella")
        self.folders.heading("size", text="Spazio")
        self.folders.column("size", width=80, anchor="e")
        self.folders.pack(fill="both", expand=True)
        self.folders.bind("<<TreeviewSelect>>", self._cartella_scelta)
        self.list = ttk.Treeview(right, columns=("check", "size", "date"), show="tree headings",
                                 height=16)
        self.list.heading("#0", text="File")
        self.list.heading("check", text="✓")
        self.list.heading("size", text="Dimensione")
        self.list.heading("date", text="Data")
        self.list.column("check", width=34, anchor="center")
        self.list.column("size", width=90, anchor="e")
        self.list.column("date", width=120)
        self.list.pack(fill="both", expand=True)
        self.list.bind("<Button-1>", self._clic)
        self.list.bind("<space>", lambda _e: self._spunta(self.list.focus()))
        buttons = ttk.Frame(top)
        buttons.pack(fill="x", pady=(8, 0))
        for text, command in (("Seleziona tutto", self.seleziona_tutto),
                              ("Deseleziona tutto", self.deseleziona_tutto),
                              ("Ascolta", self.ascolta), ("Apri cartella", self.apri_cartella)):
            ttk.Button(buttons, text=text, command=command).pack(side="left", padx=(0, 6))
        ttk.Button(buttons, text="Sposta nel Cestino", command=self.elimina).pack(side="right")
        self.status = tk.StringVar()
        ttk.Label(top, textvariable=self.status).pack(anchor="w", pady=(6, 0))
        self.carica_cartelle()

    # --- cartelle ---------------------------------------------------------------------
    def carica_cartelle(self):
        self.folders.delete(*self.folders.get_children())
        for label, root in radici():
            node = self.folders.insert("", "end", iid=str(root), text=label + "  (" + root.name + ")",
                                       values=(leggibile(dimensione(root)),), open=True)
            for sub in sottocartelle(root):
                self.folders.insert(node, "end", iid=str(sub), text=sub.name,
                                    values=(leggibile(dimensione(sub)),))

    def _cartella_scelta(self, _event=None):
        selected = self.folders.selection()
        if selected:
            self.mostra(Path(selected[0]))

    def mostra(self, folder: Path):
        self.folder = folder
        self.checked.clear()
        self.files = {str(f.path): f for f in file_in(folder)}
        self.list.delete(*self.list.get_children())
        for key, info in self.files.items():
            name = ("⚠ " if info.importante else "") + ("♪ " if info.audio else "") + info.path.name
            self.list.insert("", "end", iid=key, text=name,
                             values=("☐", leggibile(info.size),
                                     time.strftime("%d/%m/%Y %H:%M", time.localtime(info.mtime))))
        self._riassunto()

    # --- caselle ----------------------------------------------------------------------
    def _clic(self, event):
        if self.list.identify_column(event.x) == "#1":
            row = self.list.identify_row(event.y)
            if row:
                self._spunta(row)
                return "break"
        return None

    def _spunta(self, key, value=None):
        if not key or key not in self.files:
            return
        on = (key not in self.checked) if value is None else value
        (self.checked.add if on else self.checked.discard)(key)
        self.list.set(key, "check", "☑" if on else "☐")
        self._riassunto()

    def seleziona_tutto(self):
        for key in self.files:
            self._spunta(key, True)

    def deseleziona_tutto(self):
        for key in list(self.files):
            self._spunta(key, False)

    def _riassunto(self):
        size = sum(self.files[k].size for k in self.checked)
        self.status.set("%d file, selezionati %d (%s)" % (len(self.files), len(self.checked),
                                                          leggibile(size)))

    # --- azioni -----------------------------------------------------------------------
    def ascolta(self):
        key = self.list.focus()
        info = self.files.get(key)
        if info is None or not info.audio:
            self.status.set("Scegli un file audio (♪) da ascoltare.")
            return
        if self.play_audio is None:
            return
        threading.Thread(target=self._play, args=(info.path,), daemon=True,
                         name="lumi-pulizia-ascolta").start()

    def _play(self, path):
        self.playing = True
        try:
            self.play_audio(path)
        except Exception as exc:     # file rovinato o uscita audio occupata
            message = "Ascolto non riuscito: " + str(exc)[:80]
            self.window.after(0, lambda: self.status.set(message))
        finally:
            self.playing = False

    def _ferma_ascolto(self):
        if self.playing and self.stop_audio is not None:
            self.stop_audio()

    def apri_cartella(self):
        if self.folder is not None and os.name == "nt":
            os.startfile(self.folder)    # noqa: S606 — cartella dei dati di Lumi

    def elimina(self, *, confirm=None):
        from tkinter import messagebox
        confirm = confirm or (lambda title, text: messagebox.askyesno(title, text, parent=self.window))
        chosen = [self.files[k] for k in self.checked]
        if not chosen:
            self.status.set("Nessun file spuntato.")
            return False
        size = leggibile(sum(f.size for f in chosen))
        if not confirm("Lumi // Pulizia", "Spostare %d file (%s) nel Cestino?" % (len(chosen), size)):
            return False
        important = [f for f in chosen if f.importante]
        if important and not confirm(
                "Lumi // File importanti",
                "%d file segnati ⚠ (archivi di chat e memoria, impostazioni o modelli). "
                "Senza di loro Lumi perde quei dati finché non li ripristini dal Cestino. "
                "Continuare?" % len(important)):
            return False
        self._ferma_ascolto()
        ok = al_cestino([f.path for f in chosen])
        self.notify("PULIZIA > " + ("%d file spostati nel Cestino (%s)." % (len(chosen), size)
                                   if ok else "Spostamento nel Cestino non riuscito (file in uso "
                                   "o permessi): controlla la lista, alcuni possono essere rimasti."))
        if self.folder is not None:
            self.mostra(self.folder)
        return ok

    def chiudi(self):
        self._ferma_ascolto()
        self.window.destroy()
