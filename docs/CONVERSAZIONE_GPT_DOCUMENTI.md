# Jarvis: conversazione GPT continua e gestione vocale dei documenti

**Stato:** progettazione vincolante, prima implementazione incrementale. La versione installata sul Pavilion **non** include ancora questa modalità. Non dichiararla funzionante finché l'integrazione GUI/GPT/Windows e i test hardware non sono completati.

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
