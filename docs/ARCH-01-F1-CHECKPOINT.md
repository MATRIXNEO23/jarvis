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
