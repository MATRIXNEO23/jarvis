"""Groq (con la Q): modelli aperti velocissimi, API compatibile OpenAI."""
from servizi_online.base import Servizio

SERVIZIO = Servizio(
    uso="Velocissimo: risposte rapide e lavori a più passi sul PC.",
    id="groq", nome="Groq", ordine=2, gratis=True,
    base_url="https://api.groq.com/openai/v1",
    modello="llama-3.3-70b-versatile",
    chiavi="https://console.groq.com/keys",
    # Piano gratuito per llama-3.3-70b-versatile: 30 al minuto, 1.000 al giorno
    # (documentazione Groq, verificato sul web il 15/11/2026). Groq manda anche le
    # richieste rimaste in ogni risposta: Lumi usa quelle quando ci sono.
    limite="Gratis: 1.000 richieste al giorno e 30 al minuto con questo modello.",
    richieste_giorno=1000,
    passi=("Apri console.groq.com/keys e accedi (anche con Google o GitHub).",
           "Premi «Create API Key» e dai un nome qualsiasi, per esempio Lumi.",
           "Copia la chiave (inizia con gsk_…) e incollala in Lumi: dopo non si rivede."))
