"""«Cosa ti ho detto prima?» — risposta di Lumi dalla cronologia della chat (15/11 sera).

Lumi cerca da sola nella chat aperta (salvata parola per parola), senza passare dal
modello: risposta esatta e immediata anche sul Pavilion.
- «cosa ti ho detto/chiesto (prima | poco fa)?»  -> l'ultima cosa che hai scritto;
- «… 3 turni fa» / «… tre messaggi fa»           -> la terza dall'ultima;
- «… prima di questo argomento»                  -> gli ultimi scambi scritti in chat
  (l'argomento non si riconosce in modo affidabile: scegli tu).
"""
from __future__ import annotations

import re

_NUMERI = {"un": 1, "uno": 1, "una": 1, "due": 2, "tre": 3, "quattro": 4, "cinque": 5,
           "sei": 6, "sette": 7, "otto": 8, "nove": 9, "dieci": 10}

_DOMANDA = re.compile(
    r"^\W*(?:lumi\W+)?(?:che\s+)?cosa\s+ti\s+(?:ho|avevo)\s+(?:detto|chiesto|scritto)"
    r"(?:\s+(?P<quando>prima\s+di\s+quest\w*\s+argomento|prima|poco\s+fa|"
    r"(?P<n>\d{1,2}|" + "|".join(_NUMERI) + r")\s+(?:turn[io]|messaggi[o]?|domand[ae]|volte?)\s+fa))?"
    r"\W*$", re.IGNORECASE)

ARGOMENTO = 3   # quanti scambi mostrare per «prima di questo argomento»

# Tutto quello che l'utente dice o scrive da quando Lumi è aperta, anche i comandi risolti
# da Lumi senza modello (prova sul Pavilion 15/11: «cosa ti ho detto prima» saltava
# «ricordati che…», «chi sei», timer…). Dopo un riavvio si usa la cronologia della chat.
from collections import deque
ULTIMI = deque(maxlen=50)


def registra(text: str) -> None:
    text = " ".join(str(text or "").split())
    if text and not (ULTIMI and ULTIMI[-1] == text):
        ULTIMI.append(text)


def capisci(text: str):
    """None se non è una domanda di richiamo, altrimenti ("ultimo", n) o ("argomento", 0)."""
    if not isinstance(text, str) or len(text) > 120:
        return None
    match = _DOMANDA.match(text)
    if match is None:
        return None
    if match.group("quando") and "argomento" in match.group("quando").casefold():
        return ("argomento", 0)
    raw = match.group("n")
    if raw:
        n = int(raw) if raw.isdigit() else _NUMERI[raw.casefold()]
        return ("ultimo", max(1, n))
    return ("ultimo", 1)


def _corto(text: str, limit: int = 220) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


def rispondi(text: str, pairs) -> tuple[str, str] | None:
    """pairs: [(domanda, risposta)] della chat, dalla più vecchia. -> (scritto, detto)."""
    request = capisci(text)
    if request is None:
        return None
    current = " ".join(str(text).split())
    said = list(ULTIMI)
    while said and said[-1] == current:          # la domanda stessa non conta
        said.pop()
    asked = said or [q for q, _a in pairs if str(q).strip()]
    if not asked:
        return ("In questa chat non mi hai ancora detto niente.",) * 2
    kind, n = request
    if kind == "argomento":
        last = asked[-ARGOMENTO:]
        lines = ["Le ultime cose che mi hai detto in questa chat:"]
        lines += ["%d) «%s»" % (i + 1, _corto(q, 160)) for i, q in enumerate(last)]
        return ("\n".join(lines), "Te le ho scritte in chat: dimmi quale ti serve.")
    if n > len(asked):
        message = ("In questa chat ci sono solo %d messaggi tuoi." % len(asked) if len(asked) > 1
                   else "In questa chat c'è un solo messaggio tuo: «%s»." % _corto(asked[0]))
        return (message, message)
    quote = _corto(asked[-n])
    when = "Prima" if n == 1 else "%d messaggi fa" % n
    message = "%s mi hai detto: «%s»." % (when, quote)
    return (message, message)


def coppie_chat_aperta(count: int = 32):
    """(domanda, risposta) della chat aperta, dalla più vecchia; [] se non c'è."""
    rows = __import__("chat_elenco").contesto_recente(count)
    pairs = []
    for row in rows:
        try:
            (_ru, question), (_ra, answer) = row
        except (TypeError, ValueError):
            continue
        pairs.append((question, answer))
    return pairs


def risposta_di_lumi(text: str):
    """Ciò che Lumi risolve da sola, prima di qualsiasi modello (Gemma, GPT o online):
    «cancellalo», «chi sei», «cosa puoi fare», «cosa ti ho detto prima».
    -> (scritto, detto) oppure None. Prova 16/11: col GPT acceso queste frasi finivano a GPT."""
    memory = __import__("ricordi")
    own = (memory.cancella_se_chiesto(memory.cervello(), text)
           or __import__("scheda_lumi").risposta_propria(text))
    if own:
        return own, own
    return rispondi(text, coppie_chat_aperta())
