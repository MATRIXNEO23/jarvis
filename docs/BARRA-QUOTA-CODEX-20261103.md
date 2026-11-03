# Barra quota Codex — proposta e verifica iniziale, 3 novembre2026

Stato: richiesta di fattibilità/proposta; nessuna implementazione, test funzionale o build. Posizione richiesta: spazio libero superiore accanto a «Interfaccia neurale».

## Risultato richiesto e proposta
Barra compatta coerente con HUD esistente, quota Codex residua e ripristino, con dettaglio delle finestre effettivamente restituite dal servizio. Distinguere quota dell’account/limite da contatori locali. Mostrare ultimo aggiornamento e «quota non disponibile» se non letta; niente0/100 supposti. Non inventare durate delle finestre né applicare esempi ufficiali come dati dell’utente. Nessun cambiamento delle modalità voce o connessione richiesto da questa sola UI.

## Verifica del percorso esistente
Sorgenti004/a1b93f34ff25bd9a972ed971a432af4984366f28: gpt_bridge.mjs usa createChatGPT, getSession, listModels, streamResponse; restituisce testo/modello, non quote. gpt_client.py inoltra questo protocollo. installa_gpt.ps1 fissa sign-in-with-chatgpt-devkit a0a36fefeb913055c8c7a1a29b63d82b96b2e841a. Riletti index.ts/types.ts/responses.ts di tale SDK: interfaccia pubblica senza metodo di lettura quote, streamResponse ritorna solo text. Esiste CHATGPT_USAGE_URL=https://chatgpt.com/settings/usage.
Quindi non basta disegnare una barra o contare richieste/token Jarvis per ottenere il residuo richiesto.

## Fonti ufficiali aperte
- https://learn.chatgpt.com/docs/app-server — account/rateLimits/read, account/rateLimits/updated; usedPercent, windowDurationMins, resetsAt, bucket limitId/multi-bucket.
- https://developers.openai.com/siwc/token-sharing-open-source/profiles-and-sessions — collegamento Settings→Usage; limiti condivisi dell’integrazione SiwC Plus.
- https://developers.openai.com/siwc/token-sharing-open-source/codex-app-server — configurazione del provider Responses con OAuthSiwC.
Le fonti non provano che i token SiwC della004 possano leggere i bucket Codex: invocare Responses via provider non dimostra autenticazione per i servizi account Codex. Non equiparare automaticamente la quotaCodex a quellaSiwC o agli header rate limit API.

## Prossimo passo tecnico, se si procede all’implementazione
Prova limitata Windows in sola lettura del protocollo disponibile e dell’autenticazione appropriata, senza cambiare il backend conversazione, senza nuove richieste di inferenza né servizi a pagamento. Verificare Windows10/Pavilion e peso di eventuali componenti prima di scegliere un app-server aggiuntivo. Prima riuso del collegamento esistente; un componente ausiliario va motivato e isolato secondo le regole add-on. Nessun polling serrato o processo residente imposto dalla sola barra.
Solo dopo risposta reale associata all’account corretto: raccordo nel bridge/IPC attuale e HUD; test Windows per percentuali, più finestre, reset, dati mancanti/scaduti, errori/disconnessione/cambio account e nessun blocco UI. Aggiornamenti a richiesta o eventi se effettivamente disponibili. Nessun consumo inferenza per controllare la quota.
Se lettura non disponibile, proporre apertura della pagina ufficiale Uso; non consegnare una percentuale stimata presentandola come quota.
Build soltanto su richiesta separata.

## Punto PC conservato
L’utente conferma nella004 che «apri Netflix» a voce ha aperto Netflix, dopo riscontro positivo catalogo e Prova avvio. Riscontro riferito specifico, non osservazione diretta o prova universale. Proverà programmi dai nomi difficili e possibili frasi personali; esiti ancora pendenti. Nessuna correzione del catalogo necessaria dal caso iniziale poi rettificato.
