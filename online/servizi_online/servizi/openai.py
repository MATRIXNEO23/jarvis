"""OpenAI GPT tramite API: a consumo, separato dall'abbonamento ChatGPT."""
from online.servizi_online.base import Servizio

SERVIZIO = Servizio(
    uso="GPT con la TUA CHIAVE OpenAI (diverso da «ChatGPT dal browser», che usa il tuo account senza chiave): bravo in tutto, anche nei lavori a più passi. A pagamento.",
    id="openai", nome="GPT con chiave (OpenAI API)", ordine=7, gratis=False,
    base_url="https://api.openai.com/v1", modello="gpt-4o-mini",
    ragionamento="effort", ragionamento_modelli=("o1", "o3", "o4", "gpt-5"),
    chiavi="https://platform.openai.com/api-keys",
    limite="A pagamento, a parte: l'abbonamento ChatGPT (anche Plus) non copre le API.",
    passi=("Apri platform.openai.com e accedi.", "Aggiungi del credito in Billing.",
           "Vai in API keys → «Create new secret key», copiala e incollala in Lumi."))
