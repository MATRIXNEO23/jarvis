"""Firecrawl: ricerca web. API verificata sulla documentazione ufficiale (17/11):
POST https://api.firecrawl.dev/v2/search, Authorization: Bearer, corpo {query, limit},
risposta {success, data:{web:[{title, url, description}]}}."""
from online.servizi_ricerca.base import Ricerca, Risultato

URL = "https://api.firecrawl.dev/v2/search"


def cerca(key, query, approfondisci, timeout, post) -> Risultato:
    data = post(URL, key, {"query": query[:500], "limit": 8 if approfondisci else 5}, timeout)
    inner = data.get("data")
    items = inner.get("web") if isinstance(inner, dict) else inner      # v2: data.web; v1: data[]
    results = [r for r in (items or []) if isinstance(r, dict) and r.get("url")]
    previews = tuple(" ".join(str(r.get("description") or "").split())[:160] for r in results)
    summary = " ".join(p for p in previews[:3] if p).strip()
    return Risultato(summary, tuple((str(r.get("title") or r["url"])[:120], str(r["url"]))
                                    for r in results), previews)


SERVIZIO = Ricerca(
    id="firecrawl", nome="Firecrawl", ordine=3, chiavi="https://www.firecrawl.dev/app/api-keys",
    adattatore=cerca, limite="Crediti gratuiti iniziali.",
    passi=("Apri firecrawl.dev/app/api-keys e accedi.", "Copia la chiave (fc-…).",
           "Incollala in Lumi con «Chiave…»."))
