## Localizzazione dal nome programma — codice verificato, distribuzione pendente
Esempi: «dove è installato Nome», «dov'è installato Nome», «trovami la cartella del programma Nome». Riutilizzano localizza e i dati Windows; il nome leggibile di un collegamento può differire dalla directory/exe reale. Scelta e apertura nella finestra risultati restano vocali. Template target/scope supportati: %APPDATA%, %LOCALAPPDATA%, %USERPROFILE% più sottopercorso, risolti sul profilo corrente e controllati dalla policy. Esempi, non formule obbligatorie; parafrasi non risolte restano al modello collegato. [Prove e limiti](ACCESSO-FILE-PASSO8-CARTELLE-PROGRAMMI-20261101.md). Nessun nuovo comando/add-on parallelo o percorso Minecraft codificato. Vecchi ZIP distinti dai sorgenti verificati.

## Raffinamento ricerca — sorgenti verificati, distribuzione pendente
Nessun comando nuovo: riusati ricerca/localizza/apri/leggi di Accesso file. Se un indizio non produce risultati, il GPT già attivo e collegato può precisarlo una volta; la successiva azione locale mantiene operazione, ambito e tipo. Un chiarimento conserva la richiesta iniziale; annulla ricerca revoca anche la proposta pendente. Errori lettura e figlio Explorer assente non avviano ricerche ampliate. [Prove e limiti](ACCESSO-FILE-PASSO6-MODELLO-20261101.md). Nessuna funzione web leggibile dal modello aggiunta. Non attribuire il comportamento ai vecchi ZIP.

# Catalogo delle capacità di Jarvis

Il file **`jarvis_commands.json`** è l'elenco dichiarativo delle azioni effettivamente disponibili nel ramo sperimentale. `capability_registry.py` lo valida e fornisce a GPT nomi e descrizioni delle azioni. È un **catalogo di capacità**, non un elenco arbitrario di comandi di Windows e non contiene istruzioni eseguibili.

## Come funziona una frase naturale

Per esempio «Mi chiudi quel Blocco note?», «Ho finito con gli appunti, chiudi Blocco note» e «Puoi chiuderlo?» possono essere interpretate da GPT come l'intenzione `notepad.close`, **solo se Jarvis ha già identificato un suo documento attivo**. GPT non deve conoscere ogni variante testuale: restituisce il nome dell'azione autorizzata e l'esecutore decide quale procedura chiamare. La chiusura passa per la scelta vocale di salvataggio, annullamento o uscita senza salvare; non si usa `taskkill`.

Il flusso di fiducia è: **voce Vosk → GPT (interpretazione) → catalogo delle capacità → verifica stretta in Python → esecutore locale → eventuale risposta SAPI**. In modalità «Ehi Jarvis» i comandi fissi restano offline; soltanto nella modalità Conversazione GPT scelta manualmente il testo trascritto viene sottoposto a GPT.

## Programmi inizialmente supportati

| Applicazione | Azioni supportate | Limiti |
|---|---|---|
| Blocco note | `notepad.open`, `notepad.write`, `notepad.close` | Solo finestra di Blocco note classico aperta e identificata da Jarvis; nessuna chiusura di altri documenti |
| Esplora file | `explorer.open`, `explorer.downloads`, `explorer.drive_c` | Il disco C è un percorso fisso; niente path arbitrari da GPT |
| Browser | `browser.open`, `browser.search` | Browser predefinito, ricerca Google esplicita; non controllo generale di tab o account |
| Calcolatrice | `calculator.open` | Apertura, non chiusura |
| Sistema | `system.status`, `history.list` | Consultazione CPU/RAM e attività |
| Download | `downloads.list`, `downloads.find` | Solo elenchi e ricerca per nome nei Download |

Il modello riceve una rappresentazione compatta di queste azioni, comprensiva di descrizione ed esempi, invece di una lista di frasi magiche. Le risposte GPT sono JSON con `action_id` e `arguments`. Gli argomenti sono verificati: non può inventare `run_shell`, eliminare file, passare `force: true` per chiudere Blocco note o scegliere un eseguibile arbitrario.

**Aggiungere un'azione soltanto nel JSON non la abilita.** Per supportare un nuovo programma occorre implementare un adattatore Python, una politica di autorizzazione, il controllo della finestra/focus e test di regressione, quindi aggiungere l'identificatore alla lista di esecutori autorizzati in `capability_registry.py`. Il catalogo non legge automaticamente tutti i menu dei programmi: questa capacità richiederebbe adapter e ispezione UI specifici per ciascuna applicazione.

## Requisiti di sicurezza

- Il microfono parte **sempre spento**; le modalità sono manuali.
- Nessun nuovo costo, hosting o API a consumo. L'interpretazione tramite GPT usa il DevKit già configurato ed è soggetta ai suoi limiti; le azioni locali e i comandi precisi funzionano anche senza GPT.
- Un comando ambiguo come «chiudi quel file» senza un documento identificato deve produrre un chiarimento, **non chiudere un processo qualunque**.
- La scrittura di file resta limitata ai nuovi documenti gestiti da Jarvis; file esistenti, repository e documenti sensibili non sono modificabili per effetto del catalogo.
- Se manca `jarvis_commands.json`, la struttura è sbagliata o contiene ID sconosciuti, la risoluzione GPT delle capacità fallisce invece di eseguire azioni.
- I vecchi formati GPT sono mantenuti per compatibilità temporanea, ma il nuovo prompt indirizza GPT al registro; non sono consentiti nuovi tool arbitrari nei formati precedenti.

## Verifica e rilascio

I test automatici coprono: corrispondenza tra catalogo e codice, varianti di intenzioni canoniche, nuova apertura del disco C, rifiuto di path/eseguibili inventati, rifiuto di chiusura Blocco note senza documento gestito e controllo delle preferenze precedenti.

**Il collaudo reale sul Pavilion resta necessario**, soprattutto perché GPT può scegliere di chiarire una frase ambigua. Conservare la vecchia cartella e provare solo la ZIP sperimentale estratta in una cartella nuova. Nessun merge automatico nella versione principale.
