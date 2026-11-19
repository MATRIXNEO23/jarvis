"""GPT dal browser tra i servizi online (16/11, corretto nella 058 su richiesta del 17/11 05:04).

Non è un servizio a chiave: usa il tuo account ChatGPT già collegato dal browser, con lo stesso
ponte del pulsante GPT (gpt_bridge.mjs / gpt_client). Nella lista mostra «collegato» o «non
collegato» con il pulsante «Collega»; niente chiave e niente pagina delle chiavi.
Riceve testo e restituisce testo: niente strumenti, quindi niente lavori a più passi sul PC.
"""
from online.servizi_online.base import Servizio

SERVIZIO = Servizio(
    uso="Domande difficili, spiegazioni e testi lunghi col tuo account ChatGPT; niente lavori a più passi sul PC.",
    id="chatgpt_account", nome="ChatGPT dal browser", ordine=5, gratis=True, tipo="account",
    orchestratore=False, base_url="", modello="(scelto nel collegamento GPT)",
    chiavi="",
    limite="Usa il tuo account ChatGPT collegato dal browser (GPT dal browser): niente chiave da incollare.",
    passi=("Premi «Collega» e accedi con il tuo account ChatGPT nel browser.",
           "Quando lo stato dice «collegato», spunta «ChatGPT dal browser» e mettilo nella posizione che vuoi.",
           "Non serve nessuna chiave."))
