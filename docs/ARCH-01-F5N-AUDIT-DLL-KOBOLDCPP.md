# ARCH-01 / F5N — Audit della DLL nativa KoboldCpp (9 novembre 2026)

## Decisione di prodotto
Jarvis è l'unico programma visibile e l'unica interfaccia. L'utente chiede le **funzioni di KoboldCpp ufficiale direttamente nel motore nativo di Jarvis**, possibilmente con DLL compilata dallo stesso codice sorgente upstream, non un processo KoboldCpp server esterno pilotato da Jarvis. Le funzioni dell'assistente (memoria, strumenti, applicazioni Windows, Telegram) devono restare in Jarvis, separate dalla DLL che effettua l'inferenza; questo evita di riscrivere il motore a ogni nuova azione.

## Evidenza dal codice del progetto
- `local_model/native_factory.py` carica in-process il sorgente upstream `koboldcpp.py` (ABI ctypes), `NativeGemmaBridge` e `NativeLocalProvider`. La DLL predefinita è `native_engine/koboldcpp_noavx2.dll` (non è necessario aprire KoboldCpp standalone).
- `local_model/native_initializer.py` estrae l'inizializzazione dell'upstream, invoca `init_library()`, imposta CPU, `--noavx2`, `--gpulayers 0`, threads, blasthreads e contextsize. Attualmente dipende dalla **struttura AST** del blocco `if __name__`: un aggiornamento upstream può romperla.
- `local_model/native_bridge.py` espone `load()`, `generate()`, `count_tokens()`, `abort()` e aggiornamento dei sampler; `abort()` **non rilascia** necessariamente il GGUF. La generazione invia context, max output, temperatura, top_k, top_p e seed; stop sequence è fissata a `<end_of_turn>` per Gemma.
- `local_model/native_provider.py` e `native_chat_adapter.py` serializzano le conversazioni con `format_gemma_messages`; il template non è ancora scelto dai metadata del vero GGUF. `NativeModelConfig` non espone tutti i controlli di KoboldCpp. `NativeChatAdapter.prepare` richiama `stop()` per sostituire il provider, ma non certifica che la DLL abbia liberato il vecchio modello.
- Le conversazioni persistenti della chat non devono essere modificate per intervenire sul motore. F4.2 su Pavilion è ancora non misurata.

