"""Current-user Windows metadata and native activation; no generated commands."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

from file_access.windows import require_windows


@dataclass(frozen=True)
class AppEntry:
    id: str
    name: str
    kind: str
    target: str
    fingerprint: str = ''
    manual: bool = False


def fingerprint(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Programma o collegamento locale non disponibile.')
    if path.suffix.casefold() == '.lnk':
        return hashlib.sha256(path.read_bytes()).hexdigest()
    stat = path.stat()
    return hashlib.sha256(f'{stat.st_size}:{stat.st_mtime_ns}'.encode()).hexdigest()


def entry(name, kind, target, *, manual=False):
    if (kind not in ('exe', 'lnk', 'store', 'shell') or not isinstance(name, str)
            or not name.strip() or not isinstance(target, str) or not target.strip()
            or len(name) > 300 or len(target) > 32767
            or any(ord(c) < 32 for c in name + target)):
        raise ValueError('Identità applicazione non valida.')
    signature = ''
    if kind in ('exe', 'lnk'):
        path = Path(target)
        if not path.is_absolute() or str(path).startswith('\\\\'):
            raise ValueError('Seleziona un programma locale.')
        if path.suffix.casefold() != '.' + kind:
            raise ValueError('Tipo di programma non valido.')
        target = str(path.resolve())
        signature = fingerprint(target)
    ident = hashlib.sha256((kind + '\0' + target.casefold()).encode('utf-8')).hexdigest()
    return AppEntry(ident, name.strip(), kind, target, signature, manual)


def manual_entry(path):
    path = Path(path)
    return entry(path.stem, path.suffix.casefold().lstrip('.'), str(path), manual=True)


def discover(cancelled=None):
    require_windows()
    script = Path(__file__).with_name('windows_apps.ps1')
    if not script.is_file():
        raise OSError('Manca program_apps/windows_apps.ps1: reinstalla Programmi e app.')
    powershell = Path(os.environ['SystemRoot']) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    started = time.monotonic()
    with subprocess.Popen([str(powershell), '-NoProfile', '-NonInteractive',
            '-ExecutionPolicy', 'Bypass', '-File', str(script)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
            errors='replace', creationflags=0x08000000,
            cwd=os.environ['SystemRoot']) as process:
        try:
            while True:
                if cancelled is not None and cancelled.is_set():
                    raise OSError('Aggiornamento annullato; elenco precedente conservato.')
                if time.monotonic() - started > 60:
                    raise OSError('Rilevamento Windows scaduto; elenco precedente conservato.')
                try:
                    output, error = process.communicate(timeout=.2)
                    break
                except subprocess.TimeoutExpired:
                    pass
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()
    if process.returncode or len(output) > 8_000_000:
        raise OSError('Rilevamento Windows non completato; elenco precedente conservato.')
    try:
        payload = json.loads(output.lstrip('\ufeff'))
        rows, warnings = payload['apps'], list(payload['warnings'])
        found = {}
        rejected = 0
        for row in rows:
            try:
                candidate = entry(row['name'], row['kind'], row['target'])
                found[candidate.id] = candidate
            except (ValueError, OSError, KeyError):
                rejected += 1
        if rejected:
            warnings.append(f'{rejected} voci non disponibili o non avviabili escluse.')
        return sorted(found.values(), key=lambda a: (a.name.casefold(), a.id)), warnings
    except (ValueError, KeyError, TypeError) as exc:
        raise OSError('Risposta inventario Windows non valida; elenco precedente conservato.') from exc


def launch(app):
    require_windows()
    if app.kind in ('exe', 'lnk') and fingerprint(app.target) != app.fingerprint:
        raise OSError('Programma o collegamento cambiato: aggiorna e conferma la selezione.')
    if app.kind == 'store':
        _activate_store(app.target)
    else:
        target = 'shell:AppsFolder\\' + app.target if app.kind == 'shell' else app.target
        _shell_open(target)
    return 'Richiesta di avvio di ' + app.name + ' accettata da Windows.'


def _shell_open(target):
    class ExecuteInfo(ctypes.Structure):
        _fields_ = [('cbSize', wintypes.DWORD), ('fMask', ctypes.c_ulong),
            ('hwnd', wintypes.HWND), ('lpVerb', wintypes.LPCWSTR),
            ('lpFile', wintypes.LPCWSTR), ('lpParameters', wintypes.LPCWSTR),
            ('lpDirectory', wintypes.LPCWSTR), ('nShow', ctypes.c_int),
            ('hInstApp', wintypes.HINSTANCE), ('lpIDList', ctypes.c_void_p),
            ('lpClass', wintypes.LPCWSTR), ('hkeyClass', wintypes.HKEY),
            ('dwHotKey', wintypes.DWORD), ('hIcon', wintypes.HANDLE),
            ('hProcess', wintypes.HANDLE)]
    info = ExecuteInfo()
    info.cbSize = ctypes.sizeof(info)
    info.fMask = 0x40 | 0x400
    info.lpVerb, info.lpFile, info.nShow = 'open', target, 1
    api = ctypes.WinDLL('shell32', use_last_error=True).ShellExecuteExW
    api.argtypes, api.restype = [ctypes.POINTER(ExecuteInfo)], wintypes.BOOL
    if not api(ctypes.byref(info)):
        raise ctypes.WinError(ctypes.get_last_error())
    if info.hProcess:
        close = ctypes.WinDLL('kernel32', use_last_error=True).CloseHandle
        close.argtypes = [wintypes.HANDLE]
        close(info.hProcess)


def _activate_store(aumid):
    class Guid(ctypes.Structure):
        _fields_ = [('bytes', ctypes.c_ubyte * 16)]
    def guid(value):
        return Guid((ctypes.c_ubyte * 16).from_buffer_copy(uuid.UUID(value).bytes_le))
    ole = ctypes.OleDLL('ole32')
    initialized = False
    try:
        ole.CoInitializeEx(None, 2)
        initialized = True
    except OSError as exc:
        if getattr(exc, 'winerror', None) != -2147417850:
            raise
    instance = ctypes.c_void_p()
    try:
        clsid = guid('45ba127d-10a8-46ea-8ab7-56ea9078943c')
        iid = guid('2e941141-7f97-4756-ba1d-9decde894a3d')
        ole.CoCreateInstance(ctypes.byref(clsid), None, 4, ctypes.byref(iid), ctypes.byref(instance))
        table = ctypes.cast(instance, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        activate = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, wintypes.LPCWSTR,
                    wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD))(table[3])
        pid = wintypes.DWORD()
        result = activate(instance, aumid, None, 0, ctypes.byref(pid))
        if result < 0:
            raise OSError(f'Windows non ha attivato questa app Store (HRESULT {result & 0xffffffff:08x}).')
        return pid.value
    finally:
        if instance:
            table = ctypes.cast(instance, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
            ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(table[2])(instance)
        if initialized:
            ole.CoUninitialize()
