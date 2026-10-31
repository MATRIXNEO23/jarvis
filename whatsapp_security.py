"""Windows-user encrypted WhatsApp Cloud API credentials; never settings.json."""
from __future__ import annotations
import base64
import json
import os
from pathlib import Path
import re
from settings import default_path
from telegram_security import _windows_dpapi

class WhatsAppAuthError(RuntimeError): pass
_PHONE_ID=re.compile(r"^[0-9]{5,30}$")
_VERSION=re.compile(r"^v[0-9]{2}\.0$")

def auth_path()->Path:
    return default_path().with_name("whatsapp-cloud.dpapi")

def validate_credentials(data):
    if (not isinstance(data,dict) or set(data)!={
            "phone_number_id","access_token","app_secret","verify_token","api_version"}
            or not isinstance(data["phone_number_id"],str)
            or not _PHONE_ID.fullmatch(data["phone_number_id"])
            or not isinstance(data["api_version"],str)
            or not _VERSION.fullmatch(data["api_version"])):
        raise WhatsAppAuthError("Configurazione Cloud API non valida.")
    for key,min_size,max_size in (
            ("access_token",20,800),("app_secret",16,400),
            ("verify_token",16,400)):
        s=data[key]
        if (not isinstance(s,str) or not min_size<=len(s)<=max_size
                or any(ord(c)<33 or ord(c)>126 for c in s)):
            raise WhatsAppAuthError("Credenziali Cloud API incomplete o non valide.")
    return dict(data)

def save_credentials(data, path:Path|None=None, protect=_windows_dpapi):
    valid=validate_credentials(data)
    target=Path(path) if path is not None else auth_path()
    if target.is_symlink():
        raise WhatsAppAuthError("Percorso credenziali non sicuro.")
    target.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(valid,separators=(",",":")).encode("utf-8")
    sealed=protect(payload,True)
    tmp=target.with_suffix(".tmp")
    if tmp.is_symlink():
        raise WhatsAppAuthError("Percorso temporaneo non sicuro.")
    try:
        tmp.write_bytes(b"JARVIS-WA1\n"+base64.b64encode(sealed))
        os.replace(tmp,target)
    finally:
        if tmp.is_file():
            tmp.unlink()

def load_credentials(path:Path|None=None,protect=_windows_dpapi):
    target=Path(path) if path is not None else auth_path()
    try:
        if target.is_symlink() or target.stat().st_size>12_000:
            raise WhatsAppAuthError("File credenziali non valido.")
        raw=target.read_bytes()
        if not raw.startswith(b"JARVIS-WA1\n"):
            raise WhatsAppAuthError("Formato cifrato non riconosciuto.")
        sealed=base64.b64decode(raw.partition(b"\n")[2],validate=True)
        return validate_credentials(json.loads(protect(sealed,False).decode("utf-8")))
    except (OSError,UnicodeError,ValueError,KeyError) as exc:
        raise WhatsAppAuthError("Cloud API non configurata o credenziali illeggibili.") from exc

def credentials_present(path:Path|None=None)->bool:
    return (Path(path) if path is not None else auth_path()).is_file()
