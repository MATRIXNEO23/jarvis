"""«Lumi, cambia modello»: elenco dei modelli locali (.gguf) e salvataggio della scelta.

Riusa NativeModelConfig / update_native_settings (la stessa configurazione delle impostazioni)
e il riavvio del motore già esistente (lumi_model_restart in jarvis.py): qui solo l'elenco e
il salvataggio. Nessun download, nessun caricamento del modello.
"""
from __future__ import annotations

import re
from pathlib import Path

MASSIMO = 9          # a voce si riconoscono i numeri 1..9 (risposte.NUMBERS); l'elenco non ha limite


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
    """File .gguf presenti (cartelle dei modelli + modelli aggiunti da dove si trovano), senza
    doppioni e senza limite; esclusi i file «mmproj» (proiettori delle immagini). Ordine:
    prima le caselle 1/2/3, poi gli altri per nome."""
    found, seen = [], set()
    candidates = []
    for folder in (folders if folders is not None else cartelle_modelli(config_path)):
        try:
            candidates += sorted(Path(folder).glob("*.gguf"), key=lambda p: p.name.casefold())
        except OSError:
            continue
    if folders is None:
        from . import registro_modelli
        candidates += sorted(registro_modelli.registrati(config_path), key=lambda p: p.name.casefold())
    for item in candidates:
        try:
            key = str(item.resolve()).casefold() if item.is_file() else None
        except OSError:
            key = None
        if key is None or key in seen or "mmproj" in item.name.casefold():
            continue
        seen.add(key)
        found.append(item)
    if folders is None:
        from . import registro_modelli
        return registro_modelli.elenco_ordinato(found, modello_in_uso(config_path), config_path)
    return found


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
    """(testo per la finestra/chat, frase da dire a voce). A voce solo il conteggio (FIX 6):
    i nomi stanno in chat e nella finestra; i numeri 1/2/3 sono le caselle fisse."""
    if not models:
        return ("Non trovo modelli .gguf nella cartella dei modelli.",) * 2
    lines = ["%d. %s" % (n, nome_breve(m)) for n, m in enumerate(models, 1)]
    spoken = "Ne ho %d. Scegli il numero." % len(models)
    if len(models) > MASSIMO:
        spoken = "Ne ho %d. Scegli il numero, fino a %d: gli altri dalla finestra." % (len(models), MASSIMO)
    return ("Modelli locali (1, 2 e 3 sono le caselle fisse):\n" + "\n".join(lines)
            + "\nDi' il numero per sceglierne uno."), spoken


def proposta_caselle(righe) -> tuple[str, str, dict]:
    """058 (04:50): «cambia modello» propone SOLO le caselle fisse 1/2/3 (le stesse della tendina
    MODELLO in alto). `righe` = [(numero, percorso o None, in_uso)]. Una casella vuota non si propone.
    Ritorna (testo per la chat, frase a voce, {numero: percorso}). L'elenco completo resta nella pagina Modelli."""
    piene = [(n, m) for n, m, _uso in righe if m]
    if not piene:
        frase = "Non ho modelli nelle caselle 1, 2 e 3: scegline uno dalla pagina Modelli."
        return frase, frase, {}
    parti = ["%d %s" % (n, nome_breve(m)) for n, m in piene]
    frase = ", ".join(parti) + ": quale carico?"
    righe_chat = ["%d. %s%s" % (n, nome_breve(m), "   (in uso)" if uso else "")
                  for n, m, uso in righe if m]
    return ("Modelli nelle caselle fisse:\n" + "\n".join(righe_chat) + "\nDi' il numero per caricarlo."), frase, dict(piene)


def nota_famiglia(model_path, config_path=None) -> str:
    """Frase per la chat dopo la scelta: famiglia riconosciuta e profilo caricato."""
    from .profili_famiglia import messaggio_famiglia, riconosci_famiglia, slot_ricordato
    family, known = riconosci_famiglia(model_path)
    return messaggio_famiglia(family, known, slot_ricordato(model_path, config_path))
