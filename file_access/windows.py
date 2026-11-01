"""Small native Windows adapters. No resident process or extra Python packages."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import uuid

FOLDERS = {
    'profilo': '5E6C858F-0E22-4760-9AFE-EA3317B67173',
    'desktop': 'B4BFCC3A-DB2C-424C-B029-7FE99A87C641',
    'documenti': 'FDD39AD0-238F-46AF-ADB4-6C85480369C7',
    'download': '374DE290-123F-4565-9164-39C4925E467B',
    'appdata': '3EB685DB-65F9-4CF6-A03A-E3EF65729F3D',
    'appdata locale': 'F1B32785-6FBA-4FCF-9D55-7B8E7F157091',
    'windows': 'F38BF404-1D43-42F2-9305-67DE0B28FC23',
}


def require_windows():
    if os.name != 'nt':
        raise OSError('Accesso file disponibile soltanto su Windows.')


def known_folder(name: str) -> Path:
    require_windows()
    guid = (ctypes.c_ubyte * 16).from_buffer_copy(uuid.UUID(FOLDERS[name]).bytes_le)
    pointer = ctypes.c_void_p()
    shell = ctypes.WinDLL('shell32', use_last_error=True)
    api = shell.SHGetKnownFolderPath
    api.argtypes = [ctypes.c_void_p, wintypes.DWORD, wintypes.HANDLE,
                    ctypes.POINTER(ctypes.c_void_p)]
    api.restype = ctypes.c_long
    # DONT_VERIFY resolves redirected folders without creating anything.
    result = api(ctypes.byref(guid), 0x4000, None, ctypes.byref(pointer))
    ole = ctypes.WinDLL('ole32')
    ole.CoTaskMemFree.argtypes = [ctypes.c_void_p]
    try:
        if result < 0 or not pointer.value:
            raise OSError('Windows non ha risolto la cartella '+name+'.')
        return Path(ctypes.wstring_at(pointer))
    finally:
        if pointer.value:
            ole.CoTaskMemFree(pointer)


def native_kernel():
    require_windows()
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                  ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
                                  wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.GetFinalPathNameByHandleW.argtypes = [wintypes.HANDLE, wintypes.LPWSTR,
                                               wintypes.DWORD, wintypes.DWORD]
    kernel.GetFinalPathNameByHandleW.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.GetVolumePathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    kernel.GetVolumeNameForVolumeMountPointW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR,
                                                       wintypes.DWORD]
    return kernel


def volume_identity(path: Path) -> str:
    kernel = native_kernel()
    root, guid = ctypes.create_unicode_buffer(32768), ctypes.create_unicode_buffer(256)
    if not kernel.GetVolumePathNameW(str(path), root, len(root)):
        raise ctypes.WinError(ctypes.get_last_error())
    if not kernel.GetVolumeNameForVolumeMountPointW(root.value, guid, len(guid)):
        raise OSError('Identità del volume non verificabile: seleziona un disco locale.')
    return guid.value.casefold()


def final_path(handle: int) -> Path:
    kernel = native_kernel()
    size = kernel.GetFinalPathNameByHandleW(handle, None, 0, 0)
    if not size or size > 32768:
        raise ctypes.WinError(ctypes.get_last_error())
    buffer = ctypes.create_unicode_buffer(size + 1)
    got = kernel.GetFinalPathNameByHandleW(handle, buffer, len(buffer), 0)
    if not got or got >= len(buffer):
        raise OSError('Percorso finale non verificabile.')
    value = buffer.value
    if value.startswith('\\\\?\\UNC\\'):
        value = '\\\\'+value[8:]
    elif value.startswith('\\\\?\\'):
        value = value[4:]
    return Path(value)


def resolved_path(path: Path) -> Path:
    kernel = native_kernel()
    # Access to attributes only; don't request write or administrative rights.
    handle = kernel.CreateFileW(str(path), 0, 7, None, 3, 0x02000000, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return final_path(handle)
    finally:
        kernel.CloseHandle(handle)


def drives() -> list[Path]:
    kernel = native_kernel()
    mask = kernel.GetLogicalDrives()
    # Drive types fixed/removable only. Network and MTP need separate validation.
    kernel.GetDriveTypeW.argtypes = [wintypes.LPCWSTR]
    return [Path(chr(65+i)+':\\') for i in range(26)
            if mask & (1 << i) and kernel.GetDriveTypeW(chr(65+i)+':\\') in (2, 3)]


def indexed_candidates(query: str, root: Path, *, timeout: float = 8) -> tuple[list[Path], str]:
    """One fixed script; user strings enter as JSON on stdin, never shell code."""
    require_windows()
    script = Path(__file__).with_name('windows_search.ps1')
    powershell = Path(os.environ.get('SystemRoot', r'C:\Windows'))/'System32/WindowsPowerShell/v1.0/powershell.exe'
    if not script.is_file():
        return [], 'Manca file_access/windows_search.ps1: reinstalla il pacchetto Accesso file.'
    try:
        run = subprocess.run(
            [str(powershell), '-NoProfile', '-NonInteractive', '-File', str(script)],
            input=json.dumps({'query': query, 'root': str(root)}, ensure_ascii=True),
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            timeout=timeout, shell=False, creationflags=0x08000000)
        if run.returncode or len(run.stdout) > 64000:
            return [], 'Indice Windows non disponibile; ricerca diretta nelle cartelle consentite.'
        result = json.loads(run.stdout.lstrip('\ufeff'))
        if result.get('status') != 'ok':
            return [], 'Indice Windows non disponibile; ricerca diretta nelle cartelle consentite.'
        paths = result.get('paths', [])
        if not isinstance(paths, list) or len(paths) > 50 or any(
                not isinstance(p, str) or len(p) > 32767 for p in paths):
            raise ValueError('Risposta indice non valida')
        return [Path(p) for p in paths], 'Indice Windows interrogato; copertura non necessariamente completa.'
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return [], 'Indice Windows non disponibile o scaduto; ricerca diretta nelle cartelle consentite.'


def installed_locations(query: str) -> list[tuple[Path, str]]:
    """Read registered program identities, not just folder-name matches."""
    require_windows()
    import winreg
    found = []
    for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
            try:
                with winreg.OpenKey(hive, r'Software\Microsoft\Windows\CurrentVersion\Uninstall',
                                    0, winreg.KEY_READ | view) as root:
                    count = min(winreg.QueryInfoKey(root)[0], 3000)
                    for i in range(count):
                        try:
                            with winreg.OpenKey(root, winreg.EnumKey(root, i)) as item:
                                name = winreg.QueryValueEx(item, 'DisplayName')[0]
                                if not isinstance(name, str) or query.casefold() not in name.casefold():
                                    continue
                                for field in ('InstallLocation', 'DisplayIcon'):
                                    try:
                                        raw = winreg.QueryValueEx(item, field)[0]
                                        if not isinstance(raw, str):
                                            continue
                                        path = Path(raw.split(',')[0].strip('" '))
                                        if field == 'DisplayIcon':
                                            path = path.parent
                                        if path.is_absolute() and path.is_dir():
                                            found.append((path, 'Registrazione Windows: '+name[:100]))
                                    except OSError:
                                        pass
                        except OSError:
                            continue
            except OSError:
                continue
    return found[:50]


def long_path(path: Path) -> Path:
    """Expand DOS 8.3 aliases without following a junction to another location."""
    kernel = native_kernel()
    kernel.GetLongPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    kernel.GetLongPathNameW.restype = wintypes.DWORD
    current, tail = Path(path), []
    while True:
        buffer = ctypes.create_unicode_buffer(32768)
        result = kernel.GetLongPathNameW(str(current), buffer, len(buffer))
        if result and result < len(buffer):
            return Path(buffer.value).joinpath(*reversed(tail))
        if current.parent == current:
            raise OSError('Nome del percorso non verificabile.')
        tail.append(current.name)
        current = current.parent
