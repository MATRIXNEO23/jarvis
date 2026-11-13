"""Frasi di Lumi: tante varianti per ogni azione, scelte a caso (mai la stessa due
volte di fila), personalizzabili. Le predefinite restano sempre; le frasi dell'utente
si aggiungono, si modificano o si tolgono una alla volta (profilo: frasi.json).
Una predefinita tolta dall'utente si recupera con «Ripristina predefinite».

Segnaposto nelle frasi: {nome}, {finestra}, {comando}, {testo}, {numero}, {tasti}.
"""
from __future__ import annotations

import json
import os
import random
from pathlib import Path

# categoria -> azione -> (descrizione, frasi predefinite)
DEFAULTS: dict[str, dict[str, tuple[str, tuple[str, ...]]]] = {
    "Saluti": {
        "avvio_mattina": ("All'avvio, di mattina", (
            "Buongiorno! Sono pronta.", "Buongiorno, eccomi qui.", "Ben svegliato! Ci sono.",
            "Buongiorno! Cosa facciamo oggi?", "Eccomi, buongiorno. Dimmi pure.",
            "Buongiorno! Tutto pronto da questa parte.")),
        "avvio_pomeriggio": ("All'avvio, di pomeriggio", (
            "Buon pomeriggio! Sono pronta.", "Eccomi, buon pomeriggio.",
            "Buon pomeriggio! Cosa ti serve?", "Ciao! Pronta per il pomeriggio.",
            "Buon pomeriggio, ci sono.")),
        "avvio_sera": ("All'avvio, di sera", (
            "Buonasera! Sono pronta.", "Eccomi, buonasera.", "Buonasera! Cosa facciamo?",
            "Ciao, buonasera. Ti ascolto.", "Buonasera, tutto pronto.")),
        "avvio_notte": ("All'avvio, di notte", (
            "Ciao! Ancora sveglio? Ci sono.", "Eccomi, anche a quest'ora.",
            "Buonanotte quasi… ma sono pronta.", "Ci sono, dimmi pure.")),
        "chiusura_giorno": ("Alla chiusura, di giorno", (
            "A dopo!", "Ciao, a più tardi.", "Buona giornata!", "Ci sentiamo dopo.",
            "Alla prossima!", "Chiudo. A presto!")),
        "chiusura_sera": ("Alla chiusura, di sera", (
            "Buona serata!", "A domani!", "Buonanotte!", "Ciao, buona serata.",
            "Riposati, a domani.", "Chiudo. Buona notte!")),
    },
    "Comprensione": {
        "intendevi": ("Quando una frase somiglia a un comando", (
            "Intendevi «{comando}»?", "Volevi dire «{comando}»?", "Ti riferisci a «{comando}»?",
            "Faccio «{comando}», giusto?", "Dici «{comando}»?", "Parli di «{comando}»?",
            "Forse intendevi «{comando}»?", "Devo fare «{comando}»?")),
        "capito_come": ("Quando ha capito il comando con altre parole", (
            "Ok, {comando}.", "Capito: {comando}.", "Va bene, {comando}.", "Fatto: {comando}.",
            "Subito: {comando}.")),
        "annullato": ("Quando rispondi no", (
            "Va bene, non faccio nulla.", "Ok, lascio stare.", "Nessun problema, annullato.",
            "Come vuoi, niente da fare.", "Ok, fermo tutto.")),
    },
    "Controllo PC": {
        "passo": ("Passa a una finestra", (
            "Passo a {finestra}.", "Ecco {finestra}.", "Vado su {finestra}.",
            "Eccoti in {finestra}.", "Apro {finestra}.", "Ci sono: {finestra}.")),
        "chiudo": ("Chiude una finestra", (
            "Chiudo {finestra}.", "Ok, chiudo {finestra}.", "{finestra} chiusa.",
            "Via {finestra}.")),
        "minimizza": ("Riduce a icona una finestra", (
            "Riduco {finestra}.", "{finestra} ridotta a icona.", "Metto giù {finestra}.")),
        "ingrandisci": ("Ingrandisce una finestra", (
            "Ingrandisco {finestra}.", "{finestra} a tutto schermo.", "Ecco {finestra} più grande.")),
        "ripristina": ("Ripristina una finestra", (
            "Ripristino {finestra}.", "{finestra} di nuovo normale.")),
        "clic": ("Clic su un elemento", (
            "Clic su «{nome}».", "Premo «{nome}».", "Ecco, «{nome}».", "Fatto: «{nome}».")),
        "doppio": ("Doppio clic / apre l'elemento", (
            "Apro «{nome}».", "Doppio clic su «{nome}».", "Ecco «{nome}».", "Apro subito «{nome}».")),
        "selezionato": ("Seleziona un elemento", (
            "Selezionato «{nome}».", "Sono su «{nome}».", "Ecco «{nome}».", "«{nome}», selezionato.",
            "Qui c'è «{nome}».")),
        "scritto": ("Scrive in un campo", (
            "Scritto in «{nome}».", "Fatto, ho scritto in «{nome}».", "Ecco, «{nome}» compilato.")),
        "aggiunto": ("Aggiunge testo in un campo", (
            "Aggiunto in «{nome}».", "Ho aggiunto il testo in «{nome}».")),
        "pulito": ("Svuota un campo", (
            "Campo svuotato.", "Ripulito.", "Fatto, il campo è vuoto.", "Ricerca cancellata.")),
        "tasti": ("Preme una scorciatoia", (
            "Premo {tasti}.", "{tasti}, fatto.", "Ecco {tasti}.")),
        "scorro_giu": ("Scorre verso il basso", ("Scorro giù.", "Giù.", "Vado più in basso.")),
        "scorro_su": ("Scorre verso l'alto", ("Scorro su.", "Su.", "Torno più in alto.")),
        "indietro": ("Esplora file: indietro", ("Torno indietro.", "Indietro.", "Cartella precedente.")),
        "avanti": ("Esplora file: avanti", ("Avanti.", "Vado avanti.")),
        "su_livello": ("Esplora file: livello superiore", (
            "Salgo di un livello.", "Cartella superiore.", "Su di un livello.")),
        "indirizzi": ("Va alla barra degli indirizzi", (
            "Sono nella barra degli indirizzi: detta il percorso.", "Barra degli indirizzi pronta.")),
        "numeri": ("Mostra i numeri sugli elementi", (
            "Ecco i numeri: di' «clicca il» e il numero.", "Ho numerato gli elementi.",
            "Numeri pronti: scegli quello che vuoi.")),
        "conferma": ("Chiede conferma prima di agire", (
            "{testo}? Di' sì o no.", "{testo}: confermi?", "Vuoi che {testo_minuscolo}?",
            "{testo}, va bene?")),
        "apri_selezionato": ("«Apri» da solo con un elemento selezionato", (
            "Apro «{nome}»? Se volevi un programma, di' «apri» e il nome insieme.",
            "Apro il file selezionato, «{nome}»?",)),
    },
    "Lumi": {
        "minimizzo": ("Si riduce a icona", (
            "Mi metto da parte. Chiamami quando vuoi.", "Mi riduco, resto in ascolto.",
            "Ok, sparisco nella barra.", "Mi faccio piccola.")),
        "sveglia": ("Riapre l'interfaccia", (
            "Eccomi!", "Sono qui.", "Rieccomi.", "Ci sono, dimmi.", "Presente!")),
        "nascondo": ("Nasconde l'avatar", (
            "Mi nascondo. Di' «Lumi, sveglia» per riavermi.", "Ok, sparisco.",
            "Nascosta. Mi ritrovi con «sveglia».")),
        "riavvio": ("Si riavvia", ("Mi riavvio, torno subito.", "Riavvio in corso, a tra poco.")),
    },
}


