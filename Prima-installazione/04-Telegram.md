# 4. Telegram da zero
Questo modulo usa il tuo account Telegram tramite Telethon. Non richiede un bot né un account Business. Credenziali e codici vanno inseriti solo nelle finestre locali previste.

## Componenti
1. Con Jarvis chiuso esegui installa_telegram.bat nella cartella programma. Installa Telethon >=1.36,<2 nel Python selezionato.
2. Per note vocali in uscita serve anche FFmpeg con libopus nel PATH, più la sintesi Windows descritta nella guida Voce. Per trascrivere vocali ricevuti servono inoltre Vosk e il modello italiano.
3. Per risposte generate dal GPT esterno serve il suo collegamento attivo. L'invio vocale manuale di testo dettato/scritto usa invece sintesi locale.

## FFmpeg per i vocali
1. Consulta [FFmpeg](https://ffmpeg.org/download.html). Per Windows, una fonte di build è [Gyan](https://www.gyan.dev/ffmpeg/builds/): la variante release essentials contiene libopus e offre uno ZIP estraibile da Windows.
2. Estrai il pacchetto in una cartella stabile, per esempio C:\Strumenti\ffmpeg. Trova la sottocartella bin che contiene ffmpeg.exe.
3. Cerca in Start «modifica le variabili di ambiente per l'account». Nelle variabili utente seleziona Path → Modifica → Nuovo e aggiungi il percorso completo di quella cartella bin. Non cancellare le altre righe.
4. Chiudi e riapri Jarvis e il terminale. Verifica:

    ffmpeg -version
    ffmpeg -hide_banner -encoders

Nel secondo elenco deve comparire libopus. La sola presenza del file non prova la conversione completa; la compatibilità della build scaricata col Pavilion va verificata. Non serve installare un pacchetto Python chiamato ffmpeg e non serve comprare codec.

## API ID e API hash
1. Usa un account Telegram già attivo nell'app ufficiale.
2. Apri [my.telegram.org](https://my.telegram.org), accedi col tuo numero e completa il codice richiesto.
3. Apri API development tools e compila il modulo con i dati della tua applicazione.
4. Conserva privatamente api_id e api_hash restituiti. Non sono un token BotFather.
Fonte della procedura: [documentazione Telegram](https://core.telegram.org/api/obtaining_api_id).
Se il sito rifiuta la creazione, conserva l'errore esatto; non inventare credenziali né condividere hash/codici nel repository.

## Configurare l'account nel profilo giusto

> **Lumi 023 e successive:** avvia Lumi con `avvia_lumi.bat` e usa il pulsante «Configura Telegram (accesso sicuro)» in ingranaggio → Progetti e servizi: così l'accesso viene salvato nel profilo `%LOCALAPPDATA%\Jarvis-Gemma-Trial` letto da Lumi. Nella 023, `configura_telegram.bat` aperto da Esplora file salva invece nel profilo base e Lumi non lo vede (corretto dalla build successiva, che mostra il profilo usato e rilegge le credenziali dopo il salvataggio). L'errore «Formato credenziali non riconosciuto» delle build 019-022 è corretto nella 023.

1. Avvia Lumi col launcher del pacchetto che stai usando.
2. Apri ingranaggio → Progetti e servizi → Configura Telegram (accesso sicuro).
3. Inserisci API ID; nella finestra protetta incolla API hash con Ctrl+V o Incolla. Il codice accetta 32 caratteri esadecimali.
4. Inserisci il numero con prefisso internazionale, per esempio +39, poi il codice ricevuto da Telegram. Se richiesto, inserisci la password di verifica in due passaggi.
5. Attendi «Accesso Telegram salvato con cifratura Windows DPAPI». Nessun messaggio viene inviato dalla configurazione.
6. Torna in Lumi e premi Rileggi configurazione Telegram.

**Profilo Trial:** il riferimento esaminato usa %LOCALAPPDATA%\Jarvis-Telegram50-Trial. La configurazione deve scrivere nello stesso profilo. Se lanci configura_telegram.bat separatamente da Esplora file, senza il contesto del launcher, può usare il profilo base. Non confondere una configurazione nel posto sbagliato con credenziali perse.

Per configurare esplicitamente il Trial, se il percorso dall'interfaccia non viene ereditato correttamente: chiudi Jarvis, apri Prompt dei comandi nella cartella programma, poi copia queste due righe una alla volta:

    set "JARVIS_TRIAL_HOME=%LOCALAPPDATA%\Jarvis-Telegram50-Trial"
    configura_telegram.bat

Chiudi quel prompt e riapri avvia_jarvis.bat. Non usare queste righe per un profilo di produzione diverso. La propagazione dal pulsante UI va collaudata sul Windows reale; non è dimostrata da questa guida.

## Contatti e funzioni
1. Premi Gestisci contatti Telegram (spunta), poi Carica contatti Telegram.
2. Seleziona le persone desiderate e salva le spunte. La selezione cambia le autorizzazioni e lascia le risposte automatiche spente.
3. Lascia OFF finché non vuoi provarle. Se attivi Risposte vocali automatiche ON/OFF, verifica account GPT, FFmpeg e voce.
4. Per invio manuale usa la relativa finestra; per voce prova «Jarvis, manda un messaggio a NOME», rispondi alla domanda sul testo e conferma esplicitamente con «confermo», oppure annulla. Verifica destinatario e testo.
5. Un invio reale di prova va concordato con il destinatario. Nessun invio viene effettuato creando queste istruzioni.

Le chat locali del riferimento sono separate per contatto, con 50 eventi massimi e ultimi 4 per il contesto. La migrazione di database vecchi richiede copia coerente prima di avviare una versione precedente; vedi la guida Reinstallazione.

## Se non funziona
- Telethon assente: esegui installa_telegram.bat nello stesso Python di Jarvis.
- FFmpeg assente: completa PATH e riapri Jarvis.
- Nessun contatto: completa accesso e caricamento, poi spunta/salva.
- Voce o conversione fallita: nessun ripiego automatico a testo; risolvere l'errore.
- Credenziali non leggibili dopo cambio Windows/utente: ripeti l'accesso; DPAPI non è un backup portabile di credenziali.
- Non usare due Jarvis collegati allo stesso account Telegram durante la prova.
