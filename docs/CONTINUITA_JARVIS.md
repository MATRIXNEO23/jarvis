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


## 8. Collaudo reale: bug dettatura e correzione del 30/10/2026

Durante il collaudo effettivo della nuova versione `feature/voice-browser-dictation` sul Pavilion, l'utente ha confermato che:
- Vosk riconosce il parlato (ad es. «ciao»); il microfono e l'ascolto continuo funzionano.
- Durante dettatura, **né Blocco note né il browser ricevevano testo**; Jarvis stampava «Windows non ha inserito il testo; controlla la finestra selezionata».
- La dettatura era selezionata («Disattiva dettatura» visibile) e Blocco note aveva il focus, quindi il problema non era soltanto la selezione del campo.

### Causa individuata nel codice, correzione pubblicata

In `desktop_dictation.py` la union `_InputUnion` conteneva solo `KEYBDINPUT` e il `ctypes.sizeof(_Input)` risultava **32 byte su architettura 64 bit**, mentre `SendInput` per Win64 richiede **40 byte**. Windows respinge una `cbSize` errata. Aggiunto layout completo di `MOUSEINPUT` alla union, verifica preventiva `sizeof(INPUT)==40` Win64 (28 Win32), gestione esplicita `GetLastError` e testo UI che non dichiara mai che i caratteri sono comparsi se Windows ha soltanto accettato gli eventi. Regressioni in `tests/test_desktop_dictation.py`: dimensione ABI, invio Unicode con mock Windows e errore 87.

