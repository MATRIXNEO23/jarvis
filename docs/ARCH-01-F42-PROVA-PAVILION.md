# F4.2 — Come misurare Jarvis e KoboldCpp senza perdere nulla

**Stato:** strumento di benchmark sperimentale, non incluso nella build 014 pubblicata. Esiste solo sul ramo `feature/jarvis-kobold-f42-benchmark-20261109` ([PR #66](https://github.com/MATRIXNEO23/jarvis/pull/66)). **Non è stato eseguito sul Pavilion.**

## Condizioni che devono restare uguali
Prima del confronto annotare: stesso GGUF/quantizzazione Gemma 2 2B IT Q4_K_M, Context Size 1024, Max Output 256, Threads e BLAS 2, sampler, seed, cache cold/warm, impostazione Second Brain e domanda esatta. Chiudere il motore embedded Gemma di Jarvis **prima** di avviare KoboldCpp standalone: un solo modello GGUF in RAM sul Pavilion. Nessun API online, nessun accesso remoto, nessun nuovo abbonamento o chiave.

### 1) Preparare il foglio dati (nessuna rete o generazione)
Nel checkout del ramo di prova:
```powershell
python -m tools.f42_benchmark template > f42-misure.json
```
Il file contiene quattro casi (KoboldCpp originale, Jarvis Console Brain OFF e ON, Jarvis Chat locale) con campi vuoti e **nessun testo privato**. Compilare SOLO i numeri dei log e della diagnostica dei prompt. Indicare il valore reale di `total_seconds`, `quality_ok` (true/false/null), `cache_state`, `model`, `sampler`, `threads` e `blas_threads`; mettere `null` per conteggi non disponibili. **Non aggiungere** campi come `prompt`, `response`, nomi, recapiti o `api_key`: lo strumento li rifiuta. `prompt_sha256` è l'impronta SHA-256 del prompt effettivo; lasciarla null quando non misurata.

### 2) Registrare i tempi di Jarvis
Sulla build che comprende F3 (non ancora pubblicata), aprire **Impostazioni Gemma → Diagnostica prompt... → Acquisisci prossima domanda**, inviare una domanda, poi **Aggiorna**. Annotare soltanto:
- il numero totale di token del prompt;
- `Processed N ... in X seconds` dai log del motore (può differire dal totale prompt per effetto della cache);
- `Generated N ... in Y seconds`;
- tempo totale osservato, contesto, Second Brain ON/OFF e un giudizio di qualità/continuità;
- memoria RAM in MB se misurata esternamente (Gestione attività Windows), altrimenti null.
Non condividere il testo integrale del report: può contenere conversazioni e ricordi. La diagnostica non altera il prompt né cancella memoria. Per Brain OFF usare soltanto il toggle temporaneo, **mai cancellare i dati**.

### 3) Misurare KoboldCpp originale (soltanto su richiesta esplicita)
Con **KoboldCpp standalone già avviato manualmente** in locale, stessa configurazione, senza Jarvis GGUF embedded aperto:
```powershell
python -m tools.f42_benchmark probe
```
Mostra il nome modello caricato; non genera testo. Per una/due domande sintetiche e pubbliche:
```powershell
python -m tools.f42_benchmark server --model "NOME_ESATTO_DEL_PROBE" --allow-generation --turns 2 --output f42-kobold.json
```
Il flag `--allow-generation` è obbligatorio; lo script non avvia KoboldCpp, non esegue comandi Jarvis e usa solo `http://127.0.0.1:5001` per raggiungere il canary F4.1. Genera una semplice spiegazione sui buchi neri e un approfondimento, **senza stampare o salvare le risposte**. Gli output vengono mantenuti solo in memoria per costruire il follow-up. Salva soltanto tempi, modello, impronta SHA-256 del prompt sintetico, dati grezzi `/api/extra/perf`. **Non sovrascrive file esistenti**.
Nota: i campi `last_process` e `last_eval` di KoboldCpp rappresentano tempi in secondi; `last_token_count` è conservato come **contatore grezzo**, NON interpretato come token Processed o Generated. Mancano i contatori? Lasciare null invece di inventarli.

### 4) Confrontare senza confondere il testo delle conversazioni
```powershell
python -m tools.f42_benchmark compare f42-misure.json
```
Riporta secondi totali e, **soltanto se disponibili**, token/s in elaborazione e generazione. Quando GGUF, template/prompt, sampler, Threads, contesto, stato cache o qualità sono diversi o sconosciuti, segnala il confronto come **NON CONTROLLATO**, anche se calcola il rapporto descrittivo dei tempi. Per confronti con Second Brain ON e OFF è normale che il prompt differisca: questo serve a misurare il costo della memoria, non a certificare che due prompt differenti abbiano lo stesso lavoro computazionale.

### Decisione F4
- Misurare almeno una domanda breve e il suo approfondimento con risposte coerenti. Ripetere quando i tempi variano molto.
- Se il server risulta più veloce a parità di condizioni e qualità, progettare separatamente un selettore backend; il canary **non** si inserisce automaticamente in Jarvis.
- Se la differenza nasce dai token del Second Brain, non migrare il motore prima di avere misure di recupero/deduplicazione. Ricordi, messaggi e archivi persistono comunque.
- Nessun risultato del Pavilion è stato acquisito in questa fase: test automatici verificano **solo codice e protocollo**, non il rendimento sul tuo hardware.

**Rollback:** fermare i test, chiudere KoboldCpp, avviare la 014 originale. Nessuna migrazione, cancellazione o modifica di Second Brain e cronologia. I file di misura, creati solo quando richiesti, restano dove l'utente li ha salvati e non vengono caricati online.
