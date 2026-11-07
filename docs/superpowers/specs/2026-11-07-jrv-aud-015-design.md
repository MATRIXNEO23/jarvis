# JRV-AUD-015 — una scadenza per indice e scansione

Base verificata014 `4f436630b3aae935c808b13e798c9b8991fdedc8`. L'utente autorizza correzioni mirate e conservative. Nessuna build, nuovo indice, modifica dei permessi o dato personale.

## Evidenza e intervento minimo

`FileAccessService._search_impl` interroga tutte le radici con timeout fisso di8s ciascuna e solo dopo avvia un nuovo budget di10s per la scansione. Il tempo teorico cresce con le radici; non è una misura sul PC dell'utente. `indexed_candidates` accetta già un timeout: riusarlo con il tempo residuo, senza processi o dipendenze nuovi.

Una deadline monotona all'inizio della fase indice vale anche per la scansione successiva. Non cambiare la precedenza delle radici o eliminare radici sovrapposte: possono rappresentare reinclusioni dopo esclusioni. Prima di ogni interrogazione e ingresso in directory verificare tempo e revoca. Il timeout dell'indice di produzione è min(8s, residuo). Mantenere il protocollo a due argomenti degli adattatori iniettati esistenti, senza tentare due volte una chiamata dopo TypeError.

Risultati validi già ricevuti restano selezionabili, entro20 e nei permessi. Scadenza significa copertura parziale/time_limit, visibile nel riepilogo anche con risultati dell'indice. Revoca/annullamento prevalgono: nessun risultato esposto. Indice rapido/vuoto lascia il residuo alla scansione; niente budget nuovo. Restano5000voci, esclusione reparsepoint, progressi non vocali e raffinamento esistente.

Il budget comprende le fasi indice/scansione, non il precedente rilevamento Known Folders/policy né la localizzazione nelle registrazioni Windows. Non è un limite rigido di wall clock: avvio processi, I/O/validazione filesystem o callback iniettata non cooperativa possono ritardare il ritorno. Nessuna terminazione forzata di thread o processo estraneo. Il wrapper subprocess esistente gestisce il proprio helper al timeout.

## Prove

Windows2022/Python3.11 e3.12, suite unittest esistente. Nuove prove sul servizio/add-on reali e filesystem temporaneo; orologio e risposta subprocess controllati, wrapper Windows reale senza avviare PowerShell per simulare lentezza. Limite globale multiradice, residuo al fallback, timeout singolo massimo, risultati tardivi ammessi, esclusioni, annullamento/revoca, callback a due argomenti, limiti risultati/voci e directory vuote. Nessuna misura prestazionale sul Pavilion o prova Windows10/HDD; probe Windows Search live esistente distinto.
