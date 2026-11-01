# 2. Collegare il GPT esterno
Occorrono Python, Node.js con npm e un account ChatGPT autorizzato. Il modello resta esterno: non devi scaricare un modello GPT sul PC.

## Prima configurazione
1. Chiudi Jarvis.
2. Dalla cartella del programma avvia installa_gpt.bat con doppio clic.
3. Attendi la conclusione. Lo script scarica il sorgente SDK fissato al commit 0a36fefeb913055c8c7a1a29b63d82b96b2e841a e compila il solo workspace locale con npm.
4. Il risultato atteso è la presenza di:
   %LOCALAPPDATA%\Jarvis\runtime\siwc\packages\local\dist\index.js
5. Avvia avvia_jarvis.bat.
6. Apri ingranaggio → GPT e memoria → Connessione ChatGPT. Lascia abilitato il collegamento e premi Connetti ChatGPT.
7. Completa l'accesso nel browser aperto dal flusso di login. Non incollare password o token nella console di Jarvis.
8. Attendi lo stato «connesso». Scrivi una domanda breve e usa Chiedi a GPT. Una risposta pertinente è la prima prova reale; lo stato abilitato da solo non basta.

Non occorre una chiave API a consumo e non è previsto un fallback a pagamento. Disponibilità, autorizzazione e quote dipendono dal servizio e dall'account.

## Se qualcosa manca
- Node/npm non trovati: completa l'installazione Node e riapri Jarvis/terminale.
- SDK non installato: esegui installa_gpt.bat e leggi l'esito finale.
- Cartella SDK incompleta: lo script non la sovrascrive; conserva una copia e fai diagnosticare il motivo prima di rinominarla e riprovare. Non cancellare gpt_account per riparare l'SDK.
- Non connesso o autenticazione scaduta: premi Connetti ChatGPT. Non serve reinstallare Python.
- Errore di quota/autorizzazione: è diverso da un componente assente. Jarvis deve mostrarlo, senza attivare servizi a pagamento.

L'account cifrato è in %LOCALAPPDATA%\Jarvis\gpt_account; SDK/account restano qui anche quando il launcher usa il profilo Trial.
Il login reale non viene eseguito dai test automatici senza credenziali.
