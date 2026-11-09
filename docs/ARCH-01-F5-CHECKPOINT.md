# ARCH-01 — F5.0: profili locali Gemma/Qwen, checkpoint 9 novembre 2026

**Stato:** prima implementazione isolata e test unitari aggiunti, CI non ancora verificata, nessuna UI, nessuna build, nessun collegamento runtime. Branch `feature/jarvis-kobold-f5-profiles-20261109` derivato da `feature/jarvis-kobold-f42-benchmark-20261109`; rollback pubblicato: ZIP014. Non modificare main o gli archivi.

## Obiettivo confermato
Una sola chat locale con scelta esplicita fra profili Gemma/Qwen, impostazioni simili a KoboldCpp (context size, max output, threads, BLAS, temperatura, top_p, seed), rilevamento/verifica del modello realmente disponibile, cambio profilo senza cancellare cronologia o Second Brain, possibilità futura di backend embedded oppure KoboldCpp originale. Usare **un solo modello GGUF caricato alla volta** sul Pavilion i3-2100/10 GB RAM. Nessun download automatico o API online. Nessun passaggio automatico al server: F4.2 prestazioni reali non eseguite.

## Implementazione F5.0
- `local_model/model_profiles_f5.py`: dataclass immutabile, valori di esempio per Gemma e Qwen, controlli espliciti di famiglia/backend/parametri, scarto campi non riconosciuti (incluse chiavi API). Il nome del modello è un'etichetta e **non** equivale al rilevamento del GGUF.
- `tests/test_model_profiles_f5.py`: casi positivi/negativi per limiti, campi sconosciuti, immutabilità, parsing e nessuna importazione runtime.
- Nessuna importazione di F5 dal processo Jarvis; nessuna lettura/scrittura su disco; nessun processo, server, invio rete o modifica a Second Brain.

## Prossimi incrementi, con gate
1. **F5.0 gate:** Windows Python 3.11/3.12 tests e verifica diff (solo modulo/test/documenti); documentare commit e regressioni. Non chiamare F5 completa con questo gate.
2. **F5.1 discovery:** capire il punto esatto di configurazione di Gemma embedded e del canary KoboldCpp, con adapter di lettura capacità/identità modello; rispondere modello non disponibile senza fallback occulto. Prima definire contratto e test mock Windows.
3. **F5.2 UI:** Impostazioni modello: profilo selezionabile, scelta backend se supportato, context/max output/threads/sampler/seed, applicazione al prossimo caricamento con validazione; preferenze separate per profilo, senza alterare le impostazioni della 014; percorso vocale e mouse equivalenti ove possibile.
4. **F5.3 switch:** chiudere con certezza il motore precedente prima di avviare l'altro; se fallisce, messaggio breve, recupero senza perdita dei messaggi e rollback profilo; preservare Second Brain e tutti i file personali.
5. **F5.4 collaudo:** suite Windows, audit processi/ram, prova manuale Pavilion Gemma/Qwen e fluidità chat; confronto F4.2 prima di approvare migrazione DLL → server o pubblicare ZIP.

## Fuori ambito
F8 provider API online, segreti, ricerca modelli, download GGUF, auto-selezione/modello in parallelo, nuovo backend DLL Qwen non dimostrato, cambio template per azioni Windows/Telegram, auto-build o nuova release.

## Rischi e rollback
La quantizzazione e il template di chat devono dipendere dal vero GGUF; l'etichetta `qwen` da sola non autorizza un template. Non scegliere in automatico formati o payload senza test delle famiglie. Il server KoboldCpp resta canary opzionale e **non** è stato dimostrato più veloce sul Pavilion. Se il gate fallisce, fermare F5, correggere soltanto il difetto e ripetere la prova; per l'utente resta ZIP014; nessun dato va migrato o eliminato. I test Windows in CI non sostituiscono test reali.

## Stato F4.2 ereditato
PR #66; 1064 test/job Windows riferiti GREEN, prova Pavilion assente. Guida: `docs/ARCH-01-F42-PROVA-PAVILION.md`. Non dichiarare completata la misura hardware.

## Ripresa
Leggere AGENTS.md, RECUPERO.md, docs/STATO-ATTIVITA.md, docs/DECISIONI-E-LEZIONI.md, questo file, PR F4.2 e PR F5. Riprendere dal gate F5.0; integrare la UI soltanto dopo revisione del codice effettivo e decisione sul backend.

## F5.1 — Implementazione di rilevamento isolato (9 novembre 2026)
Aggiunti `local_model/model_availability_f5.py` e `tests/test_model_availability_f5.py`. L'API `inspect_embedded` controlla soltanto l'esistenza dei file GGUF e DLL esplicitamente forniti; **non** identifica famiglia, quantizzazione, compatibilità ABI o possibilità di caricare il modello. La risposta `files_present_not_loaded` è intenzionalmente prudente. `inspect_koboldcpp` riutilizza il client canary F4.1, effettua solo GET `/api/v1/model`, verifica per uguaglianza esatta un identificatore modello fornito dal chiamante, e restituisce `model_mismatch` o `server_unavailable_or_unverified` senza testo privato. Nessuna generazione, switch, modifica runtime, rete su import, cartella scandita, salvataggio o persistenza.

