"""Offline Italian timer intents and monotonic countdown state.

No GPT, microphone, network, UI or new dependency is required.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import time
from collections.abc import Callable

MAX_TIMER_SECONDS = 24 * 3600 - 1

ITALIAN_NUMBERS = {
    "zero":0, "un":1, "uno":1, "una":1, "due":2, "tre":3,
    "quattro":4, "cinque":5, "sei":6, "sette":7, "otto":8,
    "nove":9, "dieci":10, "undici":11, "dodici":12,
    "tredici":13, "quattordici":14, "quindici":15,
    "sedici":16, "diciassette":17, "diciotto":18,
    "diciannove":19, "venti":20, "trenta":30, "quaranta":40,
    "cinquanta":50, "sessanta":60, "settanta":70,
    "ottanta":80, "novanta":90,
}
ONES = ("","uno","due","tre","quattro","cinque","sei","sette","otto","nove")
for tens,stem in ((20,"venti"),(30,"trenta"),(40,"quaranta"),
                  (50,"cinquanta"),(60,"sessanta"),
                  (70,"settanta"),(80,"ottanta"),(90,"novanta")):
    for digit in range(1,10):
        base=stem[:-1] if digit in (1,8) else stem
        ITALIAN_NUMBERS[base+ONES[digit]]=tens+digit
        if digit==3:
            ITALIAN_NUMBERS[base+"tré"]=tens+digit


@dataclass(frozen=True)
class TimerIntent:
    action: str
    seconds: int | None = None


UNITS = {
    "ore":3600, "ora":3600,
    "minuti":60, "minuto":60,
    "secondi":1, "secondo":1,
}
_DURATION = re.compile(
    r"\b(\d{1,5}|[a-zàèéìòù]+)\s*(ore|ora|minuti|minuto|secondi|secondo)\b",
    re.I,
)
_PREFIX = re.compile(
    r"^(?:(?:ehi|hey|ok)\s+)?jarvis[,:\s]+",re.I)


def _number(raw: str) -> int | None:
    if raw.isascii() and raw.isdigit():
        return int(raw)
    return ITALIAN_NUMBERS.get(raw.casefold())


def parse_timer_intent(message: str) -> TimerIntent | None:
    """Exact timer commands only; narrative mentions remain normal chat."""
    if not isinstance(message,str) or len(message)>220:
        return None
    words=" ".join(_PREFIX.sub("",message.casefold().strip(" .!?")).split())
    if not words or re.search(r"\b(?:non|evita|senza)\b",words):
        return None
    if not re.match(r"^(?:timer\b|(?:metti|imposta|avvia|crea|apri|"
                    r"fai partire|ferma|arresta|stop|pausa|metti in pausa|"
                    r"riprendi|continua|azzera|resetta)\b)",words):
        return None
    if "timer" not in words.split() and "conto alla rovescia" not in words:
        return None
    if any(phrase in words for phrase in ("metti in pausa","pausa timer",
                                         "pausa il timer")):
        return TimerIntent("pause")
    if re.search(r"\b(?:ferma|arresta|stop|annulla)\b",words):
        return TimerIntent("stop")
    if re.search(r"\b(?:riprendi|continua)\b",words):
        return TimerIntent("resume")
    if re.search(r"\b(?:resetta|azzera|reset)\b",words):
        return TimerIntent("reset")
    segments=list(_DURATION.finditer(words))
    if not segments:
        # 'timer' alone opens editable popup without inventing a duration.
        return TimerIntent("open")
    total=0
    seen=set()
    for match in segments:
        amount=_number(match.group(1))
        scale=UNITS[match.group(2)]
        if amount is None or scale in seen:
            return None
        total+=amount*scale
        seen.add(scale)
    if not 1<=total<=MAX_TIMER_SECONDS:
        return None
    return TimerIntent("start",total)


def format_remaining(seconds: float) -> str:
    """Ceil to avoid showing 00:00:00 before expiration."""
    seconds=max(0,float(seconds))
    whole=int(seconds)
    if seconds>whole:
        whole+=1
    hours,left=divmod(whole,3600)
    minutes,secs=divmod(left,60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


class Countdown:
    """Single countdown, no scheduling threads or wall-clock drift."""
    def __init__(self,duration: int = 300,clock: Callable[[],float] = time.monotonic):
        self.clock=clock
        self.duration=0
        self._remaining=0.0
        self._deadline=None
        self.state="stopped"
        self._notified=False
        self.set_duration(duration)

    def set_duration(self,seconds: int) -> None:
        if type(seconds) is not int or not 1<=seconds<=MAX_TIMER_SECONDS:
            raise ValueError("Timer fuori intervallo (1 secondo - 23:59:59)")
        self.duration=seconds
        self._remaining=float(seconds)
        self._deadline=None
        self.state="stopped"
        self._notified=False

    def remaining(self) -> float:
        if self.state=="running":
            return max(0.0,self._deadline-self.clock())
        return self._remaining

    def start(self) -> bool:
        if self.state=="running":
            return False
        if self.state=="finished" or self._remaining<=0:
            self._remaining=float(self.duration)
            self._notified=False
        self._deadline=self.clock()+self._remaining
        self.state="running"
        return True

    def pause(self) -> bool:
        if self.state!="running":
            return False
        self._remaining=self.remaining()
        self._deadline=None
        self.state="paused"
        return True

    def stop(self) -> None:
        self._remaining=float(self.duration)
        self._deadline=None
        self.state="stopped"
        self._notified=False

    def reset(self) -> None:
        self.stop()

    def check_finished(self) -> bool:
        if (self.state=="running" and self.remaining()<=0
                and not self._notified):
            self._remaining=0.0
            self._deadline=None
            self._notified=True
            self.state="finished"
            return True
        return False
