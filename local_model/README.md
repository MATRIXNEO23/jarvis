# Permessi GPT online

In Impostazioni → GPT e memoria → Autorizzazioni GPT per funzione:

- **Mai (solo locale)**: quella funzione non può inviare richieste GPT, anche con una conferma precedente o con il consenso Telegram di sessione.
- **Chiedi autorizzazione**: una conferma per richiesta; Telegram può riusare il consenso esplicito della sessione finché non viene revocato.
- **Autorizzato per questa funzione**: evita la conferma di invio ripetuta per quella sola funzione.

Permessi distinti: conversazione, raffinamento ricerca file, spiegazione contenuto file, preparazione risposte Telegram, pianificazione e valutazione della diagnosi. Le voci web non aggiungono un browser assistito non implementato.

Se manca il file permessi, il valore resta Mai. Per usare GPT occorre scegliere Chiedi o Autorizzato nella funzione desiderata. Un file illeggibile non concede permessi. I permessi vengono ricontrollati prima dell'invio. Una revoca non può richiamare dati già trasmessi.

Login/stato account e azioni locali restano separati. Autorizzare GPT non autorizza l'esecuzione di un piano, l'accesso a nuove cartelle o l'invio di messaggi a contatti non selezionati. I consensi alle azioni restano necessari.

Il file `addon-data/modello_locale/online-permissions.json` è nel profilo Jarvis o nel profilo di prova indicato da `JARVIS_TRIAL_HOME`. Questa correzione non lo migra e non modifica automaticamente le preferenze esistenti.

## Memoria breve Gemma

La conversazione generale e ogni progetto hanno ricordi brevi separati nella stessa sessione. La chat riusa il modello caricato; una Prova generazione esplicita può ricaricarlo in modo serializzato. Il limite resta globale:32 messaggi, cioè16 scambi completi; gli scambi più vecchi escono dalla sola memoria RAM quando arrivano i nuovi. Tornando a un progetto si ritrovano i suoi scambi ancora nel limite, senza importare quelli degli altri.

Una risposta generata entra in memoria solo quando la UI la accetta nello stesso contesto ed epoca della richiesta. Se nel frattempo cambia progetto, modalità o autorizzazione, la risposta revocata non viene ricordata. Telegram e selettore programmi non leggono né scrivono questa memoria chat.

Non vengono modificati database, cronologie o file di progetto. Questa correzione non aggiunge persistenza al dialogo Gemma: il collegamento alla memoria duratura resta il distinto JRV-AUD-009.

## Proprietario della prova Gemma — JRV-AUD-005

Nel pacchetto Gemma il pulsante Prova generazione usa la stessa sessione della chat e di Telegram. Aprire il pannello o salvare le impostazioni non carica il modello. La prova esplicita attende le altre richieste, ricarica con lo snapshot delle impostazioni salvate e genera senza usare o modificare i ricordi della chat. Alla fine lascia il modello pronto alle richieste successive; non ferma un'altra sessione.

Se le impostazioni cambiano mentre la prova aspetta, la richiesta vecchia viene rifiutata e va ripetuta. Un salvataggio successivo all'acquisizione dello snapshot non cambia il modello che quella prova sta caricando. La prova non invia richieste online e non esegue azioni sul PC.

Il pulsante resta aggiunto dal builder Gemma; i sorgenti root del pannello sono l'editor di configurazione. Le verifiche Windows usano il callback generato reale con ABI controllata, senza produrre un archivio. Il collaudo con DLL/GGUF reali sul PC di riferimento resta necessario.

## Impostazioni Gemma — correzione008 in verifica

Salva conserva i nuovi valori senza avviare il modello. La prossima richiesta valida li usa: max output, temperatura, top-k/top-p e seed senza ricaricare il GGUF; cambi di modello, thread o contesto richiedono ricaricamento automatico dopo la richiesta in corso. Il carattere continua ad applicarsi al prossimo prompt. Un errore non deve cancellare i ricordi della chat; correggere le impostazioni e riprovare.

Queste modifiche sono nel ramo di correzione, ancora in verifica Windows e senza nuova build pubblicata. Le prove usano ABI controllata e non certificano prestazioni o qualità sul PC. Nessuna dipendenza o impostazione del microfono aggiunta.
