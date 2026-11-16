"""Google Gemini: API compatibile OpenAI (ai.google.dev/gemini-api/docs/openai)."""
from servizi_online.base import Servizio

SERVIZIO = Servizio(
    preferiti=("gemini-flash-latest", "gemini-2.5-flash", "gemini-flash-lite-latest"),
    uso="Domande lunghe e documenti grandi; sa fare i lavori a più passi sul PC.",
    id="gemini", nome="Google Gemini", ordine=1, gratis=True,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
    modello="gemini-flash-latest",
    chiavi="https://aistudio.google.com/apikey",
    # Google non pubblica più numeri fissi: dipendono dal progetto (pagina «Rate limit»
    # di AI Studio). Verificato sul web il 15/11/2026.
    limite="Gratis con limiti del tuo progetto: li vedi in AI Studio → Rate limit. "
           "Si azzerano a mezzanotte (ora del Pacifico).",
    passi=("Apri aistudio.google.com/apikey e accedi con il tuo account Google.",
           "Premi «Create API key» (crea chiave API) e scegli o crea un progetto.",
           "Copia la chiave (inizia con AIza…) e incollala in Lumi."))
