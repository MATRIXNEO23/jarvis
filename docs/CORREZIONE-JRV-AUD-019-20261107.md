# JRV-AUD-019 — distinguere caratteri e token

Stato: verificata nei sorgenti in bozza; nessuna nuova build. Source `190cac1e1080134de06e64ed241079ba07a7a369`.
Base017 `530fad08935f29b2909a6ae2481a19cf77dcefc8`.
[Specifica](superpowers/specs/2026-11-07-jrv-aud-019-design.md), [piano](superpowers/plans/2026-11-07-jrv-aud-019-fix.md).

## Evidenza e correzione minima

Il budget storico prompt_max_tokens è applicato con len(str) da sessione/adapter nativi: il default600 limita i caratteri del prompt completo, incluse istruzioni, prefissi, domanda e memoria che vi entra. Non è un conteggio dei token del GGUF. Il metodo available_prompt_tokens conserva un nome storico ingannevole; cambiarlo o migrare lo schema non è necessario per correggere l'indicazione visibile.

| Punto | Correzione | Comportamento conservato |
|---|---|---|
| memory_ui | «Caratteri massimi nel prompt», spazi inclusi; sintesi automatica esplicitamente non collegata | Valori e chiavi dei controlli, validazione/salvataggio invariati |
| memory_ui / riassunto | «Limite riassunto (non collegato)» | Non si attribuisce un effetto runtime o un'unità attiva a summary_max_tokens, oggi solo validato |
| native_ui | Context Size e Max Output esplicitamente in token | Parametri n_ctx/n_predict del backend, non convertiti o ricalibrati |
| memory_preferences | Docstring spiega budget in caratteri e nomi legacy | Defaults, schema JSON, API e algoritmo identici |

Nessun tokenizer, dipendenza o sintesi automatica attivata. CompactContext e IdleMemoryGate non vengono collegati. Nessun riassunto o storico riscritto.

## Verifiche

AST/diff locali soltanto. Confronto statico con la base dei defaults/schema, metodo di budget (esclusa docstring) e callback save dei due pannelli; nessun test funzionale Linux. Suite Windows2022/Python3.11 e3.12 esistente da acquisire, inclusi roundtrip/valori memoria, budget e dialogo nativo. Nessun nuovo test che rispecchi letteralmente etichette per una correzione reversibile del testo. Nessun Red/TDD runtime rivendicato: il comportamento numerico non cambia.

## Limiti

Caratteri significa punti Unicode Python, non byte o simboli grafici. La sottrazione numerica di output/margine dalla finestra del modello resta una politica prudente, non un tokenizer o una garanzia per ogni testo Unicode. Non verificata tokenizzazione GGUF, qualità semantica, layout sul PC reale, Windows10/i3/HDD o pacchetto estratto.022/023 restano aperti indipendentemente da questo testo.

Ramo isolato e reversibile fix/jrv-aud-019-memory-units-20261107 sulla017. Nessuna build/ZIP/merge/release, configurazione/profilo/credenziale reale o pacchetto precedente modificato. Recupero: tornare alle etichette precedenti senza migrare o cancellare dati. Prossimo021: durata della voce durante chiusura dell'app.

## Verifica Windows conclusa

[Run42361597736](https://github.com/MATRIXNEO23/jarvis/actions/runs/42361597736) SUCCESS al tentativo1, source `190cac1e1080134de06e64ed241079ba07a7a369`. Python3.11.9 job128370965405:884test in139.336s; Python3.12.10 job128370965635:884test in137.486s. Zero failure/errori/skip. Sintassi Python/JavaScript/PowerShell e probe nativo passati; Searchlive3.12 passato con servizio ripristinato e fixture rimossa. Build/estrazione/artifact/pubblicazione saltati.022/023 non osservati, restano aperti.

[Evidenza JSON](evidence/jrv-aud-019-fix-20261107.json). Checkpoint finale soltanto documenti/evidenza, hash dei tre moduli da confrontare col sourceverde prima di dichiarare conservazione remota. Prove di regressione esistenti, senza nuovo test che rispecchi le etichette. L'assenza di modifica numerica è verificata staticamente, non una prova della tokenizzazione GGUF o del layout sul PC.
