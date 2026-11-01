## Aggiornamento concordato — continuità prima della navigazione, 2026-11-01

Questo aggiornamento supera i dubbi già risolti e le vecchie priorità sotto. Stato: studio/progetto, nessuna nuova implementazione o build. L'utente concorda l'obiettivo, chiede ora di studiarlo bene; build/pubblicazione restano su richiesta esplicita.

### Requisiti confermati
- Navigazione dalla cartella realmente attiva, anche aperta manualmente. «Apri Foto» deve aprire il figlio identificato nel contesto corrente, senza ricominciare una ricerca generale. Se non identificabile/mancante, chiarire prima di ampliare. Conservare distinzione tra cartella osservata e ultima cartella aperta da Jarvis; contesto non osservabile non va inventato.
- Una domanda deve conservare l'obiettivo: «apri una cartella» → «quale?» → solo nome/numero → apertura richiesta. Non chiedere di nuovo cosa fare col nome. «Questa» richiede selezione concreta o chiarimento breve. Nome ambiguo non deve aprire arbitrariamente il primo risultato.
- Finestra dedicata per risultati numerati/tipo/percorso, selezionabili con mouse o voce; niente elenchi lunghi recitati o riversati in chat. Voce breve e possibilità di interrompere il parlato con un nuovo comando richiesta, ancora da verificare/progettare.
- Programmi installati, finestre aperte e finestra attiva riconoscibili; passaggio alla finestra scelta. Chiusura consentita anche per finestre aperte manualmente, per programmi autorizzati, normale e con eventuale salvataggio lasciato all'utente. Il vecchio dubbio sull'origine della finestra è risolto: non ripeterlo. Spunte apertura/chiusura separate nelle impostazioni.
- Vista distinta per processi in background; nessuna autorizzazione implicita alla terminazione forzata. Schede del browser richieste, fattibilità/integrazione da verificare separatamente senza assumere che una scheda sia una finestra.
- Ricerca non abbandonata per un budget breve: proposta di lavoro in background annullabile, con avanzamento e copertura effettiva, senza bloccare i nuovi comandi o promettere risultato universale. Non aggirare permessi/esclusioni; sospensione o limite devono produrre «incompleta», non «assente».
- Cercare riferimenti del programma anche con nomi parziali/differenti: identità, collegamenti, registrazioni e percorsi verificabili; distinguere installazione, impostazioni, dati e cache. Cercare configurazioni anche in AppData, senza presumere che ogni programma vi conservi tutto. Più profili/installazioni richiedono scelta; associazioni probabili etichettate. Nessuna modifica ai file per il solo ritrovamento.

### Evidenza statica e limite della diagnosi
Letto service.py nel ramo feature/file-access-20261101, blob 2f4255589afc3dd6e08d8111421527b563549bbc. parse_command riconosce il numero dei risultati e produce select; execute(select) consuma _pending e riprende open/read. Manca un collegamento equivalente per il solo nome scelto dall'elenco. Il resolver del nome dell'app pendente riguarda solo locate/installazione. _target risolve alias, numeri e selezione oppure richiede un percorso; non cerca un figlio della cartella Explorer corrente. Sono lacune osservabili nel codice, non una riproduzione runtime né prova del motivo preciso di ogni risposta GPT riferita. LocalEngine usa il parser file prima del proprio percorso generale; la domanda nel focus GPT è un dato conversazionale e non sostituisce l'azione locale pendente.

La ricerca diretta attuale confronta nomi, visita ricorsivamente cartelle consentite, evita link/reparse point e conta le voci incontrate prima di alcuni filtri. Limiti attuali: 5000 voci, 10 secondi della fase diretta, 20 risultati; l'indice Windows è interrogato separatamente. Il numero esaminato non conta documenti letti né certifica copertura completa. Non sono disponibili i percorsi effettivamente visitati sul PC.

