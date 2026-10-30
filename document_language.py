"""Understand clear Italian voice choices for closing one Jarvis-owned document.

Decisions are made locally rather than by an LLM. A clear, explicit request to
discard is itself consent; unrelated speech and quoted/hypothetical examples
can never silently discard user text.
"""
from __future__ import annotations

import re
import unicodedata

_CLOSE = re.compile(r"\b(?:chiud\w*|esci|uscire|usc\w*|termina|terminare)\b")
_SAVE = re.compile(r"\b(?:salv\w*|registr\w*)\b")
_NO_SAVE = re.compile(
    r"\b(?:senza(?:\s+\w+){0,2}\s+salv\w*|"
    r"non(?:\s+\w+){0,4}\s+salv\w*|"
    r"evita\s+di\s+salv\w*)\b")
_THROW_AWAY = re.compile(
    r"\b(?:scart\w*|butt\w*\s+via|cancell\w*\s+le\s+modifiche|"
    r"perd\w*\s+le\s+modifiche)\b")
_CANCEL = re.compile(
    r"\b(?:annull\w*|lascia\w*\s+apert\w*|tieni\s+apert\w*|"
    r"non\s+chiud\w*|non\s+uscire|fermati|aspetta)\b")
_META_START = re.compile(
    r"^(?:se\b|quando\b|come\b|cosa\b|perch[eé]\b|"
    r"mi\s+spieghi\b|che\s+succede\b|"
    r"che\s+significa\b|ti\s+chiedo\s+se\b)")
_WAKE = re.compile(r"^(?:(?:ehi|hey|ok)\s+)?jarvis\s+")


def clean_speech(utterance: str) -> str:
    if not isinstance(utterance, str) or not utterance.strip() or len(utterance) > 220:
        return ""
    phrase = unicodedata.normalize("NFKC", utterance).casefold()
    phrase = re.sub(r"[^\w\sàèéìòù]", " ", phrase)
    phrase = " ".join(phrase.split())
    return _WAKE.sub("", phrase)


def classify_document_choice(utterance: str, *, pending: bool) -> str | None:
    """Return save, discard, cancel or None.

    pending=True means Jarvis has just offered save/discard/cancel for its
    own identified Notepad window; a short reply like 'non salvare' is enough.
    pending=False requires an explicit close/discard request, never a bare
    'salva' or 'non salvare' from ordinary conversation.
    """
    phrase = clean_speech(utterance)
    if (not phrase or _META_START.search(phrase) or
            not re.match(
                r"^(?:chiud|esc|usc|salv|non|senza|scart|butt|annull|"
                r"lasci|tieni|puoi|potresti|per favore|per cortesia|"
                r"si |sì |ok |va bene|allora|guarda|vai|invece|"
                r"voglio|mi raccomando|no |aspetta|fermati)", phrase)):
        return None
    if False:
        return None
    if _CANCEL.search(phrase):
        return "cancel" if pending else None

    close = bool(_CLOSE.search(phrase))
    no_save = bool(_NO_SAVE.search(phrase))
    throw = bool(_THROW_AWAY.search(phrase))
    save = bool(_SAVE.search(phrase))

    # Ambiguity between saving and throwing away must not discard data.
    if (throw or no_save) and re.search(
            r"\b(?:prima\s+salv\w*|salv\w*\s+(?:prima|comunque))\b", phrase):
        return None

    if (no_save or throw) and (close or pending):
        return "discard"
    if save and not (no_save or throw) and (close or pending):
        return "save"
    if pending and phrase in ("no", "lascia stare", "niente", "non fare nulla"):
        return "cancel"
    return None
