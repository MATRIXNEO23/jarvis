"""056b: saluti e domande brevi non ripetono la risposta precedente.

Per un saluto: meno cronologia (un solo scambio, con la vecchia risposta tagliata), nessun
ricordo del second brain. Per una domanda breve: al massimo due scambi con risposte tagliate.
L'ultimo messaggio è segnato chiaramente come l'unico a cui rispondere."""
from __future__ import annotations

import re

SEPARATORE = ("[Sopra: conversazione precedente, solo contesto; non ripeterla.]\n"
              "Messaggio da cui partire per rispondere (rispondi solo a questo):\n")
_SALUTI = re.compile(r"^(ciao|salve|buongiorno|buonasera|buonanotte|hey|ehi|ei|hola|hello|hi|"
                     r"grazie|ok|va bene|perfetto|a dopo|arrivederci|come stai|come va)\b[\s!?.,]*"
                     r"(lumi|jarvis)?[\s!?.,]*$", re.I)
_APPROFONDISCI = re.compile(r"approfond|spiega|dettagli|continua|ripeti|di piu|di più|riassum", re.I)
LIMITE_RISPOSTA_VECCHIA = 280


def saluto(text: str) -> bool:
    return bool(_SALUTI.match((text or "").strip()))


def breve(text: str) -> bool:
    text = (text or "").strip()
    return (saluto(text) or (len(text.split()) <= 5 and not _APPROFONDISCI.search(text)))


def taglia(text: str, limite: int = LIMITE_RISPOSTA_VECCHIA) -> str:
    text = " ".join(str(text).split())
    if len(text) <= limite:
        return text
    cut = text[:limite]
    stop = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    return (cut[:stop + 1] if stop > limite // 2 else cut.rstrip()) + " […]"


def adatta_storia(history, latest: str):
    """history: lista di coppie ((ruolo, testo), (ruolo, testo)). Ritorna la storia ridotta."""
    if not history or not breve(latest):
        return list(history or [])
    if saluto(latest):
        (ru, tu), (ra, ta) = history[-1]
        return [((ru, taglia(tu, 160)), (ra, taglia(ta, 120)))]
    # Domanda breve: al massimo due scambi; il più vecchio ha la risposta tagliata, l'ultimo
    # resta intero (può servire per capire a cosa si riferisce la domanda).
    out = []
    for n, pair in enumerate(list(history)[-2:]):
        (ru, tu), (ra, ta) = pair
        last = n == len(list(history)[-2:]) - 1
        out.append(pair if last else ((ru, taglia(tu, 160)), (ra, taglia(ta))))
    return out
