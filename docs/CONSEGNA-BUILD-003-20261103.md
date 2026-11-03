# Consegna Jarvis003 — interruttori rapidi

[Scarica Jarvis-003.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-003.zip).

MIC, GPT e MEMORIA in alto a destra sono cliccabili. Riutilizzano i controlli esistenti: stessa configurazione, salvataggio e rollback. La memoria generale OFF conserva archivi/progetti e conversazione RAM. Lo stato distingue GPT NON CONNESSO e MIC NON ATTIVO/PTT dall'attività effettiva. Nessun backend/add-on duplicato o modifica delle modalità d'avvio.

## Identificazione e recupero

- Sorgenti: [2d52ba540aad1f9989f588e45b7a0b0973d49e67](https://github.com/MATRIXNEO23/jarvis/tree/2d52ba540aad1f9989f588e45b7a0b0973d49e67), ramo build/jarvis-003 dalla UI9a4b77f; runtime UI2dba1d3, fixture corretta0eafb12.
- ZIP:79 file,266469 byte; SHA256 `9554fd5bdde7b9f8c387bfa2fed66167abb90c5c98e691f74ad5ffb6bcf119fb`.
- Cartella estratta Jarvis-003; VERSIONE.json build_number3,label003,version0.1.3-candidate e manifest.
- Pubblicazione mainb7e1e0d612d5ca338ec6359a099968051bb5daea; registro latest3,next4.001/002 e i loro metadati restano immutati.
- Base PC storica confermata b936879 conservata.003 è candidata: collaudo PC pendente.
- Trigger push del ramo rimosso e publisher disabilitato nel commitae4eca2822e79407c3230367fba31af7bb08c4e8. Futuri pacchetti richiedono nuova richiesta; non ripetere questo rilascio.
- Stesso profilo LOCALAPPDATA\\Jarvis-AccessoFile-Trial, nessuna migrazione dati. Chiudere Jarvis, estrarre in cartella nuova, avviare solo avvia_jarvis.bat. Conservare cartella002 e profilo; per ritorno chiudere003 e riaprire002, senza cancellare dati.

## Prove della consegna

[Run41675960102](https://github.com/MATRIXNEO23/jarvis/actions/runs/41675960102) SUCCESS sul source esatto.

| Ambiente | Esito |
| --- | --- |
| Windows2022 Python3.11.9/job126056505277 | 511 test OK,72.029s |
| Windows2022 Python3.12.10/job126056503832 | 511 test OK,87.707s |
| ZIP estratto Python3.12 | 136 test OK,27.748s; inclusi tre nuovi casi Tk |
| Pacchetto | CRC, manifest hash/esatto inventario, numero/cartella/source, launcher unico, import PASS |
| UI estratta | Avvio e chiusura normale con profilo temporaneo e servizi live spenti PASS |
| Ricostruzione | Secondo build con orologio diverso, byte identici PASS; ZipInfo fisso anche VERSIONE |
| Sintassi/probe | Python/Node/PowerShell e probe nativo PASS |
| Windows Search live | Crea/rinomina/cancella, ambito, ripristino servizio e fixture PASS |
| Publisher126058351370 | Download HTTP003/hash/byte/link e hash pubblici001/002 PASS |

Il publisher pubblica soltanto Download e README principale; sorgenti applicativi storici main invariati. Registro e metadati pubblicati riletti tramite API:003 coincide con artifact verificato e prime due voci registro identiche a quelle precedenti. Nessun test funzionale Linux.

## Revisione e limiti

Review indipendente circoscritta a9a4b77f…111983d: nessun blocco statico; corretta etichetta publisher002→003 nel source finale2d52ba5. Review controlla gating di entrambi i job, immutabilità, retry obsoleto prima delle scritture e verifica pubblica; non esegue i test, documentati separatamente sopra. Il retry dopo future release viene rifiutato senza ripuntare i link alla vecchia candidata. Non fare rerun-all per rigenerare una candidata già consegnata.

Tre test HUD usano Tk, callback/provider/binding effettivi, JSON e SQLite temporanei; trasporto GPT, hardware audio e scheduling controllati. Precedente Red/Green e correzione fixture in [scheda UI](HUD-INTERRUTTORI-RAPIDI-20261103.md). Audio/account reali, stop-riavvio rapido, layout/DPI e consumi Pavilion restano da collaudare. Prima prova PC: soltanto MIC in alto, spegnere e riaccendere con un clic alla volta.

Ricerca limitata a20 risultati, nomi Explorer come Programmi, riferimenti lunghi/tardivi, conferme libere e rischio salva/chiudi documenti restano filoni aperti:003 non li corregge. Evitare salva/chiudi su documenti importanti. Contesto cartella della002 preservato, senza garanzia su ogni risposta del modello reale.
