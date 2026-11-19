"""Anthropic Claude tramite API (compatibilità OpenAI): a consumo."""
from online.servizi_online.base import Servizio

SERVIZIO = Servizio(
    uso="Claude con chiave: testi e codice molto curati, lavori a più passi. A pagamento.",
    id="anthropic", nome="Anthropic Claude (API)", ordine=8, gratis=False,
    base_url="https://api.anthropic.com/v1", modello="claude-haiku-4-5",
    chiavi="https://console.anthropic.com/settings/keys",
    limite="A pagamento, a parte dall'abbonamento a Claude.",
    passi=("Apri console.anthropic.com e accedi.", "Aggiungi del credito in Billing.",
           "Vai in Settings → API Keys → «Create Key», copiala e incollala in Lumi."))
