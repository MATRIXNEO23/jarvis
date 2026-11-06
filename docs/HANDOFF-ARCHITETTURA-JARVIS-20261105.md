# JARVIS — handoff tecnico, mappa architetturale e checkpoint (2026-11-05)

## 6 novembre 2026 — Carattere di Gemma locale

La configurazione del modello include istruzioni facoltative di stile (240 caratteri). Il valore è locale e compatibile con i profili precedenti. Si applica alle nuove risposte della conversazione Gemma e a Prova generazione, senza richiedere un ricaricamento per il solo cambio di stile. Si preserva la domanda se il budget è stretto. Le risposte Telegram continuano a usare il contesto del contatto. La prima run 42268657858 ha rilevato un'asserzione UI eseguita dopo Ripristina anziché dopo Salva. Sul commit correttivo `3c71ca4` le due suite Windows e la verifica dello ZIP estratto sono passate nella [run 42269297921](https://github.com/MATRIXNEO23/jarvis/actions/runs/42269297921). Resta il collaudo con il GGUF sul Pavilion.

## 6 novembre 2026 — Consenso GPT per Telegram durante la sessione

La modalità predefinita resta la conferma per messaggio. L'opzione esplicita in Impostazioni → Telegram autorizza l'invio dei messaggi e del contesto recente dei soli contatti selezionati. Il consenso è solo in RAM e si azzera disattivando o disconnettendo GPT oppure chiudendo Jarvis. Il trasporto ricontrolla token, epoca e bridge prima dell'invio e scarta risposte obsolete. Console e planner mantengono i propri controlli. Le due suite Windows e la verifica dello ZIP estratto sono passate nella [run 42246973814](https://github.com/MATRIXNEO23/jarvis/actions/runs/42246973814). I test simulano conferma, rifiuto, sessione e revoca. Resta il collaudo con l'account reale sul Pavilion.

## 6 novembre 2026 — Indicatore Telegram dei messaggi da vedere

