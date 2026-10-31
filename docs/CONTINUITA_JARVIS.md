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

## 24. Requisito aggiuntivo confermato: gestione progetti tramite conversazione VOCALE (31 ottobre 2026)

**Richiesta utente inequivocabile:** tutta la gestione dei progetti deve potersi fare **parlando naturalmente a JARVIS**, senza necessità di cliccare il pulsante "Progetti" o passare da una finestra. Il pulsante/HUD orbite resta accesso alternativo e visivo, ma NON deve essere l'interfaccia obbligatoria. È parte dello stesso obiettivo di autonomia Windows/meteo/web del §23. L'utente sottolinea che questa funzione era già stata avviata: non ricominciare da zero o inventare un secondo sistema di progetti.

**Audit puntuale del branch sperimentale fix/telegram-secret-paste-dialog (31 ottobre):**
- workspace_memory.py implementa già create_project, project, projects, set_active, set_summary, add_turn, recent, search, prompt_context, continuity_file e snapshot CONTINUITA.md; usa SQLite per l'isolamento di contesto. La memoria generale e Telegram devono rimanere separate.
- workspace_gui.py offre i pulsanti "Nuovo progetto", "Apri", "Attiva / archivia", "Generale", "Apri CONTINUITA.md" e "Salva stato del progetto", ma NON collega direttamente tali operazioni a un comando vocale.
- jarvis.py ha switch_context(project_id), open_project_manager() e interfaccia "Progetti" e pallini orbitanti; la voce viene ricevuta, ma il parser voice/GPT conversation_router.py e il catalogo capability_registry.py + jarvis_commands.json NON elencano attualmente capacità di gestione progetti. NON sostenere che voce-progetti sia già implementata.
- Nuove capacità richieste con esempio frasi naturali: "Jarvis, crea un progetto chiamato Minecraft"; "Apri [nome progetto]"; "A che punto eravamo con [nome]?"; "Salva lo stato di questo progetto"; "Passa al progetto FILUM"; "Quali progetti sono attivi?"; "Archivia questo progetto"; "Ritorna alla conversazione generale". Il parser deve capire parafrasi, non pretendere parole esatte. Prevedere testo e voce attraverso lo stesso dispatcher validato, senza hardcoding del solo esempio.
- "Salva lo stato" deve effettuare un vero aggiornamento persistente coerente: cronologia se l'opzione Second Brain è ON; per uno stato/summary consolidato distinguere ciò che l'utente ha dichiarato, ciò che Jarvis ha verificato e ciò che è soltanto pianificato, chiedendo il minimo chiarimento necessario; non inventare progressi, non dichiarare salvato senza ricevuta locale. L'opzione Second Brain può restare sotto consenso; non abilitarla di nascosto. I file CONTINUITA.md e SQLite esistenti non vanno cancellati o migrati distruttivamente.
- Per l'apertura e la ricerca, risolvere nomi in UUID persistenti con confronto robusto, segnalare omonimie/ambiguità invece di aprire il progetto sbagliato; al cambio progetto resettare solo la memoria breve, non cancellare archivi. Impedire cambi durante una richiesta GPT o task non concluso usando i controlli già esistenti.
- Per archiviazione, distinguere operazione reversibile da eliminazione: archiviazione mantiene contenuti, dati e orbita può sparire; eliminazione non va introdotta come sinonimo. Confermare le operazioni potenzialmente distruttive. Le operazioni di lettura, elenco, riepilogo, creazione e apertura autorizzate non devono imporre menu o conferme inutili.
- Al completamento usare le orbite HUD già implementate (ciano per progetto attivo) e risposta parlata breve; se serve chiarire, Jarvis può chiedere verbalmente. Tono di JARVIS sintetico.
- Implementazione PROPOSTA e ancora da eseguire: adapter deterministico per progetti sopra WorkspaceMemory; nuove voci capability_registry.py/catalogo e traduzione nel conversation_router.py; integrazione del parser per entrate voce+testo in jarvis.py; feedback voce/TTS + test. Non affidare a GPT esecuzioni SQL, comandi shell o manipolazioni dirette di file. Test: create→save→switch→restore after app restart, omonimi, progetti archiviati, Second Brain OFF, fallimento sicuro, nessuna contaminazione fra progetti, collisione Telegram, UI orbite e prestazioni sul Pavilion.
- Nessuna implementazione di queste nuove azioni vocali è stata fatta in questo aggiornamento: il file è un checkpoint di requisiti. Non fare merge automatico in main. Zero nuovi costi/API; mantenere backward compatibility e tutti i dati.

