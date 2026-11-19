"""Tavily: ricerca web pensata per gli assistenti (risposta breve + fonti)."""
from online.servizi_ricerca.base import Ricerca, Risultato

URL = "https://api.tavily.com/search"


def cerca(key, query, approfondisci, timeout, post) -> Risultato:
    data = post(URL, key, {"query": query,
                           "search_depth": "advanced" if approfondisci else "basic",
                           "max_results": 8 if approfondisci else 5,
                           "include_answer": True}, timeout)
    results = [r for r in (data.get("results") or []) if isinstance(r, dict) and r.get("url")]
    answer = str(data.get("answer") or "").strip()
    if not answer:
        answer = " ".join(str(r.get("content") or "").strip()[:240] for r in results[:3]).strip()
    return Risultato(answer, tuple((str(r.get("title") or r["url"])[:120], str(r["url"]))
                                   for r in results),
                     tuple(" ".join(str(r.get("content") or "").split())[:160] for r in results))


SERVIZIO = Ricerca(
    id="tavily", nome="Tavily", ordine=1, limite_mese=1000, adattatore=cerca,
    chiavi="https://app.tavily.com",
    limite="Piano gratuito con crediti mensili.",
    passi=("Apri app.tavily.com e accedi.", "Copia la chiave API dalla pagina principale (tvly-…).",
           "Incollala in Lumi con «Chiave…»."))
