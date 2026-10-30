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
