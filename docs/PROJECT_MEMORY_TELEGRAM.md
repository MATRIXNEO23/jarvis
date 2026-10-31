# JARVIS — progetti, continuità, orbite e Telegram vocale

**Prototipo sperimentale**: ramo `feature/project-memory-orbits-telegram`, [PR #12 draft](https://github.com/MATRIXNEO23/jarvis/pull/12). Discende dall'HUD con sfondo cinematografico ed è isolato: non sovrascrive la versione precedente né modifica automaticamente il branch stabile. Tutti i dati di memoria e configurazione restano sul computer Windows. **Nessun invio Telegram live è stato effettuato dai test automatici.**

## Progetti e Second Brain

Nella finestra JARVIS, in basso nella console, usa **Progetti**; oppure apri ⚙ > **Gestisci progetti / apri continuità**. Il gestore permette di creare, aprire, archiviare e riattivare un progetto.

- Ciascun progetto ha un **identificatore immutabile** (non il nome o il percorso); conversazioni e ricerca hanno lo stesso `scope_id`. Gli scambi del Progetto A non vengono salvati come scambi generali o del Progetto B.
- La memoria generale continua a utilizzare il precedente Second Brain; lo storico esistente non viene cancellato, migrato né confuso con i nuovi progetti.
- La nuova base `%LOCALAPPDATA%\Jarvis\jarvis_workspaces.sqlite3` contiene indici SQLite per contesto e ricerca FTS5. Se FTS5 manca, la ricerca è limitata agli ultimi 150 scambi, evitando di caricare tutta la base dati.
- Ogni progetto ha un file leggibile `%LOCALAPPDATA%\Jarvis\projects\<id>\CONTINUITA.md`, aggiornato automaticamente con ultimi scambi, nome, stato e data. Esiste anche `CONTINUITA.previous.md` come precedente snapshot e lo storico integrale in SQLite. Lo **stato consolidato** è scritto dall'utente nel gestore, non inventato dal modello.
- **Importante:** la registrazione persistente delle conversazioni rimane subordinata all'opzione esistente **Second Brain locale**. Se è spenta, i progetti sono comunque creabili e i file di stato esplicitamente salvati restano, ma la chat non viene registrata automaticamente. Se desideri continuità della chat, attiva Second Brain da ⚙.
- Per passare al generale usa **Generale** nel gestore. Il cambio di contesto svuota la memoria breve in RAM e non riutilizza il contesto del progetto precedente. Non cambia contesto durante una chiamata GPT ancora in elaborazione.

### Pallini sul nucleo

- **Ciano** = progetti attivi, un pallino per progetto. Ruotano lentamente con il nucleo; mouse sopra = nome; clic = passa al progetto. Gli archiviati spariscono dall'orbita, ma restano nel gestore.
- **Viola** = storico Telegram del contatto autorizzato (messaggi ricevuti, risposte vocali effettuate e nuovi messaggi); mouse sopra = contatore, clic = registro cronologico Telegram.
- **Ambra** = messaggio esplicitamente lasciato dall'utente e ancora da riferire.
- Per non coprire il nucleo, oltre il limite visivo compare un indicatore “Altri progetti”, che apre il gestore completo.

Gli indicatori sono costruiti con pochi oggetti Tk Canvas e animati nella frequenza HUD già esistente. Non cambiano microfono, GPT o permessi dei file.

## Personalità

JARVIS usa un tono più ironico e un po' irriverente, ma mai offensivo. Di norma risponde in **1–3 frasi**, senza lunghi preamboli. Se richiedi un'analisi approfondita, deve spiegare tutto ciò che serve.

## Telegram personale: attivazione esplicita e note vocali

**Sono necessarie tre cose gratuite:**
1. Il pacchetto Python **Telethon**. Esegui `installa_telegram.bat`. Nessun abbonamento o servizio a consumo.
2. **FFmpeg** nel PATH di Windows, per convertire il WAV di Microsoft SAPI in **OGG/Opus**, formato necessario per una vera **nota vocale Telegram**. È software libero; va installato separatamente se manca. JARVIS rifiuta l'attivazione vocale quando non è disponibile, senza fingere di inviare un vocale.
3. Il tuo **api_id** e **api_hash** di Telegram, ottenuti tramite `https://my.telegram.org` e un account Telegram personale. Questi dati sono richiesti dall'API ufficiale client MTProto, **non** sono una chiave API OpenAI né un costo ChatGPT. L'accesso può richiedere un codice Telegram e l'eventuale password in due passaggi.

**Configurazione**: apri `configura_telegram.bat` e segui le istruzioni. Una finestra elenca SOLO le chat private personali effettive; scegli **un contatto** per indice e conferma digitando esattamente `SI`. Non vengono autorizzati gruppi, bot o altri contatti. L'app salva `api_hash` e sessione MTProto cifrati **Windows DPAPI**, nel profilo di quello specifico utente, `%LOCALAPPDATA%\Jarvis\telegram-auth.dpapi`. In `settings.json` salva solo ID numerico, nome e flag ON/OFF. Non copiare il file delle credenziali né pubblicarlo su GitHub.

**Avvio**: riapri JARVIS oppure premi ⚙ > **Rileggi contatto autorizzato**; verifica che il contatto sia esattamente quello giusto. L'interruttore **Risposte vocali automatiche** è **OFF di default** anche dopo il collegamento. Dopo l'attivazione, JARVIS può rispondere autonomamente via **note vocali OGG/Opus Microsoft SAPI** a **nuovi messaggi in chat privata di quel singolo contatto** finché l'applicazione e il computer sono accesi. Serve anche ChatGPT connesso e abilitato nel programma; in assenza di GPT registra l'arrivo, ma non inventa una risposta.

JARVIS si presenta chiaramente come **assistente**, non impersona l'utente, e la persona deve sapere che è attiva un'automazione. Può comprendere i testi e, se Vosk italiano e FFmpeg sono disponibili, trascrivere i vocali ricevuti (dimensione e durata limitate). La voce emessa è la SAPI già selezionata in JARVIS; il modello più naturale potrà essere valutato in futuro.

**Memoria Telegram**: il contatto dispone di una propria cronologia indicizzata, separata da progetti, dialogo generale e ricevute private. Soltanto le istruzioni lasciate **esplicitamente** dall'utente vengono condivise. Per esempio, nel campo chat o a voce: **“Jarvis, riferisci alla mia amica che domani potrò parlarle”**; oppure il pulsante **Lascia un messaggio per il contatto**. L'istruzione viene conservata come pendente fino alla risposta autorizzata e risulta inviata soltanto con ricevuta del provider; in caso di invio incerto non viene ritentata automaticamente, evitando duplicati.

L'indicatore Telegram viola tiene conto di messaggi **ricevuti e risposti durante l'attività del connettore**. Con l'interruttore OFF la connessione è chiusa: non effettua monitoraggio in background e non risponde. Non recupera automaticamente messaggi vecchi non ascoltati, e non può funzionare a PC spento.

## Sicurezza e limiti

- Nessuna azione automatica su contatti diversi dall'ID autorizzato; si accettano solo messaggi **privati entranti**.
- I messaggi Telegram non autorizzano comandi Windows, accesso ai file, ad altri contatti o ad archivi dei progetti.
- Non si caricano tutte le conversazioni nel prompt GPT. Ricerca mirata SQLite FTS5, contesto breve e limiti su numero e dimensione delle stringhe.
- Le risposte hanno un limite di lunghezza e frequenza. Un mancato invio non viene presentato come successo.
- La conversione di audio richiede CPU quando arriva un vocale, ma non usa nuovi processi residenti mentre il sistema è inattivo. Il costo CPU sul Pavilion i3-2100 va verificato.
- La registrazione e l'uso di questa integrazione con un account personale devono rispettare i termini Telegram. È opportuno che il contatto conosca il ruolo di JARVIS.
- **Nessun test automatico invia realmente messaggi Telegram**: gli esiti CI convalidano logica, archiviazione e interfacce, non la connessione reale, il login, la qualità vocale o i permessi Telegram. Collaudare prima un singolo messaggio dopo autorizzazione.

### Prova della ZIP

Scarica `https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/project-memory-orbits-telegram.zip`, estraila in una **cartella nuova** e avvia `avvia_jarvis.bat`. Non cancellare `%LOCALAPPDATA%\Jarvis`, il precedente Vosk, le altre installazioni né la repository principale. Verifica prima creazione progetti, pallini, mouse hover, click, file continuità, separazione di contesti, voce breve/ironia e memoria; configura Telegram **solo dopo** questi controlli. Non integrare automaticamente il ramo in `main` senza l'approvazione dopo il test sul Pavilion.
