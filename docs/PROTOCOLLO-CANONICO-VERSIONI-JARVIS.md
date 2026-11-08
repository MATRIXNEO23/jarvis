# Protocollo canonico delle versioni Jarvis
Data di adozione: 2026-11-08. Stato: regola di progetto per tutte le versioni successive alla 013.
Fonte primaria: repository GitHub MATRIXNEO23/jarvis. Questo protocollo integra, non sostituisce, Download/REGISTRO-VERSIONI.md e Download/BUILD-NUMBERS.json.

## Regola non negoziabile
Prima di qualsiasi modifica al runtime, creare una scheda di modifica nel registro docs/REGISTRO-DELTA-VERSIONI-JARVIS.md, con motivazione, problema osservato, baseline immutabile, file e simboli interessati, rischio di regressione, criterio di accettazione e rollback. Aggiornare la stessa scheda durante l'implementazione con diff/commit effettivo, esito dei test, decisioni e limitazioni. NON scrivere "corretto", "testato", "pubblicato", "verificato sul PC" senza una prova corrispondente. Separare esplicitamente proposte, modifiche implementate, test CI, package verificato e collaudo dell'utente.

Per ciascuna nuova versione salvare SEMPRE:
1. Identificativo versione precedente e nuova, data, stato e autore/attività; riferimenti SHA completi della base runtime, sorgente candidato, commit di packaging e commit di pubblicazione (se disponibili). Se manca un riferimento, indicare "non ancora disponibile", mai inventarlo.
2. Problema e motivazione: sintomi esatti riportati, comportamento atteso, ipotesi ancora da verificare, alternative scartate e perché.
3. Delta per file/funzione: cosa è cambiato, precedente -> nuovo, perché, effetti su UI, memoria, prompt, comandi, Telegram, microfono, add-on, configurazione e profili. Dichiarare esplicitamente cosa NON è cambiato.
4. Configurazione e riproducibilità: GGUF/DLL, Context Size, Max Output, temperatura, top-k/top-p/seed, budget storia, esempio di input, prompt/token di input e output effettivi, tipo di invio (testo/voce) e profilo di prova. Non includere dati personali né chiavi.
5. Prove RED/GREEN e regressioni con link ad Actions, command-line, esito e numero test. Per prestazioni separare caricamento, prefill/Process, decoding/Generated, UI/TTS e durata totale; dichiarare macchina/runner utilizzati. Mai generalizzare tempi runner sul Pavilion.
6. Compatibilità dati e sicurezza: schema/percorsi configurazione, migrazioni, file sidecar, autorizzazioni, dati persistentemente salvati, eventuale rischio di cancellazione, protezioni anti-esecuzione. Conservare il controllo allowlist anche dopo modifiche al parser.
7. Rollback concreto, ripetibile: ZIP immutabile e hash della versione stabile, source commit, impostazioni da ripristinare, eventuale differenza schema, verifica a posteriori e limiti. Vietato cancellare automaticamente cronologia, progetti, memoria, salvataggi, profili o consensi per ripristinare.
8. Stato finale e prossimo passo. Ogni problema non risolto va dichiarato come "aperto", non nascosto.

## Gate prima di una release
- Baseline: scegliere i sorgenti esatti indicati nei metadata della build, non presumere che la radice main sia il runtime attuale; registrare il confronto dei commit.
- Un cambiamento alla volta e test prima/dopo. Proteggere i comportamenti funzionanti e includere test negativi di sicurezza.
- Codice e documenti possono essere verificati senza creare una nuova build. Pubblicazione e sovrascrittura degli ZIP non sono automatiche: richiedono richiesta esplicita dell'utente e gate Windows/package.
- Il numero di build non va riutilizzato; i pacchetti precedenti restano immutabili. Prima di dichiarare pubblicato verificare manifest, SHA-256, Download, metadata e URL remoto.
- Evitare di fare dipendere la continuità della documentazione da una sola chat: la scheda e il piano devono essere persistiti nel repository; l'handoff collega ai percorsi canonici.
- Se un test peggiora la coerenza a favore della velocità, bloccare la promozione e documentare il rollback. Non garantire prestazioni reali senza prova sul PC.

## Modello di scheda obbligatoria
### JRV-CHANGE-[NNN] / Versione [precedente] -> [nuova]
- Stato: proposta | implementata | CI verificata | ZIP verificato | pubblicata | collaudata PC | respinta/rollback
- Motivo / evidenza di partenza:
- Base esatta (commit sorgente, hash ZIP e link):
- Requisito invariabile / criterio verificabile:
- File/funzioni modificate + diff/commit + motivo per modifica:
- Configurazione di prova e impatto su dati/compatibilità:
- Test RED / GREEN / regressioni + evidenze:
- Latenza e qualità prima/dopo con hardware e condizioni:
- Rischi, sicurezza, problemi aperti:
- Rollback: passi precisi e controlli di riuscita:
- Esito, data, prossimo passo:

## Fonti operative
- Registro storico e differenze: docs/REGISTRO-DELTA-VERSIONI-JARVIS.md
- Piano attuale: docs/superpowers/plans/2026-11-08-jarvis-014-coerenza-e-prestazioni.md
- Registro pubblicazioni: Download/REGISTRO-VERSIONI.md e Download/BUILD-NUMBERS.json
- Punto di ripresa: RECUPERO.md / AGENTS.md.
