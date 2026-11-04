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