## Verifica puntuale del codice ufficiale
Upstream esaminato: `LostRuins/koboldcpp`, branch `concedo`, commit di riferimento osservato `6d2fedf8624e5f05926af3191f9efdcb13c4133c` (da **verificare/fissare esattamente** prima di compilare). File esaminati: [koboldcpp.py](https://github.com/LostRuins/koboldcpp/blob/concedo/koboldcpp.py), [Makefile](https://github.com/LostRuins/koboldcpp/blob/concedo/Makefile), [README](https://github.com/LostRuins/koboldcpp/blob/concedo/README.md).

- Il Makefile supporta build DLL Windows; su x86 con `LLAMA_PORTABLE` e `LLAMA_NOAVX2` usa le flag `-mavx -msse3 -mssse3`, coerenti con CPU i3-2100 AVX senza AVX2. Serve comunque compilare e testare su Windows.
- L'interfaccia ctypes upstream include `load_model`, `generate`, `abort_generate`, gestione token e `get_chat_template`. Nell'esame del file Python non è emerso un binding pubblico `handle.unload_model` o `def unload_model`; l'opzione amministrativa testuale `unload_model` NON prova l'esistenza di un'API di deallocazione in-process. Questa è una **lacuna da verificare anche nel sorgente C/C++**, non una prova che il rilascio sia impossibile.
- La DLL del repo, nel probe CI Windows precedente, esponeva almeno `load_model`, `generate`, `abort_generate`, `token_count` e alcune metriche. Probe dell'export != prova di corretto unload o generazione Qwen.
- Il README upstream dichiara AGPL-3.0 per KoboldCpp salvo file con licenza differente. Prima di distribuire una DLL ricompilata o modificata occorre verificare obblighi di licenza, disponibilità sorgente corrispondente e attribuzioni di componenti terzi.

## Matrice preliminare di parità

| Funzione | Jarvis DLL corrente | Upstream verificato | Gate per parità |
|---|---|---|---|
| CPU/no AVX2 | Configurata e provata in CI limitata | Build target presente | Inference reale sul Pavilion |
| Modello GGUF Gemma | Caricamento e generazione nativi | load_model/generate | Comparazione stesso GGUF e sampler |
| GGUF Qwen | Non verificato | Dipende da modello e versione | GGUF, tokenizer, template e risposta coerente |
| Context / output / threads / BLAS | Esposti | Opzioni upstream presenti | Equivalenza dei valori applicati |
| Sampler e seed | Sottoinsieme (temp/top_k/top_p/seed) | Più parametri | Inventario campo-per-campo e test |
| Template per famiglia | Solo Gemma attivo | get_chat_template disponibile | Metadata reali e stop tokens corretti |
| Unload e cambio a caldo | **Non certificato** | Nessuna API Python di unload trovata nell'audit | Esaminare C++ e verificare deallocazione |
| Memoria / strumenti di Jarvis | Sono del livello Jarvis | Non sono il compito del motore | Non regredire autorizzazioni/conversazioni |
| Prestazioni rispetto al KoboldCpp originale | Non misurate sul Pavilion | Nessuna equivalenza automatica | F4.2 a condizioni identiche |

## Piano tecnico vincolante, incrementale
1. **F5N.1 — Audit ABI C/C++**: identificare esatta versione/commit della DLL bundled e provenienza, confrontare export ctypes e sorgente C/C++ ufficiale, individuare gestione reale di `llama_model`/context e possibili vie di teardown. Non chiamare `load_model` un secondo GGUF nello stesso processo prima di chiarire questo punto.
2. **F5N.2 — Build riproducibile da upstream**: fissare SHA/tag Git upstream **prima** di compilare, toolchain Windows e flag `LLAMA_PORTABLE=1 LLAMA_NOAVX2=1`, mantenere patch minime isolate e inventario differenze ABI. Prove su runner Windows senza sostituire la DLL distribuita. No Linux test.
3. **F5N.3 — Configurazione compatibile**: derivare l'elenco dei parametri dal codice effettivo upstream, esporre solo quelli supportati dalla DLL; serializzare secondo metadata reali del modello, senza assumere Gemma=Qwen2.5=Qwen3. Aggiungere test di payload e regressione per Console/Chat/Telegram.
4. **F5N.4 — Lifecycle**: dimostrare unload/reload reale se possibile; in assenza di API attendibile non promettere cambio a caldo né sovrascrivere un modello caricato. Valutare isolamento interno alternativo solo se indispensabile e compatibile con il requisito di una sola applicazione.
5. **F5N.5 — Benchmark Pavilion**: stesso GGUF, quantizzazione, contesto, threads, BLAS, prompt, sampling e cache (guida F4.2). Verificare memoria reale e continuità dialogo prima della nuova ZIP.

## Regole di sicurezza e rollback
Nessuna modifica a `main`, DLL bundled, file di configurazione personali, Second Brain, storico chat o ZIP014 durante l'audit. Nessun KoboldCpp standalone da richiedere all'utente come prodotto. Il laboratorio subprocess `owned_kobold_lab_f5.py` resta **fuori** dalla strada principale. Il controllo mock Windows misura solo il software di test; non certifica prestazioni, qualità Qwen, RAM liberata o parità con KoboldCpp ufficiale. Non distribuire DLL senza licenza e sorgenti corrispondenti gestiti correttamente.

## F5N.1 — Evidenze C++ e audit riproducibile (9 novembre 2026)
**Sorgente C++ effettivamente consultato**, upstream commit `6d2fedf8624e5f05926af3191f9efdcb13c4133c`:
- `kcpp_src/expose.cpp`: definisce `load_model(const load_model_inputs)`, `get_chat_template()`, e invoca `gpttype_load_model`; non risulta una definizione `unload_model` in questo file.
- `kcpp_src/model_adapter.h`: dichiara `gpttype_load_model` e `gpttype_generate_abort`, non una corrispondente funzione esplicita di deallocazione generale.
- `kcpp_src/gpttype_adapter.cpp`: **riscontro rilevante**: dentro `gpttype_load_model` compare `kcpp_data = new kcpp_params(); //allocate on heap to avoid linux segfault. yes this leaks memory.` Il codice commenta esplicitamente una perdita di memoria per allocazione. Sono presenti anche usi di `llama_free` e `llama_model_free` legati a contesti secondari/speculative, ma questi non dimostrano il teardown integrale del modello principale. Altri stati del motore sono statici/globali (per esempio `llama_ctx_v4`). Prima di implementare hot-switch serve una verifica delle dipendenze e ownership di **tutte** le risorse, non basta aggiungere una semplice funzione esportata.
- La mancanza di `unload_model` nell'export consultato non dimostra assenza di qualunque meccanismo privato di swap: dimostra soltanto che non abbiamo identificato un'ABI riutilizzabile con garanzia in-process.

**Nuovo strumento:** `tools/f5n_abi_audit.py` inventaria offline il contenuto di `expose.cpp`, i riferimenti `handle.*` in `koboldcpp.py`, e produce SHA-256 e dimensione della DLL esplicitamente fornita dal chiamante. Non esegue il Python upstream, non carica la DLL, non lancia processi/modelli e non fa rete; segnala chiaramente che è una ricerca statica, non una prova dell'export PE o dell'assenza di leak. Aggiunto `tests/test_f5n_abi_audit.py` con fixture finte per evitare di confondere commenti con definizioni reali. I test Windows sono da verificare.

**Per riprodurre su checkout upstream fissato**:
```powershell
python -m tools.f5n_abi_audit --expose-cpp "C:\\koboldcpp\\kcpp_src\\expose.cpp" --kobold-python "C:\\koboldcpp\\koboldcpp.py" --dll "C:\\Jarvis\\native_engine\\koboldcpp_noavx2.dll"
```
Questi percorsi sono esempi, non assumere installazioni reali. Per risultati autorevoli fissare **SHA esatto dei tre file sorgente** e versione/checksum della DLL. L'analisi automatica non modifica Jarvis né prova il consumo RAM sul Pavilion.

**Decisione operativa:** non modificare la DLL per inserire un `unload_model` improvvisato; prima costruire matrice completa delle allocazioni e dei distruttori con test C++ Windows e una prova reale in memoria. Il rischio di corrompere il processo e perdere la sessione prevale sul vantaggio di uno switch prematuro. Un solo Jarvis, nessun backend server come prodotto. ZIP014 e dati invariati.

## F5N.2 — Build Windows nativa riproducibile: procedura preparata (9 novembre 2026)

**Upstream scelto e fissato**: `LostRuins/koboldcpp`, commit `6d2fedf8624e5f05926af3191f9efdcb13c4133c`. Il target Windows del Makefile ufficiale per `make koboldcpp_noavx2 LLAMA_PORTABLE=1 LLAMA_NOAVX2=1` non produce più una DLL monolitica; dipende almeno da `koboldcpp_common.dll`, `koboldcpp_default.dll`, `koboldcpp_noavx2.dll` e dal forwarder `backend_routes/koboldcpp_noavx2/koboldcpp_backend.dll`. Questa è una **incompatibilità potenziale con l'installer attuale** che distribuisce la sola `koboldcpp_noavx2.dll`: non sostituire un unico file.

**Workflow nuovo, SOLO manuale:** `.github/workflows/f5n-koboldcpp-native-dll-windows.yml`, su `windows-2022`, `msys2/setup-msys2` MinGW64, `git clone --recurse-submodules`, `git checkout --detach` della revisione fissata, verifica SHA, compilazione CPU senza AVX2 con `-j2`, controllo presenza quattro DLL, manifest di ricerca e artefatto separato con retention breve. Il workflow non gira sui pull request, non genera una ZIP Jarvis, non aggiorna `native_engine/`, non effettua inferenza né pubblica release. Potrebbero occorrere correzioni allo script in funzione del compilatore MinGW e delle dipendenze upstream: **non è ancora stato eseguito né dichiarato green**.

**Verifica statica indipendente**: `tools/f5n_bundle_audit.py` controlla presenza delle quattro DLL, firma iniziale PE `MZ`, dimensione e SHA-256 senza caricarle. `tests/test_f5n_bundle_audit.py` prova fixture complete/incomplete/corrotte. È un controllo di confezionamento, NON prova che le DLL siano linkabili, che non utilizzino AVX2 accidentalmente, che sia presente unload, che Qwen funzioni o che il Pavilion non rallenti. L'archivio candidato non deve essere consegnato come Jarvis utilizzabile prima di prova runtime, licenze e sorgente corrispondente.

**Procedura per sviluppo:** una volta disponibile in GitHub Actions sul ramo F5, avviare manualmente il workflow F5N.2; controllare build, output dell'audit e struttura dei file con sorgente upstream conservato/identificato, senza installare il candidato. In caso di fallimento, correggere **solo** workflow/toolchain o mismatch upstream e ritestare Windows. Dopo il verde, il successivo gate verifica ABI/forwarder e compatibilità nativa con Jarvis, poi performance Pavilion. La `ZIP014` resta il rollback. Non lanciare file o programmi del candidato sul PC dell'utente finché non ci sono prove.

**Aggiornamento trigger CI:** il nuovo workflow nel ramo feature ora include anche `pull_request` con filtro sui tre file specifici della build, così GitHub può eseguirlo senza doverlo prima registrare su `main`. `workflow_dispatch` resta disponibile quando GitHub lo riconoscerà; la build resta isolata e non tocca gli artefatti utenti. **Non è una build attestata:** primo controllo del commit `3bbe376a...` non restituiva ancora run associati. In caso di mancato avvio, verificare configurazione GitHub Actions/permessi PR e non dichiarare verde.
