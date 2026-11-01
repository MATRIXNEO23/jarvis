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

## 2026-11-01 — Add-on web e memoria di sviluppo: piano, non implementazione
**Richieste:** navigazione vocale autonoma con GPT esterno e motore locale, solo su richiesta, minimo carico sul Pavilion; add-on separate, UI semplice, reset configurazione e ritorno di versione; diagnostica leggibile e verifiche integrate. Prima di creare, discutere e pianificare per fasi.

**Prove:** letti addon_manager.py, addon_ui.py, self_diagnostics.py, diagnostic_session.py, runtime_diagnostics.py, diagnostic_handoff.py e punti diagnostici di jarvis.py nel ramo evoluto. Il gestore .jaddon ammette azioni descrittive limitate: l'esecuzione web richiede un adattatore revisionato. La diagnostica runtime attuale è passiva e non esegue test funzionali. Blob e limiti sono nel piano.

**Decisione e motivo:** proposta estensione Edge + add-on, per usare il browser esistente; non è ancora provata come soluzione più leggera o affidabile. Separare osservazioni passive, test locali con pagina controllata e collaudo reale GPT/browser. Non riutilizzare il precedente budget 1–2 GB come misura reale.

**Memoria persistente:** AGENTS.md ora impone lettura di handoff, registro e piano più verifica del codice prima delle modifiche; checkpoint di fase con fatti, motivazioni tecniche sintetiche, test/esiti e prossimo passo. Regola commit cf19eff734c7b85e81fa296f73b7b258d3aafc1c. Gli approcci falliti restano esclusi dai riferimenti raccomandati, con causa/lezione conservate.

**Risultato:** piano docs/PIANO-ADDON-WEB-E-DIAGNOSTICA-20261101.md creato nel commit 04c8bf86c3f39158f6dd14b8cd9cb1125a541d3a e aggiornato con checkpoint. Nessuna implementazione, nuovo workflow, prova funzionale o misura prestazionale. Conservare distinzione tra proposta e verifica.

## 2026-11-01 — Responsabilità nello sviluppo
**Richiesta e scelta:** l'utente non programma e vuole occuparsi delle decisioni di prodotto. L'assistente assume pianificazione, scelte tecniche motivate, realizzazione autorizzata, test e continuità; interventi manuali inevitabili sul PC guidati un passo alla volta. Regola aggiunta ad AGENTS.md e al piano web. Il piano è documentato, l'implementazione resta non avviata. Nessun nuovo test o workflow.

## 2026-11-01 — Continuità fra attività
L'utente richiede recupero dei progetti precedenti anche dopo un cambio di argomento. Creato docs/STATO-ATTIVITA.md nel commit d074634e96b584c1a1f339176ea22962108a357b, con fonti e punti di ripresa per web, dialogo e metodo. Regola in AGENTS.md: recuperare dati confermati, distinguere proposte/autorizzazioni/esecuzione, aggiornare checkpoint prima di sospendere. Solo documentazione: nessuna nuova funzione runtime o test.

## 2026-11-01 — Recupero iniziale e aggiornamento a ogni modifica
**Decisione:** RECUPERO.md come ingresso unico, creato nel commit aa1bce7e0f56ce4ede2258fe5e6742f14ded4186; AGENTS.md ne impone la lettura all'avvio e collega indice/handoff/lezioni/piano. Aggiornare continuità per ogni modifica e prima di sospendere, raggruppando edit correlati in checkpoint coerenti.
**Motivo:** recuperare fatti e autorizzazioni senza dipendere dal contesto della chat e senza ripetere lavoro o errori. Se una richiesta è incompatibile, proporre alternative motivate invece di seguirla alla cieca.
**Limite:** regole documentali verificate per presenza, non un test con una nuova istanza; la sessione deve avere accesso al repository. Nessun caricamento automatico garantito in chat esterna; nessun nuovo test runtime o implementazione web.

## 2026-11-01 — Handoff continuo, non a richiesta
Precisazione dell'utente: recupero necessario anche se la sessione termina all'improvviso. Regola in AGENTS.md e RECUPERO.md: checkpoint prima di ogni modifica coerente, subito dopo e dopo le verifiche. Stato «in corso» recuperabile confrontando codice/diff/commit. Non limitarsi al salvataggio di fine turno e non promettere che scritture interrotte siano persistite. Modifica solo documentale, nessun test runtime.

## 2026-11-01 — Prevenzione degli errori con revisione limitata
**Problema:** individuare incompatibilità solo alla build finale, oppure ripetere controlli senza un criterio di arresto.
**Decisione:** progetto basato su fonti reali, consultazione delle lezioni pertinenti, una revisione iniziale e un ricontrollo mirato delle correzioni. Una criticità bloccante residua richiede scelta o prova di fattibilità limitata; il numero di revisioni non autorizza a ignorarla. Dopo approvazione provare subito un percorso minimo completo e poi ampliare.
**Apprendimento operativo:** errore riprodotto → evidenza/causa o ipotesi → rimedio verificato → lezione preventiva e test di regressione quando utile. Riutilizzare solo nel contesto pertinente, senza ripetere tutte le verifiche del progetto.
**Ambito:** procedura salvata in AGENTS.md e piano web; non dimostra efficacia empirica o assenza di bug. Nessuna implementazione, nuova build o test runtime in questa fase.