### Primo percorso minimo proposto, non implementato
Riutilizzare stato e servizio file esistenti: conservare operazione richiesta, ambito, tipo e risultati mentre si attende il solo dato mancante. Prima di trattare una risposta breve come nuova domanda, tentare di completare la richiesta pendente con nome, numero o selezione verificata. Non riusare richieste annullate/scadute, risultati sostituiti o contesti revocati; cambio argomento e nuovi comandi devono essere gestiti senza eseguire la vecchia azione. Scelta tecnica ordinaria: migliorare il componente responsabile, nessun motore di memoria parallelo o nuova add-on per ogni comando.

### Fasi e accettazione da verificare solo Windows
1. Chiarimento completo: apertura richiesta → scelta fra due cartelle → risposta col solo nome/numero → esatta cartella, una sola esecuzione; provare doppioni, nome non presente, file al posto di cartella, annulla, scadenza, cambio progetto/argomento e GPT indisponibile. Testare callback testo/voce simulati distinti dal microfono reale. Non presentare il comportamento locale come già collaudato.
2. Cartella corrente e navigazione: prova Windows limitata di rilevazione Explorer/focus, figlio, cartella superiore e cambio manuale. Finestre/schede multiple e viste virtuali devono produrre ambiguità esplicita; verificare consumo sul target senza polling continuo non motivato.
3. Risultati e ricerca: vista dedicata, avanzamento, annullamento, cause distinte di arresto e copertura; programma/impostazioni collegati a prove locali. Scansione incompleta e file non accessibile vanno distinti da zero corrispondenze. Valutare riuso prima di nuovi componenti.
4. Inventario programmi, permessi e passaggio/chiusura finestre; processi e schede browser in incrementi distinti con fattibilità verificata. Registro capacità e add-on restano coerenti con quanto davvero attivo.
Per ogni incremento servono regressioni Windows e verifica del percorso completo; una fase fallita blocca le dipendenti. Nessuna suite nuova o prova PC effettuata in questo studio. Prossimo passo: completare progetto tecnico mirato del primo percorso e punti di integrazione del contesto voce/testo/GPT, senza avviare automaticamente implementazione o build.

# Proposta — navigazione file e programmi con permessi

Stato: proposta da discutere, non nuova build. La richiesta più recente ferma build automatiche e sviluppo delle nuove funzioni finché non concordata la soluzione. Windows soltanto per i test. Codice esistente da riusare; niente nuovo modello, indicizzatore, servizio residente o API a consumo.

## Esperienza proposta
- Ricerca: elenco numerato in chat, etichetta File/Cartella e percorso; nessuna lettura vocale di righe/nomi. Un riscontro breve può chiedere quale aprire soltanto se ci sono più corrispondenze. Un solo risultato viene mostrato senza domanda inutile; una ricerca non equivale a un ordine di apertura.
- Scelta: numero o nome fra i risultati. «Questo» usa una selezione identificabile in Explorer o la scelta già fatta in chat; se non identificabile chiede una precisazione breve.
- Navigazione: dopo apertura, contenuto della destinazione e nuovi numeri; «qui dentro», nome della sottocartella e «vai indietro di una cartella». Quest’ultimo significa cartella superiore, non vecchio argomento o nuova ricerca dall’inizio.
- Cambio manuale: interrogare cartella e selezione di Esplora file a richiesta. Più finestre/schede o viste virtuali possono essere ambigue: chiedere quale usare, non dedurlo da uno screenshot. Mantenere il contesto dell’ultima cartella gestita distinguendolo dalla cartella effettivamente osservata.
- Ricerca per indizi: riusare Windows Search anche sui contenuti indicizzati e l’interpretazione GPT già collegata per estrarre indizi. Copertura dipende da indice, formato e impostazioni Windows. Non promettere comprensione semantica universale o contenuto ricercabile di qualunque file; dichiarare quando il fallback cerca soltanto nei nomi. Nessuna scansione completa residente.

