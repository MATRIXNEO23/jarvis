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

_ORD = (r"(?P<pos>\d{1,3}|primo|prima|secondo|seconda|terzo|terza|quarto|quarta|quinto|"
        r"quinta|sesto|sesta|settimo|settima|ottavo|ottava|nono|nona|decimo|decima|ultimo|ultima|"
        r"penultimo|penultima)")
_KIND = r"(?:\s+(?P<kind>elemento|file|cartella|immagine|foto|video|documento|voce|riga))?"
_ART = r"(?:il\s+|la\s+|l'\s*|lo\s+)?(?:numero\s+)?"

_PATTERNS = [
    # --- aiuto contestuale e numeri sugli elementi
    ("context_help", re.compile(
        r"^(?:cosa\s+posso\s+(?:fare|dire)\s+(?:qui|adesso|ora|in\s+questa\s+finestra)|"
        r"aiutami\s+qui|che\s+comandi\s+(?:ci\s+sono|posso\s+usare)\s+qui|aiuto\s+qui)" + _END, re.I)),
    ("more_help", re.compile(r"^(?:altri|altri\s+comandi|e\s+poi|cos'?\s?altro)" + _END, re.I)),
    ("show_numbers", re.compile(
        r"^(?:(?:mostra|metti|fammi\s+vedere)\s+i\s+numeri|numera(?:\s+gli\s+elementi)?|"
        r"cosa\s+posso\s+cliccare)" + _END, re.I)),
    ("hide_numbers", re.compile(r"^(?:nascondi|togli|leva)\s+i\s+numeri" + _END, re.I)),
    # --- griglia a 9 caselle e mouse a piccoli passi
    ("grid_start", re.compile(
        r"^(?:(?:mostra|apri|attiva)\s+(?:la\s+)?griglia(?:\s+(?:del\s+)?mouse)?|griglia(?:\s+mouse)?)"
        + _END, re.I)),
    ("grid_close", re.compile(r"^(?:chiudi|nascondi|togli|leva)\s+(?:la\s+)?griglia" + _END, re.I)),
    ("click_here", re.compile(
        r"^(?P<right>clic(?:k)?\s+destro|clicca\s+(?:col|con\s+il)\s+(?:tasto\s+)?destro|tasto\s+destro)"
        + _END, re.I)),
    ("nudge", re.compile(
        r"^(?:sposta\s+(?:il\s+)?)?(?:mouse|puntatore|cursore)\s+(?P<small>di\s+poco\s+)?"
        r"(?:a\s+|in\s+|verso\s+)?(?P<dir>destra|sinistra|su|giù|giu|alto|basso)"
        r"(?P<small2>\s+di\s+poco)?" + _END, re.I)),
    ("nudge_again", re.compile(r"^(?:ancora|di\s+nuovo|ancora\s+un\s+po')" + _END, re.I)),
    # --- riproduci / play (scritta, pulsante tondo o Invio)
    ("play", re.compile(
        r"^(?:riproduci|play|fai\s+partire(?:\s+il\s+video)?|metti\s+play|premi\s+play|"
        r"avvia\s+(?:il\s+)?video|guarda(?:\s+ora)?)" + _END, re.I)),
    # --- schermo intero (tasto in base al programma davanti)
    ("fullscreen_on", re.compile(
        r"^(?:(?:metti|mettilo|mettila|vai|passa)\s+(?:lo\s+|a\s+|in\s+)?schermo\s+intero|"
        r"(?:a\s+)?schermo\s+intero|ingrandisci\s+a\s+schermo\s+intero|full\s*screen)" + _END, re.I)),
    ("fullscreen_off", re.compile(
        r"^(?P<bare>esci)?(?:(?:esci|togli|leva|chiudi)\s+(?:dallo\s+|da\s+|lo\s+)?schermo\s+intero|"
        r"schermo\s+normale|esci\s+dal\s+full\s*screen)?" + _END, re.I)),
    # --- righe di copertine (frecce ai lati, es. Netflix)
    ("row_scroll", re.compile(
        r"^(?:scorri\s+(?:la\s+riga\s+)?(?:a\s+|verso\s+)?(?P<dir>destra|sinistra)|"
        r"riga\s+(?P<dir2>avanti|indietro))" + _END, re.I)),
    # --- Gestione attività e chiusura forzata (sempre con conferma, mai Lumi)
    ("task_manager", re.compile(
        r"^(?:apri\s+|mostra\s+)?(?:la\s+)?(?:gestione\s+attivit[aà]|task\s+manager)" + _END, re.I)),
    ("force_close", re.compile(
        r"^(?:chiudi\s+forzatamente|termina\s+forzatamente|forza\s+(?:la\s+)?chiusura\s+(?:di\s+|del\s+|della\s+)?)"
        r"\s*(?P<window>.+?)" + _END, re.I)),
    # --- scelta per numero o posizione (il 3, il primo file, l'ultima cartella)
    ("pick", re.compile(
        r"^(?P<how>clicca|clic(?:k)?|seleziona|scegli|apri|doppio\s+clic(?:k)?\s+(?:su|sul|sulla)?)"
        r"\s*(?:su\s+|sul\s+|sulla\s+)?" + _ART + _ORD + _KIND + _END, re.I)),
    # --- elemento selezionato
    ("open_selected", re.compile(
        r"^(?:aprilo|aprila|apri\s+questo|apri\s+questa|apri\s+quello|apri\s+quella|"
        r"doppio\s+clic(?:k)?|fai\s+doppio\s+clic(?:k)?)" + _END, re.I)),
    ("click_selected", re.compile(r"^(?:clicca|clic(?:k)?|clicca\s+qui|clicca\s+lì)" + _END, re.I)),
    ("open_bare", re.compile(r"^apri" + _END, re.I)),
    # --- passo passo e navigazione (solo se stai usando il Controllo PC: vedi claims)
    ("step", re.compile(r"^(?P<dir>giù|giu|sotto|su|sopra|prossimo|successivo|precedente|"
                        r"destra|sinistra|(?:file|elemento)\s+(?:successivo|precedente)|"
                        r"riga\s+(?:successiva|precedente|sotto|sopra))" + _END, re.I)),
    ("nav", re.compile(r"^(?P<dir>indietro|torna\s+indietro|avanti|vai\s+avanti|"
                       r"su\s+di\s+un\s+livello|livello\s+superiore|cartella\s+superiore|"
                       r"sali\s+di\s+un\s+livello)" + _END, re.I)),
    ("address", re.compile(
        r"^(?:vai\s+(?:alla|nella|sulla)\s+barra\s+degli\s+indirizzi|barra\s+degli\s+indirizzi|"
        r"vai\s+al(?:l')?\s*(?:campo\s+)?indirizzo)" + _END, re.I)),
    # --- finestre
    ("list_windows", re.compile(
        r"^(?:(?:mostra|elenca|dimmi)\s+(?:le\s+)?finestre(?:\s+aperte)?|finestre\s+aperte|"
        r"che\s+finestre\s+(?:ci\s+sono|sono\s+aperte|ho\s+aperto)|cosa\s+c'?\s?è\s+aperto|"
        r"cosa\s+ho\s+aperto|programmi\s+aperti)" + _END, re.I)),
    ("list_elements", re.compile(
        r"^(?:(?:mostra|elenca)\s+(?:i\s+)?(?:pulsanti|elementi|comandi"
        r"\s+della\s+finestra))(?:\s+(?:in|su|di)\s+(?P<window>.+?))?" + _END, re.I)),
    ("name_window", re.compile(
        r"^(?:chiama|rinomina)\s+(?:questa\s+finestra|la\s+finestra\s+(?P<window>.+?))\s+"
        r"(?:come\s+)?(?P<name>[\w'àèéìòù ]{1,30}?)" + _END, re.I)),
    ("window_state", re.compile(
        r"^(?P<how>minimizza|ingrandisci|massimizza|ripristina)(?:\s+(?:la\s+)?finestra)?"
        r"(?:\s+(?:di\s+|del\s+|della\s+)?(?P<window>.+?))?" + _END, re.I)),
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
    # --- campi di testo
    ("clear_field", re.compile(
        r"^(?:pulisci|svuota|cancella|azzera)\s+(?:la\s+)?(?P<target>ricerca|campo\s+.+?|casella\s+.+?|"
        r"barra\s+.+?)" + _END, re.I)),
    ("press", re.compile(r"^(?:premi|schiaccia|digita\s+il\s+tasto)\s+(?P<keys>.+?)" + _END, re.I)),
    ("click", re.compile(
        r"^(?:(?P<double>doppio\s+clic(?:k)?)|clicca|clic(?:k)?|premi\s+(?:il\s+)?pulsante|"
        r"seleziona)\s+(?:su\s+|sul\s+|sulla\s+|sullo\s+|nel\s+|nella\s+|il\s+|la\s+)?"
        r"(?P<target>.+?)(?:\s+(?:in|su|di)\s+(?P<window>[^\s].*?))?" + _END, re.I)),
    ("type_in", re.compile(
        r"^(?P<mode>scrivi|aggiungi)\s+(?P<text>.+?)\s+(?:nel\s+campo|nella\s+casella|nella\s+barra|"
        r"nella\s+ricerca|nel)\s+(?P<target>.+?)" + _END, re.I)),
    ("type_in", re.compile(
        r"^(?P<mode>cerca)\s+(?P<text>.+?)\s+(?P<target>nella\s+ricerca|nel\s+campo\s+cerca)" + _END, re.I)),
    ("type_in", re.compile(
        r"^(?P<mode>scrivi|aggiungi)\s+(?:nel\s+campo|nella\s+casella|nella\s+barra)\s+(?P<target>[^:,]+?)"
        r"\s*[:,]\s*(?P<text>.+?)" + _END, re.I)),
    ("type", re.compile(r"^(?:digita|scrivi\s+qui)\s+(?P<text>.+?)" + _END, re.I)),
    ("scroll", re.compile(
        r"^(?:scorri|scroll)\s+(?:in\s+)?(?P<dir>giù|giu|su|in\s+basso|in\s+alto|basso|alto)"
        r"(?:\s+di\s+(?P<amount>\d+|\w+))?" + _END, re.I)),
]

