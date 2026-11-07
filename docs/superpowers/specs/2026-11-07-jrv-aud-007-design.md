# JRV-AUD-007 — correzione degli eventi vocali scaduti

Obiettivo concordato: scartare le frasi della sessione precedente dopo spegnimento/riaccensione o cambio modalità. L'utente ha dato «ok» alla soluzione spiegata dopo la verifica Windows; attuare il passo007 con spiegazioni brevi, senza nuova intervista o approvazioni ripetute sui dettagli tecnici.

Base `c9d1d29a085770744e1a1cc34fc7d5f2826ac35b`, bozza40, contiene il riproduttore reale: run42340988254,723 test/job Windows3.11/3.12,9 fallimenti comportamentali e0 errori. Non serve ripetere il Red invariato. Conservare questa evidenza storica.

Scelta tecnica dell'assistente: estendere soltanto gli eventi prodotti da VoiceController a `(kind,value,generation)`; aggiungere `accepts_event(generation: object) -> bool`, che ammette solo interi esatti della generazione corrente, controller aperto e modo attivo. Nel loop reale di `poll`, prima di ogni dispatch vocale, rifiutare payload senza identità, formato/valore non valido o generazione scaduta. Tutti gli altri tipi di evento mantengono il contratto corrente.

Alternative: svuotare tutta la coda perderebbe anche risultati non vocali; una coda/thread paralleli duplicano componenti inutilmente. Portare il numero esistente conserva ordine e controlli senza dipendenze, timer o scansioni aggiuntivi. Non mantenere un fallback per tuple vocali senza generazione: il produttore attuale è unico e il fallback riaprirebbe il difetto.

Preservare PTT/continuo/GPT, hotword, dettatura, consensi, profili, memoria, altri eventi e controllo manuale. Non aggiungere migrazioni, add-on o nuove funzionalità. Il check deve precedere anche log/campione/stato/telemetria e disattivazione dettatura per errori vecchi. Rischio MEDIO: formato condiviso e consumer UI. Il lock del produttore non deve coprire callback/dispatch UI.

Limiti: non risolve né dimostra problemi di cambio progetto o dialoghi modali mentre un evento è già in esecuzione, né nuove sessioni PTT nello stesso modo; nessuna modifica a queste semantiche. Prove Windows con trascrizioni e confini azione/modello controllati, non microfono/Vosk/account reali. Nessun test funzionale Linux, build, merge, ZIP o pubblicazione applicativa.022/023 restano separati e aperti.
