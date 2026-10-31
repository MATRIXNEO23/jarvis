# Decisioni e lezioni — Jarvis

## Regola del registro
Conservare le soluzioni riuscite come riferimenti entro il loro ambito verificato. Scartare quelle fallite dalle raccomandazioni, conservando la spiegazione tecnica del fallimento. Ogni nuova scheda indica data, stato (verificato, scartato, ipotesi o proposto), problema, decisione/motivazione, prove, commit/workflow e limiti. Gli stati non si confondono: la CI verde non dimostra la qualità del dialogo GPT.

## 2026-10-31 — CI dialogo: verificato
**Problema:** run 41230403859 e 41230414187 fallite. Tutti gli 8 log mostrano l'unico fallimento test_second_brain.py:26: 16 non è <=8.

**Decisione e motivo:** mantenere l'ampliamento intenzionale a 16 scambi e aggiornare il test al contratto nuovo. Tornare a 8 avrebbe annullato l'obiettivo della modifica; disabilitare il test avrebbe nascosto il problema. La regressione ora verifica anche contenuto, ordine, espulsione e budget, non soltanto la dimensione.

**Prove:** prima della patch 373 test locali, un fallimento identico alla CI; dopo 373 OK (5 Windows saltati in Linux). Commit faba67363e07ea478241fbe549c45474aab5144a sul ramo feature/timer-settings-ui-20261031. Run https://github.com/MATRIXNEO23/jarvis/actions/runs/41232983494 SUCCESS: quattro job Linux/Windows, Python 3.11/3.12, 373 test ciascuno; Windows nessuno skip, Linux 5 skip. Sintassi e parser PowerShell PASS.

**Limite:** non risolve i difetti della pipeline di memoria e non prova il dialogo reale con GPT. Nessun pacchetto pubblicato.

## 2026-10-31 — Aumento dei limiti come soluzione sufficiente: scartato
**Errore da evitare:** considerare 16 turni RAM/2400 caratteri come prova di continuità migliore.

**Causa:** jarvis.py richiede solo 860 caratteri, poi il router riduce fino a 850 o allo spazio residuo; la capacità di archivio non è il contenuto consegnato al modello. Cinque turni medi si riducono a due nella riproduzione locale. Il percorso permanente.recent non è letto dal compattatore finale.

**Lezione applicabile:** verificare il payload finale del client e il recupero dopo riavvio. Non aumentare indiscriminatamente i limiti e non considerare i test dei singoli moduli una prova dell'intero flusso. Correzione del nucleo proposta, ancora da approvare.

## 2026-10-31 — Archify: verificato parzialmente
**Decisione:** usarlo da main contro checkout separato dei sorgenti evoluti 1f7310f; così la mappa rappresenta il codice effettivamente esaminato.

**Prove:** docs/architecture-20261031/jarvis.html e candidato/ricevuta su main. Validate, deliver e check PASS. Browser-check saltato perché Chrome/Chromium assente; finalize codice 2. Non dichiarare riuscita completa o ispezione visiva.

**Lezione:** distinguere integrità/fonti dell'artefatto, controllo browser e collaudo dell'app. Nessuna dipendenza Archify aggiunta al runtime.

## 2026-10-31 — Correzione del nucleo: verifica locale completata
**Autorizzazione:** piano approvato dall'utente con «Sì» nella continuazione della sessione.

**Decisione e motivazione:** raccogliere i record senza budget intermedi, selezionarli una volta nel prompt finale, recuperare SQLite e conservare la domanda finale. Il confronto tra vecchio e nuovo payload dimostra il problema del doppio taglio; aumentare solo la RAM non lo corregge. Nessun modello aggiuntivo o add-on. Dettagli in CORREZIONE-NUCLEO-DIALOGO-20261031.md.

**Prove locali:** 386 test OK, skipped=5; 13 nuovi test anche sui callback reali voce/testo fino alla chiamata client. Sintassi e diff PASS. In attesa di CI Windows/Linux e smoke Windows senza login; non dichiarare ancora collaudo GPT/Pavilion o pacchetto pronto.

**Tentativi scartati e lezioni:** conteggio con len Python insufficiente per emoji/escaping, corretto con unità UTF-16 come Node; domanda finale con prefisso residuo dopo salvataggio, corretto il separatore. Entrambi i casi ora hanno test di regressione. Non eliminare i vecchi log diagnostici.

**Microfono:** inizializzazione in standby senza sovrascrivere una scelta manuale; impostazioni salvate conservate, rimosso solo l'effetto della migrazione che riabilitava auto_listen. Il controllo della vecchia opzione automatica è sospeso in UI.
