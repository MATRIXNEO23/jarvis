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

## Registro operativo dei problemi — sequenza di risoluzione
Stati: DA VERIFICARE / IN LAVORAZIONE / TEST CI / TEST PC / RISOLTO. Nessun problema si considera RISOLTO sulla sola base di un commit.

| ID | Priorità | Problema | Stato | Evidenza e prossimo gate |
| --- | --- | --- | --- | --- |
| JRV-001 | P0 | Gemma produce note interne, anche lette dal TTS | TEST PC | `d8dab46` ripristina sintassi, `e581701` aggiunge casi di regressione; verificare workflow Windows e prova vocale reale |
| JRV-002 | P0 | Avvio microfono: preferenze e documentazione in conflitto | TEST CI | `settings.py` usa `auto_listen=True` come default; README/ROADMAP discordanti; verificare percorso runtime e requisito vigente prima di modificare |
| JRV-003 | P1 | Programmi e app: errore generico e Netflix non verificato | TEST CI | add-on disattivato nel test riportato; distinguere OFF/permessi/catalogo/parser/esecuzione |
| JRV-004 | P1 | Consenso GPT online su ogni entry point | DA VERIFICARE | inventario chiamate da voce, testo, piani, fallback, Telegram |
| JRV-005 | P1 | Memoria locale 8/8, compattazione e continuità | DA VERIFICARE | distinguere `CompactContext` da `NativeConversationSession`; benchmark prima di 12/12 |
| JRV-006 | P1 | Indicizzazione completa e portabilità Windows | DA VERIFICARE | percorso Known Folders presente, indice totale non confermato |
| JRV-007 | P1 | Interferenze router comandi, GUI e add-on | DA VERIFICARE | test integrati per precedenza e azioni autorizzate |
| JRV-008 | P1 | Telegram: segreti, cronologia, autorizzazioni, messaggi vocali | DA VERIFICARE | test simulati + collaudo account autorizzato |
| JRV-009 | P2 | Documenti/progetti: persistenza, rollback, salvataggi | DA VERIFICARE | verifiche isolamento profili e non regressione |
| JRV-010 | P2 | Prestazioni, avvio, CPU AVX, RAM, TTS e code UI | DA VERIFICARE | misure su hardware target |
| JRV-011 | P0 | Packaging, ZIP, README, workflow e riproducibilità | IN LAVORAZIONE | confrontare hash/commit, contenuti e modalità pubblicazione |

### Procedura
Un ID alla volta: riproduzione -> causa -> fix minimo -> test Windows -> prova sul PC -> aggiornamento stato. Non eseguire build pubblica senza consenso esplicito. Per JRV-001, `tests/test_native_conversation_session.py` copre note `What's Going Right`, blocchi `<think>`, preservazione di risposte normali e fallback; non prova da solo che il modello generi correttamente italiano.

### Aggiornamento 2026-11-05 — JRV-001/JRV-002
- JRV-001: test Windows `42104937299` SUCCESS, commit `e581701`; resta prova TTS/modello su hardware utente.
- JRV-002: `settings.py` definisce `auto_listen=True`, carica e salva scelta persistente; `avvia_jarvis.bat` annuncia esplicitamente microfono ON, `README.md` ON, `ROADMAP.md` OFF. Prima di modificare default occorre confermare requisito vigente; evitare di sovrascrivere preferenze dell'utente. Verificare poi startup reale e test Windows.

### JRV-002 — intervento 2026-11-05
Utente conferma microfono ON automaticamente all'avvio, hotword «Jarvis» obbligatoria. Analisi: `settings.py` default `auto_listen=True`, preferenza persistente e modificabile; `prepara_test_telegram50.py` imposta ON soltanto in migrazione iniziale; `voice_control.WakeWordGate.route(require_name=True)` rifiuta richieste senza hotword; `jarvis.py` usa `require_name=True` in entrambi i modi passivi. Correzione `ee9f622`: etichette UI non dichiarano più erroneamente invio automatico a GPT, chiariscono Gemma locale e hotword. Correzione `718f953`: roadmap aggiornata al requisito corrente. Nessun cambiamento al comportamento di microfono o alle preferenze salvate. Restano test Windows e prova su microfono Vosk reale.

### JRV-003 — intervento 2026-11-05
Verificati `program_apps/service.py`, `native.py`, test service/integration. Il parser è locale, le selezioni sono persistenti, l'add-on è un gate e il lancio Windows restituisce solo accettazione, non verifica finestra aperta. `65e79d8` distingue rifiuto per app assente dal catalogo e app presente senza autorizzazione; `53b79ba` aggiunge regressione Windows. Restano: test CI, prova reale app Store/Netflix, e progettazione della verifica apertura senza promesse false.

### JRV-011 — rischio pubblicazione automatica scoperto durante JRV-003
`.github/workflows/gemma-windows-test-package.yml` aveva trigger push sul ramo Gemma e step `Publish ZIP to main Download` che effettuava `git push` su `main`. Ciò viola la regola build solo su richiesta esplicita. Commit `5636470`: eliminato il trigger push, mantenuto solo `workflow_dispatch`; il pacchetto può essere generato/pubblicato soltanto con avvio manuale. Non è stata richiesta né avviata una build in questo intervento. Audit degli altri workflow di pubblicazione ancora necessario.

### JRV-003 — nota test
`tests.yml` non include `feature/gemma-local-20261104` fra i trigger push: i test specifici programmi aggiunti in `53b79ba` non hanno ancora un run CI su quel commit. Il workflow Gemma precedente non copre `test_program_apps_service.py`. Non dichiarare superata questa regressione senza esecuzione Windows della suite.

### Regola di pubblicazione confermata dall'utente
Quando tutte le verifiche obbligatorie sono superate, pubblicazione automatica della build; nessuna conferma aggiuntiva. Non equivale a pubblicare ogni push o con test non eseguiti. `3330d6a` abilita la suite completa Windows sul ramo Gemma; `daa872d` configura il publisher per reagire soltanto al completamento positivo della suite (o avvio manuale). **Limite da risolvere prima di dichiarare l'automazione operativa:** GitHub Actions esegue i trigger `workflow_run` solo se il file ricevente è presente sul branch predefinito; la modifica è per ora solo sul ramo feature. Inoltre il collaudo reale del microfono/app Store non è coperto dalla suite: non equiparare CI verde a «tutto fatto». Verificare gate di release e workflow sul default branch prima di una pubblicazione automatica. Nessuna build pubblicata da questi commit.

### Regressione completa Windows — 2026-11-05
Run `42106340408` (commit `329f6ed`): **FAIL**, 626 test, 8 failures, 13 errors. Il runner conferma Windows Search CI positivo, ma nessuna verifica sul PC utente. Due cause tecniche direttamente osservate nei log: fixture del callback voce eseguito isolatamente non fornisce `gemma_trial_busy` (NameError in test_gpt_voice_addressing); fixture del worker GPT non fornisce `chat_transport` (NameError, test_file_refinement). Non risolvere alterando le asserzioni senza distinguere test legacy da regressioni reali. La pubblicazione rimane bloccata. URL: https://github.com/MATRIXNEO23/jarvis/actions/runs/42106340408
