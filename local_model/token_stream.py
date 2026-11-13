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


_REPLY_KEY = None


def visible_reply(raw: str) -> str:
    """Partial text to show for a reply that may be the action JSON schema.

    Plain prose is shown as is. ``{"kind":"chat"|"clarify","reply":"..."}`` shows
    the reply string decoded so far. Anything else (a capability proposal,
    incomplete keys) shows nothing: actions are never displayed while generated.
    """
    import re
    global _REPLY_KEY
    if _REPLY_KEY is None:
        _REPLY_KEY = re.compile(r'"reply"\s*:\s*"')
    text = (raw or "").lstrip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].lstrip() if "\n" in text else ""
    if not text:
        return ""
    if not text.startswith("{"):
        return "" if text.startswith("`") else raw.strip()
    if '"capability"' in text or '"action_id"' in text:
        return ""
    match = _REPLY_KEY.search(text)
    if not match:
        return ""
    out = []
    i = match.end()
    escapes = {"n": "\n", "t": " ", '"': '"', "\\": "\\", "/": "/", "r": ""}
    while i < len(text):
        ch = text[i]
        if ch == '"':
            break
        if ch == "\\":
            if i + 1 >= len(text):
                break
            nxt = text[i + 1]
            if nxt == "u":
                if i + 6 > len(text):
                    break
                try:
                    out.append(chr(int(text[i + 2:i + 6], 16)))
                except ValueError:
                    pass
                i += 6
                continue
            out.append(escapes.get(nxt, nxt))
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)
