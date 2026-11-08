# Comandi interni — verifica per passi

Riferimento requisiti: [piano confermato](superpowers/plans/2026-11-08-local-command-routing.md).

1. Riproduzione `e4641bea24f8c2439d0b52e48c5de78aa8d9fa26`, PR56, run42426651526:928test Windows per Python3.11/3.12,7failure attese/0errori. Sintomo console/engine stato e browser e5varianti mancanti. Gli assert su negazioni e dialoghi già coperti passano; nessuna prova di microfono/GGUF personale.
2. Prima candidata `55be411ab9f1df450f1ae61767f96f7c6ab200ab`, stesso tree locale5d96302. Run42427227254 ancora da concludere. Riuso riconoscimento voce nella console e negli ingressi engine/file, sinonimi, mostra Download apertura, help. Il raccordo interpretazione Gemma resta da fare.
3. Review indipendente readonly dell'esatto diff e464..5d96302: individuata regressione statica nella priorità del chiarimento su progetti esistenti chiamati Cronologia/Stato sistema. Preparato test con callback console+risolutore progetti e WorkspaceMemory reali; solo cambio contesto finale controllato. Verifica Windows Red del nuovo caso prima della correzione.

Prossimo passo: leggere Red del caso review, poi conservare la priorità del risolutore progetti. Nessuna build o test funzionale Linux. Lacune dichiarate: nuovo test console sostituisce submit_local, quindi bookkeeping ledger non coperto direttamente da questo test; Netflix viene coperto solo dal gate simulato nel nuovo test, mentre le prove applicative preesistenti restano necessarie; verificare mostra Download anche con servizio file attivo.

## Correzioni mirate dopo i riscontri

- Run42427227254/job128567991118:930test,1failure/0errori. Tutti i nuovi casi del primo passo passano. Il test reale planner→engine individua la regressione list_downloads che usa ancora mostra: corretto il comando canonico del planner in elenca download, senza cambiare gli assert.
- Run42427484026, sourcef6f6711a91a5adfd846b36b848b08383acadbb1b, job128568773631:931test,3failure/0errori (planner e2subcase progetti). Test della review riprodotto prima della correzione. Candidata ora chiama il risolutore progetti esistente prima di eseguire il nuovo comando riconosciuto; non sposta i gestori delle altre richieste.
- Aggiunta caratterizzazione servizio file attivo: mostra Download apre una sola volta, non produce listing, revoca della cartella blocca la nuova apertura. Rimossi alias mostra dai rami di elenco ormai superati; il riconoscitore condiviso determina l'apertura.

Prossimo controllo: nuova suite Windows della candidata, ricontrollo mirato della review. Raccordo Gemma ancora pendente, nessuna build.

## Primo passo verificato; avvio raccordo Gemma

Source949f31df5993f284f08e2ec4f5a0400822da1080 (tree equivalente localef112a3c), run42427784373 SUCCESS. Python3.11/job128569691692:932test/152.957s/OK; Python3.12/job128569691484:932test/185.997s/OK. Sintassi/probe e integrazione Windows Search nel workflow verificati dal successo dei job. Review mirata readonly non ha trovato ulteriori difetti nelle correzioni. Nessun pacchetto creato, nessuna inferenza su GGUF/microfono personali.

Passo seguente autorizzato: proposta Gemma in formato del protocollo già esistente → validatore esistente → esecutore esistente, senza nuove azioni o seconda inferenza automatica. Preparati6test del callback owner reale e della sessione con inferenza controllata: stato/browser, capacità sconosciuta, duplicati, revoca e chat strutturata. Runtime di questo secondo passo ancora invariato. Red Windows da eseguire prima dell'implementazione.

Implementazione prevista: catalogo compatto dalle fonti esistenti, riuso del dispatcher delle capacità già usato da GPT, accettazione una sola volta senza salvare JSON d'azione come risposta chat. Conservare memoria/contesto e stop/epoch. Prompt entro i limiti configurati: se il catalogo non entra, preservare la chat esistente e segnalare che l'interpretazione azioni non è disponibile con quel contesto; nessuna modifica automatica delle preferenze. Nessun nuovo processo o dipendenza. Verificare separatamente la correttezza strutturale e l'accuratezza del modello reale, che qui non è provata.

## Raccordo Gemma — Red e candidata

Source9e629a292038c30a8541b00c8fe1bafca299332a, run42429202766/job128574098234:938test/159.623s,5failure attese/0errori nei nuovi casi; revoca epoch già protetta. Candidata: catalogo di soli ID esistenti, singola generazione nella sessione già caricata, stesso parse_conversation_intent e dispatcher capacità estratto senza cambiare i rami GPT. Proposta nativa accettata una sola volta senza salvare JSON d'azione come chat; controlli contesto/epoch/revisione sessione, dati mancanti, permessi live e documento corrente. Telegram isolato e API chat standalone mantengono il comportamento precedente.

Il catalogo di sistema ha spazio separato dal budget dei dati conversazionali ma resta entro contesto modello meno risposta/margine; impostazioni salvate invariate. Se non entra, chat legacy con avviso e nessuna nuova autorità. Test del budget complessivo aggiornato al limite reale1792=2048−128−128, mantenuti controlli memoria utile, sanitizzazione e caso256 caratteri del contesto512. Fixture d'inferenza della chat UI restituisce il protocollo JSON quando richiesto; non si cambiano gli assert su cronologia/progetti.

Aggiunte prove per JSON malformato, stop dopo generazione, proposta su frase negata, nuovo dialogo, documento cambiato, add-on revocato e contesto piccolo. Totale previsto945test. Prossimo passo: Windows della candidata e review indipendente del solo raccordo. Nessuna build o garanzia di accuratezza del GGUF reale.

Review indipendente readonly del raccordo4d678fa..9b3c0b5: un rilievo concreto, manca il dialogo Telegram pendente nel gate che rifiuta una vecchia proposta nativa dopo un nuovo dialogo. Esteso il test del callback con Telegram che diventa pendente fra generazione e polling; previsto946test. Red del caso prima del fix. Nessun altro difetto concreto nei confini esaminati; bookkeeping submit_local e accuratezza GGUF restano limiti distinti. Il dispatcher GPT estratto risulta equivalente nei rami esaminati.


### Correzione dei tre fallimenti della candidata
Il run 42430228966 termina con 946 test, un fallimento e due errori. Il callback GPT nel test file viene ora selezionato dentro poll, evitando il nuovo callback nativo; il fake adapter implementa stop; la proposta nativa viene respinta durante un dialogo Telegram pendente. Sintassi AST e diff verificati; verifica funzionale Windows da eseguire. Richiesta utente: arrivare alla build dopo verifica.
