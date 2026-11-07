# JRV-AUD-011 — timeout coerente e annullamento GPT per richiesta

Autorizzazione corrente: procedere con le correzioni preservando quanto funzionava; spiegazione sintetica per ogni passo. Base010 `e65b5ebfa01fe83b7c6ec605da7df836a66ae42e`, nessuna build/merge/dato utente.

Problema: run_gpt tratta typed_conversation come inferenza per permessi/routing ma gli assegna40s anziché180s. GPTClient rimuove pending al timeout (risultati tardivi già isolati per ID), senza chiedere al bridge di interrompere il lavoro. Nessun retry automatico va aggiunto.

Riutilizzo verificato SDK ufficiale fissato a `0a36fefeb913055c8c7a1a29b63d82b96b2e841a`: `packages/local/src/types.ts:75–80` StreamResponseOptions.signal; index.ts listModels(options.signal) e streamResponse(options.signal); responses.ts combina signal con timeout180000ms e lo passa allo stream. Fonte https://github.com/openai/sign-in-with-chatgpt-devkit/tree/0a36fefeb913055c8c7a1a29b63d82b96b2e841a/packages/local/src . Nessun nuovo SDK/dipendenza/API a consumo.

Contratto:

- ask/conversation/typed_conversation180s; sign_in600s e controlli40s conservati.180s riguarda attesa richiesta dopo startup, non il tempo totale di avvio SDK.
- GPTClient timeout di ask: invio best effort del solo comando cancel_request con request_id originario al processo già posseduto, sotto lockpipe. ID controllo nuovo, senza pending/attesa, senza start/login/nuovo ask. Errori pipe non nascondono il timeout originale. Pending originario rimosso comunque; ID mai riusato, risposta vecchia non raggiunge richiesta nuova.
- Bridge: AbortController per ask registrato prima del primo await. cancel_request valida identificativo, interrompe soltanto la richiesta corrispondente; ID inesistente non interrompe altre richieste. Map ripulita in finally. signal a listModels e streamResponse, check dopo await non annullabile di getSession e dopo risultato, nessuna risposta parziale/tardiva dichiarata accettata.
- Shutdown richiede abort alle inferenze ancora possedute prima di uscire; OAuth cancelSignIn preservato. Non disconnettere account per un timeout, non alterare credenziali/configurazione.
- UI mostra timeout e se la richiesta di annullamento è stata inviata; non dichiara conferma remota o token rimborsati. Modello/server/SDK possono impiegare tempo: annullamento best effort, non garanzia di zero consumo o arresto remoto istantaneo.

Rischi: protocollo pipe, concorrenza Telegram/chat, lifecycle bridge e permessi001. Nessuna modifica a routing azioni/microfono/memoria. Test soloWindows con callback reali, client/reader reali con pipe controllata e bridgeNode reale contro SDK finto in profilo temporaneo: nessun account/rete/login, nessuna falsa prova dell'SDK remoto.
