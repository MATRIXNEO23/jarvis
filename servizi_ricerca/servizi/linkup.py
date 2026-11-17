"""Linkup: ricerca web con risposta e fonti. API verificata sulla documentazione ufficiale (17/11):
POST https://api.linkup.so/v1/search, Authorization: Bearer, corpo {q, depth, outputType,
maxResults}, risposta sourcedAnswer {answer, sources:[{name, url, snippet}]}."""
from servizi_ricerca.base import Ricerca, Risultato

URL = "https://api.linkup.so/v1/search"


def cerca(key, query, approfondisci, timeout, post) -> Risultato:
    data = post(URL, key, {"q": query, "depth": "standard" if approfondisci else "fast",
                           "outputType": "sourcedAnswer",
                           "maxResults": 8 if approfondisci else 5}, timeout)
    sources = [r for r in (data.get("sources") or []) if isinstance(r, dict) and r.get("url")]
    answer = str(data.get("answer") or "").strip()
    previews = tuple(" ".join(str(r.get("snippet") or "").split())[:160] for r in sources)
    if not answer:
        answer = " ".join(p for p in previews[:3] if p).strip()
    return Risultato(answer, tuple((str(r.get("name") or r["url"])[:120], str(r["url"]))
                                   for r in sources), previews)


SERVIZIO = Ricerca(
    id="linkup", nome="Linkup", ordine=4, chiavi="https://app.linkup.so", adattatore=cerca,
    limite="Crediti gratuiti iniziali.",
    passi=("Apri app.linkup.so e accedi.", "Copia la chiave API dalla pagina principale.",
           "Incollala in Lumi con «Chiave…»."))
