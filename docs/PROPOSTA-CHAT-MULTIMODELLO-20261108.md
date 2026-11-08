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
