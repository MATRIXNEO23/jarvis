# Proposta di riordino 058 (solo proposte: NIENTE è stato spostato, unito o tolto)

Regola: ogni scelta nuova aspetta l'ok dell'utente (AGENTS.md, «Chiedere con opzioni»). Ogni proposta ha: cosa, perché, rischio, alternativa. Dati ricavati leggendo il codice (import statici e dinamici `__import__`) il 18/11.

## a) File nella radice del programma

La radice ha 124 file: 96 moduli Python, 9 launcher e script (`avvia_lumi.bat`, `installa_*.bat/.ps1`, `configura_telegram.bat`), `gpt_bridge.mjs` e testi di documentazione. Tutti i file tracciati da git finiscono nel pacchetto (`tools/build_jarvis_f5_candidate.py`), salvo i `.md`, `.yml`, `tests` e le eccezioni elencate lì. Importati da `jarvis.py` in modo statico o con `__import__("nome")`: tutti tranne i due sotto.

### Da togliere o spostare fuori dal pacchetto

**A1. `prepara_test_telegram50.py` (140 righe) e `LEGGIMI_PROVA_TELEGRAM_50.txt`**
- Cosa: Spostare lo script in `tools/` e il testo in `docs/`. Lo script prepara i dati per una prova di 50 messaggi Telegram: non lo importa nessun file di Lumi, solo 3 test.
- Perché: È uno strumento da sviluppatore, non serve a chi usa Lumi, e oggi finisce nel pacchetto.
- Rischio: Basso: vanno corretti i 3 test che lo importano (`test_file_access`, `test_hud_ui_regressions`, `test_telegram_trial_launcher`).
- Alternativa: Lasciarlo dov'è ma escluderlo dal pacchetto con una riga in `include()` della build.

**A2. `installa_modello_voce.py` (94 righe)**
- Cosa: Spostare in `tools/` oppure dentro la cartella voce quando esisterà. Lo lancia solo `installa_voce.bat`; nessun modulo lo importa.
- Perché: Serve a installare una voce una volta sola, non fa parte dell'avvio.
- Rischio: Medio-basso: va aggiornato il percorso in `installa_voce.bat`; se si sbaglia l'installazione della voce non parte.
- Alternativa: Lasciarlo in radice (nessun rischio, resta un file in più).

**A3. Testi storici nella radice: `LEGGIMI-ACCESSO-FILE.txt`, `RECUPERO.md`, `ROADMAP.md`, `README.md`**
- Cosa: Spostare `LEGGIMI-ACCESSO-FILE.txt` in `docs/` (`RECUPERO.md` è già escluso dal pacchetto). Il `.txt` oggi entra nel pacchetto dell'utente ma parla di una build vecchia.
- Perché: L'utente trova nella cartella solo ciò che gli serve.
- Rischio: Basso: nessun codice lo legge; da controllare che nessun `.bat` lo citi.
- Alternativa: Lasciarlo e aggiornarne il contenuto.

**A4. Tre programmi di installazione voce: `installa_voce.bat` (22 righe), `installa_voce_edge.bat` (18), `installa_voce_naturale.bat` (32)**
- Cosa: Unirli in un solo `installa_voce.bat` che chiede quale voce installare (circa 50 righe). Fanno la stessa cosa con voci diverse.
- Perché: Meno file in radice e una sola istruzione per l'utente.
- Rischio: Medio: se il file unito sbaglia un percorso, la voce non si installa; il pacchetto estratto va provato su Windows. Non posso verificarlo su Linux.
- Alternativa: Tenerli separati ma spostarli in una cartella `installazione/`.

**A5. `installa_gpt.bat` (13 righe) + `installa_gpt.ps1` (67) + `gpt_bridge.mjs`**
- Cosa: Nessuna unione: sono tre pezzi di un'unica funzione (il ponte con ChatGPT). Proposta: spostare i tre in `gpt/` insieme a `gpt_client.py` (249 righe).
- Perché: Raggruppa un'unica responsabilità.
- Rischio: Medio: `gpt_client.py` è importato da 7 file e il `.bat` cita i percorsi; vanno corretti tutti insieme e provato il login GPT.
- Alternativa: Non toccarli finché il ponte GPT non si riscrive.

