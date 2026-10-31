# Handoff Jarvis → Codex — 2026-10-31

## Stato verificato
- Repository: MATRIXNEO23/jarvis, branch di distribuzione `main`.
- Archify v3.2.0 installato per Codex, solo come strumento di sviluppo in `.agents/skills/archify/`. La workflow `Install Archify skill for Codex (repository only)` run 41232507968 è PASS; verificato che `.agents/skills/archify/SKILL.md` è presente su `main`.
- Archify **non** è un add-on di Jarvis, non è un componente del runtime Windows e non corregge automaticamente bug.
- Due workflow recenti `Jarvis unit and GPT protocol checks` falliti: run 41230414187 (commit 1f7310f...) e 41230403859 (commit 8d439df...). Esaminare log, identificare cause, non indovinare.
- Workflow `Publish Jarvis timer audio fix ZIP to Download` run 41229495866 PASS; correzione nota: `winsound.SND_SYNC` non esiste, usare `SND_NODEFAULT` per WAV. Bip alternativo funzionante sul PC utente; WAV ancora da verificare sul PC dopo l'aggiornamento.
- Problema aperto: in conversazione normale Jarvis perde coerenza dopo 2-3 scambi. Le limitazioni note sono in `conversation_memory.py`, `conversation_router.py`, `jarvis_persona.py`, `jarvis.py`; verificare branch e versioni effettive prima di modificare. Le modifiche precedenti sul branch `feature/timer-settings-ui-20261031` non sono da considerare collaudate; due workflow falliti.
- Ultima richiesta: diagnosi architetturale con Archify, review del percorso voce/testo → memoria → prompt → modello esterno → risposta, e risoluzione dei workflow falliti. **Nessun nuovo add-on per questa correzione del nucleo conversazionale**.

## Vincoli del progetto
- Nessun costo aggiuntivo, nessuna API a consumo, nessun hosting a pagamento.
- Nuove funzionalità modulari `.jaddon` salvo correzioni tecniche del nucleo come questa.
- Preservare compatibilità, impostazioni, memoria/salvataggi e funzionalità.
- Microfono OFF/standby all'avvio; modalità di ascolto solo sotto controllo manuale.
- Hardware target: Windows 10 x64, HP Pavilion i3-2100, 10 GB RAM; evitare processi residenti superflui.
- Pubblicare pacchetti completi testati in `Download/`, aggiornare `Download/README.md` con link in cima solo dopo test PASS; non cancellare pacchetti precedenti.
- Prima di intervenire, verificare lo stato attuale di `main`, branch, diff e workflow; evitare sovrascritture e modifiche non richieste.

## Prossimo lavoro Codex
1. Leggere `.agents/skills/archify/SKILL.md` e documentazione necessaria. Usare Archify come strumento di sviluppo, non integrarlo nell'app.
2. Analizzare in sola lettura il codice e i log delle due run fallite; distinguere bug, regressioni e problemi CI.
3. Tracciare con prove da file/linee l'intero percorso della conversazione e la gestione del contesto; produrre mappa Archify validata e un breve rapporto.
4. Proporre una correzione minima e test multi-turno (riferimenti, cambio argomento, limiti e comandi); non aumentare indiscriminatamente il prompt.
5. Prima di modificare il codice, presentare risultati e piano all'utente per approvazione. Dopo approvazione, test e build review; pubblicare ZIP solo a verifiche superate.
6. Registrare commit, workflow, test e questioni aperte aggiornando questo handoff.

## Riferimenti
- Installazione: https://github.com/MATRIXNEO23/jarvis/actions/runs/41232507968
- Run fallite: https://github.com/MATRIXNEO23/jarvis/actions/runs/41230414187 e https://github.com/MATRIXNEO23/jarvis/actions/runs/41230403859
- Archify ufficiale: https://github.com/tt-a1i/archify
