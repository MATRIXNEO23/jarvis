# Protocollo di accettazione — almeno le prestazioni di Kobo

Requisito utente vincolante: motore incorporato nell’add-on, stesse impostazioni utili configurabili, prestazioni almeno pari a Kobo e nessun blocco durante le prove. Stato: protocollo, non risultati.

## Precondizioni

- Confronto sullo STESSO Pavilion/i3-2100 Windows10, alimentazione e carico comparabili. Il runner Windows della CI non sostituisce questo PC.
- GGUF identico verificato con SHA256, non solo nome e quantizzazione. Versione Kobo dell’utente e build DLL fissate; snapshot delle impostazioni effettive completo.
- Stessi prompt tokenizzati, template Gemma, context size, max output, thread e batch thread, sampler order/valori, seed, stop/EOS e opzioni memoria/cache. Nessun criterio raggiunto accorciando l’output o omettendo parti della richiesta.
- Modalità CPU identica; nessun backend AVX2/FMA/F16C selezionato implicitamente. Contare i processi del motore e di Jarvis per memoria/CPU.
- Online spento per tutta la prova; nessuna chiamata GPT per mascherare un fallimento locale.

## Misure separate

1. Caricamento dal processo arrestato fino a modello utilizzabile. Distinguere prima lettura dal disco e successive letture con file cache Windows; non chiamarle entrambe “a freddo”. Nessuna pulizia forzata di RAM/cache sul PC utente.
2. Attesa invio→primo token (TTFT) e tempo totale percepito dalla console.
3. Tempo native prompt evaluation e tempo/token di generazione, con conteggi reali. Primo token non si può ricavare dall’unica risposta finale: occorre streaming o strumentazione nativa.
4. RAM privata/working set e CPU di Jarvis più processo del motore, inattivo e durante generazione, almeno prima e dopo una sequenza ripetuta.
5. Reattività console e comandi locali mentre il motore elabora; annullamento/timeout, errore di caricamento, disattivazione e arresto senza risultato tardivo eseguito.

## Ordine delle prove

Almeno dieci coppie di richieste brevi a modello già caricato, alternando ordine Kobo→Jarvis e Jarvis→Kobo per ridurre l’effetto dell’ordine. Separare un giro con contesto nuovo da una conversazione che sfrutta la cache, mantenendo la stessa storia su entrambi. Confrontare anche un prompt con catalogo capacità e più turni: i 9–10s riferiti nella prima chat non provano la latenza con il catalogo completo.

Testi fissi: saluto, appunti, calcolo, negazione, domanda informativa, chiarimento seguito da risposta breve. Per le prestazioni usare anche una generazione a lunghezza controllata con lo stesso testo di input, senza forzare nel prodotto risposte inutilmente lunghe. Per la correttezza verificare separatamente azioni richieste, nessuna azione con negazioni e nessuna falsa conferma di esecuzione.

## Esito

Riportare tutti i valori delle coppie, mediana e coda dei tempi, token/s e conteggi, non il solo caso più rapido. Passa il confronto soltanto se non emerge peggioramento di latenza/velocità e la sequenza resta funzionante. Dati con rumore elevato o impostazioni/identità diverse: INCONCLUDENTE, mai “equivalente per ipotesi”; acquisire solo le misure necessarie a risolvere l’incertezza. Un singolo blocco osservato è un rilievo da riprodurre/correggere prima della consegna. Nessuna prova finita garantisce assenza assoluta di blocchi in ogni utilizzo futuro.

Il risultato completo richiede inoltre configurazioni salvate/applicate nel motore, stessa console Jarvis per voce/testo, Telegram e altre capacità esistenti con i loro permessi, switch online e consenso monouso. Un benchmark nativo verde non dimostra l’integrazione del prodotto.
