# Jarvis — progetti a voce e salvataggio dei documenti

## Cartelle: dati utente separati dal codice

Per evitare di perdere la memoria aggiornando il programma, tutti i progetti
restano sotto:

- Windows: %LOCALAPPDATA%\Jarvis\projects\<UUID>\
- Dentro ogni progetto: CONTINUITA.md, STATO.json, PASSI.md, EVENTI.jsonl,
  ARTIFATTI.md, PROGETTO.txt e files\.
- files\ contiene i documenti creati o salvati per quel progetto.
- L'UUID resta stabile e non dipende dal nome riconosciuto dal microfono.
  PROGETTO.txt rende riconoscibile la cartella. Non modificare manualmente
  lo schema SQLite o spostare le cartelle singolarmente.

La voce «Apri la cartella del progetto» apre quella specifica cartella.
Non è necessario specificare un percorso o scrivere un nome di cartella.

## Frasi locali di prova (nessuna API aggiuntiva)

- «Jarvis, crea un progetto chiamato Minecraft»
- «Jarvis, crea un progetto» → Jarvis domanda il nome, si risponde «Minecraft»
- «Jarvis, apri il progetto Minecraft»
- «Jarvis, quali sono i progetti attivi?»
- «Jarvis, apri la cartella del progetto»
- «Jarvis, torna alla conversazione generale»

Sono supportate anche le varianti implementate in project_voice.py,
e le stesse operazioni funzionano dalla casella chat di Jarvis.
Per creare e navigare i progetti non serve che GPT sia online.
Con nomi duplicati Jarvis non sceglie arbitrariamente tra i progetti.

## File di Blocco note nel progetto

1. Apri il progetto e chiedi a Jarvis di aprire Blocco note e scrivere un testo.
2. Pronuncia «Jarvis, salva» o «Salva come rapporto del progetto».
3. Jarvis salva una COPIA TXT del contenuto attuale nella directory files\
   del progetto che possedeva il documento. Suggerisce il nome a partire
   dall'argomento della richiesta originale (o «appunti-<progetto>»).
4. La finestra di Blocco note rimane aperta. Il salvataggio avviene tramite
   file locale creato da Jarvis, non attraverso il menu Salva di Notepad.
5. Se l'utente modifica il testo dopo il salvataggio, il successivo «salva»
   crea una NUOVA versione numerata e mantiene quella precedente.
6. «Salva e chiudi» usa la stessa cartella di progetto e chiude soltanto
   la finestra gestita da Jarvis dopo un salvataggio riuscito.
7. Se nessun progetto è attivo, Jarvis continua a chiedere «Dove vuoi salvare?»
   e accetta il percorso vocale già autorizzato («sul desktop come appunti»)
   oppure il selettore visuale.

Sono esclusi overwrite, percorsi suggeriti liberamente dal modello, comandi
di shell e cancellazioni. Il salvataggio fuori dalla cartella del progetto
richiede una destinazione esplicita. Se un documento è ancora aperto,
Jarvis non cambia progetto per evitare di salvare nel contesto sbagliato.

## Verifiche richieste sul Pavilion

- Salva backup dell'intera cartella %LOCALAPPDATA%\Jarvis prima della prova.
- Chiudi il Jarvis attuale, estrai la ZIP in una nuova cartella, avvia solo
  la nuova istanza con lo stesso utente Windows.
- Prova creazione a voce, cartella visibile, documento di testo con nome
  automatico e salvataggio ripetuto; verifica che i file precedenti restino.
- Chiudi e riapri Jarvis e verifica che ritrovi il progetto selezionato
  e i documenti/registri automatici.
- Verifica vecchia chat, cronologia progetti e Telegram con autorisposta
  disattivata. Nessun test deve inviare messaggi reali a terzi.

Funzioni incluse: solo applicazioni e documenti gestiti dal runtime Jarvis.
Non è ancora una gestione completa di tutti gli editor e applicazioni Windows.
Il collaudo Windows nel CI non sostituisce il test della voce e di Notepad reali.
