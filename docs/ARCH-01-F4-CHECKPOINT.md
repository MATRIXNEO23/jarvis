# ARCH-01 F4.0 — Canary KoboldCpp server locale: protocollo e rollback

**Data:** 9 novembre 2026 · **Stato:** preparazione F4, nessun server avviato, nessun release/merge.
**Sorgente congelata F3:** `b8828f0facca6fb916ccd341e313670627e67a1d` da [PR #64](https://github.com/MATRIXNEO23/jarvis/pull/64); F3 testata al runtime commit `0c3247b69ac7033ec3d8194fbe1f6583d78108c0` in [42533254766](https://github.com/MATRIXNEO23/jarvis/actions/runs/42533254766) 1040 PASS per job Windows e [42533254794](https://github.com/MATRIXNEO23/jarvis/actions/runs/42533254794) nativo SUCCESS. Base installabile da ripristinare: ZIP014 source `88c2934cbd6081f94fb33fba5f87f1800b07ebc0`.
**Gate precedente non soddisfatto sul Pavilion:** il benchmark F3 Jarvis vs KoboldCpp originale con stessi prompt/config e Second Brain on/off NON è ancora stato eseguito. Perciò questa F4 è **solo una prova tecnica opzionale, senza modificare l'architettura di Jarvis**: niente switch automatico al server, niente seconda copia di GGUF, niente avvio del processo, niente collegamento alla UI.
**Documentazione KoboldCpp:** https://koboldcpp.net/docs/api/endpoints/ (GET `/api/v1/model`, POST `/api/v1/generate`, GET `/api/extra/perf`); https://koboldcpp.net/docs/api/overview/ ; https://github.com/LostRuins/koboldcpp/wiki/ (payload generazione con `prompt`, `max_context_length`, `max_length`, `stop_sequence`).

## Sottofasi
- **F4.0:** branch isolato, test di contratto scritti prima dell'implementazione, documentazione di protocollo, revisione sicurezza.
- **F4.1:** modulo nuovo `local_model/kobold_server_canary.py` con **chiamata esplicita** a KoboldCpp *già avviato separatamente* su `http://127.0.0.1:<porta>`; `probe()` read-only, `generate(...)` solo su chiamata manuale, `perf()` read-only. Solo urllib/std library, nessun import nel programma Jarvis.
- **Sicurezza:** host esattamente IP 127.0.0.1 (no DNS, LAN, HTTPS, router/admin); disabilitare proxy ambiente e redirect; timeout e massimo corpo di risposta; validazione tipi/campi, nessuna stampa prompt in errori, nessun download di modelli, credenziali locali in memoria solo se fornite dal chiamante; blocco su mismatch del modello prima di inviare testo, no retry implicito.
- **Test:** URL esterni/SSRF e redirect rifiutati, niente connessioni alla costruzione, probe parser, model mismatch senza POST, generazione raw esatta/limiti/stop, risposta malformata, errore/timeout, proxy isolato. Fake opener/HTTP local mock: nessun GGUF, rete o credenziale reale in CI.
- **Integrazione:** vietato modificare `jarvis.py`, `native_bridge.py`, `native_provider.py`, `chat_sessions.py`, `second_brain.py` o profili. F4 GUI e selezione backend sono una decisione successiva, condizionata a benchmark sulla macchina utente e consenso. Un solo GGUF caricato per il confronto pratico.
- **Rollback:** abbandonare branch/PR F4 e tornare a F3 `b8828f...`; nessun DB, memoria o profilo modificato, ZIP014 resta la versione installabile; nessun nuovo pacchetto/numero consumato.

## Registro verifiche
| Checkpoint | Stato | Evidenza |
|---|---|---|
| F4.0 preparazione | IN CORSO | questo documento, branch source F3 |
| F4.1 test RED | DA FARE | file test senza implementazione |
| F4.1 modulo opzionale | DA FARE | locale-only, no runtime wiring |
| F4.1 GREEN CI Windows | DA FARE | risultati e SHA obbligatori |
| F4.2 confronto Pavilion | NON ESEGUITO | protocollo F3 e prova utente |
| Migrazione DLL→server | NON APPROVATA | richiede dati e gate separato |