### Da unire (stessa funzione). Lunghezza indicata = righe del file risultante

**A6. Documenti: `document_recovery` (18) + `document_execution` (44) + `project_documents` (84) + `document_language` (77) → `document_tools.py` (circa 223 righe)**
- Cosa: Quattro piccoli moduli che lavorano sullo stesso tema: recupero, esecuzione, lingua e documenti del progetto. Restano fuori `document_dialog` (185), `document_store` (123) e `managed_documents` (165), già di buona dimensione.
- Perché: Meno file (4 → 1) senza creare un file lungo.
- Rischio: Medio: sono importati da `jarvis.py`, `conversazione_lumi.py` e `lumi_parti/documenti_progetti.py` con `__import__`; una svista dà un errore solo a runtime. Servono test che importino ogni nome.
- Alternativa: Spostarli soltanto in una cartella `documenti/` senza unirli (più sicuro, stessa pulizia).

**A7. Chat: `chat_link` (56) + `chat_ruoli` (68) + `chat_stream` (112) → `chat_utili.py` (236 righe)**
- Cosa: Tre moduli piccoli, tutti usati solo dalla chat in `jarvis.py` (chat_stream anche da `conversazione_lumi`).
- Perché: Meno file, tutti sul tema «testo della chat».
- Rischio: Basso-medio: cambiano 3 import; `chat_stream` ha uno stato globale (`STREAM`) che non deve duplicarsi.
- Alternativa: Lasciarli separati.

**A8. Tendine: `menu_modello` (67) + `menu_ricerca` (97) + `menu_modelli` (183) → `menu_tendine.py` (347 righe)**
- Cosa: Le tre tendine della barra in alto (modello, ricerca, elenco modelli) condividono già `menu_modelli`.
- Perché: Una sola fonte per le tendine, utile anche per il restyling finale.
- Rischio: Medio: il clic delle tendine è stato corretto nella 057 (bug del Label dentro il tasto); un'unione sbagliata lo riapre. Test `test_056c_tendine` da riverificare.
- Alternativa: Rimandare all'inizio del restyling.

**A9. Memoria: `ricordi` (143) + `ricordi_ui` (97) + `cancella_memoria` (62) → `ricordi.py` (302 righe)**
- Cosa: Elenco e finestra dei ricordi e cancellazione della memoria.
- Perché: Stessa funzione: gestire i ricordi.
- Rischio: Medio: la cancellazione chiede conferma e tocca dati dell'utente; richiede test sulla cancellazione a sezioni (053).
- Alternativa: Unire solo `ricordi` e `ricordi_ui` (240 righe) e lasciare `cancella_memoria` a parte.

**A10. Dialogo: `dialogue_style` (100) + `dialogue_focus` (128) → `dialogue.py` (228 righe); `plan_runner` (34) + `action_planner` (181) → `action_planner.py` (215 righe)**
- Cosa: Coppie che si chiamano a vicenda (`conversation_router` importa tutte e due).
- Perché: Meno file senza file lunghi.
- Rischio: Medio-basso: import in `conversation_router`, `jarvis_persona`, `planner_ui`.
- Alternativa: Lasciarli separati.

**A11. Voce: `speech_activity` (72) + `voice_style` (66) + `preference_voice` (68) → `voce_preferenze.py` (206 righe)**
- Cosa: Piccoli moduli sulle preferenze e sull'attività della voce; `voice_control` (465) e `piper_voice` (560) restano come sono.
- Perché: Meno file sulla stessa responsabilità.
- Rischio: Medio: `voice_style` è usato da `edge_voice`, `lumi_parti/voce.py` e `jarvis.py`.
- Alternativa: Spostarli in una cartella `voce/` insieme agli altri moduli voce (`voice_control`, `piper_voice`, `edge_voice`, `offline_tts`, `audio_player`, `adaptive_voice`, `desktop_dictation`, `project_voice`, `la_mia_voce`).

