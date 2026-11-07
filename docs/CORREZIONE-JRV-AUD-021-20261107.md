# JRV-AUD-021 — fermare il solo helper della voce

Stato: candidata implementata/revisionata, Green Windows da acquisire. Nessuna build.
Base019 `e059883a1e446ca71452a2358920b4af02001b69`, [bozza51](https://github.com/MATRIXNEO23/jarvis/pull/51).
[Specifica](superpowers/specs/2026-11-07-jrv-aud-021-design.md), [piano](superpowers/plans/2026-11-07-jrv-aud-021-fix.md).

## Causa e correzione minima

close impostava l'evento e svuotava la coda senza possedere il processo di subprocess.run in corso. Il chunk vocale poteva continuare dopo la chiusura della UI fino alla sua fine/timeout90s. Essere daemon non certifica l'uscita del figlio Windows.

Solo offline_tts.py cambia nel runtime: il runner vocale predefinito ora conserva il proprio Popen. Lock breve per pubblicazione/rimozione per identità e snapshot di close; creazione, communicate, termine/attesa fuori dal lock. Close terminale/idempotente ritira quel solo handle, senza cercare processi per nome/PID o toccare altre app. La coda è scartata e una creazione ancora in corso, pubblicata dopo close, viene ritirata senza inviarle il testo.

Riferimento posseduto visibile fino alla fine della pulizia; pipe gestite dal context manager anche su errore. Timeout/errore communicate non vengono sostituiti da un errore secondario di kill: nota diagnostica generica sull'eccezione primaria. Se Windows rifiuta la terminazione, il worker può attendere l'uscita effettiva: non si promette un hard deadline oltre il sistema operativo. La UI non aspetta la fine del worker, il fallimento di terminate viene segnalato tramite il canale errori esistente.

installed_voices conserva subprocess.run finito. Runner custom(payload, timeout=...) compatibili; non vengono terminati forzatamente. Busy/cooldown non azzerati prima dell'uscita, protezione anti-eco invariata. Restano JSON su stdin, script/argv fissi, cwd SystemRoot,3messaggi in coda,2800caratteri per messaggio e600per chunk. Nessun nuovo mute/checkbox o modifica del microfono.

## Red e review

SourceRed `556a4b4460287fb41f0bf7e7c1d080c6b81ec993`, [run42362426651](https://github.com/MATRIXNEO23/jarvis/actions/runs/42362426651) FALLITO:897test per job,6failure0errori tutti nel nuovo021. Python3.11.9 job128373412696144.361s; Python3.12.10 job128373412895196.734s. Figlio/worker vivi dopo close, incluso il caso prima della pubblicazione. Baseline precedente passa; nessun022/023, Searchlive3.12 passato con servizio e fixture ripristinati. Nessun risultato audio reale dedotto dai test.

Review indipendente readonly rafforza latenza e cleanup: tutte le close nei test/teardown tramite chiamante bounded, worker trattenuto dopo communicate deve restare busy mentre close è già tornata; terminateOSError non blocca le altre fasi. Cleanup ritira tutti i figli e unisce i worker anche dopo errori per risorsa; marker JSON pubblicato atomicamente. Review runtime rileva kill capace di mascherare l'eccezione iniziale: corretto e aggiunto metodo con due subtest pipe-error/timeout+killfallita.16nuovi/900attesi,3metodi aggiunti dopo il primo sourceRed, nessun extraRed rivendicato. Ultimo ricontrollo indipendente senza blocchi individuati; Green Windows necessario.

## Verifiche e limiti

Popen/pipe/processi Windows reali, helper Python silenzioso temporaneo al posto dell'eseguibile PS intercettato alla sola frontiera Popen. Processo estraneo separato controllato; nessun SAPI/audio, account, microfono o profilo personale. AST/diff locali soltanto; nessuna esecuzione funzionale Linux. Nuove prove non certificano suono, latenza Windows10/i3/HDD o pacchetto estratto.022/023 restano aperti. Nessuna dipendenza o impostazione modificata.

Ramo isolato reversibile `fix/jrv-aud-021-owned-tts-20261107`, nessun main/merge/build/ZIP/release o cancellazione di dati/versioni precedenti. Recupero tramite ritorno alla019 nel ramo di sviluppo. Prossimi012/013: coerenza dei sorgenti e guide nel futuro pacchetto;020 indice repository;016 distinta come funzione incompleta,022/023 da verificare causalmente.

## Prima verifica candidata: parziale, blocco022

Source6504abffe/run42363252951:3.11job128375837812 passa900test in172.068s (tutti16nuovi021).3.12job128375837908 abortisce conTcl_AsyncDelete durante DocumentSaveRace, prima dei021; nessun riepilogo completo assegnato. Errore022 già storico, causa di ownershipTk da investigare senza attribuirla alla voce. Searchlive3.12 passato con ripristino. Green completo021 non dichiarato, nessun retry cieco; specifica/piano022 e regressione controllata avviati nella stessa bozza per sbloccare il collaudo, runtimeTTS invariato.
