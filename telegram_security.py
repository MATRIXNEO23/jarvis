"""Windows DPAPI seal for Telegram MTProto API hash and StringSession.

Sessions never appear in settings.json, command arguments, logs, GitHub or
prompt memory. Scope is the current Windows user on the same computer.
"""
from __future__ import annotations

import base64
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path

from settings import default_path


class TelegramAuthError(RuntimeError):
    pass


class _Blob(ctypes.Structure):
    _fields_=[("cbData",wintypes.DWORD),
              ("pbData",ctypes.POINTER(ctypes.c_byte))]


def _blob(value:bytes):
    buf=ctypes.create_string_buffer(value,max(1,len(value)))
    return _Blob(len(value),ctypes.cast(buf,ctypes.POINTER(ctypes.c_byte))),buf


def _windows_dpapi(value:bytes,encrypt:bool):
    if os.name!="nt":
        raise TelegramAuthError("Le credenziali Telegram richiedono Windows DPAPI.")
    source,backing=_blob(value)
    destination=_Blob()
    fn=(ctypes.windll.crypt32.CryptProtectData if encrypt
        else ctypes.windll.crypt32.CryptUnprotectData)
    # CRYPTPROTECT_UI_FORBIDDEN avoids unexpected desktop dialogs.
    if encrypt:
        ok=fn(ctypes.byref(source),None,None,None,None,0x1,
              ctypes.byref(destination))
    else:
        ok=fn(ctypes.byref(source),None,None,None,None,0x1,
              ctypes.byref(destination))
    if not ok:
        raise TelegramAuthError("Impossibile proteggere o aprire la sessione Telegram.")
    try:
        return ctypes.string_at(destination.pbData,destination.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(destination.pbData)


# File header is a data format, not a visible name: 014-018 wrote JARVIS-TG1.
# The 019-022 rename changed it to LUMI-TG1 and made saved logins unreadable
# ("Formato credenziali non riconosciuto"). Write the original header again
# (also readable by older builds) and accept both.
_HEADER = b"JARVIS-TG1\n"
_HEADERS = (b"JARVIS-TG1\n", b"LUMI-TG1\n")


def credential_path():
    return default_path().with_name("telegram-auth.dpapi")


def save_credentials(api_id:int,api_hash:str,session:str,
                     path:Path|None=None,protect=_windows_dpapi):
    if (type(api_id) is not int or api_id<=0
            or not isinstance(api_hash,str) or len(api_hash)<16
            or not isinstance(session,str) or len(session)<32):
        raise TelegramAuthError("Credenziali Telegram incomplete.")
    target=Path(path) if path is not None else credential_path()
    target.parent.mkdir(parents=True,exist_ok=True)
    raw=json.dumps({"api_id":api_id,"api_hash":api_hash,
                    "session":session},ensure_ascii=False).encode("utf-8")
    encrypted=protect(raw,True)
    # A .dpapi blob is unreadable outside this Windows account.
    tmp=target.with_suffix(".tmp")
    try:
        tmp.write_bytes(_HEADER+base64.b64encode(encrypted))
        os.replace(tmp,target)
    finally:
        if tmp.exists():
            tmp.unlink()


def load_credentials(path:Path|None=None,protect=_windows_dpapi):
    target=Path(path) if path is not None else credential_path()
    try:
        raw=target.read_bytes()
        if not raw.startswith(_HEADERS):
            raise TelegramAuthError("Formato credenziali non riconosciuto.")
        plain=protect(base64.b64decode(raw.split(b"\n",1)[1],
                                       validate=True),False)
        data=json.loads(plain.decode("utf-8"))
        if (type(data.get("api_id")) is not int or data["api_id"]<=0
                or not isinstance(data.get("api_hash"),str)
                or not isinstance(data.get("session"),str)):
            raise TelegramAuthError("Credenziali Telegram incomplete.")
        return data
    except (OSError,ValueError,UnicodeError,KeyError) as exc:
        raise TelegramAuthError(
            "Accesso Telegram non configurato o sessione illeggibile.") from exc


def credentials_present(path=None):
    return (Path(path) if path is not None else credential_path()).is_file()
