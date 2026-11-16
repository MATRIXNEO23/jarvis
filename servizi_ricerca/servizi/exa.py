"""Exa: ricerca web semantica. Voce predisposta: chiave e link, ricerca non ancora collegata."""
from servizi_ricerca.base import Ricerca

SERVIZIO = Ricerca(
    id="exa", nome="Exa", ordine=2, chiavi="https://dashboard.exa.ai",
    limite="Crediti gratuiti iniziali.",
    passi=("Apri dashboard.exa.ai e accedi.", "Vai in API Keys e crea una chiave.",
           "Incollala in Lumi con «Chiave…»."))
