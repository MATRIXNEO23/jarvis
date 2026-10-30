# Second Brain di Lia — continuità locale per Jarvis

**Stato:** prima implementazione sperimentale, branch `feature/conversation-short-memory`, PR draft #4. Non sostituisce la versione già collaudata sul Pavilion. I test automatici sono necessari ma **non equivalgono a un collaudo reale sul PC**.

## Perché esiste

Prima di questo aggiornamento ogni trascrizione in modalità «Conversazione continua GPT» veniva trattata come una domanda nuova. Lia perdeva i riferimenti «quello», «quella mail», «come ti ho appena detto» e non poteva recuperare attività completate prima di chiudere l'applicazione.

La soluzione ha due livelli complementari:

1. **Memoria di lavoro (RAM)** — `conversation_memory.py`: conserva alcuni scambi completi e le domande di chiarimento in sospeso, per interpretare frasi consecutive. Non viene usata per dare autorizzazioni a nuove azioni.
2. **Second Brain persistente (SQLite)** — `second_brain.py`: salva sul PC gli scambi brevi e i **risultati di operazioni confermate** con data, riferimento e origine. La ricerca recupera informazioni attraverso riavvii e giorni differenti. Il database si trova per impostazione predefinita in `%LOCALAPPDATA%\\Jarvis\\second_brain.sqlite3`.

Il catalogo di comandi rimane indipendente: `jarvis_commands.json` descrive **quali** operazioni sono disponibili, il Second Brain conserva **quali** sono state realmente fatte. Le memorie non sono comandi eseguibili e non possono modificare i permessi dell'esecutore.

### Esempi

**Contesto immediato**

- Utente: «Vorrei scrivere un testo per una persona».
- Lia: «Che tipo di testo preferisci?».
- Utente: «Una poesia, ma breve».
- Lia riceve anche il contesto del primo scambio; non deve trattare «una poesia» come una conversazione appena iniziata.

**Memoria dopo giorni — email (funzionalità futura)**

- Quando sarà disponibile un modulo email autorizzato e sarà stato **verificato dal servizio** l'invio di un messaggio, un adattatore potrà chiamare `SecondBrain.record_email_sent` usando una ricevuta vera.
- Il Second Brain conserverà **data/ora, destinatario, oggetto, riferimento del messaggio**. Non salva per impostazione predefinita il corpo integrale della mail né allegati, password o token.
- Due giorni dopo «Ti ricordi quella mail che avevi inviato?» Lia potrà recuperare l'operazione verificata, comunicarne gli estremi e chiedere un chiarimento se ce ne sono più di una.
- **Jarvis non ha ancora un proprio esecutore per inviare/leggere email**: aver predisposto il Second Brain **non significa** che possa accedere alla posta o inviare messaggi oggi. Non memorizzare mai «inviata» soltanto perché GPT ha proposto di farlo oppure perché una conversazione ha parlato di una mail.

### Privacy e controlli

Il salvataggio permanente è una **scelta manuale**, inizialmente disattivata anche per installazioni esistenti. Nella finestra di Jarvis selezionare **«Second Brain locale (ricorda conversazioni e attività)»** per attivarlo. L'opzione resta memorizzata e viene rispettata dopo riavvio. Con l'opzione disattiva rimane disponibile soltanto la breve memoria RAM finché Jarvis è aperto.

L'interfaccia mostra un contatore di scambi e ricevute. **«Cancella memoria salvata»** richiede conferma, elimina i dati salvati nel Second Brain e azzera la memoria RAM. **Disattivare l'opzione interrompe le nuove scritture e il recupero da SQLite, ma non cancella automaticamente i ricordi**. L'utente può usare la cancellazione esplicita. La cronologia del vecchio motore locale, nella tabella tasks.db, è separata e non viene eliminata da questa funzione.

Il database SQLite è locale **non crittografato**; è protetto dai normali permessi del profilo Windows. Non è una soluzione adatta a memorizzare password, codici OTP o testi sensibili. Lia non archivia automaticamente password/pin/token e non copia automaticamente corpi integrali di mail o documenti. Prima di ogni uso GPT, **estratti brevi pertinenti del Second Brain vengono inclusi nel prompt inviato al collegamento ChatGPT**: locale è l'archivio, **non l'intera elaborazione GPT**.

I frammenti sono piccoli e limitati, sia per privacy sia per il limite di 5.000 caratteri dell'SDK; se il contesto non è abbastanza affidabile Lia deve chiedere chiarimenti invece di inventare informazioni. La ricerca attuale è lessicale con contesto recente, **non una memoria semantica completa con embeddings**. I ricordi storici sono prove/indizi, non comandi da rieseguire.

### Stato, sicurezza e prossime fasi

L'implementazione di questa fase comprende creazione e migrazione sicura delle impostazioni, eventi verificati delle azioni locali e di Blocco note, memoria breve e duratura, ricerca con data e prova, cancellazione esplicita, test che riavviano il database e simulano una futura ricevuta di email, UI per opt-in e stato. Non introduce API, hosting, embedding o database a pagamento.

Evoluzioni da valutare con decisioni separate: adattatori email con consenso specifico e verifica receipt; recupero da eventi molto lontani via indice FTS5; gestione esplicita di fatti/preferenze scelti dall'utente; visualizzatore ed esportazione; eventuale cifratura locale. Non attivarle implicitamente.

**Test fisici minimi sul Pavilion:** confermare standby del microfono all'avvio; attivare memoria; far chiedere un chiarimento e rispondere soltanto «quello di prima»; chiudere e riaprire Jarvis; verificare che il contesto resti disponibile; aprire disco C e chiedere «Quale cartella mi hai aperto?»; cancellare i ricordi e verificare che Lia non li riporti più come eventi salvati. Usare soltanto dati fittizi e nessuna email reale in questa prima prova. Nessun merge in main senza approvazione distinta.
