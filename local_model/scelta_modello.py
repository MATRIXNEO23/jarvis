"""«Lumi, cambia modello»: elenco dei modelli locali (.gguf) e salvataggio della scelta.

Riusa NativeModelConfig / update_native_settings (la stessa configurazione delle impostazioni)
e il riavvio del motore già esistente (lumi_model_restart in jarvis.py): qui solo l'elenco e
il salvataggio. Nessun download, nessun caricamento del modello.
"""
from __future__ import annotations

import re
from pathlib import Path

MASSIMO = 9          # i numeri 1..9 si dicono e si riconoscono a voce (risposte.NUMBERS)


def _percorso_config() -> Path:
    from .native_settings import default_native_settings_path
    return default_native_settings_path()


def cartelle_modelli(config_path=None) -> list[Path]:
    """Cartella del modello in uso (dove l'utente tiene i suoi .gguf) e la sottocartella
    «modelli» accanto alla configurazione."""
    path = Path(config_path) if config_path else _percorso_config()
    folders = []
    try:
        from .native_config import NativeModelConfig
        model = NativeModelConfig.load(path).model
        if model:
            folders.append(Path(model).parent)
    except (OSError, ValueError):
        pass
    folders.append(path.parent / "modelli")
    return folders


def elenca_modelli(config_path=None, folders=None) -> list[Path]:
    """File .gguf presenti, in ordine di nome, senza doppioni; esclusi i file «mmproj»
    (proiettori delle immagini, non modelli di testo)."""
    found, seen = [], set()
    for folder in (folders if folders is not None else cartelle_modelli(config_path)):
        try:
            names = sorted(Path(folder).glob("*.gguf"), key=lambda p: p.name.casefold())
        except OSError:
            continue
        for item in names:
            key = str(item.resolve()).casefold() if item.is_file() else None
            if key is None or key in seen or "mmproj" in item.name.casefold():
                continue
            seen.add(key)
            found.append(item)
    return found[:MASSIMO]


def nome_breve(path) -> str:
    """«Qwen_Qwen3-1.7B-Q4_K_M.gguf» → «Qwen Qwen3 1.7B Q4 K M» (leggibile a voce)."""
    return re.sub(r"[\s_\-]+", " ", Path(path).stem).strip()


def modello_in_uso(config_path=None) -> str:
    from .native_config import NativeModelConfig
    try:
        return NativeModelConfig.load(Path(config_path) if config_path else _percorso_config()).model
    except (OSError, ValueError):
        return ""


def salva_scelta(model_path, config_path=None):
    """Scrive il modello scelto in native.json (stesse regole delle impostazioni); ritorna
    la configurazione nuova. Il riavvio del motore lo fa il chiamante."""
    from .native_config import NativeModelConfig
    from .native_settings import update_native_settings
    path = Path(config_path) if config_path else _percorso_config()
    target = Path(model_path)
    if not target.is_file() or target.suffix.lower() != ".gguf":
        raise ValueError("Il modello scelto non esiste più.")
    # 054: riconosce la famiglia e carica lo slot ricordato (stessa strada per «cambia
    # modello» a voce e per «Usa questo» nelle impostazioni).
    from .profili_famiglia import applica_modello
    revised, _family, _known, _reload = applica_modello(target, path)
    return revised


def testo_elenco(models) -> tuple[str, str]:
    """(testo per la finestra/chat, frase da dire a voce) per l'elenco numerato."""
    if not models:
        return ("Non trovo modelli .gguf nella cartella dei modelli.",) * 2
    lines = ["%d. %s" % (n, nome_breve(m)) for n, m in enumerate(models, 1)]
    spoken = "Ho trovato %d modelli. " % len(models) + ". ".join(lines) + ". Quale scegli? Di' il numero."
    return "Modelli locali:\n" + "\n".join(lines) + "\nDi' il numero per sceglierne uno.", spoken


def nota_famiglia(model_path, config_path=None) -> str:
    """Frase per la chat dopo la scelta: famiglia riconosciuta e profilo caricato."""
    from .profili_famiglia import messaggio_famiglia, riconosci_famiglia, slot_ricordato
    family, known = riconosci_famiglia(model_path)
    return messaggio_famiglia(family, known, slot_ricordato(family, config_path))