Base `0055607`. Il pallino del contatto riusa il conteggio dei messaggi in arrivo non ancora visti. L'animazione HUD esistente alterna due tonalità viola per i nuovi messaggi e mantiene una tonalità tenue e fissa dopo l'apertura della cronologia. Il clic registra solo gli ID in arrivo mostrati, così un messaggio concorrente resta da vedere. Nessuna modifica alle ricevute di Telegram. Le due suite Windows e la verifica dello ZIP estratto sono passate nella [run 42221709872](https://github.com/MATRIXNEO23/jarvis/actions/runs/42221709872) sul commit `addc19e`. Resta la prova visiva sul Pavilion. Nessuna pubblicazione in Download.

## Telegram con Gemma locale

Il bridge mantiene contatti autorizzati, contesto recente della singola chat, presentazione, sintesi e invio dei vocali. Se GPT è attivo e connesso, resta il consenso per richiesta. Se GPT non è disponibile, Gemma riusa il modello caricato senza accedere alla cronologia della console o dei progetti. Il collaudo con account Telegram e modello reali resta separato dalla CI Windows.

## 6 novembre 2026 — rimossa la barra sostitutiva

La candidata `Download/Jarvis-Gemma-Comandi-e-Interfaccia-6e73e3b.zip` è pubblicata su main `14967a4`. Il commit `6e73e3b` mantiene solo i tre pulsanti, integrati nell'intestazione HUD esistente o raggruppati in alto a destra nelle finestre secondarie. Eliminata la fascia aggiuntiva con il titolo. I dialoghi nativi Windows mantengono l'aspetto di sistema. [Suite Windows, archivio estratto e pubblicazione](https://github.com/MATRIXNEO23/jarvis/actions/runs/42147766728) riusciti.

## Segnalazione Pavilion — dialogo Gemma e apertura app

La foto mostra «Apri Netflix» come risposta della chat. Il percorso scritto di Gemma non condivideva la selezione app del percorso vocale. Ora «con Gemma» può essere scritto oppure pronunciato. Dopo uno scambio recente che identifica una sola app autorizzata, una richiesta esplicita come «me lo apri?» passa al motore come proposta da confermare. Il testo del dialogo continua ad andare in chat. Scambio valido per 120 secondi e solo nella stessa epoca di conversazione. [Matrice Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42145643937) superati sul commit `0d99357`. Nessuna pubblicazione in Download.

## Finestre Windows con comandi integrati

Le finestre Tk di Jarvis usano una barra interna scura con riduci, massimizza/ripristina e chiudi. La rimozione della cornice avviene sul wrapper Win32 e mantiene i protocolli di chiusura Tk. La barra si applica anche alle finestre secondarie mappate dopo l’avvio e alla finestra separata di configurazione segreti Telegram. Le finestre native di sistema seguono l'aspetto Windows. La run [42144862058](https://github.com/MATRIXNEO23/jarvis/actions/runs/42144862058) sul commit `72af40e` ha superato 639 test per versione Python, compresa la prova Windows della barra su finestra principale e secondaria. Il pacchetto CI è stato generato e verificato dopo estrazione. Nessuna pubblicazione in `Download` per questa modifica.

## 6 novembre 2026 — candidata Gemma pubblicata

La [run Windows 42142495567](https://github.com/MATRIXNEO23/jarvis/actions/runs/42142495567) sul commit `5d554c8` ha superato la matrice Windows, i 26 test mirati dal pacchetto estratto e il caricamento della DLL inclusa. Il commit `7088b95` su main ha pubblicato `Download/Jarvis-Gemma-Avvio-Programmi-5d554c8.zip` e aggiornato `Download/README.md`. Archivio: 8.093.345 byte, SHA-256 `e54912b4e3de94c06dc654cd2fc4f64b698f0f2f2249ff67dab6e091022b8944`. Candidata per il collaudo su Pavilion. Voce, Gemma e app reali restano da provare.

## 6 novembre 2026 — avvio app con varianti locali e prova Gemma

I commit `9c08935` e `56fd9e4` riusano il catalogo e le autorizzazioni di Programmi e app. Una selezione abilita i verbi comuni. Frase senza nome, risposta successiva con nome esatto e suggerimenti per somiglianza sono stati verificati con launcher controllato. Il suggerimento Gemma richiede il prefisso vocale «con Gemma» in modalità conversazione e una conferma della scelta. La prova del selettore usa un modello simulato e verifica una generazione e l'esclusione della cronologia.

La [run Windows 42139706373](https://github.com/MATRIXNEO23/jarvis/actions/runs/42139706373) su `56fd9e4` ha superato 638 test per versione di Python. Restano il collaudo con voce, Gemma e app reali sul Pavilion, e il gate di rilascio. Nessuna nuova build pubblicata.

## Apertura locale e prova Gemma su richiesta

Programmi e app riconosce anche aprimi, avviami, lanciami, esegui, fai partire e metti in esecuzione. Una frase senza nome apre un chiarimento locale. I nomi simili suggeriscono un'app autorizzata e attendono una scelta. La prova vocale esplicita «Jarvis, con Gemma, mi serve qualcosa per vedere un film» seleziona una proposta fra 1–12 app abilitate e disponibili, senza cronologia nel prompt. Il motore chiede conferma e applica i permessi correnti. Gemma usa una sola generazione con il modello già caricato se disponibile. Prova Windows CI e collaudo Pavilion da registrare.

## 6 novembre 2026 — JRV-004, verifica Windows

La [run 42129127625](https://github.com/MATRIXNEO23/jarvis/actions/runs/42129127625) sul commit `e51c269` ha superato 635 test per job con Python 3.11 e 3.12. È passata anche la prova live Windows Search sul job previsto. Copertura mirata nei log: rifiuto e revoca dei callback, Telegram simulato, disconnessione immediata, revoca durante avvio del bridge e toggle HUD.

`dea28e6`: consenso console e planner. `4dd0e1f`: consenso Telegram e generazione di revoca del planner. `43d29e4`: ripristina il guard esplicito di rifiuto dell'autodiagnosi, mantenendo il controllo dell'epoca. `36d549e`: verifica nel trasporto prima dell'invio e scarto dei piani di un contesto superato. `e51c269`: inizializza lo stato Telegram nella fixture del pannello rapido dopo il fallimento della run 42129015218. Il risultato è simulato per account GPT e Telegram. Restano la configurazione persistente per funzionalità, le prove con account reale e il gate di rilascio. Una revoca dopo l'invio può scartare la risposta in Telegram, mentre i dati già trasmessi restano fuori dal controllo di Jarvis.

Prossimo intervento: JRV-005, isolare la cronologia Gemma tra progetto e contesto generale conservando il modello caricato e gli archivi persistenti. Verificare anche la configurazione applicata al provider quando si modificano contesto massimo e output.

## JRV-004 — Telegram e revoca durante la conferma

Il worker Telegram attende fino a 30 secondi una decisione monouso della console prima di inviare messaggio e contesto recente a GPT. Il collegamento Telegram e il recapito dei messaggi approvati dal proprietario restano separati. Una richiesta scaduta o riferita a un bridge disattivato viene scartata. Il pianificatore usa lo stesso dialogo e conserva la generazione di consenso fino al worker. La disattivazione o la perdita del collegamento GPT revoca l'accesso del worker Telegram. Verifica Windows e collaudo con account reale distinti.

Il trasporto ricontrolla il consenso dopo l’avvio del bridge e prima di scrivere la richiesta. La disconnessione revoca subito planner e Telegram. Telegram scarta le risposte arrivate dopo la revoca. Un piano ricevuto o confermato dopo un cambio di contesto viene scartato prima dell’esecuzione.

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

## JRV-002 — console senza trascrizione vocale, 6 novembre 2026

Confronto tra le candidate `f387779` e `9adc86e`: il percorso da `voice_text` alla riga `TU` non è cambiato con Telegram. Riprodotti due difetti: il profilo Gemma ignorava un modello Vosk presente solo nel profilo sorgente del launcher e lo stato generico di microfono spento sostituiva il messaggio di errore.

Jarvis ora cerca il modello anche nel profilo sorgente e conserva l'errore di avvio del microfono, visibile anche in console. Restano il controllo della hotword e la modalità selezionata. Le due regressioni riprodotte falliscono prima del fix e passano dopo. Suite Windows e prova acustica sul Pavilion da verificare.

## JRV-002 — Ascolto continuo senza parola di richiamo

Il richiamo è richiesto in modalità Hey Jarvis. Ascolto continuo accetta la trascrizione direttamente. Entrambe mostrano sotto TU le richieste riconosciute, provano prima i gestori locali e usano Gemma per le richieste rimaste senza risposta. Durante la dettatura manuale le frasi libere vanno al campo di destinazione e il comando esplicito di arresto funziona anche senza prefisso. Il collaudo acustico sul Pavilion resta da fare.