**Ripresa complessiva:** restano aperti la prova reale Telegram (§22), l'autonomia computer/web (§23) e ora il pieno controllo vocale dei progetti (§24). Non sacrificare uno dei requisiti per implementare gli altri.

## 25. Memoria operativa dei progetti AUTONOMA — prototipo isolato (31 ottobre 2026)

**Nuovo requisito confermato con massima priorità dall'utente:** non deve mai essere necessario dire "Salva la continuità" quando si lavora su un progetto. La memoria deve evolvere DURANTE l'attività, passo dopo passo. JARVIS deve sapere quale progetto è attivo, a che punto è, quali attività sono pianificate, in corso, completate con riscontro, fallite o interrotte, quali file ha realmente prodotto e dove riprendere dopo un riavvio. Questo principio vale progressivamente per l'intero assistente, non soltanto per gli scambi testuali; vietato inventare esiti. I file dello stato e della cronologia devono nascere automaticamente nella directory del progetto, senza cancellare la memoria esistente. Non basta la continuità iniziale.

**Implementazione reale avviata in RAMO ISOLATO:** feature/automatic-project-continuity, basato su fix/telegram-secret-paste-dialog; PR draft #14 https://github.com/MATRIXNEO23/jarvis/pull/14 ; ZIP per sviluppo https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/automatic-project-continuity.zip . NESSUN merge nel main e NESSUNA prova fisica su Pavilion ancora effettuata.

**Interventi tecnici già committati nel ramo di prova:**
- workspace_memory.py: nuove tabelle persistenti SQLite project_steps, project_events, project_artifacts con ID per passo, stato planned/running/completed/failed/interrupted, ricevuta del risultato, cronologia delle transizioni e riferimenti a file la cui esistenza è stata verificata. A creazione progetto sono generati automaticamente per UUID CONTINUITA.md, STATO.json, PASSI.md, ARTIFATTI.md, EVENTI.jsonl e files/; il database resta fonte canonica. Proiezioni salvate atomically con backup del markdown precedente e riconciliazione all'avvio se sono mancanti o disallineate; un passo non concluso è marcato interrupted senza ritentare o dichiarare successo.
- jarvis.py: chat del progetto persistita automaticamente anche se Second Brain GENERALE è OFF (consenso al progetto esplicito; memorie isolate). Lo switch Second Brain conserva controllo sulla sola chat generale. Comandi locali: checkpoint prima della partenza e risultato con task_id; documenti: risultato reale e registrazione dei file solo se esistono; GPT riceve stato avanzamento e distinzione delle ricevute, non soltanto ultimi scambi. Se la registrazione iniziale fallisce, l'operazione di progetto è bloccata invece di svolgersi senza traccia.
- planner_ui.py e plan_runner.py: i passi di un piano approvato diventano planned, si aggiornano quando l'esecutore termina il singolo step con una ricevuta, e i passi non eseguiti sono interrotti. Il planner continua a richiedere consenso per le operazioni già previste, nessuna esecuzione arbitraria.
- jarvis_persona.py: in un contesto di memoria limitato dà priorità alle prove di attività invece che ai soli messaggi, senza trasformare le memorie in nuovi permessi.
- Interfaccia impostazioni: spiega la nuova memoria di progetto automatica e il Second Brain generale separato.
- tests/test_auto_project_continuity.py: creazione file, progressione, ricevute, duplicati, recupero da crash, isolamento, integrazione prompt e protezione segreti. Documentazione specifica docs/AUTO_PROJECT_CONTINUITY.md.
- PR di test Windows/Linux Python 3.11/3.12: run 41175352552 SUCCESS sul primo checkpoint codice; successivi run su perfezionamenti (es. 41175478542) da verificare prima di dichiarare pronto. Nessuna autenticazione Telegram o microfono reale esercitata dai test.

