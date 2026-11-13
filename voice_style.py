"""Velocità, tonalità e volume della voce, comuni a tutte le voci di Lumi.

Valori in percentuale, impostati da Impostazioni > Voce:
- rate   -50..+50  (0 = normale; +50 = 1,5 volte più veloce)
- pitch  -50..+50  (0 = normale; circa +-4 semitoni agli estremi)
- volume  10..100  (100 = pieno)
Usati da Piper (length_scale + ricampionamento), Edge (rate/pitch/volume del
servizio), voci Windows (Rate/Volume SAPI e SSML prosody) e note Telegram.
"""
from __future__ import annotations

import threading

LIMITS = {"rate": (-50, 50), "pitch": (-50, 50), "volume": (10, 100)}
DEFAULT = {"rate": 0, "pitch": 0, "volume": 100}
_lock = threading.Lock()
_current = dict(DEFAULT)


def clamp(name: str, value) -> int:
    low, high = LIMITS[name]
    try:
        number = int(round(float(value)))
    except (TypeError, ValueError):
        number = DEFAULT[name]
    return max(low, min(high, number))


def update(**values) -> dict:
    with _lock:
        for name, value in values.items():
            if name in LIMITS:
                _current[name] = clamp(name, value)
        return dict(_current)


def current() -> dict:
    with _lock:
        return dict(_current)


def speed_factor(style=None) -> float:
    return 1 + (style or current())["rate"] / 100.0


def pitch_factor(style=None) -> float:
    """Fattore di frequenza: +50 -> ~1,26 (circa +4 semitoni)."""
    return 2 ** (((style or current())["pitch"] / 50.0) * 4 / 12)


def gain(style=None) -> float:
    return (style or current())["volume"] / 100.0


def edge_params(style=None) -> dict:
    s = style or current()
    return {"rate": f"{s['rate']:+d}%",
            "volume": f"{s['volume'] - 100:+d}%",
            "pitch": f"{int(round(s['pitch'] * 0.5)):+d}Hz"}


def sapi_params(style=None) -> dict:
    s = style or current()
    return {"rate": max(-10, min(10, int(round(s["rate"] / 5)))),
            "volume": s["volume"],
            "pitch": s["pitch"]}