**Verifiche:** aggiunti test mock e filesystem temporaneo; la CI Windows relativa alla nuova implementazione resta da verificare. Il gate F5.0 precedente disponeva di workflow Windows completati con successo sul commit `8fe4990...` ([unit protocol 42538543827](https://github.com/MATRIXNEO23/jarvis/actions/runs/42538543827), [tokenizer nativo 42538544094](https://github.com/MATRIXNEO23/jarvis/actions/runs/42538544094)); questi workflow non verificano automaticamente le modifiche F5.1. Corretto anche il controllo valori NaN/infinito in `model_profiles_f5.py`.

**Prossimo gate:** CI Windows F5.1 e revisione; dopo il verde, progettare F5.2 UI con opzione di scelta modello, senza usare `files_present_not_loaded` come prova di modello eseguibile. Qwen richiede template testato e provider confermato, e il passaggio embedded/server attende le prove Pavilion F4.2. Il rollback resta ZIP014; nessuna build nuova.

## F5.2 — Anteprima interfaccia collegata alle Impostazioni (9 novembre 2026)
**Implementato:** `local_model/multimodel_ui_f5.py` (dialog Tkinter con scelta profilo Gemma/Qwen, Context Size, Max Output, Threads CPU/BLAS, Temperature, Top P, Seed); `tests/test_multimodel_ui_f5.py` (test di validazione senza aprire Tk); pulsante nella pagina esistente **GPT e memoria** di `jarvis.py` denominato `Anteprima multimodello Gemma / Qwen...`. Rimane il vecchio pannello Gemma. Le bozze si validano e si conservano **solo nella memoria della finestra**: nessun salvataggio persistente, nessun GGUF caricato, nessun server avviato e nessun cambio del provider della chat. Chiudendo il pannello si perdono le bozze; questo limite è comunicato nella UI.

**Diff e rischio:** unica modifica al runtime Jarvis: aggiunta di callback + bottone lazy import nel gruppo esistente, senza alterazione dei comandi vocali, della sessione Gemma, dei salvataggi, del Second Brain, di Telegram o della gestione di GPT. Questo rende F5.2 visibile nei sorgenti ma non nella ZIP014 pubblicata. Codice del dialog non importato all'avvio. L'anteprima non verifica la disponibilità del modello: F5.1 offre API read-only separate, ma l'interfaccia non le invoca per evitare rete/operazioni inattese. Test UI reali Pavilion ancora da fare.

**Gate:** eseguire suite Python 3.11/3.12 Windows, revisione delle modifiche al runtime e test manuale del dialog prima di affermare F5.2 completa. La funzione futura di salvataggio persistente deve usare archivio isolato versionato/atomico e non sovrascrivere `native_config`; il passaggio effettivo di profilo è F5.3 con verifica un solo GGUF in memoria, timeout, rollback e test delle due famiglie. Nessun nuovo pacchetto ZIP né API online; rollback utente 014.

**CI di F5.1:** al momento della preparazione F5.2, [unit protocol 42539072431](https://github.com/MATRIXNEO23/jarvis/actions/runs/42539072431) era ancora in esecuzione, [nativo 42539072563](https://github.com/MATRIXNEO23/jarvis/actions/runs/42539072563) SUCCESS. Non assimilare la CI F5.1 ai nuovi test F5.2.

## F5.3a — Gate di lifecycle prima dello switch reale (9 novembre 2026)
**Audit:** `jarvis.py` usa `NativeConversationSession(NativeChatAdapter(source))`; `NativeChatAdapter.stop()` chiama `provider.stop()`, che imposta l'abort cooperativo senza prova di deallocazione GGUF, e il bridge `NativeGemmaBridge` non espone una funzione di unload confermato. La chat si serve di `format_gemma_messages` e di `NativeConversationSession` con template specifico per Gemma. La cronologia chat F2 è salvata a parte in SQLite attraverso `ChatSessionsPanel`; non deve essere eliminata per cambiare modello. **Nessuna prova che cambiare attualmente Gemma→Qwen sia sicuro.**

**Modifica:** `local_model/model_switch_gate_f5.py` aggiunge una barriera autonoma, non collegata al runtime, che impedisce ogni transizione se il modello corrente è occupato, backend/template target non verificati, release della risorsa precedente non confermata o nuovo modello non avviato con successo. Le attestazioni sono esplicitamente responsabilità del futuro proprietario del ciclo di vita, non sono dedotte da `stop()` o dalla presenza di un file. Test `tests/test_model_switch_gate_f5.py` (senza GGUF, rete, UI o DB) per conferme mancanti, tentativi concorrenti, ticket obsoleti, annullamento prudente. **Non usare questo modulo da solo come prova di unload o come selettore attivo.**

**Gate successivo:** progettare e testare in Windows una lifecycle manager che chiuda e rilasci realmente le risorse del modello embedded prima di avviarne un altro, con prova ABI e PID/memoria; verificare il template Qwen reale e percorso Chat/Console/Telegram prima di collegare `begin` a UI o chat. Se non è garantito il rilascio, preferire esplicitamente riavvio del processo tra profili (con stato persistente conservato), non promettere hot switch. Nessuna build/ZIP nuova; rollback 014. CI del nuovo gate ancora da verificare.