# Destinazioni che appartengono ad altri comandi di Lumi: mai finestre.
RESERVED = re.compile(
    r"^(gpt|chatgpt|gemma|il\s+modello|modello|modello\s+locale|conversazione(\s+generale)?|"
    r"la\s+conversazione.*|progetto.*|musica|la\s+musica|timer|il\s+timer|sveglia|la\s+sveglia|"
    r"cartella.*|indietro.*|lumi|jarvis)$", re.I)

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


def _position(text: str):
    """1, 2, … oppure -1 (ultimo), -2 (penultimo)."""
    text = text.lower()
    if text.isdigit():
        return int(text)
    if text in ("ultimo", "ultima"):
        return -1
    if text in ("penultimo", "penultima"):
        return -2
    return _ORDINALS.get(text)


def parse_keys(text: str):
    """«ctrl più c», «Ctrl+Shift+T», «invio», «alt f4» -> ["ctrl", "c"] o None."""
    from controllo_comune.windows import KEYS
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
    bare = re.match(r"^(?:il|la|l'|numero|il\s+numero)\s*" + _ORD + _END, value, re.I)
    if bare:                                  # «il 3», «numero 7»: dopo «mostra i numeri»
        return "pick", {"position": _position(bare.group("pos")), "kind": "", "how": "select",
                        "bare": True}
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
        window = values.get("window")
        if (isinstance(window, str) and RESERVED.match(" ".join(window.lower().split()))
                and not (action == "force_close" and window.lower() in ("lumi", "jarvis"))):
            return None                       # «passa a GPT», «chiudi la musica»…: non è una finestra
        if action == "click":
            values["double"] = bool(values.get("double"))
            if number_of(values["target"]) is not None or values["target"].lower().startswith(
                    ("il numero", "numero")):
                continue
        if action == "pick":
            how = values["how"].lower()
            values = {"position": _position(values["pos"]), "kind": (values.get("kind") or "").lower(),
                      "how": ("double" if how.startswith(("apri", "doppio")) else
                              "select" if how in ("seleziona", "scegli", "vai") else "click")}
        if action == "type_in":
            mode = (values.get("mode") or "scrivi").lower()
            target = values["target"]
            if mode == "cerca" or target.lower() in ("ricerca", "nella ricerca"):
                target = "cerca"
            values = {"text": values["text"], "target": target, "window": values.get("window"),
                      "append": mode == "aggiungi"}
        if action == "clear_field":
            target = values["target"].lower()
            values = {"target": "cerca" if target == "ricerca" else
                      re.sub(r"^(?:campo|casella|barra)\s+", "", values["target"])}
        if action == "window_state":
            how = values["how"].lower()
            values = {"how": "ingrandisci" if how == "massimizza" else how,
                      "window": values.get("window")}
        if action == "fullscreen_off":
            if not value.strip(" .!?"):
                continue
            values = {"on": False, "bare": bool(values.get("bare")) and value.lower().strip(" .!?") == "esci"}
            return "fullscreen", values
        if action == "fullscreen_on":
            return "fullscreen", {"on": True, "bare": False}
        if action == "row_scroll":
            direction = (values.get("dir") or values.get("dir2") or "").lower()
            return action, {"dir": "destra" if direction in ("destra", "avanti") else "sinistra"}
        if action == "nudge":
            direction = values["dir"].lower().replace("giù", "giu")
            direction = {"alto": "su", "basso": "giu"}.get(direction, direction)
            return action, {"dir": direction,
                            "amount": 10 if (values.get("small") or values.get("small2")) else 50}
        if action == "nudge_again":
            return "nudge", {"dir": "ancora"}
        if action == "click_here":
            return action, {"right": True}
        if action in ("play", "task_manager", "grid_start", "grid_close"):
            return action, {}
        if action in ("step", "nav"):
            values = {"dir": values["dir"].lower()}
        if action == "scroll":
            direction = values["dir"].lower()
            amount = values.get("amount")
            amount = (int(amount) if amount and amount.isdigit() else _ORDINALS.get(amount or "", 3))
            values = {"amount": max(1, min(amount, 30)) * (1 if direction in ("su", "in alto", "alto") else -1)}
        return action, values
    return None
