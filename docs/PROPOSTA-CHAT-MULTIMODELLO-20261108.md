# Jarvis — Proposta chat tipo KoboldAI Lite, modelli e template per modello

Data 2026-11-08. Stato: **progettazione soltanto, nessun runtime modificato, nessuna build**.
Baseline: Jarvis-014 source `88c2934cbd6081f94fb33fba5f87f1800b07ebc0`. PR #61 resta riservata alla diagnostica dei prompt.

## Requisiti dell'utente

- Riutilizzare nella zona dell'attuale console dell'HUD Jarvis un'interfaccia chat simile a KoboldAI Lite con schede/impostazioni accessibili dalla chat, senza eliminare la console operativa, pulsanti, voce, hotword, Telegram e funzioni Windows.
- Più conversazioni isolate, selezionabili come schede di ChatGPT: `Nuova chat` parte senza l'argomento precedente; torna a una chat esistente senza perdere i messaggi. Progetti e memoria generale devono continuare a rispettare i rispettivi confini.
- Selettore dei modelli GGUF (Gemma, Qwen e altri se compatibili), configurazione separata per modello. **Il formato dei messaggi deve cambiare con il modello**, come nelle impostazioni Instruct di KoboldAI Lite; evitare un template Gemma applicato a Qwen.
- Zero costi aggiuntivi; target Windows 10 / i3-2100 AVX (senza AVX2), RAM 10GB, GPU 1GB, quindi massimo un GGUF caricato alla volta; il cambio modello può richiedere ricaricamento, senza promettere zero attesa.
- Prima ispezionare e misurare i prompt della 014 (PR #61), poi decidere ottimizzazioni Second Brain e cache. Nessuna perdita di salvataggi/conversazioni, nessuna disattivazione arbitraria di verifiche delle azioni.

## Codice attuale verificato

- `jarvis.py`: console a sinistra `tk.Text` in `hud.console_host`, composer e controlli in `hud.command_host`; `write_line` colora i ruoli e mostra anche eventi operativi. Quindi separare visualmente `Chat` e `Console` (tab/pannelli) è una modifica puntuale alla presentazione, ma la logica di invio resta da isolare correttamente.
- `local_model/native_provider.py`: `format_gemma_messages` inserisce *sempre* marcatori Gemma `<start_of_turn>user/model`; non è corretto per Qwen. `native_bridge.py` invia la stringa finale a `upstream.generate` con `stop_sequence=["<end_of_turn>"]` Gemma. Non basta sostituire il file GGUF; vanno rese compatibili anche stop e schema ruoli.
- `NativeModelConfig` ha un percorso GGUF singolo e campi campionamento, ma non profili multimodello.
- `NativeConversationSession` conserva un `deque(maxlen=16)` globale, filtrato per `context_id` (None in chat generale, ID del progetto negli altri casi): non esistono chat generali distinte; Second Brain può recuperare conversazioni dall'archivio generale. La separazione deve valere anche per recupero e ripristino, non soltanto per le schede UI.
- Non confondere sessioni chat multiple con copie del processo/modello: selettore scheda cambia solo history e stato, non il numero di modelli in RAM.

## Riferimento ufficiale KoboldCpp

- https://koboldcpp.net/docs/features/lite/ — Lite prevede Instruct/Chat/Story/Adventure, temi di visualizzazione e impostazioni General, GUI, Samplers, Tokens, Misc.
- https://koboldcpp.net/docs/troubleshooting/output-quality/ — l'uso di tag instruct sbagliati può provocare generazioni anomale; Lite adatta le sequenze di default al modello.
- https://github.com/LostRuins/koboldcpp/wiki/ — AutoGuess.json inferisce heuristically da template Jinja; opzioni per forzare tag di chat.
- https://koboldcpp.net/docs/reference/flags/ — opzioni Jinja/chat template, ma **non assumere** compatibilità con l'ABI KoboldCpp *pin* usata da Jarvis: verificare pin e template disponibile prima di implementare auto-detection.

## Proposta di interfaccia

Nell'area sinistra attuale: barra `[Chat 1] [Chat 2] [+ Nuova chat]`, selettore `Modello: Gemma 2 2B IT ▼`, indicatore modalità `Conversazione / Comando`; corpo `Chat` per bot e utente, scheda `Console` conservata per log tecnico/azioni/errori; campo di invio e microfono esistenti. Impostazioni in pannello secondario, non tutte visibili sempre.

Le impostazioni per modello comprendono file GGUF, template `Auto` con formato rilevato, opzione manuale esplicita se metadata assenti, stop tokens, contesto, output, thread e sampler, personalità eventuale; salvare profili locali senza modificare quello attuale Gemma. Esempi di formati candidati: Gemma 2 e Qwen2.5/Qwen3 ChatML-like, da confermare su GGUF concreto e template tokenizer, non per semplice nome file. Un modello sconosciuto non deve ricevere un template arbitrario e la modifica non deve aprire la possibilità di eseguire capacità fuori allowlist.

Separazione dati: chat ID stabile locale, titolo e cronologia per scheda, selettore delle fonti di memoria; Second Brain globale solo quando autorizzato e pertinente, senza mischiare automaticamente una chat nuova con tutte le altre; progetti/Telegram ancora isolati. Salvataggi atomici/backward-compatible e pulsanti di gestione senza cancellazioni automatiche.

## Implementazione proposta per fasi (non autorizzata ora)

1. Collaudo diagnostica prompt separata PR #61 e misure sul Pavilion; verifica della provenienza dei 400–500 token e confronto KoboldCpp originale in condizioni comparabili.
2. Interfaccia chat/console con schede isolate **senza cambiare motore**, test anti-contaminazione e recupero, mantenere vecchia console accessibile.
3. Motore template per GGUF con rilevamento verificato e fallback manuale; profili per modello e caricamento di **un solo modello alla volta**, test regressione Gemma, Qwen testato con un GGUF reale compatibile, incluse sequenze di stop, end-of-turn e prompt; nessuna dipendenza online.
4. Dopo dati reali, ottimizzazione Second Brain dedup/retrieval e prefix caching senza perdita di qualità. Benchmark effettivi Process/Generated e qualità sul PC, profilo dati intatto.

Rischi: auto-detection imprecisa, meta GGUF mancante, modelli specializzati thinking/tools, stop tokens differenti, compatibilità con CPU AVX; le chat indipendenti devono evitare fughe di memoria globale e non perdere continuità delle chat precedenti. Non promettere che un modello Qwen sarà più rapido o intelligente senza misure.

## Rilascio

La build 014 e l'archivio restano immutabili. La PR #61 NON include queste funzioni. Nessun ZIP 015 o successivo senza autorizzazione, review, test Windows, prova su GGUF e regole canoniche di versione.


## Revisione architetturale — KoboldCpp vs Jarvis (richiesta utente successiva, 8 novembre 2026)

**Stato: valutazione, non approvazione di riscrittura, nessuna modifica runtime e nessuna build.** Questa sezione aggiorna l'ordine consigliato delle fasi precedenti dopo la richiesta di valutare se costruire Jarvis attorno a KoboldCpp oppure il contrario.

### Evidenze (sorgenti della 014 e manuali upstream)
- Jarvis 014 usa **KoboldCpp embedded** con `native_initializer.py`, `native_bridge.py`, `native_provider.py`; non avvia il server HTTP né il web UI KoboldAI Lite. `native_bridge.generate` passa una stringa già formattata, con tag e sequenza di stop Gemma.
- KoboldCpp standalone ufficiale include **KoboldAI Lite in http://localhost:5001**: New Session, Save/Load, Context e schede Settings (General, GUI, Samplers, Tokens, Tools, Misc, Media). Una nuova sessione non equivale automaticamente alla navigazione di più schede persistenti stile ChatGPT: richiede persistenza e un selettore di conversazione aggiuntivi.
- KoboldCpp serve API locali `/api/v1/generate`, `/v1/chat/completions` ecc. e gestisce formati di chat mediante AutoGuess/Jinja. Un client può scegliere il modello tramite Admin / Router Mode, che carica il modello richiesto al bisogno, non più modelli simultaneamente per default.
- KoboldCpp: FastForwarding e ContextShift attivi di default, SmartCache disattivo (ha costo in RAM); la verifica di efficacia della cache va fatta su sequenze reali perché i prompt di Jarvis cambiano con storia/ricordi/routing. Il riuso di prefissi identici può aiutare, ma non azzera il tempo per gli altri token.
- In Jarvis `SecondBrain.prompt_context` può riportare dati recenti e correlati anche se `NativeConversationSession.prepare_turn` ha già inviato la cronologia: **duplicazione possibile, non quantificata**; gli errori JSON operativi richiedono traccia separata.
- Su i3-2100/10GB RAM evitare il doppio caricamento del GGUF. In modalità server impostare bind `127.0.0.1`, non esporre in LAN; username/password admin se usato. La versione attuale KoboldCpp è AGPLv3: eventuale fork o integrazione/copia del frontend richiede verifica degli obblighi di licenza. L'uso tramite API è distinto dal copiare il codice.
- Riferimenti: https://koboldcpp.net/docs/features/lite/ ; https://koboldcpp.net/docs/api/overview/ ; https://koboldcpp.net/docs/settings/context-size/ ; https://koboldcpp.net/docs/settings/admin-mode/ ; https://koboldcpp.net/docs/hardware/old-and-cpu-only/ ; https://github.com/LostRuins/koboldcpp (licenza).

### Scelta di progetto raccomandata (condizionata alle prove)
**Jarvis = orchestratore/sicurezza/voce/progetti/memoria; KoboldCpp = motore GGUF e gestione template/sampler; Lite = frontend di riferimento o base riutilizzabile, da valutare con test.** Non infilare tutte le capacità Jarvis dentro il codice KoboldCpp e non ricostruire alla cieca l'intero Lite in Tk. Il percorso server HTTP loopback sostituirebbe *opzionalmente* l'attuale chiamata DLL in-process, ma introdurrebbe un processo gestito, connessioni, start/stop, incompatibilità versione e UI browser. Non promettere automaticamente prestazioni superiori senza benchmark confrontabile. Il vecchio percorso DLL resta modalità rollback.

Per le chat: un **chat_id** locale per scheda, contenuti, modello e preferenze isolati; **un solo server/GGUF in RAM** per tutte le chat, con generazioni serializzate. Second Brain globale non deve mescolare spontaneamente il contesto di chat nuove: eventuali ricordi globali vanno recuperati solo su scelta/autorizzazione e pertinenza; i dati restano sul disco e i progetti ancora isolati. La console tecnica Jarvis resta accessibile, azioni Windows sempre validate dal motore Jarvis, non direttamente autorizzate da testo/HTML/LLM di Lite.

### Test decisivo prima di scegliere la migrazione

1. Raccogliere con la diagnostica PR #61 il **prompt esatto** e la ripartizione delle fonti della 014, soprattutto quando Second Brain è attivo.
2. Misurare KoboldCpp originale e Jarvis 014 **sullo stesso GGUF, stessa quantizzazione, context 1024, output 256, threads 2/2 e domanda/cronologia confrontabili**, includendo la seconda domanda per testare cache. Raccogliere prompt tokens, Processed tokens e s, Generated tokens e s, RAM e qualità di continuità.
3. Prova locale non distruttiva: KoboldCpp standalone come server **loopback** + piccola connessione *sperimentale*, senza sostituire il provider attuale né avviare due GGUF. Verificare modelli Gemma e Qwen concreti, template/stop, start/stop, timeout, port in use e nessuna esecuzione azioni dal solo output modello.
4. Solo se prestazioni/coerenza e compatibilità passano: elaborare il frontend chat stile Lite con schede/Save&Load e le impostazioni equivalenti, preservando console/voce/add-on e memoria; decidere se interfaccia nel browser locale con Jarvis integrato oppure finestra dedicata. L'integrazione dentro la console Tk può richiedere componente web e RAM extra: misurare prima di sceglierlo.

**Gate:** la 014 rimane disponibile; PR #61 solo diagnostica; nessun code change per questa decisione e nessuna build fino al consenso e ai test. 
