"""Small deterministic conversation focus hints for LUMI.

These are *data* for conversation, never a command or authorization to act.
No database, filesystem, model, network, or background processing.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata

_SHORT = re.compile(
    r"^(?:s[iì]|no|certo|esatto|giusto|va bene|ok|okay|"
    r"quello|quella|questo|questa|lui|lei|il primo|la prima|"
    r"il secondo|la seconda|entrambi|tutti e due|nessuno|"
    r"non lo so|non ricordo|forse|quello l[iì]|questo qui)$",re.I)
_PROJECT_DEICTIC = re.compile(
    r"\b(?:questo|questa|quel|quello|quella|attuale|corrente|in corso|"
    r"nostro|nostra)\s+progett[oa]\b|"
    r"\bprogett[oa]\s+(?:attuale|corrente|in corso|aperto|attivo|"
    r"di cui stiamo parlando)\b",re.I)
_PROJECT_QUERY = re.compile(
    r"^(?:a che punto|come (?:va|procede)|cosa (?:sai|abbiamo fatto)|"
    r"che cosa (?:sai|abbiamo fatto)|quali (?:passi|file)|"
    r"dove (?:sono|si trovano)|parlami)\b",re.I)
_BARE_REPLY = re.compile(r"^[\wÀ-ÿ'-]+(?:\s+[\wÀ-ÿ'-]+){0,4}$",re.UNICODE)
_ACTION_PREFIX = re.compile(
    r"^(?:apri|crea|salva|elimina|cancella|rinomina|chiudi|invia|"
    r"cerca|mostra|scrivi|avvia|esegui|analizza|esamina)\b",re.I)
_INVALID_NAME = frozenset({"si","sì","no","ok","okay","va bene",
    "certo","esatto","giusto","forse","non lo so","quello","quella",
    "questo","questa","il progetto","questo progetto","la cartella",
    "niente","annulla","non ricordo","il primo","la seconda"})


def normalized_utterance(value: str) -> str:
    if not isinstance(value,str):
        return ""
    text=unicodedata.normalize("NFKC",value).strip(" ,.!?;:")
    return re.sub(r"^(?:(?:ehi|hey|ok)\s+)?jarvis[\s,.:;-]+",
                  "",text,flags=re.I).strip(" ,.!?;:")


def is_short_followup(value: str) -> bool:
    text=normalized_utterance(value)
    return bool(text and len(text)<=65 and not _ACTION_PREFIX.match(text)
                and (_SHORT.fullmatch(text) or _BARE_REPLY.fullmatch(text)))


def is_ambiguous_short_reply(value: str) -> bool:
    """An isolated yes/no/pronoun needs a real preceding question."""
    return bool(_SHORT.fullmatch(normalized_utterance(value)))


def is_unusable_project_name(value: str) -> bool:
    return normalized_utterance(value).casefold() in _INVALID_NAME


def mentions_current_project(value: str) -> bool:
    return bool(_PROJECT_DEICTIC.search(normalized_utterance(value)))


def needs_project_clarification(value: str, *, project_selected: bool) -> bool:
    """Only chat questions about *this* project require a chosen project."""
    text=normalized_utterance(value)
    return not project_selected and mentions_current_project(text)


def single_question(text: str) -> str:
    """Keep one meaningful concrete question, not a questionnaire."""
    if not isinstance(text,str):
        return "Quale dettaglio intendi?"
    clean=" ".join(text.split()).strip()
    if not clean:
        return "Quale dettaglio intendi?"
    if "?" in clean:
        first=clean.split("?",1)[0].strip(" .!;:")
        if first and len(first)<=175:
            return first+"?"
    if len(clean)<=150:
        return clean.rstrip(".! ")+"?"
    return "Quale dettaglio intendi?"


def focus_hint(utterance: str, *, active_project_name: str = "",
               last_question: str = "") -> dict:
    """Anchor deictic references and direct short replies; never invent a task."""
    result={}
    if active_project_name:
        result["project"]={
            "name":active_project_name[:65],
            "status":"currently_selected",
        }
    if last_question and is_short_followup(utterance):
        result["pending_question"]=single_question(last_question)[:180]
        result["follow_up"]=normalized_utterance(utterance)[:65]
    return result


@dataclass
class PendingProjectReference:
    """One scoped follow-up to 'which project?' that never assumes a name."""

    question: str = ""

    def start_if_needed(self, text: str, *, selected: bool) -> bool:
        if needs_project_clarification(text,project_selected=selected):
            self.question=normalized_utterance(text)[:180]
            return True
        return False

    def reset(self) -> None:
        self.question=""

    def parse_answer(self, text: str) -> str | None:
        """Return a deliberate project name only; keep pending on vague answer."""
        if not self.question:
            return None
        answer=normalized_utterance(text)
        if not answer or is_unusable_project_name(answer):
            return None
        if len(answer)>65 or "/" in answer or "\\" in answer:
            return None
        if _ACTION_PREFIX.match(answer):
            return None
        if not _BARE_REPLY.fullmatch(answer):
            return None
        return answer
