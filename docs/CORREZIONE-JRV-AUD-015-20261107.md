# JRV-AUD-015 — tempo della ricerca tra indice e scansione

Stato: verificata nei sorgenti in bozza; nessuna nuova build installabile. Source `bd722353fce33a38647e102778eb585579cb428e`.
Base014 `4f436630b3aae935c808b13e798c9b8991fdedc8`, [bozza48](https://github.com/MATRIXNEO23/jarvis/pull/48).
[Specifica](superpowers/specs/2026-11-07-jrv-aud-015-design.md), [piano](superpowers/plans/2026-11-07-jrv-aud-015-fix.md).

## Causa dimostrata

Il servizio passava attraverso tutte le radici autorizzate, con un timeout indice di8s per ogni radice. Solo dopo iniziava un nuovo budget di10s per la scansione diretta. La durata teorica si sommava con il numero di radici; il limite200regole è reale, i1600s dell'audit sono un calcolo teorico e non una misura sul PC.

## Correzione e compatibilità

Un'unica deadline monotona nella fase indice/scansione e il timeout residuo al wrapper Windows esistente. Nessun nuovo indice persistente016, processo residente, dipendenza, modifica delle spunte o deduplicazione delle radici che potrebbe perdere una reinclusione. Le callback iniettate legacy a due argomenti restano supportate, senza ripetere una richiesta dopo TypeError.

Gli esiti indicizzati validi restano disponibili; quando manca tempo, il riepilogo dichiara una ricerca parziale e stop_reason=time_limit. Con indice vuoto/rapido, la scansione usa il residuo, senza ricaricare10s. Revoca/annullamento scartano i risultati. Restano20risultati/5000voci, controllo reparsepoint, progressi non vocali e selezione numerica.

## Prove ed esiti

Red1 `82379bfe793aa35938542408ff007a7cc5e02903`, [run42358971980](https://github.com/MATRIXNEO23/jarvis/actions/runs/42358971980), quindici metodi nuovi,867totali attesi. Runtime ancora014 nel Red. Esito FALLITO:867test per job,10failure/0errori, tutti nel nuovo015. Python3.11.9 job128363078992 in192.808s, Python3.12.10 job128363079143 in181.795s. Le prove mostrano timeout8s ripetuti, avvio di scansione oltre deadline, copertura dichiarata erroneamente completa e tre directory vuote visitate invece di una. Nessun022/023 osservato. La candidata ora modifica solo file_access/service.py;17metodi nuovi con i due gap di review aggiunti dopoRed, senza altroRed rivendicato. Green documentato sotto.

Review preventiva indipendente readonly ha chiesto un caso TypeError interno per escludere doppie richieste e un risultato acquisito dal fallback prima della scadenza e ancora selezionabile. Aggiunti entrambi dopo il primo source Red, senza rivendicare un altro Red:17nuovi/869attesi nella candidata. Prove sul servizio/add-on e file temporanei reali; orologio/subprocess/iterazione controllati. Nessun account, microfono o file personale. Nessuna esecuzione funzionale Linux; AST/diff locali soltanto.

## Limiti e recupero

Non è un hard timeout: avvio del processo, risoluzione/validazione percorsi e I/O possono ritardare il ritorno; una callback legacy non cooperativa non viene terminata. Il wrapper subprocess esistente gestisce il proprio helper scaduto, nessun processo estraneo. Rilevamento Known Folders/policy e registrazioni delle installazioni precedono il budget indice/scansione. Nessun benchmark Windows10/i3/HDD e nessuna prova sul pacchetto estratto.022/023 restano aperti indipendentemente da questa verifica.

Ramo separato e reversibile `fix/jrv-aud-015-search-deadline-20261107`, nessun merge/main/ZIP/release o dato utente modificato. Ripristino del comportamento tramite ritorno alla014 nel ramo di sviluppo, senza cancellare profilo, cronologie o pacchetti precedenti.

Review runtime indipendente readonly completata: nessun rilievo bloccante individuato, con entrambi i gap test recepiti. La review è statica e non sostituisce il Green Windows.

## Green Windows e consegna

[Run42359421674](https://github.com/MATRIXNEO23/jarvis/actions/runs/42359421674) SUCCESS sulla prima candidata runtime, source `bd722353fce33a38647e102778eb585579cb428e`. Python3.11.9 job128364417473:869test in126.668s; Python3.12.10 job128364417195:869test in130.805s. Zero failure/errori/skip, tutti17nuovi metodi passati. Nessun022/023 osservato, che restano aperti: non sono dichiarati corretti da un run senza riproduzione.

Sintassi Python/JavaScript/PowerShell e probe nativo passati. Windows Search live sul job3.12: ricerca file/cartelle, ambito, rename/delete passati; servizio ripristinato e fixture rimossa. Questa prova reale del wrapper è distinta dalla simulazione delle attese nel servizio. Build, estrazione, artifact e publisher saltati. Nessun test funzionale Linux.

[JSON evidenza](evidence/jrv-aud-015-fix-20261107.json) conserva Red/Green, ambiente e limiti. Checkpoint finale soltanto documenti/evidenze; runtime/test devono coincidere con i blob del source verde prima di dichiarare il passaggio conservato. Prossimo017: stato HUD dell'elaborazione Gemma, senza creare/caricare il modello per leggere un indicatore.
