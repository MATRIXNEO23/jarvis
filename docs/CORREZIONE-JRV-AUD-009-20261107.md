# JRV-AUD-009 — memoria Gemma collegata agli archivi esistenti

Collegamento verificato nei sorgenti in bozza: gli scambi Gemma accettati possono essere salvati negli archivi già presenti e gli estratti pertinenti possono rientrare nel prompt dopo riapertura. RAG lessicale limitato, senza nuovo archivio, embedding o servizio. Nessuna nuova build installabile o modifica al Jarvis sul PC.

Base `8ca48295da24cd4c5494fd8344e70df20c533133`/bozza42 con001–008; source verificato `5cb797a0d8e7cb1ed508ee1ed2367839fd8b4426`, [bozza43](https://github.com/MATRIXNEO23/jarvis/pull/43), ramo `fix/jrv-aud-009-gemma-memory-20261107`. [Specifica](superpowers/specs/2026-11-07-jrv-aud-009-design.md), [piano](superpowers/plans/2026-11-07-jrv-aud-009-fix.md), [evidenza](evidence/jrv-aud-009-fix-20261107.json).

## Causa e intervento

Il poll Gemma registrava soltanto la storia RAM002, senza `remember_exchange`; il prompt nativo non interrogava SecondBrain/WorkspaceMemory. Gli archivi e il recupero usati da GPT esistevano già. Non era necessario duplicarli in CompactContext o aggiungere un motore di embedding.

| ID/stato | File e funzione | Modifica | Rischio/test |
|---|---|---|---|
|JRV-AUD-009, MEDIO, CONFERMATO; collegamento verificato in bozza|`jarvis.py:4228`, `native_memory_request`; `submit_gemma_voice/poll_gemma_trial`|Cattura archivio, progetto e revisione sul thread UI; lettura nel worker senza Tk. Dopo epoca/progetto e commit unico, salva attraverso `remember_exchange` solo con proprietario ancora autorizzato.|MEDIO: consenso, revoca e contesti. Test OFF, cambi owner, doppio poll, epoca/progetto revocati, processo nuovo e isolamento.|
|Stessa009|`native_conversation_session.py:80,115`, `forget_context/prepare_turn`; `chat_transport.py:35`|Reader opzionale per richiesta, con spazio nel budget e massimo600caratteri di archivio; domanda/tag di ruolo preservati, delimitatori di template archiviati neutralizzati. Clear RAM con lock breve della storia.|Test budget piccolo, testo template, reader su worker reale/no accessi UI e Clear durante inferenza bloccata.|
|Stessa009|`workspace_memory.py:542`, `prompt_context`|Preferenza per ricordi correlati solo sul nuovo chiamante; ordine preesistente dei chiamanti default mantenuto. Nome progetto deve rientrare nel budget della nuova modalità.|Test vecchio fatto pertinente contro rumore recente con budget stretto; suite Workspace/GPT preesistente.|
|Stessa009|`jarvis.py:652,2156`, `remember_exchange/clear_saved_memory`|Risultato esplicito della scrittura per avviso; Clear generale revoca turni Gemma e RAM prima dell'I/O, anche se DELETE riesce e pulizia successiva fallisce.|Test errori lettura/scrittura, eliminazione reale seguita da errore e nessuna resurrezione tardiva; progetti preservati.|

Nessuna modifica a schema SQL, dati precedenti, permessi delle azioni, microfono o impostazioni dell'utente. Nessun nuovo thread di servizio, indicizzatore o scansione continua.

## Politica della memoria

- Generale: lettura solo con Second Brain autorizzato alla partenza; scrittura dopo accettazione soltanto se archivio e consenso sono ancora validi. OFF→ON e ON→OFF→ON non autorizzano retroattivamente turni vecchi. OFF conserva dati già sul disco e memoria breve, come prima.
- Progetti: archivio del progetto catturato alla richiesta, senza importare generale/altri progetti. Progetti espliciti mantengono la politica già esistente, indipendente dalla spunta del Second Brain generale. Epoca/progetto devono ancora coincidere all'accettazione.
- Clear generale: dopo conferma revoca subito turni generali Gemma in attesa e relativa RAM, senza attendere l'inferenza o cancellare progetti. Un prompt già letto non può essere ritirato dalla generazione; non può però causare accettazione/riscrittura tardiva dopo Clear.
- Trial/picker/Telegram isolato mantengono i percorsi senza archivio della chat Gemma. Ricordi restano dati e non autorizzano azioni o ricevute verificate. I filtri e i limiti di testo dei due archivi sono riusati.

## Prove Windows

Comando `python -m unittest discover -s tests -v`, Windows Server2022 x64.

| Fase | Source/run | Python e job | Risultato |
|---|---|---|---|
|Red1|6b10d15 /42346405650|3.11.9/128324998261|765 test,16 fallimenti009,0 errori,182.984s.|
|Red1|6b10d15 /42346405650|3.12.10/128324998507|765 test,16 fallimenti009,0 errori,171.711s.|
|Red2 ampliato|c6ce3e0 /42346662291|3.11.9/128325781974|767 test,18 fallimenti009,0 errori,152.013s.|
|Red2 ampliato|c6ce3e0 /42346662291|3.12.10/128325781765|767 test,18 fallimenti009,0 errori,151.260s.|
|Green|5cb797a /[42347553638](https://github.com/MATRIXNEO23/jarvis/actions/runs/42347553638)|3.11.9/128328470822|768 test,0 fallimenti/errori/skip,171.328s.|
|Green|5cb797a /42347553638|3.12.10/128328470641|768 test,0 fallimenti/errori/skip,138.359s.|

Green al tentativo1, nessun retry. Tutti21nuovi metodi passano. Conservata la suite precedente747; una caratterizzazione002 che richiedeva assenza di persistenza è intenzionalmente aggiornata al comportamento009 autorizzato: record precedenti invariati più append accettato. Altre asserzioni mantenute, fixture allineata ai callback reali.

Le prove eseguono callback/trasporto/sessione e SQLite reali; inferenza catturata. Una nuova sessione e un processo Python nuovo recuperano un turno generale precedentemente accettato: asseriti richiamo del dato e0chiamate online. Verificati salvataggio voce/testo una volta, lookup pertinente, isolamento, OFF, owner/epoca/progetto revocati, Clear concorrente e Clear con errore dopo eliminazione reale, feedback errori, filtri esistenti, budget e template. Il test di thread registra eventuali accessi impropri invece di affidarsi a un'eccezione che potrebbe essere assorbita.

Sintassi Python/JavaScript/PowerShell e probe nativo file passati in entrambi i job. Search live3.12 passata con servizio ripristinato e fixture rimossa; live3.11 non previsto. Build, pacchetto estratto e pubblicazione saltati. La suite include il probe006 di DLL/export, distinto dalle inferenze catturate009 e senza GGUF.

## Review e limiti

Review indipendente in sola lettura: tre lacune iniziali dei test recepite. Un difetto importante della prima candidata è stato corretto prima del Green: `clear_all` può committare DELETE e poi fallire su VACUUM; revocare solo dopo il ritorno permetteva il ripristino tardivo. Ora la revoca precede l'I/O. Nuovo test con eliminazione reale e errore simulato successivo, ricontrollo mirato senza rilievi residui. Questo21°caso è stato aggiunto dopo Red2: non viene dichiarato come ulteriore Red eseguito. Il revisore non ha eseguito test.

Il recupero è lessicale e limitato a estratti, non garantisce ricordo universale o comprensione reale di Gemma. SecondBrain mantiene i limiti esistenti di ricerca fino a3000ricevute/1500episodi; Workspace usa FTS o fallback limitato, con4candidati per prompt. I testi salvati rimangono troncati secondo le regole degli archivi. Budget troppo piccolo può escludere i ricordi; la domanda resta prioritaria.

Nessun nuovo archivio CompactContext, sintesi automatica o IdleMemoryGate è attivato: quelle funzionalità restano incomplete/proposte distinte e non sono dichiarate verificate dalla009. I21test provano il collegamento, non qualità di un GGUF reale. Nessun account GPT/Telegram, microfono, modello reale o benchmark Windows10/i3-2100/HDD/RAM/CPU. Nessun test funzionale Linux.

La persistenza riusa il percorso UI sincrono preesistente: timeout SQLite5/6s e snapshot progetto possono rallentare un tick in caso di contesa HDD. La lettura avviene nel worker; non è una misura delle prestazioni sul target. Le garanzie Clear qui sono per Gemma generale; i flussi GPT esterni in corso non sono stati modificati o nuovamente verificati.022/023 non riprodotti e ancora aperti;010/timeout-abort resta separato.

Nessuna build/ZIP/release/merge o alterazione di profili/dati dell'utente. Checkpoint finale solo documentazione/evidenze, runtime/test identici al source verde. Fermarsi dopo009. Prossimo al via: riprodurre010 e valutare arresto/timeout nativo senza attendere il lock d'inferenza, prima di qualsiasi modifica o build.
