# Jarvis — audit trasversale dell'intero repository (2026-11-05)

## Metodo e limiti
Review iniziale repository `feature/gemma-local-20261104`, 320 file tracciati, 178 Python, 80 file sotto tests/, 27 workflow. Esaminati direttamente `AGENTS.md`, `README.md`, `ROADMAP.md`, `docs/AUDIT_COMPLETO_20261031.md`, `docs/HANDOFF-ARCHITETTURA-JARVIS-20261105.md`, `jarvis.py` (percorsi Gemma/programmi), `local_engine.py`, `addon_manager.py`, `program_apps/service.py`, `program_apps/native.py`, `local_model/native_conversation_session.py`, `local_model/memory_preferences.py`, `local_model/compact_context.py`, `conversation_memory.py`, `source_review.py`, `self_diagnostics.py`, `runtime_diagnostics.py`, `network_telemetry.py`, `memory_boundaries.py`. Non equivale a lettura riga-per-riga di tutti i 320 file, né a collaudo fisico di Windows 10. Il repository dispone di una skill/strumento interno di audit statico (`self_diagnostics.py` + `source_review.py`), ma non è stato eseguito su una copia locale completa; non confondere con skill ChatGPT installate.

## Stato CI verificato
Commit `d8dab462ae350954ad11a8c5d482f5b0cde44480`: `Local model contract (Windows)` run 42104081590 SUCCESS, `Native chat routing (Windows)` run 42104081499 SUCCESS, `Jarvis Gemma clean Windows trial` run 42104081575 SUCCESS. Le run precedenti `af5424d` fallivano per SyntaxError `native_conversation_session.py`, ora risolto a livello CI. Successo CI non prova risposta naturale italiana, TTS reale o apertura Netflix.

## Mappa sistemi e superfici di audit
- UI e orchestrazione: `jarvis.py`, `workspace_gui.py`, `animated_hud.py`, `hud_orbits.py`, `hud_backdrop.py`, `planner_ui.py`.
- Voce: `voice_control.py`, `adaptive_voice.py`, `speech_activity.py`, `offline_tts.py`, `startup_greeting.py`; verificare startup, wake word, mute, code e TTS.
- GPT e autorizzazioni: `gpt_client.py`, `gpt_bridge.mjs`, `conversation_router.py`, `action_planner.py`, `plan_runner.py`, `capability_registry.py`, `live_capabilities.py`, `local_model/online_permissions.py`.
- Gemma offline: `local_model/native_*.py`, `memory_preferences.py`, `compact_context.py`; inferenza CPU KoboldCpp, prompt, filtro, memoria e configurazione.
- Azioni Windows: `local_engine.py`, `program_apps/`, `file_access/`, `desktop_dictation.py`, `notepad_controller.py`, `document_*.py`, `managed_documents.py`.
- Add-on: `addon_manager.py`, `addon_ui.py`, manifest `.jaddon`; doppio consenso add-on/app.
- Memoria e progetti: `conversation_memory.py`, `second_brain.py`, `workspace_memory.py`, `project_documents.py`, `memory_boundaries.py`, `dialogue_focus.py`.
- Telegram: `telegram_bridge.py`, `telegram_commands.py`, `telegram_directory.py`, `telegram_outbound_flow.py`, `telegram_security.py`, `telegram_secret_dialog.py`, `telegram_voice.py`, `telegram_ui.py`.
- Diagnostica, packaging, CI: `self_diagnostics.py`, `source_review.py`, `runtime_diagnostics.py`, `diagnostic_session.py`, `diagnostic_handoff.py`, `network_telemetry.py`, `tools/`, `.github/workflows/`, `Download/`.

## Rilievi prioritari
**P0 — conflitto di specifica del microfono all'avvio.** `ROADMAP.md` impone microfono SPENTO all'avvio; `README.md` e `docs/AUDIT_COMPLETO_20261031.md` descrivono microfono ATTIVO nel profilo di audit. `AGENTS.md` include istruzioni storiche e aggiornamenti. Verificare codice e preferenza più recente prima di qualunque modifica; non dedurre il comportamento effettivo dalla documentazione. Consolidare una sola fonte di verità.