def _path() -> Path | None:
    try:
        from settings import default_path
        return default_path().parent / "frasi.json"
    except Exception:
        return None


_cache = {"path": None, "mtime": None, "data": {"added": {}, "removed": {}}}
_last: dict[str, str] = {}


def load(path: Path | None = None) -> dict:
    path = Path(path) if path else _path()
    empty = {"added": {}, "removed": {}}
    if path is None:
        return empty
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return empty
    if _cache["path"] == path and _cache["mtime"] == mtime:
        return _cache["data"]
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raw = {}
    data = {"added": {}, "removed": {}}
    for part in ("added", "removed"):
        for key, items in (raw.get(part) or {}).items() if isinstance(raw, dict) else ():
            if isinstance(items, list):
                data[part][str(key)[:60]] = [str(i)[:200] for i in items if isinstance(i, str)][:100]
    _cache.update(path=path, mtime=mtime, data=data)
    return data


def save(data: dict, path: Path | None = None) -> None:
    path = Path(path) if path else _path()
    if path is None:
        raise OSError("Profilo non disponibile.")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)
    _cache["mtime"] = None


def _defaults(key: str) -> tuple[str, ...]:
    for actions in DEFAULTS.values():
        if key in actions:
            return actions[key][1]
    return ()


def phrases(key: str, data: dict | None = None) -> list[tuple[str, bool]]:
    """[(frase, è_tua)] attive per l'azione: predefinite non tolte + tue."""
    data = load() if data is None else data
    removed = set(data["removed"].get(key, []))
    result = [(p, False) for p in _defaults(key) if p not in removed]
    result += [(p, True) for p in data["added"].get(key, [])]
    return result


