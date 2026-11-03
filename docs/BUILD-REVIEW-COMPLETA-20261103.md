# Jarvis — review completa della build, 3 novembre 2026

## Esito e ambito

**Review del pacchetto e dei sorgenti completata; collaudo funzionale completo della prossima versione ancora da eseguire su Windows.** Sono state esaminate tutte le aree esistenti elencate sotto, senza modificare il prodotto e senza creare o pubblicare una nuova build. Il pacchetto non va dichiarato corretto sulla sola base di questa review.

La prima priorità richiesta dall'utente è la continuità tra frasi e la veridicità delle risposte nel passaggio GPT–motore locale. Sono emersi punti concreti nel codice che possono perdere il contesto o consentire conferme prive di un risultato locale. Non è dimostrato che spieghino ogni episodio riferito dall'utente; servono conversazioni riproducibili e tracciate.

È salvata e **differita** la richiesta di apertura per nome dei programmi desktop e delle app Microsoft Store, con aggiunta manuale per quelli non rilevati: vedere [WINDOWS.md](implementabili/WINDOWS.md). Questa review riguarda le funzioni già presenti.

Metodo: Brainstorming per chiarire obiettivo e vincoli; Systematic Debugging per seguire i passaggi reali; Writing Plans per ordinare interventi e prove; Verification Before Completion per separare verifiche svolte e mancanti. Applicato anche il metodo di [Requesting Code Review](https://github.com/obra/superpowers/tree/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/requesting-code-review), con una revisione indipendente di voce, documenti, Telegram, timer, persistenza e ciclo di vita. Questa ulteriore skill non è stata installata.

## Quale versione è stata controllata

| Elemento | Riferimento / risultato |
| --- | --- |
| ZIP pubblicato | Jarvis-Accesso-File-0.1.0-20261101-d06e233.zip |
| Sorgenti del pacchetto | d06e233a98e4ea5b4e99a9d296b9570ce0c92d86 |
| Dimensione / SHA-256 | 266689 byte / ac130883d32518b430737f8f3d767a16a56e3cad9b3ae32f37d8f20799f42699 |
| Archivio | 79 file, 64 moduli Python; CRC, percorsi ed estrazione controllati |
| Manifest | 78 impronte dei file operativi corrispondenti ai byte estratti |
| Confronto sorgenti | 78/78 file operativi corrispondono dopo normalizzazione CRLF→LF; le differenze grezze di fine riga non sono difetti di contenuto |
| Sintassi | Parsing statico AST dei 64 moduli riuscito; non è un avvio dell'app |
| Correzioni successive | 806685275947cea4b933d20aa0317658d13b853c; non incluse nello ZIP |
| Ramo di lavoro verificato | feature/fix-file-search-20261102, testa 445efe657e8bbac504d11ce71b10c7c110c3880d; rispetto a 8066852 cambiano documentazione e LEGGIMI, non codice eseguibile |
| Base stabile da preservare | b936879a431370d206152be7b089baf587d15499, Timer Audio Fix2 confermata dall'utente |

Sono stati riletti i log Windows esistenti, non rilanciate le suite in questa review:

- [Run 41350638557](https://github.com/MATRIXNEO23/jarvis/actions/runs/41350638557), versione pubblicata: 466 test su ciascuna versione Python 3.11/3.12, 93 test sullo ZIP estratto, controlli manifest, probe, Windows Search e avvio/chiusura UI riusciti nei rispettivi job.
- [Run 41367835278](https://github.com/MATRIXNEO23/jarvis/actions/runs/41367835278), correzioni successive: 471 test per Python 3.11/3.12, senza fallimenti nei log esaminati. Questo risultato non aggiorna automaticamente il pacchetto distribuito.

Non sono stati eseguiti test funzionali su Linux. I risultati storici non provano microfono, altoparlanti, account GPT/Telegram, rendering o prestazioni sul PC dell'utente.

## Copertura di tutte le aree esistenti

| Area | Esame svolto e limite attuale | Esito / verifica successiva |
| --- | --- | --- |
| Dialogo, memoria, GPT, instradamento e azioni | Tracciati messaggi, budget, memoria, parser, risposta e dispatch locale | R01–R04 e R06; prove a più turni prioritarie |
| Ricerca file, cartelle, lettura, Explorer | Ambiti autorizzati, risultati, raffinamento, cancellazione, indice e scansione | R02 e R05; distinguere ricerca parziale e assenza verificata |
| Programmi e browser | Catalogo attuale limitato, apertura prevista e ricerca nel browser | Apertura generale desktop/Store differita; aprire una pagina di ricerca non equivale a leggerne i risultati |
| Documenti e dettatura | Blocco Note gestito da Jarvis, creazione, append, versioni, salvataggio, chiusura e recupero | R07; non promettere controllo di qualsiasi documento già aperto |
| Microfono, PTT, ascolto continuo | Flussi di registrazione, riconoscimento, attivazione e worker | Prove reali Windows con dispositivo e cambio modalità ancora necessarie |
| Voce e TTS | Coda, sintesi, subprocess, chiusura, messaggi pronunciati | R08 e R09; provare interruzione e uscita durante parlato |
| Timer e allarmi | Stato, avvio/annullamento, persistenza e percorsi audio | Test storici disponibili; suono e interazione con voce da provare sul PC |
| Telegram | Selezione contatti, conferma, invio, controlli, risposte automatiche e storico | Nessun ulteriore difetto ad alta confidenza emerso da questa lettura; consegna reale non provata qui |
| Progetti, memoria e preferenze | Separazione dei contesti, persistenza e cambio progetto | Verificare che cambio progetto revochi risultati e autorizzazioni precedenti senza contaminare la conversazione |
| Add-on e permessi | Manifest JSON, handler consentiti, abilitazione e revoca | Conservare controlli; non introdurre esecuzione arbitraria da manifest |
| Diagnostica e revisione interna | Elenco sorgenti, worker, timeout e resoconti | R10: copertura incompleta di file_access; nessuna diagnosi deve presentarsi come controllo universale |
| HUD, finestre e ciclo di vita | Collegamenti worker/UI, transizioni, metriche e uscita | R06 e R08; collaudo visivo e prestazioni su Windows ancora necessari |
| Installazione e distribuzione | Launcher, file runtime, manifest, ZIP e corrispondenza sorgenti | Integrità verificata; prima installazione e autenticazione da collaudare su Windows |

Per le letture locali sono presenti limiti di formato/dimensione e verifiche dei percorsi e dei permessi. Per Telegram restano necessari contatti e conferme previste. Questi controlli vanno mantenuti durante le correzioni.

## Rilievi e prove richieste

Tutti i rilievi sotto derivano dalla lettura statica dei sorgenti. Le riproduzioni funzionali indicate devono ancora essere eseguite su Windows. “Alta” indica priorità prima della prossima consegna, non una perdita dati o un evento già osservato.

### R01 — Alta: il contesto dei risultati viene preparato e poi escluso dal prompt

**Evidenza:** [jarvis.py:622](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/jarvis.py#L622) aggiunge file_results al contesto, mentre [jarvis_persona.py:114](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/jarvis_persona.py#L114) conserva solo alcuni campi del focus e non serializza quel blocco. Il dato può quindi mancare a GPT anche quando c'è spazio nel prompt.

**Intervento:** trasmettere una sintesi strutturata minima di richiesta attiva, operazione, ambito, domanda in sospeso, selezione e risultati effettivi. Riutilizzare i provider esistenti e verificare quanto arriva davvero al modello.

**Prova:** ricerca → elenco reale → “il secondo” → chiarimento → “aprilo”. Controllare prompt e azione finale, inclusi risultati cambiati, scaduti o revocati.

### R02 — Alta: una frase non riconosciuta può cancellare la ricerca attiva

**Evidenza:** [jarvis.py:2695](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/jarvis.py#L2695) può chiamare reset prima del passaggio a GPT sulla base dell'esito del parser e di alcune parole; [file_access/service.py:109](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/file_access/service.py#L109) azzera risultati, selezione e stato pendente.

**Intervento:** conservare la richiesta quando il turno è un chiarimento non risolto; definire transizioni esplicite per annullamento, nuova richiesta, cambio progetto, scadenza e revoca. Conservare contesto non deve conservare autorizzazioni revocate.

**Prova:** dopo una ricerca usare una parafrasi senza le parole previste dal controllo; chiedere poi “quello di prima”. Verificare anche annullamento e cambio progetto.

### R03 — Alta: la risposta libera può dichiarare un'azione senza conferma locale

**Evidenza:** [conversation_router.py:218](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/conversation_router.py#L218) accetta risposte chat/clarify dopo i controlli testuali e di schema; [jarvis.py:3446](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/jarvis.py#L3446) le mostra, pronuncia e ricorda. La validazione non lega una dichiarazione operativa a una ricevuta del motore locale. I comandi locali restano limitati dal catalogo: il problema qui è l'attendibilità del resoconto.

**Intervento:** per le richieste operative, derivare “trovato”, “aperto”, “salvato” e relativi errori da risultati locali strutturati. Il modello può interpretare e formulare il chiarimento, ma non sostituire la verifica dell'azione. Una ricerca incompleta deve rimanere dichiarata incompleta.

**Prova:** usare risposte simulate che dichiarano successo senza azione, percorso inesistente, risultato vuoto e errore locale. Nessuna conferma di successo deve essere emessa senza esito coerente. Non basta una lista di parole proibite.

### R04 — Alta, insieme a R01/R02: otto scambi salvati non significano otto messaggi completi inviati

**Evidenza:** [conversation_memory.py:13](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/conversation_memory.py#L13) limita turni e lunghezza dei testi; il contesto è ulteriormente adattato in context. [jarvis.py:624](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/jarvis.py#L624) chiede un budget ridotto; [jarvis_persona.py:172](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/jarvis_persona.py#L172) considera al massimo sei record recenti e li abbrevia ancora. Il router applica infine il budget residuo del prompt.

**Intervento:** separare lo stato operativo necessario dalla cronologia narrativa abbreviabile. Conservare obiettivo e domanda pendente in forma compatta e misurabile; troncare prima contenuti accessori. Aumentare semplicemente da otto a molti turni non risolve questi passaggi e può superare di nuovo i limiti.

**Prova:** stessa richiesta con conversazione breve, lunga e risposte verbose; misurare il prompt effettivo e controllare la continuità sia entro due turni sia oltre otto scambi.

### R05 — Alta: l'indice Windows non precede globalmente la scansione diretta

**Evidenza:** [file_access/service.py:739](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/file_access/service.py#L739) interroga l'indice e poi scansiona direttamente ciascuna radice; il budget può terminare prima delle radici successive. Una ragione già impostata può inoltre nascondere la nota del provider. [file_access/windows.py:116](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/file_access/windows.py#L116) restituisce risultati e testo, senza distinguere in modo robusto tutte le condizioni di disponibilità/copertura.

**Intervento:** interrogare prima l'indice in tutte le radici autorizzate, quindi eseguire il fallback entro budget. Rendere distinguibili indisponibilità, copertura parziale, zero risultati e scansione interrotta; conservare esclusioni, deduplicazione e revoca.

**Prova:** prima radice grande, elemento nella seconda; indice disponibile, disabilitato e con copertura incompleta; stop per budget. Verificare che il resoconto non trasformi una ricerca parziale in “non esiste”.

### R06 — Media: tempi di attesa diversi e lavoro GPT non cancellato alla scadenza

**Evidenza:** [jarvis.py:1803](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/jarvis.py#L1803) assegna tempi diversi a login, richieste vocali e altre richieste; typed_conversation ricade nel limite più breve. [gpt_client.py:147](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/gpt_client.py#L147) rimuove una richiesta scaduta senza interrompere lo stream sottostante.

**Intervento:** applicare una politica coerente per la stessa operazione vocale/testuale e gestire le risposte tardive o la cancellazione. Non correggere il problema soltanto aumentando tutti i timeout.

**Prova:** risposta controllata dopo circa 45 secondi, invocata a voce e da testo; poi annullamento, nuova richiesta e risposta tardiva. Nessuna risposta vecchia deve alterare il nuovo compito.

### R07 — Alta prima della consegna: possibile modifica persa nel salvataggio con chiusura

**Evidenza:** [managed_documents.py:103](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/managed_documents.py#L103) legge una fotografia del testo, la salva e chiude; [notepad_controller.py:235](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/notepad_controller.py#L235) può azzerare il flag di modifica e inviare la chiusura senza confrontare nuovamente il contenuto corrente. Esiste una finestra temporale per una modifica manuale successiva alla lettura.

**Intervento:** rendere coerenti testo salvato e chiusura, bloccando temporaneamente l'editing oppure rileggendo e confrontando; in caso di differenza mantenere il documento aperto e la protezione per modifiche non salvate. Preservare versioni e recupero.

**Prova:** inserire una modifica tra lettura e chiusura; verificare che venga salvata oppure che la chiusura venga fermata. La perdita dati è un rischio statico, non un incidente riprodotto durante questa review.

### R08 — Media: la sintesi in corso può sopravvivere alla chiusura dell'interfaccia

**Evidenza:** [offline_tts.py:78](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/offline_tts.py#L78) usa subprocess.run con attesa fino a 90 secondi; close in [offline_tts.py:161](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/offline_tts.py#L161) chiude la coda senza un handle di cancellazione del processo già attivo. [jarvis.py:3777](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/jarvis.py#L3777) prosegue con l'uscita della UI.

**Intervento:** prevedere arresto esplicito del processo di sintesi corrente e chiusura controllata del worker, oltre allo svuotamento della coda. Verificare anche il comando di interruzione durante il parlato.

**Prova:** frase lunga → interruzione e, separatamente, uscita dall'app. Controllare cessazione udibile, processi residui e riavvio pulito.

### R09 — Media: il percorso legacy può leggere ad alta voce elenchi di file

**Evidenza:** [local_engine.py:196](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/local_engine.py#L196) e [local_engine.py:223](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/local_engine.py#L223) producono elenchi/percorsi senza separare sempre il messaggio vocale. [jarvis.py:3295](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/jarvis.py#L3295) usa il testo completo quando manca spoken_message. Il percorso Accesso file ha già una risposta vocale separata, ma il fallback legacy può essere ancora raggiunto quando l'add-on è disabilitato.

**Intervento:** applicare la regola richiesta dall'utente anche al fallback: dettagli nell'interfaccia, breve conferma vocale priva dell'elenco.

**Prova:** ricerca Downloads con Accesso file attivo e disattivo, risultati multipli, nessun risultato e nomi lunghi; controllare il testo effettivamente inviato al TTS.

### R10 — Media: la diagnostica globale non comprende i moduli file_access

**Evidenza:** [self_diagnostics.py:52](https://github.com/MATRIXNEO23/jarvis/blob/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86/self_diagnostics.py#L52) elenca i sorgenti della radice e tests senza includere ricorsivamente il pacchetto file_access; l'elenco viene usato dalla diagnostica successiva.

**Intervento:** includere esplicitamente le directory fidate dei moduli installati, entro limiti di costo, ed esporre la copertura effettiva. Non estendere la scansione indiscriminatamente a dati utente o AppData.

**Prova:** un errore controllato in un modulo file_access deve comparire; verificare anche limiti, esclusioni e file non accessibili.

## Correzioni già presenti nei sorgenti successivi, ma assenti dallo ZIP

Il commit 8066852 contiene già interventi per ridurre il prompt/catalogo che superava il limite, conservare nome e azione nel chiarimento della ricerca, correggere l'aiuto sugli ambiti e impedire che una ricerca generica venga trattata subito come ricerca nel browser.

Questi interventi hanno test Windows storici riusciti, ma **non** risolvono automaticamente tutti i rilievi di questo rapporto e **non** sono stati distribuiti nello ZIP d06e233. Ripartire da quel lavoro, evitando di rifarlo o sostituirlo con la vecchia copia di main.

## Piano di ripresa e condizioni prima della prossima build

1. **Continuità e attendibilità (R01–R04):** preparare prove di regressione Windows per frasi consecutive, chiarimenti, selezioni, budget e falsi successi; poi correggere i punti separatamente. Tracciare richiesta, stato prima/dopo, esito locale e resoconto, senza registrare credenziali.
2. **Ricerca (R05):** provare indice su più radici e fallback parziale; correggere ordine e stato dei risultati senza cambiare i permessi.
3. **Affidabilità delle altre funzioni (R06–R10):** verificare per primo il rischio di salvataggio R07; poi timeout, arresto TTS, fallback vocale e copertura diagnostica. Ogni difetto richiede una prova mirata, non soltanto una modifica che sembra plausibile.
4. **Consolidamento:** suite Windows 3.11/3.12, controlli delle integrazioni e regressioni su timer, Telegram, progetti, documenti e add-on; successivamente controlli sullo ZIP estratto e prova reale sul PC per voce, dispositivi, account e prestazioni. Preparazione/pubblicazione della build resta un passaggio successivo, senza pubblicazione automatica.

Criteri minimi: nessuna azione dichiarata riuscita senza esito locale; contesto operativo conservato nei casi riprodotti e correttamente revocato; ricerche parziali esplicite; nessuna perdita nella prova di salvataggio; chiusura e timeout coerenti; assenza di regressioni nelle funzioni esistenti. Questi criteri riducono errori concreti: non sono una garanzia di assenza assoluta di allucinazioni.

## Stato salvato per la continuità

- Rapporto definitivo della review: questo file.
- Evidenza sintetica: [build-review-completa-20261103.json](evidence/build-review-completa-20261103.json).
- Documenti precedenti conservati: [handoff ricerca](HANDOFF-RIPRESA-RICERCA-20261102.md), [correzioni dialogo](RICERCA-DIALOGO-CORREZIONI-20261102.md), [priorità indice Windows](INDICE-WINDOWS-PRIORITA-20261102.md), [skill di sviluppo](SKILL-SVILUPPO.md).
- Nessun codice prodotto, dato utente, skill installata o ZIP modificato da questa chiusura della review.
- Prossimo lavoro concreto: riproduzioni Windows e correzioni ordinate sopra, iniziando dalla continuità; non aggiungere ora l'apertura generale delle applicazioni.
