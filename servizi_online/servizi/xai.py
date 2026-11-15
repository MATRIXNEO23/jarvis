"""xAI Grok (con la K): a consumo."""
from servizi_online.base import Servizio

SERVIZIO = Servizio(
    id="xai", nome="xAI Grok", ordine=6, gratis=False,
    base_url="https://api.x.ai/v1", modello="grok-3-mini",
    chiavi="https://console.x.ai/",
    limite="A pagamento: si paga quello che si usa.",
    passi=("Apri console.x.ai e accedi.", "Aggiungi un metodo di pagamento o dei crediti.",
           "Vai in API Keys → crea una chiave, copiala e incollala in Lumi."))
