"""Narrow, explicit preference commands; conversation is never mined for prefs."""
from __future__ import annotations
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class PreferenceIntent:
    kind: str
    key: str = ""
    value: str = ""


_PREFIX = re.compile(r"^(?:(?:ehi|hey|ok)\s+)?lumi[\s,.:;-]*",re.I)
_SET = re.compile(r"^(?:ricorda(?:ti)?\s+(?:la\s+preferenza\s+)?(?:che\s+)?|"
                  r"salva\s+(?:la\s+)?preferenza\s+)(.+)$",re.I)
_LIST = re.compile(r"^(?:quali\s+sono\s+le\s+mie\s+preferenze|"
                   r"(?:mostra|elenca)\s+(?:le\s+)?(?:mie\s+)?preferenze)$",re.I)
_FORGET = re.compile(r"^(?:dimentica|rimuovi|cancella)\s+"
                     r"(?:la\s+)?preferenza\s+(risposte|lingua|interazione)$",re.I)
_VALUES={
    "preferisco risposte brevi": ("response_length","brief"),
    "preferisco risposte concise": ("response_length","brief"),
    "preferisco risposte equilibrate": ("response_length","balanced"),
    "preferisco risposte dettagliate": ("response_length","detailed"),
    "preferisco la voce": ("interaction","voice"),
    "preferisco il testo": ("interaction","text"),
    "preferisco sia voce sia testo": ("interaction","both"),
    "preferisco risposte in italiano": ("language","it"),
    "preferisco risposte in inglese": ("language","en"),
    "preferisco risposte in spagnolo": ("language","es"),
}
_FORGET_KEYS={"risposte":"response_length","lingua":"language",
              "interazione":"interaction"}


def parse_preference_intent(text: str) -> PreferenceIntent | None:
    if not isinstance(text,str) or len(text)>180:
        return None
    text=_PREFIX.sub("",text.strip(" ,.!?;:")).strip(" ,.!?;:")
    if _LIST.fullmatch(text):
        return PreferenceIntent("list")
    match=_FORGET.fullmatch(text)
    if match:
        return PreferenceIntent("remove",_FORGET_KEYS[match.group(1).casefold()])
    match=_SET.fullmatch(text)
    if match:
        result=_VALUES.get(" ".join(match.group(1).casefold().split()))
        return (PreferenceIntent("set",*result) if result else
                PreferenceIntent("unsupported"))
    return None
