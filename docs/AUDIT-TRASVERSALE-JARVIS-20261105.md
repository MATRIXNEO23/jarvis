# Jarvis — audit trasversale dell'intero repository (2026-11-05)

## JRV-004 — Telegram e revoca durante la conferma

Il worker Telegram attende fino a 30 secondi una decisione monouso della console prima di inviare messaggio e contesto recente a GPT. Il collegamento Telegram e il recapito dei messaggi approvati dal proprietario restano separati. Una richiesta scaduta o riferita a un bridge disattivato viene scartata. Il pianificatore usa lo stesso dialogo e conserva la generazione di consenso fino al worker. La disattivazione o la perdita del collegamento GPT revoca l'accesso del worker Telegram. Verifica Windows e collaudo con account reale distinti.

## 6 novembre 2026 — JRV-004, consenso per richiesta dalla console

Il percorso `run_gpt` richiede il consenso prima di avviare un worker di inferenza e ricontrolla connessione, stato ed epoca dopo il dialogo. Login, stato e disconnessione seguono il loro percorso. Il raffinamento chiede prima di consumare il token, la spiegazione distingue il testo dell'anteprima, il chiarimento progetto conserva il riepilogo locale e l'autodiagnosi riusa il consenso specifico già esistente. I comandi locali precedono il dialogo del pulsante GPT. Il pianificatore separa il consenso a inviare la richiesta dall'approvazione del piano. Aggiornati i test Windows dei callback. Verifica CI sul nuovo commit in attesa. Restano il worker Telegram, la policy persistente per funzionalità e il collaudo con account reale.

## Verifica Windows e blocchi di rilascio

