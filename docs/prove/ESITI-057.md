# Prove Lumi 057 (73b2b3c)

| prova | esito | dettaglio |
|---|---|---|
| 1 ciao | ko | CtxLimit:121/800 (non 896); il motore si e' anche ricaricato con n_ctx 1024. Chat: una sola risposta, nessun /nothink visibile |
| 2 Promessi sposi + approfondisci + sì | ko parziale | Chiede «Vado online? Di' sì o no.»; risposta Groq su Manzoni (ok, non sul ciao). Ma in lumi_chat il testo lungo («Domanda dell'utente: ... Spiega meglio...») compare come messaggio utente |
| 3 meteo domani | ok | «Domani a San Vendemiano: pioggia, minima 6 e massima 12 gradi.» Nessun modello/conferma. Manca solo il cielo esplicito oltre a «pioggia» |
| 4 approfondisci senza risposta pertinente | ko/dubbio | Prima risposta era il meteo; ha chiesto «Vado online?» invece di «Cosa vuoi approfondire?». Prova non del tutto pulita (contesto precedente presente) |
| 5 lumi_online | ok | Gemini, Groq, OpenRouter spuntati; Mistral spento (senza chiave) |
| 6 lumi_impostazioni | non verificato | Voci Modelli: Modelli offline, GPT dal browser, Servizi online, Servizi di ricerca, Orchestratore, Altro. Nessun «Contesto e memoria» nell'elenco; pagina non aperta |
