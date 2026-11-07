# JRV-AUD-004 — incastro lifecycle / richiesta file

Goal: disattivazione/rimozione/aggiornamento/revoca devono terminare insieme al controllo di un chiarimento file pendente, revocando selezioni e autorizzazioni. Base386fcd191659adf844cfa0d7711e8c2162162099, comprende001/002/003; ramo isolato e PR dipendente dalla36. Nessuna build/merge/configurazione personale.

Ipotesi: AddonManager.refresh tiene manager._lock mentre chiama FileAccessService.reset che prende files._lock; pending_clarification tiene files._lock mentre available→files_enabled prende manager._lock. install/set_enabled/remove chiamano refresh anche sotto il lock esterno. Il solo spostamento di reset fuori dal with interno non basta.

Scelta finale dopo Red e ulteriore verifica dei permessi: mantenere il lock transazionale nei callback. Separare refresh dei record e reset file; una guardia comune dei lifecycle rilascia il lock esterno prima di chiamare reset, anche su return/eccezione. FileAccessService.reset(only_if_inactive=True) ricontrolla attivazione sotto il lock del servizio, evitando reset obsoleti dopo riattivazione. ProgramService.reset attuale non prende lock ed è conservato nella transazione originale, senza modifiche. Nessun nuovo thread, cache o dipendenza.

Alternativa iniziale scartata PRIMA di implementarla: callback senza lock sullo snapshot dei record. Durante una transazione di revoca ancora in I/O leggerebbero il vecchio enabled=True invece di attendere la pubblicazione, indebolendo la garanzia dei permessi. Un unico lock condiviso serializzerebbe ricerca e metadati e può rallentare la UI. Non basta spostare reset fuori dal with interno di refresh: install/set_enabled/remove mantenevano un lock esterno. La guardia comune copre tutti questi percorsi e conserva i controlli sincroni esistenti.

- [x] Red Windows: manager/servizio/lock/file veri, eventi ai callback per riprodurre l'intercalazione, processo figlio isolato per non appendere la suite. Quattro lifecycle: off, remove, upgrade, cancellazione ledger con refresh. Run42331515560/job128278876066:692 test, quattro fallimenti comportamentali, nessun errore; entrambi i thread ancora bloccati dopo join, confini raggiunti.
- [x] Correzione mirata: guardia lifecycle e refresh record separati dal reset file fuori lock; ricontrollo condizionale sotto lock del servizio. Nessun cambiamento schema/consensi su disco.
- [ ] Test significativi di revoca, nessun vecchio chiarimento/selezione dopo riattivazione, filtri per operazione e copie protette, preservazione dei file.
- [ ] Review indipendente in sola lettura; suite Windows3.11/3.12 e probe esistenti; continuità/evidenze remote con SHA e limiti.

Review focus: lock esterno dei lifecycle; callback che rientrano nel manager; permessi durante una transazione; reset differito dopo riattivazione; mutazione indiretta dei descrittori; revoca osservabile e vecchie selezioni dopo off/on. Recupero: ramo separato, nessun pacchetto distribuito o dato personale toccato. Stato: Red confermato, candidata implementata, Green e review pendenti. Non eseguiti test funzionali Linux.
