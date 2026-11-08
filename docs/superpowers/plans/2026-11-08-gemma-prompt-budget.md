# Gemma prompt budget Implementation Plan

> **For agentic workers:** Execute this plan task-by-task using the user's authorized project workflow. Steps use checkbox syntax for tracking.

**Goal:** ridurre il contesto elaborato mantenendo l'ultimo riferimento utile e tutte le capacità/autorizzazioni.
**Architecture:** migliorare MemoryPreferences, il selettore esistente e la stessa finestra di impostazioni. Budget nativo separato dal limite legacy; istruzioni stabili sul primo user, richiamo variabile sull'ultimo user prima della domanda.
**Tech Stack:** Python stdlib/Tkinter, tokenizer/DLL KoboldCpp già pinned, unittest/CI Windows.
**Spec:** docs/AUDIT-PRESTAZIONI-GEMMA-20261108.md, proposta finale approvata dall'utente con «Ok procediamo», più richiesta esplicita di preservare funzioni e configurabilità.

## Global Constraints
- Solo Windows per test funzionali; nessuna build/pubblicazione autorizzata da questo passo.
- Zero nuove dipendenze, processi, servizi o generazioni di riassunto; modello e context/max_output invariati.
- Preservare controlli delle azioni, revoche, ruoli Gemma, memoria per progetto, Telegram isolato e profilo leggibile dalle versioni precedenti.
- Modifica del componente esistente, non nuova add-on né doppio percorso.

## Scelte circoscritte
- `history_max_tokens` 250 iniziali, intero128–600; massimo conserva la vecchia politica, non apre un budget maggiore.
- `prompt_max_tokens` continua ad avere lo stesso significato/caratteri e JSON legacy invariato.
- Persistenza del nuovo campo in `memory.native.json` accanto a `memory.json`: necessaria perché il lettore010/012 rifiuta chiavi aggiuntive nel JSON legacy. Entrambi scritti atomicamente per file; non sono una transazione multipla. Un errore resta visibile, nessuna conversione silenziosa di profilo.
- Nessun riassunto LLM. Ultimo scambio protetto dall'estrattore esistente entro budget; domanda corrente mai troncata. Vecchi scambi eccedenti esclusi dal solo prompt, non cancellati da RAM/archivio.
- Dati richiamati vicino alla domanda, con stessi delimitatori come dati e sanificazione del serializer. Catalogo/validatori invariati. Controllo finale dell'adapter conservato.
- Rinviate deduplica archivio/ricerca DB e nuove metriche runtime: non necessarie a questo intervento e non dimostrate come causaPC.
- Alternative scartate: aumentare contesto aggrava il prefill; riassuntore aggiunge inferenza; riusare parametro legacy converte vecchi valori senza consenso.

## Review Focus
- File legacy valido senza sidecar: caricare250 senza riscriverlo; malformed sidecar non deve resettare il profilo.
- Budget cambiato in sessione: effetto alla richiesta successiva senza reload o perdita della storia accettata.
- Ultima risposta lunga e riferimento tardivo: estrarre e conservare soggetto/parola richiamata anche con128token.
- Ricordo variabile e template nel dato: primo scambio invariato, niente confini ruolo introdotti, domanda attuale integra.
- UI Salva/Valori iniziali/errori: campo reale collegato, nessun modello avviato dal pannello; vecchie opzioni preservate.

### Task1: regressioni e RED Windows
**Files:** tests/test_native_prompt_policy.py; .github/workflows/native-context-proof.yml.
- [x] Aggiungere regressioni su default, override live128/600, riferimento lungo, collocazione/sanificazione ricordi, profilo legacy/sidecar invalido e UI reale Salva/Reset.
- [x] Eseguire prima di cambiare runtime: `python -m unittest discover -s tests -p test_native_prompt_policy.py -v` su Windows; documentare failure comportamentali.

### Task2: modifica minima e GREEN
**Files:** local_model/memory_preferences.py, native_conversation_session.py, memory_ui.py; local_model/README.md.
- [x] Nuovo campo e compatibilità/persistenza descritti sopra. Nessuna migrazione automatica o scrittura su load.
- [x] Sostituire600hardcoded solo nel budget nativo di history+recall. Spostare ricordi variabili, evitare la misura del prefisso se manca callback/spazio; non saltare validazione finale.
- [x] Campo UI numerico e help aggiornati, spiegazione del compromesso e default; mantenere gli altri controlli.
- [x] Eseguire focused + suite Windows completa; affrontare ogni regressione dimostrata.

### Task3: prova nativa, review, checkpoint
**Files:** tools/probe_native_prompt_performance.py, .github/workflows/native-prompt-performance.yml; documenti di stato/handoff/lezioni.
- [x] Conservare casi audit600 espliciti; aggiungere stesso input sintetico con250 e confronto prefisso con richiamo A/B. Assert budget con tokenizer reale, ultimo riferimento conservato,1load,1generazione/richiesta.
- [x] Review indipendente dei diff esatti e recheck mirato. Prova nativa Windows, tempi come osservazioni del runner e non garanzie Pavilion.
- [x] Salvare risultati e limiti nella repo, distinguere sorgente verificato da pacchetto non ancora pubblicato; nessun nuovo ZIP.

## RED osservato e stato della modifica
628e908, run42499660390/job128789426794:7test,2failure (storia oltre250 e primo turno alterato da richiamo),4errori per nuovo campo API/UI assente,1controllo ruoli già OK. Comando focused del piano, Windows. Nessun import/sintassi mancante. Correzione runtime ora presente nel worktree:3file responsabili e prova nativa aggiornata per confronto600/250; GREEN e review pendenti. Nessun nuovo ZIP.

## Prima GREEN e review
58b8059:focused7test e integrazione nativa42499942818SUCCESS, prestazioni42499942823SUCCESS. Review indipendente in sola lettura senza blocchi runtime; aggiunto assert esplicito storia+recall<=budget con tokenizer reale e caso riferimento tardivo128. Recheck strumentazione/test necessario, nessun runtime aggiuntivo modificato. Dati runner non sono promessa di velocità sul Pavilion.

## Chiusura verificata
Recheck c91ebb5:7focused+DLL42500290904SUCCESS,11richieste native con contributi token espliciti42500290988SUCCESS,1006test per ciascun Python Windows3.11/3.12nel run42500291039SUCCESS. Review indipendente e recheck statico conclusi senza rilievi residui. Rapporto canonico docs/CORREZIONE-PROMPT-GEMMA-20261108.md ed evidenza JSONpersistente. Nessuna build pubblicata, successivo passo solo su richiesta.