**Limiti attuali importanti:** non è ancora integrato il comando VOCALE per creare/aprire/archiviare progetti (requisito §24 ancora aperto); la memoria automatica riguarda le operazioni che passano attraverso JARVIS, NON tutti i programmi e file modificati indipendentemente dall'utente; il lavoro esterno a JARVIS non viene finto come completato. La memoria generale Second Brain resta con il suo controllo opt-in e richiede analisi separata per aggiornamento globale automatico. Risoluzione Telegram/FFmpeg e invio nota pendente (§22), autonomia web e Windows (§23) restano aperti.

**Gate per il prossimo turno:** verificare CI dell'HEAD effettivo del branch, rivedere eventuali failure e correggere in isolamento; sul Pavilion provare progetto nuovo e progetto esistente senza perdere dati, avanzamento dopo ogni passo, riavvio forzato, file/stati e carico su HDD/i3. Soltanto dopo conferma esplicita decidere merge; mantenere vecchie ZIP e memorie utente, nessuna modifica alle credenziali Telegram.

**Aggiornamento di implementazione (stesso checkpoint):** per non perdere anche *quale progetto si stava usando*, il ramo sperimentale contiene ora una tabella workspace_session con selezione del progetto corrente, aggiornata al cambio progetto o al ritorno al generale; jarvis.py ripristina il contesto alla successiva apertura. jarvis_persona.py e jarvis.py passano a GPT evidenze verificate dei passi prima della sola conversazione, con stato esplicito; gli altri casi rimangono distinti. La guida PROJECT_MEMORY_TELEGRAM.md nel ramo è stata aggiornata per spiegare che i progetti hanno memoria automatica indipendente dal Second Brain generale. Gli ultimi commit di codice del ramo sono stati sottoposti a CI Windows/Linux; verificare la run della HEAD prima di affermare successo finale. Test fisico sul Pavilion sempre da fare.

