# JRV-AUD-012 — parità dei sorgenti Python nel futuro pacchetto

Stato: verificata nei sorgenti in bozza; nessuna build/ZIP dell'app.
Base021/022 `8626d193ef33ddc141f9c1ef1bce3decb0388185`, [bozza52](https://github.com/MATRIXNEO23/jarvis/pull/52).

Il builder riscriveva native_ui/native_factory dopo la suite principale. La prova Gemma e il fallback della DLL bundled esistevano solo nel codice trasformato, con copertura parziale successiva. Ora quei moduli contengono esattamente il comportamento già generato: confronto statico del testo con le sostituzioni/literal della base positivo. Nessuna riscrittura Python nel builder. Il launcher del pacchetto conserva Jarvis-Gemma-Trial; launcher sorgente/profili/dati invariati. Due helper test copiano direttamente i moduli, senza indebolire le asserzioni precedenti.

Il futuro workflow registra gli hash dei filePY/MJS/PS1 tracciati prima del builder e rifiuta differenze dopo. Controlla separatamente exitcode builder, py_compile e unittest, evitando che un successo successivo nasconda un errore. Il processo futuro di estrazione resta necessario prima della pubblicazione.

## Evidenza prima della correzione

SourceRed1af0f654cdea500b5099ad98b4026509e868f3e6, run42377060724:907test/job,4failure1errore tutti nel nuovo012. Python3.11.9 job128416727551170.282s; Python3.12.10 job128416727411157.150s. L'errore è il vero fallbackDLL assente nel rawfactory, non una fixture illeggibile. Fallimenti: UI assente nei sorgenti, mutazione Python, accettazione script alterati e builder fallito coperto da comandi successivi.022 passa,023 non osservato; Searchlive3.12 passa con servizio e fixture ripristinati.

Review preventiva rafforza il raggiungimento di git ls-files prima dell'assert pre-ZIP (evita falso verde), hostpwsh uguale al workflow, mutazioni su tutte tre le estensioni e fallimento py_compile seguito da unittest positivo.7nuovi/908attesi,1metodo e rafforzamenti successivi al primo sourceRed, nessun altroRed rivendicato. Review runtime indipendente readonly completata senza rilievi bloccanti; Green Windows ancora necessario.

## Prove senza build

Builder reale in directory temporanea, assets nativi volutamente assenti e writerZIP vietato da stub; nessun archivio può essere creato. Blocchi PowerShell reali del workflow in Git temporaneo, con comando python sostituito da stub innocuo. Trial/factory reali dai sorgenti con ABI controllata e DLL/GGUF fittizi mai caricati. Letture/AST/diff locali soltanto, nessun test funzionale Linux.

Queste verifiche non sono una build o estrazione del pacchetto finale. Restano da eseguire, dopo autorizzazione: ripristino DLL pin/hash, build su Windows, hash prima/dopo, estrazione pulita, prove del pacchetto e caricamento reale DLL. Windows10/i3/HDD, audio/modello/account reali non verificati. Nessuna dipendenza o dato utente modificato; nessun merge/main/release o vecchio ZIP alterato.013 guide e020 indice sono separati,016 nuova funzione distinta e023 ancora aperto.

## Green Windows

Source `a95cbd2884afe1079774419bedabf2f324d1a611`, [run42377581328](https://github.com/MATRIXNEO23/jarvis/actions/runs/42377581328) SUCCESS al tentativo1. Python3.11.9 job128418236381:908test in119.730s; Python3.12.10 job128418236628:908test in137.421s. Zero failure/errori/skip, tutti7nuovi metodi passati. Provati su pwsh sia la parità PY/MJS/PS1 sia lo stop per builder/compile falliti. Source UI/factory passano direttamente e i test precedenti restano verdi.022 passa,023 non osservato.

Sintassi Python/JavaScript/PowerShell e probe nativo passati, Searchlive3.12 passato con servizio e fixture ripristinati. Build/estrazione/artifact/pubblicazione saltati. [Evidenza](evidence/jrv-aud-012-fix-20261107.json). Checkpoint finale solo documenti/evidenza;7file di codice/test/workflow da confrontare col sourceverde prima della consegna remota. La build/estrazione vera resta non eseguita, non viene dichiarata superata.
