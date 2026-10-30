# Jarvis — Continuità operativa

**Snapshot:** 30 ottobre 2026, ore 19:16 (Europa/Roma)  
**Repository canonica:** `MATRIXNEO23/jarvis`  
**Branch stabile/documentazione:** `main`  
**Principio:** non considerare una funzione completata senza test automatici e verifica effettiva sul Pavilion quando necessaria.

> **Aggiornamento alla ripresa, 30 ottobre 2026:** il blocco dei test della ricerca web descritto sotto è stato **corretto**. La nuova branch sperimentale ora include anche la chiamata «Ehi Jarvis» in ascolto continuo e la scelta della voce offline Windows con risposte parlate. Le nuove funzioni **non sono state ancora testate fisicamente sul Pavilion**. Lo storico sottostante rimane per tracciabilità; per lo stato attuale leggere la sezione finale.

## 1. Dove siamo arrivati

Jarvis è un assistente Windows 10 64 bit progettato per HP Pavilion i3-2100, 10 GB RAM, disco HDD; zero costi aggiuntivi, niente API a consumo. Si usa ChatGPT tramite il collegamento già configurato (SDK/DevKit ufficiale) e i comandi locali devono funzionare anche senza GPT.

Il 30/10/2026 l'utente ha verificato **di persona sul Pavilion**:
- Connessione ChatGPT e risposta a una domanda.
- Pianificatore: richiesta di apertura applicazione e controllo RAM, anteprima/approvazione ed esecuzione.
- Chiusura di Jarvis durante il piano: l'esecuzione si interrompe; al riavvio non riparte automaticamente.
- Installazione facoltativa del motore vocale italiano Vosk (installatore `installa_voce.bat` e modello `vosk-model-small-it-0.22`).
- **Premi per parlare**: comando «apri blocco note» effettivamente funzionante. Successivamente l'utente ha dichiarato che **tutti i comandi vocali proposti** funzionano sul Pavilion; non presume però che sia stato completato il collaudo approfondito di ascolto continuo durante Minecraft, consumo RAM o errori hardware.
- Il microfono deve essere **spento a ogni nuovo avvio**; il suo cambio di modalità è sempre sotto controllo manuale.

