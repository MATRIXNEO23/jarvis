# Scarica Jarvis per Windows 10 — HP Pavilion

## ULTIMA PROVA — INTERFACCIA JARVIS COME NEL PREVIEW

**[SCARICA JARVIS HUD CON GLOBO DETTAGLIATO E REATTORE CIANO/ARANCIONE/VERDE (ZIP)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/hud-reference-redesign.zip)**

Questa è la **revisione del design richiesta dopo il confronto fotografico** tra la precedente build sul Pavilion e l'immagine concept. Il nuovo layout avvicina la schermata al preview: console/chat con schede **Console / Attività / Sistema** a sinistra, **cerchio JARVIS più ricco di anelli e luci** al centro, **Terra con continenti, luci e orbite rotanti** a destra e quattro strumenti di monitoraggio reali in basso.

**Codice colore del centro:** ciano quando Jarvis è inattivo; **arancione lampeggiante** soltanto se il microfono Vosk è realmente aperto; **verde lampeggiante** quando la sintesi vocale Windows sta parlando, con precedenza sullo stato di ascolto. Il nome **JARVIS** non cambia; nessuna scritta «ASCOLTO» nel nucleo.

**Installazione per il test:** chiudi la vecchia istanza, scarica questa ZIP, estraila in **un'altra cartella** e avvia `avvia_jarvis.bat`. Nessun nuovo modello o costo API. Il microfono rimane **in Standby all'avvio**: scegli la modalità manualmente da ⚙. Confronta i colori, la rotazione terrestre e la leggibilità sul Pavilion. **Non cancellare il Jarvis precedente, la cartella Vosk né `%LOCALAPPDATA%\\Jarvis`.**

