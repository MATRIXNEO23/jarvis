"""Comprensione deterministica prima del modello (nessun modello, nessuna rete).

Quando una frase non è un comando preciso, prima di passarla al modello Lumi:
1. toglie parole di cortesia/riempitivo («per favore», «puoi», articoli…);
2. sostituisce i sinonimi dei verbi con un verbo comune (attiva/avvia/metti → imposta,
   stoppa/spegni → ferma…), sia nella frase sia nei comandi che conosce (catalogo);
3. se la frase coincide con un comando del catalogo → lo esegue («CAPITO COME > …»);
4. con MODELLO OFF, se gli somiglia → chiede «Intendevi …? sì / no».
I comandi di una sola parola + parte variabile («metti …», «passa a …») non vengono
mai presi per sinonimo: «avvia il computer» non diventa musica.
I sinonimi personali si aggiungono in Impostazioni > Personalizzazione comandi.
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from pathlib import Path

# verbo comune -> sinonimi (anche all'infinito e all'imperativo).
SYNONYMS = {
    "imposta": ("metti", "mettere", "imposta", "impostare", "avvia", "avviare", "attiva",
                "attivare", "fai partire", "far partire", "parti con", "setta", "settare",
                "programma", "programmare", "inizia", "iniziare"),
    "ferma": ("ferma", "fermare", "stoppa", "stoppare", "spegni", "spegnere", "blocca",
              "bloccare", "termina", "terminare", "interrompi", "interrompere", "basta con",
              "chiudi il", "annulla"),
    "riprendi": ("riprendi", "riprendere", "continua", "continuare", "rimetti", "fai ripartire"),
    "pausa": ("pausa", "metti in pausa", "pausa a", "sospendi", "sospendere"),
    "apri": ("apri", "aprire", "lancia", "lanciare", "esegui", "eseguire", "mostrami"),
    "alza": ("alza", "alzare", "aumenta", "aumentare", "più alto"),
    "abbassa": ("abbassa", "abbassare", "diminuisci", "diminuire", "riduci", "più basso"),
    "elenca": ("elenca", "elencare", "mostra", "mostrare", "dimmi", "fammi vedere"),
}
FILLERS = ("per favore", "per piacere", "per cortesia", "potresti", "puoi", "riesci a",
           "vorrei che", "vorrei", "voglio", "mi", "ti prego", "dai", "un attimo", "subito",
           "adesso", "ora", "ok", "allora", "ehi", "lumi")
ARTICLES = {"il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "l", "di", "del", "della",
            "dello", "dei", "degli", "delle", "da", "per", "a", "al", "alla", "allo", "ai"}
_SLOT = re.compile(r"\{([a-zA-Z_]{1,20})\}")
# Con il modello ACCESO non si chiede mai «Intendevi…?»: ciò che non coincide con un
# comando va al modello come prima. La domanda sì/no vale con MODELLO OFF.
ASK_THRESHOLD_MODEL_OFF = 0.6
_cache = {"path": None, "mtime": None, "extra": {}}


def _plain(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode().lower()
    return " " + " ".join(re.sub(r"[^a-z0-9{}_]+", " ", text).split()) + " "


def _flatten_map(extra=None):
    pairs = []
    groups = {k: list(v) for k, v in SYNONYMS.items()}
    for word, base in (extra or {}).items():
        groups.setdefault(base, []).append(word)
    for base, words in groups.items():
        for word in words:
            pairs.append((_plain(word).strip(), base))
    pairs.sort(key=lambda p: -len(p[0]))          # prima le espressioni più lunghe
    return pairs


def canonical(text: str, extra=None) -> str:
    value = _plain(text)
    for filler in sorted(FILLERS, key=len, reverse=True):
        value = value.replace(" " + _plain(filler).strip() + " ", " ")
    for word, base in _flatten_map(extra):
        value = value.replace(" " + word + " ", " " + base + " ")
    words = [w for w in value.split() if w not in ARTICLES]
    return " ".join(words)


def _literal_words(command: str) -> list[str]:
    return [w for w in canonical(_SLOT.sub(" ", command)).split()]


def _pattern(command: str, extra=None):
    parts, last = [], 0
    for match in _SLOT.finditer(command):
        literal = canonical(command[last:match.start()], extra)
        if literal:
            parts.append(re.escape(literal))
        parts.append(f"(?P<{match.group(1)}>.+?)")
        last = match.end()
    tail = canonical(command[last:], extra)
    if tail:
        parts.append(re.escape(tail))
    return re.compile("^" + r"\s*".join(parts) + "$")


def _fill(command: str, values: dict) -> str:
    return _SLOT.sub(lambda m: values.get(m.group(1), "").strip(), command)


def _similarity(said: list[str], literal: list[str]) -> float:
    """Parole uguali o quasi (errori di trascrizione: sistemi/sistema) su totale."""
    from difflib import SequenceMatcher
    used, matches = set(), 0
    for word in said:
        for index, other in enumerate(literal):
            if index not in used and (word == other or (
                    len(word) > 3 and SequenceMatcher(None, word, other).ratio() >= 0.8)):
                used.add(index)
                matches += 1
                break
    return 2 * matches / (len(said) + len(literal))


def understand(text: str, commands, model_on: bool = True, extra=None):
    """("esatto", comando) | ("simile", comando, punteggio) | None.

    commands: comandi del catalogo (con {testo} per la parte variabile)."""
    if not isinstance(text, str) or not text.strip() or len(text) > 200:
        return None
    extra = load_extra() if extra is None else extra
    said = canonical(text, extra)
    if not said:
        return None
    raw = " ".join(_plain(text).split())
    ordered = sorted(set(commands), key=lambda c: -len(_literal_words(c)))
    for command in ordered:
        literal = _literal_words(command)
        if len(literal) < 2 and _SLOT.search(command) and not raw.startswith(
                _plain(_SLOT.sub(" ", command)).strip().split(" ")[0] + " "):
            continue                     # «metti …», «passa a …»: solo con il verbo esatto
        match = _pattern(command, extra).fullmatch(said)
        if match:
            return ("esatto", _fill(command, match.groupdict()))
    if model_on:
        return None
    threshold = ASK_THRESHOLD_MODEL_OFF
    best, best_score = None, 0.0
    for command in commands:
        if _SLOT.search(command):
            continue                     # i comandi con parte variabile non si «indovinano»
        literal = _literal_words(command)
        if not literal:
            continue
        score = _similarity(said.split(), literal)
        if score > best_score:
            best, best_score = command, score
    if best is not None and best_score >= threshold and len(said.split()) <= 8:
        return ("simile", best, round(best_score, 2))
    return None


# --- sinonimi personali (profilo: synonyms.json) -------------------------------
def _path() -> Path | None:
    try:
        from settings import default_path
        return default_path().parent / "synonyms.json"
    except Exception:
        return None


def load_extra(path: Path | None = None) -> dict:
    path = Path(path) if path else _path()
    if path is None:
        return {}
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return {}
    if _cache["path"] == path and _cache["mtime"] == mtime:
        return _cache["extra"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    extra = {}
    for word, base in (data.get("synonyms", {}) if isinstance(data, dict) else {}).items():
        word, base = " ".join(str(word).lower().split())[:40], " ".join(str(base).lower().split())[:40]
        if word and base and len(extra) < 300:
            extra[word] = base
    _cache.update(path=path, mtime=mtime, extra=extra)
    return extra


def save_extra(extra: dict, path: Path | None = None) -> None:
    path = Path(path) if path else _path()
    if path is None:
        raise OSError("Profilo non disponibile.")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"synonyms": extra}, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)
    _cache["mtime"] = None


# --- conferma «Intendevi …?» ----------------------------------------------------
_PENDING = {"command": None}
_YES = {"si", "sì", "esatto", "proprio", "confermo", "ok", "va bene", "certo", "giusto"}
_NO = {"no", "annulla", "niente", "lascia stare", "no grazie"}


def ask(command: str) -> str:
    _PENDING["command"] = command
    return f"Intendevi «{command}»? Di' «sì» o «no»."


def answer(text: str):
    """("si", comando) | ("no", None) | None se non c'è domanda o non è una risposta."""
    command = _PENDING["command"]
    if command is None:
        return None
    word = " ".join(_plain(text).split())
    _PENDING["command"] = None
    if word in _YES or word.startswith("si "):
        return ("si", command)
    if word in _NO:
        return ("no", None)
    return None                      # altra frase: la domanda decade


