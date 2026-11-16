"""Groq (con la Q): modelli aperti velocissimi, API compatibile OpenAI."""
from servizi_online.base import Servizio

SERVIZIO = Servizio(
    preferiti=("openai/gpt-oss-120b", "qwen/qwen3.6-27b", "openai/gpt-oss-20b"),
    uso="Velocissimo: risposte rapide e lavori a più passi sul PC.",
    id="groq", nome="Groq", ordine=2, gratis=True,
    base_url="https://api.groq.com/openai/v1",
    modello="openai/gpt-oss-120b",
    chiavi="https://console.groq.com/keys",
    # llama-3.3-70b-versatile ritirato il 16/08/2026 (console.groq.com/docs/deprecations):
    # sostituto consigliato openai/gpt-oss-120b. Groq manda le richieste rimaste in ogni
    # risposta: Lumi usa quelle per la barra della quota.
    limite="Gratis con limiti al minuto e al giorno (Groq li comunica a ogni risposta).",
    passi=("Apri console.groq.com/keys e accedi (anche con Google o GitHub).",
           "Premi «Create API Key» e dai un nome qualsiasi, per esempio Lumi.",
           "Copia la chiave (inizia con gsk_…) e incollala in Lumi: dopo non si rivede."))
