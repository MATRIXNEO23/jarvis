"""Scheda di sé (passo 7, decisione 15/11 10:22).

Costruita al momento dai dati veri (add-on attivi, modello locale scelto, GPT collegato,
modalità del microfono) più una breve presentazione scritta a mano. Va al modello solo
per domande su Lumi («chi sei», «come funzioni», «che modello usi»…), che risponde con
parole sue; con il modello spento Lumi risponde con frasi pronte che variano.
«Chi sei» e «cosa puoi fare» (15/11 sera): frasi di Lumi a caso, configurabili in
Frasi di Lumi, con quello che è acceso davvero; «comandi» e «aiuto» restano l'elenco.
"""
from __future__ import annotations

import random
import re
from pathlib import Path

PRESENTAZIONE = (
    "Sono Lumi, un'assistente vocale per Windows. Lavoro soprattutto sul tuo PC: capisco i "
    "comandi a voce con un riconoscitore offline, apro e controllo programmi e finestre, "
    "cerco file, metto musica, timer e sveglie, e converso con un modello locale sul PC o, "
    "se lo colleghi, con GPT. Le azioni le esegue sempre Lumi sul PC, il modello propone.")

_DOMANDA = re.compile(
    r"\b(?:chi\s+sei|come\s+ti\s+chiami|presentati|parlami\s+di\s+te|cosa\s+sei|che\s+cosa\s+sei|"
    r"come\s+funzioni|che\s+modello\s+(?:usi|sei|hai)|quale\s+modello|"
    r"(?:che|quali)\s+add-?on\s+(?:hai|ci\s+sono|sono\s+attivi)|sei\s+un'?\s*(?:ia|intelligenza))\b",
    re.IGNORECASE)


_CHI_SEI = re.compile(
    r"^\W*(?:lumi\W+)?(?:chi\s+sei|come\s+ti\s+chiami|presentati|parlami\s+di\s+te|"
    r"(?:che\s+)?cosa\s+sei)\W*$", re.IGNORECASE)
_COSA_FAI = re.compile(
    r"^\W*(?:lumi\W+)?(?:(?:che\s+)?cosa\s+(?:puoi|sai)\s+fare|cosa\s+fai|"
    r"di\s+cosa\s+sei\s+capace|cosa\s+mi\s+sai\s+fare)\W*$", re.IGNORECASE)

# add-on acceso -> cosa sa fare, in parole semplici (decisione 15/11 sera: niente elenco)
CAPACITA = (
    ("programmi_app", "aprire e chiudere i programmi"),
    ("accesso_file", "cercarti i file"),
    ("controllo_pc", "muovermi tra finestre e tasti"),
    ("musica", "mettere la musica"),
    ("sveglia", "puntare timer e sveglie"),
    ("telegram", "leggere e rispondere su Telegram"),
    ("modello_locale", "chiacchierare con il modello sul PC"),
)

# Chi fornisce i dati veri (impostato da jarvis.py all'avvio): () -> dict come fatti().
FONTE = {"fatti": None}


def chi_sei(text: str) -> bool:
    return isinstance(text, str) and len(text) < 80 and bool(_CHI_SEI.match(text))


def cosa_sai_fare(text: str) -> bool:
    return isinstance(text, str) and len(text) < 80 and bool(_COSA_FAI.match(text))


def elenco_naturale(items) -> str:
    items = [i for i in items if i]
    if not items:
        return ""
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " e " + items[-1]


def capacita(ids=(), online=False) -> str:
    words = [text for ident, text in CAPACITA if ident in ids]
    if online:
        words.append("chiedere ai servizi online le cose difficili")
    return elenco_naturale(words) or "ascoltarti e rispondere ai comandi di base"


def risposta_propria(text: str) -> str:
    """Risposta di Lumi a «chi sei» / «cosa puoi fare», dalle frasi configurabili; "" se no."""
    import frasi_lumi
    if chi_sei(text):
        return frasi_lumi.say("chi_sono")
    if cosa_sai_fare(text):
        info = {}
        try:
            info = FONTE["fatti"]() if FONTE["fatti"] else {}
        except Exception:
            info = {}
        return frasi_lumi.say("cosa_so_fare", capacita=capacita(
            info.get("ids", ()), bool(info.get("online") or info.get("servizi_online"))))
    return ""


