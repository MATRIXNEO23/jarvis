# Gemma nativa — checkpoint configurazione (2026-11-04)

## Evidenza verificata
- Run 41866803511: SUCCESS su Windows 2022, inferenza Gemma 2 2B Q4_K_M tramite DLL CPU senza launcher/server. La correzione UTF-8 è nel commit 24a3587.
- Il test non misura parità di velocità con KoboldCpp sul Pavilion i3-2100, né prova l'integrazione nell'interfaccia Jarvis.
- local_model/runtime.py è ancora un contratto incompleto e i suoi test precedenti si riferiscono al percorso eseguibile/server. Non sostituirlo implicitamente.

## Scelta e modifica
- Creato local_model/native_config.py: impostazioni native persistenti e validate, con scrittura atomica e protezione del file precedente quando i parametri sono invalidi.
- Creati tests/test_native_model_config.py e workflow Windows native-config.yml.
- Parametri: DLL, GGUF, threads, batch_threads, context_size, max_output, temperature, top_k, top_p, seed.
- La configurazione non avvia il modello, non modifica le preferenze correnti di Jarvis e non richiede download/API.

## Stato e prossimo passo
- Modifica pubblicata nel ramo feature/gemma-local-20261104. Esito CI da verificare prima di dichiarare superati i test.
- Implementare un adattatore DLL isolato e arrestabile, con timeout, errori sicuri e controllo della concorrenza; prima ispezionare API native e lifetime reali della libreria fissata.
- Collegare al ModelService solo dopo prova Windows di almeno due turni, regressioni e verifica delle impostazioni.
- Prestazioni e stabilità sul Pavilion: NON VERIFICATE. Nessuna build installabile pubblicata.

## Diagnosi CI e correzione 2026-11-04
- Run 41868898297 FAILED: 3/4 test superati; test_reject_bad_parameters falliva perché il test forniva la sequenza letterale \\x00 anziché un vero carattere NUL. Corretto il fixture con chr(0), commit b511486.
- Run 41868856559 FAILED: workflow preesistente local-model, 8 fallimenti nel contratto legacy di local_model/runtime.py ancora incompleto. Non è una regressione dimostrata della configurazione nativa e non è stato disabilitato o modificato.
- Attendere esito della nuova CI Windows prima di dichiarare verificata la configurazione; poi affrontare il contratto legacy separatamente, decidendo se mantenerlo o migrare con test.

## Checkpoint successivo — bridge isolato
- Run 41869848924 SUCCESS: test Windows della configurazione nativa.
- Aggiunto local_model/native_bridge.py: contratto di caricamento singolo e generazione con impostazioni configurate; non lancia server o processi.
- Aggiunti test con upstream fittizio e workflow native-bridge.yml. Questi test NON verificano la DLL reale.
- Limitazione bloccante: il modulo upstream KoboldCpp richiede inizializzazione ABI, argomenti e libreria prima di load_model; la prova tools/probe_native_gemma.py la esegue, il bridge attuale non la riproduce. NON collegare il bridge a Jarvis o distribuirlo prima di completare e verificare l'inizializzazione reale.
- Il timeout del bridge non interrompe ancora una chiamata C bloccante. Non dichiarare capacità di annullamento o equivalenza di prestazioni. Il runtime legacy continua a fallire i test separati.

## Checkpoint inizializzazione (2026-11-04)
- Run 41870600838 SUCCESS: test del bridge con ABI simulata. Run 41870562360 FAILED: contratto runtime legacy ancora incompleto.
- Il bridge ora richiede una callback esplicita di inizializzazione ABI prima di load_model: senza callback rifiuta il caricamento, evitando false inizializzazioni.
- Creato native_initializer.py che replica la preparazione argomenti CPU/noAVX2 della prova pinned upstream, ma il caricamento della DLL esatta e la compatibilità dell'intero ciclo di vita NON sono ancora verificati in un workflow di inferenza reale integrata.
- Workflow native-initializer.yml testa il contratto con fake, non la DLL reale. Non pubblicare build né dichiarare integrazione Jarvis completata.

