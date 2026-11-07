# JRV-AUD-019 — unità visibili e compatibilità

Base017 verificata `530fad08935f29b2909a6ae2481a19cf77dcefc8`. Correzione mirata di etichette/documentazione, nessun cambiamento di valori, algoritmo o schema JSON.

Il prompt nativo usa len(str) e il budget restituito dal metodo storico available_prompt_tokens:600 significa caratteri Python, spazi inclusi. Context Size e Max Output sono invece parametri in token del backend nativo. Il parametro summary_max_tokens non è consumato da un gestore di sintesi collegato al runtime: non attribuirgli una lunghezza in caratteri attiva o promettere riassunti automatici.

Chiarire questi fatti nel pannello memoria, nelle etichette del pannello Gemma e nella docstring del metodo storico; documentare la differenza senza rinominare chiavi/campi/API né attivare sintesi/CompactContext/IdleMemoryGate. Nessun tokenizer o dipendenza nuova. Il cap in caratteri è una politica locale prudente, non una tokenizzazione né prova matematica che ogni testo Unicode rientri nella finestra del modello.

Verifica: AST/diff locali soltanto, suite Windows2022/Python3.11 e3.12 esistente per conservazione budget/roundtrip/configurazione e dialogo. Nessun nuovo test che duplichi letteralmente etichette o implementazione per una modifica reversibile di testo. Non rivendicare Red/TDD runtime non eseguito. Layout della finestra sul PC reale, GGUF, tokenizzazione e pacchetto estratto restano non verificati.
