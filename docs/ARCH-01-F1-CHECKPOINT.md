# ARCH-01 / F1 — Registro di implementazione incrementale
**Avvio:** 8 novembre 2026. **Branch:** `feature/jarvis-kobold-chat-f1-20261108`. **Baseline source:** `88c2934cbd6081f94fb33fba5f87f1800b07ebc0` (Jarvis 014); branch non pubblicato.
**Piano approvato:** `docs/PIANO-IMPLEMENTAZIONE-KOBOLD-CHAT-20261108.md` (prima salvato su main, poi copiato nel ramo). **Fase corrente:** F1 fondazione delle chat locali; F2–F7 non iniziate.

## Motivazione e vincoli
- La UI attuale Jarvis offre una cronologia generale condivisa, non chat indipendenti. L'utente vuole istanze/chat sul modello KoboldAI Lite / ChatGPT con salvataggi persistenti, poter cambiare argomento partendo da zero senza perdere conversazioni.
- Modulo opzionale e inattivo: **nessun import dal runtime Jarvis, nessuna chiamata al modello, nessun servizio o GGUF aggiuntivo, nessun accesso al Second Brain/progetti**.
- Schema privato nuovo e separato dal profilo storico; un file DB solo quando verrà esplicitamente creato da un chiamante, senza alterare le tabelle legacy.
- Partizioni per generale vs ID progetto (32 esadecimali); nuovo chat ID casuale, titolo, date, selezione attiva, scambi coppia domanda/risposta in transazioni atomiche.
- Le future F2/F6 devono aggiungere i collegamenti UI/voce/Second Brain con gate separati; F1 non dichiara che il nuovo programma abbia già schede utilizzabili.

## Tracciamento
| Checkpoint | Fonte/diff | Prove | Stato |
|---|---|---|---|
| F0 piano/branch | Piano su main e ramo, source 014 immutabile | ispezione documenti e ref | fatto |
| F1 RED | test di archivio/partizioni prima del modulo | CI Windows 3.11/3.12 | da eseguire |
| F1 GREEN | `local_model/chat_sessions.py` solo import esplicito | stessi test e regressioni | da eseguire |
| F1 verifica/remoto | compare base + HEAD, nota canonica, link CI | nessun ZIP | da eseguire |

## Ripristino
Il runtime 014 non viene alterato; non eseguire merge né installare nuovi file sul Pavilion. Per annullare l'esperimento, tornare al source 014/ZIP immutabile e non importare `ChatSessionStore`. Il nuovo DB, qualora creato in futuro, **non si cancella automaticamente**. Nessun profilo esistente viene migrato o toccato.

## Problemi aperti
- UI e voce non collegate (F2).
- Diagnostica prompt separata PR #61 (F3) da integrare solo con scelta tracciata.
- KoboldCpp server e template Qwen non ancora validati (F4/F5).
- Confinamento recall Second Brain per nuova chat non ancora implementato (F6).


## Esito F1 — verifica dei sorgenti Windows completata (8 novembre 2026)

- **RED:** commit `742fea63d28ffabe095d80b541d58769cb130d34`, solo test: [run 42529168718](https://github.com/MATRIXNEO23/jarvis/actions/runs/42529168718), due job Windows FAILED per un unico errore atteso `ModuleNotFoundError: local_model.chat_sessions` (1014 test scoperti; la nuova suite non era ancora importabile). Nessun altro difetto attribuito a questa fase.
- **GREEN:** commit runtime `2f3c8d207ab1aff41d578fca6e48d606f7cd00d3`: nuovo modulo `local_model/chat_sessions.py`, F1 isolata; [run 42529275925](https://github.com/MATRIXNEO23/jarvis/actions/runs/42529275925) SUCCESS, **1022 test per job** Windows Python 3.11/3.12; suite servizi SUCCESS. [Prova tokenizer nativo 42529275993](https://github.com/MATRIXNEO23/jarvis/actions/runs/42529275993) SUCCESS.
- **Diff vs 014:** solo `local_model/chat_sessions.py` aggiunto come nuova capacità opt-in (nessun import nel codice Jarvis), test `tests/test_chat_sessions.py`, documentazione. `jarvis.py`, motore GGUF, prompt, store Second Brain, Telegram, wakeword, mic e autorizzazioni **invariati**. Nessuna cartella/profile utente toccato; test SQLite su `TemporaryDirectory` Windows.
- **Funzioni realmente implementate:** crea chat e la ritrova dopo riavvio dello store, elenco per ambito, selezione attiva per generale/progetto, rinomina, salvataggio atomico di coppie utente/assistant, lettura recente con limite ma senza eliminare storico; ID validati e scope rispettato; chiavi SQL parametrizzate; scritture serializzate per istanza store. Non contiene cancellazione e non crea alcun nuovo processo.
- **Cosa NON è pronto:** nessuna nuova scheda/pannello nell'app; nessuna condivisione con Second Brain, nessun cambio sorgenti di chat ancora, nessuna selezione modelli/template, nessun colloquio col server KoboldCpp. F2 è il prossimo intervento; la 014 consegnata resta identica.
- **Rollback:** chiudere/ignorare il ramo e riutilizzare il source 014 + ZIP immutabile. Nessun DB nuovo viene creato dall'app attuale; in futuro un DB di chat creato non dovrà essere cancellato dal rollback. **Nessuna build 015 o altra ZIP creata/pubblicata**.
- **Gate F1:** PASS nei test dei sorgenti Windows; non affermare collaudo sul Pavilion, microfono, account, app avviata o JSON reale di Qwen. F2 richiederà test di integrazione e UI dedicati.
