# Memoria: risposta fondata e distinzione dai comandi — attività futura

Data: 8 novembre 2026. Stato: **da risolvere, non implementare ora**. Autorizzazione corrente soltanto per annotazione e handoff, nessuna modifica runtime o nuova build.

## Riscontro e limiti dell'evidenza
Dopo la consegna013 l'utente segnala un nuovo dialogo: domanda sul ricordo di una persona, risposta affermativa del modello; alla domanda successiva su cosa ricordi, errore «Risposta non interpretabile: Azione non eseguita: Parametri file non consentiti». La descrizione è generalizzata: nessun dettaglio personale o trascrizione privata pubblicato.
Versione effettivamente eseguita, budget salvato, ricordi recuperati e output grezzo del modello non sono stati acquisiti. Non affermare che l'archivio sia vuoto, che il recupero sia riuscito, o che il problema sia causato da128token. Il consiglio precedente di usare128token e2messaggi recenti non conferma che tali valori siano stati applicati.

## Percorso verificato nei sorgenti013
`file_access/service.py:validate_arguments` produce quell'errore per chiavi non ammesse nei parametri di un'operazione file. `conversation_router.py:parse_conversation_intent` e `parse_native_conversation_intent` validano la proposta; `jarvis.py:poll_gemma_trial` mostra il rifiuto e non esegue l'azione.
Questo è compatibile con una proposta file errata per una domanda conversazionale. La risposta grezza non è disponibile: action_id, argomenti specifici e causa del fraintendimento restano da accertare. Un «sì, ricordo» del modello non dimostra recupero effettivo. Non è un motivo per allentare i validatori o concedere accesso ai file.

## Comportamento futuro richiesto dall'utente
- Distinguere una domanda sui ricordi da una richiesta di operare sui file; rispondere in conversazione senza proporre comandi estranei.
- Affermare di ricordare solo sulla base di informazioni pertinenti realmente disponibili dal contesto/Brain, senza inventare dettagli.
- Se il recupero eseguito non trova ricordi pertinenti, dirlo chiaramente, per esempio «Non ho ricordi pertinenti salvati su questa persona».
- Se l'archivio non è accessibile o il recupero fallisce, dichiarare «Non riesco a recuperare questo dato»; non confonderlo con assenza certa di ricordi.
- Se le informazioni non entrano nel contesto, non sono state recuperate oppure il riferimento è ambiguo, dichiarare il limite o fare una domanda breve di chiarimento. Non dire che non esistono dati soltanto perché non sono nel prompt.
- Conservare azioni file legittime, autorizzazioni, validatori, impostazioni configurabili e separazione chat/progetti/Telegram. Non aggirare la validazione JSON o disattivare funzioni per nascondere il problema.

## Prossima ripresa, solo su nuova istruzione
Verificare versione/opzioni reali e confrontare esito del Brain, contesto serializzato e risposta grezza con fixture sintetiche; non salvare contenuti personali o credenziali nella repo. Riprodurre prima le condizioni: ricordo pertinente, nessun risultato, errore archivio, recupero non eseguito/budget insufficiente, riferimento ambiguo, domanda su memoria seguita da richiesta file valida. Progettare la modifica minima nel percorso esistente senza aggiungere un altro modello o servizi. Test funzionali su Windows e review prima di una futura consegna.

Non è una correzione inclusa nella013. La diagnosi Telegram sul PC e il collaudo prestazioni restano aperti e separati. Nessun lavoro di implementazione avviato da questa nota.
