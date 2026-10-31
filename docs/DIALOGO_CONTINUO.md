# JARVIS — dialogo continuativo e personalità coerente

> **Nota aggiornata 31/10/2026:** questa guida documenta una fase precedente con microfono spento al lancio. Nel ramo di audit attuale è richiesta e configurata la **conversazione GPT con microfono attivo all'avvio**, purché Vosk e il dispositivo funzionino. Le modalità si possono sempre modificare manualmente; le sezioni sottostanti sono prove storiche.\n\n
**Ramo sperimentale:** `feature/dialogue-continuity-personality`, PR draft [#8](https://github.com/MATRIXNEO23/jarvis/pull/8), derivato dalla nuova interfaccia più fedele al preview (`feature/hud-reference-redesign`). Non modifica automaticamente la versione già installata sul Pavilion.

## Problema riscontrato nel test reale

L'utente ha osservato che JARVIS, pur riconoscendo spesso le parole, si comporta come se ogni nuova frase fosse isolata e non seguisse il discorso. Ha inoltre chiesto una personalità più simile all'idea di JARVIS: naturale, competente, discreta e occasionalmente ironica.

Nella revisione del codice sono emerse **due cause concrete**:

1. La memoria di lavoro usata nelle richieste vocali era limitata a 360 caratteri; un singolo scambio lungo non entrava e l'algoritmo restituiva `[]`, facendo perdere del tutto l'ultimo chiarimento.
2. Mentre il collegamento GPT elaborava una richiesta, le frasi riconosciute in seguito erano scartate con il messaggio «GPT sta rispondendo: attendi prima di parlare.»

## Nuovo comportamento

- **Memoria breve sempre attiva in RAM:** le ultime risposte e domande di chiarimento vengono mantenute, anche quando sono un po' lunghe. L'algoritmo riduce la lunghezza dei turni per preservare almeno l'ultimo anziché eliminarli tutti; non viene scritto nulla sul disco se Second Brain permanente è disattivato.
- **Contesto prioritario per i riferimenti:** il prompt a GPT riceve gli scambi recenti in formato strutturato e pone **alla fine la richiesta attuale**, in modo che frasi come «quella seconda», «più breve», «no, intendevo l'altra» possano completare il discorso invece di avviarne uno nuovo.
- **Coda bounded delle frasi durante l'elaborazione GPT:** fino a **tre** interventi vocali riconosciuti possono attendere il completamento della risposta precedente. Saranno inviati uno alla volta, con la memoria aggiornata dall'ultima risposta. Se la coda è piena, JARVIS segnala che bisogna ripetere l'ultima frase: non elimina silenziosamente quelle già conservate. La coda viene svuotata quando cambi modalità o disconnetti GPT, e non si riproduce dopo un riavvio.
- **Personalità coerente:** in chat vocale e scritta JARVIS usa il tu, tono educato e competente, frasi semplici, discrezione e qualche tocco di ironia asciutta quando ci sta, senza battute obbligatorie, nomignoli, saluti ripetuti o imitazioni di frasi cinematografiche. Non inventa ricordi o capacità.
- **Controlli di sicurezza invariati:** gli scambi passati non sono autorizzazioni per aprire, chiudere, modificare o inviare elementi nuovi. Il JSON delle azioni deve ancora passare per il catalogo dei comandi e il suo esecutore autorizzato; la chiusura dei documenti rispetta le conferme reali.
- **Costi e prestazioni:** nessun nuovo modello, servizio, API a pagamento, embedding o processo sempre attivo. Soltanto brevi frammenti di testo inclusi nella richiesta GPT attraverso il collegamento già disponibile; limite rigido di 5.000 caratteri mantenuto mediante catalogo capacità più compatto.

### Esempio da testare

Utente: «Vorrei che mi scrivessi un racconto ambientato a Venezia.»

JARVIS: «Preferisci un racconto breve o qualcosa di più articolato?»

Utente: «Breve, con un finale un po' malinconico.»

Atteso: JARVIS collega la seconda frase alla richiesta di racconto; **non** risponde come se «breve» fosse un nuovo comando. L'effetto preciso dipende anche dalla qualità della trascrizione Vosk e dall'interpretazione del modello.

## Limiti importanti

Questo non trasforma Vosk in un riconoscitore audio più accurato: si corregge la **continuità del dialogo dopo la trascrizione**. La protezione contro l'eco di Windows continua a ignorare la voce dell'utente durante la riproduzione della sintesi SAPI, quindi non è ancora una conversazione full-duplex con interruzioni naturali *mentre JARVIS parla*. La coda gestisce invece più interventi trascritti quando GPT sta ancora pensando.

Il Second Brain persistente rimane una **scelta manuale e separata**: se attivo, consente il recupero dopo riavvio di dialoghi e attività effettivamente verificate; altrimenti la memoria breve esiste solo finché JARVIS è aperto. Estratti pertinenti della memoria persistente vengono inviati a GPT durante le conversazioni: la memorizzazione su disco è locale, l'elaborazione GPT è online.

## Prova sul Pavilion

Scaricare [la ZIP di questo ramo](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/dialogue-continuity-personality.zip), estrarla in una cartella diversa e avviare `avvia_jarvis.bat`. Non cancellare la versione precedente né `%LOCALAPPDATA%\\Jarvis`.

1. Verificare che il microfono parta sempre spento, quindi attivare manualmente **Conversazione continua GPT**.
2. Chiedere un testo con un dettaglio mancante, quindi dare soltanto quel dettaglio in una seconda frase. Verificare che il contesto resti presente.
3. Provare una seconda frase mentre GPT sta elaborando; deve essere mantenuta in coda e interpretata dopo la risposta precedente.
4. Provare una normale domanda conversazionale; il tono deve essere naturale e sobriamente «JARVIS», non un elenco impersonale di opzioni.
5. Verificare che passare a standby, disconnettere GPT o chiudere la finestra non esegua frasi pendenti; riprovare le conferme di salvataggio con un documento fittizio.
6. Provare sia con il Second Brain spento sia, separatamente, con la memoria permanente attivata. Il funzionamento della memoria breve non deve richiedere l'opt-in.

La CI verifica sintassi, limiti, schema di esecuzione e regressioni. La qualità effettiva delle conversazioni va valutata sul Pavilion con GPT collegato, senza considerare il solo test automatico una prova del comportamento completo.
