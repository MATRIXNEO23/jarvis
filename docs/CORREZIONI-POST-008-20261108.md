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

## Checkpoint 8 novembre — candidata e ultimo passo
Red Windows completo run42438204627:951 test,8 failure di asserzione,0 errori. Gli otto failure includono i quattro sinonimi: il baseline non cambia selezione. Corretto il solo errore UTF-8 della fixture prima di questa prova.
Candidata scelta/consenso/sinonimi/Telegram:78d66c2, run42438583283 in corso. Revisione indipendente ha trovato due ulteriori problemi: vecchi ask GPT in coda dopo doppio cambio modello e frasi di cambio modello consumate durante composizione Telegram; corretti con epoch e priorità del dialogo pendente, regressioni incluse. Non è una nuova build.
Ultimo passo avviato dopo avviso: formato/context Gemma2/3. Red aggiuntivo09ebdff, run42438698661 in corso, tre regressioni per ruoli/coppie/PTT. Analisi fonti e soluzione documentate nel piano. Nessun risultato positivo dichiarato prima di leggere Windows.


## Verifica candidata formato/contesto
Candidata53c711c:run42439040155, Windows Python3.12,960 test,1 failure,0 errori. Unica asserzione non aggiornata attendeva user seguito immediatamente da ciao; il prompt osservato contiene correttamente istruzioni nel primo user, ciao, risposta e seconda domanda in turni separati. Corretta l'asserzione senza rimuovere i controlli storia/ruoli. Seconda candidata solo test4c4b315 in verifica; runtime identico a53c711c.
Le modifiche sono correzioni del routing e della serializzazione nei componenti core esistenti; un nuovo jaddon duplicato renderebbe discordanti selettore, permessi e sessione. Nessuna nuova dipendenza, migrazione, modifica DLL/GGUF o variazione delle impostazioni salvate.

## Precisazione utente — template Jinja del modello effettivo
L'utente richiede esplicitamente confronto del template Jinja e dell'intero contesto inviato: non basta dichiarare il formato standard. Nel pin upstream letto, format_jinja rende cached_chat_template con jinja2, add_generation_prompt=True, bos/eos vuoti; main valorizza cached_chat_template da handle.get_chat_template(). Jarvis esegue initializer+load_model+generate e non main/server: quel percorso di rendering Jinja non viene chiamato. Il provider Jarvis serializza in proprio. La nuova serializzazione è conforme al formato testuale Gemma2/3 IT documentato, ma NON è ancora confronto con tokenizer.chat_template del GGUF utente. Il modello utente è descritto in precedenza come Gemma2 2B, senza nome GGUF/repository/revisione verificabile; la CI usa un GGUF diverso non confermato. Manca il file o il nome/link esatto del modello in uso. Nessuna nuova dipendenza Jinja introdotta né template arbitrario eseguito. Prossimo controllo specifico: acquisire identità e template del GGUF reale e confrontare output su più turni, istruzioni, separatori e fine generazione con il prompt Jarvis. Non dichiarare risolta la qualità semantica sul PC sulla sola suite controllata.

## Checkpoint verificato — 8 novembre 2026, scelta modello e contesto
Fonte verificata ae3649d37da23d446871fbb6c6dbcead2edb72e8, PR57, run42439513080 SUCCESS:962 test per job Windows Python3.11/3.12,0 failure/errori; sintassi Python/Node/PowerShell e probe file Windows PASS, Windows Search live PASS nel job previsto. Review indipendente completata; rilievi epoch ask, dialogo Telegram e overhead prompt corretti. Codice sul ramo fix/model-selection-session-20261108, non integrato né distribuito in nuovo ZIP. La008 pubblicata resta immutabile.
Correzioni verificate con callback/ABI controllati: GPT scelto ha precedenza voce/chat/PTT; primo consenso conversazionale condiviso in RAM; sinonimi sul toggle esistente; errori connessione senza Gemma sostitutiva; Telegram segue scelta e permessi propri; turni Gemma user/model completi, contesti isolati, istruzioni iniziali, budget serializzato coerente col catalogo.
Richiesta utente ancora aperta: confrontare Jinja/tokenizer.chat_template del GGUF realmente caricato con il prompt Jarvis. Nel repository non c'è quel modello e manca nome/link esatto verificabile; famiglia descritta dall'utente Gemma2 2B. Il formato standard Gemma2/3 IT e il percorso upstream pin sono stati letti, ma non equivalgono a verifica del file utente. Chiedere nome completo/link GGUF; non confonderlo col modello CI. Nessun collaudo microfono/account/GGUF sul Pavilion o benchmark eseguito. Budget storico in caratteri, non tokenizer. Nessuna build senza nuova richiesta esplicita. Lista completa: docs/CORREZIONI-POST-008-20261108.md; prove: docs/evidence/model-selection-context-20261108.json.

