# Jarvis: conversazione GPT continua e gestione vocale dei documenti

**Stato attuale:** prima implementazione end-to-end nel ramo sperimentale, destinata a Blocco note classico Windows 10 e a nuovi documenti di testo. **Non collaudata sul Pavilion: non confondere i test CI con il funzionamento su Windows reale.** Le versioni già funzionanti rimangono separate.

## Obiettivo espresso dall'utente

Quando l'utente seleziona volontariamente **Conversazione continua con GPT**, può parlare normalmente senza ripetere «Ehi Jarvis». Jarvis deve distinguere:
- **conversazione**: risponde con sintesi vocale, senza azioni Windows;
- **comando operativo**: interpreta la richiesta, costruisce azione consentita, esegue in modo controllato;
- **scrittura e modifica documenti**: apre/crea il documento richiesto, inventa o trascrive testo secondo la richiesta, lo inserisce automaticamente **senza attivazione manuale della dettatura**;
- **chiusura documento**: chiede esplicitamente se «salvare e chiudere», «chiudere senza salvare» o «annullare». La risposta può essere vocale e deve riguardare **solo quel documento e quella richiesta pendente**.

Esempio desiderato:
- Utente: «Apri Blocco note e scrivi un testo su Venezia; poi chiudi».
- Jarvis: genera il testo via GPT, lo mostra/scrive nel documento identificato.
- Jarvis: «Vuoi salvare e chiudere, chiudere senza salvare o annullare?»
- Utente: «Salva e chiudi».
- Jarvis: se il documento è nuovo e il nome/percorso mancano, chiede dove salvare prima di effettuare modifiche permanenti; altrimenti salva e chiude **solo il documento gestito**.
- «Annulla» torna al documento senza scartare le modifiche.
- «Chiudi senza salvare» richiede conferma esplicita e contestuale per la perdita di modifiche, non è deducibile automaticamente da GPT.

## Architettura di fiducia

`Vosk offline` (trascrizione) → `modalità microfono scelta dall'utente` → `router intenzioni` → `GPT` (solo quando abilitato e connesso) → `JSON validato` → `esecutore locale controllato` → `Windows editor/file controller` → `SAPI offline` (risposta vocale).

**L'LLM decide soltanto quale azione proporre e il contenuto**; non riceve accesso diretto a PowerShell, percorso arbitrario, chiusura processi o file system. Le risposte di GPT non devono essere interpretate come comandi di sistema o privilegi.

