"""Independent opt-in WhatsApp Business Cloud API settings, never passwords."""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
from settings import default_path

_PHONE=re.compile(r"^[1-9][0-9]{7,14}$")
_MAX_CONTACTS=80

class WhatsAppSettingsError(ValueError): pass

def canonical_phone(value: str) -> str:
    if not isinstance(value,str):
        raise WhatsAppSettingsError("Numero WhatsApp non valido.")
    value=value.strip().replace(" ","").replace("-","")
    if value.startswith("+"):
        value=value[1:]
    if not _PHONE.fullmatch(value):
        raise WhatsAppSettingsError("Usa un numero internazionale con prefisso, da 8 a 15 cifre.")
    return value

def clean_contact(value) -> dict:
    if not isinstance(value,dict) or set(value)!={"phone","name","enabled","read","reply","send"}:
        raise WhatsAppSettingsError("Contatto WhatsApp non valido.")
    number=canonical_phone(value["phone"])
    name=value["name"]
    if (not isinstance(name,str) or not 1<=len(name.strip())<=90 or
            any(ord(c)<32 for c in name)):
        raise WhatsAppSettingsError("Nome contatto non valido.")
    for key in ("enabled","read","reply","send"):
        if type(value[key]) is not bool:
            raise WhatsAppSettingsError("Autorizzazioni WhatsApp non valide.")
    if value["reply"] and not value["read"]:
        raise WhatsAppSettingsError("Per rispondere devi autorizzare la lettura.")
    return {"phone":number,"name":name.strip(),
            "enabled":value["enabled"],"read":value["read"],
            "reply":value["reply"],"send":value["send"]}

def validate_settings(raw) -> dict:
    if not isinstance(raw,dict) or set(raw)!={
            "enabled","auto_reply","reply_voice","free_message_budget","contacts"}:
        raise WhatsAppSettingsError("Configurazione WhatsApp non valida.")
    if any(type(raw[k]) is not bool for k in ("enabled","auto_reply","reply_voice")):
        raise WhatsAppSettingsError("Interruttori WhatsApp non validi.")
    budget=raw["free_message_budget"]
    if type(budget) is not int or not 0<=budget<=1000:
        raise WhatsAppSettingsError("Limite mensile non valido (0-1000).")
    contacts=raw["contacts"]
    if not isinstance(contacts,list) or len(contacts)>_MAX_CONTACTS:
        raise WhatsAppSettingsError("Massimo 80 contatti WhatsApp.")
    found=set()
    cleaned=[]
    for entry in contacts:
        c=clean_contact(entry)
        if c["phone"] in found:
            raise WhatsAppSettingsError("Numero WhatsApp duplicato.")
        found.add(c["phone"])
        cleaned.append(c)
    return {"enabled":raw["enabled"],"auto_reply":raw["auto_reply"],
            "reply_voice":raw["reply_voice"],
            "free_message_budget":budget,"contacts":cleaned}

DEFAULTS={"enabled":False,"auto_reply":False,"reply_voice":True,
          "free_message_budget":0,"contacts":[]}

def config_path()->Path:
    return default_path().with_name("whatsapp-settings.json")

def load_config(path:Path|None=None)->dict:
    target=Path(path) if path is not None else config_path()
    try:
        if target.stat().st_size>50_000:
            raise WhatsAppSettingsError("File impostazioni troppo grande.")
        return validate_settings(json.loads(target.read_text(encoding="utf-8")))
    except FileNotFoundError:
        return validate_settings(DEFAULTS)
    except (OSError,UnicodeError,ValueError,TypeError) as exc:
        raise WhatsAppSettingsError(
            "Configurazione WhatsApp illeggibile: nessuna funzione autorizzata.") from exc

def save_config(config:dict,path:Path|None=None)->None:
    clean=validate_settings(config)
    target=Path(path) if path is not None else config_path()
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.is_symlink():
        raise WhatsAppSettingsError("File impostazioni non sicuro.")
    temporary=target.with_suffix(".tmp")
    if temporary.is_symlink():
        raise WhatsAppSettingsError("File temporaneo non sicuro.")
    try:
        temporary.write_text(json.dumps(clean,ensure_ascii=False,indent=2)+"\n",
                             encoding="utf-8")
        os.replace(temporary,target)
    finally:
        if temporary.is_file():
            temporary.unlink()

def permitted(config:dict,phone:str,permission:str)->dict|None:
    if permission not in ("read","reply","send") or config.get("enabled") is not True:
        return None
    for contact in config.get("contacts",[]):
        if (contact["phone"]==phone and contact["enabled"] is True
                and contact[permission] is True):
            return contact
    return None
