"""Profili per OGNI modello (055; nella 054 erano per famiglia): 3 slot di impostazioni.

Riusa NativeModelConfig / update_native_settings (la configurazione che salvano le
impostazioni) e vive accanto a native.json, in addon-data/modello_locale/profili.json.
Invariante: native.json contiene sempre i valori dello slot attivo del modello in uso; le
modifiche fatte a mano restano lì finché non si usa «Salva in questo profilo».
Migrazione senza perdite: la prima volta che un modello viene visto, i suoi 3 slot copiano i
profili della sua famiglia (versione 054) se esistono; altrimenti lo slot 1 prende i valori
attuali di native.json (se è il modello in uso) e gli slot 2 e 3 i default.
La famiglia serve solo come etichetta e per la migrazione; «famiglia incerta» se non si capisce.
Salvataggio atomico (FIX 3): native.json e profili.json si scrivono insieme (file temporanei,
poi rinomina), con ritorno al profili.json precedente se il secondo passo fallisce.
"""
from __future__ import annotations

import json
import os
import re
import struct
import tempfile
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

# Dimensione in byte dei tipi GGUF a lunghezza fissa (8 = stringa, 9 = array: a parte).
_TIPI = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 1, 10: 8, 11: 8, 12: 8}
_MAX_COPPIE = 100000


def _salta(stream, kind: int, depth: int = 0) -> None:
    """Salta un valore GGUF di tipo `kind` (anche stringhe e array annidati)."""
    if kind in _TIPI:
        stream.seek(_TIPI[kind], 1)
    elif kind == 8:
        (length,) = struct.unpack("<Q", _leggi(stream, 8))
        stream.seek(length, 1)
    elif kind == 9 and depth < 4:
        sub, count = struct.unpack("<IQ", _leggi(stream, 12))
        if sub in _TIPI:
            stream.seek(_TIPI[sub] * count, 1)
        else:
            for _ in range(min(count, 5_000_000)):
                _salta(stream, sub, depth + 1)
    else:
        raise ValueError("Tipo GGUF non valido.")


def _leggi(stream, size: int) -> bytes:
    data = stream.read(size)
    if len(data) != size:
        raise ValueError("File GGUF troncato.")
    return data


def leggi_architettura(model_path) -> str:
    """Valore «general.architecture» dai metadati GGUF, o «» se non leggibile. Scorre le
    coppie chiave/valore (FIX 5: niente buffer fisso da 64 KiB), mai i pesi."""
    try:
        with open(model_path, "rb") as stream:
            if stream.read(4) != b"GGUF":
                return ""
            _version, _tensors, count = struct.unpack("<IQQ", _leggi(stream, 20))
            for _ in range(min(count, _MAX_COPPIE)):
                (klen,) = struct.unpack("<Q", _leggi(stream, 8))
                if klen > 1024:
                    return ""
                key = _leggi(stream, klen)
                (kind,) = struct.unpack("<I", _leggi(stream, 4))
                if key == b"general.architecture":
                    if kind != 8:
                        return ""
                    (vlen,) = struct.unpack("<Q", _leggi(stream, 8))
                    return _leggi(stream, vlen).decode("ascii", "ignore") if vlen <= 64 else ""
                _salta(stream, kind)
    except (OSError, struct.error, ValueError):
        return ""
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


def chiave(model_path) -> str:
    """Identità del modello nei profili: il suo percorso (senza maiuscole)."""
    return os.path.normcase(os.path.abspath(str(model_path))).casefold()


def valori(config: NativeModelConfig) -> dict:
    data = asdict(config)
    return {key: data[key] for key in CAMPI}


def default_valori() -> dict:
    return valori(NativeModelConfig())


def carica(config_path=None) -> dict:
    try:
        data = json.loads(_file(config_path).read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data.setdefault("famiglie", {})
            if not isinstance(data.get("modelli"), dict):
                data["modelli"] = {}
            if isinstance(data["famiglie"], dict):
                data["versione"] = 2
                return data
    except (OSError, ValueError):
        pass
    return {"versione": 2, "famiglie": {}, "modelli": {}}


def _scrivi_temp(directory: Path, name: str, text: str) -> Path:
    with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=directory, prefix=name + ".", suffix=".tmp",
            delete=False) as stream:
        temp = Path(stream.name)
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    return temp


