"""Registro dei modelli aggiunti e caselle fisse 1/2/3 (055).

«Aggiungi modello…» non copia più il file: ne ricorda il percorso in
addon-data/modello_locale/modelli_aggiunti.json e lo usa da dove si trova. Se il file sparisce
(disco scollegato, spostato, cancellato) `mancanti()` lo segnala; l'elenco lo salta.
Le 3 caselle (1/2/3) ricordano un modello ciascuna per passare in fretta dall'uno all'altro;
in memoria (RAM) resta comunque UN solo modello alla volta (lo carica il motore).
Scrittura atomica (file temporaneo + rinomina), come native.json.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

CASELLE = (1, 2, 3)
_FILE = "modelli_aggiunti.json"


def _config(config_path=None) -> Path:
    if config_path:
        return Path(config_path)
    from .native_settings import default_native_settings_path
    return default_native_settings_path()


def _percorso(config_path=None) -> Path:
    return _config(config_path).parent / _FILE


def chiave(path) -> str:
    return os.path.normcase(os.path.abspath(str(path))).casefold()


def _carica(config_path=None) -> dict:
    try:
        data = json.loads(_percorso(config_path).read_text(encoding="utf-8"))
        if isinstance(data, dict):
            aggiunti = [str(p) for p in data.get("aggiunti", []) if isinstance(p, str)]
            caselle = {str(k): str(v) for k, v in (data.get("caselle") or {}).items()
                       if str(k) in {str(n) for n in CASELLE} and isinstance(v, str)}
            return {"aggiunti": aggiunti, "caselle": caselle}
    except (OSError, ValueError):
        pass
    return {"aggiunti": [], "caselle": {}}


def _salva(data: dict, config_path=None) -> None:
    target = _percorso(config_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=target.parent, prefix=target.name + ".",
                suffix=".tmp", delete=False) as stream:
            temp = Path(stream.name)
            json.dump({"versione": 1, **data}, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, target)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


def controlla(sorgente) -> Path:
    source = Path(sorgente)
    if source.suffix.lower() != ".gguf" or not source.is_file():
        raise ValueError("Scegli un file .gguf esistente.")
    if "mmproj" in source.name.casefold():
        raise ValueError("Questo è un proiettore di immagini, non un modello di testo.")
    return source


def aggiungi(sorgente, config_path=None) -> Path:
    """Ricorda il modello dove si trova (nessuna copia). ValueError se non va bene o c'è già."""
    source = controlla(sorgente)
    data = _carica(config_path)
    if any(chiave(p) == chiave(source) for p in data["aggiunti"]):
        raise ValueError("Questo modello è già nell'elenco.")
    data["aggiunti"].append(str(source))
    _salva(data, config_path)
    return source


def togli(percorso, config_path=None) -> bool:
    """Toglie il modello dal registro (il file resta dov'è). True se c'era."""
    data = _carica(config_path)
    rimasti = [p for p in data["aggiunti"] if chiave(p) != chiave(percorso)]
    cambiato = len(rimasti) != len(data["aggiunti"])
    data["aggiunti"] = rimasti
    data["caselle"] = {k: v for k, v in data["caselle"].items() if chiave(v) != chiave(percorso)}
    _salva(data, config_path)
    return cambiato


def registrati(config_path=None) -> list[Path]:
    """Modelli aggiunti il cui file esiste ancora."""
    return [Path(p) for p in _carica(config_path)["aggiunti"] if Path(p).is_file()]


def mancanti(config_path=None) -> list[Path]:
    """Modelli aggiunti il cui file non c'è più: Lumi li segnala, non li cancella dal registro."""
    return [Path(p) for p in _carica(config_path)["aggiunti"] if not Path(p).is_file()]


def e_registrato(percorso, config_path=None) -> bool:
    return any(chiave(p) == chiave(percorso) for p in _carica(config_path)["aggiunti"])


def caselle(elenco, in_uso="", config_path=None) -> dict:
    """{1: Path|None, 2: …, 3: …}. Le caselle assegnate restano; quelle vuote o con un file
    sparito si riempiono (senza salvare) coi modelli dell'elenco non ancora assegnati,
    mettendo prima il modello in uso."""
    saved = _carica(config_path)["caselle"]
    valid = {chiave(m): m for m in elenco}
    out, used = {}, set()
    for n in CASELLE:
        k = chiave(saved[str(n)]) if str(n) in saved else None
        if k in valid and k not in used:
            out[n] = valid[k]
            used.add(k)
        else:
            out[n] = None
    pool = ([valid[chiave(in_uso)]] if in_uso and chiave(in_uso) in valid else []) + list(elenco)
    for n in CASELLE:
        if out[n] is None:
            for m in pool:
                if chiave(m) not in used:
                    out[n] = m
                    used.add(chiave(m))
                    break
    return out


def assegna_casella(numero: int, percorso, config_path=None) -> None:
    if numero not in CASELLE:
        raise ValueError("Casella non valida: scegli 1, 2 o 3.")
    if not Path(percorso).is_file():
        raise ValueError("Il modello non esiste più.")
    data = _carica(config_path)
    data["caselle"] = {k: v for k, v in data["caselle"].items() if chiave(v) != chiave(percorso)}
    data["caselle"][str(numero)] = str(percorso)
    _salva(data, config_path)


def elenco_ordinato(elenco, in_uso="", config_path=None) -> list[Path]:
    """Prima le caselle 1/2/3, poi gli altri modelli: i numeri a voce valgono per questo ordine."""
    slots = caselle(elenco, in_uso, config_path)
    first = [slots[n] for n in CASELLE if slots[n] is not None]
    taken = {chiave(m) for m in first}
    return first + [m for m in elenco if chiave(m) not in taken]
