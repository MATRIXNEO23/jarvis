"""Interruttore della base comune: mouse, tastiera e chiusura finestre funzionano
solo se è attivo almeno un add-on che la usa (Controllo PC oggi, Controllo browser
in futuro). Con tutti spenti Lumi non tocca né mouse né tastiera."""
from __future__ import annotations

_USERS: dict = {}


def register(name: str, is_enabled) -> None:
    _USERS[name] = is_enabled


def unregister(name: str) -> None:
    _USERS.pop(name, None)


def active() -> bool:
    for check in list(_USERS.values()):
        try:
            if check():
                return True
        except Exception:
            continue
    return False


def require() -> None:
    if not active():
        raise PermissionError("Controllo di mouse e tastiera spento: nessun add-on di controllo attivo.")
