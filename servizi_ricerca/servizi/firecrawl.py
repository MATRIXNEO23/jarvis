"""Firecrawl: ricerca e lettura di pagine. Voce predisposta: chiave e link, ricerca non ancora collegata."""
from servizi_ricerca.base import Ricerca

SERVIZIO = Ricerca(
    id="firecrawl", nome="Firecrawl", ordine=3, chiavi="https://www.firecrawl.dev/app/api-keys",
    limite="Crediti gratuiti iniziali.",
    passi=("Apri firecrawl.dev/app/api-keys e accedi.", "Copia la chiave (fc-…).",
           "Incollala in Lumi con «Chiave…»."))
