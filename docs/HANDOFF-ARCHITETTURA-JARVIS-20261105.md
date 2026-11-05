# JARVIS — handoff tecnico, mappa architetturale e checkpoint (2026-11-05)

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

## Fonte di verità e stato
Repository: `MATRIXNEO23/jarvis`. Ramo di integrazione Gemma: `feature/gemma-local-20261104`. Pubblicazione ZIP su `main/Download/Jarvis-Gemma-PROVA-CORRETTA.zip`; pagina `main/Download/README.md`. Il ramo `main` contiene anche pubblicazioni automatiche: NON assumere che il codice applicativo su main coincida con il ramo Gemma. Verificare sempre ref/commit, ZIP e workflow prima di dichiarare un rilascio.

Checkpoint verificato: il modello Gemma risponde nella chat principale (test visivo dell'utente); la sintesi vocale è stata collegata via `speak_result` (commit `5481310272c474de9a8f210dd8d196cf39698627`), build Windows riuscita run `42081191577`. Il guardrail per richieste esplicite di avvio senza esecuzione è nel commit `950acac1ed3d33d0bae8f4428ed1be4e6350a99f`, build riuscita run `42081766861`, ZIP pubblicata su main. Non equivale a test reale del PC.

Problema Netflix: prima Gemma rispondeva «Ti aiuterò a avviare Netflix» senza prova dell'avvio; poi la console mostrava «PROGRAMMI > Non ho avviato il programma. Attiva Programmi e app...». L'utente ha confermato che Netflix era già spuntato ma l'add-on **Programmi e app era disattivato**. È la causa operativa individuata; l'utente deve ancora confermare un avvio riuscito dopo attivazione. NON registrare «Netflix funziona» come collaudato.

## Mappa di esecuzione (codice verificato sul ramo Gemma)
```text
Utente: tastiera / microfono (Vosk e controlli voce)
                 |
                 v
          jarvis.py (GUI, eventi, stato, console)
                 |
       +---------+---------------------+
       |                               |
  comandi espliciti                conversazione
  try_file_command                 send_console_input
       |                               |
  try_program_command             configurazione GGUF valida?
       |                            /             \
  ProgramService.parse_command    sì             no
       |                           |               |
  addon_manager.is_active       submit_gemma_trial  GPT solo secondo
       |                           |                impostazioni/permessi
  submit_local / LocalEngine       | 
       |                       NativeConversationSession
  execute_program                 -> NativeChatAdapter
       |                          -> NativeLocalProvider
  ProgramService.execute          -> NativeGemmaBridge
       |                          -> DLL KoboldCpp no-AVX2 / GGUF
  allowlist app, consenso,           |
  identità e disponibilità       poll_gemma_trial
       |                          -> write_line + speak_result
  program_apps/native.py
  avvio Windows EXE/LNK/Store
       |
  risultato reale in console / voce
```
Il modello non esegue programmi autonomamente: il testo libero generato non è un comando sicuro. Il servizio ProgramService verifica app consentita, identità, catalogo, disponibilità, ambiguità, revoca e permesso add-on. Evitare shell arbitraria e bypass delle spunte.

## File chiave
- `jarvis.py`: punto di composizione GUI, eventi voce/chat, `send_console_input`, `try_file_command`, `try_program_command`, `submit_local`, `submit_gpt`, `submit_gemma_trial`, `poll_gemma_trial`, `speak_result`. Attenzione ai rami di risposta e alle priorità di routing.
- `local_engine.py`: motore deterministico e TaskResult, delega alle capacità approvate; nessun codice generato eseguito.
- `addon_manager.py` / `addon_ui.py`: installazione, attivazione e permessi separati. Manifest `.jaddon` dichiarativi, nessun codice eseguibile nell'installazione.
- `program_apps/ProgrammiApp.jaddon`: azione `addon.programmi_app.avvia` -> `apps.launch`; **OFF iniziale**.
- `program_apps/service.py`: `launch_query`, `protected`, `blocked`, `parse_command`, `execute`, `save_preferences`, `refresh_catalog`. `available()` dipende da `enabled()`; la spunta della singola app NON abilita l'add-on. `programs.json` salva elenco, disponibilità, preferenze e alias. L'esecuzione richiede `enabled=True` per l'app e add-on attivo.
- `program_apps/native.py`, `windows_apps.ps1`: enumerazione e avvio app Windows (classiche/Store); `program_apps/ui.py`: selezione, alias, aggiornamento, test avvio.
- `local_model/native_config.py`, `native_settings.py`, `native_ui.py`: GGUF, DLL, threads, context_size, max_output, sampling; impostazioni configurabili.
- `local_model/native_conversation_session.py`: storico locale limitato, costruzione prompt con budget; esplicitamente nessuna azione desktop né fallback online.
- `local_model/native_chat_adapter.py`, `native_factory.py`, `native_initializer.py`, `native_provider.py`, `native_bridge.py`: trasporto e inferenza KoboldCpp in processo, senza servizio HTTP; errore nativo con status/stopreason.
- `local_model/online_permissions.py`: controlli permessi online; verificare TUTTI i percorsi prima di affermare che nessuna chiamata online parte senza consenso.
- `file_access/`: accesso file e ricerca; `project_voice.py`, `workspace_memory.py`, `conversation_memory.py`: progetti e continuità; `voice_control.py`, `speech_activity.py`: comandi e stato voce.
- `.github/workflows/gemma-windows-test-package.yml`: build prova Windows da ramo Gemma; scarica DLL no-AVX2 pinned, esegue test e pubblica ZIP su main. Trigger push include `jarvis.py`, `local_model/**`, build script e workflow; **modifiche solo a `program_apps/**` non attivano necessariamente questa build**.
- `tools/build_gemma_clean_trial.py`: creazione ZIP. `Download/README.md`: indice download. `docs/PROGRAMMI-APP-IMPLEMENTAZIONE-20261103.md`: design, controlli e prove precedenti.

## Vincoli e decisioni permanenti
Windows 10 x64, HP Pavilion i3-2100 (AVX, NO AVX2), 10 GB RAM, Radeon HD6450 1GB; zero costi extra, nessuna API a consumo. Preferire CPU no-AVX2 e mini-LLM locale; online solo con consenso esplicito. Gemma deve usare la chat principale e TTS esistente, non una chat separata. Tutte le nuove capacità preferibilmente add-on `.jaddon`, core solo per collegamenti tecnici motivati. Non migrare indiscriminatamente le vecchie funzioni. App Store e desktop devono essere supportate, ma solo se selezionate. Sinonimi e alias vocali; non eseguire comandi senza autorizzazione. Microfono in standby/spento all'avvio, poi controllo manuale e wake word «Jarvis»; evitare consumo token a microfono acceso. Preservare preferenze, memoria, progetti, salvataggi e rollback. Non dichiarare un successo basandosi sulla sola risposta testuale del modello.

## Rischi / opportunità di miglioramento
1. Diagnostica specifica di `try_program_command`: distinguere add-on OFF, app non selezionata, catalogo obsoleto, parser non riconosce, ambiguità, permesso revocato, avvio Windows fallito. Il guardrail del commit `950acac` usa ancora un messaggio generico; non è una riparazione del launcher.
2. Allineare messaggi TTS/console all'esito `ProgramResult`, non al testo del modello. Eseguire prove reali per EXE/LNK e Store (Netflix) su Windows.
3. Testare input sia scritto sia vocale (wake word, varianti «apri», «avvia», alias) e tutte le combinazioni: add-on OFF/ON, app non spuntata/spuntata, app assente, due match, modifica/revoca consenso.
4. Verificare che la sintesi vocale non blocchi la UI e rispetti mute e preferenze; testare risposte Gemma e errori.
5. Verificare l'integrazione tra modello locale e azioni: le richieste non parseabili non devono diventare «ho fatto» fittizi; proporre eventualmente un intent strutturato validato, senza dare al modello privilegi di esecuzione.
6. Audit di tutti i percorsi online (chat, voce, fallback, comandi GPT) per conferma esplicita e zero traffico non autorizzato.
7. Test regressione, benchmark reali su CPU AVX-only (RAM, latenza, TTFT), timeout e recupero errori; nessuna garanzia di prestazioni senza misure.

## Ripresa operativa per un nuovo agente / programma
1. Aprire questo file e `docs/PROGRAMMI-APP-IMPLEMENTAZIONE-20261103.md`; verificare SHA corrente di main e ramo Gemma.
2. Leggere `jarvis.py` (funzioni nominate sopra), `addon_manager.py`, `program_apps/service.py`, `program_apps/native.py`, `local_engine.py`, `local_model/native_conversation_session.py`.
3. Chiedere soltanto l'esito mancante: «Dopo aver attivato l'add-on, Netflix si apre?». Non assumere fallimento o successo.
4. Se fallisce, riprodurre con app spuntata e add-on ON, aggiungere test mirato e diagnostica, correggere causa minima, preservare permessi e percorsi esistenti.
5. Eseguire test Windows, compilare ZIP, verificare workflow e artefatto pubblicato, aggiornare `Download/README.md` con nome chiaro, commit e stato di collaudo. Evitare di dire «pubblicato» prima di controllare.
6. Aggiornare questo handoff dopo ogni modifica: data, ref, commit, test, ZIP, risultati reali, problemi aperti. Nessun lavoro in background presunto.

## Riferimenti release
- Gemma chat/voce: `5481310`, run `42081191577`.
- Guardrail programmi: `950acac`, run `42081766861`.
- README Download aggiornato: `7e1cfad8113205a266d63785c374dc967116f7a9`.
- URL ZIP: `https://github.com/MATRIXNEO23/jarvis/raw/refs/heads/main/Download/Jarvis-Gemma-PROVA-CORRETTA.zip`.
- **Non ancora collaudato**: Netflix dopo riattivazione add-on; TTS reale su Pavilion.
