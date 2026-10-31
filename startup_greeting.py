"""Local startup greeting for JARVIS, independent of GPT connectivity."""
from __future__ import annotations

from datetime import datetime


def greeting_for_hour(hour: int) -> str:
    """Use Windows local time; no clock API, GPS, network or saved profile."""
    if type(hour) is not int or not 0 <= hour <= 23:
        raise ValueError("Ora locale non valida.")
    if hour < 5:
        opening = "Buonanotte"
    elif hour < 12:
        opening = "Buongiorno"
    elif hour < 18:
        opening = "Buon pomeriggio"
    else:
        opening = "Buonasera"
    return f"{opening}, signore. Come posso esserle utile?"


def startup_greeting() -> str:
    return greeting_for_hour(datetime.now().hour)