**A12. HUD: `hud_orbits` (155) + `hud_backdrop` (182) + `hud_raster` (270) + `hud_reference` (568) + `barra_tasti` (134) + `slide_modalita` (58) + `network_telemetry` (101) + `animated_hud` (761)**
- Cosa: Non unirli (sarebbe un file da oltre 2200 righe): spostarli in una cartella `hud/`.
- Perché: Sono 8 file sulla stessa responsabilità e ora sono sparsi tra altri 90.
- Rischio: Medio: `meteo/icone.py` importa `hud_reference`; il test `test_056c_barra_meteo` e le prove a 1366x768 vanno ripetuti.
- Alternativa: Lasciarli in radice fino al restyling (il restyling li riscrive comunque).

**A13. `finestra_adatta.py` (46 righe, nuovo della 058) in `window_chrome.py` (205) → 251 righe**
- Cosa: Le due fanno parte della stessa funzione: l'aspetto e la posizione delle finestre.
- Perché: Evitare un file nuovo in più.
- Rischio: Basso. `window_chrome` oggi esce subito su Linux; il test della 058 importa `finestra_adatta` da solo.
- Alternativa: Lasciarli separati: il modulo nuovo è importabile senza Windows.

**A14. Telegram nella radice (11 file, 1.700 righe in totale: `telegram_bridge` 535, `telegram_ui` 192, `telegram_vista` 245, `telegram_voice` 182, `telegram_directory` 134, `telegram_outbound_flow` 120, `telegram_security` 107, `telegram_commands` 35, `telegram_secret_dialog` 138, `configura_telegram` 143)**
- Cosa: Spostarli nella cartella dell'add-on (vedi parte b, ultimo passo). Unioni possibili solo allora: `telegram_commands` + `telegram_security` + `telegram_directory` (276 righe) e `telegram_secret_dialog` + `configura_telegram` (281 righe).
- Perché: È l'unico add-on con codice sparso nella radice.
- Rischio: Alto: `telegram_security` è importato da 13 file e Telegram è l'add-on con più prove dal vivo (33 test).
- Alternativa: Lasciare Telegram com'è: è la scelta già decisa (Telegram per ultimo).

### Cartelle per responsabilità (opzionale, dopo le unioni)

**A15. Cartelle `hud/`, `voce/`, `documenti/`, `chat/`, `diagnostica/`, `modello_dialogo/`**
- Cosa: Raggruppare i moduli rimasti per tema (oggi 96 file in una sola cartella). Una cartella per volta, con un pacchetto `__init__.py` e gli import corretti.
- Perché: Chi riprende il lavoro trova subito dove mettere le mani.
- Rischio: Alto per `jarvis.py` (5349 righe, usa `__import__` con nomi di stringa che nessuna ricerca di import trova): ogni spostamento richiede cercare anche le stringhe. La CI Windows è l'unica prova valida.
- Alternativa: Fare solo A1-A5 (tolti dal pacchetto) e rimandare il resto.

## b) Add-on: file, punti che li richiamano, cartella `addon/<nome>/` e ordine