# --- collegamento con Lumi (jarvis.py registra; qui nessuna variabile nuova nelle sue funzioni)
_RUNTIME = {"run_local": None, "commands": None, "write": None, "busy": False}


def register(run_local, commands, write) -> None:
    """run_local(testo): esegue un comando interno; commands(): elenco del catalogo."""
    _RUNTIME.update(run_local=run_local, commands=commands, write=write)


def before_model(text: str) -> bool:
    """Prima di passare al modello: True se la frase è stata capita/gestita qui."""
    run, commands, write = _RUNTIME["run_local"], _RUNTIME["commands"], _RUNTIME["write"]
    if run is None or _RUNTIME["busy"]:
        return False
    reply = answer(text)
    if reply is not None:
        if reply[0] == "no":
            write("LUMI > Va bene, non faccio nulla.")
            return True
        return _run(reply[1])
    try:
        from model_gate import enabled as model_enabled
        result = understand(text, commands(), model_on=model_enabled())
    except Exception:
        return False
    if result is None:
        return False
    if result[0] == "esatto":
        write("CAPITO COME > " + result[1])
        return _run(result[1])
    write("LUMI > " + ask(result[1]))
    return True


def _run(command: str) -> bool:
    _RUNTIME["busy"] = True          # niente seconda interpretazione dello stesso testo
    try:
        _RUNTIME["run_local"](command)
    finally:
        _RUNTIME["busy"] = False
    return True
