"""Link cliccabili nella chat (054): «[titolo](https://…)» e indirizzi nudi.

La chat è un widget Text senza markdown: qui ogni link diventa un tag con sottolineatura,
cursore a mano al passaggio e clic che apre il browser. Usato da write_line (jarvis.py).
"""
from __future__ import annotations

import re

COLORE = "#46ccfa"
_LINK = re.compile(r"\[([^\]\n]{1,200})\]\((https?://[^\s)]+)\)|(?<![(\w/])(https?://[^\s)<>\]]+)")


def segmenti(body: str) -> list[tuple[str, str | None]]:
    """[(testo, url o None)] nell'ordine: il testo di un link markdown è il titolo."""
    out, pos = [], 0
    for match in _LINK.finditer(body):
        if match.start() > pos:
            out.append((body[pos:match.start()], None))
        if match.group(2):
            out.append((match.group(1), match.group(2)))
        else:
            url = match.group(3).rstrip(".,;:!?")
            out.append((url, url))
            if len(match.group(3)) > len(url):
                out.append((match.group(3)[len(url):], None))
        pos = match.end()
    if pos < len(body):
        out.append((body[pos:], None))
    return out


def ha_link(body: str) -> bool:
    return _LINK.search(body) is not None


def inserisci(text, body: str, role: str, open_url, counter: list | None = None) -> dict:
    """Inserisce `body` in fondo al Text con i link cliccabili; ritorna {tag: url}."""
    counter = counter if counter is not None else _CONTATORE
    found = {}
    for piece, url in segmenti(body):
        if url is None:
            text.insert("end", piece, role)
            continue
        counter[0] += 1
        tag = "link_%d" % counter[0]
        text.tag_configure(tag, foreground=COLORE, underline=True)
        text.tag_bind(tag, "<Enter>", lambda _e: text.configure(cursor="hand2"))
        text.tag_bind(tag, "<Leave>", lambda _e: text.configure(cursor=""))
        text.tag_bind(tag, "<Button-1>", lambda _e, u=url: open_url(u))
        text.insert("end", piece, (role, tag))
        found[tag] = url
    return found


_CONTATORE = [0]
