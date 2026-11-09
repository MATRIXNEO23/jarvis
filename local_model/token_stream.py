"""Streaming of the local model's text while it is being generated.

The caller sets a callback for the current thread; the native bridge polls the
upstream engine (get_pending_output) and passes the clean text so far. Only
ordinary chat uses it: action/JSON replies are never streamed to the user.
"""
from __future__ import annotations

from contextlib import contextmanager
import threading

_local = threading.local()


@contextmanager
def streaming(callback):
    previous = getattr(_local, "callback", None)
    _local.callback = callback
    try:
        yield
    finally:
        _local.callback = previous


def current():
    return getattr(_local, "callback", None)


def visible_text(raw: str, stop: str | None) -> str:
    """Text safe to show: cut at the stop sequence and hold back a partial one."""
    if not isinstance(raw, str):
        return ""
    if stop:
        index = raw.find(stop)
        if index >= 0:
            return raw[:index]
        for n in range(min(len(stop) - 1, len(raw)), 0, -1):
            if raw.endswith(stop[:n]):
                return raw[:-n]
    return raw
