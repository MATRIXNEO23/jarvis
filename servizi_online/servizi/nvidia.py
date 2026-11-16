"""NVIDIA (build.nvidia.com): modelli aperti come DeepSeek e Llama."""
from servizi_online.base import Servizio

SERVIZIO = Servizio(
    uso="Modelli grandi (DeepSeek, Llama) per ragionamenti difficili; lavori a più passi.",
    id="nvidia", nome="NVIDIA (DeepSeek, Llama…)", ordine=5, gratis=True,
    base_url="https://integrate.api.nvidia.com/v1",
    modello="meta/llama-3.3-70b-instruct",
    chiavi="https://build.nvidia.com/settings/api-keys",
    # Gratis per sviluppo e prove: circa 40 richieste al minuto; ad alcuni account
    # vengono dati crediti iniziali. Verificato sul web il 15/11/2026.
    limite="Gratis per uso personale e prove: circa 40 richieste al minuto, senza limite "
           "giornaliero pubblicato.",
    passi=("Apri build.nvidia.com e crea l'account gratuito NVIDIA Developer.",
           "Vai in Settings → API Keys e premi «Generate API Key».",
           "Copia la chiave (inizia con nvapi-…) e incollala in Lumi."))