## Verifica reale del bridge avviata
- Run 41871634418 SUCCESS: inizializzatore/contratto con upstream simulato; non equivale a generazione reale.
- Nuovo script tools/probe_native_bridge_real.py e workflow native-bridge-real.yml: eseguono su Windows 2022 la DLL pinned con SHA256 verificato e GGUF verificato, chiamando NativeGemmaBridge.load/generate per due prompt. Report JSON pubblicato come artifact se disponibile.
- Run iniziale 41872170746: in coda al momento del checkpoint. In caso di errore leggere log e correggere la causa, non dichiarare passaggio completato.
- Restano da fare: timeout/cancellazione reali, eventuale compatibilità dell'ABI, instradamento verso ModelService e UI, impostazioni utente, benchmark su Pavilion, test regressione; non generare ZIP automaticamente.

## Integrazione servizio locale (checkpoint)
- Run 41873044370 SUCCESS: DLL reale + GGUF hanno generato due risposte attraverso NativeGemmaBridge su Windows CI. Non è un benchmark sul Pavilion.
- Run 41873759981 SUCCESS: contratto NativeLocalProvider con prompt singolo/multi-turno.
- Aggiunta native_factory.py: costruzione esplicita del provider in-process (senza attivazione automatica).
- Aggiunto test_native_service_routing.py e workflow native-service-routing.yml: verifica che ModelService instradi localmente e non usi GPT online senza consenso. Run 41874409746 avviata, esito da controllare.
- Restano non verificati: cablaggio UI/app principale, distribuzione DLL/modello, timeout/cancel robusti, prestazioni CPU AVX del PC reale e vecchio runtime legacy (workflow rosso). Non pubblicare ZIP.

## Arresto e timeout nativi
- Run 41874409746 SUCCESS: instradamento ModelService e consenso online verificati con fake.
- Aggiunto NativeGemmaBridge.abort(): segnala stop e invoca abort_generate() se disponibile, senza prendere il lock della generazione.
- NativeLocalProvider.stop() inoltra l'abort senza attendere il lock del provider.
- NativeGemmaBridge.generate() scarta il risultato se abortito o se il tempo è già scaduto. Il timeout NON preempta la chiamata nativa bloccante: non dichiarare hard timeout.
- Nuovi test Windows tests/test_native_abort.py e workflow native-abort.yml, run 41874727654 avviata (esito da verificare).
- Rischi ancora aperti: thread safety del backend C, cancellazione reale su DLL, race di stop, UI/impostazioni, benchmark hardware reale. Il runtime legacy resta rosso.

## Revisione ABI abort 04/11
- Run 41874727654 SUCCESS per test finto di abort e timeout, NON prova cancellazione della DLL reale.
- Analisi del sorgente KoboldCpp upstream pinned 7e0eb2d: la funzione è `upstream.handle.abort_generate()`, NON `upstream.abort_generate()`. Corretta la chiamata in native_bridge.py e adeguato FakeUpstream dei test.
- Estesa la prova reale per verificare la presenza di `handle.abort_generate` sulla DLL caricata, senza rischiare di interrompere una generazione live non ancora testata. Workflow Windows avviato automaticamente.
- Mancano ancora prova di cancellazione durante generazione reale, hard timeout, cablaggio UI e benchmark Pavilion. Non dichiarare queste capacità come verificate.

## Prova cancellazione reale
- Run 41875814331 SUCCESS: generazione reale attraverso bridge e presenza ABI abort verificata.
- Run 41875796810 SUCCESS: test di contratto cancellazione con fake aggiornato.
- Nuovo script tools/probe_native_abort_real.py: avvia una generazione lunga in thread, richiede abort mentre è attiva, verifica completamento entro 15 s e assenza di risposta restituita. Il test fallisce se la generazione termina prima dell'abort (inconcludente).
- Nuovo workflow .github/workflows/native-abort-real.yml, run 41878329249 in coda al checkpoint. L'esito deve essere verificato prima di dichiarare cancellazione reale funzionante.
- Nessuna build, nessuna modifica alla UI; test isolato Windows CI. Benchmark Pavilion e hard timeout non verificati.

