# Registro canonico dei delta — Jarvis
Data di avvio: 2026-11-08. Questo registro è append-only: correggere le inesattezze con note esplicite, non riscrivere silenziosamente la storia. Per ogni versione applicare il protocollo docs/PROTOCOLLO-CANONICO-VERSIONI-JARVIS.md.

## JRV-CHANGE-013 — 012 -> 013 (ricostruzione documentale)
**Stato:** 013 pubblicata come candidata; rapporti utente di regressioni conversazionali; causa precisa non ancora dimostrata. Non presentare il collaudo PC come superato.

**Fonte esatta:**
- 012: source commit 5820b00623ec1632df86028c8bd9ac0341c5dc7d, ZIP Jarvis-012.zip, SHA-256 57c8fa161d36020207a46e2a6eee45f5fec8f0987546ae601e3abe1b6881c680.
- 013: source commit b9db9e0dc158b07f0c057cffa7b5c97a6f9ff974, ZIP Jarvis-013.zip, SHA-256 1926bb5b65d98bb78d1c829cd9143b1e39773c8c14581f6f63a8d0d9454ed781.
- Metadata e inventario: Download/Jarvis-012.json, Download/Jarvis-013.json, Download/BUILD-NUMBERS.json.
- Confronto source: https://github.com/MATRIXNEO23/jarvis/compare/5820b00623ec1632df86028c8bd9ac0341c5dc7d...b9db9e0dc158b07f0c057cffa7b5c97a6f9ff974 .

**Perché era stata modificata:** ridurre il prefill lento del prompt e preservare il riferimento recente, mantenendo dialogo/permessi/memoria/compatibilità. Sulla 012 era stata osservata un'elevata latenza.

**Delta implementato identificato:**
- local_model/memory_preferences.py: aggiunto history_max_tokens predefinito 250 (min 128, max 600); salvato in memory.native.json per non cambiare lo schema legacy memory.json. Campo prompt_max_tokens legacy mantenuto.
- local_model/native_conversation_session.py: limite totale storia/ricordi passato da 600 hardcoded al parametro history_max_tokens; ricordi variabili spostati dall'inizio delle istruzioni vicino all'ultima domanda utente. Vincolo di token e serializzazione Gemma mantenuti.
- local_model/memory_ui.py: aggiunto controllo impostazioni e descrizione.
- Test/piani/docs aggiornati. conversation_router.py, capability_registry.py e action_planner.py risultano identici fra i due source commit: rifiuto JSON e argomenti non consentiti NON introdotto nel parser 013.

**Evidenze/limiti noti al 2026-11-08:** l'utente riferisce 013 più rapida ma risposte lunghe rifiutate ("JSON non valido", "argomenti non consentiti"). Anche 012 ha in seguito trattato impropriamente "Cos'è un buco nero?" come richiesta di stato sistema; quindi la regressione non è attribuibile con certezza al solo delta 013. Console 012 dell'utente: circa 96 secondi Process e 25 secondi Generated per una prova; non è un benchmark comparabile 012/013. I due pacchetti condividono normalmente il percorso profilo %LOCALAPPDATA%/Jarvis/addon-data/modello_locale, a meno di JARVIS_TRIAL_HOME. Variare Max Output influenza lo spazio prompt. Non cancellare o resettare i profili per effettuare prove.

**Rollback:** conservare l'archivio 012 e le relative SHA; eseguire da cartella nuova e, prima, fare copia dei profili/configurazioni. Per un confronto determinante usare un profilo di prova isolato o snapshot di configurazione. La 012 ignora il nuovo sidecar memory.native.json, ma legge memory.json legacy; non garantire una qualità ripristinata se le impostazioni sono state condivise. Non sovrascrivere 013, non rimuovere dati.

**Prossimo passo:** seguire il piano Jarvis 014, distinguere routing scorretto, JSON tronco, prompt insufficiente e performance; misurare a condizioni uguali prima di correggere.

## JRV-CHANGE-014 — 013 -> 014 (pianificata, non implementata)
**Stato:** SOLO PIANO. Nessun commit runtime, ZIP, benchmark o pubblicazione 014.
**Motivazione:** ripristinare coerenza nella conversazione, impedire l'esecuzione di azioni Windows da domande informative e ridurre il prefill sul Pavilion.
**Baseline:** usare il source commit 013 sopra; confrontare anche il source 012; la radice main non è automaticamente il runtime pubblicato.
**Specifiche, task, test e gate:** docs/superpowers/plans/2026-11-08-jarvis-014-coerenza-e-prestazioni.md.
**Rollback previsto:** non promuovere 014 se test semantici/sicurezza falliscono; conservare 012/013 e profilo. Se pubblicata, tornare a ZIP precedente verificato solo dopo backup profilo e confronto differenze schema.
**Prossimo aggiornamento obbligatorio:** indicare file/simboli realmente cambiati, motivo per ogni modifica, commit, prove RED/GREEN, misure su runner/PC, esito e codice di rollback prima di pubblicare.


## JRV-CHANGE-014 — Primo intervento di routing, 8 novembre 2026 (ancora in verifica)
**Stato:** implementata una prima correzione nei SORGENTI ISOLATI, non in una build pubblicata. PR draft https://github.com/MATRIXNEO23/jarvis/pull/60, ramo fix/jarvis014-native-chat-routing-20261108, base sorgenti 013 b9db9e0dc158b07f0c057cffa7b5c97a6f9ff974.
**Perché:** domande informative come «Cos'è un buco nero?» e «Consigliami una serie TV» entravano nel parser JSON del catalogo Windows; lo stesso percorso può produrre falsi `system.status` o errori JSON anche nella 012.
**Cosa cambiato:**
- tests/test_native_informational_routing.py aggiunto prima del fix: prima CI RED 42513947407, test non importabile perché la funzione richiesta non esisteva (errore previsto; suite preesistente altrimenti in verde).
- conversation_router.py: nuova funzione conservativa `native_intent_context_for_request` per omettere catalogo/JSON nelle richieste univocamente informative; azioni e richieste ambigue rimangono nel percorso originale.
- jarvis.py: usa la selezione del formato PRIMA della generazione, senza una seconda chiamata al modello e senza modificare le protezioni di esecuzione.
- Prima CI dopo fix 42514115267: regressioni individuate in richiesta `Dimmi come sta il computer` e negazione `Non aprire il browser`. Corretto in 07eb750806e48f914a19bd04bc29707ccc2ad69a e test aggiornati in ecf5e1069809e99db00c6ec813c759db166fca3a. Una nuova CI è in esecuzione (42514495366); NON dichiarare GREEN fino al termine.
**Cosa non cambiato:** parser `parse_native_conversation_intent`, `capability_registry.py`, `action_planner.py`, GGUF/DLL, impostazioni, file dei ricordi, Telegram, add-on e pacchetti 012/013. Nessuna migrazione o cancellazione profilo.
**Limiti:** classificatore conservativo per frasi informative riconoscibili, non comprensione semantica generale; nessun test locale GGUF sul Pavilion. Il calo di prefill è plausibile (catalogo omesso in chat) ma prestazioni reali e coerenza non ancora misurate.
**Rollback:** non incorporare il branch nel runtime; 012/013 restano immutabili. Per annullare il prototipo, tornare al source SHA b9db9e0 e non importare i due cambi runtime. Nessun dato utente da migrare.
**Gate:** accettare solo con test Windows senza regressioni; dopo questa prima fase servono prove reali comparabili e task restanti del piano. Non pubblicare automaticamente.
