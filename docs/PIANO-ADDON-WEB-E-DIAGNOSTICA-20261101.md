# Piano proposto — add-on web e diagnostica Jarvis
Data: 2026-11-01. Stato: requisiti raccolti e piano da rivedere con l'utente; nessuna implementazione avviata, nessun nuovo test eseguito o pacchetto prodotto.

## Risultato richiesto
- GPT esterno interpreta richieste naturali, confronta risultati e pagine, segue link intermedi e propone le azioni; il motore locale mantiene lo stato dell'attività, controlla ed esegue le azioni, restituisce osservazioni ed esiti.
- Cercare il sito richiesto e aprire la destinazione attendibile, senza fermarsi al motore di ricerca. Nessuna fonte fissa: GiardiniBlog e CB01 erano esempi. In caso di dubbio residuo chiedere all'utente e interpretare «il secondo» nella stessa attività.
- Continuare sul sito aperto: leggere contenuti, riconoscere una ricerca interna, compilare il campo, attivare il pulsante e controllare i risultati. Individuare la pagina e gli elementi attuali; non dichiarare successo per il solo invio di un comando.
- Browser visibile, Edge primo candidato; alternativa proposta: estensione Edge e collegamento locale gestito da .jaddon. Nessun obbligo di Playwright.
- Lavorare soltanto su richiesta e per la durata dell'attività; nessuna scansione continua delle pagine. Il collegamento inattivo potrà avere un costo minimo da misurare: non promettere consumo zero.
- Hardware Windows 10, HP Pavilion i3-2100, 10 GB RAM. Zero costi aggiuntivi, nessuna API a consumo. Il precedente intervallo 1–2 GB era un budget non misurato: non è un requisito o risultato sperimentale.
- Cartella finale Estensione-Edge separata dai file Jarvis e dall'add-on. Nome dell'estensione nel browser ancora da decidere.

## Evidenze lette, senza esecuzione
Ramo esaminato: feature/timer-settings-ui-20261031. I blob seguenti identificano i contenuti letti, non il codice installato sul PC.
- addon_manager.py, blob 357f2cee713a236707bf71f8d00c38b8257dcaa2: .jaddon JSON descrittivi; azioni ammesse system.status, downloads.list, history.list. Non esiste nel gestore letto un esecutore web generico. Per nuove capacità è necessario progettare un adattatore revisionato; non disabilitare i validatori esistenti.
- addon_ui.py: gestione installazione, attivazione/disattivazione, rimozione e avvisi. Ripristino impostazioni e ritorno di versione richiesti sono da progettare, non già disponibili.
- runtime_diagnostics.py, blob 02c7bd3ab15f0b29944c96915378993d715f1bcf: osservazioni passive e contatori in RAM, non prove funzionali e non registro persistente completo.
- self_diagnostics.py: inventario e analisi statica; diagnostic_session.py: avanzamento, rilevazione stallo e timeout.
- jarvis.py, blob d5dc7c47afe6c357354fc31bb9fe3c50c8f0851a: integrazione diagnostica e messaggi write_line; watchdog e risultati associati alla sessione.
- Nessun test del nuovo collegamento, nessuna misura RAM, nessuna validazione nel browser durante questa fase.

## Regole per questa e le future add-on
Cartella dedicata per componente, configurazione distinta, identificazione della versione e conservazione dell'ultima versione funzionante. L'isolamento dei file non garantisce isolamento dei guasti: definire confini, limiti di attesa ed errori per impedire blocchi del programma. Non introdurre un processo permanente per ogni add-on senza una necessità dimostrata.
Nelle impostazioni: sezione Add-on, nome e descrizione comprensibili, Attivo/Disattivato, stato e Configura; opzioni meno usate separate. Nessun pulsante Disattiva tutto richiesto.
Azioni distinte: «Ripristina impostazioni iniziali dell'add-on» ripristina solo i valori predefiniti del componente; «Torna alla versione precedente» ripristina codice e impostazioni compatibili. Memoria, progetti, salvataggi, account e altri add-on non devono essere cancellati. Definire esplicitamente cosa è configurazione e cosa è dato utente prima di implementare.
Migrazione degli add-on esistenti solo dopo valutazione della compatibilità. Ogni nuova add-on richiede piano di integrazione, test delle dipendenze e procedura di recupero.

