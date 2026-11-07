# JRV-AUD-004 — incastro lifecycle / richiesta file

Goal: disattivazione/rimozione/aggiornamento/revoca devono terminare insieme al controllo di un chiarimento file pendente, revocando selezioni e autorizzazioni. Base386fcd191659adf844cfa0d7711e8c2162162099, comprende001/002/003; ramo isolato e PR dipendente dalla36. Nessuna build/merge/configurazione personale.

Ipotesi: AddonManager.refresh tiene manager._lock mentre chiama FileAccessService.reset che prende files._lock; pending_clarification tiene files._lock mentre available→files_enabled prende manager._lock. install/set_enabled/remove chiamano refresh anche sotto il lock esterno. Il solo spostamento di reset fuori dal with interno non basta.

Scelta proposta dopo Red: i callback di consultazione del servizio file leggono uno snapshot pubblicato in blocco, senza riprendere il lock del lifecycle. _records viene già costruito ex novo e sostituito da refresh; nessuna modifica in-place dopo pubblicazione. Catturare un unico riferimento locale per files_enabled e file_descriptors; restituire copie dei descrittori. Mantiene l'attuale reset sincrono e la revoca prima del ritorno. Nessun nuovo thread, cache o dipendenza.

Alternative: estrarre refresh_locked e riprogettare tutti i lifecycle per reset esterno richiede più modifiche e controllo dei reset obsoleti dopo riattivazione; un unico lock condiviso serializza ricerca e metadati e può rallentare la UI. La lettura dello snapshot esistente elimina la sola dipendenza inversa dei callback file con una modifica mirata. Lo snapshot è una consultazione, mai un grant per un'azione: il servizio continua i suoi controlli di attivazione/policy/revisione/cancellazione.

- [ ] Red Windows: manager/servizio/lock/file veri, eventi ai callback per riprodurre l'intercalazione, processo figlio isolato per non appendere la suite. Quattro lifecycle: off, remove, upgrade, cancellazione ledger con refresh.
- [ ] Correzione minima dei callback snapshot; mantenere record immutabili dopo pubblicazione e copie dei descrittori. Nessun cambiamento schema/consensi su disco.
- [ ] Test significativi di revoca, nessun vecchio chiarimento/selezione dopo riattivazione, filtri per operazione e copie protette, preservazione dei file.
- [ ] Review indipendente in sola lettura; suite Windows3.11/3.12 e probe esistenti; continuità/evidenze remote con SHA e limiti.

Review focus: lock esterno dei lifecycle; callback che rientrano nel manager; lettura coerente della singola generazione; mutazione indiretta dei descrittori; revoca osservabile e vecchie selezioni dopo off/on. Recupero: ramo separato, nessun pacchetto distribuito o dato personale toccato. Stato: runtime invariato, Red da eseguire, rischio non ancora confermato in esecuzione.