**Verifica finale automatica del ramo memoria:** [GitHub Actions run 41175634069](https://github.com/MATRIXNEO23/jarvis/actions/runs/41175634069), SUCCESS su tutti e quattro i job Python 3.11/3.12 Windows e Ubuntu, commit HEAD `9ae0c269e3acd497b0310cc0a6b483a89474eaea`. Include i nuovi test del journal, recupero contesto corrente e regressione. Questo non equivale a collaudo sul Pavilion; PR #14 resta DRAFT e isolata.

## 26. Progetti a voce e salvataggio TXT automatico nella cartella del progetto (31 ottobre 2026)

**Segnalazione utente:** nel collaudo precedente non riusciva a creare il progetto mediante la voce; desidera che Jarvis crei da solo una cartella per ogni progetto in una cartella principale esterna al codice (preferibilmente AppData Jarvis), e che, quando pronuncia «Salva» in Blocco note, salvi un file TXT nel progetto corrente scegliendo automaticamente un nome coerente con la richiesta e il lavoro in corso, senza richiedere sempre cartella/nome. Continuità sempre aggiornata in autonomia (§25); nessuna perdita di dati. Confermata la preferenza di trovare un file ZIP aggiornato **fisicamente nella cartella Download della repository** (§25 e richiesta successiva).

**Realizzazione isolata completata su** `feature/voice-project-folder-documents`, base `feature/automatic-project-continuity`; **PR draft #15** https://github.com/MATRIXNEO23/jarvis/pull/15 . HEAD testato `d20999446ccad0ff72203436b9b7ed4abebe2321`. CI 41177638619 con tutti i job Python 3.11/3.12 su Windows/Ubuntu SUCCESS: https://github.com/MATRIXNEO23/jarvis/actions/runs/41177638619 . **Non collaudato fisicamente sul Pavilion**, nessun merge a main, nessuna modifica distruttiva alla memoria o a Telegram.

- `project_voice.py` nuovo: parser deterministico, senza modello online, di richieste naturali «crea un progetto chiamato X», «crea un progetto» (Jarvis domanda il nome), «apri il progetto X», «elenca progetti», «torna alla conversazione generale», «apri la cartella del progetto». Validazione nomi, rifiuto duplicati ambigui, niente comandi arbitrari o path pronunciati da GPT. In `jarvis.py` integrate per voce GPT, push-to-talk e ascolto con wake, oltre che campo chat. La GUI progetti continua come alternativa.
- `workspace_memory.py`: confermata la struttura già presente `%LOCALAPPDATA%\Jarvis\projects\<UUID>\`; ogni progetto ha `CONTINUITA.md`, `STATO.json`, `PASSI.md`, `EVENTI.jsonl`, `ARTIFATTI.md`, `PROGETTO.txt` con nome leggibile, e `files\`. Il nome non modifica l'identificatore UUID esistente; nessuna migrazione/sostituzione delle cartelle vecchie. `project_files_directory()` controlla e usa solo la cartella propria.
- `project_documents.py` nuovo: nomi .txt suggeriti dalla richiesta originaria, fallback `appunti-<progetto>.txt`, suffissi numerici per file già esistenti, nessun overwrite/path traversal. Si salva nella cartella del progetto che possedeva il documento (non in quella di un altro progetto). Il cambio contesto con un documento ancora aperto viene bloccato.
- `managed_documents.py`: `save_only()` scrive una COPIA del testo letto dalla finestra Blocco note gestita, **senza chiudere** Notepad; modifiche dopo il primo salvataggio richiedono una nuova versione (copia precedente conservata). `save_and_close()` dopo modifiche permette nuova versione sicura, mai sovrascrittura. Limite onesto: il TXT viene scritto direttamente da Jarvis, non associato al menu Salva nativo della finestra Notepad ancora aperta.
- `jarvis.py` riconosce «salva» e «salva come NOME», usa il progetto corrente e suggerisce nome; «salva e chiudi» resta distinto. Fuori da un progetto richiede destinazione esplicita come prima. I salvataggi vengono registrati con ricevuta e riferimento al file realmente creato nella memoria operativa.
- Nuovi test `tests/test_voice_project_documents.py`, verifica parole, cartelle, isolamento, file duplicati, versioni, ripresa da riavvio e comportamento del fake editor. Test CI automatici superati (non equivalgono al test del microfono e Notepad sul Pavilion).
- Guida di sviluppo `docs/VOICE_PROJECT_DOCUMENTS.md` nel ramo.

**ZIP DISPONIBILE realmente in** `main/Download/Jarvis-Progetti-Vocali-e-Salvataggio.zip`, verificata presenza tramite API GitHub. Link diretto https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Progetti-Vocali-e-Salvataggio.zip ; elenco aggiornato https://github.com/MATRIXNEO23/jarvis/tree/main/Download . Workflow di confezionamento `.github/workflows/package-jarvis-voice-projects.yml` in main ha creato il pacchetto dall'HEAD fissato del ramo; il codice sperimentale NON è integrato in main. La ZIP precedente `Jarvis-Memoria-Automatica.zip` è rimasta intatta.

**Punto di ripresa per test reale:** chiudere Jarvis; backup completo `%LOCALAPPDATA%\Jarvis`; estrarre la ZIP in una nuova cartella; mai eseguire insieme versione vecchia e nuova; nel nuovo Jarvis attivare a piacere la modalità vocale manualmente; pronunciare «Jarvis, crea un progetto chiamato Test Colosseo», controllare l'orbita e il file `PROGETTO.txt` sotto `%LOCALAPPDATA%\Jarvis\projects\<UUID>`; creare con GPT un documento Blocco note, dire «salva», verificare `files\<nome>.txt`, poi modificare e ripetere per vedere il suffisso numerico; verificare continuità e riavvio, non aprire i due Jarvis contemporaneamente. Telegram mantiene le impostazioni precedenti, non attivare invio durante il collaudo salvo test esplicito. Ancora aperti gli altri requisiti di autonomia desktop/web/meteo (§23) e invio Telegram (§22). Non dichiarare conclusi senza prova reale.

## 27. Blocco antivirus download ZIP — collaudo sospeso (31 ottobre 2026)

**Segnalazione reale:** l'utente su Windows 10 Pavilion, tentando di scaricare `Download/Jarvis-Progetti-Vocali-e-Salvataggio.zip`, ottiene il messaggio «virus rilevato». Il nome preciso dell'antivirus, la categoria della minaccia (Trojan, PUA ecc.) e la regola che ha bloccato il pacchetto NON sono ancora stati forniti. NON dichiarare che sia un falso positivo e NON suggerire di disattivare Defender/SmartScreen, autorizzare minaccia, aggiungere esclusioni o cambiare ZIP per eludere il filtro. Sospendere il collaudo e mantenere la versione già funzionante.

**Verifica della provenienza effettuata in sola lettura su GitHub:** il workflow `.github/workflows/package-jarvis-voice-projects.yml` pubblica il pacchetto dal commit fissato e verificato `d20999446ccad0ff72203436b9b7ed4abebe2321` ed esclude `.github`, `Download`, `.git` e cache. Nel tree di tale commit ci sono 97 file distribuiti (69 .py, 19 .md, 5 .bat, 2 .mjs, 1 .ps1, 1 .json); nessun .exe o .dll nella tree sorgente. Tuttavia questo NON costituisce una scansione antivirus del file ZIP e non ne garantisce la sicurezza. L'installatore facoltativo GPT `installa_gpt.bat` contiene una chiamata PowerShell con `-ExecutionPolicy Bypass`, e `installa_gpt.ps1` scarica/builda uno SDK: sono pattern che possono meritar controllo, ma non è stato provato che siano il motivo del rilevamento. Non cambiare i comandi per aggirare antivirus senza diagnosi.

**Intervento documentale:** la pagina `main/Download/README.md` è stata marcata «SOSPESO PER VERIFICA ANTIVIRUS» con avviso a non forzare il download e a non aggiungere esclusioni. Il file ZIP originale è stato conservato, non cancellato né alterato, per analisi/riproducibilità.

**Prossimo passo prioritario:** richiedere foto da Sicurezza di Windows → Protezione da virus e minacce → Cronologia della protezione (espandere l'evento), con nome preciso della minaccia, eventuale file interno e azione. Se l'evento non c'è, chiedere screenshot della pagina Download del browser e nome prodotto antivirus. Poi eseguire analisi mirata e, se confermata segnalazione errata, seguire procedura ufficiale Microsoft di revisione dei falsi positivi; se confermato comportamento rischioso, correggere il codice, rieseguire CI + scansione e pubblicare soltanto dopo nuova valutazione. Niente credenziali/screenshot contenenti dati privati. Mantenere separati branch e memoria.

**Aggiornamento identificazione minaccia:** l'utente ha precisato il nome, pronunciato «Trojan script wakata B punto esclamativo ML». Corrisponde verosimilmente a **Trojan:Script/Wacatac.B!ml** di Microsoft Defender; la scheda ufficiale Microsoft https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?name=Trojan%3AScript%2FWacatac.B%21ml la definisce etichetta euristica ampia, talvolta falsi positivi ma non dimostra che questo ZIP sia innocuo. **Rilevamento da trattare come potenziale minaccia finché non è accertato.** Richiedere il campo **Elementi interessati** / percorso esatto della rilevazione in Sicurezza di Windows → Cronologia della protezione, evitando informazioni personali. Non chiedere di disattivare Defender, ripristinare file, consentirli o mettere esclusioni. Il source tree del commit pacchettizzato è privo di .exe/.dll, ma non è una scansione antivirus. Il collaudo resta sospeso. L'eventuale contestazione di falso positivo deve passare per Microsoft Security Intelligence https://www.microsoft.com/en-us/wdsi/filesubmission e/o una scansione ufficiale dell'artefatto.

## 28. Recupero progetto errato, cestino e autodiagnostica sicura (31 ottobre 2026)

**Segnalazione reale dell'utente:** nel test del pacchetto per progetti vocali, Jarvis ha creato un progetto con nome riconosciuto erroneamente; al tentativo di rinominarlo ha risposto che non esiste nessun progetto salvato. Il collaudo è rimasto bloccato. L'utente richiede esplicitamente gestione vocale della **rinomina** e della **eliminazione** dei progetti da Jarvis, senza intervenire a mano sui database, oltre a ricerca ed elenco affidabili. L'intero archivio locale deve restare preservato.

**Soluzione di progetto adottata:** rinomina dello stesso UUID senza alterare messaggi, file, percorso, stato, cronologia; eliminazione come **spostamento nel cestino logico** reversibile, nascosto da orbite ed elenco, previa richiesta di conferma vocale forte «confermo»; recupero dal cestino a voce/chat e con pulsante. La cancellazione fisica/permanente NON è autorizzata né implementata. Se la memoria SQLite non è leggibile, dire «archivio non disponibile», non inventare che i progetti sono scomparsi. Riconoscere espressioni naturali italiane (anche cortesi e all'infinito), elencare i nomi effettivamente salvati.

**Nuovo requisito dell'utente, distinto:** Jarvis deve conoscere la collocazione dei file del proprio programma e poterli leggere/analizzare per comprendere cosa esiste, trovare potenziali problemi e proporre correzioni da comunicare all'assistente di questa chat. **Autonomia di scrittura sul proprio codice: eventualmente possibile in futuro solo con esplicita richiesta**, ma **per ora l'utente preferisce che le correzioni siano fatte da ChatGPT**, non da Jarvis autonomamente. Quindi nessun automodifica, autoupdate, auto-patch, auto-merge o esecuzione di codice senza revisione; usare solo diagnostica offline di lettura, test isolati, backup e possibile rollback. Futuri permessi di automodifica richiedono una decisione esplicita successiva.

**Implementazione sperimentale avviata in branch isolato:** fix/project-rename-and-discovery, base feature/voice-project-folder-documents; [PR draft #16](https://github.com/MATRIXNEO23/jarvis/pull/16). Interventi verificabili nel ramo:
- workspace_memory.py: migrazione additiva SQLite colonna trashed, senza eliminare tabelle o contenuti; rename_project, trash_project, restore_project, trashed_projects, lista ordinaria esclude il cestino. Cartelle identificate con UUID invariabile; titoli CONTINUITA.md, STATO.json, PROGETTO.txt aggiornati sul rename. Nessun delete fisico.
- project_voice.py: gestione esplicita italiano per rinomina, elenco progetti salvati, elimina previa conferma, mostra cestino, recupera progetto; gestisce varianti cortesi.
- jarvis.py: integra il dispatcher voce/testo e i prompt di conferma; individua il progetto corrente o esattamente nominato, non sceglie fra omonimie, conserva contesto al rename, resetta solo se quello corrente viene cestinato. workspace_gui.py: pulsanti rinomina, cestino, ripristino.
- self_diagnostics.py: controllo AST read-only e offline dei soli sorgenti del programma, elenco moduli, funzioni e classi principali, sintassi e posizioni file; comando «analizza il tuo codice» / «dove sono i tuoi file» / «analizza nome_modulo.py». Nessun import/exec, lettura credenziali o invio sorgenti a GPT. Questa è una **prima analisi statica**, non una revisione semantica completa né un test eseguito.
- tests/test_project_maintenance.py verifica invarianti di memoria su rinomina/cestino/ripristino/restart e protezione diagnostica. docs/PROJECT_MAINTENANCE_AND_SELF_AUDIT.md descrive comandi e limiti.

**Gate e sicurezza:** correggere ogni regressione CI Windows/Ubuntu prima di dichiarare pronta la patch; test sul Pavilion con progetti reali solo dopo backup completo della cartella %LOCALAPPDATA%\Jarvis. Rimane attivo il blocco antivirus: lo ZIP precedentemente pubblicato è stato identificato da Microsoft Defender come possibile Trojan:Script/Wacatac.B!ml (§27). Non proporre di consentire, escludere o disattivare Defender; **non pubblicare una nuova ZIP destinata all'utente fino a diagnosi/risoluzione del rilevamento**. PR resta draft, nessun merge a main.

**Verifica CI completata:** https://github.com/MATRIXNEO23/jarvis/actions/runs/41179416762 ha esito SUCCESS in tutti i quattro job Windows/Ubuntu con Python 3.11 e 3.12 sul commit `468ff31f0253bb7de7929076febaa71e6329dc68` del ramo `fix/project-rename-and-discovery`. Include i test della rinomina, del cestino, del ripristino, della diagnostica AST, l'assenza di esecuzione del codice letto e i test regressione del progetto. Il fallimento precedente su Windows era un file SQLite lasciato aperto **nel test**, non nei dati utente; corretto con chiusura esplicita della connessione. La PR draft #16 resta isolata, nessuna nuova ZIP per il problema antivirus non ancora accertato, nessun collaudo reale sul Pavilion.

## 29. Contesto conversazionale: risposte brevi e progetto selezionato (31 ottobre 2026)

**Richiesta dell'utente:** migliorare UNA cosa alla volta: collegare le risposte brevi alla domanda precedente, capire i riferimenti al progetto in corso e porre un solo chiarimento concreto. Non espandere la modifica alle altre funzioni o all'automodifica (resta in sola lettura).

**Ramo sperimentale:** feature/contextual-followups-and-project-references; PR draft #17 https://github.com/MATRIXNEO23/jarvis/pull/17 ; HEAD pacchettizzato e verificato eaae39fbb21fa75294221a1363300cda250c34da; base fix/project-rename-and-discovery. CI 4/4 Windows/Ubuntu Python 3.11 e 3.12 SUCCESS: https://github.com/MATRIXNEO23/jarvis/actions/runs/41181339526 . Non testato con voce e GPT reali sul Pavilion.

- dialogue_focus.py nuovo: brevi risposte, domanda effettivamente pendente, progetto corrente dal reale scope, niente azioni dedotte da un sì/no. Se manca selezione ma utente dice questo progetto, Jarvis domanda quale progetto salvato aprire; il nome risposta è verificato contro il DB e la richiesta originale è ripresa solo in chat, senza strumenti eseguibili.
- conversation_memory.py: ultima domanda valida (clarify o chat con una sola domanda alla fine); un turno non domanda o un cambio di progetto interrompe il riferimento.
- jarvis_persona.py/conversation_router.py: contesto JSON compatto prioritario per progetto e domanda pendente, memoria non attendibile e non autorizzativa; schema clarify limitato a una sola domanda; preservato limite bridge 5000 caratteri.
- jarvis.py: aggancio comandi vocali, chat e pulsante Ask GPT; un sì/no/quello isolato senza domanda riceve una domanda concreta; non permette tool GPT nati da risposta breve ambigua; le richieste di nome progetto mantengono il chiarimento se utente risponde sì/no generico, non creano falso progetto.
- project_voice.py: riferimenti rinomina/elimina questo progetto al focus corrente, mantenute le conferme precedenti e UUID invariati.
- tests/test_dialogue_focus.py: test mirati focus, chiarimenti, prompt e sicurezza. docs/CONTESTO_DIALOGO_V1.md: guida di prova.

**ZIP disponibile su GitHub:** Download/Jarvis-Contesto-e-Risposte-Brevi.zip; 262463 byte, verificata presenza nella repository, URL https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Contesto-e-Risposte-Brevi.zip ; confezionata dal workflow SUCCESS https://github.com/MATRIXNEO23/jarvis/actions/runs/41181418788 . README Download aggiornato. Le ZIP precedenti sono conservate; nessun merge della PR in main.

**AVVISO antivirus irrisolto:** ZIP precedente bloccato da Defender come Trojan:Script/Wacatac.B!ml. Mancano analisi indipendenti del nuovo ZIP; test CI non garantiscono assenza di malware. Non proporre eccezioni, disattivazione antivirus o forzare esecuzione. Sul Pavilion fare backup completo di %LOCALAPPDATA%\Jarvis, usare una sola istanza, non perdere database/progetti/Telegram. Se Defender blocca, sospendere test.

**Collaudo prossimo:** 1. Crea progetto e prova sì alla domanda sul nome (deve chiedere un nome reale). 2. Fornisci nome, verifica che non abbia creato progetto sì. 3. A progetto aperto, chiedi a che punto siamo con questo progetto. 4. In Generale ripeti, verificare una domanda concreta sul nome e il recupero della richiesta. 5. Risposta breve a domanda GPT recente. 6. Sì isolato non provoca operazioni. 7. Riavvio e conferma continuità.

## 30. Affidabilità memoria: preferenze isolate e prove operative distinte (31 ottobre 2026)

**Richiesta utente:** rinviare il collaudo contestuale sul Pavilion fino alla prova della build; migliorare una cosa alla volta, ora la memoria: separare preferenze, informazioni dei progetti e cronologia delle operazioni, non trattare ricordi come nuovi comandi, distinguere attività richieste o riferite da quelle effettivamente eseguite e verificate. Nessuna automodifica di Jarvis autorizzata.

**Ramo sperimentale:** feature/memory-provenance-and-separation, base feature/contextual-followups-and-project-references, PR draft #18 https://github.com/MATRIXNEO23/jarvis/pull/18 . Commit canonico testato e usato nel pacchetto: 15658a1ad140c60247502052d634173f3ad184c5. GitHub Actions https://github.com/MATRIXNEO23/jarvis/actions/runs/41182354475 SUCCESS 4/4 (Python 3.11 e 3.12, Windows e Ubuntu). Il codice NON è integrato nel branch main. Il collaudo con voce reale e GPT sul Pavilion resta DA FARE, non dichiararlo completato.

**Archivi separati in AppData:**
- jarvis_preferences.sqlite3: nuovo PreferenceStore, tabella dei valori tipizzati (response_length, interaction, language), mai estratti da dialoghi; scrittura/rimozione solo con user_confirmed=True. Il comando esplicito «Jarvis, ricorda che preferisco risposte brevi» apre una conferma vocale/testuale «confermo»/«annulla», «mostra preferenze» e «dimentica preferenza risposte» disponibili; nulla viene scritto da un GPT o da una semplice citazione. La scelta interaction=voice NON attiva microfono; priorità alle modalità manuali (§16).
- jarvis_workspaces.sqlite3 e projects/<UUID>/: memoria dei progetti, documenti e passi invariati per UUID. Migrazione ADDITIVA project_steps.verified INTEGER DEFAULT 0; le azioni completed esistenti con receipt vengono considerate reported/unverified finché non provate. Snapshot schema_version 2 ricostruiti, CONTINUITA.md, STATO.json, PASSI.md separano verifica e risultato. Nessuna cancellazione delle versioni preesistenti.
- second_brain.sqlite3: conversazioni e ricevute preesistenti conservate. Migrazione ADDITIVA action_receipts.proof_kind DEFAULT legacy_unassessed; le ricevute legacy vengono mostrate come reported_action, non verified_action. Solo record nuovi con prova osservata e identificativo attendibile contano come verified e contribuiscono ai contatori. La memoria conversazionale è DATO, mai autorizzazione o comando. Cancellare Second Brain NON cancella automaticamente preferenze archiviate separatamente.
- jarvis_actions.sqlite3: nuovo OperationJournal indipendente. Ciclo requested→running→reported/verified/failed/interrupted/uncertain; registro avviato prima dei comandi locali e delle operazioni Notepad. Al riavvio i pending/running sono marcati interrupted, nessuna ripetizione automatica. Un TaskResult completed per browser/notepad lanciato è soltanto reported: non garantisce che una finestra sia attiva. Le letture locali verificabili (RAM/Download/cronologia) e i TXT che esistono realmente su disco sono classificati verified, con ricevuta; per il TXT verificata esistenza, NON prova semantica del contenuto. Il vecchio LocalEngine.tasks.db è conservato.

**File:** memory_boundaries.py (PreferenceStore, OperationJournal, classificatori osservazione), preference_voice.py (grammatica controllata), jarvis.py (integrazione dialogo e journaling senza ripetere ricordi), second_brain.py (proof_kind e migration), workspace_memory.py (verified, proiezioni v2), jarvis_persona.py (preferenze vs reported_action vs verified_action), tests/test_memory_boundaries.py e test auto continuity aggiornato; docs/MEMORIA_AFFIDABILE_V1.md.

**Pubblicazione:** nuova ZIP in main/Download/Jarvis-Memoria-Affidabile.zip, verificata presenza via API, 282608 byte, URL https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Memoria-Affidabile.zip . Workflow pubblicazione GitHub Actions SUCCESS: https://github.com/MATRIXNEO23/jarvis/actions/runs/41182455597 . All'interno SOURCE-COMMIT.txt e SOURCE-MANIFEST.json con SHA-256 dei sorgenti. README Download aggiornato con nuova versione e avvertenza. ZIP precedenti e dati utenti conservati.

**AVVERTENZA:** causa del precedente rilevamento Defender Trojan:Script/Wacatac.B!ml NON risolta (§27); il nuovo pacchetto non è stato sottoposto a una scansione antivirus indipendente. Non dichiarare il file sicuro per il solo fatto di avere CI verde, e non consigliare di disattivare protezioni o forzare file bloccati. Prima di avviare qualsiasi ZIP effettuare backup completo di %LOCALAPPDATA%\Jarvis, non eseguire due Jarvis insieme.

**Prossimo collaudo (non ora):** con il PC reale verificare conferma preferenza, lettura dopo riavvio, isolamento progetto, percorso JSON memoria, differenza fra 'avvio browser riferito' e 'file TXT esistente verificato', step legacy demoted senza perdite, e nessun vecchio comando ripetuto. Non avanzare ad altri moduli se questo fallisce.