I test automatici Windows/Linux sono verdi; manca **il collaudo visivo e prestazionale direttamente sul Pavilion**. Le versioni precedenti rimangono negli altri collegamenti sotto. [Dettagli e test da fare](https://github.com/MATRIXNEO23/jarvis/blob/feature/hud-reference-redesign/docs/HUD_REFERENCE_V2.md) · [PR #7 di prova](https://github.com/MATRIXNEO23/jarvis/pull/7).

## NOVITÀ — JARVIS HUD ANIMATO (PROVA SEPARATA)

**[SCARICA LA NUOVA INTERFACCIA JARVIS ANIMATA — ZIP](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/animated-hud-interface.zip)**

L'interfaccia approvata dall'utente è ora nel ramo di prova: **console dei comandi e risposte sulla sinistra**, **reattore JARVIS animato al centro**, **globo olografico che ruota a destra**. Il centro passa leggermente dal **blu al turchese mentre Jarvis sta parlando**, poi torna blu. In alto trovi l'**ingranaggio ⚙**: tutte le impostazioni già esistenti sono spostate lì e non riempiono più la schermata principale. I pulsanti per salvare/annullare un documento restano visibili accanto alla chat quando servono.

**Per provare sul Pavilion:** chiudi la vecchia finestra di Jarvis, scarica lo ZIP e decomprimilo in una **cartella nuova**, poi apri `avvia_jarvis.bat`. Il microfono resta **in standby all'avvio**, da attivare solo manualmente tramite ⚙. Per vedere il bagliore del centro in azione, attiva la voce di Windows e chiedi a Jarvis di rispondere; il globo gira da solo. **Non reinstallare Vosk/GPT se già funzionanti; non cancellare la cartella vecchia né `%LOCALAPPDATA%\\Jarvis`.**

È un'implementazione grafica leggera in Tkinter, senza video o componenti aggiuntivi; **l'effetto deve ancora essere verificato fisicamente sul Pavilion**. I test automatici non sostituiscono il collaudo della finestra reale. [Guida e limiti](https://github.com/MATRIXNEO23/jarvis/blob/feature/animated-hud-interface/docs/HUD_ANIMATO.md) · [Sviluppo isolato PR #6](https://github.com/MATRIXNEO23/jarvis/pull/6).

## ULTIMA VERSIONE SPERIMENTALE — LIA IMPARA LE CORREZIONI VOCALI

**[SCARICA JARVIS CON VOCE ADATTIVA E SECOND BRAIN (ZIP)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/adaptive-offline-voice.zip)**

Questa versione mantiene **Vosk italiano offline, Conversazione continua GPT, Second Brain e i comandi precedenti**, aggiungendo il pulsante **«Correggi voce...»**. Quando Vosk sbaglia il nome di un'applicazione, puoi correggere la frase: Lia ne memorizza la correzione e la applica alle successive trascrizioni. Non si scarica nessun nuovo modello e non si usa una nuova API a pagamento.

**Prova sul Pavilion:** chiudi Jarvis; scarica lo ZIP ed estrailo in una **cartella nuova**; esegui `avvia_jarvis.bat`. Attiva manualmente **Second Brain locale** per consentire il salvataggio delle correzioni. Seleziona una modalità microfono, pronuncia una frase semplice, premi **«Correggi voce...»**, modifica la frase come l'avevi pronunciata e seleziona **«Conferma correzione»**. Ripeti la frase e verifica che venga riconosciuta correttamente. Le parole «chiudi», «salva», «non» e «Jarvis» non possono essere cambiate da questo dizionario.

**Non reinstallare Vosk né eliminare `%LOCALAPPDATA%\\Jarvis`.** Il microfono parte sempre in Standby. L'apprendimento riguarda il testo trascritto, non un riaddestramento automatico di Vosk. La versione va collaudata sul PC prima di integrarla nella versione stabile.

[Funzioni e limiti dell'adattamento vocale](https://github.com/MATRIXNEO23/jarvis/blob/feature/adaptive-offline-voice/docs/VOCE_ADATTIVA.md) · [PR sperimentale #5](https://github.com/MATRIXNEO23/jarvis/pull/5).

## NUOVA PROVA SEPARATA — SECOND BRAIN DI LIA

**[SCARICA JARVIS CON SECOND BRAIN (ZIP SPERIMENTALE)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/conversation-short-memory.zip)**

Questa variante aggiunge **memoria conversazionale breve** (capisce meglio i riferimenti alle frasi precedenti) e un **archivio persistente SQLite locale** per scambi e azioni realmente confermate, consultabile anche dopo aver riavviato Windows. Funziona sia nella conversazione vocale GPT sia nel campo «Chiedi a GPT». Mantiene catalogo comandi, dettatura e Blocco note della versione sperimentale precedente.

**Attivazione:** scarica lo ZIP di questa sezione, estrailo in una **nuova cartella** e avvia `avvia_jarvis.bat`. Nell'interfaccia seleziona **«Second Brain locale»** per consentire il salvataggio permanente (inizialmente disattivato). Puoi successivamente disattivarlo e cancellare i ricordi archiviati tramite pulsante dedicato. Il microfono resta sempre **spento all'avvio**. Non cancellare la tua vecchia cartella né `%LOCALAPPDATA%\\Jarvis`.

**Privacy:** gli scambi selezionati e le ricevute delle attività restano nel database del profilo Windows, non crittografato; brevi estratti pertinenti vengono comunque inviati al modello ChatGPT quando chiedi di utilizzarli per la conversazione. Non salvare password o dati riservati. **Lettura e invio reali delle email non sono ancora funzioni di questa versione:** il Second Brain è soltanto predisposto a registrarne in futuro le ricevute quando un modulo email avrà confermato l'invio.

[Guida completa al Second Brain e limiti](https://github.com/MATRIXNEO23/jarvis/blob/feature/conversation-short-memory/docs/SECOND_BRAIN.md) · [Ramo separato di sviluppo PR #4](https://github.com/MATRIXNEO23/jarvis/pull/4). **Versione non ancora collaudata sul Pavilion:** verificare con conversazioni fittizie prima di sostituire qualsiasi installazione.

## NOVITÀ — CATALOGO DEI COMANDI PER APPLICAZIONE

La versione **Conversazione GPT e documenti** include ora `jarvis_commands.json`, un catalogo delle azioni che Jarvis sa realmente eseguire. GPT può collegare frasi diverse alla stessa azione, per esempio **«Chiudimi Blocco note»** → `notepad.close`, senza imporre parole identiche. Aggiunta anche l'apertura del **disco locale C**. Sono supportate soltanto le funzioni con un esecutore verificato; non viene dato a GPT accesso libero ai programmi, ai file o alla shell. [Leggi il catalogo e i limiti](https://github.com/MATRIXNEO23/jarvis/blob/feature/gpt-conversazione-documenti/docs/CATALOGO_COMANDI.md).

Per provare l'aggiornamento, scarica la ZIP desiderata qui sopra e tieni separata la versione che già funziona. Il catalogo richiede ancora la prova reale sul Pavilion; il microfono parte sempre spento.

## NUOVA PROVA ISOLATA — CONVERSAZIONE GPT E DOCUMENTI

**[SCARICA LO ZIP SPERIMENTALE CON GPT CONVERSAZIONALE E BLOCCO NOTE](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/gpt-conversazione-documenti.zip)**

Questa versione aggiunge **Conversazione continua GPT** (senza ripetere «Ehi Jarvis»), risposte vocali e gestione assistita di **nuovi documenti in Blocco note classico**: GPT prepara il testo, Jarvis tenta di inserirlo, chiede se salvare e chiudere, non salvare oppure annullare, e accetta la scelta a voce. Permette un nuovo file `.txt` sul Desktop, in Documenti o Download, per esempio **«sul desktop come poesia di Venezia»**. I file esistenti non vengono mai sovrascritti. La versione è **solo di prova: i test automatici non verificano la reale automazione di Blocco note sul Pavilion**. [Funzioni, limiti e prove necessarie](https://github.com/MATRIXNEO23/jarvis/blob/feature/gpt-conversazione-documenti/docs/CONVERSAZIONE_GPT_DOCUMENTI.md).

**Installazione sul PC:** chiudi Jarvis; estrai lo ZIP in **un'altra cartella**, senza sostituire la precedente, avvia `avvia_jarvis.bat`. Non reinstallare Vosk né il DevKit GPT se sono già presenti. Non cancellare `%LOCALAPPDATA%\\Jarvis`. Il microfono rimane sempre **spento all'avvio**: per provare seleziona manualmente «Conversazione continua GPT», con ChatGPT collegato, e usa documenti di prova non importanti.

**Mantieni anche la versione vocale precedente funzionante:** è ancora disponibile nei link sottostanti. Nessun merge automatico nella versione principale.

**[NUOVA PROVA — JARVIS CON BROWSER, DETTATURA, «EHI JARVIS» E RISPOSTE A VOCE](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/voice-browser-dictation.zip)**

**AGGIORNAMENTO DETTATURA (30/10/2026):** il primo test reale sul Pavilion ha mostrato che Jarvis riconosceva le parole ma Windows rifiutava l'inserimento. La correzione modifica la struttura `SendInput` per Windows 64 bit e aggiunge test specifici: [CI Windows/Linux superata](https://github.com/MATRIXNEO23/jarvis/actions/runs/41129730526). **Da confermare nuovamente sul Pavilion.**

**Per avviare e fermare la dettatura completamente a voce:** seleziona **Ascolto continuo**, clicca nel campo di testo di Blocco note, quindi pronuncia **«Ehi Jarvis, attiva dettatura»**. Per interrompere di' **«Ehi Jarvis, disattiva dettatura»**. Una volta attiva, il parlato comune diventa testo senza ripetere «Jarvis». La modalità del microfono non cambia da sola.

**Per riprovare la correzione:** scarica di nuovo lo ZIP del **primo link**, estrailo in una **cartella nuova**, chiudi il Jarvis precedente e apri il nuovo `avvia_jarvis.bat`. **Non reinstallare Vosk** se già funziona. Non cancellare o sostituire le cartelle precedenti né `%LOCALAPPDATA%\\Jarvis`.

Il ramo di prova consente di aprire/cercare nel browser, dettare in un campo esterno, chiamare Jarvis con «Ehi Jarvis» durante l'ascolto continuo e **scegliere una voce Windows per le risposte parlate offline**. [Test automatici Windows/Linux superati](https://github.com/MATRIXNEO23/jarvis/actions/runs/41126671637); **collaudo reale sul Pavilion ancora necessario**. Non sostituisce per ora la versione vocale precedente. [Istruzioni risposte vocali](https://github.com/MATRIXNEO23/jarvis/blob/feature/voice-browser-dictation/docs/VOCE_RISPOSTE.md) · [Dettatura e browser](https://github.com/MATRIXNEO23/jarvis/blob/feature/voice-browser-dictation/docs/DETTATURA_BROWSER.md).

## SCARICA JARVIS — ZIP COMPLETO AGGIORNATO CON VOCE OFFLINE (VERSIONE DI PROVA)

**[PREMI QUI PER SCARICARE JARVIS CON LA VOCE](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/offline-voice-pavilion.zip)**

Questo link scarica lo ZIP del branch `feature/offline-voice-pavilion` con il comando vocale offline italiano e i file di installazione. **Non scaricare lo ZIP `main` se vuoi provare la voce.**

Il microfono **rimane spento a ogni avvio**. Puoi scegliere manualmente Standby, Premi per parlare e Ascolto continuo. Nessun passaggio automatico a standby per Minecraft o altri programmi.

### Installazione della versione con voce sul Pavilion

1. **Chiudi Jarvis** se e' aperto. Scarica lo ZIP dal pulsante qui sopra.
2. In Download di Windows, clic destro sullo ZIP e scegli **Estrai tutto** in **una cartella nuova**. Non cancellare o sovrascrivere la precedente cartella Jarvis.
3. Apri la cartella estratta `jarvis-feature-offline-voice-pavilion` (il nome puo' variare).
4. Fai doppio clic su **`installa_voce.bat`**: installa i moduli Vosk e SoundDevice e scarica il piccolo modello italiano ufficiale. Serve Internet soltanto per questa installazione; segui il testo nella finestra fino al completamento.
5. Fai doppio clic su **`avvia_jarvis.bat`**. Il microfono parte **spento**. Per la prima prova seleziona **Premi per parlare**, tieni premuto il pulsante e pronuncia «Jarvis, apri la calcolatrice».

Non devi reinstallare il collegamento GPT gia' installato nella cartella dei dati utente. Se l'installazione voce fallisce, il normale input testuale di Jarvis rimane utilizzabile. **Non cancellare i dati in `%LOCALAPPDATA%\Jarvis`.**

**Stato di verifica:** i test automatici Python/Node per Windows e Linux sono superati ([CI](https://github.com/MATRIXNEO23/jarvis/actions/runs/41099757267)). Il microfono fisico e le prestazioni sul tuo Pavilion non sono ancora collaudati; questa non e' una versione definitiva.

[Guida completa alla voce offline](https://github.com/MATRIXNEO23/jarvis/blob/feature/offline-voice-pavilion/docs/VOCE_OFFLINE.md) · [Codice e avanzamento della voce](https://github.com/MATRIXNEO23/jarvis/pull/1)

## Versione precedente senza voce

**[SCARICA JARVIS — ZIP PRINCIPALE (MAIN, SENZA VOCE)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/main.zip)**

Questa e' la versione gia' utilizzata per il pianificatore e i comandi testuali sul Pavilion. Mantienila finche' la prova del microfono non e' completata.

[Pagina principale del progetto](../README.md)