## Impostazioni native isolate
- Run 41878329249 SUCCESS: cancellazione durante generazione reale Windows CI, entro la finestra del test. Non è benchmark Pavilion né garanzia di hard timeout.
- Aggiunto local_model/native_settings.py con campi editabili e indicazione di reload per modello/context/threads, senza applicare modifiche a generazione in corso. Percorso separato: %LOCALAPPDATA%/Jarvis/addon-data/modello_locale/native.json; prova isolata JARVIS_TRIAL_HOME.
- Aggiunti tests/test_native_settings.py e .github/workflows/native-settings.yml (esito da verificare); corretto rifiuto di NaN/inf nella configurazione nativa.
- ATTENZIONE: questo è il contratto delle impostazioni, NON ancora pannello UI integrato; i parametri avanzati KoboldCpp inventariati in docs/GEMMA-IMPOSTAZIONI-20261104.md non sono ancora tutti collegati alla DLL. Nessuna build.

## Preparazione build con UI isolata
- Run 41881063593 SUCCESS: configurazione nativa editabile, isolata dal settings.json principale, verificata Windows.
- Le skill disponibili via catalogo sono per documenti/media/Drive, non per sviluppo Python Windows; seguire istruzioni AGENTS.md e skill Archify del repository quando disponibile. La skill .agents/skills/archify/SKILL.md non è presente in questo ramo (404), non inventarne contenuti.
- Creato local_model/native_ui.py: pannello Tk opt-in per GGUF, Context Size, Max Output, thread, temperatura, Top-K/P, seed; Salva, Sfoglia, ripristina campi, messaggi ricaricamento. Non carica/attiva la DLL, non modifica la UI principale né settings.json.
- Test Tk Windows tests/test_native_ui.py e workflow native-ui.yml aggiunti; esito da verificare.
- GATE BUILD: non pubblicare una build finché il pannello non è raggiungibile dall'interfaccia reale, il provider non è cablato al ModelService nel programma, il runtime legacy rosso non è chiarito, e non sono superate regressioni Windows. Prestazioni KoboldCpp sul Pavilion ancora non misurate. L'utente ha autorizzato l'obiettivo di arrivare a una build, non la distribuzione di un prototipo difettoso.

## Integrazione pulsante impostazioni nella UI Jarvis
- Run 41884682083 SUCCESS: pannello Tk separato testato Windows.
- Modificato jarvis.py: nella scheda esistente «GPT e memoria» aggiunto pulsante «Configura Gemma locale...» che apre NativeSettingsWindow solo su richiesta, senza caricare DLL né cambiare instradamento GPT.
- Aggiunto tests/test_native_settings_entry.py e aggiornato workflow native-ui.yml per verificare l'entrypoint; nuovo run da verificare.
- La configurazione NON rende Gemma utilizzabile nella chat: provider reale non ancora collegato al percorso di chiamata Jarvis. Il contratto legacy executable/server resta incompatibile e workflow rosso; non mascherare la regressione. Non creare build pubblica prima di risolvere entrambi.

## Fase 3 — predisposizione collegamento conversazione
- Creati local_model/native_chat_adapter.py (NativeChatAdapter) e local_model/chat_transport.py (ChatTransport): adapter usa factory nativa e restituisce dizionario text, transport separa richieste e non fa fallback online.
- jarvis.py: worker conversazione instradato attraverso ChatTransport, per ora con native non disponibile e use_native=False implicito. GPT esistente resta predefinito, senza cambiamento di comportamento. Telegram continua sul GPT esistente.
- tests/test_native_chat_transport.py e workflow native-chat-routing.yml creati, esito Windows da verificare.
- STOP prima della fase 4 come richiesto dall'utente: spiegare opzioni di selezione manuale, autorizzazione GPT per singola richiesta e comportamento in caso di errore; non abilitare Gemma automaticamente.
- Non dichiarare completa integrazione Gemma in chat prima del selettore e prova reale end-to-end in Jarvis. Nessuna build.

