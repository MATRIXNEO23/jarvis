"""Profili per famiglia di modello (054): Gemma, Qwen, … con 3 slot di impostazioni ciascuna.

Riusa NativeModelConfig / update_native_settings (la configurazione che salvano le
impostazioni) e vive accanto a native.json, in addon-data/modello_locale/profili.json.
Invariante: native.json contiene sempre i valori dello slot attivo della famiglia in uso; le
modifiche fatte a mano restano lì finché non si usa «Salva in questo profilo».
Migrazione senza perdite: la prima volta che una famiglia viene vista, lo slot 1 prende i
valori attuali di native.json se il modello in uso è di quella famiglia, altrimenti i default;
gli slot 2 e 3 partono dai default.
"""
from __future__ import annotations

import json
import os
import re
import struct
from dataclasses import asdict
from pathlib import Path

from .native_config import NativeModelConfig
from .native_settings import update_native_settings

SLOT = (1, 2, 3)
GENERICA = "generico"
# Solo parametri di rendimento e stile; modello, DLL, personalità, note restano globali.
CAMPI = ("threads", "batch_threads", "context_size", "max_output", "temperature", "top_k",
         "top_p", "seed", "fast_forward", "reply_length", "explain_sentences")
# Cambiano solo dopo il riavvio del motore (vedi native_settings.RELOAD_FIELDS).
CAMPI_RIAVVIO = ("threads", "batch_threads", "context_size", "fast_forward")

_NOMI = (("gemma", re.compile(r"gemma", re.I)), ("qwen", re.compile(r"qwen|qwq", re.I)),
         ("llama", re.compile(r"llama", re.I)), ("mistral", re.compile(r"mistral|mixtral", re.I)),
         ("phi", re.compile(r"(?<![a-z])phi[-_ ]?\d", re.I)))
_ARCH = (("gemma", "gemma"), ("qwen", "qwen"), ("llama", "llama"), ("mistral", "mistral"),
         ("phi", "phi"))


def leggi_architettura(model_path) -> str:
    """Valore «general.architecture» dall'intestazione GGUF, o «» se non leggibile.
    Legge solo l'inizio del file (mai i pesi)."""
    try:
        with open(model_path, "rb") as stream:
            head = stream.read(1 << 16)
        if head[:4] != b"GGUF":
            return ""
        key = b"general.architecture"
        at = head.find(key)
        if at < 0:
            return ""
        at += len(key)
        kind, length = struct.unpack_from("<IQ", head, at)
        if kind != 8 or length > 64:
            return ""
        return head[at + 12: at + 12 + length].decode("ascii", "ignore")
    except (OSError, struct.error):
        return ""


def riconosci_famiglia(model_path, architettura: str | None = None) -> tuple[str, bool]:
    """(famiglia, riconosciuta). Prima i metadati GGUF (se dati o leggibili), poi il nome del
    file. Famiglia sconosciuta: («generico», False) e il chiamante lo segnala."""
    arch = (architettura if architettura is not None else leggi_architettura(model_path)).casefold()
    for family, prefix in _ARCH:
        if arch.startswith(prefix):
            return family, True
    name = Path(str(model_path)).name
    for family, rx in _NOMI:
        if rx.search(name):
            return family, True
    return GENERICA, False


def _percorso(config_path=None) -> Path:
    from .native_settings import default_native_settings_path
    return Path(config_path) if config_path else default_native_settings_path()


def _file(config_path=None) -> Path:
    return _percorso(config_path).parent / "profili.json"


def valori(config: NativeModelConfig) -> dict:
    data = asdict(config)
    return {key: data[key] for key in CAMPI}


def default_valori() -> dict:
    return valori(NativeModelConfig())


def carica(config_path=None) -> dict:
    try:
        data = json.loads(_file(config_path).read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("famiglie"), dict):
            return data
    except (OSError, ValueError):
        pass
    return {"versione": 1, "famiglie": {}}


