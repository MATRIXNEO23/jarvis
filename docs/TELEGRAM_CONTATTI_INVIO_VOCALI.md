# Telegram — selezione multipla e messaggi vocali su richiesta

**Stato:** sviluppo sperimentale su `feature/telegram-multicontact-voice-outbound`, PR #26. Nessun merge automatico. Questa funzione non richiede un modello locale o nuovi servizi a pagamento: usa Telegram tramite Telethon, Windows SAPI, FFmpeg e GPT esterno via Sign in with ChatGPT **solo** per generare le risposte automatiche.

## Impostazioni
1. Configurare l'account Telegram mediante `Configura Telegram (accesso sicuro)` se non già configurato. Hash, codice e sessione sono gestiti dal percorso esistente e protetti con DPAPI; non salvare credenziali in un prompt.
2. Aprire `Gestisci contatti Telegram (spunta)`, poi `Carica contatti Telegram`. La lista proviene dai veri contatti Telegram e dalle chat private recenti, senza gruppi, bot o account proprietario.
3. Spuntare uno o più contatti e premere `Salva le spunte`. Per sicurezza, cambiare l'elenco disattiva le risposte automatiche: riattivarle manualmente quando desiderato. La versione precedente con un contatto viene migrata automaticamente al primo caricamento delle impostazioni, senza cancellare la sessione.
4. `Risposte vocali automatiche ON/OFF` continua a controllare **solo** le risposte automatiche ai messaggi dei contatti selezionati. Le chat e la memoria restano separate per ID numerico Telegram.

## Inviare manualmente un vocale
Premere `Invia messaggio vocale`, selezionare un contatto con la spunta, digitare 1–480 caratteri e premere `Conferma e invia vocale`. Una finestra mostra destinatario e testo, chiedendo un ulteriore `Sì` esplicito. Il motore esegue la sintesi SAPI e converte in OGG/Opus con FFmpeg, quindi invia la nota tramite `voice_note=True`. Nessun invio parte da un pulsante senza conferma, né dal GPT. Funziona anche con risposte automatiche disattivate, ma richiede l'account Telegram configurato.

## Inviare tramite comando vocale
Con un microfono **attivato manualmente**, dire «Jarvis, manda un messaggio a Nico» (in Ascolto continuo è necessaria la wake-word iniziale). Jarvis verifica se `Nico` identifica un solo contatto con spunta; in caso di nomi omonimi chiede di usare il nome completo. Poi chiede «Che messaggio vuoi mandare a Nico?». Pronunciare il testo. Jarvis chiede «Vuoi inviarlo come vocale?». Solo «confermo» autorizza l'invio. «annulla» revoca la richiesta. Il dialogo scade dopo 120 secondi senza conferma. La stessa sequenza è disponibile tramite il campo di testo Jarvis.

## Limiti e precauzioni
- Nessun contatto non autorizzato può ricevere o provocare risposte da Jarvis. Un contatto disattivato non può essere usato dal nuovo comando e viene ricontrollato prima dell'effettivo invio.
- Per chiarezza, i vecchi comandi di promemoria differito funzionano soltanto se è selezionato **un solo** contatto; per più contatti utilizzare il nuovo invio diretto.
- Non viene usata la comprensione GPT per scegliere un destinatario. La generazione vocale è locale; le risposte automatiche, se abilitate, continuano a usare GPT esterno.
- Se l'account ha chiuso la sessione Telegram, mancano Telethon/FFmpeg o fallisce la sintesi, non inviare automaticamente un testo in alternativa. L'assenza di ricevuta significa esito incerto: niente reinvii automatici per evitare duplicazioni.
- Una sintesi può essere annullata togliendo la spunta; una chiamata di invio già consegnata alla rete potrebbe comunque completarsi. Il destinatario deve sapere che le risposte automatiche sono di un assistente.
- Carico previsto contenuto: nessun browser WhatsApp né modello vocale generativo, solo SAPI + FFmpeg già usati. Telethon aggiorna i contatti soltanto su richiesta.

## Collaudo reale ancora richiesto
Test CI: parsing, ambiguità, selezione persistente, isolamento per peer, conferma, revoca, assenza invio prima della conferma; nessuna rete Telegram reale né audio Windows nelle unit test. Prima della distribuzione sul Pavilion verificare configurazione, carico contatti, nomi duplicati, interruttori, dialogo vocale, conferma e ricezione di un reale OGG/Opus su un contatto di prova consenziente. **Non dichiarare testato l'invio reale fino a quel controllo.**
