"""Exa: ricerca web semantica. API verificata sulla documentazione ufficiale (17/11):
POST https://api.exa.ai/search, intestazione Authorization: Bearer (o x-api-key),
corpo {query, numResults, contents:{highlights:true}}, risposta results[].title/url/highlights."""
from servizi_ricerca.base import Ricerca, Risultato

URL = "https://api.exa.ai/search"


def cerca(key, query, approfondisci, timeout, post) -> Risultato:
    data = post(URL, key, {"query": query, "numResults": 8 if approfondisci else 5,
                           "contents": {"highlights": True}}, timeout)
    results = [r for r in (data.get("results") or []) if isinstance(r, dict) and r.get("url")]

    def estratto(r):
        parts = r.get("highlights") or []
        return " ".join(" ".join(str(p) for p in parts if p).split()) or " ".join(
            str(r.get("text") or r.get("summary") or "").split())
    previews = tuple(estratto(r)[:160] for r in results)
    summary = " ".join(p[:240] for p in previews[:3] if p).strip()
    return Risultato(summary, tuple((str(r.get("title") or r["url"])[:120], str(r["url"]))
                                    for r in results), previews)


SERVIZIO = Ricerca(
    id="exa", nome="Exa", ordine=2, chiavi="https://dashboard.exa.ai", adattatore=cerca,
    limite="Crediti gratuiti iniziali.",
    passi=("Apri dashboard.exa.ai e accedi.", "Vai in API Keys e crea una chiave.",
           "Incollala in Lumi con «Chiave…»."))
