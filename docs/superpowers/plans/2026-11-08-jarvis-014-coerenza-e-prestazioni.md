# Piano operativo Jarvis 014 — coerenza, instradamento e prefill
Data: 2026-11-08. Stato: PIANIFICATO; nessuna modifica runtime né ZIP 014 creata o pubblicata.
Protocollo obbligatorio: docs/PROTOCOLLO-CANONICO-VERSIONI-JARVIS.md; registro: docs/REGISTRO-DELTA-VERSIONI-JARVIS.md.

## Scopo e non-obiettivi
Ripristinare un dialogo coerente e affidabile quanto il miglior comportamento riferito sulla 012, mantenere le ottimizzazioni utili della 013 e ridurre il tempo di lettura del prompt. Non introdurre nuove API, altri LLM, riassunti generativi, dipendenze, servizi o permessi Windows. Nessuna cancellazione di ricordi, progetti, preferenze o ZIP.

## Dati di partenza verificati
- 012 source 5820b00623ec1632df86028c8bd9ac0341c5dc7d; 013 source b9db9e0dc158b07f0c057cffa7b5c97a6f9ff974.
- 013 modifica history_max_tokens predefinito 600 fisso -> 250 configurabile, e colloca i ricordi richiamati presso l'ultima domanda. Parser e validatori identici tra versioni.
- Le due build possono condividere configurazione e memoria su %LOCALAPPDATA%/Jarvis. Con Context Size 1024 e Max Output 600, riserva sicurezza 128, il massimo input teorico resta 296 token; quest'ultimo NON è il solo budget della cronologia.
- Prove utente: "Cos'è un buco nero?" e "Consigliami una serie TV" hanno prodotto errori interpretazione/JSON nella 013; nella 012 si è verificato anche un falso "stato sistema". Console 012 circa 96 s Process + 25 s Generated in una prova. La causa precisa e il confronto prestazionale omogeneo NON sono ancora dimostrati.

## Vincoli operativi
1. Sorgenti baseline immutabili: non riscrivere 012/013 o pubblicare prima dei gate. Eseguire in branch dedicato derivato dal runtime esatto della 013, non dalla root main storica. Registrare ogni singolo commit in docs/REGISTRO-DELTA-VERSIONI-JARVIS.md.
2. Profilo di prova temporaneo separato tramite JARVIS_TRIAL_HOME quando supportato; snapshot non distruttivi. Non acquisire credenziali/chat personali nel registro. Log del prompt grezzo solo opt-in e limitato al profilo prova, con redazione dei dati sensibili e scadenza.
3. Una generazione per richiesta nel percorso normale; nessun retry nascosto verso GPT; catalogo/sicurezza/autorizzazioni restano obbligatori per azioni.
4. Non definire "più veloce" senza stesso GGUF, DLL, thread, contesto, Max Output, samplers, seed (se riproducibile), profilo, domanda, cronologia e temperature. Distinguere qualità semantica da validità JSON.

## Task 0 — baseline riproducibile
- [ ] Verificare ZIP/hash e runtime esatti 012/013; annotare impostazioni dei singoli profili e la condivisione in LOCALAPPDATA.
- [ ] Riprodurre almeno quattro percorsi digitati e vocali: "Cos'è un buco nero?", "Consigliami una serie TV", "stato sistema", "apri calcolatrice". Aggiungere "Se dico stato sistema, cosa succede?" come caso negativo.
- [ ] Acquisire per ogni turno, su fixture sintetica, domanda effettiva, ID percorso scelto, flag della disponibilità del catalogo, lunghezza/count input, output, stopreason (eos/max_length/abort), risposta grezza, esito parser, tempi load/process/generate. Non copiare chat private.

## Task 1 — RED: regressioni mirate
- [ ] Scrivere test che falliscano sulla baseline per due domande informative interpretate come azioni o JSON invalidi (usando risposte simulate realistiche), oltre a test di integrazione reali ove disponibili.
- [ ] Coprire testo libero con parentesi graffe, JSON incompleto per limite token, JSON valido chat, JSON capability valida e capability con arguments non consentiti.
- [ ] Conservare la negazione, le ambiguità, la conferma e la protezione contro esecuzioni non richieste: mai convertire un JSON fallito in un comando.
- [ ] Testare risposte contestuali a follow-up, cambio progetto e memoria disattivata/attivata; verificare archivio intatto.

