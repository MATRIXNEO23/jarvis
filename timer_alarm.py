"""Local, selectable alarm sounds. Uses only Windows winsound and stdlib PCM.

Nothing plays until the owner presses Test or a countdown expires.
"""
from __future__ import annotations
import io
import math
import os
import struct
import threading
import wave

ALARM_PATTERNS = {
    "Bip classico": ((880, .17, .20), (880, .17, .20), (880, .22, .45)),
    "Allarme rapido": ((1020,.11,.10),(1020,.11,.10),
                       (1020,.11,.10),(1020,.11,.27)),
    "Allarme lungo": ((650,.54,.12),(740,.54,.35)),
    "Triplo impulso": ((540,.16,.08),(740,.16,.08),(960,.23,.42)),
}
DEFAULT_ALARM="Bip classico"


def alarm_wave(frequency: int, seconds: float, volume: int) -> bytes:
    """Bounded PCM wave with short fade-in/out to prevent clicks."""
    if (type(frequency) is not int or not 100<=frequency<=2500
            or not .01<=seconds<=1.0
            or type(volume) is not int or not 0<=volume<=100):
        raise ValueError("Parametri suoneria non validi.")
    rate=22050
    count=max(1,int(seconds*rate))
    amp=21000*volume/100
    samples=bytearray()
    for i in range(count):
        fade=min(1.0,i/180,(count-1-i)/180)
        value=round(amp*max(0.0,fade)*math.sin(2*math.pi*frequency*i/rate))
        samples.extend(struct.pack("<h",value))
    output=io.BytesIO()
    with wave.open(output,"wb") as sound:
        sound.setnchannels(1)
        sound.setsampwidth(2)
        sound.setframerate(rate)
        sound.writeframes(samples)
    return output.getvalue()


class AlarmPlayer:
    def __init__(self):
        self._cancel=threading.Event()
        self._thread=None

    def stop(self):
        self._cancel.set()

    def play(self,name: str = DEFAULT_ALARM,volume: int = 65,
             *,repeat: bool = False):
        """Asynchronous; no Tk call, no external shell or network."""
        if name not in ALARM_PATTERNS or type(volume) is not int or not 0<=volume<=100:
            raise ValueError("Suono o volume non valido")
        self.stop()
        cancel=threading.Event()
        self._cancel=cancel
        if volume==0:
            return
        def worker():
            if os.name!="nt":
                return
            try:
                import winsound
            except ImportError:
                return
            while not cancel.is_set():
                for hz,duration,pause in ALARM_PATTERNS[name]:
                    if cancel.is_set():
                        return
                    try:
                        winsound.PlaySound(
                            alarm_wave(hz,duration,volume),winsound.SND_MEMORY)
                    except (RuntimeError,OSError,ValueError):
                        return
                    if cancel.wait(pause):
                        return
                if not repeat:
                    break
                if cancel.wait(.55):
                    return
        self._thread=threading.Thread(
            target=worker,name="jarvis-timer-alarm",daemon=True)
        self._thread.start()
