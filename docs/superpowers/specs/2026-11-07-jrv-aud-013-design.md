# JRV-AUD-013 — guide operative distribuite

Base012 verificata `605c7056a1320523bb2a177fc95acbadb70a6159`. Il builder esclude tutti docs e quasi tutti i Markdown: manca la guida richiamata dall'installer vocale e quelle dei componenti. Includere soltanto docs/VOCE_OFFLINE.md, docs/RECUPERO-IMPOSTAZIONI.md, file_access/LEGGIMI.md e program_apps/LEGGIMI.md. Renderle obbligatorie, preservando esclusioni di sviluppo/handoff/test/upstream e nessun dato personale.

La guida voce attuale mescola istruzioni storiche contraddittorie: aggiornare le sole istruzioni operative a installazione manuale, modalità e preferenze reali. L'installer non deve promettere microfono sempre spento; nessun avvio/consenso viene cambiato. La storia resta nel commit precedente. Niente installer eseguiti o download. Il riferimento tecnico Accesso file escluso dal pacchetto diventa link HTTPS immutabile alla repository.

Test Windows del selettore reale estratto tramite AST, senza eseguire il builder: quattro guide incluse, sviluppo escluso, rimedi locali e link relativi risolvibili/inclusi. Nessuna build/ZIP. Poi suite/probe esistenti3.11/3.12, review readonly e hash remoti. Verifica dell'archivio estratto resta pendente fino a build autorizzata.