**P0 — filtro conversazionale Gemma appena riparato.** Prima delle run 4210408 il modulo aveva SyntaxError. Ora i workflow passano, ma il filtro per sezioni interne è euristico: può tralasciare formati non previsti o troncare testo legittimo. Mancano prove su casi realistici dell'utente, incluse risposte italiane e output vocale.

**P1 — comandi app e diagnosi generica.** Netflix era selezionato ma `Programmi e app` disattivato. Il messaggio del guardrail non distingue in modo affidabile add-on OFF, app non consentita, parser non riconosce, catalogo obsoleto e fallimento Windows. Verificare `try_program_command` -> `ProgramService.parse_command` -> `addon_manager.is_active` -> `LocalEngine.execute_program` -> avvio Windows. Nessuna conferma reale Netflix dopo attivazione.

**P1 — consenso GPT online.** `submit_gpt` è stato protetto in un percorso ma occorre audit di tutti i punti di invocazione (voce, piani, fallback, Telegram, errori). Non dichiarare copertura universale prima di test per ogni entry point.

**P1 — memoria a 8.** `MemoryPreferences` prevede `recent_messages=8`, `summarize_every=8`, `background_summaries=True`; `CompactContext` effettua compattazione deterministica, ma `NativeConversationSession` usa il budget e gli ultimi turni senza chiamare direttamente il compattatore. Non attribuire a questa regola le note interne di Gemma senza una traccia. Valutare 12/12 solo dopo benchmark context size e latenza su CPU AVX.

**P1 — compatibilità Windows/portabilità.** Catalogo programmi e indice file devono adattarsi a qualunque PC, senza copiare percorsi/consensi da un'altra macchina. L'indice completo è descritto in `AGENTS.md` come ancora da realizzare: non dichiararlo implementato.

**P1 — rischi integrazione / regressione.** `jarvis.py` concentra GUI e routing; cambi di priorità fra documenti, progetti, Telegram, programmi, Gemma e GPT possono oscurare comandi validi. Richiesti test end-to-end per percorso scritto/voce e conflitti di stato.

**P2 — osservabilità.** Distinguere operazione richiesta, accettata, avviata, verificata, fallita. `runtime_diagnostics.py` dichiara esplicitamente che mostra stati osservati, non certificazioni; usare ledger e diagnostica senza esporre credenziali.

**P2 — packaging e documentazione.** `README.md` descrive un ramo audit 31/10 e microfono attivo; `ROADMAP.md` un assetto GPT-first storico. `main` pubblica ZIP tramite workflow su ramo Gemma. Verificare commit ZIP, link README Download, isolamento profili e rollback. Non modificare o cancellare dati personali.

## Piano di review completa, ancora da eseguire
1. **Inventario e import graph** su tutti i file Python, rilevare dipendenze circolari, moduli non raggiungibili, import con side effect, duplicazioni e dimensioni; usare `source_review.py` e `self_diagnostics.py` su checkout Windows isolato.
2. **Security pass**: subprocess, shell, path traversal, file permissions, Telegram secrets, rete, esecuzione piani e prompt injection, confini di add-on.
3. **Functional matrix**: voce, hotword, TTS, GPT online, Gemma, timer, programmi, file, documenti, progetti, Telegram, autodiagnosi, HUD; per ogni caso: percorso, stato, test, prova PC.
4. **Performance pass**: startup, RAM, thread, UI Tk, audio queue, HDD, GGUF TTFT/tokens/sec, indici file, carico misto.
5. **Regression & release pass**: test Windows 3.11/3.12, prove di integrazione, packaging, ZIP, confronto manifest/commit, backup e rollback.
6. Correggere per gravità con commit piccoli e test; aggiornare handoff e matrice dei requisiti. Non dichiarare audit integrale completato finché ogni sottosistema non è stato ispezionato e testato.

## Vincoli
Nessun costo aggiuntivo, CPU i3-2100 AVX-only, Windows 10 x64, 10GB RAM, microfono sotto controllo manuale secondo scelta corrente, preferenza voce/GUI, add-on modulari `.jaddon`, nessuna esecuzione di testo generato dal modello, nessuna perdita dati, test su Windows, build solo dopo autorizzazione esplicita.
