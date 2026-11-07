# JRV-AUD-014 — autodiagnosi dei moduli runtime

Stato: candidata in bozza, Green Windows ancora da eseguire. Base018
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