- Modalità audio distinti: **Standby** (sempre all'avvio), **Premi per parlare**, **Ascolto continuo con Ehi Jarvis** e **Conversazione continua con GPT**. Nessun cambio automatico, anche durante Minecraft, guasti, carico CPU o scadenza del turno conversazionale. Un timer di turno/attesa di risposta **non spegne il microfono**.
- In modalità GPT conversazionale le frasi pronunciate possono essere inviate al servizio GPT dopo trascrizione: informare chiaramente l'utente in UI; l'audio resta locale e non è caricato come file.
- In modalità normale «Ehi Jarvis» resta necessario. In modalità dettatura manuale esistente, parlato libero scrive nel campo selezionato e i comandi di controllo necessitano la wake word. La nuova modalità **non** sovrascrive queste regole.
- Se GPT è indisponibile, informare e mantenere le azioni locali offline esplicite; niente fallback ad API a consumo.
- Eventi di ritorno vocali non devono rientrare come nuovi comandi (prevenzione eco).
- Richieste ambigue relative a «quel file», applicazione/finestra o destinazione: chiedere quale, non indovinare.
- Non memorizzare trascrizioni o contenuti del file nella cronologia SQLite senza consenso separato.

## Gestione documenti: strategia a livelli

**Livello 1 (file testuali, Blocco note):** supporto a nuovi documenti e file UTF-8 esplicitamente selezionati. Il salvataggio deve essere atomico e i file esistenti necessitano backup e controllo modifica concorrente. La scelta «salva e chiudi» non è autorizzazione a sovrascrivere un percorso qualsiasi deciso dal modello.

**Livello 2 (formati di progetto):** `.md`, `.json`, `.txt`, `.py`, `.js`, `.yml` ecc. Validazione sintattica dove disponibile, preview diff, backup, conferma specifica e rollback. Supporto a repository GitHub separato dai file locali; nessun push o commit automatico.

**Livello 3 (editor/app terze):** gestire finestre esistenti tramite identificatori stabili, verifica owner PID/handle e stato modificato. Non eseguire `taskkill` sul nome `notepad.exe`; potrebbe chiudere altri documenti e perdere dati. Se l'app esterna gestisce autonomamente lo stato «non salvato» e non lo espone in modo attendibile, lasciare la finestra aperta o deferire al dialogo di conferma originale Windows, senza falsi «salvato».

## Stato del dialogo documentale (senza automatismi distruttivi)

- `idle`: nessun documento attivo.
- `editing`: contenuto in corso/proposto, eventuali modifiche non salvate.
- `awaiting_close_choice`: l'utente ha richiesto di chiudere, non salvare/chiudere ancora.
- `awaiting_save_destination`: scelta «salva e chiudi» per nuovo documento senza destinazione.
- `awaiting_discard_confirmation`: l'utente ha chiesto esplicitamente di scartare modifiche; ribadire nome documento e irreversibilità prima dell'azione.
- `closed`: risorsa chiusa e stato azzerato senza toccare altri documenti.

Interpretare «salva», «non salvare» o «annulla» **solo quando il dialogo corrispondente è attivo**; domande generiche non devono triggerare operazioni. Una richiesta in sospeso si invalida quando cambia documento o finestra, si disconnette GPT o si chiude Jarvis; non deve risvegliarsi dopo riavvio o riconnessione.

## Piano di implementazione e acceptance

1. Isolare kernel deterministico dei dialoghi file e testarne transizioni/consensi.
2. Introdurre un router GPT con schema rigoroso: `answer`, `local_action`, `compose_document`, `edit_document`, `close_document`, `clarify`; nessuna esecuzione su testo libero.
3. Implementare editor dei file testuali con preview e salvataggio sicuro; richiedere nome/percorso quando ignoti. Il backend deve distinguere le bozze non salvate dai file già presenti.
4. Integrare nella GUI un'**opzione esplicita** Conversazione GPT (l'utente è il solo a cambiare modalità), trascrizione Vosk, TTS in uscita, interruzione/revoca e limiti di carico su i3-2100/10 GB RAM.
5. Integrazione specifica con Blocco note per apertura, inserimento e chiusura di **solo** quella finestra; niente `taskkill`, niente interazione automatica con finestre terze non selezionate.
6. Test automatici Windows/Linux, compatibilità Python 3.12, mock GPT e controlli negativi; prova reale sul Pavilion con file vergini e documenti con modifiche non salvate.
7. Collaudare senza modificare la build funzionante. Merge/adottare soltanto con decisione separata dell'utente.

**Prove obbligatorie**: chiacchiera libera → solo voce; «scrivimi un testo» → documento, mai necessario attivare dettatura; «chiudi» → domanda vocale; «annulla» → finestra e modifiche restano; «salva e chiudi» → contenuto salvo e una sola finestra chiusa; «chiudi senza salvare» → conferma esplicita, niente perdite accidentali; altri Blocco note aperti intatti; errori GPT/Windows non portano a chiusure accidentali; dopo riavvio niente azioni pendenti; test di performance col vecchio HDD; costo aggiuntivo zero.

**Vincoli non negoziabili:** nessuna nuova API a consumo, microfono OFF all'avvio, ChatGPT soltanto con SDK già configurato e entro limiti dell'account, Vosk/SAPI offline, salvaguardia versioni/backup e della cartella utente `%LOCALAPPDATA%\\Jarvis`.

## Stato implementazione al 30/10/2026 — primo stadio verificabile

Nella PR draft sono stati aggiunti:
- `conversation_router.py`: costruzione del prompt per distinguere conversazione, azione locale, composizione testo e richiesta di chiusura; verifica JSON strettamente, riutilizza `action_planner.parse_plan` per impedire strumenti o argomenti fuori whitelist; nessuna esecuzione di codice generato.
- `voice_control.py`: modalità esplicita `GPT_CONVERSATION` **selezionata manualmente** con microfono off all'avvio e senza «Ehi Jarvis». Lo stato del microfono non viene mutato dal classificatore.
- `jarvis.py`: selezione della modalità GPT, invio delle frasi trascritte al collegamento ChatGPT già presente e risposta tramite sintesi vocale Windows; comandi semplici possono restare offline. Le risposte GPT vecchie vengono invalidate dopo cambio modalità o disconnessione.
- `document_dialog.py`: kernel senza effetti collaterali per le scelte di chiusura, con conferme contro perdita dati.
- Test `tests/test_conversation_router.py`, `tests/test_document_dialog.py` e test della modalità voce.