def _salva(data: dict, config_path=None, config: NativeModelConfig | None = None) -> None:
    """Scrive profili.json e, se dato, native.json insieme (FIX 3). Entrambi prima in file
    temporanei; poi profili.json, poi native.json; se native.json fallisce si rimette il
    profili.json di prima, così i due file non restano divergenti."""
    native = _percorso(config_path)
    target = _file(config_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temps = []
    previous = None
    try:
        profili_tmp = _scrivi_temp(target.parent, target.name, json.dumps(data, indent=2))
        temps.append(profili_tmp)
        if config is not None:
            config.validate()
            native_tmp = _scrivi_temp(native.parent, native.name,
                                      json.dumps(asdict(config), ensure_ascii=False, indent=2) + "\n")
            temps.append(native_tmp)
        try:
            previous = target.read_bytes()
        except OSError:
            previous = None
        os.replace(profili_tmp, target)
        if config is not None:
            try:
                os.replace(native_tmp, native)
            except OSError:
                if previous is None:
                    target.unlink(missing_ok=True)
                else:
                    back = _scrivi_temp(target.parent, target.name, previous.decode("utf-8"))
                    temps.append(back)
                    os.replace(back, target)
                raise
    finally:
        for temp in temps:
            if temp.exists():
                temp.unlink()


def _voce(data: dict, model_path, corrente: dict | None, usa_corrente: bool = False) -> dict:
    """Crea i 3 slot del modello se mancano. Migrazione: dai profili della famiglia (054)
    se ci sono; altrimenti slot 1 = valori attuali (solo per il modello in uso), 2 e 3 = default."""
    key = chiave(model_path)
    item = data["modelli"].get(key)
    if not isinstance(item, dict) or not isinstance(item.get("slot"), dict):
        family, _known = riconosci_famiglia(model_path)
        legacy = data.get("famiglie", {}).get(family)
        if isinstance(legacy, dict) and isinstance(legacy.get("slot"), dict) and len(legacy["slot"]) == 3:
            slots = {k: dict(v) for k, v in legacy["slot"].items()}
            last = legacy.get("ultimo", 1)
        else:
            slots = {"1": corrente if (usa_corrente and corrente is not None) else default_valori(),
                     "2": default_valori(), "3": default_valori()}
            last = 1
        item = {"nome": Path(str(model_path)).name, "ultimo": last, "slot": slots}
        data["modelli"][key] = item
    return item


def assicura(config_path=None) -> dict:
    """Migra se serve (all'avvio e a ogni cambio modello). Ritorna
    {'chiave', 'famiglia', 'riconosciuta', 'slot'} per il modello in uso."""
    path = _percorso(config_path)
    config = NativeModelConfig.load(path)
    family, known = riconosci_famiglia(config.model) if config.model else (GENERICA, False)
    data = carica(path)
    before = json.dumps(data, sort_keys=True)
    key = chiave(config.model) if config.model else ""
    slot = 1
    if config.model:
        slot = int(_voce(data, config.model, valori(config), usa_corrente=True)["ultimo"])
    if json.dumps(data, sort_keys=True) != before:
        _salva(data, path)
    return {"chiave": key, "modello": config.model, "famiglia": family, "riconosciuta": known,
            "slot": slot}


def applica_modello(model_path, config_path=None):
    """Chiamata dopo la scelta di un modello: carica lo slot ricordato di QUEL modello.
    Ritorna (configurazione, famiglia, riconosciuta, serve_riavvio); salva i due file insieme."""
    path = _percorso(config_path)
    config = NativeModelConfig.load(path)
    family, known = riconosci_famiglia(model_path)
    data = carica(path)
    # Prima del cambio: i valori attuali restano al modello precedente se non ha ancora profili.
    if config.model:
        _voce(data, config.model, valori(config), usa_corrente=True)
    item = _voce(data, model_path, valori(config))
    slot = str(item["ultimo"])
    revised, reload_needed = update_native_settings(
        config, {"model": str(model_path), **item["slot"][slot]})
    _salva(data, path, revised)
    return revised, family, known, reload_needed


def scegli_slot(model_path, numero: int, config_path=None) -> dict:
    """Cambia slot del modello: scrive in native.json i suoi valori e lo ricorda.
    {'config', 'serve_riavvio', 'campi_riavvio'}: se serve_riavvio, il motore va riavviato."""
    if numero not in SLOT:
        raise ValueError("Profilo non valido: scegli 1, 2 o 3.")
    path = _percorso(config_path)
    config = NativeModelConfig.load(path)
    data = carica(path)
    item = _voce(data, model_path, valori(config), usa_corrente=True)
    revised, reload_needed = update_native_settings(config, item["slot"][str(numero)])
    item["ultimo"] = numero
    _salva(data, path, revised)
    changed = [f for f in CAMPI_RIAVVIO if getattr(config, f) != getattr(revised, f)]
    return {"config": revised, "serve_riavvio": reload_needed, "campi_riavvio": changed}


def salva_in_slot(model_path, numero: int, config_path=None) -> None:
    """«Salva in questo profilo»: copia i valori attuali di native.json nello slot del modello."""
    if numero not in SLOT:
        raise ValueError("Profilo non valido: scegli 1, 2 o 3.")
    path = _percorso(config_path)
    config = NativeModelConfig.load(path)
    data = carica(path)
    item = _voce(data, model_path, valori(config), usa_corrente=True)
    item["slot"][str(numero)] = valori(config)
    item["ultimo"] = numero
    _salva(data, path)


def ripristina_default(model_path, numero: int, config_path=None) -> dict:
    """«Ripristina default» per lo slot (anche per lo slot 1): ricarica i valori di fabbrica."""
    if numero not in SLOT:
        raise ValueError("Profilo non valido: scegli 1, 2 o 3.")
    path = _percorso(config_path)
    data = carica(path)
    item = _voce(data, model_path, valori(NativeModelConfig.load(path)), usa_corrente=True)
    item["slot"][str(numero)] = default_valori()
    _salva(data, path)
    return scegli_slot(model_path, numero, path)


def slot_ricordato(model_path, config_path=None) -> int:
    item = carica(config_path)["modelli"].get(chiave(model_path))
    try:
        return int(item["ultimo"]) if item else 1
    except (KeyError, TypeError, ValueError):
        return 1


def messaggio_famiglia(family: str, known: bool, slot: int) -> str:
    if known:
        return "Famiglia %s: carico il profilo %d di questo modello." % (family, slot)
    return "Famiglia incerta: carico comunque il profilo %d di questo modello." % slot
