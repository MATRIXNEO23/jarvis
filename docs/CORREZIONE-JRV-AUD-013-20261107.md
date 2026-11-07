# JRV-AUD-013 — guide operative nel futuro pacchetto

Stato: verificata nei sorgenti in bozza; nessuna build. Source 970bcb17e15b9c197ec4fa5766eac6a6519058a6.
Base 012: 605c7056, [bozza53](https://github.com/MATRIXNEO23/jarvis/pull/53).

Il selettore ora ammette esattamente quattro guide: docs/VOCE_OFFLINE.md, docs/RECUPERO-IMPOSTAZIONI.md, file_access/LEGGIMI.md e program_apps/LEGGIMI.md. Sono anche obbligatorie: se mancanti o escluse, il futuro builder fallisce. Docs di sviluppo, handoff, test, tool, download storici e upstream restano esclusi. Nessun allargamento generale dei Markdown.

La guida voce ora distingue installazione manuale, modalità, preferenza di avvio e configurazione illeggibile. Il solo messaggio finale del BAT non promette più microfono sempre spento; nessun comportamento o preferenza viene cambiato. La versione storica è linkata al commit012. La guida Accesso file rimanda al registro tecnico via HTTPS immutabile, senza un rimedio locale verso un documento escluso.

Red1ed0200671de5a6f4eca128cbaf16bfe830019f6/run42378209746:911test/job5failure0errori, tutti i quattro subtest guide e il rimedio dell'installer. Python3.11.9 job128420097593139.441s; Python3.12.10 job128420097746192.454s. Gli altri test passano,022 passa e023 non osservato; Searchlive3.12 con servizio/fixture ripristinati.

Tre metodi nuovi eseguono il selettore reale viaAST e controllano inclusioni/esclusioni/rimedi/link relativi. Fixture012 aggiornata con le guide obbligatorie e guard sul raggiungimento degli asset nativi mancanti: writerZIP sempre vietato, nessun archivio creato o builder effettivo completato. Non si indeboliscono gli assert preesistenti. Sintassi/diff locali soltanto, nessun test funzionale Linux.

Build/estrazione vere e controllo delle guide dall'archivio restano non eseguiti fino ad autorizzazione. Nessun installer, download, DLL/GGUF/account/audio o dato utente utilizzato. Nessuna dipendenza o impostazione, main/merge/release/ZIP precedente modificato. Review readonly conferma selezione/esclusioni e chiede allineamento delle modalità al codice e del print installer modello: recepiti, AST/diff passano. Ricontrollo readonly completato senza blocchi; Green Windows completato come documentato sotto; prossimo 020: indice delle versioni. 016 resta una funzione distinta e 023 rimane aperto.

## Green Windows

Source 970bcb17e15b9c197ec4fa5766eac6a6519058a6, [run42378831525](https://github.com/MATRIXNEO23/jarvis/actions/runs/42378831525) SUCCESS tentativo1. Python3.11.9 job128421936403:911test in129.771s; Python3.12.10 job128421936166:911test in151.451s.0failure/errori/skip, tutti3nuovi metodi passati, controlli012 e022 preservati;023 non osservato. Sintassi/probe passati, Searchlive3.12 con ripristino servizio/fixture. Build/estrazione/artifact/publisher saltati. [Evidenza](evidence/jrv-aud-013-fix-20261107.json).

Review indipendente readonly e ricontrollo senza blocchi residui. Checkpoint finale solo documenti/evidenza, codice/test/guide da confrontare col sourceverde. Manifest selettivo e link verificati, archivio reale non costruito: controllo dall'estrazione ancora necessario quando autorizzato. Prossimo020 documentale da main, senza trasferimento del runtime.
