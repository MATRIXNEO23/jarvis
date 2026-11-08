# JARVIS — Piano di implementazione: chat stile KoboldAI Lite e gestione multimodello
**Data:** 8 novembre 2026 · **Stato:** F0–F3 implementate/verified on Windows sources, NON pubblicate; F4–F8 pianificate e soggette ai gate. **Versione:** roadmap ARCH-01 v2.
**Baseline runtime immutabile:** Jarvis 014 source `88c2934cbd6081f94fb33fba5f87f1800b07ebc0`, pacchetto `Download/Jarvis-014.zip`, SHA256 `f9c9cd92d1443774e48be89674ce04d9897f47d003df0ad11972ab7815d671c0`. Repository `MATRIXNEO23/jarvis`. Non usare la radice runtime storica di main come punto di partenza.
**Proposta iniziale:** `docs/PROPOSTA-CHAT-MULTIMODELLO-20261108.md`. **Diagnostica separata:** [PR #61](https://github.com/MATRIXNEO23/jarvis/pull/61), verificata su Windows ma NON pubblicata.
**Regole:** `docs/PROTOCOLLO-CANONICO-VERSIONI-JARVIS.md`; per ogni fase, stato nel `docs/REGISTRO-DELTA-VERSIONI-JARVIS.md`, checkpoint in `RECUPERO.md`, codice e test in branch isolato; NO ZIP, merge/main runtime, migratori o cancellazioni automatici. Ogni fase con proprio commit/PR, test Windows, rollback esplicito.

## Obiettivo e risultato desiderato
La zona della console Jarvis deve offrire un'esperienza **molto vicina a KoboldAI Lite**: chat leggibile, gestione istanze/conversazioni (crea, passa, rinomina, salva, riapri), pannello impostazioni organizzato come l'originale (General/GUI/Samplers/Tokens/Tools/Misc ove pertinenti), selettore e profili GGUF (Gemma 2, Qwen e compatibili), scelta automatica/manuale del template corretto, accesso alla precedente console tecnica. Conservare GUI ciano HUD, voce/hotword/mic, Telegram, progetti, add-on e validazione dei comandi Windows.

**Architettura proposta, da dimostrare e non imporre a priori:** Jarvis resta il proprietario delle azioni, profili e memoria; KoboldCpp resta il motore GGUF e in futuro può essere esposto via server locale 127.0.0.1 per usare i suoi endpoint chat/template e l'eventuale frontend Lite. Non esporre azioni Windows al frontend non fidato. Un solo modello caricato, generazioni serializzate: le **istanze sono conversazioni**, non copie di Gemma. Non assumere che la modalità server sia più veloce dell'attuale integrazione ABI.

## Inventario e fatti della 014
- `jarvis.py` ha composer in `hud.command_host`, `tk.Text` in `hud.console_host`, `write_line` che mescola timeline umana ed eventi. Le funzioni restano in Tk: cambiare il pannello di output senza distruggere la console.
- `local_model/native_conversation_session.py`: buffer condiviso `deque(maxlen=16)`, suddiviso per `context_id` (generale=None o progetto). Nessuna istanza generale con ID indipendente.
- `second_brain.py` e `workspace_memory.py` recuperano prove, scambi recenti e risposte in JSON; possono sovrapporsi alla cronologia RAM. La quantità reale si misura con il report PR#61 prima di ottimizzare; l'errore di risposta JSON operativo è un problema distinto.
- `local_model/native_provider.py` forza i tag `<start_of_turn>user/model`, `native_bridge.py` forza stop `<end_of_turn>`: non compatibili automaticamente con Qwen. `native_initializer.py` avvia direttamente il DLL KoboldCpp, NON il server web Lite.
- `local_model/native_config.py` ha un singolo file GGUF e parametri generazione; non contiene profili per modello.
- CLI/servizio KoboldCpp upstream: API native `/api/v1/`, chat `/v1/chat/completions`; `/props` e `/api/extra/perf` permettono controllo; template per modello AutoGuess/Jinja; FastForwarding attivo e ContextShift condizionato dal modello. SmartCache opzionale usa RAM.

Fonti originali controllate (2026-11-08):
- https://koboldcpp.net/docs/api/overview/
- https://koboldcpp.net/docs/api/endpoints/
- https://koboldcpp.net/docs/settings/context-size/
- https://koboldcpp.net/docs/settings/launcher-tour/
- https://koboldcpp.net/docs/faq/ (licenza KoboldCpp/Lite AGPL-3.0)
Il riferimento *grafico* al frontend upstream non autorizza a copiarne sorgenti senza verificare licenza, dipendenze e distribuzione. Configurazioni più recenti dell'upstream non sono garantite dal PIN incorporato nella 014.

## Architettura di responsabilità (proposta)
```text
     UI Jarvis sinistra: Chat/Console/Impostazioni stile Lite
              |  selezione chat_id + profilo modello
       Jarvis orchestratore (voce, hotword, permessi)
          |                       |
   ChatSessionStore          Validatore azioni Windows
 (solo dati chat isolati)    Telegram / progetti / add-on
          |
      Native model transport (attuale DLL, futuro server SOLO se supera i gate)
          |
    Un KoboldCpp + un GGUF alla volta
          ^
   Second Brain (ricordi separati, solo se autorizzati/pertinenti)
```

## Fasi piccole e gate

### F0 — Congelamento base e pianificazione (ora)
**Input:** source 014, PR#61 diagnostica, piano/registro/versioning. **Output:** piano nel main, branch di implementazione derivato dal source 014, PR draft contro un branch archivio esatto della 014, checkpoint recuperabile.
**Gate:** confermare commit base, assenza di modifiche a profili/dati, diff preciso; il piano è salvato prima del codice. **Rollback:** abbandonare branch; avviare ZIP 014 originale.

### F1 — Fondazione delle istanze locali, senza toccare l'app esistente (primo intervento codice)
**Obiettivo minimo:** storage isolato, opt-in, solo Python standard library; una chat con ID stabile, titolo, scope generale/progetto, data e scambi utente/modello; crea/lista/seleziona/rinomina e legge, anche dopo riapertura. **Nessun avvio GGUF, processo nuovo, connessione web, richiesta e nessun import/instanziazione nel runtime 014.** Non copiare dati dal Second Brain né migrare tabelle.
**File previsti:** nuovo `local_model/chat_sessions.py`, test `tests/test_chat_sessions.py`, documenti/checkpoint. DB separato solo quando usato esplicitamente; operazioni SQL atomiche; niente eliminazione automatica; titolo modificabile e archivio esplicito in futuro.
**Accettazione:** ID non collisione, partizione per progetto, nomi UTF-8, persistenza di due chat con messaggi distinti, switch senza mescolare scambi, riapertura invariata, errore controllato su ID sconosciuto/errato, zero effetti collaterali su Sessione Gemma/Second Brain, test Windows e nessuna regressione. Nessuna garanzia UI prima della F2.
**Rollback:** vecchio Jarvis ignora il nuovo modulo e archivio; branch non distribuito. Se in futuro il DB viene creato, si conserva senza eliminazione.
**Stato iniziale:** DA IMPLEMENTARE.

### F2 — Chat e console in area HUD
**Obiettivo:** sidebar/elenco o tab per conversazioni, Nuova chat, Apri, Salva/rinomina e ritorno alla precedente; vista `Chat` separate da `Console` (log/azioni/errori). Widget entro `hud.console_host` e composer esistente; senza nuovo web runtime obbligatorio. L'utente deve poter comandare a voce le istanze. Memoria scelta per istanza; prototipo usa Gemma attuale.
**Test:** Tk Windows, routing invio testo/voce, cambio chat con generazione in corso respinto o annullato in modo sicuro, persist after restart, nuova chat senza storia vecchia anche se Second Brain global è attivo, assenza di perdita di messaggi. Non rimuovere la console originale.
**Gate UX:** confrontare una schermata col riferimento Lite e verificare se la superficie Tk è abbastanza vicina; in caso contrario, esplorare Lite/WebView2 separatamente, misurandone RAM, compatibilità e licenza prima di aggiungerlo.

### F3 — Diagnostica e baseline quantitativa del motore
**Obiettivo:** integrare/fornire opt-in la diagnostica PR#61 senza incrociarla silenziosamente alle altre patch; test non sensibili su tre domande e follow-up a parità di GGUF/context/output/threads e memoria on/off. Confronto Jarvis vs KoboldCpp originale con prompt/tokens/qualità/tempi e riuso prefissi.
**Gate:** distinguere token del prompt, `Processed` realmente processati, tempo prefill, tempo generazione, latenza totale e PSS/RAM. Non tagliare ricordi a intuito.

### F4 — Adattatore KoboldCpp locale opzionale, canary senza sostituire DLL
**Obiettivo:** sperimentare API locali del server originale su `127.0.0.1`, un backend alla volta, senza far partire il secondo GGUF assieme al primo. Confronto e rollback instantaneo verso provider DLL, timeout/disconnessione/porta occupata, versione incompatibile, no fallback online.
**Test:** process/API start/stop, modello assente, token/template, abort, coda, permessi; verifica su Windows e i3. **Decisione:** se non porta un vantaggio misurato, rimanere sulla DLL e riusare solo le impostazioni UX di Lite.

### F5 — Modelli multipli/profili e template
**Obiettivo:** scelta file GGUF Gemma/Qwen, un modello attivo per volta, settaggi per profilo e template Auto da metadata (quando disponibile) o override manuale con anteprima. Parametri separati per modello: Threads/BLAS, Context, MaxOutput, temp, top-p/k, seed, stop strings, modalità thinking/tool ove compatibile. Impostazioni equivalenti a Lite raggruppate per tab, non riprodurre ogni controllo non pertinente.
**Gate:** GGUF reale per ciascuna famiglia, test stop/role/tool, ripristino Gemma 014 esatto, nessuna azione da chat non validata, Qwen che fallisce non rende inutilizzabile Gemma; test non promette velocità o qualità superiori.

### F6 — Second Brain selettivo e cache (solo in base a prove)
**Obiettivo:** separare memoria globale, di progetto, di singola conversazione. Nuova chat parte pulita per la conversazione ma memoria globale richiamata solo con consenso/pertinenza. Deduplica fondata sulle misure; ultimo riferimento protetto. FastForwarding e eventuale SmartCache (solo se RAM lo consente) misurati. No compressione generativa per turno sul Pavilion.
**Gate:** qualità e memoria almeno pari alla 014 su gold set, verifica 0 incroci, no falsi ricordi/JSON, prestazioni misurate; rollback delle singole scelte.

### F7 — Stabilizzazione, pacchetto e collaudo
**Gate:** Windows Python 3.11/3.12, DLL/GGUF reale, ZIP estratto e UI, profili legacy, hotword, voce, Telegram, azioni e sicurezza. Numero di build nuovo e immutabile, SHA256 e manifest, Download, publish solo **se l'utente richiede esplicitamente una build**. Nuova cartella di estrazione; rollback ZIP 014. La prova CI non sostituisce il Pavilion dell'utente. Review indipendente prima di dichiarare pronto.

## Tracciabilità e ripristino a ogni fase
1. Prima: riga di change nel registro (ID `JRV-ARCH-01-Fx`), obiettivo, source SHA, test RED/gap, rischi, rollback.
2. Durante: branch/checkpoint dedicati, commit piccolissimi per codice/test/doc; nessuna scrittura in Download e nessuna sovrascrittura file esistenti della 014; aggiornamento `RECUPERO.md` a inizio e fine fase, e `docs/DECISIONI-E-LEZIONI.md` a esito.
3. Dopo: `compare_commits` contro source 014, link test Windows con numeri reali, controllo dati e `STATO-ATTIVITA.md`; nuovo passo solo se gate passato. Se RED dopo fix, bloccare promozione e conservare evidenza.
4. Rollback codice = selezionare commit baseline o branch predecessore; rollback installazione = chiudere nuova app e usare Jarvis-014.zip estratto precedentemente. **Mai cancellare** `%LOCALAPPDATA%/Jarvis`, `JARVIS_TRIAL_HOME`, memoria/progetti, file di autorizzazione o gli archivi nuovi.
5. Profili GGUF ed eventuali DB nuovi in percorsi sidecar/nuovo schema; caricamento legacy sempre leggibile. Prove distruttive soltanto su profili temporanei.

## Decisioni e criteri di stop
- Non scegliere anticipatamente WebView2: embedding Lite aggiunge processi e RAM sul Pavilion. Un'interfaccia Tk strutturata può bastare se corrisponde alla UX desiderata; se la fedeltà Kobold richiede browser, valutarlo con prototipo separato e budget RAM misurato.
- Se un passaggio peggiora la qualità/coerenza, sbaglia tag Qwen, mischia istanze o rompe sicurezza delle azioni, si ferma e si torna al commit precedente.
- Nessun nuovo costo, account o API remota; l'accesso HTTP, se introdotto, resta loopback isolato.
- L'autorizzazione dell'utente copre l'avvio dell'implementazione passo passo e salvataggio del piano, **non autorizza automaticamente nuove release** né riscritture invasive.


## Stato di avanzamento e checkpoint verificato — 8 novembre 2026
- F0: **COMPLETATA**. Piano versionato su main, source 014 congelato e branch isolato.
- F1: **COMPLETATA NEI SORGENTI**. PR draft [#62](https://github.com/MATRIXNEO23/jarvis/pull/62), modulo `local_model/chat_sessions.py` e test, source `2f3c8d207ab1aff41d578fca6e48d606f7cd00d3`. RED [42529168718](https://github.com/MATRIXNEO23/jarvis/actions/runs/42529168718), GREEN [42529275925](https://github.com/MATRIXNEO23/jarvis/actions/runs/42529275925) **1022 test PASS per Windows 3.11 e 3.12**, prova nativa [42529275993](https://github.com/MATRIXNEO23/jarvis/actions/runs/42529275993) SUCCESS. Documentazione verificabile `docs/ARCH-01-F1-CHECKPOINT.md` sul ramo.
- F2: **IMPLEMENTATA NEI SORGENTI E VERIFICATA DA CI WINDOWS**. [PR draft #63](https://github.com/MATRIXNEO23/jarvis/pull/63), runtime commit `026f150953962bffe39404fb62312e1ec5dc8239`, suite [42532269337](https://github.com/MATRIXNEO23/jarvis/actions/runs/42532269337) SUCCESS con 1030 test per job (Python Windows 3.11/3.12), tokenizer nativo [42532269371](https://github.com/MATRIXNEO23/jarvis/actions/runs/42532269371) SUCCESS. UI Chat locali/Console in HUD, istanze persistent scoped, routed voice/typed Gemma con reader soltanto per chat attiva. Non ingloba la PR #61, non attiva server KCPP, Qwen o API online, non cambia il Second Brain legacy. **Nessuna build 015/ZIP nuova, nessun collaudo Pavilion**, ZIP014 immutabile.
- F3: **IMPLEMENTATA E GREEN SU WINDOWS CI**. [PR draft #64](https://github.com/MATRIXNEO23/jarvis/pull/64) su F2 importa il lavoro già verificato in PR#61, aggiunge attribuzione corretta delle chat F2 e prove di prompt immutato. [Run 42533254766](https://github.com/MATRIXNEO23/jarvis/actions/runs/42533254766) SUCCESS **1040 test per job** Windows 3.11/3.12, [tokenizer 42533254794](https://github.com/MATRIXNEO23/jarvis/actions/runs/42533254794) SUCCESS. Protocollo [confronto Pavilion](https://github.com/MATRIXNEO23/jarvis/blob/feature/jarvis-kobold-chat-f3-20261108/docs/ARCH-01-F3-PROTOCOLLO-BENCHMARK.md) pronto ma **ancora non eseguito sul dispositivo reale**. Nessun prompt, inferenza o Second Brain modificati.
- F4–F7: **NON INIZIATE**; passaggio server KoboldCpp F4 condizionato al confronto effettivo. F8 provider API con chiavi personali e piani gratuiti eventuali è pianificata separatamente, non implementata.
- Release: **NESSUN nuovo ZIP**, 014 intatta; nessun test utente Pavilion attribuito a F1.


## Requisito aggiuntivo ARCH-01 / F8 — provider online con chiavi API (richiesta 8 novembre 2026, durante la F2)
**Stato: progettato, non implementato in F2.** L'utente desidera aggiungere, oltre a GPT e ai GGUF locali, un selettore di più provider online utilizzando chiavi API personali, compresi endpoint con piano gratuito quando effettivamente disponibile. Evitare di promettere gratuità permanente o compatibilità con ogni provider.

**Contratto proposto per F8, dopo F2 e i gate modelli F5:**
1. Estendere lo stesso selettore modelli/provider della chat: `Locale KoboldCpp`, `GPT collegato`, `API provider`, con configurazione separata per ogni provider e modello. Supportare un adapter standard OpenAI-compatible **solo quando** gli endpoint sono realmente compatibili; adapter specifico per gli altri.
2. Parametri per provider `base_url`, `model_id`, `max_output`, `context`, `temperature`, timeout, budget/limiti e capabilities, senza convertire automaticamente JSON o tool calling fra formati eterogenei.
3. Credenziali archiviate mediante Windows Credential Manager o protezione equivalente del sistema, non in JSON plaintext, log, prompt, clipboard automatica, SQLite chat o repository. Import/export profili **senza segreti**. Connessioni HTTPS verso endpoint ufficiali, no HTTP non locale, nessuna esecuzione arbitraria di URL suggeriti dal modello.
4. Ogni chat con provider/modello selezionato; costo e privacy visibili prima dell'invio. Nessun fallback invisibile dal locale a provider online e nessun invio di Second Brain/documenti/progetti senza consenso esplicito e policy per fonte. Separare le conversazioni e gli spazi di progetto anche fra servizi.
5. Il piano gratuito, rate limit, accesso API e condizioni cambiano: catalogo solo da fonti ufficiali e ricontrollo al momento dell'integrazione; non trattare abbonamento ChatGPT come credito API.
6. Errori quota, rete, autorizzazione e provider gestiti senza perdere il messaggio e senza eseguire azioni. Nessuna esecuzione azioni locali da testo del provider senza attuale validatore e permessi.
7. Mock test offline (chiavi mai vere in CI), test di concorrenza/cancellazione, protezione credenziali, backup non distruttivo e controllo consumi. Nessun nuovo SDK obbligatorio per chi usa solo Gemma.

**Ordine:** F2 chat/console e isolamento → F3 diagnostica/benchmark → F4/F5 motore/template e picker → F6 memoria/caching → F8 adapter API online (può precedere la F7 di rilascio finale, ma non entra nella build F2). **Rollback:** disattivare adapter e usare percorso locale 014; non cancellare le credenziali o le chat salvo richiesta esplicita. Nessuna implementazione o account API creati in questa fase.