def domanda_su_lumi(text: str) -> bool:
    return isinstance(text, str) and len(text) < 200 and bool(_DOMANDA.search(text))


def fatti(*, addons=(), local_model: str = "", local_on: bool = True, online: bool = False,
          mic: str = "") -> dict:
    return {"addons": [a for a in addons if a][:20], "modello": Path(local_model).name if local_model else "",
            "locale": bool(local_on), "online": bool(online), "microfono": mic}


def scheda(info: dict) -> str:
    lines = ["[Scheda di Lumi: dati veri su di te, rispondi con parole tue]", PRESENTAZIONE]
    if info["addons"]:
        lines.append("Add-on attivi: " + ", ".join(info["addons"]) + ".")
    if info["locale"]:
        lines.append("Modello locale: " + (info["modello"] or "scelto nelle impostazioni") + ".")
    else:
        lines.append("Modello locale: spento.")
    lines.append("GPT: " + ("collegato." if info["online"] else "non collegato."))
    if info["microfono"]:
        lines.append("Microfono: " + info["microfono"] + ".")
    return "\n".join(lines)[:1500]


def scheda_breve(info: dict) -> str:
    """Versione corta per il modello locale (prova 15/11: la scheda intera non entrava nel
    contesto di Gemma e lui si presentava come «un modello di Google»)."""
    parts = ["Sei Lumi, assistente vocale per Windows creata da Alberto; esegui i comandi sul PC."]
    parts.append("Modello locale: " + (info["modello"] or "scelto nelle impostazioni") + "."
                 if info["locale"] else "Modello locale: spento.")
    if info["addons"]:
        parts.append("Add-on accesi: " + ", ".join(info["addons"][:6]) + ".")
    parts.append("GPT: " + ("collegato." if info["online"] else "non collegato."))
    return " ".join(parts)[:400]


def risposta_pronta(info: dict, rng=random) -> str:
    """Con il modello spento: frase pronta, diversa di volta in volta."""
    addons = ", ".join(info["addons"][:5]) or "nessun add-on in più"
    choices = (
        "Sono Lumi, la tua assistente vocale per Windows. Adesso ho attivi: %s." % addons,
        "Mi chiamo Lumi: ti aiuto a usare il PC con la voce. Add-on accesi: %s." % addons,
        "Lumi, piacere. Comandi a voce, finestre, file e musica sul tuo PC; ora uso: %s." % addons,
    )
    tail = (" Il modello locale è spento, quindi rispondo solo con i comandi."
            if not info["locale"] else "")
    return rng.choice(choices) + tail


def fatti_da(d) -> dict:
    """Dati veri dal contesto di jarvis.py (d = lumi_contesto.Vivo); ciò che manca si salta."""
    def get(name, default=None):
        try:
            return getattr(d, name)
        except Exception:
            return default
    addons = ()
    ids = ()
    manager = get("addon_manager")
    if manager is not None:
        try:
            enabled = [a for a in manager.list_installed() if a["enabled"]]
            addons = tuple(a["name"] for a in enabled)
            ids = tuple(a["id"] for a in enabled)
        except Exception:
            addons = ()
    model = ""
    try:
        from local_model.native_config import NativeModelConfig
        from local_model.native_settings import default_native_settings_path
        model = NativeModelConfig.load(default_native_settings_path()).model
    except Exception:
        model = ""
    try:
        from model_gate import local_enabled
        local_on = bool(local_enabled())
    except Exception:
        local_on = True
    mic = ""
    mode = get("voice_mode")
    if mode is not None:
        try:
            mic = {"standby": "spento", "premi_per_parlare": "premi per parlare",
                   "ascolto_continuo": "ascolto continuo",
                   "conversazione_gpt": "serve «Lumi» prima di ogni comando"}.get(mode.get(), "")
        except Exception:
            mic = ""
    info = fatti(addons=addons, local_model=model, local_on=local_on,
                 online=bool(get("active_gpt", False)), mic=mic)
    info["ids"] = ids
    try:
        info["servizi_online"] = bool(__import__("servizi_online").disponibili())
    except Exception:
        info["servizi_online"] = False
    return info
