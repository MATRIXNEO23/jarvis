# Jarvis — review completa della build, 3 novembre 2026

## Mandato e priorità
Richiesta attuale: applicare le skill installate alla review di TUTTE le funzioni esistenti di Jarvis, prima di aggiungere altre capacità. Comprende dialogo/GPT/memoria, ricerca/file/Explorer, documenti/dettatura, voce/TTS/microfono, timer, Telegram, progetti/persistenza, diagnostica, add-on/impostazioni, HUD e distribuzione.

L'apertura generale per nome dei programmi desktop e delle app Microsoft Store, con aggiunta manuale per gli elementi non rilevati, è una richiesta confermata ma differita. È già descritta in [WINDOWS](implementabili/WINDOWS.md); non è implementata nella build corrente. Non riprendere quell'incremento durante questa review.

## Metodo
- Brainstorming: usare i requisiti salvati e chiarire soltanto dubbi che cambiano il risultato; non ricominciare la raccolta.
- Writing Plans: inventario delle funzioni e controlli per componente, poi priorità delle correzioni.
- Systematic Debugging: rilievi con trigger, percorso del codice, evidenza e ipotesi separate.
- Verification Before Completion: distinguere codice, prove automatiche storiche, osservazioni di questa review e prove ancora necessarie.
- Seconda lettura indipendente secondo il workflow pubblico Requesting Code Review di Superpowers; nessuna nuova skill installata per questo controllo.

Review in sola lettura del prodotto: non implica autorizzazione a nuove funzioni, refactoring esteso o pubblicazione ZIP. Test funzionali soltanto Windows. I controlli locali dei byte/archivio e l'analisi statica non sono collaudi runtime Windows.

## Riferimenti e primo riscontro
Pacchetto: Jarvis-Accesso-File-0.1.0-20261101-d06e233.zip, source d06e233a98e4ea5b4e99a9d296b9570ce0c92d86. Acquisiti i byte dalla repository: 266689 byte, 79 file, SHA-256 ac130883d32518b430737f8f3d767a16a56e3cad9b3ae32f37d8f20799f42699; CRC e percorsi dell'archivio controllati, estrazione riuscita. Nessun avvio dell'app in questa osservazione.

Sorgenti correttivi distinti: 806685275947cea4b933d20aa0317658d13b853c, ramo feature/fix-file-search-20261102, testa 445efe657e8bbac504d11ce71b10c7c110c3880d; correzioni dialogo non distribuite nello ZIP. [Evidenza](evidence/file-search-dialogue-20261102.json) e [handoff precedente](HANDOFF-RIPRESA-RICERCA-20261102.md).

## Stato del checkpoint
IN CORSO: confronto pacchetto/sorgenti, lettura delle funzioni e delle integrazioni, copertura delle verifiche Windows, seconda lettura indipendente. Nessun risultato globale di correttezza dichiarato.

Prossimo controllo: chiudere la matrice di copertura e i rilievi prioritari con riferimenti al codice; separare difetti confermati, punti da riprodurre su Windows e capacità future. Poi salvare rapporto, limiti e sequenza di correzione senza creare una nuova build.
