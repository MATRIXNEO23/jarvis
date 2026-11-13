"""Carattere di Lumi e lunghezza delle risposte, con frasi brevi e semplici.

Ordine nel prompt (per il fast forwarding di KoboldCpp, che riusa la parte
iniziale uguale alla richiesta precedente):
1. ``persona_block``: SEMPRE uguale finché non cambi le impostazioni ->
   carattere, tocco in più, testo libero, note sull'utente. Va in cima.
2. istruzioni della modalità (chat o catalogo azioni), poi la cronologia.
3. ``length_rule``: cambia con la domanda -> va in fondo, accanto alla domanda.

La scelta tra risposta breve e spiegazione la fa Lumi, non il modello: al
modello piccolo arriva una sola regola semplice, mai una condizione.
"""
from __future__ import annotations

import re

NONE_LABEL = "Nessuno"
# chiave -> come appare nella frase «Sei ...» (femminile, Lumi)
CHARACTERS = {
    "dolce": "dolce",
    "amorevole": "amorevole",
    "affettuosa": "affettuosa",
    "monella": "un po' monella",
    "giocosa": "giocosa",
    "ironica": "ironica",
    "sarcastica": "sarcastica",
    "allegra": "allegra",
    "energica": "energica",
    "calma": "calma",
    "paziente": "paziente",
    "empatica": "empatica",
    "curiosa": "curiosa",
    "timida": "timida",
    "sicura di sé": "sicura di sé",
    "seria": "seria",
    "schietta": "schietta",
    "elegante": "elegante",
    "professionale": "professionale",
}
LENGTHS = {
    "": NONE_LABEL,
    "brief": "Breve, scegli tu",
    "1": "1 frase",
    "2": "2 frasi",
    "3": "3 frasi",
    "4": "4 frasi",
    "5": "5 frasi",
}
NOTES_LIMIT = 300
EXPLAIN_MIN, EXPLAIN_MAX = 3, 15

# Parole spia scelte dall'utente: allungano la risposta.
_SPY = re.compile(
    r"\b(spiegami|spiegamelo|spiegamela|come\s+funzion\w*|approfondisci|approfondiamo"
    r"|in\s+dettaglio|nel\s+dettaglio|descrivimi|descrivimelo|consigliami)\b",
    re.IGNORECASE)


def wants_explanation(question: str) -> bool:
    return isinstance(question, str) and _SPY.search(question) is not None


def _clean(text: str) -> str:
    return " ".join(str(text or "").split())


def persona_block(config) -> str:
    """Parte fissa in cima al prompt; stringa vuota se non è impostato nulla."""
    parts = []
    traits = [CHARACTERS[k] for k in (getattr(config, "character_main", ""),
                                      getattr(config, "character_extra", ""))
              if k in CHARACTERS]
    if len(traits) == 2 and traits[0] == traits[1]:
        traits = traits[:1]
    if traits:
        parts.append("Carattere: sei " + " e ".join(traits) + ".")
    free = _clean(getattr(config, "personality", ""))
    if free:
        parts.append("Stile: " + free)
    notes = _clean(getattr(config, "user_notes", ""))
    if notes:
        parts.append("Sull'utente: " + notes)
    return "".join(p + "\n" for p in parts)


def length_rule(config, question: str) -> str:
    """Una sola regola semplice per questa domanda, oppure stringa vuota."""
    if wants_explanation(question):
        n = getattr(config, "explain_sentences", 8)
        return f"Spiega in massimo {n} frasi."
    choice = getattr(config, "reply_length", "")
    if choice == "brief":
        return "Rispondi brevemente."
    if choice == "1":
        return "Rispondi in una frase."
    if choice in ("2", "3", "4", "5"):
        return f"Rispondi in massimo {choice} frasi."
    return ""
