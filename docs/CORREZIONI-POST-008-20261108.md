# Correzioni richieste dopo il collaudo 008 — 8 novembre 2026

Requisiti confermati dall'utente durante il collaudo. Nessuno dei punti seguenti è ancora dichiarato corretto.

- [ ] GPT attivo e autorizzato deve essere il modello della conversazione sia scritta sia vocale. Difetto individuato: send_console_input privilegia il modello locale configurato; start_conversation_gpt chiama direttamente submit_gemma_voice.
- [ ] Prima del primo invio GPT chiedere conferma, valida per la sessione corrente. Rispettare autorizzazioni per funzione e revoche; nessun invio online implicito.
- [ ] Conservare esecuzione locale dei comandi riconosciuti. Con GPT selezionato, richieste non riconosciute e conversazione vanno a GPT; le proposte di azione usano validatore/esecutori esistenti. Con Gemma selezionato usare il percorso locale.
- [ ] Cambio modello a voce e in chat mediante sinonimi: passa a/torna a/usa/attiva/avvia GPT o Gemma, con formule sensate e richiamo Jarvis nella voce. Stessa scelta/interruttore UI, indicazione immediata; nessuna modalità duplicata. Non eseguire richieste negate.
- [ ] Indagare e correggere perdita del contesto e scarsa continuità della conversazione Gemma. Verificare turni realmente salvati e reinviati, budget, troncamento, identificativo progetto/sessione e passaggio voce/chat. Non assumere che la DLL sia responsabile.
- [ ] Verificare prompt effettivo fino al provider Kobold/DLL: template Gemma, ruoli, separatori e fine turno, istruzioni, cronologia e token. Il provider oggi avvolge il prompt testuale in un singolo turno user; la sessione costruisce la cronologia come testo Utente/Jarvis. Verificare l'effetto e usare il percorso messages esistente se appropriato, senza duplicare template. Verificare anche coerenza del budget sessione/adapter: il catalogo aggiunge spazio nella sessione ma l'adapter controlla il budget originale.
- [ ] Help aggiornato a comportamento, consenso e sinonimi effettivamente supportati.
- [ ] Preservare comandi interni, browser predefinito, programmi/Netflix, Explorer/permessi, documenti, progetti, memoria, Telegram e modalità microfono. Nessuna funzione extra o refactoring superfluo.
- [ ] Prove riproducibili prima del fix, test Windows completi e verifica pacchetto estratto. Distinguere modello simulato da GGUF reale/Pavilion. Aggiornare stato/handoff e consegnare tutte le correzioni richieste, senza affermare prontezza prima delle verifiche.

Ordine: scelta modello e consenso; cambio modello con sinonimi; contesto/template/budget Gemma; help e regressioni; pacchetto verificato. La 008 pubblicata resta immutabile. Nuova pubblicazione solo di una candidata verificata nel perimetro richiesto.

## Precisazione confermata — GPT per tutta la sessione

- [ ] GPT selezionato e autorizzato: al primo invio conversazionale chiedere conferma; dopo accettazione mantenerlo per tutta la sessione, condivisa fra voce e chat, senza richieste ripetute.
- [ ] Tornare a Gemma solo su scelta esplicita mediante interruttore o comando riconosciuto. Un errore o una disconnessione GPT deve essere segnalato, senza fallback silenzioso a Gemma.
- [ ] Consenso soltanto runtime, non salvato come autorizzazione permanente. Nuova sessione richiede nuova conferma; revoche dei permessi restano efficaci.

Stato: elenco salvato; correzioni e verifiche ancora da completare.

### Riproduzione instradamento GPT
Aggiunta prova sul callback vocale reale: GPT selezionato non deve chiamare Gemma e deve raggiungere run_gpt. Inferenza e invio online controllati ai confini, nessun account. Sintassi verificata; test Windows ancora da eseguire. Runtime invariato.

## Telegram — ulteriore requisito confermato

- [ ] Con GPT selezionato e autorizzato per Telegram, risposte tramite GPT; nessun uso silenzioso di Gemma per disconnessione/non prontezza. Preservare permessi telegram.compose e consenso Telegram di sessione.
Analisi: ask_telegram_reply sceglie gia GPT quando telegram_gpt_ready è impostato e non ricade su Gemma se ask_telegram_gpt fallisce. Il flag è però azzerato anche quando GPT è selezionato ma disconnesso; allora il ramo corrente usa Gemma. Distinguere scelta utente da disponibilita connessione e aggiungere prove per entrambi. Nessuna correzione dichiarata o test Windows nuovo eseguito.

## Ordine aggiornato dall’utente

Formato e contesto Gemma per ultimi. Prima: instradamento voce/chat secondo GPT selezionato, consenso e permanenza per la sessione; cambio modello con sinonimi; Telegram secondo scelta esplicita e permessi. Poi formato/template/budget/continuita Gemma. Help e prove accompagnano ciascun passo, verifica completa e pacchetto soltanto alla fine. Nessun requisito rimosso.

## Ripresa: Red Windows verificato
Run42437319811:947 test, un solo failure: GPT selezionato richiama Gemma. Aggiunte prove chat con Gemma configurato, consenso condiviso e revoca, Telegram disconnesso. Runtime invariato; nuovo Red da leggere.
