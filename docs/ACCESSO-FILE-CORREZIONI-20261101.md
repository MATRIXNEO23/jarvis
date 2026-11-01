# Correzioni Accesso file dopo prova PC — 2026-11-01

Stato in corso. Candidato installato dall’utente: 7298fb6. Elenco Documenti e lettura testo osservati dall’utente; non collaudo completo. Difetti riferiti: elenco pronunciato integralmente, numeri detti in lettere non risolti, richiesta Cartella applicata a File, ricerca installazione e obiettivo perso dopo chiarimento. Nuovo requisito: proseguire nelle sottocartelle e riconoscere il contesto Esplora file anche dopo navigazione manuale. Nessun percorso privato pubblicato.

Passo 1: sorgenti 83fc6d0, run Windows 41329991457 fallita (399 test; 2 errori e 2 fallimenti), pubblicazione bloccata. Causa runtime dimostrata: esempio «elenca cartella» richiedeva erroneamente articolo «la». Errore distinto della fixture del callback: dipendenza runtime_events assente. Correzione 755f988, run 41330559676 in corso. Nessun nuovo test Linux. Liste in chat e riscontri vocali separati; numeri italiani e tipo esplicito controllati localmente; non implementata interruzione vocale generale.

Passo 2: correggere «cerca cartella di installazione» perché non diventi query letterale e conservare un solo obiettivo pendente dopo domanda di chiarimento, revocato a scadenza/cambio argomento/progetto/disattivazione. Nessuna correzione arbitraria Minecraft/Microsoft senza trascrizione. Localizzazione attuale legge registrazioni Uninstall: non garantisce tutte le installazioni Store o gestite da launcher.

Passo 3: stato di navigazione nel servizio già presente; contenuto della cartella aperta in chat con nuovo elenco numerato. Per cartella effettivamente a schermo usare API Windows/Shell a richiesta, senza OCR o monitoraggio residente; ambiguità fra finestre/schede va dichiarata, non scegliere una cartella inventata. Funzioni Windows documentate da Microsoft, integrazione ancora da verificare su Windows.

Sorgenti feature/file-access-20261101; main radice storica preservata. Build nuova consegnabile solo dopo suite Windows, pacchetto estratto, avvio/chiusura e pubblicazione riusciti. Base PC confermata b936879 e ZIP storici conservati. Prossimo controllo: esito run 41330559676 prima di dipendere dai risultati del passo 1.
