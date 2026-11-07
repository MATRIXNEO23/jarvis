## Aggiornamento008 — 7 novembre2026, correzione verificata nei sorgenti in bozza

Il pannello attuale esiste: modello, thread CPU/batch, contesto, max output, temperatura, top-k/top-p, seed e carattere. Inventario sotto storico; gli altri controlli restano proposte. La correzione008 applica i valori salvati alla prossima richiesta serializzata: samplers senza reload; modello/thread/contesto e DLL interna con reload. Salva non avvia inferenza. [Specifica008](superpowers/specs/2026-11-07-jrv-aud-008-design.md); Windows run42344534309 SUCCESS,747test per Python3.11/3.12. [Rapporto008](CORREZIONE-JRV-AUD-008-20261107.md); nessun nuovo pacchetto.

# Impostazioni configurabili — mappa dal codice KoboldCpp1.121

Stato: inventario tecnico, UI ancora da implementare. Fonte immutabile koboldcpp.py, commit7e0eb2dc4a23f1a0fc42a7660ad43be7a4b9e759, funzioni load_model e generate. Il sampler può ricavare default dall’adapter scelto: non spacciare un valore base per quello misurato nella chat dell’utente. Il preset della chat e il file .kcpps effettivi del PC non sono stati acquisiti.

## Pagina principale proposta

| Controllo utente | Campo nativo | Applicazione |
|---|---|---|
| Modello GGUF | load_model_inputs.model_filename | caricamento |
| Context Size | max_context_length di caricamento e generazione | allocazione/contesto; gestione riavvio da verificare |
| Max Output | generation_inputs.max_length | prossima generazione |
| Thread CPU | load_model_inputs.threads | caricamento |
| Thread prompt/batch | load_model_inputs.blasthreads | caricamento |
| Batch Size | load_model_inputs.batchsize | caricamento |
| Temperatura | generation_inputs.temperature | prossima generazione |
| Top-K / Top-P / Min-P | top_k / top_p / min_p | prossima generazione |
| Ripetizioni: penalità, finestra, pendenza | rep_pen / rep_pen_range / rep_pen_slope | prossima generazione |
| Seed | generation_inputs.seed, parametro sampler_seed | prossima generazione |
| Formato Gemma / template | prompt costruito e jinja_template se usato | prompt o caricamento secondo campo |

## Avanzate CPU e memoria

mmap, mlock, Direct I/O; ContextShift, FastForward, SmartContext e SmartCache/slots; Flash Attention e quantizzazione KV K/V; SWA/prevent_swa/padding; priorità processo; BOS; override contesto/RoPE. Esistenza del campo non dimostra vantaggio o compatibilità col modello: verificare ogni opzione scelta. GPU layers restano zero nel profilo CPU dell’i3/Radeon richiesto; non introdurre auto-offload. Nessun blocco arbitrario8192 se il backend consente contesti più grandi: UI mostra costo e limiti reali, con validazione dell’allocazione.

## Avanzate generazione da mantenere configurabili

Top-A, Typical-P (API typical), TFS, N-Sigma, presence penalty; Mirostat/tau/eta; XTC threshold/probability; ordine sampler; temperatura dinamica range/exponent; smoothing factor/curve; adaptive target/decay; DRY multiplier/base/allowed_length/penalty_last_n/sequence_breakers; stop sequences; EOS allow/bypass; grammar/retain_state; token bans e logit bias dove supportati. Semantica, limiti e combinazioni vanno ripresi da generate e dal backend prima di esporli. Non inviare chiavi mai consumate dal motore.

## Salvare e confrontare

Configurazione versionata nel profilo addon-data/modello_locale, fuori dal codice e dagli aggiornamenti. Configurazione attiva distinta da modifiche non ancora applicate. Pulsanti Salva/Applica, Ripristina default e stato ricaricamento; durante generazione non cambiare a metà l’istanza nativa. Conservare modello/profilo/dati utente nel rollback. Nessuna impostazione del microfono modificata implicitamente.

Per confronto prestazioni serve snapshot di ogni opzione attiva in Kobo e nell’add-on, identità GGUF e prompt tokenizzato, non soltanto thread e temperatura. Context Size e Max Output restano distinti; memoria conversazione Jarvis e KV cache non sono la stessa cosa. Risposta completa e output troncato non sono prove equivalenti.
