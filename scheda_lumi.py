"""Scheda di sé (passo 7, decisione 15/11 10:22).

Costruita al momento dai dati veri (add-on attivi, modello locale scelto, GPT collegato,
modalità del microfono) più una breve presentazione scritta a mano. Va al modello solo
per domande su Lumi («chi sei», «come funzioni», «che modello usi»…), che risponde con
parole sue; con il modello spento Lumi risponde con frasi pronte che variano.
«Cosa sai fare» e «comandi» restano l'elenco dei comandi di sempre (stessa fonte delle
capacità reali).
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
    manager = get("addon_manager")
    if manager is not None:
        try:
            addons = tuple(a["name"] for a in manager.list_installed() if a["enabled"])
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
    return fatti(addons=addons, local_model=model, local_on=local_on,
                 online=bool(get("active_gpt", False)), mic=mic)