def _salva(data: dict, config_path=None) -> None:
    target = _file(config_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(".tmp")
    temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(temp, target)


def _voce(data: dict, family: str, corrente: dict | None) -> dict:
    """Crea la famiglia se manca (migrazione: slot 1 = valori attuali, 2 e 3 = default)."""
    item = data["famiglie"].get(family)
    if not isinstance(item, dict) or not isinstance(item.get("slot"), dict):
        item = {"ultimo": 1, "slot": {"1": corrente if corrente is not None else default_valori(),
                                      "2": default_valori(), "3": default_valori()}}
        data["famiglie"][family] = item
    return item


def assicura(config_path=None) -> dict:
    """Migra se serve (chiamata all'avvio e a ogni cambio modello). Ritorna
    {'famiglia', 'riconosciuta', 'slot'} per il modello in uso."""
    path = _percorso(config_path)
    config = NativeModelConfig.load(path)
    family, known = riconosci_famiglia(config.model) if config.model else (GENERICA, False)
    data = carica(path)
    before = json.dumps(data, sort_keys=True)
    item = _voce(data, family, valori(config))
    if json.dumps(data, sort_keys=True) != before:
        _salva(data, path)
    return {"famiglia": family, "riconosciuta": known, "slot": int(item["ultimo"])}


def applica_modello(model_path, config_path=None):
    """Chiamata dopo la scelta di un modello: carica lo slot ricordato della sua famiglia.
    Ritorna (configurazione, famiglia, riconosciuta, serve_riavvio); salva native.json."""
    path = _percorso(config_path)
    config = NativeModelConfig.load(path)
    family, known = riconosci_famiglia(model_path)
    data = carica(path)
    # Prima del cambio: se la famiglia del modello precedente non esiste ancora, la si migra
    # con i valori attuali, così nulla va perso.
    if config.model:
        old_family, _ = riconosci_famiglia(config.model)
        _voce(data, old_family, valori(config))
    item = _voce(data, family, valori(config))
    slot = str(item["ultimo"])
    revised, reload_needed = update_native_settings(
        config, {"model": str(model_path), **item["slot"][slot]})
    revised.save(path)
    _salva(data, path)
    return revised, family, known, reload_needed


def scegli_slot(family: str, numero: int, config_path=None) -> dict:
    """Cambia slot: scrive in native.json i suoi valori e lo ricorda per la famiglia.
    {'config', 'serve_riavvio', 'campi_riavvio'}: se serve_riavvio, il motore va riavviato."""
    if numero not in SLOT:
        raise ValueError("Profilo non valido: scegli 1, 2 o 3.")
    path = _percorso(config_path)
    config = NativeModelConfig.load(path)
    data = carica(path)
    item = _voce(data, family, valori(config))
    revised, reload_needed = update_native_settings(config, item["slot"][str(numero)])
    item["ultimo"] = numero
    revised.save(path)
    _salva(data, path)
    changed = [f for f in CAMPI_RIAVVIO if getattr(config, f) != getattr(revised, f)]
    return {"config": revised, "serve_riavvio": reload_needed, "campi_riavvio": changed}


def salva_in_slot(family: str, numero: int, config_path=None) -> None:
    """«Salva in questo profilo»: copia i valori attuali di native.json nello slot."""
    if numero not in SLOT:
        raise ValueError("Profilo non valido: scegli 1, 2 o 3.")
    path = _percorso(config_path)
    config = NativeModelConfig.load(path)
    data = carica(path)
    item = _voce(data, family, valori(config))
    item["slot"][str(numero)] = valori(config)
    item["ultimo"] = numero
    _salva(data, path)


def ripristina_default(family: str, numero: int, config_path=None) -> dict:
    """«Ripristina default» per lo slot (anche per lo slot 1): ricarica i valori di fabbrica."""
    if numero not in SLOT:
        raise ValueError("Profilo non valido: scegli 1, 2 o 3.")
    path = _percorso(config_path)
    data = carica(path)
    item = _voce(data, family, valori(NativeModelConfig.load(path)))
    item["slot"][str(numero)] = default_valori()
    _salva(data, path)
    return scegli_slot(family, numero, path)


def slot_ricordato(family: str, config_path=None) -> int:
    item = carica(config_path)["famiglie"].get(family)
    try:
        return int(item["ultimo"]) if item else 1
    except (KeyError, TypeError, ValueError):
        return 1


def messaggio_famiglia(family: str, known: bool, slot: int) -> str:
    if known:
        return "Famiglia %s: carico il profilo %d." % (family, slot)
    return "Famiglia del modello sconosciuta: uso il profilo generico %d." % slot