## Impostazioni → Programmi, proposta
Elenco dei programmi rilevati dall’utente Windows corrente, con nome e stato. Due autorizzazioni indipendenti per riga: «Consenti apertura» e «Consenti chiusura». Nuove app rilevate non vengono abilitate automaticamente. Jarvis può mostrare un programma rilevato anche se le azioni sono disabilitate; vederlo non concede il permesso di eseguirlo. Aggiornamento dell’elenco a richiesta; memorizzare le scelte nel profilo, non nella cartella di installazione.

Per aprire riusare le identità di avvio di Windows: nome visualizzato associato a identità verificata. Non usare un percorso inventato o un comando GPT da eseguire. Registrazioni classiche, pacchetti Store e programmi realmente avviabili sono informazioni differenti; un portabile non registrato può richiedere aggiunta manuale successiva, da concordare. Non nascondere i limiti di rilevamento.

Per chiudere inviare una normale richiesta alla finestra identificata e consentita. Se l’app chiede di salvare, mostrare che attende una scelta e lasciare la decisione all’utente. Nessun taskkill/terminazione forzata, chiusura automatica di documenti o autorizzazione implicita a chiudere tutte le finestre con lo stesso nome.

Dubbio sostanziale da risolvere: chiusura limitata alle finestre avviate e identificate da Jarvis (raccomandazione iniziale), oppure anche finestre delle app consentite aperte manualmente dall’utente? Nel secondo caso mostrare quale finestra verrà chiusa e chiedere scelta se più finestre corrispondono. Un avvio può riusare una finestra preesistente: non attribuire proprietà in base al solo nome/PID.

## Ordine dei passi, dopo accordo
1. Consolidare risultati visibili e navigazione avanti/superiore con API Windows e il servizio file esistente; provare revoca, selezione, cambi manuali, ambiguità, cartella scomparsa e limiti di lettura.
2. Elenco programmi e spunte persistenti nel gestore impostazioni esistente; nessuna apertura prima di permesso. Usare nuova cartella add-on se serve una capacità separata, senza duplicare inventario o gestori.
3. Avvio e chiusura normale, identificazione della finestra, richieste di salvataggio e stato osservato distinti da semplice invio del comando.
4. Test Windows dei percorsi completi, poi proporre build soltanto su richiesta esplicita. Non passare da una fase fallita a una dipendente.

## Cosa è già reale e cosa manca
Candidato 7298fb6 sul PC: utente conferma elenco Documenti e lettura, ma segnala difetti voce, numeri, tipi e contesto. Correzione 755f988, run 41330559676: Windows PASS, 399 test per job, archivio estratto e avvio/chiusura PASS. Correzione installazione 950f655, run 41330921134: Windows PASS, query classiche/Store e chiarimento mantenuto. Queste esecuzioni sono terminate prima del nuovo divieto di build automatiche. Non sono test del microfono personale o del Minecraft installato sul PC. L’errore iniziale 41329991457 e la correzione sono documentati in ACCESSO-FILE-STATO.md.
Navigazione, contenuto indicizzato, impostazioni programmi e apertura/chiusura consentite: non consegnati. Bozza navigazione conservata in evidence/accesso-file-navigazione-BOZZA-20261101.patch, non applicata al runtime e non testata; non riusarla automaticamente.

## Fonti primarie verificate
Microsoft Learn: [Shell.Windows](https://learn.microsoft.com/en-us/windows/win32/shell/shell-windows), [ShellFolderView.Folder](https://learn.microsoft.com/en-us/windows/win32/shell/shellfolderview-folder), [GetForegroundWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getforegroundwindow), [Navigate2](https://learn.microsoft.com/en-us/previous-versions/aa752134(v=vs.85)), [FREETEXT Windows Search](https://learn.microsoft.com/en-us/windows/win32/search/-search-sql-freetext), [Get-AppxPackage](https://learn.microsoft.com/en-us/powershell/module/appx/get-appxpackage), [Get-StartApps](https://learn.microsoft.com/en-us/powershell/module/startlayout/get-startapps). Le API documentate non provano l’integrazione o il comportamento del Pavilion: occorrono prove Windows mirate prima di qualsiasi consegna.
