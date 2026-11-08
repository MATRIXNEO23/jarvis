# Valutazione memoria leggera — 8 novembre 2026
Stato: AUDIT completato sul codice del ramo e sul pin KoboldCpp; proposta, non nuova implementazione. Richiesta utente: prima pubblicare010, poi valutare memoria/riassunti senza appesantire. Ordine rispettato:010 verificata e pubblicata prima di questa analisi.

## Prove e limiti
- VERIFICATO: local_model/memory_preferences.py, available_prompt_tokens calcola context_size-max_output-reserve e lo confronta con prompt_max_tokens, ma restituisce un budget usato come caratteri. Default prompt_max_tokens600; non sono stati acquisiti i valori attuali del PC.
- VERIFICATO: native_conversation_session.prepare_turn confronta len(format_gemma_messages(...)) con quel budget, inserisce istruzioni/catalogo prima della storia e scarta coppie intere se non entrano. _commit_turn conserva al massimo2000 caratteri della risposta nella RAM; massimo16 scambi condivisi.
- VERIFICATO: SecondBrain.remember_turn conserva domanda320/risposta350 caratteri. prompt_context reinserisce domande110/risposte100 nei recenti, dopo i risultati correlati. Il contenuto omesso in quei record non è recuperabile da quegli stessi record.
- VERIFICATO: nel pin7e0eb2dc4a23f1a0fc42a7660ad43be7a4b9e759 koboldcpp.py contiene tokenize_ids(countprompt,tcaddspecial), che usa handle.token_count sotto token_count_lock e copia gli ID prima di rilasciarlo. È tokenizzazione, non generazione. Integrazione nel ciclo di vita Jarvis ancora NON VERIFICATA: richiede modello caricato, nessun secondo load/owner, serializzazione con inferenza/stop.
- VERIFICATO: IdleMemoryGate già presente, coopera con busy/heavy_load/idle; il modulo non avvia thread né generazioni. La presenza di opzioni summarize_every/background_summaries non dimostra da sola un riassunto prodotto o salvato.
- RISCONTRO UTENTE:009 risponde discretamente quando gli scambi non sono lunghi. Non è benchmark generale né prova che modello/template siano sempre corretti.
- INFERITO: il primo intervento da provare è l'assemblaggio/recupero del contesto, evitando di sostituire modello o avviare riassunti a ogni turno. Non attribuire automaticamente tutte le uscite fuori tema alla sola memoria.
- NON VERIFICATO: RAM/latenza/qualità reali sul Pavilion, valori attuali di configurazione, template del singolo GGUF e contenuto grezzo della precedente risposta con errore JSON.

## Opzioni
| Opzione | Costo previsto | Limiti |
| --- | --- | --- |
| Allineare unità/token e riservare contesto agli scambi recenti | Nessuna seconda generazione; tokenizzazione e gestione di pochi testi | Più token realmente inviati possono rallentare la risposta; preservare il limite scelto1024/2048 e riserva output |
| Conservare originali recenti entro limiti espliciti e recuperare estratti pertinenti quando necessario | I/O SQLite e selezione testuale locale, senza altro modello | Più dati su disco; rispettare consenso Memoria, filtri, cancellazione, isolamento generale/progetti/Telegram; un estratto non è un riassunto semantico |
| Riassunto generativo con lo stesso Gemma, solo quando serve | Generazione aggiuntiva e contesa della stessa CPU/sessione | Da misurare; può perdere fatti o attribuzioni. Eventuale uso opzionale in inattività, dopo aver verificato priorità/annullamento |

## Raccomandazione
Procedere per incrementi reversibili: prima correggere il budget e la priorità della storia, poi preservare/recuperare in modo limitato il contesto recente anche dopo riavvio. Se non entra una risposta intera, valutare un estratto che conservi domanda, argomento e frasi relative al richiamo attuale, marcato come estratto con omissioni. Non fingere di aver recuperato parti mancanti. Conservare sempre la distinzione utente/modello: un errore di Gemma non diventa un fatto.
Non aggiungere ora una seconda generazione sincrona a ogni turno, nuovo modello, embedding o servizio residente. Non aumentare automaticamente contesto/RAM.2048 è una scelta da provare sul PC, non una soluzione alla metrica errata. Riassunto semantico da rivalutare soltanto se gli interventi economici risultano insufficienti e con misure reali.

## Contratto/prove prima di implementare
R1: usare la finestra configurata senza confondere token/caratteri; A1: confronto con contatore nativo su italiano/Unicode, delimitatori, output e margine.
R2: mantenere il riferimento all'ultima risposta lunga; A2: storia sintetica lunga seguita da domanda su una frase interna, verifica del contenuto effettivamente inviato senza una seconda inferenza.
R3: recupero post-riavvio rispettando i confini; A3: profilo temporaneo riaperto, Memoria on/off, cancellazione, isolamento progetti/Telegram, permessi e filtri invariati. Eventuale archivio più completo richiede scelta esplicita di limiti/retention prima di salvare più dati.
R4: evitare blocchi e regressioni; A4: carico/stop/concorrenza/nessun secondo caricamento, memoria limitata e confronto prestazioni sul PC prima/dopo. Suite Windows e review prima di una futura candidata;010 non viene cambiata.
Nessun test funzionale nuovo eseguito per questa sola valutazione; nessuna nuova funzione di memoria implementata o pubblicata.