**CI nuovo codice test superata:** [run 41129624639](https://github.com/MATRIXNEO23/jarvis/actions/runs/41129624639). La successiva [run 41129730526](https://github.com/MATRIXNEO23/jarvis/actions/runs/41129730526) ha superato tutti i test con nuove prove dei comandi vocali attiva/disattiva. Le prove automatiche **non sostituiscono** la verifica sul Pavilion di caratteri davvero scritti.

### Richiesta ulteriore utente: attivazione/disattivazione dettatura con la voce

Richiesta esplicita durante il collaudo: i pulsanti `Attiva dettatura` e `Disattiva dettatura` devono avere equivalenti pronunciabili senza mouse. **Già presenti nel routing**, ora coperti da test di integrazione logica tra `WakeWordGate`, `dictation_voice_action` e `DesktopDictation`, nel branch sperimentale:
- «**Ehi Jarvis, attiva dettatura**» (oppure «Ehi Jarvis», pausa, «attiva dettatura»).
- «**Ehi Jarvis, disattiva dettatura**»; alternativa «Ehi Jarvis, interrompi dettatura».
- Dopo l'attivazione il parlato normale viene scritto nel campo selezionato senza wake word. I comandi richiedono sempre il nome esplicito nell'ascolto continuo, in conformità al requisito utente. Pronunciare «disattiva dettatura» come testo libero senza chiamare Jarvis **non** deve poter spegnere autonomamente la dettatura.
- Il microfono non cambia modalità automaticamente; spegnere la dettatura non equivale a standby.
- Documentato in `docs/DETTATURA_BROWSER.md`.

### Stato e istruzioni per la ripresa del test

1. Nel branch sperimentale `feature/voice-browser-dictation` sono stati pubblicati il fix e i test; la vecchia versione vocale `feature/offline-voice-pavilion` **non è stata modificata**; nessun merge richiesto/autorizzato.
2. Il download ZIP del ramo di prova si trova come **primo link** della pagina `main/Download/README.md` del repository GitHub, accessibile direttamente dal PC dell'utente.
3. **Chiudere il Jarvis ancora aperto, estrarre lo ZIP aggiornato in una cartella nuova** (senza eliminare il vecchio) e avviare `avvia_jarvis.bat`. Non reinstallare Vosk già funzionante e non cancellare `%LOCALAPPDATA%\\Jarvis`.
4. Selezionare **Ascolto continuo** manualmente e verificare lo stato microfono attivo. Aprire Blocco note, cliccare sulla pagina bianca, pronunciare «Ehi Jarvis, attiva dettatura», poi una frase. Verificare che **appaia effettivamente** nel documento, non solo nel registro di Jarvis. Pronunciare «Ehi Jarvis, disattiva dettatura» e verificare che ulteriori frasi non vengano scritte.
5. Se continua a fallire, fotografare il messaggio nuovo con eventuale **codice Windows** nel registro e non indovinare nuovi fix. Testare su un campo browser solo dopo Blocco note.
6. Prima di affermare «funziona sul Pavilion», attendere la conferma reale dell'utente. I test automatici da soli non bastano.

**Continuità preservata.** Non introdurre API a consumo, non eliminare la vecchia build, non effettuare merge automatici.


## 9. Nuovo requisito: conversazione GPT naturale e controllo vocale dei documenti

**Richiesta confermata dall'utente:** in una modalità **Conversazione continua con GPT** selezionabile manualmente, Jarvis ascolta le frasi senza richiedere «Ehi Jarvis», distingue conversazione/risposte vocali e comandi di Windows, e **scrive direttamente il contenuto richiesto in documenti** senza dover attivare/disattivare la dettatura a ogni operazione. Può inventare testi, inserirli nel documento e, quando l'utente vuole chiudere Blocco note, chiedere **«salva e chiudi», «chiudi senza salvare» o «annulla»**. Se il file non ha nome/percorso, deve chiedere una destinazione. La chiusura senza salvare, se sono presenti modifiche, richiede una conferma esplicita ulteriore. L'utente non programma; tutta l'interazione deve poter essere vocale.

**Il requisito NON è ancora disponibile nel programma installato.** Il riconoscimento continuo Vosk, il TTS SAPI e GPT sono componenti esistenti ma il router naturale, il controller di documenti e l'integrazione Blocco note devono essere sviluppati e provati.

**Sviluppo isolato iniziato** in `feature/gpt-conversazione-documenti`, PR [#3 draft](https://github.com/MATRIXNEO23/jarvis/pull/3), basato sulla versione corretta `feature/voice-browser-dictation`. File nuovo `docs/CONVERSAZIONE_GPT_DOCUMENTI.md` con schema di fiducia e acceptance; `document_dialog.py` è una macchina a stati **senza effetti su file o finestre** per conferme di chiusura/salvataggio, annullamento e revoca, con test in `tests/test_document_dialog.py`. Non confondere questo kernel con una funzionalità completa dell'interfaccia.

**Prossimi passi obbligatori:** validare CI; aggiungere router GPT vincolato a JSON per parlare vs. agire vs. comporre testo; inserimento testo via controller Windows in documento identificato; gestione salvataggi reali con backup/preview; nuova modalità UI manuale; risposte vocali di conferma; test automatizzati e reali sul Pavilion. Nessuna API a pagamento, merge o sostituzione della build funzionante senza consenso.


### Aggiornamento primo prototipo funzionale (ramo isolato, stesso giorno)

Nel ramo `feature/gpt-conversazione-documenti` sono stati aggiunti:
- `conversation_router.py`: prompt strutturato e validazione rigida dei tipi di risposta GPT: conversazione, chiarimento, comando consentito, bozza di documento e richiesta di chiusura. Blocca tool arbitrari, parametri estranei, salvataggi forzati e file scelti dal modello.
- La modalità microfono **«Conversazione continua GPT»** è ora selezionabile manualmente in `jarvis.py` e `voice_control.py`. In questa modalità il parlato non richiede wake word, i comandi locali già noti rimangono eseguibili offline e le altre frasi vanno al DevKit ChatGPT con risposta TTS Windows. Lo stato conversazionale invalida le risposte tardive al cambio modalità o alla disconnessione.
- `document_dialog.py`: policy separata di conferma vocale «salva e chiudi», «chiudi senza salvare», «annulla», con scelta destinazione per documenti nuovi e revoca; per ora **non agisce su file né finestre**.
- Test nuovi per transizioni e parser; GitHub CI [run 41132795533](https://github.com/MATRIXNEO23/jarvis/actions/runs/41132795533) SUCCESS sul codice, con ulteriore verifica sul documento in corso.
**ATTENZIONE:** quando GPT riceve una richiesta di scrittura, il programma in questo prototipo **mostra soltanto una BOZZA e dichiara che non l'ha inserita**; quando GPT riceve una richiesta di chiudere, risponde che il controllo documenti non è pronto e **non chiude nulla**. I dialoghi di salvataggio non sono ancora cablati alla GUI o a Blocco note. Non far scaricare questa branch come se la funzione completa fosse disponibile; mancano controller Windows, salvataggi verificati, backup e test Pavilion. Tenere la PR #3 in draft e il ramo vocale precedente intatto.

Prossima fase: implementare controller documenti e gestione del focus/Notepad senza `taskkill`, collegare conferme vocali con salvataggio atomico e backup, prove hardware reali, solo poi decidere distribuzione.


## 10. Implementazione di prova end-to-end dei documenti — 30/10/2026

**Fonte canonica di codice per la nuova modalità:** `feature/gpt-conversazione-documenti`. PR [#3 draft](https://github.com/MATRIXNEO23/jarvis/pull/3). **Non integrata in main o nella build già funzionante sul Pavilion.** La nuova ZIP è raggiungibile dalla [pagina Download nella repository](https://github.com/MATRIXNEO23/jarvis/tree/main/Download), perché l'utente parla da telefono ma lavora al PC.

**Richiesta utente:** parlare in modo naturale con GPT senza wake word nella modalità scelta volontariamente; «Apri Blocco note e scrivimi un testo su X, poi chiudi» → GPT genera il testo; Jarvis scrive nella finestra; domanda «salva e chiudi», «chiudi senza salvare» o «annulla»; riceve la conferma a voce; se non ancora salvato chiede nome e cartella. Spegnimento/ripristino della dettatura non necessario in modalità GPT. Nessun costo API.

**Codice implementato nel ramo isolato**:
- `conversation_router.py`: classificazione GPT a JSON validato con tipi conversazione, tool locale, testo, chiusura, chiarimento; campo `close_after` chiede la conferma **dopo** l'inserimento. Selezione del documento vincolata all'ID del documento aperto quando l'utente ha parlato.
- `jarvis.py`: scelta manuale Conversazione continua GPT, inoltro trascrizioni al DevKit GPT, dialoghi vocali con sintesi Windows, instradamento delle scelte «salva/annulla/non salvare» senza consultare GPT. Pulsanti aggiuntivi di conferma e selezione percorso come fallback. Risposte stale GPT scartate dopo cambio modalità o disconnessione.
- `notepad_controller.py`: lancia un nuovo Blocco note classico e conserva PID/HWND/control Edit/titolo originali; scrive tramite `WM_SETTEXT` Windows, rilegge e verifica il testo; legge anche modifiche manuali prima di salvare, chiude **solo quella finestra** dopo salvataggio verificato o doppia conferma di scarto; niente `taskkill`, shell, clipboard o tasti globali. App Notepad moderne non riconosciute vengono lasciate intatte.
- `managed_documents.py`: sessione unica, apertura, composizione, aggiunta di testo senza sovrascrivere il preesistente, salvataggio e chiusura con gestione di esiti parziali, recupero se l'utente chiude manualmente.
- `document_store.py`: interpreta la destinazione parlata soltanto per **Desktop, Documenti o Download** e nomi `.txt` semplici, rispetta percorsi Windows reindirizzati, salva file **nuovi** con `O_EXCL` e `fsync`, rifiuta file già esistenti. La modifica di file .md/.json preesistenti e delle repository **non è ancora implementata**, non nasconderlo.
- `document_dialog.py`: macchina a stati richiesta scelta, domanda nome/percorso, doppia conferma perdita modifiche, annullamento, revoca dopo disconnessione; non è consentito a GPT decidere di scartare.
- Test unitari con Notepad simulato; CI [run 41134478291](https://github.com/MATRIXNEO23/jarvis/actions/runs/41134478291) SUCCESS per l'ultima revisione con nuovi test. Quando nuovi commit vengono aggiunti, verificare sempre il CI aggiornato.

**STATO REALE:** il codice e la logica sono implementati nel ramo di prova, ma la *reale* automazione Win32 Notepad e le voci di conferma **non sono ancora state collaudate dal Pavilion**. Non dichiarare il collaudo riuscito prima della verifica utente.

**Prova richiesta all'utente (solo file nuovi/non importanti):** salvare l'installazione corrente, estrarre nuova ZIP in una cartella diversa, avviare in standby, selezionare Conversazione continua GPT, chiedere «Apri Blocco note e scrivi una poesia su Venezia, poi chiudilo»; controllare che il testo compaia davvero in Blocco note, rispondere «annulla»; chiedere di chiudere di nuovo, dire «salva e chiudi», poi «sul desktop come poesia di Venezia»; verificare file creato e *solo* quel Blocco note chiuso. Testare inoltre «chiudi senza salvare» con seconda conferma, presenza di altro Blocco note aperto e ripetizione dello stesso nome (nessuna sovrascrittura).

**Blocco temporaneo all'adozione:** nessun merge automatico, non cancellare la vecchia build e non sovrascrivere `%LOCALAPPDATA%\\Jarvis`. Se il controllo finestra fallisce, lasciare il documento aperto e leggere il messaggio. In particolare, su alcuni Windows 10 la versione Notepad può avere un layout diverso da quello classico.


## 12. Lia Second Brain — continuità breve e permanente

Nuova richiesta esplicita dell'utente durante il collaudo: Lia non deve perdere il contesto alla frase successiva, e negli anni dovrà ricordare le attività **realmente compiute**. Esempio prospettico: «ti ricordi quella mail che hai inviato due giorni fa?» deve recuperare una ricevuta di invio con destinatario, oggetto, data e riferimento, ma **solo dopo l'effettiva conferma del servizio email**. Non confondere il desiderio futuro con un modulo posta già disponibile.

Sviluppo separato nel branch `feature/conversation-short-memory`, PR [#4 draft](https://github.com/MATRIXNEO23/jarvis/pull/4), basato sul ramo di GPT conversazionale e catalogo. File principali:
- `conversation_memory.py`: memoria RAM limitata agli scambi recenti, gestione di domande di chiarimento e follow-up;
- `second_brain.py`: SQLite persistente nel profilo locale Windows, dialoghi brevi e ricevute verificate, ricerca datata e recupero dopo riavvio; `record_email_sent` è **solo hook per un futuro adattatore email**, non un esecutore mail;
- `conversation_router.py` e `jarvis.py`: gli estratti recenti e pertinenti entrano come contesto GPT senza essere autorizzazioni; registrazione conversazione e azioni confermate del motore locale/Blocco note; anche il campo «Chiedi a GPT» recupera memoria;
- `settings.py`: opzione `memory_enabled` manuale, inizialmente **falsa**, e interfaccia per attivare/disattivare e cancellare la memoria;
- `tests/test_second_brain.py` e aggiornamenti ad altri test: riavvio, idempotenza, privacy, ricevuta mail simulata, no replay, limite prompt DevKit 5000.

Documentazione della feature: [docs/SECOND_BRAIN.md](https://github.com/MATRIXNEO23/jarvis/blob/feature/conversation-short-memory/docs/SECOND_BRAIN.md). ZIP da provare nel PC, **senza sovrascrivere le versioni precedenti**: [Download su GitHub](https://github.com/MATRIXNEO23/jarvis/tree/main/Download). Nessun merge nella versione funzionante senza prova e adozione esplicita.

**Privacy:** salvataggio persistente solo dopo opt-in; SQLite locale non cifrato, nel profilo Windows; brevi estratti saranno comunque trasmessi a ChatGPT per la comprensione in modalità GPT. Vietata l'archiviazione automatica dei corpi email e di segreti. Il pulsante cancella il Second Brain, non il vecchio `tasks.db` del motore locale. Disattivare non elimina i dati già salvati. Non cancellare `%LOCALAPPDATA%\\Jarvis` durante i test.

**Test fisico ancora da fare**: memoria a breve su due frasi, chiusura/riapertura e recupero di informazioni precedenti, azioni effettivamente eseguite, azzeramento dopo cancellazione, nessun riavvio di azioni vecchie. Nessuna email reale in questo test.


## 13. Adattamento vocale Vosk leggero — ramo sperimentale (31 ottobre 2026)

L'utente ha approvato il miglioramento progressivo del riconoscimento vocale senza appesantire l'HP Pavilion i3-2100/10GB RAM, mantenendo Vosk offline, nessuna API a pagamento, nessun secondo modello caricato continuamente, nessun cambio automatico della modalità microfono.

**Sviluppo isolato:** `feature/adaptive-offline-voice`, PR [#5 draft](https://github.com/MATRIXNEO23/jarvis/pull/5), derivato dal Second Brain precedente. **Non toccare le versioni stabili già collaudate.** ZIP sperimentale [Download](https://github.com/MATRIXNEO23/jarvis/tree/main/Download).

Implementazioni:
- `adaptive_voice.py`: dizionario di correzioni approvate esplicitamente in SQLite locale `%LOCALAPPDATA%\\Jarvis\\second_brain.sqlite3`, massimo 80 correzioni, regex precompilate in RAM e un solo passaggio per frase. Nessun audio archiviato, nessun modello nuovo.
- In `jarvis.py` pulsante **«Correggi voce...»** apre popup. Il testo Vosk dell'ultima frase è mostrato all'utente; l'utente inserisce la frase effettivamente pronunciata e preme **«Conferma correzione»**. Il modulo estrae la differenza di 1–4 parole, ad esempio «apri blocco moto» → «apri blocco note», imparando la variante del nome applicazione.
- Applicazione della correzione **prima** del wake gate/comando locale/router GPT e in dettatura. Correzioni che cambiano wake word, verbi di comando, negazioni, conferme o riferimenti a percorsi/script sono rifiutate. Il Second Brain deve essere opt-in per conservare e applicare le correzioni.
- Pulsante separato per cancellare il solo dizionario correzioni e aggiornamento di `SecondBrain.clear_all` per cancellarle quando si cancella tutta la memoria. Disattivare Second Brain sospende l'applicazione delle correzioni e non cancella i dati salvati.
- Test `tests/test_adaptive_voice.py` per persistenza, differenza tra frasi, sicurezza, compatibilità Windows/Ubuntu, limite dizionario, non riattivazione dei comandi per effetto di dati pregressi.

**Stato e limiti:** il riconoscitore acustico Vosk resta invariato, non c'è ancora VAD/denoise avanzato, Whisper o training continuo. Questo è un **adattatore testuale controllato**. Prima di dire che «il microfono impara», chiarire sempre che viene migliorato il testo riconosciuto grazie alle correzioni esplicite dell'utente. È necessario un test fisico sul Pavilion per misurare il vantaggio e il costo CPU. La build non è automaticamente approvata all'adozione. Guida [docs/VOCE_ADATTIVA.md](https://github.com/MATRIXNEO23/jarvis/blob/feature/adaptive-offline-voice/docs/VOCE_ADATTIVA.md).

**CI finale confermata:** [run 41145317021](https://github.com/MATRIXNEO23/jarvis/actions/runs/41145317021), tutte e quattro le combinazioni Python 3.11/3.12 × Windows/Ubuntu SUCCESS sul commit `5297bc836bd617af0dbc3c4c48ba769512928117`. La versione Windows fisica del Pavilion non è ancora collaudata.


## 14. Interfaccia JARVIS HUD — globo e nucleo animati (31 ottobre 2026)

L'utente ha approvato un concept futuristico blu/ciano e ha chiesto di implementare una nuova interfaccia **senza lasciare statico il globo a destra**: il mondo deve ruotare, con elementi discreti in movimento. Requisiti vincolanti: **scritta JARVIS fissa al centro** (non Lia); grande cerchio centrale animato; **mentre la voce di Jarvis parla il centro sfuma leggermente dal blu al turchese e torna blu quando termina**; console/chat a sinistra con ciò che dice l'utente, risposte e operazioni; impostazioni prima visibili nella finestra principale soltanto dietro l'ingranaggio ⚙. Tema scuro blu/nero olografico. Niente costi nuovi o modelli pesanti; preservare funzioni/microfono e la build precedente.

**Implementazione isolata:** branch `feature/animated-hud-interface`, [PR #6 draft](https://github.com/MATRIXNEO23/jarvis/pull/6), basato su `feature/adaptive-offline-voice`. Modulo `animated_hud.py`: Canvas Tkinter puro con cerchi/archetti rotanti, nucleo JARVIS che varia gradualmente colore **solo con `OfflineSpeaker.is_speaking()`**, globo di punti proiettati che ruota lentamente, indicatori reali MIC/GPT/memoria, RAM/disco C/orario senza valori inventati. Aggiornamento grafico ogni ~110ms, refresh costoso ~7s, nessun video/GPU/Chromium e nessuna geolocalizzazione. `offline_tts.py`: nuova lettura non invasiva dello stato di sintesi vocale. `jarvis.py`: HUD finestra principale 1200×670, console laterale con righe cronologiche colorate e orari, input/comandi visibili; impostazioni in `Toplevel` scrollabile nascosto, apertura tramite ⚙; pulsanti per file/save/annulla nella console soltanto quando servono. Microfono sempre in standby all'avvio e modalità manuali invariate. Test matematici e stato SAPI in `tests/test_animated_hud.py`.

**Fonte/istruzioni:** [docs/HUD_ANIMATO.md](https://github.com/MATRIXNEO23/jarvis/blob/feature/animated-hud-interface/docs/HUD_ANIMATO.md); ZIP sperimentale dalla [cartella Download](https://github.com/MATRIXNEO23/jarvis/tree/main/Download) e direttamente `https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/animated-hud-interface.zip`.

**Non dichiarare collaudata l'animazione sul Pavilion:** GitHub CI testa sintassi e matematica, non mostra la grafica live né misura la CPU reale del vecchio i3. Necessaria prova fisica con TTS attivo, audio che cambia il centro, globo rotante, console, pannello impostazioni e salvataggio file, prima di approvare l'adozione. Il ramo stabile/vecchie ZIP restano intatti; nessun merge automatico.


**Verifica automatica conclusiva HUD:** [CI run 41148255002](https://github.com/MATRIXNEO23/jarvis/actions/runs/41148255002), **SUCCESS** su quattro job Python 3.11/3.12 Windows e Ubuntu, HEAD del ramo `83815ce94067aac212f8b5ddf7df7881325a6fbd`. Test GUI/resa 3D/consumo effettivo **non** svolti sul Pavilion; la ZIP sperimentale rimane separata e pronto per il collaudo utente.


## 15. Revisione HUD per maggiore fedeltà al preview e nuovi colori (31 ottobre 2026)

L'utente ha confrontato una fotografia dell'interfaccia Jarvis realmente avviata sul Pavilion con un precedente preview grafico in stile cinematografico, indicando che la prima implementazione era troppo semplice. Ha confermato che desidera un layout **molto più simile al preview originale**: console verticale sulla sinistra con schede Console/Attività/Sistema, grande reattore JARVIS luminoso al centro, Terra geografica animata più dettagliata a destra e strumenti di monitoraggio nella fascia bassa.

**Indicazione vincolante sul nucleo:** deve avere il testo **JARVIS** fisso, senza scritte «ASCOLTO» dentro il cerchio. **Ciano** in riposo; **arancione pulsante** quando il microfono è realmente attivo; **verde pulsante** durante la risposta vocale, con priorità del verde se la voce SAPI parla mentre il microfono è aperto. Dopo la voce deve tornare arancione se il microfono rimane attivo, altrimenti ciano. Non cambiare le modalità microfono automaticamente: all'avvio devono rimanere standby/off.

**Nuovo ramo isolato:** `feature/hud-reference-redesign`, [PR #7 draft](https://github.com/MATRIXNEO23/jarvis/pull/7) basato sul precedente ramo `feature/animated-hud-interface`. **Non integrato in main**.

Implementazioni reali:
- `hud_reference.py`: arte vettoriale Tkinter con reattore a più fasce concentriche/archi, piccoli punti e circuiti, nucleo a sfumatura di stato; globo con coste/continenti pieni, texture luminosa campionata, punti decorativi, paralleli, meridiani, orbite e rotazione lenta. Non è una texture fotografica né una vera telemetria satellitare.
- `animated_hud.py`: nuova struttura più fedele al preview, console con 3 schede **funzionanti**, riquadri CPU/RAM/disco C/GPT con valori realmente campionati o «--» quando non disponibili (niente velocità rete, GPS o CPU inventati), risparmio CPU con redraw solo su cambi di stato, globe aggiornato ogni terzo tick.
- `jarvis.py`: conversazione visualizzata come sequenza «TU», «JARVIS», «OPERAZIONE» e «SISTEMA» con timestamp; tutte le precedenti azioni e conferme file restano attive; colorazione reale collegata a `voice.is_listening()` e `speaker.is_speaking()`.
- `voice_control.py`: `is_listening()` riferito al reale stream audio generazionale, per evitare false segnalazioni arancioni quando la modalità è selezionata ma il microfono non si apre. Non modifica la logica di ascolto o accensione.
- Test aggiornati `tests/test_animated_hud.py` e `tests/test_voice_control.py`: stati e colori, clip del globo, limiti del loop e smoke test GUI Tk Windows.

**Verifica automatica:** [CI Windows/Linux run 41150102312](https://github.com/MATRIXNEO23/jarvis/actions/runs/41150102312), **SUCCESS** su quattro job; codice del redesign allo stato successivo da ricontrollare dopo altri commit. Non equiparare i test del modello geometrico al collaudo fisico del Pavilion.

**Distribuzione:** nuova ZIP isolata [feature/hud-reference-redesign](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/hud-reference-redesign.zip) linkata anche in [Download](https://github.com/MATRIXNEO23/jarvis/tree/main/Download); [guida](https://github.com/MATRIXNEO23/jarvis/blob/feature/hud-reference-redesign/docs/HUD_REFERENCE_V2.md).

**Prossima prova fisica:** mostrare e confrontare il nuovo UI con la reference foto dell'utente. Verificare (1) ciano standby (2) arancione pulsante con flusso Vosk realmente aperto (3) verde durante la voce SAPI (4) globo e tutti i tre tab della console (5) impostazioni dietro ⚙ e pulsanti save/annulla (6) carico CPU/memoria mentre Minecraft o altri programmi pesanti sono attivi. Non fare merge fino a esito positivo e decisione separata dell'utente. Conservare vecchia cartella e `%LOCALAPPDATA%\\Jarvis`.


## 16. Continuità conversazionale e personalità JARVIS (31 ottobre 2026)

**Nuovo feedback da test utente:** nonostante il riconoscimento abbastanza corretto delle parole, Jarvis tratta una nuova frase come nuovo input autonomo invece di proseguire la conversazione; l'utente vuole inoltre che abbia una personalità sobria simile all'assistente JARVIS. L'utente non chiede soltanto più accuratezza acustica di Vosk.

**Difetti reali individuati nella logica del ramo precedente:**
- `conversation_memory.context(max_chars=360)` poteva restituire `[]` per un singolo scambio utente/GPT troppo lungo. Alla domanda successiva GPT non riceveva il riferimento, pur essendo appena stato pronunciato.
- Durante un'operazione `busy_gpt` le nuove frasi in modalità conversazione venivano scartate con il messaggio «GPT sta rispondendo», non conservate.
- Il prompt vocale era centrato sul ruolo di traduttore di comandi, poco naturale; quello scritto presentava ancora l'assistente come Lia, con diverso stile.
- Il collegamento DevKit ChatGPT ha un **limite massimo di 5000 caratteri per richiesta** e la lista descrittiva completa dei comandi riduceva lo spazio per memorie e personalità.

**Soluzione isolata:** branch `feature/dialogue-continuity-personality`, [PR #8 draft](https://github.com/MATRIXNEO23/jarvis/pull/8), basato sul redesign HUD precedente `feature/hud-reference-redesign`. **Non sostituire il Jarvis già funzionante; nessun merge automatico.**

Implementazioni:
- `conversation_memory.py`: mantiene l'ultimo scambio anche se lungo, usando troncamenti progressivi, senza eliminare l'intero turno quando supera il budget; memoria breve **sempre attiva in RAM**, senza Second Brain persistente.
- `jarvis_persona.py`: profilo testuale leggero **JARVIS**, italiano naturale, competente, discreto e lievemente ironico solo quando appropriato; risposte non ripetitive, nessuna falsa dichiarazione di azioni o capacità. Funzioni di compattazione JSON dei ricordi per mantenere i riferimenti immediati e prompt della chat scritta con lo stesso profilo.
- `conversation_router.py` e `capability_registry.py`: il modello riceve un catalogo di azioni più conciso (con esempi), istruzioni di conversazione e un contesto di memoria prioritario. La **frase corrente** è alla fine del prompt. Il passato non autorizza azioni; strumenti e conferme continuano a essere verificati localmente. Tutto il prompt rientra nei 5000 caratteri del collegamento.
- `jarvis.py`: recupero di una finestra recente più ampia per GPT, nuovo stile anche nel campo «Chiedi a GPT», e **coda di massimo 3 interventi vocali** quando GPT sta elaborando. Le frasi sono inviate una alla volta, dopo la registrazione dell'esito precedente; niente perdita silenziosa delle frasi già ricevute. La coda viene cancellata se si cambia modalità, GPT viene disattivato o il collegamento si interrompe. Mai riavviare una vecchia richiesta da memoria.
- `tests/test_jarvis_persona.py` e test preesistenti: coperti memoria lunga, chiarimenti in più turni, ruolo/personalità, prompt limitati, assenza di ri-esecuzione dalla memoria.

**CI verificata:** [run 41150861417](https://github.com/MATRIXNEO23/jarvis/actions/runs/41150861417), **SUCCESS** su Python 3.11/3.12 × Windows/Ubuntu (4 job); ultimo commit di codice testato `52134b28417656d6604383a19e5302286b87c1a4`. Documentazione su branch successiva alla CI non modifica l'eseguibile.

**Documentazione:** [docs/DIALOGO_CONTINUO.md](https://github.com/MATRIXNEO23/jarvis/blob/feature/dialogue-continuity-personality/docs/DIALOGO_CONTINUO.md). **ZIP testabile** [feature/dialogue-continuity-personality](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/dialogue-continuity-personality.zip) esposta in [Download](https://github.com/MATRIXNEO23/jarvis/tree/main/Download).

**Limiti onesti:** questa correzione non migliora direttamente il riconoscimento fonetico Vosk; la protezione eco continua a ignorare il microfono quando Jarvis sta parlando, quindi non c'è ancora vero barge-in/full-duplex. La memoria persistente continua a richiedere opt-in. I test Windows/Linux non dimostrano che GPT interpreti perfettamente ogni follow-up: serve test fisico del dialogo sul Pavilion con account collegato. Mantieni standby/OFF all'avvio e modalità manuali, vecchia versione e directory del profilo intatte.


## 17. Nuova regola di avvio e colore del reattore in base alla VOCE, non al microfono (31 ottobre 2026)

**Cambio esplicito da parte dell'utente dopo i test visivi:** la precedente regola per cui il microfono deve partire sempre SPENTO/STANDBY quando si apre Jarvis **non vale più per questa nuova versione sperimentale**. L'utente ora vuole che, quando **avvia l'app Jarvis**, il microfono sia **già attivo in ascolto continuo** e che Jarvis saluti a voce in base all'orario, con formule sobrie stile JARVIS come «Buongiorno/Buonasera, signore. Come posso esserle utile?».

**Distinguere avvio dell'app da avvio di Windows:** l'utente ha chiesto ascolto immediato **all'apertura dell'app**; non ha chiesto che Jarvis si avvii automaticamente quando Windows fa login. Non aggiungere autostart OS. La modalità preferita per questa richiesta, in continuità con il progetto, è **Conversazione continua GPT**, senza dover dire «Ehi Jarvis»; il microfono è controllabile in qualsiasi momento, con scelta manuale Standby / Push-to-talk / Continuo wake-word / Continuo GPT. **Nessun passaggio automatico a Standby mentre girano programmi pesanti.**

**Altro cambio fondamentale:** arancione non significa «microfono in ascolto». Il cerchio deve essere **CIANO anche quando il microfono è acceso ma l'utente tace**; deve **lampeggiare ARANCIONE soltanto quando rileva la voce in ingresso** e **lampeggiare VERDE durante la risposta vocale di Jarvis**; prevale sempre il verde. Terminata la voce di Jarvis e in silenzio, ritorna ciano anche se il microfono continua a essere aperto. Il testo fisso al centro è **JARVIS** e non devono comparire «ASCOLTO» o «PARLO» al centro.

**Implementazione isolata:** branch `feature/hud-speech-activity-auto-start`, [PR #9 draft](https://github.com/MATRIXNEO23/jarvis/pull/9), basata su `feature/dialogue-continuity-personality`. Non integrata automaticamente in main/stabile.

- `speech_activity.py`: RMS adattivo da campioni PCM 16-bit già letti da Vosk, con soglia antirumore e rilascio di circa 0,63s, sola indicazione grafica. **Non è un modello neurale VAD e può reagire a rumori forti**; non modifica trascrizione, azioni o permessi e non memorizza registrazioni.
- `voice_control.py`: nuovo metodo `is_user_speaking()` separato da `is_listening()`; l'indicatore è aggiornato nel thread del microfono, si azzera su cambio modalità e durante/ridopo sintesi vocale `OfflineSpeaker.is_audible()`, evitando che Jarvis illumini arancione il proprio parlato.
- `animated_hud.py` e `jarvis.py`: il colore del reattore riceve `is_user_speaking()` (non il semplice stato dello stream), mentre il punto di stato MIC indica il flusso reale. Stato esterno «microfono attivo - in attesa» senza falso «standby» quando il microfono è acceso e c'è silenzio.
- `settings.py`: `auto_listen=True` come **nuovo valore predefinito** (anche con vecchi settings privi della chiave), interruttore visibile in ⚙ per opt-out persistente dal **prossimo lancio dell'app**. Disattivare l'opzione NON modifica automaticamente il microfono della sessione corrente.
- `jarvis.py`: circa 650 ms dopo apertura finestra seleziona `GPT_CONVERSATION` e chiama la normale funzione di cambio modalità; Vosk continua a caricarsi sul thread audio. La voce SAPI è attivata come già avveniva scegliendo Conversazione GPT; saluto locale una sola volta. Nessun avvio di GPT automatico senza normale connessione/autorizzazione, e nessuna registrazione di voce.
- `startup_greeting.py`: saluto secondo l'orario di Windows, senza API: notte 00–04, mattina 05–11, pomeriggio 12–17, sera 18–23, con «signore. Come posso esserle utile?».
- Test `tests/test_speech_activity.py` più aggiornamenti `tests/test_settings.py`: microfono aperto/silenzio ciano, energia vocale arancione, voce TTS verde, reset/coda, orari, opt-out e persistenza settings.

**CI automatica verificata:** [run 41151683977](https://github.com/MATRIXNEO23/jarvis/actions/runs/41151683977), **SUCCESS** 4 job Python 3.11/3.12 Windows e Ubuntu sul commit di codice/test `e0db083b75bd663e2e8a5c4c7d068de431adbb82`. File documentazione aggiunti dopo non modificano codice/test.

**Distribuzione testabile:** [ZIP separata](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/hud-speech-activity-auto-start.zip), visibile in [Download](https://github.com/MATRIXNEO23/jarvis/tree/main/Download); [guida al test e limiti](https://github.com/MATRIXNEO23/jarvis/blob/feature/hud-speech-activity-auto-start/docs/HUD_VOICE_ACTIVITY.md).

**Test fisico ancora indispensabile:** avvio dell'app e apertura effettiva dello stream; saluto verde e nessun falso arancione; colore ciano a mic attivo e senza parole; arancione con utente che parla; verde quando Jarvis risponde; ritorno ciano con microfono ancora attivo; Standby manuale; opt-out al lancio successivo; preservazione di tutte le funzioni precedenti e CPU leggera sull'i3-2100. Non fare merge finché l'utente non approva esplicitamente dopo il test.


## 18. HUD high fidelity — replica molto più vicina al concept, con peso grafico moderatamente superiore (31 ottobre 2026)

**Ultima richiesta esplicita e approvata dell'utente:** la precedente UI, per quanto animata, era troppo semplice rispetto al preview originale fornito in immagine. L'utente vuole una somiglianza **quasi identica nella composizione e molto maggiore nella ricchezza**, accettando che la grafica sia **leggermente più pesante** sul Pavilion. Non basta mettere semplici circonferenze Tk; serve un reattore con bagliori luminosi, un mondo realistico/illuminato, cornici tecniche più elaborate, console chat più vicina alla reference e telemetria visivamente coerente. Preservare l'ascolto automatico scelto dall'utente e tutti i dati/progetti, senza integrare modifiche non approvate.

**Nuovo ramo isolato** `feature/high-fidelity-reference-hud`, [PR #10 draft](https://github.com/MATRIXNEO23/jarvis/pull/10), derivato da `feature/hud-speech-activity-auto-start`. **Nessun merge automatico nel main.** [ZIP di prova](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/high-fidelity-reference-hud.zip), ora indicata come prima opzione nella [cartella Download](https://github.com/MATRIXNEO23/jarvis/tree/main/Download).

**Modifiche implementate:**
- `hud_raster.py`: nuovo motore raster di **luci volumetriche concentriche** per i tre stati ciano, arancione e verde e texture terrestre con continenti stilizzati, ombre, atmosfera e luci. PNG generati mediante sola libreria standard Python (`math`, `zlib`, `struct`), senza Pillow, API o nuovi download. Il rendering **più pesante avviene una volta sola su thread daemon separato**; i frame PNG vengono caricati in Tk sul thread principale. Le texture hanno dimensioni quantizzate per non ricrearle per ogni pixel durante il ridimensionamento. Nel frattempo o in caso di fallimento resta la precedente grafica vettoriale.
- `hud_reference.py`: combina gli sprite raster con gli archi segmentati, le orbite, i dati e la rotazione già vettoriali. Il globo visualizza un piccolo movimento della superficie nel tempo, oltre alla rotazione di meridiani e orbite; non è mappa GPS né una fotografia reale.
- `animated_hud.py`: cornici e luci ciano più vicine al concept; indicatori CPU/RAM/disco più rifiniti e quarta tessera **RETE**. `network_telemetry.py` rileva facoltativamente il traffico reale con `netstat.exe -e`, `shell=False`, argomenti fissi, in thread di fondo. Non mostra valori di rete inventati; se non disponibili scrive «--». L'indicatore stato GPT rimane in alto e vicino al reattore.
- `jarvis.py`: console con font Segoe UI, scrollbar scura, campo più simile al mockup: pulsante microfono reale che commuta manualmente standby/GPT, freccia di invio e menu **⋯** che conserva i pulsanti Esegui locale, Chiedi a GPT e Pianifica attività. Funzioni di documenti, salvataggi, Vosk, continuità, Second Brain, impostazioni ⚙ e saluto invariate.
- Test `tests/test_hud_raster.py`, `tests/test_network_telemetry.py` più regressione completa su Windows/Linux: PNG validi/decodificabili da Tk, tre colori, terra, background worker, dimensioni, dati veri rete, controlli precedenti.
- Guida [docs/HUD_HIGH_FIDELITY.md](https://github.com/MATRIXNEO23/jarvis/blob/feature/high-fidelity-reference-hud/docs/HUD_HIGH_FIDELITY.md).

**Ultima CI finale verificata:** [run 41153785798](https://github.com/MATRIXNEO23/jarvis/actions/runs/41153785798), **SUCCESS** sui quattro job Python 3.11/3.12 Windows e Ubuntu, HEAD del ramo `902b05f05b90428cdf934ed0300f4a791faf00f1`. Anche il test Windows che carica effettivamente PNG in Tk è incluso. Restano da misurare grafica e CPU sul Pavilion reale.

**Prova reale imprescindibile:** confrontare direttamente una foto della nuova UI con la reference originale, non accettare «simile» come equivalente di «quasi identica» senza feedback. Valutare il carico CPU iniziale durante generazione raster e l'uso del microfono mentre sono aperti Minecraft/altri programmi; verificare palette, movimento della Terra, telemetria reale e integrità dei pulsanti di consenso/salvataggio. L'arte raster è **procedurale**, non i pixel originali della reference e non dà una garanzia di identità visiva. Non cancellare la vecchia installazione o `%LOCALAPPDATA%\\Jarvis`. Nessuna decisione automatica di adozione.


## 19. Sfondo dark cinematico dopo foto reale dell'HUD High Fidelity (31 ottobre 2026)

**Feedback visivo dell'utente:** è stata inviata una nuova fotografia della versione High Fidelity effettivamente avviata sul Pavilion. L'utente ha osservato che **anche lo sfondo deve essere più simile al preview** originale. La UI reale ha ancora una **griglia regolare blu** attorno al cerchio e al globo e superfici troppo blu luminose. Il preview originale ha invece uno sfondo quasi nero, tracce di circuiti ciano sottili, piccoli nodi e accenti angolari, con il colore intenso concentrato soprattutto sul reattore e sulla Terra.

**Branch isolato:** `feature/high-fidelity-cinematic-background`, [PR draft #11](https://github.com/MATRIXNEO23/jarvis/pull/11), discendente di `feature/high-fidelity-reference-hud`. Nessun merge né sostituzione della versione funzionante. ZIP di prova: https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/high-fidelity-cinematic-background.zip.

**Interventi effettuati:**
- Nuovo `hud_backdrop.py`: disegna su Canvas 24 bande di colore vicinissimo al nero (componenti RGB < 18), linee elettroniche **non regolari**, nodi luminosi ciano e microdettagli collocati soprattutto ai margini. Evita esplicitamente la precedente griglia blu a quadrati che copriva uniformemente lo sfondo.
- `hud_reference.py`: usa lo sfondo cinematico dietro al reattore e al globo, preservando sprite raster pre-renderizzati, animazioni, orbite, statuizioni audio e i fallback vettoriali.
- `animated_hud.py` e `jarvis.py`: scuriti leggermente le superfici di console, pannelli inferiori e cronologia chat per un contrasto più vicino alla reference.
- `tests/test_hud_backdrop.py`: test della palette molto scura, delle linee circuitali sparse invece della griglia, dei limiti sul numero di forme statiche, del determinismo e del controllo dimensionale.
- Documento di prova: [docs/HUD_CINEMATIC_BACKGROUND.md](https://github.com/MATRIXNEO23/jarvis/blob/feature/high-fidelity-cinematic-background/docs/HUD_CINEMATIC_BACKGROUND.md).

**Prestazioni:** il disegno del backdrop avviene solo in build/resize del Canvas, **mai nel tick di animazione**; non introduce nuove dipendenze, thread, servizi, API o costi. L'utente vuole maggiore somiglianza anche accettando un modesto aumento del carico grafico, ma non deve perdere ascolto continuo o interattività del Pavilion i3-2100.

**Comportamenti da non modificare:** ciano nel silenzio anche con mic aperto; arancione pulsante quando l'utente parla; verde pulsante quando parla JARVIS. Avvio del microfono in Conversazione continua GPT all'apertura dell'app con interruttore di opt-out, saluto iniziale basato sull'orario, Second Brain, comandi e conferme sui file invariati.

**CI conclusiva verificata:** [run 41154542225](https://github.com/MATRIXNEO23/jarvis/actions/runs/41154542225), **SUCCESS** tutti e quattro i job Python 3.11/3.12 Windows e Ubuntu sull'HEAD `389613780d6e3bd59da63cbdaa560dd04df5ecfb`. **Rimane indispensabile** il confronto fotografico reale sul Pavilion prima di considerare il risultato abbastanza fedele. Conservare vecchia installazione, modello Vosk e `%LOCALAPPDATA%\\Jarvis`. I test della geometria non garantiscono la resa visiva del monitor.


## 20. Memoria progetti, orbite, personalità e Telegram vocale (31 ottobre 2026)

**Richiesta dell'utente e decisione di implementare (non solo progettare):** ogni progetto attivo rappresentato da un **pallino colorato orbitante attorno al reattore**, nome al mouse-over e apertura al clic; segnalazioni Telegram di colore differente con messaggi ricevuti/risposti; memoria generale, memoria di ogni progetto e memoria della chat Telegram isolate; un file di continuità per progetto, recupero rapido e poco consumo RAM; JARVIS leggermente irriverente e normalmente **molto sintetico**, con dettaglio solo se richiesto; Telegram automatico a **un solo contatto autorizzato**, **risposte preferibilmente in nota vocale**, ON/OFF manuale, istruzioni dell'utente da riferire al prossimo contatto.

**Nuovo ramo di prova** `feature/project-memory-orbits-telegram`, [PR #12 DRAFT](https://github.com/MATRIXNEO23/jarvis/pull/12), discendente del ramo grafico `feature/high-fidelity-cinematic-background`. **NON unito a main; vecchie build, dati e cronologie preservati.** [ZIP](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/project-memory-orbits-telegram.zip), guida [docs/PROJECT_MEMORY_TELEGRAM.md](https://github.com/MATRIXNEO23/jarvis/blob/feature/project-memory-orbits-telegram/docs/PROJECT_MEMORY_TELEGRAM.md), link in [Download](https://github.com/MATRIXNEO23/jarvis/tree/main/Download).

**Implementazione attuale:**
- `workspace_memory.py`: nuova base dati `%LOCALAPPDATA%\\Jarvis\\jarvis_workspaces.sqlite3` con `projects`, `messages` categorizzati `general/project/telegram`, indici e ricerca FTS5 con fallback limitato (non caricare l'intero archivio in RAM). Il vecchio `second_brain.sqlite3` resta intatto. Ogni progetto usa ID UUID distinto, archivio e ricerca separati. `%LOCALAPPDATA%\\Jarvis\\projects\\<id>\\CONTINUITA.md` viene aggiornato automaticamente con ultimi scambi registrati, summary esplicitamente modificato dall'utente e backup `CONTINUITA.previous.md`. La memorizzazione **automatica delle chat** richiede l'interruttore Second Brain attivato; creazione progetti/stati dichiarati restano operazioni esplicite anche a Second Brain disattivato.
- `workspace_gui.py` + `jarvis.py`: gestore da pulsante Progetti/⚙ per nuovo/apri/archivia/riattiva, ritorno al generale e modifica del summary di continuità. Passando da un contesto all'altro la memoria breve è resettata, così non si confondono i progetti. I turni di progetto non vengono più scritti per errore nella memoria generale.
- `hud_orbits.py` e `animated_hud.py`: pallini attivi **ciano** per progetto, **viola** per messaggi Telegram ricevuti/risposti, **ambra** per istruzioni da riferire. Rotazione leggera senza nuove dipendenze, tooltips col nome e click che apre contesto o storico. Se troppi pallini, la voce «Altri progetti» apre l'elenco senza affollare il nucleo; nessun pallino perde dati di progetto.
- `jarvis_persona.py`: risposte ordinarie 1-3 frasi (circa 60 parole), ironia/sarcasmo asciutto moderati, dettagli se espressamente richiesti, niente memoria inventata.
- `telegram_security.py`, `configura_telegram.py`, `configura_telegram.bat`: account personale Telegram MTProto/Telethon, configurazione interattiva, selezione **esatta di un solo peer privato** dopo login, sessione e API hash crittografati via **DPAPI** Windows, mai credenziali nel repository o nelle preferenze in chiaro. `settings.py` registra solo ID numerico, alias e flag ON/OFF, default **OFF**.
- `telegram_bridge.py`: processo asincrono solo dopo attivazione manuale; accetta solo messaggi privati entranti dall'ID autorizzato, registro verificabile per ricezione e per invio effettivo, nessuna impersonificazione (JARVIS dichiara di essere l'assistente), prompt limitato alla memoria di quel contatto e alle istruzioni esplicitamente autorizzate dall'utente; NON permette al contatto di richiedere tool, file o informazioni di altri progetti. Invio serializzato e limiti anti-duplicati; su invio incerto, niente retry automatico.
- `telegram_voice.py`: note vocali vere OGG/Opus con SAPI locale + FFmpeg opzionale gratuito; audio in ingresso decodificato con FFmpeg e riconosciuto dal modello Vosk italiano locale (solo quando un vocale arriva). **Non** simula note vocali se FFmpeg manca. `installa_telegram.bat` installa facoltativamente Telethon, FFmpeg va installato separatamente.
- `telegram_commands.py` + UI: «Jarvis, riferisci alla mia amica che ...» e pulsante «Lascia un messaggio per il contatto». I messaggi autorizzati restano in coda fino a invio e ricevuta; in esito incerto rimangono marcati come incerti, senza ripetizioni.
- Test nuovi `tests/test_workspace_memory.py`, `tests/test_project_orbits_telegram.py`, `tests/test_telegram_commands.py`; continua CI Python Windows/Linux 3.11/3.12.

**Comportamenti fondamentali preservati:** ascolto automatico all'apertura di JARVIS (NON all'avvio di Windows) con opt-out, Vosk, saluto SAPI, nucleo CIANO nel silenzio anche a mic aperto, ARANCIONE alla voce dell'utente, VERDE durante TTS, Next Brain precedente, comandi locali, documenti con consenso e grafica high fidelity con sfondo nero cinematico.

**GATE NON SUPERATO FINCHÉ NON TESTATO REALMENTE:** la CI può verificare i moduli e la UI Tk ma non può accedere al Telegram dell'utente, al microfono/codec e al Pavilion. Prima della distribuzione reale verificare apertura e salvataggio di due progetti, FTS e file CONTINUITA dopo riavvio, nomi/azione dei pallini, performance e correttezza dello stato microfono; quindi collegare un unico contatto Telegram informato dell'automazione, abilitare risposte e provare un vocale. Non dichiarare funzionante in produzione né integrare in main senza approvazione successiva. Niente costi API aggiuntivi né invii Telegram nei test automatizzati.


**Conferma test finale del ramo sperimentale:** [GitHub Actions run 41157513574](https://github.com/MATRIXNEO23/jarvis/actions/runs/41157513574), **SUCCESS** su 4 job Linux/Windows Python 3.11/3.12, HEAD `b68f9af5fb82a40fc413f1c655398920d8bdf8b9`. Comprende test di integrazione Telegram *senza rete* con nota autorizzata consegnata fedelmente, ricevuta simulata, blocco delle duplicazioni e controllo disattivazione. **Nessun accesso o invio Telegram reale verificato**; non considerare conclusa la fase di collaudo sul Pavilion.

**Regola definitiva per i messaggi lasciati al contatto:** il testo esplicitamente dettato/scritto dall'utente viene pronunciato **letteralmente**, senza riscrittura GPT, in una nota vocale, al primo messaggio ricevuto quando Telegram è attivo. Lunghezza ammessa `MAX_NOTE=320` caratteri per evitare troncature, **una sola nota in attesa per risposta**, e marcatura `sent` solo dopo ricezione dell'ID di invio Telegram. Se l'esito è incerto si lascia `uncertain` e non si ritenta automaticamente. La conversazione ordinaria (senza note pendenti) usa la risposta GPT in contesto Telegram separato.


## 21. Fix setup Telegram: API hash non incollabile su Windows (31 ottobre 2026)

**Segnalazione concreta dell'utente, dopo avvio sul Pavilion:** lanciando `configura_telegram.bat`, dopo `API ID:` la richiesta `API hash (non viene mostrato):` non consentiva di incollare e proseguire. Causa tecnica nel codice precedente: `getpass.getpass()` sulla console Windows legge input segreto senza echo; incollare con Ctrl+V non è affidabile in alcuni host e non dà feedback visivo.

**Correzione in ramo isolato:** `fix/telegram-secret-paste-dialog`, [PR #13 DRAFT](https://github.com/MATRIXNEO23/jarvis/pull/13), derivato da `feature/project-memory-orbits-telegram`, senza toccare main né la versione testata precedente.

- `telegram_secret_dialog.py` nuovo: finestra nativa Tkinter con campo `show="*"`, **Ctrl+V**, pulsante **Incolla** che legge gli appunti solo su azione dell'utente, pulsanti **Conferma**/**Cancella**, validazione e feedback su errori. Non scrive il testo incollato nei log o a schermo.
- `configura_telegram.py`: passa da `getpass` al dialogo protetto per API hash, codice di verifica e password Telegram 2FA; controlla API hash di esattamente 32 caratteri esadecimali; Annulla non salva sessioni.
- `tests/test_telegram_secret_dialog.py`: test di validazione cross-platform più smoke test Windows Tk che incolla un valore fittizio dal clipboard mediante pulsante, verifica la mascheratura e conferma; anche Annulla.
- ZIP: https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/fix/telegram-secret-paste-dialog.zip , ora prima opzione in `main/Download/README.md`.
- **CI del codice della correzione:** [run 41160005117](https://github.com/MATRIXNEO23/jarvis/actions/runs/41160005117), **SUCCESS** su tutti e quattro i job Python 3.11/3.12 Windows e Linux, HEAD `9e4f4a956eac7944e96da6bfc725d7d01040066a`. Dopo è stato aggiunto solo un aggiornamento guida (senza toccare il codice). L'esecuzione su Pavilion e il login Telegram reale restano da verificare.

**Procedura di collaudo:** chiudere la vecchia console di configurazione, estrarre la nuova ZIP in cartella diversa, eseguire `configura_telegram.bat`, inserire API ID nella console, premere Invio; quando appare la finestra API hash, incollare con Ctrl+V o pulsante Incolla, verificare la presenza di asterischi e premere Conferma. Dopo il setup, Telegram deve restare disattivato fino alla scelta dell'utente e del singolo contatto. Non richiedere mai all'utente di condividere hash, codice o password in chat. La modifica non riguarda GPT, Vosk, grafica, archivi, colori o risposta vocale.

## 22. Collaudo reale Telegram: interfaccia corretta, FFmpeg e nota pendente (31 ottobre 2026, riprendere il 1 novembre)

**Ultimo checkpoint richiesto dall'utente prima della pausa.** Preservare integralmente i §§1–21 sopra e i branch già esistenti. NON apportare modifiche di codice automaticamente e NON dichiarare consegnato il messaggio. Repository canonica `MATRIXNEO23/jarvis`; `main` contiene documentazione e la base precedente, mentre la build sperimentale con funzioni Telegram e fix per l'API hash è nel branch **`fix/telegram-secret-paste-dialog`** (deriva da `feature/project-memory-orbits-telegram`). ZIP di prova: https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/fix/telegram-secret-paste-dialog.zip . Ultimo fix automatico CI superato come riportato al §21; NO merge in main senza decisione distinta.

### Prove sul Pavilion riferite dall'utente in questa sessione

1. Nella prima schermata fotografata **non comparivano né Telegram né il gestore Progetti**: era con ogni probabilità la versione vecchia. È stato indicato di scaricare ed estrarre la ZIP del branch di fix in una **nuova cartella**, mantenendo la vecchia installazione e i dati locali.
2. Una successiva foto **mostra effettivamente** il pannello **«Telegram — un solo contatto e risposte vocali»** nella GUI nuova: checkbox **«Risposte vocali automatiche ON / OFF»**, **«Configura Telegram (accesso sicuro)»**, **«Rileggi contatto autorizzato»**, **«Lascia un messaggio per il contatto»**. Quindi l'assenza della sezione nella prima GUI non è più il problema attuale. L'utente ha detto di avere configurato Telegram; non sono stati acquisiti né devono essere richiesti in chat API hash, codice di verifica, numero, password, sessione o identificativi privati.
3. La schermata del pannello mostra l'errore **«Telegram: manca FFmpeg (libero, per OGG/Opus). Nessun invio verrà effettuato.»**. È stata spiegata l'installazione di FFmpeg gratuito su Windows 10, PATH e comando di diagnosi `ffmpeg -version`. È stata mostrata una foto delle **Proprietà del sistema** nella scheda Protezione sistema e spiegato come aprire **Avanzate → Variabili d'ambiente → Path**. **NON c'è conferma** in chat che `ffmpeg -version` funzioni o che Jarvis, dopo riavvio, trovi FFmpeg. Non dichiarare il problema risolto.
4. L'utente ha usato **«Lascia un messaggio per il contatto»** o equivalente per un **messaggio di prova** e riferisce che Jarvis risponde che sarà inviato quando il contatto è attivo; alla chiusura della sessione **il messaggio NON risulta inviato** secondo l'utente. Il testo del messaggio non è noto e non va inventato. L'indicatore orbitante **ambra** indica una nota pendente; non dimostra che sia stata inviata. Non confondere l'orbita ciano dei progetti con il viola Telegram.

### Diagnosi tecnica verificata leggendo il codice del branch di fix

- `telegram_bridge.py`: il listener Telethon si avvia **solo con risposte Telegram ON** e connessione valida, su **un singolo contatto privato autorizzato**, e reagisce a `events.NewMessage(incoming=True)`, filtrando l'ID. Il contatto non deve essere genericamente online: deve **scrivere un NUOVO messaggio in entrata mentre il bridge è attivo**. Non esiste invio immediato della nota owner-only alla sola pressione del pulsante.
- `workspace_memory.py` memorizza le note in `telegram_outbox` con stato `pending`; `pending_for_contact` legge solo le pendenti. `telegram_bridge._handle` prende **una nota in attesa per risposta** e la pronuncia **letteralmente**, con prefisso che chiarisce che parla Jarvis, come audio OGG/Opus; segnala invio completato solo con ID di ricevuta di Telegram; errore/risultato incerto è marcato `uncertain` senza retry automatico. Una nota scritta in coda non è un messaggio già inviato.
- `jarvis.py` § Telegram GUI: il pulsante **Rileggi contatto autorizzato** ricarica da `settings.json` il contatto scelto e rimette risposte OFF; l'interruttore **Risposte vocali automatiche** è l'attivazione vera, bloccata se mancano credenziali, memoria workspace o dipendenze voce (tra cui FFmpeg). La GUI mostra stati tipo **«Telegram: ascolto attivo solo per [contatto]»**, non dedurre che sia attiva senza leggerli. Le notifiche in console dovrebbero includere ricezione e invio.

### Ripresa esatta domani: verifiche senza perdere dati

1. Chiedere/controllare nella GUI nuova **lo stato testuale Telegram** dopo **Rileggi contatto autorizzato**. Attenzione: quel pulsante disabilita l'autorisposta; per il test occorre riattivarla volontariamente.
2. Verificare FFmpeg con nuovo Prompt dei comandi `ffmpeg -version`, presenza dell'eseguibile nella cartella desiderata e PATH effettivamente ereditato da **Jarvis riavviato**; se manca, sistemare senza duplicare installazioni o toccare altre variabili non pertinenti.
3. Verificare esplicitamente checkbox **Risposte vocali automatiche ON**, contatto corretto e status **«Telegram: ascolto attivo solo per …»**; GPT connesso per risposte ordinarie, Telethon e SAPI/FFmpeg/Vosk secondo esigenze. Se c'è errore, chiedere **solo testo o screenshot dello stato**, non credenziali.
4. Per sbloccare la nota **pendente**, fare scrivere al **contatto autorizzato un nuovo messaggio privato** *dopo* che Telegram è attivo; non basta presenza online o messaggio passato. Controllare console `TELEGRAM > Ricevuto…`, `TELEGRAM > Risposta vocale inviata…`, cronologia Telegram cliccando sul pallino viola (se appare), e la nota ambra in attesa. Prima prova NON va dichiarata riuscita senza evidenza di invio.
5. Se non invia, distinguere in sequenza: contatto errato/bridge OFF; FFmpeg non trovato; nessun nuovo evento ricevuto; dipendenze audio; limite di frequenza; errore invio/receipt; stato `uncertain`. Non ripetere automaticamente note dall'esito incerto. Non usare messaggi reali a contatti non esplicitamente autorizzati.
6. **Nuova possibile funzione da valutare, non ancora autorizzata né implementata:** separare «**Invia subito al contatto**» da «**Riferisci alla prossima risposta**», con conferma esplicita, anti-duplicazione, ricevuta Telegram, audit e test; prima chiarire preferenza utente. Il feedback attuale indica che l'utente si aspettava l'invio immediato per il messaggio di prova.
7. **Miglioria UX proposta ma NON implementata:** bottone «Installa/Verifica FFmpeg» per evitare editing manuale di PATH; richiede progettazione sicura compatibile con Pavilion e costo zero, approvazione e test isolati. Non introdurre download invisibili o installazioni senza permesso.

**Criteri e vincoli invariati:** codice di branch sperimentali separato dal `main` fino ad approvazione; zero costi aggiuntivi; niente segreti in Git; proteggere `%LOCALAPPDATA%\\Jarvis`, `telegram-auth.dpapi`, `settings.json`, `jarvis_workspaces.sqlite3`, `second_brain.sqlite3`, progetti e file `CONTINUITA.md`; non cancellare vecchie ZIP, versioni, memoria, salvataggi e cronologie. Test automatici verdi non equivalgono a connessione Telegram realmente verificata. Nessun messaggio va inviato senza ON/consenso o fuori dal contatto autorizzato.

## 23. Requisito confermato: autonomia su Windows, ora/meteo e ricerca web senza browser (31 ottobre 2026)

**Nuovo desiderio espresso e confermato dall'utente:** Jarvis deve poter usare il PC quasi come una persona, aprire cartelle, trovare e aprire file, trovare e utilizzare programmi installati, dire ora e data, consultare il meteo e cercare su Internet, LEGGERE le pagine e rispondere direttamente (anche a voce) senza dover aprire visibilmente un browser. L'apertura del browser deve essere opzionale o richiesta quando una pagina non può essere letta senza interazione grafica. Vuole un vero assistente autonomo, non un semplice interprete di comandi fissi. Questo è un REQUISITO, non una capacità già realizzata né un'autorizzazione ad accedere senza limiti a file privati.

**Audit del codice letto sul ramo fix/telegram-secret-paste-dialog:**
- local_engine.py supporta solo un piccolo insieme di programmi (ad esempio Blocco note, calcolatrice, Explorer), file Download, apertura C: e ricerca tramite webbrowser.open(): la ricerca sul web oggi APRE il browser e NON legge autonomamente le pagine. Non dire che già possiede queste nuove capacità.
- capability_registry.py, jarvis_commands.json e conversation_router.py definiscono una lista chiusa di azioni consentite: serviranno nuovi adapter e aggiornamenti coerenti a catalogo, planner, UI e test. GPT non deve poter inventare comandi shell.
- Mancano comandi dedicati a interrogare il tempo locale di Windows e un servizio meteo con località e fonte; l'ora si deve poter dare offline, il meteo solo con dati realmente acquisiti online.
- Esplorazione file deve estendersi a directory SCELTE dall'utente (con ricorso a Explorer solo quando necessario), ricerche nome/data/tipo e lettura contenuti autorizzati, senza scandire tutto l'HDD continuamente. Aprire file con programma predefinito; rispettare riservatezza, esclusione di segreti, limiti I/O, backup e autorizzazioni prima di scrivere/cancellare.
- Aprire e usare programmi Windows richiede riconoscimento degli eseguibili/collegamenti approvati, adattatori per comandi di UI e esiti realmente verificati, senza elevazioni arbitrarie, shell libera o poteri nascosti.
- Ricerca silenziosa via rete: richiedere risultati e pagine pubbliche con HTTPS, timeouts, limiti dimensionali, estrazione del testo senza aprire per default il browser, sintesi tramite GPT collegato e indicazione delle fonti/URL; stato chiaro se offline, pagine bloccate o non recuperabili. Testi e pagine web sono dati non fidati e NON istruzioni eseguibili (anti prompt injection); non permettere accesso a memorie Telegram, credenziali, progetti o file privati per richiesta di una pagina.
- Autonomia incrementale con livelli configurabili Assistito / Autonomia controllata / Avanzata (proposta); operazioni irreversibili o sensibili richiedono conferme indipendentemente dal livello, cronologia verificabile e annullamento dove possibile.
- Zero costi aggiuntivi e nessuna API a consumo; carico compatibile col Pavilion i3-2100, 10 GB RAM, HDD; funzioni locali disponibili offline, meteo/web richiedono Internet; nessuna perdita di memoria, dati progetti o configurazioni Telegram.

**Ordine di lavoro proposto, non ancora implementato:** 1) ora/data locali, cartelle e file autorizzati; 2) individuazione/apertura programmi; 3) ricerca web e lettura pagine senza browser con fonti; 4) meteo con località; 5) uso GUI e sequenze multi-step con permessi, backup e test. Realizzare in ramo sperimentale isolato; test automatici e poi prova fisica sul Pavilion. Non integrare automaticamente dopo test e non cancellare vecchie ZIP, dati o branch.

**Coesistenza con checkpoint precedente:** resta APERTO il test Telegram descritto al §22 (FFmpeg non ancora confermato, nota di prova pendente). Questo requisito NON risolve né sostituisce la correzione Telegram e non autorizza invii a contatti terzi.
