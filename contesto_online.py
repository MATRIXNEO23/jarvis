"""056b: il contesto mandato online cresce con la richiesta (richiesta utente 17/11 19:01).

Domanda breve («ciao», «che ore sono») = solo l'ultimo scambio. «Approfondisci» e richieste lunghe
= fino a 6 scambi. Allegati e schede (focus file e programmi) solo se non è una domanda breve senza riferimenti.
I token stimati (caratteri / 4) restano in ULTIMO per il log e la diagnostica."""
from __future__ import annotations

import json
import re

MAX_SCAMBI_AMPIO = 6
_AMPIO = re.compile(r"approfond|spiega|dettagli|in dettaglio|descriv|riassum|continua|di piu|di più", re.I)
_RIFERIMENTI = re.compile(r"\b(file|cartell\w*|allegat\w*|document\w*|programm\w*|app|risultat\w*|elenc\w*|"
                          r"contenut\w*|trovat\w*|apri\w*|cerca\w*|il primo|il secondo|il terzo|quell\w+|prima)\b",
                          re.I)
ULTIMO: dict = {}
LOG = None          # jarvis.py ci mette write_line: una riga di log per richiesta


def profilo(spoken: str) -> str:
    from local_model.prompt_breve import breve
    text = (spoken or "").strip()
    if _AMPIO.search(text) or len(text.split()) >= 25:
        return "ampio"
    if _RIFERIMENTI.search(text):
        return "normale"          # si riferisce a file, risultati o a qualcosa di prima
    return "minimo" if breve(text) else "normale"


def _scambi(parsed) -> list:
    return list(parsed.get("breve") or []) if isinstance(parsed, dict) else []


def proporziona(raw: str, spoken: str) -> str:
    """Riduce il JSON di contesto in base al profilo e registra i token stimati."""
    kind = profilo(spoken)
    out = raw
    try:
        parsed = json.loads(raw)
    except (ValueError, TypeError):
        parsed = None
    if isinstance(parsed, dict):
        scambi = _scambi(parsed)
        if kind == "minimo":
            parsed = {"breve": scambi[-1:]} if scambi else {}
        else:
            if kind == "ampio":
                scambi = scambi[-MAX_SCAMBI_AMPIO:]
            if "breve" in parsed:
                parsed["breve"] = scambi
        out = json.dumps(parsed, ensure_ascii=False)
    ULTIMO.clear()
    ULTIMO.update({"profilo": kind, "caratteri": len(out), "token_stimati": (len(out) + 3) // 4,
                   "scambi": len(_scambi(parsed))})
    if callable(LOG):
        try:
            LOG("ONLINE > contesto %s: %d scambi, ~%d token" % (
                kind, ULTIMO["scambi"], ULTIMO["token_stimati"]))
        except Exception:
            pass
    return out
