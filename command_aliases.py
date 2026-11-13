"""Comandi personalizzati: parole a scelta dell'utente -> comando già esistente.

Esempio: «sparami {testo}» -> «metti {testo}», «buonanotte» -> «ferma la musica».
La frase viene solo riscritta prima dei comandi locali (voce e casella di testo):
non aggiunge nuovi poteri, il comando risultante passa dagli stessi controlli.
Salvati nel profilo: command-aliases.json (mai nel repository, mai cancellati
se non dall'utente).
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from pathlib import Path

MAX_ALIASES = 300
MAX_PHRASE = 80
MAX_COMMAND = 160
_SLOT = re.compile(r"\{([a-zA-Z_]{1,20})\}")
_WAKE = re.compile(r"^\s*((?:ehi\s+|ok\s+)?lumi[\s,!.:]*)", re.IGNORECASE)
_cache = {"path": None, "mtime": None, "items": []}


def default_file() -> Path | None:
    try:
        from settings import default_path
        return default_path().parent / "command-aliases.json"
    except Exception:
        return None


def _normal(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9{}_]+", " ", text.lower()).split())


def clean(items) -> list[dict]:
    result, seen = [], set()
    for item in items or []:
        if not isinstance(item, dict):
            continue
        phrase = " ".join(str(item.get("phrase", "")).split())[:MAX_PHRASE]
        command = " ".join(str(item.get("command", "")).split())[:MAX_COMMAND]
        section = " ".join(str(item.get("section", "")).split())[:40]
        key = _normal(phrase)
        if not key or not command or key in seen:
            continue
        # Ogni {segnaposto} del comando deve esistere nella frase.
        if not set(_SLOT.findall(command)) <= set(_SLOT.findall(phrase)):
            continue
        seen.add(key)
        result.append({"section": section, "phrase": phrase, "command": command})
        if len(result) >= MAX_ALIASES:
            break
    return result


def load(path: Path | None = None) -> list[dict]:
    path = Path(path) if path else default_file()
    if path is None:
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return clean(data.get("aliases") if isinstance(data, dict) else None)


def save(items, path: Path | None = None) -> None:
    path = Path(path) if path else default_file()
    if path is None:
        raise OSError("Profilo non disponibile.")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"aliases": clean(items)}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    os.replace(tmp, path)
    _cache["mtime"] = None


def _pattern(phrase: str):
    parts, last = [], 0
    for match in _SLOT.finditer(phrase):
        parts.append(re.escape(_normal(phrase[last:match.start()])))
        parts.append(f"(?P<{match.group(1)}>.+?)")
        last = match.end()
    parts.append(re.escape(_normal(phrase[last:])))
    body = r"\s*".join(p for p in parts if p)
    return re.compile(r"^" + body + r"$")


def _items(path=None):
    path = Path(path) if path else default_file()
    try:
        mtime = path.stat().st_mtime if path else None
    except OSError:
        mtime = None
    if _cache["path"] != path or _cache["mtime"] != mtime:
        _cache.update(path=path, mtime=mtime, items=load(path) if mtime else [])
    return _cache["items"]


def rewrite(text: str, items=None, path=None) -> str:
    """Testo -> comando personalizzato (con «Lumi,» iniziale conservato), o testo invariato."""
    if not isinstance(text, str) or not text.strip() or len(text) > 300:
        return text
    items = _items(path) if items is None else clean(items)
    if not items:
        return text
    wake = _WAKE.match(text)
    prefix = wake.group(1) if wake else ""
    body = _normal(text[len(prefix):]).replace("{", "").replace("}", "")
    for item in items:
        match = _pattern(item["phrase"]).fullmatch(body)
        if match:
            values = match.groupdict()
            command = _SLOT.sub(lambda m: values.get(m.group(1), ""), item["command"])
            return (prefix + command).strip()
    return text


# --- Catalogo dei comandi esistenti (per scegliere a cosa associare le tue parole) ---
# {testo} = parte variabile (nome, durata, brano…): le tue parole la mettono in fondo.
_FIXED = {
    "Comandi locali": (
        "aiuto", "stato sistema", "apri download", "elenca download", "cerca file {testo}",
        "apri blocco note", "apri calcolatrice", "apri esplora file", "apri disco locale C",
        "apri browser", "cerca nel browser {testo}", "ultimi comandi"),
    "Timer": (
        "imposta timer {testo}", "timer", "pausa timer", "riprendi timer",
        "quanto manca al timer", "ferma timer", "reset timer", "che ore sono"),
    "Modelli e GPT": ("passa a GPT", "torna a Gemma", "attiva cervello locale",
                      "spegni cervello locale", "attiva cervello online", "riavvia il modello", "spegni cervello online"),
    "Progetti e Telegram": (
        "crea progetto {testo}", "apri progetto {testo}", "elenca progetti",
        "torna alla conversazione generale"),
    "Sveglia": ("imposta sveglia alle {testo}", "ferma la sveglia"),
    "Musica": (
        "metti {testo}", "aggiungi in coda {testo}", "metti la playlist {testo}",
        "pausa", "riprendi", "ferma la musica", "avanti", "indietro",
        "alza il volume della musica", "abbassa il volume della musica"),
    "Controllo PC": (
        "finestre aperte", "passa a {testo}", "chiudi la finestra {testo}", "chiudi la finestra",
        "minimizza", "ingrandisci", "mostra i numeri", "seleziona il {testo}", "apri il {testo}",
        "aprilo", "giù", "su", "clicca su {testo}", "scrivi {testo} nel campo cerca",
        "pulisci la ricerca", "digita {testo}", "premi {testo}", "scorri giù", "scorri su",
        "indietro", "avanti", "su di un livello", "vai alla barra degli indirizzi",
        "cosa posso fare qui", "chiama questa finestra {testo}",
        "riproduci", "file successivo", "file precedente", "riga successiva", "riga precedente",
        "scorri a destra", "scorri a sinistra", "schermo intero", "esci dallo schermo intero",
        "apri gestione attività", "chiudi forzatamente {testo}", "griglia", "chiudi griglia",
        "mouse a destra", "mouse a sinistra", "mouse su", "mouse giù",
        "mouse di poco a destra", "mouse di poco a sinistra", "ancora", "clic destro",
        "invio", "torna alla home", "mostra i comandi", "nascondi i comandi"),
}
# Cosa fa ogni comando (mostrato accanto, in «Le mie parole»).
DESCRIPTIONS = {
    "aiuto": "Apre la guida (F1).",
    "stato sistema": "Dice CPU, RAM e disco.",
    "apri download": "Apre la cartella Download.",
    "elenca download": "Mostra i file in Download.",
    "cerca file {testo}": "Cerca un file per nome.",
    "apri blocco note": "Apre il Blocco note.",
    "apri calcolatrice": "Apre la Calcolatrice.",
    "apri esplora file": "Apre Esplora file.",
    "apri disco locale C": "Apre il disco C:.",
    "apri browser": "Apre il browser predefinito.",
    "cerca nel browser {testo}": "Cerca sul web nel browser.",
    "ultimi comandi": "Mostra gli ultimi comandi dati.",
    "imposta timer {testo}": "Avvia un timer (es. «5 minuti»).",
    "timer": "Apre la regolazione manuale del timer.",
    "pausa timer": "Mette in pausa il timer.",
    "riprendi timer": "Fa ripartire il timer in pausa.",
    "quanto manca al timer": "Dice il tempo che resta.",
    "ferma timer": "Ferma il timer.",
    "reset timer": "Azzera il timer.",
    "che ore sono": "Dice l'ora.",
    "passa a GPT": "Usa GPT per voce e chat.",
    "torna a Gemma": "Usa il modello locale.",
    "crea progetto {testo}": "Crea un progetto con quel nome.",
    "apri progetto {testo}": "Apre un progetto.",
    "elenca progetti": "Mostra i progetti.",
    "torna alla conversazione generale": "Esce dal progetto.",
    "imposta sveglia alle {testo}": "Imposta la sveglia (es. «alle 7:30»).",
    "ferma la sveglia": "Spegne la sveglia che suona.",
    "metti {testo}": "Suona un brano o un video (cartelle o YouTube).",
    "aggiungi in coda {testo}": "Aggiunge un brano dopo quello in corso.",
    "metti la playlist {testo}": "Suona una tua playlist.",
    "pausa": "Mette in pausa la musica.",
    "riprendi": "Riprende la musica.",
    "ferma la musica": "Ferma la musica.",
    "avanti": "Brano successivo.",
    "indietro": "Brano precedente (o ricomincia).",
    "alza il volume della musica": "Volume musica +10.",
    "abbassa il volume della musica": "Volume musica −10.",
    "finestre aperte": "Elenco numerato delle finestre aperte.",
    "passa a {testo}": "Porta davanti una finestra (nome, numero o nome tuo).",
    "chiudi la finestra {testo}": "Chiude quella finestra (chiede se salvare).",
    "chiudi la finestra": "Chiude la finestra in uso.",
    "clicca su {testo}": "Clic sul pulsante o campo con quel nome.",
    "digita {testo}": "Scrive dove c'è il cursore.",
    "premi {testo}": "Preme tasti (es. «Ctrl più C», «invio»).",
    "scorri giù": "Scorre in basso la finestra in uso.",
    "scorri su": "Scorre in alto la finestra in uso.",
    "cosa posso cliccare": "Mette i numeri sugli elementi.",
    "chiama questa finestra {testo}": "Dà un nome tuo alla finestra.",
    "mostra i numeri": "Mette i numeri sugli elementi da cliccare.",
    "seleziona il {testo}": "Seleziona per numero o posizione (il 3, il primo, l'ultimo).",
    "apri il {testo}": "Apre per numero o posizione (doppio clic).",
    "aprilo": "Apre l'elemento selezionato.",
    "giù": "Selezione all'elemento sotto (mentre usi il Controllo PC).",
    "su": "Selezione all'elemento sopra (mentre usi il Controllo PC).",
    "su di un livello": "Esplora file: cartella superiore.",
    "vai alla barra degli indirizzi": "Pronto a dettare un percorso.",
    "scrivi {testo} nel campo cerca": "Svuota il campo Cerca e scrive.",
    "pulisci la ricerca": "Svuota la casella di ricerca.",
    "minimizza": "Riduce a icona la finestra in uso.",
    "ingrandisci": "Ingrandisce la finestra in uso.",
    "cosa posso fare qui": "Suggerisce i comandi per questa finestra.",
    "attiva cervello locale": "Le frasi non capite tornano al modello sul PC (Gemma).",
    "spegni cervello locale": "Niente modello sul PC: solo comandi interni (o GPT se acceso).",
    "attiva cervello online": "Accende GPT (e in futuro i servizi online gratuiti).",
    "riavvia il modello": "Chiude e ricarica il modello locale senza chiudere Lumi (motore separato).",
    "spegni cervello online": "Spegne GPT: nessuna richiesta online.",
    "riproduci": "Preme Riproduci/Play (scritta, pulsante tondo o Invio).",
    "file successivo": "Elemento dopo (a destra nelle copertine, sotto negli elenchi).",
    "file precedente": "Elemento prima.",
    "riga successiva": "Riga sotto.",
    "riga precedente": "Riga sopra.",
    "scorri a destra": "Freccia a destra della riga (es. Netflix), poi rinumera.",
    "scorri a sinistra": "Freccia a sinistra della riga.",
    "schermo intero": "Schermo intero col tasto giusto del programma davanti.",
    "esci dallo schermo intero": "Esce dallo schermo intero (anche solo «esci»).",
    "apri gestione attività": "Apre Gestione attività (Ctrl+Maiusc+Esc).",
    "chiudi forzatamente {testo}": "Chiude un programma bloccato (chiede sempre, mai Lumi).",
    "griglia": "Griglia 3×3 numerata: un numero stringe, «clicca» clicca.",
    "chiudi griglia": "Toglie la griglia.",
    "mouse a destra": "Sposta il puntatore di circa 50 pixel.",
    "mouse a sinistra": "Sposta il puntatore di circa 50 pixel.",
    "mouse su": "Sposta il puntatore di circa 50 pixel.",
    "mouse giù": "Sposta il puntatore di circa 50 pixel.",
    "mouse di poco a destra": "Sposta il puntatore di circa 10 pixel.",
    "mouse di poco a sinistra": "Sposta il puntatore di circa 10 pixel.",
    "ancora": "Ripete l'ultimo spostamento del mouse.",
    "clic destro": "Clic destro dove si trova il puntatore.",
    "invio": "Apre l'elemento selezionato (come doppio clic).",
    "torna alla home": "Home del programma o del sito (Netflix, browser).",
    "mostra i comandi": "Striscia con i comandi validi per la finestra davanti.",
    "nascondi i comandi": "Toglie la striscia dei comandi.",
}


def describe(command: str) -> str:
    if command in DESCRIPTIONS:
        return DESCRIPTIONS[command]
    if command.startswith("apri ") and "{" not in command:
        return "Apre il programma " + command[5:] + "."
    if command.startswith("metti la playlist "):
        return "Suona la playlist " + command[18:] + "."
    if command.startswith("passa a "):
        return "Porta davanti la finestra «" + command[8:] + "»."
    return ""


# Comandi di base (Impostazioni > Personalizzazione comandi).
BASE_SECTIONS = ("Comandi locali", "Timer", "Modelli e GPT", "Progetti e Telegram")
# Comandi di un add-on (Gestisci add-on > sezione dell'add-on).
ADDON_SECTIONS = {"sveglia": "Sveglia", "musica": "Musica", "programmi_app": "Programmi e app",
                  "accesso_file": "Accesso file", "controllo_pc": "Controllo PC"}


def catalog(engine=None, music=None, pc=None) -> dict[str, list[str]]:
    """Sezione -> comandi che Lumi sa già eseguire, compresi i programmi abilitati
    in Programmi e app, le playlist e i nomi delle finestre (si aggiornano da soli)."""
    result = {name: list(items) for name, items in _FIXED.items()}
    programs, files = [], []
    apps = getattr(engine, "program_apps", None)
    try:
        if apps is not None and apps.available():
            for row in apps.entries():
                if row.get("enabled") and row.get("available"):
                    programs.append("apri " + row["name"])
    except Exception:
        pass
    access = getattr(engine, "file_access", None)
    try:
        if access is not None and access.available():
            for item in access.descriptors():
                example = str(item.get("example", "")).strip()
                if example and example not in files:
                    files.append(example)
    except Exception:
        pass
    result["Programmi e app"] = programs
    result["Accesso file"] = files
    try:
        if music is None:
            from musica import runtime
            music = runtime.service()
        if music:
            result["Musica"] += ["metti la playlist " + n for n in sorted(music.playlists(), key=str.lower)]
    except Exception:
        pass
    try:
        if pc is None:
            from controllo_pc import runtime as pc_runtime
            pc = pc_runtime.service()
        if pc:
            result["Controllo PC"] += ["passa a " + v["label"] for v in pc.settings["nicknames"].values()]
    except Exception:
        pass
    return result


def phrase_for(phrase: str, command: str) -> str:
    """Se il comando ha {testo} e le tue parole no, la parte variabile va in fondo."""
    phrase = " ".join(str(phrase).split())
    for slot in _SLOT.findall(command):
        if "{" + slot + "}" not in phrase:
            phrase += " {" + slot + "}"
    return phrase


def section_rows(section: str, commands, items=None) -> list[tuple[str, str]]:
    """[(comando, tue parole separate da «;»)] per la sezione."""
    items = load() if items is None else items
    rows = []
    for command in commands:
        mine = [i["phrase"] for i in items if i["command"] == command]
        rows.append((command, "; ".join(mine)))
    return rows


def replace_section(section: str, values: dict, items=None) -> list[dict]:
    """values: {comando: "parole; altre parole"} → nuovo elenco completo.
    Le righe dei comandi mostrati vengono sostituite; le altre restano."""
    items = load() if items is None else items
    keep = [i for i in items if i["command"] not in values]
    for command, text in values.items():
        for phrase in str(text or "").split(";"):
            if phrase.strip():
                keep.append({"section": section, "phrase": phrase_for(phrase, command),
                             "command": command})
    return clean(keep)


# --- una frase alla volta (Le mie parole: Aggiungi / Modifica / Elimina) --------------
def phrases_for(command: str, items=None) -> list[str]:
    items = load() if items is None else items
    return [i["phrase"] for i in items if i["command"] == command]


def add_phrase(section: str, command: str, phrase: str, path=None) -> str:
    """Aggiunge un modo tuo di dire il comando (il comando standard resta valido)."""
    items = load(path)
    wanted = phrase_for(phrase, command)
    key = _normal(wanted)
    if not key:
        return "Scrivi la frase."
    other = next((i for i in items if _normal(i["phrase"]) == key), None)
    if other is not None:
        return ("C'è già." if other["command"] == command else
                f"«{phrase}» è già usata per «{other['command']}».")
    items.append({"section": section, "phrase": wanted, "command": command})
    cleaned = clean(items)
    if not any(i["phrase"] == wanted for i in cleaned):
        return "Frase non valida."
    save(cleaned, path)
    return f"Aggiunta: «{wanted.replace(' {testo}', ' …')}»."


def edit_phrase(old: str, new: str, path=None) -> str:
    items = load(path)
    target = next((i for i in items if i["phrase"] == old), None)
    if target is None:
        return "Frase non trovata."
    rest = [i for i in items if i is not target]
    save(rest, path)
    message = add_phrase(target["section"], target["command"], new, path)
    if not message.startswith("Aggiunta"):
        save(items, path)                     # niente modifica a metà
        return message
    return "Modificata."


def remove_phrase(phrase: str, path=None) -> str:
    items = load(path)
    save([i for i in items if i["phrase"] != phrase], path)
    return "Eliminata."
