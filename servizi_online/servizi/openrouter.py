"""OpenRouter: tanti modelli, quelli che finiscono con «:free» sono gratis."""
from servizi_online.base import Servizio

SERVIZIO = Servizio(
    id="openrouter", nome="OpenRouter", ordine=4, gratis=True,
    base_url="https://openrouter.ai/api/v1",
    modello="meta-llama/llama-3.3-70b-instruct:free",
    chiavi="https://openrouter.ai/keys",
    # Modelli «:free»: 20 al minuto, 50 al giorno (1.000 dopo aver comprato almeno 10
    # crediti una volta). Verificato sul web il 15/11/2026.
    limite="Gratis con i modelli «:free»: 50 richieste al giorno (1.000 se hai comprato "
           "almeno 10 $ di crediti una volta), 20 al minuto.",
    richieste_giorno=50,
    passi=("Apri openrouter.ai e accedi.",
           "Vai su openrouter.ai/keys e premi «Create Key».",
           "Copia la chiave (inizia con sk-or-…) e incollala in Lumi."))