La prova vocale funzionante è sul branch `feature/offline-voice-pavilion` (HEAD osservato: `bf7ca2c243e4a953f45fc7574c0766c90e6370d3`). Ultimo CI verificato per questo branch: [run 41099757267](https://github.com/MATRIXNEO23/jarvis/actions/runs/41099757267) **SUCCESS** (Windows/Linux, Python 3.11/3.12).

## 2. Lavoro nuovo non ancora approvato né installato

**Branch in sviluppo:** `feature/voice-browser-dictation`  
**HEAD osservato:** `45285d72d1d47a25098fb99198aaf355050b5d6d`  
**Pull request:** [#2 — Browser e dettatura](https://github.com/MATRIXNEO23/jarvis/pull/2), **draft**, verso `feature/offline-voice-pavilion`. Non fare merge automatico.

Funzioni codificate ma **non ancora collaudate sul Pavilion**:
1. `apri browser` / «Jarvis, apri il browser»: apre il browser predefinito Windows tramite `webbrowser`.
2. `cerca nel browser TESTO` / «Jarvis, cerca nel browser ...»: ricerca Google con query codificata, su richiesta esplicita. Il riconoscimento vocale continua offline; una ricerca nel browser usa Internet.
3. Voce per «Jarvis, attiva dettatura» e «Jarvis, disattiva/interrompi dettatura».
4. Dettatura verso un campo di testo nella finestra Windows in primo piano tramite input Unicode Win32; attiva soltanto con **Ascolto continuo** selezionato manualmente. Non deve cambiare la modalità del microfono; alla disattivazione dettatura il microfono rimane nella modalità scelta.
5. Controlli di focus/finestra per ridurre il rischio di scrivere nella destinazione sbagliata; disattivazione della dettatura quando si passa allo standby e chiusura Jarvis.
6. Pianificatore GPT aggiornato per offrire il browser e ricerche **solo dopo approvazione del piano**.
7. Test unitari aggiunti per voce/browser, sicurezza dettatura e pianificatore; documentazione in `docs/DETTATURA_BROWSER.md`.

**Avvertenze tecniche:** il riconoscimento di campi password Win32 tradizionali non rileva necessariamente i campi password dei browser/app personalizzate. Non usare dettatura per segreti. Validare la gestione focus Win32 e `SendInput` su Windows reale, incluse app Chrome/Firefox, Blocco note e prova con Minecraft. Il testo dettato non deve essere inviato a GPT né registrato nella cronologia comandi. Nessuna clipboard.

## 3. Blocco di test noto: PRIORITÀ ALLA RIPRESA

[GitHub Actions run 41103498708](https://github.com/MATRIXNEO23/jarvis/actions/runs/41103498708) per HEAD `45285d7`: **FAILURE**. I quattro job Windows/Linux falliscono su almeno un test unitario. Il log Windows identifica:

`FAIL: test_web_search_rejects_invalid_queries (test_action_planner.PlannerPolicyTests)`  
`AssertionError: PlanRejected not raised`, subtest `query='a\\nb'` (riga 57 di `tests/test_action_planner.py`).

**Probabile causa da verificare:** il test passa una sequenza letterale backslash+n (`a\\nb`) invece di un vero carattere di nuova riga (`a\nb`), quindi l'input potrebbe essere valido secondo la policy; occorre correggere il test o precisare la validazione desiderata, senza indebolire i controlli. **Non dichiarare CI verde né distribuire il nuovo branch come build verificata prima della correzione e di una nuova run interamente verde.**

Verificare gli altri job e gli altri eventuali errori, sistemare e rieseguire. I test CI non dimostrano il corretto funzionamento della dettatura sulle finestre reali di Windows. Collaudo fisico ancora richiesto.

## 4. Stato main e download

**HEAD main osservato:** `00e3cb5697d49418d28cf765b3cc8cf73d99027d`.

Nel `README.md` principale e in `Download/README.md` sono visibili:
- ZIP **nuovo sperimentale** browser/dettatura: [branch](https://github.com/MATRIXNEO23/jarvis/tree/feature/voice-browser-dictation) — test falliti, **non sostituisce la versione collaudata**.
- ZIP **voce già provata**: [feature/offline-voice-pavilion](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/offline-voice-pavilion.zip).
- ZIP `main`: codice base precedente senza voce.

I link per il download DEVONO restare **nella pagina GitHub della repository**, non soltanto nella chat, perché l'utente parla dal telefono mentre lavora sul PC.

**NOTA PER LA RIPRESA:** aggiornare l'indicazione dei test nel README/Download; al momento del presente snapshot i test dell'ultima versione sono **falliti**, non soltanto «in corso».

## 5. Requisiti fissi del progetto

- Avvio Jarvis: microfono **sempre SPENTO (standby)** e nessuna cattura audio automatica, anche dopo riavvio del PC.
- Modi voce **Standby, Premi per parlare, Ascolto continuo** selezionabili manualmente. Durante Minecraft o software pesante l'ascolto continuo **non** può diventare standby autonomamente; su guasto hardware è lecito chiudere il dispositivo senza cambiare la modalità scelta dall'utente.
- GPT abilitato di default, ma attivabile/disattivabile manualmente; nessun timeout d'inattività GPT imposto da Jarvis. Autenticazione richiesta. Niente API a consumo.
- Offline locale sempre possibile; motore Vosk già installato non va reinstallato a ogni nuova versione.
- Piani e comandi locali controllati, nessuna shell arbitraria; cancellazione, modifica dati e scrittura GitHub solo con approvazione specifica. Non contaminare i dati degli utenti o sovrascrivere `%LOCALAPPDATA%\Jarvis`.
- Conservare la versione funzionante in una cartella separata prima di provare la successiva.
- Test superati **non implicano** adozione automatica o merge; occorre decisione separata.
- L'utente intende più avanti gestire file di progetto (`.md`, `.json`, `.py`, `.js`, `.yml`, ecc.), modificarli con backup/ripristino e lavorare su repository GitHub: questa parte **non è stata ancora implementata**. Priorità attuale: consolidare voce, browser e dettatura.

## 6. Sequenza precisa quando l'utente dice «continua»

1. **Recupera questa continuità e rileggi la repository** su GitHub; verifica HEAD attuali e stato CI, senza ricostruire i risultati da memoria.
2. Risolvi il test fallito `test_web_search_rejects_invalid_queries`; verifica la policy di input e la stringa del test.
3. Riesegui o attendi CI Windows/Linux completo. Correggi eventuali ulteriori errori; non chiedere all'utente di installare la versione sperimentale con CI rosso.
4. Esegui review approfondita del codice di dettatura: ABI `SendInput`/Win32 su 64-bit, focus, password, chiusura, uso corretto di listener Vosk, compatibilità Python 3.12; aggiungi test dove necessario.
5. Aggiorna README/Download con stato fedele, poi pubblica il pacchetto di prova nella repository GitHub.
6. Solo dopo CI verde, guida l'utente sul Pavilion per provare browser, ricerca e dettatura; nessun download/passaggio dal telefono e nessuna reinstallazione vocale non necessaria.
7. Mantieni i branch di prova isolati e decidi il merge solo dopo collaudo e consenso.

**Stato della sessione:** l'utente ha richiesto una pausa e di salvare il file di continuità; **non procedere con altre modifiche funzionali o con merge** finché non torna a chiedere di continuare.

## 7. Aggiornamento sviluppo e punto di ripresa dopo la pausa

**Data:** 30/10/2026, dopo il rientro dell'utente. **Branch di lavoro isolato:** feature/voice-browser-dictation. Non è stato fatto alcun merge verso main né verso la versione vocale già collaudata.

### Test fallito nella sessione precedente: risolto

Nel file tests/test_action_planner.py il caso di input non valido ora utilizza una vera nuova riga, anziché i due caratteri letterali backslash+n. La validazione applicativa mantiene il rifiuto dei caratteri di controllo: nessuna policy di sicurezza è stata allentata. [Run corretta, success](https://github.com/MATRIXNEO23/jarvis/actions/runs/41125847511).

### Funzioni sperimentali aggiunte durante questa ripresa

- In **Ascolto continuo**, i comandi richiedono il nome «Ehi Jarvis» o «Jarvis»; «Ehi Jarvis» isolato attiva la finestra di **un comando successivo entro 10 secondi** senza cambiare la modalità del microfono. Il tempo riguarda soltanto l'attesa del comando, non il microfono. In Premi per parlare, il pulsante già costituisce attivazione manuale; nessuna wake word obbligatoria.
- Il filtro «Ehi Jarvis» distingue i comandi dal parlato libero. Quando la dettatura è attivata manualmente, il parlato comune resta testo, mentre «Ehi Jarvis, disattiva dettatura» è riconosciuto come comando.
- Nuovo modulo **offline_tts.py**: sintesi vocale locale Windows SAPI tramite PowerShell/System.Speech, senza API a pagamento e senza modelli da scaricare. I testi sono passati tramite JSON su standard input e non interpolati nel codice eseguibile.
- Nuova interfaccia: **Jarvis risponde a voce** (opzione separata, disabilitata di default), elenco delle voci Windows già installate, scelta voce, pulsante **Prova voce**. Risposte parlate ai comandi completati e alle risposte GPT, limite 600 caratteri per messaggio.
- Le impostazioni tts_enabled e tts_voice sono persistenti e compatibili con il vecchio settings.json. GPT resta indipendente.
- Durante la riproduzione audio di Jarvis, il riconoscimento ignora l'audio degli altoparlanti per evitare auto-attivazioni senza spegnere il microfono o passare in standby.
- Documentazione e test: docs/VOCE_RISPOSTE.md, tests/test_offline_tts.py, test impostazioni e WakeWordGate.

### Verifica automatica

[CI completa Windows/Linux SUCCESS per revisione codice aac2bf0](https://github.com/MATRIXNEO23/jarvis/actions/runs/41126671637), inclusi i nuovi test. Aggiornamenti successivi alla documentazione non alterano la logica testata. **CI verde non equivale a collaudo reale** del motore System.Speech, voci installate, microfono Vosk, audio di ritorno o interazione con altre finestre sul Pavilion.

### Prossimo intervento pratico

1. Verificare che l'ultima CI della branch sia interamente verde e controllare la HEAD, soprattutto dopo modifiche alla documentazione.
2. L'utente lavora dal PC e parla dal cellulare: la versione di prova e la versione già funzionante sono entrambe disponibili dalla [cartella Download su main](https://github.com/MATRIXNEO23/jarvis/tree/main/Download). **Mai passare soltanto un link in chat come unico canale di download.**
3. Sul Pavilion conservare la cartella vecchia e testare la nuova ZIP in un'altra cartella. Non reinstallare Vosk se già presente, non cancellare dati LOCALAPPDATA.
4. Collaudare elencazione di voci (specie italiana), selettore, pulsante Prova, risposta ai comandi e GPT, nessun feedback dal microfono, wake word, ricerca browser, dettatura, cambio focus, avvio in standby e comportamento con Minecraft.
5. Non effettuare merge o adottare automaticamente la nuova versione prima del collaudo fisico e della decisione separata dell'utente.

**Requisiti fissi invariati:** zero costi aggiuntivi, PC HP Pavilion i3-2100 con 10 GB RAM Windows 10, ascolto continuo sempre selezionato dall'utente e mai spostato in standby autonomamente, microfono sempre spento a ogni nuovo avvio.
