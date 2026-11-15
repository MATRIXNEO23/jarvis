"""OpenAI GPT tramite API: a consumo, separato dall'abbonamento ChatGPT."""
from servizi_online.base import Servizio

SERVIZIO = Servizio(
    id="openai", nome="OpenAI GPT (API)", ordine=7, gratis=False,
    base_url="https://api.openai.com/v1", modello="gpt-4o-mini",
    chiavi="https://platform.openai.com/api-keys",
    limite="A pagamento, a parte: l'abbonamento ChatGPT (anche Plus) non copre le API.",
    passi=("Apri platform.openai.com e accedi.", "Aggiungi del credito in Billing.",
           "Vai in API keys → «Create new secret key», copiala e incollala in Lumi."))
