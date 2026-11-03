# Prompt: omettere la memoria realmente vuota — 4 novembre 2026

Autorizzazione: «se è chiara la correzione procedi», dopo audit dei consumi. Incremento prudente concordato in aggiornamento: eliminare soltanto il blocco contesto semanticamente vuoto; mantenere personalità, regole operative e ricordi. Nessun taglio ancora a stile/catalogo, nessuna cancellazione memoria o nuova build automatica.

Base corretta: c08317da300adfbfc7b5896ce1f8706e374b33aa, che conserva la protezione «Jarvis» verificata su Windows. Ramo isolato fix/empty-prompt-context-20261104. Il root storico di main non è la base runtime.

Causa: build_conversation_prompt allega il blocco se la stringa raw è non vuota, anche quando compact_memory produce solo recent/evidence vuoti. build_chat_prompt lo allega anche senza contesto raw. Il controllo deve avvenire DOPO la compattazione/validazione reale, senza confondere assenza di chat recente con assenza di preferenze, progetto, domanda, file, avanzamento o prove.

Piano: riproduzione Red Windows sui payload reali; condizione minima nei due builder, invariata compact_memory e invariati i dati memorizzati; Green completo Windows3.11/3.12. Misura offline prima/dopo sui builder reali, inclusi confronti identici per contesti utili. Zero chiamate modello; distinguere lunghezza UTF-16 da token/usage/quota. Nessuna promessa percentuale sulla quota e nessun nuovo add-on, processo o SDK per una correzione esistente.

Stato: test di riproduzione preparati, runtime ancora invariato. Prossimo passo: Red, modifica minima, regressione e misura; poi aggiornare handoff.
