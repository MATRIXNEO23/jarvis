"""Deterministic tone guidance for Lumi's *text replies*, not tool actions.

No model calls, stored hidden personality, or semantic classification claims.
The current utterance alone chooses a bounded hint; it never changes intent,
authorization, documents, project state, or the actual user preference.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata


@dataclass(frozen=True)
class DialogueStyle:
    mode: str
    instruction: str


# These guards take precedence over any request for a clever joke: when
# uncertain, factual empathy and precision are more important than sarcasm.
_SERIOUS = re.compile(
    r"\b(?:sto male|fa male|dolore|medic[oa]|ospedale|diagnosi|"
    r"invalidit[aà]|licenziament[oa]|lutto|morte|morto|depress|"
    r"suicid|ansia|panico|crisi|disoccupat|"
    r"truffa|furto|malware|trojan|virus rilevato|"
    r"password|credenziali|dati persi|perso i dati)\b",
    re.I,
)
_PROCEDURE = re.compile(
    r"\b(?:come (?:posso|faccio|si fa|devo|configur[oa]|install[oa]|"
    r"aggiorn[oa]|risolv[oa]|proced[oa])\b|"
    r"spiegami (?:come|i passaggi|la procedura)|"
    r"guidami|guida (?:passo passo|completa)|"
    r"istruzioni|tutorial|procedura|passo passo|"
    r"quali (?:passaggi|operazioni|step) (?:devo|servono)|"
    r"dimmi (?:tutti|i) (?:passaggi|passi)|"
    r"configurare|installare|riparare|disinstallare)\b",
    re.I,
)
_PLAYFUL = re.compile(
    r"\b(?:fammi (?:una battuta|ridere)|"
    r"una battuta|scherz[oa]|ironia|ironico|ironica|"
    r"sarcasm[oa]|sarcastic[oa]|irriveren[tz][aei]|irriveren[tz]a|"
    r"risposta spiritosa)\b",re.I,
)
_TEXT_ARTIFACT = re.compile(
    r"\b(?:scrivi|prepara|genera|componi|redigi)\s+"
    r"(?:un[ao]?\s+)?(?:testo|lettera|email|messaggio|documento|"
    r"relazione|rapporto|codice|script)\b",re.I,
)

_RULES = {
    "sensitive": (
        "STILE: italiano chiaro e rispettoso; niente ironia, sarcasmo o "
        "formule cerimoniose. Rispondi con tatto e precisione."
    ),
    "procedure": (
        "STILE: procedura completa, ordinata e concreta: prerequisiti, passi, "
        "verifiche e avvisi essenziali. Non sacrificare dettagli alla brevità; niente battute."
    ),
    "playful": (
        "STILE: ironia intelligente, sarcasmo leggero e un pizzico di "
        "irriverenza quando pertinenti; mai offensivo, mai deridere l'utente. "
        "Non forzare una battuta in ogni frase."
    ),
    "artifact": (
        "STILE: redigi il contenuto richiesto nel tono adatto allo scopo, "
        "senza inserire ironia o battute non richieste."
    ),
    "conversation": (
        "STILE: conversazione naturale e sintetica, una risposta pertinente "
        "senza preamboli; ironia asciutta e irriverenza solo se nascono dal contesto."
    ),
}


def choose_dialogue_style(utterance: str) -> DialogueStyle:
    """Conservative intent-independent style choice, no action side effects."""
    if not isinstance(utterance,str):
        raise ValueError("Frase non valida per lo stile.")
    phrase=unicodedata.normalize("NFKC",utterance).casefold().strip()
    if len(phrase)>5000:
        raise ValueError("Frase troppo lunga per lo stile.")
    if _SERIOUS.search(phrase):
        mode="sensitive"
    elif _PROCEDURE.search(phrase):
        mode="procedure"
    elif _TEXT_ARTIFACT.search(phrase):
        mode="artifact"
    elif _PLAYFUL.search(phrase):
        mode="playful"
    else:
        mode="conversation"
    return DialogueStyle(mode,_RULES[mode])


def style_instruction(utterance: str) -> str:
    """One short instruction for LLM prompt; original user text is not edited."""
    return choose_dialogue_style(utterance).instruction
