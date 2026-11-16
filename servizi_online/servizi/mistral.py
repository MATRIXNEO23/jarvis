"""Mistral: piano gratuito «Experiment», API compatibile OpenAI."""
from servizi_online.base import Servizio

SERVIZIO = Servizio(
    uso="Buono in italiano e nei testi; sa fare i lavori a più passi.",
    id="mistral", nome="Mistral", ordine=3, gratis=False,
    base_url="https://api.mistral.ai/v1",
    modello="mistral-small-latest",
    chiavi="https://console.mistral.ai/api-keys",
    # Piano gratuito: circa 1 richiesta al secondo e un tetto mensile di token; i numeri
    # esatti sono nella pagina Limits del tuo account (verificato sul web il 15/11/2026).
    limite="Sul tuo account risulta a pagamento (16/11). Il piano gratuito, dove c'è: circa 1 richiesta al secondo, limite mensile nella "
           "pagina Limits del tuo account. Chiede di usare i dati per migliorare i modelli.",
    passi=("Apri console.mistral.ai e crea un account (serve il numero di telefono).",
           "Scegli il piano gratuito «Experiment».",
           "Vai in API Keys → «Create new key», copia la chiave e incollala in Lumi."))
