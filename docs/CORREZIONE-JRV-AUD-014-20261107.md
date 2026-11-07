# JRV-AUD-014 — autodiagnosi dei moduli runtime

Stato: verificata nei sorgenti in bozza, nessuna nuova build installabile.
Sourceverde `d74333ebe09182a8d3aa84f571fc664be405e51f`, [evidenza](evidence/jrv-aud-014-fix-20261107.json). Base018
`76e392f80eb7b1d1f43921f101eb1180cb54f76a`, [bozza47](https://github.com/MATRIXNEO23/jarvis/pull/47), ramo `fix/jrv-aud-014-diagnostic-inventory-20261107`.
Conservate001–011 e018; gli altri ID restano distinti.
[Specifica](superpowers/specs/2026-11-07-jrv-aud-014-design.md), [piano](superpowers/plans/2026-11-07-jrv-aud-014-fix.md).

## Causa e correzione minima

`_source_list` esaminava soltanto radice e tests. Nessun file nelle quattro
cartelle runtime entrava nel controllo AST o nelle raccomandazioni. Inoltre il
reviewer leggeva metadati fuori dal blocco che gestisce errori: un file sparito
o diventato illeggibile poteva interrompere tutta la diagnosi.

|Componente|Modifica|Vincoli preservati|
|---|---|---|
|self_diagnostics.py/_source_list|Ricorsione nelle sole quattro cartelle approvate, runtime prima dei test, esclusione del dataRoot prima di enumerare|140file e260000byte invariati;140directory come budget aggiuntivo per alberi vuoti, niente scansioni di drive o profili|
|source_review.py/metadata e review_sources|Criteri di esclusione condivisi; lstat, controllo degli antenati dalla radice e contenimento fisico prima della lettura; errori di metadata/read gestiti|Nessun import/exec/upload; link, junction e Hidden Windows rifiutati sotto la radice, anche con target interno|
|self_diagnostics.py/inspect_jarvis|Note di copertura nel dettaglio, oltre alle prime8osservazioni; modulo non trovato qualificato come assente dall'inventario accessibile|Limite visibile anche con molti errori; comandi e selettore semplice invariati, nessuna falsa prova di assenza fisica|

Inventario Git della base:61Python nella radice e29nelle cartelle runtime,
90in totale più gli script. Nessuna necessità dimostrata di aumentare i limiti.
Un test sul checkout reale controlla che i Python attuali delle quattro cartelle
entrino nell'inventario; i casi sintetici coprono anche sottocartelle e limiti.

## Red e review

Comando `python -m unittest discover -s tests -v`, Windows2022 x64.

|Fase|Source/run|Python/job|Esito|
|---|---|---|---|
|Red1|1d69632f7cb0fa355add17f681450ed95b0e85a6 /42355483101|3.11.9/128352529225|844test,14failure+2errori,154.869s|
|Red1|stesso|3.12.10/128352529347|844test,14failure+2errori,142.961s|
|Red2|4ec1a9f88f730a3fc06e53f6b7934cbe2b461546 /42355703061|3.11.9/128353233323|846test,16failure+2errori,141.023s|
|Red2|stesso|3.12.10/128353233067|846test,16failure+2errori,207.049s|

Tutti i fallimenti nei nuovi controlli014. Due errori sono metadati/file sparito
realmente non gestiti, non fixture difettose. Junction Windows create, nessuno
skip nei Red;022/023 non osservati e ancora aperti.

Review preventiva: aggiunti target junction interni e spy contro enumerazione
del profilo quando dati e codice coincidono. Review runtime: corrette due
lacune della candidata, limite nascosto da molti errori e Hidden Windows non
riconosciuto. Cinque test aggiunti dopo Red2: directory budget, IO+limite,
attributo Hidden reale, modulo oltre limite e checkout reale. Nessun Red
separato rivendicato per questi cinque;22nuovi metodi/851attesi.

La vecchia asserzione di testo «non è presente» è aggiornata intenzionalmente
al riferimento all'inventario accessibile, mantenendo il caso di file davvero
assente e nessun consiglio inventato. Ricontrollo indipendente senza blocchi
residui; revisore in sola lettura, nessuna esecuzione funzionale indipendente.

## Prima candidata: fixture Windows8.3 da correggere

Sourcef423fdb6/run42357007265 FALLITO:851test,1failure+8errori per job.
Python3.11.9/job128357180996133.861s e3.12.10/job128357181094124.005s.
Il TEMP delle fixture usava RUNNER~1 mentre il runtime canonizzava correttamente
in runneradmin: i confronti relative_to e alcuni spy erano incoerenti. Nessun
022/023 riprodotto. Non vengono dichiarati nove nuovi bug del programma.

Fix della sola fixture: radice canonicalizzata dopo creazione, assert conservati,
contatore che prova l'effettivo errore di metadata, caso reale GetShortPathNameW
per verificareAPIpubblica anche conalias8.3 e dati esclusi.23nuovi/852attesi;
runtime invariato, Green2 da acquisire, nessun semplice retry del source fallito.

## Green Windows dopo la correzione della fixture

Source `d74333ebe09182a8d3aa84f571fc664be405e51f`,
[run42357790841](https://github.com/MATRIXNEO23/jarvis/actions/runs/42357790841)
SUCCESS al tentativo1 del nuovo source. Non è un retry identico: il fallimento
della fixture rimane documentato, runtime invariato e assert rafforzati.

|Python/job|Esito suite completa|
|---|---|
|3.11.9/128359597362|852test,0failure/errori/skip,121.214s; tutti23nuovi metodi passati|
|3.12.10/128359597262|852test,0failure/errori/skip,149.326s; tutti23nuovi metodi passati|

Sintassi Python/JS/PS e probe file passati in entrambi; Searchlive3.12 passata
con servizio/fixture ripristinati. Build, estrazione e pubblicazione skipped.
Nessun022/023 riprodotto: non sono dichiarati risolti. Le prove con junction,
Hidden Windows e nomi brevi8.3 sono effettivamente passate, senza skip.

Verificata copertura delle quattro cartelle del checkout reale e dei moduli
annidati nelle fixture. Inventario di base:100sorgenti runtime nelle estensioni
ammesse (68radice+32pacchetti, includendo90Python), prima dei test. Test con
limiti di file/directory/byte, molti errori e messaggi visibili; profili e
cartelle collegate non enumerati/letti, literal privati non riportati e marker
mai eseguito. Metadata/file sparito non interrompono gli altri controlli.
Nessuna asserzione indebolita per ottenere Green.

Checkpoint finale solo docs/evidenze; runtime/test identici al source verde.
Riferimenti: self_diagnostics.py/_source_list56 e inspect_jarvis189;
source_review.py/metadata24 e review_sources77 (righe soggette a successivi
aggiornamenti, funzioni identificate). Consigli statici richiedono sempre
riproduzione: queste prove non certificano inferenza, hardware o assenza di bug.

## Limiti e recupero

Non è un analizzatore universale o una certificazione di assenza di bug.
Directory escluse e cap possono lasciare sorgenti non esaminati; i limiti sono
dichiarati. Non modifica grammatica, selettore modulo, autorizzazioni, microfono,
modello GPT o dati. Nessuna nuova dipendenza, persistenza o attività residente.

Prove solo su Windows CI con fixture e codice del checkout, senza leggere dati
personali. Nessun test funzionale Linux, hardware Windows10/i3/HDD, account,
microfono o pacchetto estratto. Non garantisce una sandbox contro sostituzioni
malevole concorrenti del filesystem. Nessuna build/ZIP/merge/release o modifica
di profili reali. Ramo e bozza reversibili, versioni e dati conservati.
