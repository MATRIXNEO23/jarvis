"""Frasi del Controllo PC -> (azione, valori). Nessun modello: solo regole precise.

Una frase viene presa solo se ha la forma giusta; se poi non corrisponde a
nessuna finestra/elemento, il servizio la lascia agli altri comandi.
"""
from __future__ import annotations

import re

_WAKE = re.compile(r"^\s*(?:(?:ehi|ok)\s+)?lumi[\s,!.:]*", re.IGNORECASE)
_END = r"[\s.!?]*$"
_ORDINALS = {"prima": 1, "primo": 1, "seconda": 2, "secondo": 2, "terza": 3, "terzo": 3,
             "quarta": 4, "quarto": 4, "quinta": 5, "quinto": 5, "sesta": 6, "sesto": 6,
             "settima": 7, "settimo": 7, "ottava": 8, "ottavo": 8, "nona": 9, "nono": 9,
             "decima": 10, "decimo": 10, "uno": 1, "due": 2, "tre": 3, "quattro": 4,
             "cinque": 5, "sei": 6, "sette": 7, "otto": 8, "nove": 9, "dieci": 10}

_PATTERNS = [
    ("list_windows", re.compile(
        r"^(?:(?:mostra|elenca|dimmi)\s+(?:le\s+)?finestre(?:\s+aperte)?|finestre\s+aperte|"
        r"che\s+finestre\s+(?:ci\s+sono|sono\s+aperte|ho\s+aperto)|cosa\s+c'?\s?è\s+aperto|"
        r"cosa\s+ho\s+aperto|programmi\s+aperti)" + _END, re.I)),
    ("list_elements", re.compile(
        r"^(?:cosa\s+posso\s+cliccare|(?:mostra|elenca)\s+(?:i\s+)?(?:pulsanti|elementi|comandi"
        r"\s+della\s+finestra))(?:\s+(?:in|su|di)\s+(?P<window>.+?))?" + _END, re.I)),
    ("name_window", re.compile(
        r"^(?:chiama|rinomina)\s+(?:questa\s+finestra|la\s+finestra\s+(?P<window>.+?))\s+"
        r"(?:come\s+)?(?P<name>[\w'àèéìòù ]{1,30}?)" + _END, re.I)),
    ("switch", re.compile(
        r"^(?:passa|vai|torna)\s+(?:(?:alla|allo|al|ai|a|sulla|sullo|sul|su)\s+|all'\s*)"
        r"(?:finestra\s+(?:di\s+|del\s+|della\s+)?)?(?P<window>.+?)" + _END, re.I)),
    ("switch", re.compile(
        r"^(?:mostra|apri)\s+(?:la\s+)?finestra\s+(?:di\s+|del\s+|della\s+)?(?P<window>.+?)" + _END,
        re.I)),
    ("close", re.compile(
        r"^chiudi\s+(?:la\s+)?finestra(?:\s+(?:di\s+|del\s+|della\s+)?(?P<window>.+?))?" + _END,
        re.I)),
    ("close", re.compile(r"^chiudi\s+(?P<window>.+?)" + _END, re.I)),
    ("press", re.compile(r"^(?:premi|schiaccia|digita\s+il\s+tasto)\s+(?P<keys>.+?)" + _END, re.I)),
    ("click", re.compile(
        r"^(?:(?P<double>doppio\s+clic(?:k)?)|clicca|clic(?:k)?|premi\s+(?:il\s+)?pulsante|"
        r"seleziona)\s+(?:su\s+|sul\s+|sulla\s+|sullo\s+|nel\s+|nella\s+|il\s+|la\s+)?"
        r"(?P<target>.+?)(?:\s+(?:in|su|di)\s+(?P<window>[^\s].*?))?" + _END, re.I)),
    ("type_in", re.compile(
        r"^scrivi\s+(?P<text>.+?)\s+(?:nel\s+campo|nella\s+casella|nella\s+barra|nel)\s+"
        r"(?P<target>.+?)" + _END, re.I)),
    ("type_in", re.compile(
        r"^scrivi\s+(?:nel\s+campo|nella\s+casella|nella\s+barra)\s+(?P<target>[^:,]+?)"
        r"\s*[:,]\s*(?P<text>.+?)" + _END, re.I)),
    ("type", re.compile(r"^(?:digita|scrivi\s+qui)\s+(?P<text>.+?)" + _END, re.I)),
    ("scroll", re.compile(
        r"^(?:scorri|scroll)\s+(?:in\s+)?(?P<dir>giù|giu|su|in\s+basso|in\s+alto|basso|alto)"
        r"(?:\s+di\s+(?P<amount>\d+|\w+))?" + _END, re.I)),
]

_KEY_WORDS = {"più": "+", "piu": "+", "e": "+"}
_DIRECT_KEYS = {"invio", "enter", "tab", "esc", "escape", "spazio", "canc", "cancella",
                "backspace", "home", "fine"}


def number_of(text: str):
    text = text.strip().lower()
    for prefix in ("la ", "il ", "numero ", "finestra ", "finestra numero "):
        if text.startswith(prefix):
            text = text[len(prefix):]
    if text.isdigit():
        return int(text)
    return _ORDINALS.get(text)


def parse_keys(text: str):
    """«ctrl più c», «Ctrl+Shift+T», «invio», «alt f4» -> ["ctrl", "c"] o None."""
    from .windows import KEYS
    value = text.lower().replace("+", " + ")
    parts = [_KEY_WORDS.get(p, p) for p in value.split()]
    keys = [p for p in parts if p != "+"]
    keys = [k.replace("giù", "giu") for k in keys]
    if not keys or len(keys) > 4 or any(k not in KEYS for k in keys):
        return None
    if len(keys) == 1 and keys[0] not in _DIRECT_KEYS and not keys[0].startswith("f"):
        return None        # «premi a»: troppo ambiguo da solo
    return keys


def parse_command(text: str):
    """(azione, dict) oppure None."""
    if not isinstance(text, str) or len(text) > 300:
        return None
    value = _WAKE.sub("", text).strip()
    for action, pattern in _PATTERNS:
        match = pattern.match(value)
        if not match:
            continue
        values = {k: (v.strip(" \"'«»") if isinstance(v, str) else v)
                  for k, v in match.groupdict().items()}
        if action == "press":
            keys = parse_keys(values["keys"])
            if keys is None:
                continue                      # «premi il pulsante X» -> click
            return "press", {"keys": keys}
        if action == "click":
            values["double"] = bool(values.get("double"))
        if action == "scroll":
            direction = values["dir"].lower()
            amount = values.get("amount")
            amount = (int(amount) if amount and amount.isdigit() else _ORDINALS.get(amount or "", 3))
            values = {"amount": max(1, min(amount, 30)) * (1 if direction in ("su", "in alto", "alto") else -1)}
        return action, values
    return None