## Task 2 — correggere routing/conversazione, dopo evidenza RED
- [ ] Distinguere COMANDI ESPLICITI già riconosciuti dal motore locale da DOMANDE INFORMATIVE che richiedono una risposta naturale. Non basarsi solo su parole-chiave isolate: "che cosa succede se dico ..." è informativo, non comando.
- [ ] Per chat informativa, produrre testo naturale senza chiedere JSON d'azione; conservare tono/personality, memoria recente, riferimento e contesto di progetto. Non allentare parser delle azioni.
- [ ] Per comandi non risolvibili deterministicamente, usare il percorso strutturato già validato con catalogo minimo utile e autorizzazioni attuali; chiarire in caso di ambiguità. No doppia inferenza automatica.
- [ ] Se max_output tronca un JSON, distinguere stopreason e segnalare risposta incompleta; non completare/reinterpretare un frammento come comando eseguibile. Conservare un feedback diagnostico sensato.
- [ ] Evitare che un turno di errore diventi storia autorevole per comandi futuri.

## Task 3 — qualità del contesto e prestazioni
- [ ] Mantenere il prompt semantico utile delle domande informative, con più spazio per scambi pertinenti quando necessario; comparare budget history 250/600 a parità di contesto e output.
- [ ] Misurare se catalogo e richiami variabili causano prefill superfluo; tenerli fuori SOLO dal percorso effettivamente informativo, senza perdere capacità operative quando richieste.
- [ ] Ridurre duplicazioni e mantenere prefisso stabile quando possibile senza perdere riferimenti o autorizzazioni.
- [ ] Comparare tempi di tokenizer, load, prefill, decoding, UI/TTS su Windows runner e in seguito su Pavilion reale; non promettere tempi specifici né imporre nuovi parametri utente.

## Task 4 — gate, accettazione, rilascio
- [ ] Suite Windows completa e regression tests su 012/013/014; codice di sicurezza e revoche, app Store/programmi, file, Telegram, audio/wake word, memoria/Second Brain e progetti.
- [ ] Le domande "buco nero" e "serie TV" devono ricevere chat pertinente, senza system.status, nessun parser error di natura strutturale su risposte conversazionali.
- [ ] "stato sistema" deve funzionare come comando esplicito e rispettare la modalità locale; le frasi ipotetiche non devono eseguirlo.
- [ ] Ogni test di continuità deve confermare almeno il riferimento dell'ultimo scambio; nessun dato/consenso cancellato. Un mancato recupero deve essere esplicitato, non coperto da memoria inventata.
- [ ] Per la velocità comparare mediana e intervallo di più prove identiche; la qualità del dialogo e la sicurezza hanno precedenza sul guadagno prestazionale.
- [ ] Documentare ogni diff reale nel registro canonico, con motivazione, metriche prima/dopo, SHA, hash, rischi e rollback. Fermare il rilascio se qualità/sicurezza peggiorano.
- [ ] Solo su richiesta esplicita di pubblicazione: preparare nuovo Jarvis-014.zip numerato e immutabile, verificare su ZIP estratto Windows, hash, link Download e metadata; lasciar disponibili 012/013. Il collaudo PC rimane un gate distinto.

## Procedura di ritorno indietro (prima di ogni prova su PC)
Chiudere Jarvis, fare una copia con data del profilo %LOCALAPPDATA%/Jarvis e delle cartelle di test, conservare ZIP/sha dei pacchetti, avviare la vecchia versione in cartella nuova. Se la 012 legge memory.json ma ignora memory.native.json della 013, non cancellare il sidecar; usare snapshot coerente per confronti e test. Verificare ripristino impostazioni, avvio e cronologia, registrare risultato nel delta.

## Decisione ancora da prendere con evidenze
La separazione conversazione/comandi va applicata nel punto più piccolo e sicuro del routing esistente. La proposta è un'ipotesi architetturale da provare con test RED/GREEN, non un fix già implementato.