**NON IMPLEMENTATO/DA NON DICHIARARE OPERATIVO:** scrittura automatica dentro Blocco note o in un file esistente, scelta automatica della destinazione, backup e salvataggio su disco, chiusura della finestra selezionata, risposte vocali effettive al dialogo di salvataggio. In questa fase, una richiesta di testo viene generata e mostrata come **bozza non inserita**, e una richiesta di chiusura viene rifiutata senza toccare alcuna finestra. Non pubblicare come prodotto finito o sostituire la versione precedente con questa PR.

**Test fisici da effettuare prima di dire che funziona:** Windows 10 su Pavilion, riconoscimento di normali domande, risposta parlata, blocco eco e prestazioni durante programmi pesanti; solo in seguito implementare e collaudare documenti e salvataggio.


## Implementazione attuale — prototipo Blocco note, ottobre 2026

I passaggi pratici sono implementati nel ramo `feature/gpt-conversazione-documenti`:

1. Seleziona **Conversazione continua GPT**. L'avvio del programma lascia comunque il microfono sempre in **Standby**. Le frasi di questa modalità vengono trascritte offline da Vosk e inviate come testo al collegamento ChatGPT già configurato.
2. Pronuncia **«Apri Blocco note e scrivi una poesia su Venezia, poi chiudilo»**. Il router GPT valida l'intenzione e fornisce il testo. Jarvis apre un **nuovo processo di Blocco note classico**, verifica PID, classe/handle e titolo, poi scrive il testo nel controllo Edit e ne rilegge il contenuto per verificare l'inserimento.
3. Puoi dire **«Aggiungi nel documento un altro paragrafo»**: il testo nuovo viene **aggiunto**, senza sostituire il contenuto e senza attivare la dettatura manuale.
4. Se hai richiesto «poi chiudilo» o dici **«Chiudi Blocco note»**, Jarvis domanda **«salva e chiudi», «chiudi senza salvare» o «annulla»**. La richiesta pendente viene gestita **localmente**, senza chiedere a GPT di decidere al tuo posto.
5. Con **«salva e chiudi»** su un documento nuovo, chiede la destinazione. Esempio: **«sul desktop come poesia di Venezia»**, **«in documenti chiamalo il mio racconto»**, oppure usa il pulsante **Scegli dove salvare**. Salva un nuovo **.txt UTF-8** solo se il nome non esiste ancora; non sovrascrive mai file dell'utente.
6. Con **«chiudi senza salvare»** domanda una seconda conferma specifica **«confermo uscita senza salvare»** prima di chiudere la sola finestra posseduta da Jarvis. Puoi sempre dire **«annulla»**. Sono previsti anche i pulsanti di salvataggio, annullamento e conferma come alternativa alla voce.
7. Se il file viene salvato ma la finestra non si chiude, Jarvis lo riferisce separatamente e lascia aperta la finestra. Se il titolo del documento, PID, HWND o controllo Edit non coincidono più, blocca le azioni.

**Limiti reali e non ancora completati:** per questa prima prova gestisce **solo documenti nuovi** aperti da Jarvis tramite Blocco note classico Windows 10; non si appropria di Blocco note aperti manualmente, non modifica automaticamente file .md/.json esistenti in repository, non sovrascrive file e non controlla versioni moderne di Blocco note con struttura differente. Alcuni Windows 10 potrebbero aver ricevuto un'app Blocco note più recente: in quel caso Jarvis avvisa e non interviene. La compatibilità reale con il Pavilion e l'eventuale popup nativo di salvataggio devono essere verificati con file di prova e nessun dato importante.

**Non viene usata nessuna API a consumo:** Vosk per riconoscimento offline, Windows SAPI per risposta offline e il DevKit ChatGPT già presente per la comprensione del linguaggio; l'account resta soggetto ai normali limiti del servizio ChatGPT.

### Prova hardware prima dell'adozione

Usare una cartella nuova per la ZIP sperimentale e conservare la versione già funzionante. Avvio sempre in Standby. Poi: conversazione normale e risposta parlata, «apri Blocco note», composizione e verifica visiva del testo, aggiunta dopo modifica manuale, chiudi+annulla, salva con nome sul Desktop, verifica file vero sul disco, chiudi senza salvare con doppia conferma, altri Blocco note invariati, riavvio senza azioni pendenti. Non usare documenti importanti.

**Nessuna integrazione automatica in main** prima della prova reale, e nessuna cancellazione di `%LOCALAPPDATA%\\Jarvis`.
