"""ChatGPT con il tuo account (Sign in with ChatGPT), messo tra i servizi online il 16/11.

Non usa una chiave: passa dal collegamento GPT di Lumi (gpt_bridge.mjs). Consuma la quota del
tuo piano ChatGPT, la stessa di Codex (help.openai.com/articles/20001542): in ChatGPT,
Impostazioni → Utilizzo → limiti delle app, puoi dare a Lumi una percentuale.
Riceve testo e restituisce testo: niente strumenti, quindi niente lavori a più passi sul PC.
"""
from servizi_online.base import Servizio

SERVIZIO = Servizio(
    uso="Domande difficili, spiegazioni e testi lunghi col tuo piano; niente lavori a più passi sul PC.",
    id="chatgpt_account", nome="ChatGPT (tuo account)", ordine=5, gratis=True, tipo="account",
    orchestratore=False, base_url="", modello="(scelto nel collegamento GPT)",
    chiavi="https://chatgpt.com/settings",
    limite="Compreso nel tuo piano ChatGPT, ma consuma la stessa quota di Codex: mettigli un "
           "limite in ChatGPT → Impostazioni → Utilizzo.",
    passi=("In Lumi accendi il collegamento GPT e accedi col tuo account ChatGPT.",
           "In ChatGPT → Impostazioni → Utilizzo → limiti delle app, scegli quanto può usare Lumi.",
           "In ONLINE ▾ spunta «ChatGPT (tuo account)»: niente chiave da incollare."))