def say(key: str, data: dict | None = None, **values) -> str:
    """Una frase a caso per l'azione (diversa dall'ultima), con i segnaposto riempiti."""
    options = [p for p, _mine in phrases(key, data)] or list(_defaults(key)) or ["{testo}"]
    if len(options) > 1 and _last.get(key) in options:
        options = [p for p in options if p != _last[key]]
    choice = random.choice(options)
    _last[key] = choice
    testo = str(values.get("testo", ""))
    values.setdefault("testo_minuscolo", testo[:1].lower() + testo[1:])
    try:
        return choice.format(**{k: v for k, v in values.items()})
    except (KeyError, IndexError, ValueError):
        return choice


def greeting(moment: str, hour: int) -> str:
    """moment: "avvio" | "chiusura"."""
    if moment == "avvio":
        key = ("avvio_notte" if hour < 6 else "avvio_mattina" if hour < 13 else
               "avvio_pomeriggio" if hour < 18 else "avvio_sera")
    else:
        key = "chiusura_sera" if hour >= 18 or hour < 6 else "chiusura_giorno"
    return say(key)


# --- modifiche dell'utente, una alla volta -----------------------------------------
def add(key: str, text: str, path=None) -> None:
    data = load(path)
    text = " ".join(str(text).split())[:200]
    if text and text not in data["added"].setdefault(key, []):
        data["added"][key].append(text)
    save(data, path)


def edit(key: str, old: str, new: str, path=None) -> None:
    """Le tue frasi si modificano; una predefinita modificata diventa una tua
    (la predefinita viene tolta, recuperabile con Ripristina)."""
    data = load(path)
    new = " ".join(str(new).split())[:200]
    mine = data["added"].setdefault(key, [])
    if old in mine:
        mine[mine.index(old)] = new
    else:
        data["removed"].setdefault(key, []).append(old)
        if new and new not in mine:
            mine.append(new)
    save(data, path)


def remove(key: str, text: str, path=None) -> None:
    data = load(path)
    mine = data["added"].setdefault(key, [])
    if text in mine:
        mine.remove(text)
    elif text in _defaults(key):
        data["removed"].setdefault(key, []).append(text)
    save(data, path)


def restore_defaults(key: str, path=None) -> None:
    """Rimette le predefinite tolte di quell'azione (le tue restano)."""
    data = load(path)
    data["removed"].pop(key, None)
    save(data, path)