Struttura proposta: cartella `addon/` (con `__init__.py`) e dentro `addon/<nome>/` con il `.jaddon` accanto al codice. Il nome della cartella resta quello attuale, così `from meteo...` diventa `from addon.meteo...`. Punti che ogni spostamento deve correggere in ogni caso: (1) la tabella di installazione in `jarvis.py` (riga ~392: `(id, cartella, file .jaddon)`, percorso `Path(__file__).parent / folder / file_name`); (2) `addon_manager.py` (controllo dell'identità di ogni azione); (3) `tools/build_jarvis_f5_candidate.py` (elenco dei LEGGIMI esclusi, righe 26-29, e `include()`); (4) i test che citano il percorso; (5) `.github/workflows` (23 file di workflow nominano `local_model/`, `file_access/` o `program_apps/` nei filtri di percorso e in `py_compile`); (6) i `.jaddon` già installati dall'utente nel profilo dati (copiati: cambiano solo se la versione cambia, perciò il percorso nuovo non li tocca); (7) `diagnostica_claude` (elenca gli add-on).

Ordine: dal più semplice al più legato. Dopo ogni add-on: correggere i punti, `py_compile`, CI Windows verde, poi build vera e controllo dal vivo che l'add-on si carichi (comando di prova da `lumi_diagnostica`). Un add-on per build.

### b1. sveglia (`sveglia/`, 3 file, `.jaddon`: Sveglia)

- Chiamato da 24 file di codice: `addon_manager.py` (2), `addon_righe.py` (1), `animated_hud.py` (2), `chat_ruoli.py` (1), `command_aliases.py` (7), `controllo_pc/commands.py` (2), `controllo_pc/service.py` (1), `conversation_router.py` (1), `frasi_lumi.py` (4), `impostazioni_menu.py` (2), `jarvis.py` (8), `jarvis_timer.py` (2), `la_mia_voce.py` (1), `local_help.py` (14), `local_model/conversazione_lumi.py` (1), `lumi_avatar.py` (2), `lumi_comandi.py` (7), `lumi_parti/documenti_progetti.py` (1), `lumi_parti/interfaccia.py` (2), `lumi_parti/modello_memoria.py` (1), `lumi_parti/voce.py` (1), `musica/commands.py` (2), `scheda_lumi.py` (1), `self_diagnostics.py` (1).
- Test che lo citano: 11 (`test_056b_hud_layout.py`, `test_056c_barra_meteo.py`, `test_command_aliases.py`, `test_diagnostic_inventory.py`, `test_frasi_lumi.py`, `test_impostazioni_menu.py`, `test_local_help.py`, `test_musica.py`, `test_passo11.py`, `test_sveglia.py`, `test_typed_timer_routing.py`).
- Workflow e pacchetto: nessun workflow lo nomina; il pacchetto prende tutto ciò che è in git, quindi lo spostamento è già incluso, salvo le eccezioni in `include()`.
- Documenti che lo citano: 12 (da aggiornare a mano).
- Passo 1: spostare in `addon/sveglia/`, correggere i punti sopra e gli import dinamici `__import__("sveglia...")`.

### b2. meteo (`meteo/`, 10 file, `.jaddon`: Meteo)

- Chiamato da 8 file di codice: `addon_manager.py` (10), `addon_righe.py` (1), `animated_hud.py` (4), `command_aliases.py` (27), `diagnostica_claude/server_mcp.py` (1), `jarvis.py` (46), `local_help.py` (15), `tools/build_jarvis_f5_candidate.py` (1).
- Test che lo citano: 10 (`test_052_servizi_ricerca.py`, `test_054_catena_gpt.py`, `test_056_diagnostica.py`, `test_056_meteo.py`, `test_056b_aiuto_meteo.py`, `test_056b_barra_meteo.py`, `test_056b_hud_layout.py`, `test_056c_barra_meteo.py`, `test_056c_cronologia_e_profilo.py`, `test_058_meteo.py`).
- Workflow e pacchetto: nessun workflow lo nomina; il pacchetto prende tutto ciò che è in git, quindi lo spostamento è già incluso, salvo le eccezioni in `include()`.
- Documenti che lo citano: 8 (da aggiornare a mano).
- Passo 2: spostare in `addon/meteo/`, correggere i punti sopra e gli import dinamici `__import__("meteo...")`.

### b3. musica (`musica/`, 16 file, `.jaddon`: Musica)

- Chiamato da 21 file di codice: `addon_manager.py` (2), `addon_righe.py` (1), `addon_ui.py` (4), `chat_ruoli.py` (2), `command_aliases.py` (14), `componenti/catalog.py` (2), `componenti/ui.py` (1), `controllo_pc/commands.py` (3), `controllo_pc/runtime.py` (2), `controllo_pc/service.py` (3), `conversation_router.py` (1), `intent_normalizer.py` (1), `jarvis.py` (13), `local_help.py` (6), `lumi_avatar.py` (5), `meteo/runtime.py` (1), `orchestratore.py` (2), `scheda_lumi.py` (4), `self_diagnostics.py` (1), `tools/build_jarvis_f5_candidate.py` (6), `tools/video_host_smoke.py` (1).
- Test che lo citano: 9 (`test_addon_righe.py`, `test_command_aliases.py`, `test_componenti.py`, `test_diagnostic_inventory.py`, `test_intent_normalizer.py`, `test_musica.py`, `test_native_catalog_cues.py`, `test_passo9.py`, `test_richiamo_e_chi_sono.py`).
- Workflow e pacchetto: nessun workflow lo nomina; il pacchetto prende tutto ciò che è in git, quindi lo spostamento è già incluso, salvo le eccezioni in `include()`.
- Documenti che lo citano: 5 (da aggiornare a mano).
- Passo 3: spostare in `addon/musica/`, correggere i punti sopra e gli import dinamici `__import__("musica...")`.

### b4. programmi_app (`program_apps/`, 7 file, `.jaddon`: ProgrammiApp)

- Chiamato da 15 file di codice: `addon_manager.py` (2), `addon_ui.py` (2), `command_aliases.py` (1), `jarvis.py` (10), `local_engine.py` (11), `local_help.py` (2), `local_model/conversazione_lumi.py` (7), `notepad_controller.py` (1), `self_diagnostics.py` (1), `tools/build_file_access.py` (1), `tools/build_gemma_clean_trial.py` (1), `tools/build_jarvis_f5_candidate.py` (1), `tools/check_build006.py` (2), `tools/check_file_access_package.py` (11), `tools/prepare_build006.py` (1).
- Test che lo citano: 13 (`test_command_aliases.py`, `test_diagnostic_inventory.py`, `test_gemma_package_sources.py`, `test_internal_command_routing.py`, `test_local_help.py`, `test_native_project_history.py`, `test_operational_guide_selection.py`, `test_program_apps.py`, `test_program_apps_integration.py`, `test_program_apps_native.py`, `test_program_apps_service.py`, `test_program_apps_ui.py` …).
- Workflow e pacchetto: nessun workflow lo nomina; il pacchetto prende tutto ciò che è in git, quindi lo spostamento è già incluso, salvo le eccezioni in `include()`.
- Documenti che lo citano: 17 (da aggiornare a mano).
- Passo 4: spostare in `addon/program_apps/`, correggere i punti sopra e gli import dinamici `__import__("programmi_app...")`.

### b5. accesso_file (`file_access/`, 9 file, `.jaddon`: AccessoFile)

- Chiamato da 17 file di codice: `addon_manager.py` (3), `addon_ui.py` (2), `command_aliases.py` (1), `jarvis.py` (22), `local_engine.py` (15), `local_help.py` (2), `local_model/conversazione_lumi.py` (1), `program_apps/native.py` (1), `self_diagnostics.py` (1), `tools/build_file_access.py` (1), `tools/build_gemma_clean_trial.py` (2), `tools/build_jarvis_f5_candidate.py` (2), `tools/check_build006.py` (2), `tools/check_file_access_package.py` (4), `tools/prepare_build006.py` (1), `tools/probe_file_access_windows.py` (1), `tools/probe_windows_search_live.py` (1).
- Test che lo citano: 18 (`test_052_gestori_locali.py`, `test_054_catena_gpt.py`, `test_activity_status.py`, `test_addon_concurrency.py`, `test_command_aliases.py`, `test_diagnostic_inventory.py`, `test_file_access.py`, `test_file_context_delivery.py`, `test_file_index_priority.py`, `test_file_refinement.py`, `test_file_search_deadline.py`, `test_file_search_phrase.py` …).
- Workflow e pacchetto: `avvia_lumi.bat`, `configura_telegram.bat`.
- Documenti che lo citano: 44 (da aggiornare a mano).
- Passo 5: spostare in `addon/file_access/`, correggere i punti sopra e gli import dinamici `__import__("accesso_file...")`.

### b6. controllo_pc (`controllo_pc/ + controllo_comune/`, 15 file, `.jaddon`: ControlloPC)

- Chiamato da 10 file di codice: `addon_manager.py` (2), `addon_righe.py` (1), `addon_ui.py` (4), `aiuto_comandi.py` (2), `command_aliases.py` (2), `jarvis.py` (8), `scheda_lumi.py` (1), `self_diagnostics.py` (2), `tools/build_jarvis_f5_candidate.py` (7), `tools/uia_host_smoke.py` (5).
- Test che lo citano: 5 (`test_aiuto_e_scheda.py`, `test_componenti.py`, `test_controllo_pc.py`, `test_diagnostic_inventory.py`, `test_passo11.py`).
- Workflow e pacchetto: nessun workflow lo nomina; il pacchetto prende tutto ciò che è in git, quindi lo spostamento è già incluso, salvo le eccezioni in `include()`.
- Documenti che lo citano: 2 (da aggiornare a mano).
- Passo 6: spostare in `addon/controllo_pc/`, correggere i punti sopra e gli import dinamici `__import__("controllo_pc...")`.

### b7. modello_locale (`local_model/`, 45 file, `.jaddon`: ModelloLocale)

- Chiamato da 20 file di codice: `contesto_lumi.py` (3), `contesto_online.py` (1), `diagnostica_claude/strumenti.py` (2), `jarvis.py` (27), `lumi_parti/documenti_progetti.py` (1), `lumi_parti/interfaccia.py` (1), `menu_modello.py` (3), `scheda_lumi.py` (6), `self_diagnostics.py` (1), `tools/build_gemma_clean_trial.py` (2), `tools/build_jarvis_f5_candidate.py` (5), `tools/check_build006.py` (1), `tools/f42_benchmark.py` (2), `tools/f5n_gguf_smoke.py` (4), `tools/f5n_initializer_smoke.py` (1), `tools/probe_jarvis014_native.py` (4), `tools/probe_native_abort_real.py` (3), `tools/probe_native_bridge_real.py` (3), `tools/probe_native_context_integration.py` (4), `tools/probe_native_prompt_performance.py` (6).
- Test che lo citano: 85 (`test_052_codice_online.py`, `test_052_diagnostica.py`, `test_052_scelta_modello.py`, `test_054_catena_gpt.py`, `test_054_profili_modelli.py`, `test_055_correzioni_ci.py`, `test_055_gpt_in_lista.py`, `test_055_modelli.py`, `test_055_ricerca_ui.py`, `test_056_barra.py`, `test_056_catena.py`, `test_056b_ciao_non_ripete.py` …).
- Workflow e pacchetto: nessun workflow lo nomina; il pacchetto prende tutto ciò che è in git, quindi lo spostamento è già incluso, salvo le eccezioni in `include()`.
- Documenti che lo citano: 33 (da aggiornare a mano).
- Passo 7: spostare in `addon/modello_locale/`, correggere i punti sopra e gli import dinamici `__import__("modello_locale...")`.

### b8. diagnostica_claude (`diagnostica_claude/ (non è un .jaddon)`, 6 file, `.jaddon`: -)

- Chiamato da 4 file di codice: `jarvis.py` (4), `la_mia_voce.py` (1), `orchestratore.py` (1), `tools/build_jarvis_f5_candidate.py` (1).
- Test che lo citano: 6 (`test_052_diagnostica.py`, `test_055_diagnostica_versione.py`, `test_055_gpt_in_lista.py`, `test_056_diagnostica.py`, `test_056b_contesto_online.py`, `test_passo9.py`).
- Workflow e pacchetto: nessun workflow lo nomina; il pacchetto prende tutto ciò che è in git, quindi lo spostamento è già incluso, salvo le eccezioni in `include()`.
- Documenti che lo citano: 3 (da aggiornare a mano).
- Passo 8: spostare in `addon/diagnostica_claude/`, correggere i punti sopra e gli import dinamici `__import__("diagnostica_claude...")`.

### b9. telegram (`telegram_addon/ + 9 file telegram_*.py, configura_telegram.py nella radice`, 5 file, `.jaddon`: Telegram)

- Chiamato da 19 file di codice: `barra_tasti.py` (1), `capability_registry.py` (1), `configura_telegram.py` (3), `jarvis.py` (70), `live_capabilities.py` (4), `local_model/conversazione_lumi.py` (12), `lumi_contesto.py` (3), `lumi_parti/documenti_progetti.py` (8), `lumi_parti/interfaccia.py` (9), `lumi_parti/modello_memoria.py` (9), `lumi_parti/voce.py` (8), `musica/config.py` (1), `program_apps/service.py` (1), `self_diagnostics.py` (2), `servizi_online/__init__.py` (1), `telegram_bridge.py` (5), `telegram_directory.py` (7), `telegram_voice.py` (1), `tools/build_jarvis_f5_candidate.py` (3).
- Test che lo citano: 33 (`test_054_catena_gpt.py`, `test_056b_barra_meteo.py`, `test_activity_status.py`, `test_addon_lifecycle.py`, `test_diagnostic_inventory.py`, `test_file_access.py`, `test_file_context_delivery.py`, `test_file_refinement.py`, `test_live_capabilities.py`, `test_lumi_contesto.py`, `test_native_cancellation.py`, `test_native_command_intents.py` …).
- Workflow e pacchetto: `configura_telegram.bat`.
- Documenti che lo citano: 13 (da aggiornare a mano).
- Passo 9: spostare in `addon/telegram/`, correggere i punti sopra e gli import dinamici `__import__("telegram...")`.

**B1. Spostare gli add-on in `addon/<nome>/`, uno alla volta, nell'ordine b1→b9 (Sveglia, Meteo, Musica, Programmi e app, Accesso file, Controllo PC, Modello locale, Diagnostica per Claude, Telegram per ultimo)**
- Cosa: Una cartella per add-on come ha chiesto l'utente (18/11 notte, punto 2). Ordine per numero di punti che lo richiamano: Sveglia ha 3 file, Telegram 5 più 11 nella radice.
- Perché: Ogni add-on è un blocco isolato che si può togliere o aggiornare senza toccare il resto.
- Rischio: Alto per Modello locale (45 file, 85 test, importato dal cuore di `jarvis.py`) e per Telegram. Basso per Sveglia e Meteo. Rischio comune: stringhe `__import__` e percorsi nei `.jaddon` non trovati da una ricerca di import.
- Alternativa: Spostare solo Sveglia, Meteo, Musica, Programmi e app, Accesso file e Controllo PC (i sei sicuri) e lasciare Modello locale e Telegram dove sono.

**B2. `controllo_comune/` (con `uia_host`) e `musica/video_host` insieme al loro add-on**
- Cosa: Seguono Controllo PC e Musica in `addon/controllo_pc/` e `addon/musica/` (nel pacchetto va il compilato, il sorgente C# è escluso da `include()`).
- Perché: Il sorgente C# e la sua build sono usati solo da quell'add-on.
- Rischio: Medio: la CI compila i host con percorsi nel workflow (`--video-host`, `--uia-host`); cambiano.
- Alternativa: Lasciarli dove sono finché non si sposta l'add-on.

## c) Domande aperte della 057 da riproporre

**C1. «Mic» senza scritta**
- Cosa: Nella barra in alto il tasto microfono mostra la parola «Mic» (`animated_hud.py` riga 721) e lo stato lo dà il simbolo ⏻ azzurro o arancione. Proposta: togliere la scritta e lasciare solo il simbolo disegnato.
- Perché: Libera spazio sulla barra a 1366 pixel.
- Rischio: Basso, ma chi non vede il colore (azzurro/arancione) perde il testo come indizio.
- Alternativa: Tenere «Mic» e accorciare le altre scritte; oppure scritta solo al passaggio del mouse.

**C2. Numero dei messaggi Telegram non letti**
- Cosa: Mostrare vicino al simbolo Telegram quanti messaggi non sono stati ancora letti.
- Perché: Si vede subito se qualcuno ha scritto.
- Rischio: Medio: serve un contatore persistente in `telegram_bridge` e va azzerato quando si apre la chat; Telegram è l'ultimo add-on da toccare.
- Alternativa: Solo un puntino acceso, senza numero.

**C3. Frase di «meteo domani»**
- Cosa: Oggi dice: «Domani a <città>: <cielo>, minima X e massima Y gradi.» Proposta di decidere la frase finale (ad esempio aggiungere la probabilità di pioggia, che ora i nuovi comandi già mostrano).
- Perché: Rendere uguali le frasi di domani, giorno preciso e riepilogo.
- Rischio: Basso: cambia solo il testo in `meteo/service.py`; vanno aggiornati i test.
- Alternativa: Lasciare la frase com'è.

**C4. Taglio a 120 caratteri**
- Cosa: I comandi del meteo ignorano frasi più lunghe di 120 caratteri (`meteo/commands.py`, per non confondere una domanda lunga con un comando). Proposta di confermare il limite o di cambiarlo. Se la domanda riguardava un altro taglio a 120 caratteri (per esempio nei titoli delle chat o nell'anteprima dei risultati), va indicato quale: nel codice non l'ho potuto identificare con certezza.
- Perché: Evitare che frasi lunghe sul tempo atmosferico finiscano al comando invece che al modello.
- Rischio: Basso: una frase lunga («che tempo farà a Roma sabato mattina, secondo te?») passa al modello.
- Alternativa: Alzare il limite a 200 caratteri.


## Riepilogo

Proposte in totale: **22** (a: 15, b: 2, c: 4, d: 1, più i 9 blocchi informativi per add-on).

## Aggiunte dopo la richiesta del 17/11 05:04 (GPT nella tendina)

Verifica fatta: `chatgpt_account` NON è un servizio diverso (OAuth/Codex): è già il GPT dal browser, perché risponde con `ACCOUNT["chiedi"]` che chiama lo stesso `service.call("ask", …)` del pulsante GPT (`gpt_client` / `gpt_bridge.mjs`). Il difetto era solo nella tendina e nelle impostazioni, che lo trattavano come un servizio a chiave: corretto nella fase A (stato «collegato / non collegato», pulsante «Collega», niente chiave, descrizione senza la quota di Codex). Nessun servizio è stato cancellato.

**D1 (non più proposta: deciso dall'utente alle 04:06 e implementato nella fase A).** La pagina separata «Connessione ChatGPT / GPT dal browser» è sparita: stato, Collega/Scollega e «Autorizzazioni GPT per funzione» stanno dentro «Servizi online», sotto l'elenco, nella voce ChatGPT.

**D2. Nome visibile della voce**
- Cosa: oggi si chiama «ChatGPT (tuo account)». Proposta: «GPT dal browser», come la pagina e il pulsante in alto.
- Perché: un solo nome per una sola cosa.
- Rischio: basso, ma `chatgpt_account` e il nome compaiono in impostazioni salvate e in 8 test: il nome interno resta, cambia solo il testo.
- Alternativa: lasciare «ChatGPT (tuo account)».
