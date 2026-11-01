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