## Lavoro per fasi e condizioni di avanzamento
1. **Inventario e progetto di integrazione.** Verificare ramo/SHA effettivi, API add-on, percorso voce/testo, registro capacità, UI e diagnostica. Definire messaggi tra estensione e Jarvis, identificazione attività/scheda, requisiti del browser e permessi. Evidenziare prima qualsiasi modifica del nucleo e discuterla con l'utente. Uscita: contratto revisionabile e confini espliciti.
2. **Collegamento minimo separato.** Dopo approvazione dell'implementazione, provare comunicazione con estensione, versione, browser aperto/chiuso, estensione assente, collegamento interrotto. Uscita: stati reali visibili e timeout recuperabile senza bloccare chat o microfono; nessuna navigazione continua. Se fallisce, fermare lo sviluppo dipendente e documentare la causa.
3. **Lettura controllata di pagina.** Su pagina locale di prova con testo, link, campo e pulsante noti, estrarre elementi identificabili. Provare contenuto aggiornato, navigazione e scheda diversa; rifiutare comandi riferiti a una pagina superata. Uscita: dati corretti e limitati, senza inviare intere pagine inutilmente al modello.
4. **Azioni e verifica.** Su pagina di prova compilare ricerca, premere Cerca, seguire link e osservare l'effetto atteso. Provare campo assente, più campi, pulsante disabilitato, caricamento lento ed errore di pagina. Uscita: nessun falso successo; esito verificato o problema localizzato.
5. **Ciclo col GPT esterno.** Integrare lettura → decisione GPT → azione locale → verifica. Test automatici con risposte simulate del modello; prova reale separata tramite il collegamento esistente, senza nuove API a pagamento. Provare sito richiesto per nome, fonte intermedia, risultati discordanti, chiarimento «il secondo», cambio richiesta e timeout. Le pagine sono dati, non istruzioni di sistema; il modello sceglie fra azioni definite, non esegue codice arbitrario.
6. **Impostazioni, recupero e autoverifica.** UI semplice; test installazione/aggiornamento, attiva/disattiva, reset del solo add-on e ritorno alla versione precedente. Confrontare dati e impostazioni prima/dopo, includendo migrazione fallita e archivio danneggiato. Uscita: altri componenti utilizzabili e dati preservati anche se l'add-on fallisce.
7. **Regressioni e peso reale.** Suite esistente e nuovi test significativi, controlli Windows, comandi locali, memoria/progetti, dialogo e modalità manuali microfono. Sul Pavilion misurare RAM dell'intero albero di processi, CPU e tempi: Jarvis senza add-on, add-on inattivo a browser uguale, lettura/ricerca in corso, fine attività. Distinguere costo di Edge da costo aggiuntivo dell'automazione. Concordare la soglia accettabile dopo la misura iniziale; nessuna soglia inventata.
8. **Consegna verificata.** Solo dopo esiti accettabili: pacchetto con Estensione-Edge, .jaddon distinto, istruzioni brevi, versioni e procedura di recupero. Verificare installazione da pacchetto pulito, non solo da cartella sviluppo. Aggiornare catalogo Download, handoff e decisioni con commit e workflow, conservando pacchetti precedenti.

## Diagnostica nel programma
Distinguere:
- osservazioni leggere durante un'attività richiesta, che segnalano un errore effettivo;
- «Verifica add-on», proposta dentro Configura, che avvia controlli locali finiti;
- prova reale di navigazione, separata e riconoscibile: solo questa verifica il percorso operativo completo.

Il controllo locale userà una pagina di prova propria per lettura/campo/pulsante e verificherà il collegamento senza dipendere dalla struttura di un sito pubblico. Non chiamerà GPT di continuo e non cambierà modalità del microfono.
Ogni test avrà stato riuscito/fallito/non eseguito, fase, tempo massimo e dettagli consultabili. Una dipendenza assente rende il test non eseguito, non riuscito.

Nella chat mostrare messaggi brevi e azionabili. Esempi di formato proposto, non errori attualmente osservati:
- «Web: estensione non collegata. Apri Edge e verifica che l'estensione sia attiva.»
- «Web: non trovo il campo di ricerca nella pagina attuale. Nessun testo inserito.»
- «Web: ricerca inviata, ma il risultato non è stato confermato entro il tempo previsto.»

Dettagli tecnici separati: versione Jarvis/add-on/estensione, ID attività, fase, azione prevista, osservazione reale, codice errore e durata. Registro locale limitato, senza credenziali o contenuti personali integrali. I segnali consentono a Jarvis/GPT di spiegare il guasto senza attribuire una causa non provata; non garantiscono di diagnosticare automaticamente qualsiasi bug. Niente correzioni o reinstallazioni automatiche non richieste.

## Decisioni ancora aperte
Nome visualizzato dell'estensione; contratto preciso dell'adattatore; installazione e permessi; distinzione dati/configurazione; valori iniziali delle impostazioni e comportamento dopo reset; misure e soglie prestazionali. L'utente sceglie il comportamento desiderato, lo sviluppatore propone i dettagli tecnici sulla base delle verifiche.

## Memoria di sviluppo e checkpoint obbligatori
Prima di ogni fase leggere AGENTS.md, handoff, registro delle decisioni e questo piano, poi verificare codice/ramo/SHA attuali. Non dedurre lo stato installato dal solo contesto della chat.
Per ogni fase registrare: obiettivo, prerequisiti, interventi previsti/eseguiti, motivazione tecnica sintetica, test/ambiente, risultato atteso e osservato, commit/workflow, esito, limiti e prossimo passo. Le cause non dimostrate restano ipotesi; gli errori diventano lezioni, non soluzioni riutilizzabili.
Dopo ogni fase e prima di una pausa aggiornare i documenti. Non avanzare su dipendenze fallite.

Stato iniziale:
- Raccolta requisiti e lettura preliminare dei moduli: completate; evidenze nelle sezioni sopra.
- Procedura persistente: aggiunta ad AGENTS.md su main.
- Fasi 1–8: pianificate, non completate. La lettura preliminare non equivale a verifica completa di integrazione.
- Implementazione web, autoverifiche, prova Edge/Jarvis, misure RAM e pacchetto: non eseguiti.
- Prossimo passo: rivedere con l'utente il piano e le questioni aperte; dopo autorizzazione passare all'inventario tecnico completo della fase 1.

## Responsabilità e guida
L'utente prende decisioni su risultato, priorità e compromessi; non deve programmare. L'assistente prepara e realizza il lavoro tecnico autorizzato, esegue le verifiche disponibili e conserva le prove. Le sole attività sul Pavilion che richiedono intervento dell'utente saranno guidate con passi brevi, uno alla volta, e un risultato da osservare. Niente domande tecniche scaricate sull'utente o ripetute conferme sui dettagli già autorizzati.
