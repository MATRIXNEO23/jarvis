# AUDIT-049 — Audit tecnico e strutturale di Lumi 049

**Data:** 15 novembre 2026  
**Oggetto:** `Lumi-049-PROVA.zip`  
**Sorgenti della build:** commit `bf7518b4569b38f05fe4cbb27dc057413679ce30`  
**Pubblicazione ZIP in main:** commit `a3828d59c4c485695f6690b4652ff36c46a3d85d`  
**Workflow di riferimento:** [43755471110](https://github.com/MATRIXNEO23/jarvis/actions/runs/43755471110) — **success**  
**Metodo:** lettura dei sorgenti e dei test CI; nessuna esecuzione sul Pavilion e nessuna modifica ai componenti del programma.  
**Nota:** tutte le osservazioni qui sotto sono riferite a **questa specifica build 049**, non a modifiche successive del ramo di sviluppo. Un risultato CI verde non prova ogni caso d'uso reale.

## Sintesi

**Giudizio:** la direzione architetturale di Lumi è valida, con moduli separati per conversazioni, modelli, strumenti e permessi. La versione 049 introduce miglioramenti concreti su memoria, allegati, servizi online, interfaccia e automazione. Prima di affidarle lavori autonomi importanti sul PC, occorre rafforzare l'isolamento dell'esecuzione, la protezione dei file, la veridicità e separazione dei ricordi, e la verifica del risultato finale delle azioni.

Non è consigliata una riscrittura totale: **interventi mirati, uno per volta, con test e rollback**.

## Pregi

1. **Architettura modulare.** Comandi diretti, interpretazione AI, gestione file, Telegram, voce, memoria e modelli hanno moduli distinti; l'impostazione riduce il rischio di consentire a un modello accesso indiscriminato al sistema.
2. **Ricordi a due livelli.** La tabella `ricordi` in SQLite conserva `breve` e `completo`: pochi dettagli per Gemma sul PC limitato, più contesto per il modello online. La UI dispone di ricerca, categorie, visualizzazione e cancellazione del singolo ricordo.
3. **Richiamo immediato dalla chat.** `richiamo.py` può rispondere a «cosa ti ho detto tre messaggi fa?» recuperando il testo della chat aperta, senza invocare un LLM.
4. **Orchestratore con autorizzazioni.** `orchestratore.py` distingue cartelle autorizzate e richieste esterne, con conferma per esecuzione Python e comandi Lumi; è un buon punto di partenza, benché le barriere non siano sufficienti in ogni caso.
5. **Servizi online multipli.** `servizi_online/` include configurazioni separate, scelta dell'ordine dei provider, gestione di indisponibilità e quote indicative, e protezione locale delle chiavi mediante DPAPI.
6. **Verifiche Windows positive.** Il workflow [43755471110](https://github.com/MATRIXNEO23/jarvis/actions/runs/43755471110) mostra esiti `success` per bundle KoboldCpp, audit PE, caricamento DLL, initializer, prove GGUF, voce, WebView2, UI Automation e candidato ZIP. La validità sul Pavilion va comunque misurata.

## Difetti e suggerimenti — ordinati per priorità

### A. CRITICO — Python eseguito senza isolamento sufficiente

**Evidenza:** `orchestratore.py`, funzioni `Strumenti.python` e `codice_pericoloso`. Il controllo contro codice pericoloso è basato su regex; la modalità Python `-I` isola l'ambiente Python da alcune sorgenti di configurazione, **non** i permessi Windows né l'accesso a file e rete. La UI invia un'anteprima di al massimo 3.000 caratteri benché lo script possa averne fino a 20.000.

**Perché è un difetto:** un frammento apparentemente innocuo può causare operazioni non previste; il consenso non è sufficientemente informato se la visualizzazione è parziale.

**Correzione:** eseguire in un processo con privilegi limitati e accessi perimetrati, mostrare integralmente il codice oppure una verifica completa navigabile prima del consenso, bloccare le scritture non autorizzate e prevedere test negativi.

**Beneficio:** limita l'impatto di errori o istruzioni maliziose dell'AI.

### B. CRITICO — Sovrascrittura dei file nelle cartelle sicure

**Evidenza:** `orchestratore.py`, `Strumenti.scrivi`. La conferma prima di sovrascrivere è richiesta soltanto se `target.exists()` **e** il percorso non è considerato sicuro. Per un file già esistente dentro una cartella sicura il metodo `write_text` sovrascrive senza conferma aggiuntiva.

**Perché è un difetto:** l'utente può perdere un file importante se un modello sceglie il nome sbagliato.

**Correzione:** separare «crea nuovo» da «sostituisci»; richiedere approvazione esplicita per ogni sovrascrittura, realizzare una copia recuperabile e usare salvataggio atomico.

**Beneficio:** evita perdite accidentali.

### C. ALTA — Cancellazione completa Second Brain incompleta

**Evidenza:** `second_brain.py`, `SecondBrain.clear_all`: cancella `conversations`, `action_receipts` e `speech_corrections`, ma non la nuova tabella `ricordi` (né il relativo indice FTS5).

**Perché è un difetto:** una funzione chiamata «clear_all» non elimina tutte le memorie permanenti.

**Correzione:** definire esplicitamente il significato di «cancella tutto», aggiornare tutte le tabelle interessate in transazione, testare cancellazione e riavvio su un database **di prova**. Non cancellare dati reali durante il fix.

**Beneficio:** comportamento prevedibile e controllo dei propri dati.

### D. ALTA — Ricordi di progetti non filtrati per ambito

**Evidenza:** `second_brain.py`, `salva_ricordo` conserva `project_id`; `ricordi(query, ...) ` non espone né applica un filtro `project_id`. Anche `ricordi.per_online` recupera senza indicare l'ambito.

**Perché è un difetto:** informazioni di progetti differenti possono essere mescolate nelle risposte.

**Correzione:** progettare visibilità generale/di progetto, filtro esplicito, test cross-project e regole di condivisione controllata.

**Beneficio:** memoria più coerente e separazione più sicura.

### E. ALTA — Ricordi proposti dall'AI trattati come fatti

**Evidenza:** `ricordi.py` istruisce i modelli online a emettere `[[RICORDO|categoria|breve|completo]]`; `estrai` ne analizza il formato e `salva` persiste il testo. Mancano un controllo sistematico della veridicità e una distinzione esplicita fra «detto dall'utente», «dedotto dal modello» e «verificato».

**Perché è un difetto:** interpretazioni errate del modello possono consolidarsi come ricordi duraturi.

**Correzione:** conservare provenienza, livello di conferma e data; chiedere approvazione per deduzioni personali o decisioni importanti, evitare duplicati semantici e permettere rettifica.

**Beneficio:** meno false memorie.

### F. MEDIA — Recupero ancora prevalentemente lessicale

**Evidenza:** `second_brain.py`, `ricordi()`, usa FTS5 per prefissi di parole e ordinamento per parole condivise; `search()` usa sovrapposizione lessicale.

**Perché è un difetto:** domande formulate con sinonimi o riferimenti indiretti possono non recuperare l'informazione utile.

**Correzione:** migliorare normalizzazione italiana e varianti morfologiche, introdurre ranking esplicito con fonte/recenza/pertinenza e prove con domande parafrasate. Non introdurre subito un secondo modello pesante sul Pavilion.

**Beneficio:** memoria più utile con risorse modeste.

### G. MEDIA — «Comando eseguito» senza ricevuta di esito

**Evidenza:** `orchestratore.py`, `Strumenti.comando` chiama `self.run_command(text)` e restituisce «Comando eseguito da Lumi; l'esito è nella chat dell'utente», senza attestare nel proprio return che l'azione abbia raggiunto lo scopo.

**Perché è un difetto:** l'AI può interpretare come completata un'operazione soltanto inviata all'esecutore.

**Correzione:** uniformare ricevute `success` / `failure` / `pending` / `unknown`, con identità dell'azione, identificatore e prova. Solo un risultato verificato entra come successo nella memoria operativa.

**Beneficio:** Lumi dice «riuscito» solo quando può dimostrarlo.

### H. MEDIA — Mancano prove complete dei percorsi quotidiani

**Evidenza:** esistono numerosi test unitari specifici (`tests/test_ricordi.py`, `tests/test_finestra_unica_e_python.py`, `tests/test_servizi_online.py`, `tests/test_allegati.py` ecc.), e il CI Windows ha prove reali mirate. Non è però una prova esaustiva delle sequenze utente dalla voce al risultato, persistenti al riavvio, sul Pavilion.

**Correzione:** suite end-to-end con circa 20 scenari concreti: riconoscimento, disambiguazione, conferme, comandi, file nuovi/esistenti, recupero memoria, chat/progetti separati, failover online, Telegram, annullamento, ripartenza, recupero in caso di errore e RAM/CPU.

**Beneficio:** meno regressioni di integrazione.

## Architettura raccomandata

`Voce/testo utente → router (comando diretto o domanda) → AI per interpretare/proporre → unico gate autorizzazioni → esecutore → ricevuta verificabile → memoria`.

- Mantieni l'esecuzione deterministica per comandi locali riconosciuti.
- Le risposte AI **non sono permessi**.
- Memoria e contenuti dei file **sono dati**, non istruzioni operative.
- Un esito «richiesta inoltrata» non diventa «operazione completata».
- Se non si può dimostrare il risultato, dichiararlo `unknown`.

## Piano di intervento per Claude Code

1. **P0 — Sicurezza:** isolamento Python, anteprima completa e protezione contro sovrascritture con backup.
2. **P1 — Memoria:** correggere cancellazione totale, scope dei progetti e provenienza/consenso per fatti generati dall'AI.
3. **P1 — Esiti operativi:** introdurre ricevute verificabili senza spezzare i comandi esistenti.
4. **P2 — Recupero intelligente leggero:** migliorare ricerca e contesto sul Pavilion, con misure reali.
5. **P1 — Collaudo end-to-end:** verificare tutti i flussi chiave su Windows e, prima della promozione, sul Pavilion.

**Metodo:** una correzione per volta, test mirati e suite generale, checkpoint e rollback; preservare ZIP esistenti, profili, conversazioni, Second Brain e dati Telegram. Non dichiarare una funzione verificata soltanto perché un test sintetico è verde.

## Esito

**La struttura va mantenuta e consolidata, non riscritta.** Il progresso maggiore della 049 è nell'unificazione delle capacità; il rischio maggiore è l'affidabilità delle operazioni autonome e della memoria. Prima di aggiungere funzioni nuove, migliorare sicurezza, verificabilità, continuità e prove reali.

### Limiti dell'audit

- L'audit è statico, basato sul commit sorgente `bf7518b...` della 049 e sui risultati GitHub Actions.
- Non è stato eseguito un test live sul computer dell'utente.
- Non è stato aperto/estratto localmente lo ZIP per confrontarne ogni byte con i sorgenti: la pubblicazione è attestata dal commit e dalla CI.
- I punti rappresentano difetti osservabili nel codice o rischi motivati; la loro frequenza nella pratica richiede test reali.