## Memoria compatta locale — prima implementazione
- local_model/compact_context.py: finestra scorrevole di 8 messaggi (configurabile), archivio persistente JSON atomico, estratti sintetici rolling ogni 8 messaggi archiviati, budget caratteri massimo. Dati memorizzati non sono comandi né autorizzazioni.
- tests/test_compact_context.py e workflow compact-context.yml: verificano limite, ripresa, persistenza e file danneggiato. Esito Windows da controllare.
- ATTENZIONE: digest deterministico per estratti, non vero riassunto semantico; non è ancora collegato all'inferenza Gemma e non garantisce conservazione di fatti importanti. Evitare di definirlo completo.
- Richiesta utente: sintetizzare carattere, umore e fatti importanti senza allungare il prompt; futuro riassunto semantico incrementale nei periodi di inattività, con verifiche contro perdita di decisioni e riferimenti.

## Impostazioni memoria e inattivita (richiesta utente)
- Default 60 secondi di inattivita, regolabile 10-3600 secondi; ultimi 8 messaggi; ogni 8 messaggi; 150 token riassunto; 600 token budget prompt; un lavoro alla volta; conversazione prioritaria, pausa carico alto, sintesi background attive come preferenze.
- Aggiunti local_model/memory_preferences.py (dataclass con validazione e persistenza atomica), local_model/memory_ui.py (dialogo Tk) e pulsante nella scheda GPT e memoria di jarvis.py.
- Test tests/test_memory_preferences.py e .github/workflows/memory-preferences.yml; verificare esito run 41891499740.
- Run 41890983269 compact-context SUCCESS.
- CRITICO: scheduler idle, sospensione reale su carico alto, enforcement priorita/abort e sintesi semantica NON implementati. Questi campi sono preferenze persistenti ma non ancora operative. Il budget prompt e in token configurati ma compact_context limita caratteri, serve token budgeting effettivo.

## Ripresa dopo blocco pubblicazione
- Run 41891499740 Memory preferences SUCCESS; 41890983269 Compact context SUCCESS; native routing 41891469742 SUCCESS.
- Aggiunto metodo MemoryPreferences.available_prompt_tokens(context_size, max_output, reserve=128), con test per finestra 512/2048 e configurazioni impossibili. Commit a5e3d875, test commit 62e010a8. Non equivale a conteggio token reale né a collegamento alla DLL.
- Da fare: applicare il budget al prompt realmente inviato, scheduler inattivita e priorita, sintetizzatore semantico e integrazione completa. Legacy Local model contract ancora fallisce: indagare, non disattivare.

## Sessione 04/11 — verifica skill e riparazioni
- Skill installate verificate: nessuna skill di programmazione/Archify disponibile; non dichiarare di averla usata. Usati test e GitHub Actions Windows.
- Causa verificata Local model contract rosso: local_model/runtime.py era uno stub (validate no-op, save no-op, load default, command vuoto), contraddiceva tests/test_local_model_runtime.py. Ripristinato contratto legacy con validazione, persistenza atomica e comando solo come lista; non avvia EXE ne server. Commit 9acf6eee. Run 41915731799 da verificare.
- Aggiunto local_model/idle_memory_gate.py: gate cooperativo senza thread, 60 s da preferenze, un solo lavoro, priorita conversazione, controllo carico e retry se lavoro non salvato. Test tests/test_idle_memory_gate.py e workflow idle-memory-gate.yml, run 41915760750 da verificare.
- Memory preferences Windows run 41904633981 SUCCESS. Budget finestra esposto tramite MemoryPreferences.available_prompt_tokens.
- NON ancora completo: nessun timer/event loop Jarvis collegato al gate, nessuna inferenza di sintesi semantica, nessun abort preemptivo verificato su CPU utente, nessun conteggio token reale nella pipeline nativa. Non consegnare build finale come pronta.

## Integrazione budget al confine della DLL
- Commit 5a1d8064: NativeChatAdapter ora verifica MemoryPreferences.available_prompt_tokens prima della generazione quando riceve prompt testuale. Limite caratteri volutamente conservativo, non tokenizzazione GGUF. Prompt fuori budget rifiutato, non troncato silenziosamente.
- Test con provider fittizio test_native_adapter_budget.py, commit 6dd6cd63; workflow native-chat-routing aggiornato commit d25bee13; run 41916822847 inizialmente queued, esito da controllare.
- Attenzione: percorso conversazione principale jarvis.py usa ancora ChatTransport con _UnavailableNative e use_native=False. Non dichiarare Gemma collegato alla UI finche selezione locale e caricamento sono reali. Non consegnare ZIP.