`db0b3a4`: [run 42113303954](https://github.com/MATRIXNEO23/jarvis/actions/runs/42113303954) verde su entrambi i job, 628 test per job. Il test di finestra Tk reale e i casi di accettazione, PID e finestra sono passati. Nessuna prova di apertura Netflix sul Pavilion.

`09c5e95`: [run 42113573907](https://github.com/MATRIXNEO23/jarvis/actions/runs/42113573907) ha riprodotto un errore della nuova fixture, che non passava `queue` all'esecuzione isolata del poll. `75bef3a` ripristina la dipendenza mantenendo le asserzioni. Nella [run 42113970995](https://github.com/MATRIXNEO23/jarvis/actions/runs/42113970995) i test unitari risultano verdi in entrambe le versioni Python. I job 127548563547 e 127548564393 hanno registrato 629 test ciascuno e hanno superato la nuova prova sulla risposta vocale obsoleta. La prova live di Windows Search è passata nel job Python 3.12 previsto. L'intera matrice è conclusa con successo.

Prossimo intervento JRV-004: trattare separatamente login e inferenza. Il pulsante GPT verifica un consenso condizionato alla presenza della configurazione Gemma prima di instradare azioni locali. Il chiarimento progetto, il raffinamento file e la spiegazione del file arrivano a `run_gpt`. Telegram chiama direttamente `service.call` dal worker e il pianificatore riceve lo stesso servizio. L'autodiagnosi ha un dialogo già dedicato. Per ogni percorso verificare esplicita autorizzazione, rifiuto, revoca e assenza di invio di contenuti altrimenti. Conservare il percorso locale e il consenso alle azioni come controlli distinti.

Per JRV-011 resta da collegare il pacchetto a una dipendenza esplicita dalla matrice Windows sullo stesso SHA, mantenendo separata la verifica dell'archivio estratto. La DLL no-AVX2 deve restare disponibile e verificabile per una ricostruzione futura. Il rilascio pubblico dipende anche dai collaudi obbligatori sul Pavilion, ancora aperti. Nessuna build pubblicata nel checkpoint.

## Voce Gemma: risposta in corso e cambi di contesto

La run [42112965273](https://github.com/MATRIXNEO23/jarvis/actions/runs/42112965273) su `cfa0e19` ha concluso la matrice Windows con successo. `db0b3a4` ha introdotto l'osservazione del PID e della finestra, run [42113303954](https://github.com/MATRIXNEO23/jarvis/actions/runs/42113303954). Il controllo osserva una finestra Win32 con titolo dello stesso PID, non minimizzata e non nascosta da DWM. Può rilevare una finestra già esistente o coperta. L'app Store può usare un altro processo per la finestra.

JRV-001/002: `jarvis.py` descrive Gemma locale quando si attiva la modalità conversazione. Il risultato vocale, compreso l'errore, ora appartiene alla generazione di contesto che ha avviato la richiesta: il poll scarta la risposta quando nel frattempo sono cambiati modalità, progetto o stato GPT. La risposta scritta mantiene il percorso esistente. La nuova prova esegue il callback reale su eventi controllati. Restano microfono e TTS reali, oltre all'isolamento della cronologia interna della sessione Gemma (JRV-005).

## Checkpoint Windows e osservazione avvio programmi

La matrice Windows della run [42112346657](https://github.com/MATRIXNEO23/jarvis/actions/runs/42112346657) su `57c3dd1` ha completato 626 test per job con esito OK. La revisione ha trovato il conflitto app/progetti nel ramo generico del parser. `c8c697c` ha riservato il ramo progetti esplicito, ma la run [42112742159](https://github.com/MATRIXNEO23/jarvis/actions/runs/42112742159) ha riprodotto un errore del nuovo test: Accesso file, ancora attivo nella fixture, consumava «apri Netflix». `cfa0e19` isola il test del ramo di riserva nella run [42112965273](https://github.com/MATRIXNEO23/jarvis/actions/runs/42112965273). Resta da verificare la precedenza app/file con i due componenti configurati insieme, mantenendo l'apertura implicita nella cartella Explorer.

JRV-003: `program_apps/native.py` conserva il PID fornito da Windows per l'attivazione Store o ricavato dall'handle ShellExecute. Il messaggio distingue accettazione, PID disponibile e osservazione immediata di una finestra Win32 visibile con lo stesso PID. App con finestra ospitata da un processo differente e finestre che appaiono più tardi richiedono verifica ulteriore. `tests/test_program_apps_native.py` copre i tre esiti e la prova Win32 su una finestra Tk controllata. Restano CI Windows sul commit, Netflix reale e affidabilità della corrispondenza finestra/app Store.

Altri blocchi registrati: il workflow ZIP scarica la DLL da un artefatto CI con scadenza 18 novembre 2026 e riscrive parti del runtime durante il packaging. La sessione Gemma conserva in RAM il dialogo anche quando cambia progetto e il provider già caricato conserva la configurazione precedente dopo un cambio delle impostazioni. Da verificare isolamento, aggiornamento della configurazione, consenso GPT, collaudi Pavilion e gate di rilascio.

## Riesame integrazione e programma di verifica

La run 42112126088 ha confermato la correzione del raffinamento file e del contesto in attesa. Il job 127542105108 ha chiuso con 2 fallimenti e 11 errori residui su 626 test. Il successivo checkpoint `57c3dd1` è in verifica nella run 42112346657. La revisione indipendente ha rilevato che anticipare il gestore progetti senza filtro avrebbe classificato «apri Netflix» come progetto quando l'add-on è spento. Il checkpoint successivo riserva i comandi che nominano esplicitamente un progetto e aggiunge il caso Netflix al test del callback di console.

| Sequenza | Integrazione | Prova richiesta |
| --- | --- | --- |
| 1 | File, voce, autodiagnosi, app e progetti | Callback reali con trascrizione e servizi controllati, suite Windows 3.11/3.12 |
| 2 | Gemma, TTS e hotword (JRV-001/002) | Output pulito nei due ingressi, ascolto automatico con hotword e standby manuale, collaudo Vosk/TTS sul Pavilion |
| 3 | Programmi e add-on (JRV-003/007) | Verificare precedenze, alias, revoca, accettazione Windows, PID osservabile e finestra associata. Collaudare Netflix con add-on attivo e app autorizzata |
| 4 | GPT e Telegram (JRV-004/008) | Inventario chiamate, consenso monouso prima dell'invio, rifiuto e nessun fallback implicito, collaudo account separato |
| 5 | Memoria, file e progetti (JRV-005/006/009) | Isolamento tra contesti, revoca permessi, conservazione dati esistenti, Windows Search e fallback su più unità |
| 6 | Risorse e rilascio (JRV-010/011) | Confronto con Kobold sul Pavilion, stessa configurazione. ZIP dallo stesso SHA collaudato, avvio da estrazione pulita e gate automatico senza dipendenza dal workflow assente su main |

Blocchi individuati da verificare: raffinamento file, spiegazione file e chiarimento progetto chiamano `run_gpt` senza passare dalla policy per funzionalità. Il launcher Store dispone di un PID ma lo scarta. L'attuale workflow Gemma manca su main e il percorso manuale può arrivare alla pubblicazione indipendentemente dalla suite. Lo ZIP modifica anche file Python in fase di assemblaggio, quindi i sorgenti della suite e quelli effettivamente distribuiti richiedono un controllo separato.

## 5 novembre 2026 — suite Windows del ramo Gemma

La run [42106340408](https://github.com/MATRIXNEO23/jarvis/actions/runs/42106340408) ha riprodotto 8 fallimenti e 13 errori su 626 test. `7ff60e2` collega il vero `ChatTransport` al servizio simulato in `tests/test_file_refinement.py`, usato anche da `tests/test_pending_file_context.py`. La relativa [run 42112126088](https://github.com/MATRIXNEO23/jarvis/actions/runs/42112126088) è stata avviata sul commit esatto.

Il checkpoint corrente applica lo stesso cablaggio a `tests/test_activity_status.py`. La fixture in `tests/test_voice_corrections_review.py` riproduce il contenitore `[False]` usato dal callback. `tests/test_gpt_voice_addressing.py` verifica che Gemma occupata rifiuti solo la richiesta indirizzata e che il parlato ambientale non venga inviato o accodato. `tests/test_self_review.py` controlla la precedenza della diagnosi rispetto al percorso Gemma della voce e al percorso GPT del testo. In `jarvis.py` i progetti espliciti tornano a precedere il filtro generico di avvio app, dopo la gestione dei file.

Gate aperto: verificare test mirati e matrice Windows 3.11/3.12 sul checkpoint, quindi analizzare eventuali fallimenti residui. JRV-001 e JRV-002 richiedono ancora collaudo reale. JRV-003 non ha conferma di apertura Netflix. Il rilascio resta subordinato alle prove obbligatorie.

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
