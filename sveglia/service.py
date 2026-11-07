"""Local one-shot alarm using the existing timer audio."""
from datetime import datetime, timedelta
import re
import threading

from jarvis_timer import play_alarm


def parse_command(text):
    value = " ".join(text.casefold().strip(" ,!?").split())
    if value in ("che ore sono", "che ora è", "che ora e", "dimmi l'ora", "dimmi l’ora"):
        return "clock", ""
    if value in ("annulla sveglia", "annulla la sveglia", "ferma sveglia",
                 "ferma la sveglia", "spegni la sveglia"):
        return "stop", ""
    match = re.fullmatch(r"(?:(?:imposta|metti) (?:la |una )?)?sveglia(?: (?:alle|a) (.+))?", value)
    if match:
        return "set", match.group(1) or ""
    return None


def _spoken_numbers():
    units = ("zero", "uno", "due", "tre", "quattro", "cinque", "sei", "sette", "otto", "nove")
    teens = ("dieci", "undici", "dodici", "tredici", "quattordici", "quindici",
             "sedici", "diciassette", "diciotto", "diciannove")
    numbers = {word: str(index) for index, word in enumerate(units + teens)}
    for index, tens in enumerate(("venti", "trenta", "quaranta", "cinquanta"), 2):
        numbers[tens] = str(index * 10)
        for digit in range(1, 10):
            stem = tens[:-1] if digit in (1, 8) else tens
            numbers[stem + units[digit]] = str(index * 10 + digit)
    return numbers


_SPOKEN_NUMBERS = _spoken_numbers()


def next_alarm(value, now):
    morning = bool(re.search(r"\s+(?:di mattina|del mattino)$", value.strip().casefold()))
    value = re.sub(r"\s+(?:di mattina|del mattino)$", "", value.strip(), flags=re.I)
    words = value.strip().casefold().replace("tré", "tre").replace(" e ", " ").split()
    value = " ".join(_SPOKEN_NUMBERS.get(word, word) for word in words)
    match = re.fullmatch(r"([0-9]{1,2})(?:[:. ]([0-9]{1,2}))?", value.strip())
    if not match:
        raise ValueError("Indica un orario come 07:30.")
    hour, minute = int(match.group(1)), int(match.group(2) or 0)
    if hour > 23 or minute > 59 or (morning and hour > 11):
        raise ValueError("Orario non valido. Usa un valore tra 00:00 e 23:59.")
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return target if target > now else target + timedelta(days=1)


class Alarm:
    def __init__(self, root, enabled, preferences, status, notify, on_active):
        self.root = root
        self.enabled = enabled
        self.preferences = preferences
        self.status = status
        self.notify = notify
        self.on_active = on_active
        self.target = None
        self.job = None
        self.audio_stop = threading.Event()
        self.audio_thread = None

    def arm(self, value):
        if not self.enabled():
            return "Attiva Sveglia nelle impostazioni Add-on."
        now = datetime.now()
        try:
            target = next_alarm(value, now)
        except ValueError as exc:
            return str(exc)
        self.stop()
        self.target = target
        self.on_active(True)
        day = "oggi" if target.date() == now.date() else "domani"
        message = f"Sveglia impostata per {day} alle {target:%H:%M}."
        self.status.set(message)
        self.job = self.root.after(500, self.tick)
        return message

    def tick(self):
        self.job = None
        if not self.enabled():
            self.stop()
            return
        if self.target is not None and datetime.now() >= self.target:
            self.target = None
            self.status.set("Sveglia in corso.")
            self.notify("Sveglia in corso. Dì «ferma la sveglia» per spegnerla.")
            prefs = self.preferences()
            self.audio_thread = threading.Thread(
                target=play_alarm,
                args=(prefs.get("timer_sound", "digital"), prefs.get("timer_volume", 80),
                      self.audio_stop),
                kwargs={"repeat": prefs.get("timer_repeat", True),
                        "mode": prefs.get("timer_audio_mode", "auto")},
                daemon=True,
            )
            self.audio_thread.start()
        elif self.audio_thread is not None and not self.audio_thread.is_alive():
            self.stop()
            return
        self.job = self.root.after(500, self.tick)

    def stop(self):
        self.target = None
        if self.job is not None:
            self.root.after_cancel(self.job)
            self.job = None
        self.audio_stop.set()
        self.audio_thread = None
        self.audio_stop = threading.Event()
        self.status.set("Nessuna sveglia impostata.")
        self.on_active(False)
