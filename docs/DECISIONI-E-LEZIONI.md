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

## 2026-10-31 — Nucleo dialogo: soluzione verificata automaticamente
**Autorizzazione:** piano approvato con «Sì». Commit a86c2c932af988b23916e8d4495025de5ee0a730 sul ramo evoluto, nessun add-on o API aggiuntiva.

**Scelta e motivo:** raccolta locale senza tagli intermedi, recupero recenti SQLite, domanda pendente preservata e una sola selezione nel prompt finale. Le prove dimostravano che la capacità RAM non equivale al contesto ricevuto dal modello. Limite invariato 5000 unità UTF-16; cataloghi opzionali subordinati alla memoria. Timeout testo breve allineato alla voce. Standby all'avvio senza cambiare le modalità manuali e senza riscrivere preferenze salvate.

**Prove:** 386 test per ognuno dei quattro job Windows/Linux, Python 3.11/3.12 nella run 41236238213 SUCCESS (Linux 5 skip Windows-only, Windows nessuno). Smoke reale bridge/SDK Windows senza login run 41236238208 SUCCESS. Le 13 nuove regressioni coprono riavvio, dieci turni, payload effettivo dei callback voce/testo, cataloghi, Unicode, isolamento e assenza replay.

**Errori scartati:** primo conteggio con len Python insufficiente per emoji/escaping, corretto con unità UTF-16; prima conservazione della domanda finale produceva un prefisso residuo, corretto il separatore. Entrambi restano nei test per evitare ricadute. Non promuovere tentativi precedenti a riferimenti.

**Limiti:** collaudo GPT/Pavilion non eseguito, nessun pacchetto distribuito. Archify aggiornato: tre gate PASS, browser-check assente per Chrome mancante. Il dedup confronta solo prefissi disponibili nei vecchi archivi; i dati già troncati non si ricostruiscono. Dettagli e piano di collaudo in CORREZIONE-NUCLEO-DIALOGO-20261031.md.


## 2026-11-01 — Dialogo reale: riscontro positivo riferito dall'utente
**Prova disponibile:** Alberto riferisce durante uso reale che Jarvis «mantiene abbastanza il contesto» ed è «molto migliorato».

**Decisione e motivo:** registrare un miglioramento percepito nell'uso reale, distinguendolo dai test automatici e da un collaudo completo. Il feedback aggiorna la precedente mancanza di riscontri pratici; non prova da solo tutte le regressioni.

**Limiti:** versione/SHA sul PC non verificato, nessuna misura del numero di turni o ispezione dei prompt. Non attribuire automaticamente il risultato al commit a86c2c9; riavvio, progetti, salvataggi e microfono restano da collaudare. Nessun nuovo test o pacchetto in questa fase. Dettagli nel handoff, sezione 2026-11-01.
