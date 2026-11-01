# Accesso file — proposta semplice e verifiche

2026-11-01. **Inventario e revisione iniziale completati; integrazione Windows e implementazione ancora da eseguire.** Requisiti nella [scheda WINDOWS](WINDOWS.md). Base [b936879](https://github.com/MATRIXNEO23/jarvis/tree/b936879a431370d206152be7b089baf587d15499); documentazione recuperata da main 95bed8c. Nessuna nuova add-on installabile o modifica della build funzionante.

## Criterio vigente dell'utente

Gli esempi descrivono ciò che Jarvis deve fare, non come costruirlo. L'assistente propone la soluzione tecnica in maniera semplice, con prove, usando prima Jarvis e Windows. Non creare moduli per comandi già disponibili. Add-on organizzata e codice leggibile non significano un framework nuovo o un file per ogni comando. Questa precisazione supera le scelte tecniche premature della prima stesura locale di questo documento, mai implementate o pubblicate.
Se un dubbio residuo cambia il risultato desiderato, chiedere conferma con poche opzioni concrete e una raccomandazione; non chiedere all'utente di scegliere dettagli tecnici che possono essere verificati autonomamente.

**Conservazione:** documento ed evidenze preparati nei commit locali b93cbfa/b360505. Dopo il blocco automatico iniziale, l’utente ha autorizzato esplicitamente la pubblicazione documentale su main. Chiarito che «locale» indicava il checkout dell’ambiente di sessione, non il suo PC; GitHub è il punto di conservazione e recupero concordato. Nessun cambiamento del programma o pacchetto in questa pubblicazione.

## Proposta da spiegare all'utente

| Parte | Come usarla |
|---|---|
| Jarvis esistente | Mantiene dialogo, voce, GPT esterno, impostazioni e gestore add-on. Estendiamo gli stessi comandi di ricerca/apertura, senza un secondo motore parallelo. |
| Windows | Fornisce i percorsi reali del profilo, le unità, la ricerca indicizzata dove disponibile e l'apertura delle cartelle. I permessi rimangono quelli dell'utente Windows. |
| Add-on Accesso file | Contiene soltanto le parti mancanti: scelta delle cartelle consentite, applicazione delle esclusioni, collegamento della ricerca estesa e lettura dei file supportati. Usa lo stesso registro dei comandi. |

Impostazioni → Add-on → Accesso file → Configura: selezioni un disco/cartella; le sottocartelle sono incluse, togli soltanto le eccezioni. Riepilogo leggibile: «C: consentito, con 2 cartelle escluse. Solo lettura». Caricamento delle sottocartelle quando si espandono, senza scansione completa per aprire il pannello.

«Cerca il preventivo» usa risultati reali. Se manca un dato indispensabile, Jarvis fa una domanda mirata e conserva la risposta. «Il secondo» continua quella scelta senza ripartire; una semplice chiacchiera sul preventivo non avvia azioni. Locale diretto per comandi chiari; GPT esterno già collegato per interpretazione necessaria, senza introdurre modelli locali.

## Inventario sulla base esatta

I collegamenti puntano al codice della build funzionante, non alla radice storica main.

| Punto esistente | Fatto verificato | Minimo intervento necessario |
|---|---|---|
| [LocalEngine](https://github.com/MATRIXNEO23/jarvis/blob/b936879a431370d206152be7b089baf587d15499/local_engine.py#L171) | Ricerca nomi di file soltanto in Download; non cartelle né scelta di un risultato | Estendere lo stesso percorso di ricerca con il servizio dell'add-on; conservare il comportamento precedente quando assente/spento |
| [Gestore add-on](https://github.com/MATRIXNEO23/jarvis/blob/b936879a431370d206152be7b089baf587d15499/addon_manager.py#L348) | Accetta solo azioni fisse senza parametri; una ricerca ha bisogno almeno del testo da cercare | Aggiungere un collegamento esplicito alle sole nuove operazioni revisionate e validare i loro parametri; non un caricatore generico di codice |
| [Registro live](https://github.com/MATRIXNEO23/jarvis/blob/b936879a431370d206152be7b089baf587d15499/live_capabilities.py#L28) | Binding e disponibilità già presenti; il gestore aggiorna le registrazioni | Riusare questo registro per esecuzione ed elenco «cosa puoi fare?»; niente liste parallele |
| [Pannello add-on](https://github.com/MATRIXNEO23/jarvis/blob/b936879a431370d206152be7b089baf587d15499/addon_ui.py#L15) | Gestisce installazione/attivazione/rimozione; non ha Configura | Aggiungere Configura che apre le opzioni del componente |
| [Router GPT](https://github.com/MATRIXNEO23/jarvis/blob/b936879a431370d206152be7b089baf587d15499/conversation_router.py#L110) e [dispatcher](https://github.com/MATRIXNEO23/jarvis/blob/b936879a431370d206152be7b089baf587d15499/jarvis.py#L3286) | Traducono proposte in capacità validate; add-on attuali delegate a piani fissi | Collegare le nuove operazioni allo stesso percorso, con parametri validati ed esito reale; nessuna esecuzione di testo prodotto da GPT |
| [Voce](https://github.com/MATRIXNEO23/jarvis/blob/b936879a431370d206152be7b089baf587d15499/voice_control.py#L45) | Mapping preciso «cerca file …» assente; fallback GPT dipende dalla modalità | Stessa funzione per voce/testo; non cambiare automaticamente modalità o collegamento GPT |
| [Scelta breve](https://github.com/MATRIXNEO23/jarvis/blob/b936879a431370d206152be7b089baf587d15499/jarvis.py#L3269) | Un guard generico respinge un'azione GPT da «il secondo» | Risolvere prima una scelta locale effettivamente pendente; mantenere il rifiuto per risposte isolate/scadute |
| [Documenti](https://github.com/MATRIXNEO23/jarvis/blob/b936879a431370d206152be7b089baf587d15499/managed_documents.py#L23) | Gestisce Blocco note creati da Jarvis, non lettura generale di file esistenti | Non usare compose/save per leggere un file; aggiungere solo la lettura mancante, riusando il GPT per la spiegazione richiesta |
| [Percorsi/configurazione](https://github.com/MATRIXNEO23/jarvis/blob/b936879a431370d206152be7b089baf587d15499/document_store.py#L25) e [profilo](https://github.com/MATRIXNEO23/jarvis/blob/b936879a431370d206152be7b089baf587d15499/settings.py#L38) | Risoluzione parziale cartelle nota; profilo Trial già separato | Migliorare/riusare la risoluzione percorsi, rispettare il profilo dati esistente e salvare lì le scelte dell'add-on |

Sono necessarie piccole estensioni dei collegamenti nel nucleo: il solo file .jaddon non basta. La logica nuova resta nella cartella del componente. Non migrare automaticamente le altre funzioni di Jarvis.

## Confini del collegamento

Operazioni necessarie: elencare, cercare, leggere e aprire il risultato identificato. Il motore convalida azione, argomenti, add-on attivo e cartella consentita prima dell'I/O. Non basta aggiungere il nome di un'azione al catalogo per renderla eseguibile. Il modello interpreta la richiesta; i risultati devono essere osservati dal PC.

Mantenere il .jaddon descrittivo, l'installazione inizialmente spenta, il consenso e il controllo di stato del gestore esistente. Prima scelta: adattamento circoscritto del contratto attuale per le sole operazioni file revisionate. **Non adottare adesso un nuovo schema di pacchetto, un sistema generico di provider o import dinamici.** Cambiare schema soltanto se una prova concreta dimostra che l'adattamento compatibile non basta; documentare allora il motivo.

La scelta di un risultato resta locale e legata alla ricerca corrente. «Il secondo» dopo «quale cartella vuoi aprire?» completa l'apertura richiesta; dopo una semplice lista seleziona soltanto. «Sì» completa solo una domanda sì/no identificata. Annullamento, cambio argomento/progetto, revoca e scadenza invalidano la richiesta. Una scelta non può eseguire due volte la stessa azione. Non serve inventare un protocollo generale di workflow per conservare questo piccolo stato.

Disponibilità, comandi ed elenco funzioni derivano dallo stesso registro/configurazione; se il componente è spento, mancante o senza cartelle configurate non promettere l'accesso generale. File mancante: console con nome/percorso e pacchetto corretto da ripristinare. Servizio Search indisponibile non significa dipendenza Python mancante.

## Cartelle consentite e sola lettura

Nessun disco selezionato per supposizione. Una selezione include i discendenti; eccezione più specifica prevale, conflitto identico esclude. Una cartella figlia reinclusa è l'unico ramo riaperto; genitori mostrati parziali. La schermata deve mostrare la policy effettivamente salvata, anche dopo un cambio alla spunta del genitore. Non enumerare fratelli esclusi per raggiungere un figlio consentito.

Una spunta autorizza Jarvis, non cambia ACL/UAC. Rilevare profilo/cartelle reali da Windows; niente C:/Users costruito dal nome Alberto. Identificare i volumi oltre la lettera: un'altra periferica che diventa D: non eredita il consenso. Percorso rimosso, cartella sostituita, volume assente o destinazione reindirizzata cambiata richiedono nuova verifica; non autoautorizzare una destinazione differente. Unità filesystem locali/rimovibili iniziali; rete e dispositivi MTP non dichiarati funzionanti senza prova.

Controllare ambito e destinazione reale per ogni ricerca, risultato, lettura e apertura, compresi percorsi digitati o proposti dal modello. Normalizzazione per componenti, non startswith; junction/collegamenti non devono aggirare un'esclusione. Per leggere: handle in sola lettura, verifica destinazione sullo stesso handle e lettura da quello. Rifiutare namespace dispositivo/stream alternativi non previsti; errore di verifica non concede accesso. Permessi negati: messaggio preciso, nessuna elevazione nascosta.

Nel primo incremento tutte le operazioni sui dati sono in sola lettura. Questo copre anche il sistema Windows senza inventare ora un database universale dei file protetti. Future scritture/cancellazioni restano una fase distinta, con protezione delle risorse di sistema anche fuori da Windows e prove contro collegamenti/sostituzioni. SfcIsFileProtected negativo non prova libertà di modifica.

Le spunte controllano le operazioni di questo componente, non creano un sandbox dell'intero processo o di Esplora file. Quando l'add-on è attivo, i vecchi comandi di ricerca/elenco/apertura Download/C: devono passare per la stessa policy. Quando è spento, restano le funzioni storiche nel loro ambito precedente: non chiamare le spunte «blocco globale del PC».

Aprire una cartella in Explorer è distinto da leggere un file. ShellExecute su un file può avviare un programma/editor: non garantisce sola lettura. Per il percorso minimo, cartelle in Explorer e testo supportato mostrato senza modifica; apertura esterna dei documenti resta requisito da completare/collaudare con limiti espliciti. Non eseguire script/eseguibili trovati dalla ricerca per fingere di averli soltanto letti. L'avvio programmi scelti resta nell'attività applicazioni.

## Windows prima di nuove dipendenze

Prima prova tecnica: Known Folders per profilo/percorsi, API native per unità/percorso effettivo, interrogazione dell'indice Windows Search. Python ha già ctypes e subprocess; verificare un piccolo collegamento a Windows PowerShell/ADO già presente prima di aggiungere librerie COM. Script fisso, query costruita/validata localmente e input come dati: nessuna interpolazione di comandi GPT. Timeout e chiusura risorse al termine. Non installare Everything, Syncthing o un indicizzatore per ottenere le sole spunte.

Se l'indice manca/non copre una cartella, completare con l'evoluzione della ricerca locale esistente nelle sole zone consentite. Enumerazione incrementale, contare file e cartelle, limite di tempo/elementi/risultati e annullamento; nessuna scansione continua o albero completo in RAM. Raggiungere il limite dà risultato parziale, non «non esiste». Non abilitare indicizzazione globale automaticamente.

Partire dai worker/eventi di Jarvis. Un thread non rende interrompibile un I/O Windows bloccato: provare i timeout della chiamata; **aggiungere un processo temporaneo soltanto dove necessario e dimostrato**, senza servizio residente o sistema nuovo di processi per ogni comando. Numeri di RAM/CPU e soglie finali non fissati come risultati senza misura.

Cercare le cartelle di un'app riusa ricerca e dati reali disponibili (registrazioni Windows, collegamenti, configurazione del launcher effettivo). Distinguere programma, dati e salvataggi; non fissare .minecraft o un'altra cartella come risposta universale. Più candidati: chiarimento mirato. Il risultato per significato richiede evidenze ulteriori rispetto alla sola corrispondenza del nome e resta da provare.

## Codice leggibile, senza struttura inventata in anticipo

Propria cartella dell'add-on, LEGGIMI con mappa dei file e percorsi dati, manifest e risorse necessarie. Dividere le responsabilità effettive: configurazione/interfaccia, accesso/regole, ricerca, lettura. I nomi e il numero dei file si decidono dal codice necessario, riusando helper esistenti; non obbligare nove nuovi moduli o creare un file per ogni comando. Nessun file monolitico di migliaia di righe.

Configurazione nel profilo già scelto da Jarvis tramite default_path, distinta dalle preferenze globali; niente nuova memoria parallela. Test propri raccolti dalla CI esistente. Pacchetto con i soli file runtime, risorse e istruzioni essenziali: selezione verificata sullo ZIP estratto, test/handoff fuori dal pacchetto operativo. Conservare base e ZIP precedenti.

## Ordine di lavoro e accettazione

1. **Prova nativa circoscritta Windows:** cartelle note reali, volume/percorso effettivo, indice Search presente/assente e ricerca di file temporanei noti. Nessun dato privato, permesso cambiato o app utente da scegliere come prerequisito. Qui Windows/PowerShell non sono presenti: questa prova non è ancora eseguita.
2. **Primo percorso completo sulla base b936879:** configura radice → elenco/ricerca → scelta contestuale → lettura/apertura cartella → esito. Usare i gestori di Jarvis, testare il collegamento presto; non costruire prima tutti i moduli isolati.
3. **Completamento dei requisiti per incrementi:** localizzazione installazione/dati app, spiegazione del contenuto richiesto, apertura esterna/formati supportati. TXT/MD/JSON sono candidati iniziali senza librerie aggiuntive, non supporto già realizzato. Limiti contenuto coerenti col budget reale del GPT; testo del file è dato, mai comando. Non presentare il percorso minimo come funzione generale già completa.
4. **Verifiche e consegna:** test propri, regressioni, Windows reale e ZIP estratto; link persistente in Download solo a esito positivo. Misure sul Pavilion e prova PC separati dai test simulati. Aggiornare registro senza sostituire la base finché l'utente non ha provato la nuova versione.

| Verifica necessaria | Casi principali |
|---|---|
| Compatibilità e catalogo | Vecchie add-on immutate; nuova installata/spenta/attiva/rimossa; parametri non validi; file mancanti; elenco capacità coerente |
| Spunte e profilo | Ereditarietà/eccezioni/stato parziale, riavvio/profilo Trial, cartelle reindirizzate, volume rimosso/lettera riusata |
| Accesso reale | Percorso diretto o da indice fuori ambito, Unicode/prefissi simili, junction/mount/file sostituito, revoca durante operazione, permessi negati |
| Ricerca | Prefisso/sottostringa/file/cartella, indice incompleto/stale/spento, directory enormi/vuote, timeout/annullamento, risultato parziale dichiarato |
| Lettura/apertura | Encoding, binario rinominato TXT, dimensioni, formato non supportato, file bloccato/scomparso, contenuto con istruzioni; nessuna modifica del file; richiesta di apertura distinta da finestra osservata |
| Dialogo | Chat senza esecuzione, comando chiaro senza GPT, parafrasi col GPT simulato, scelta breve una sola volta, cambio argomento/progetto e GPT indisponibile |
| Dati app | Più installazioni/launcher, cartella dati con nome diverso, ruoli distinti, app assente/ambigua e indizi insufficienti |
| Consegna e consumo | Import ed esecuzione da ZIP estratto; RAM/CPU/disco senza add-on, spenta, attiva inattiva, in ricerca e dopo; contare eventuali figli temporanei |

Callback con trascrizione simulata, audio di prova e microfono/GPT reali sono prove distinte. Nessuna garanzia di assenza totale di bug o di ritrovamento senza indizi.

## Prove eseguite e revisione

- 14 sorgenti pertinenti dell'estrazione confrontati byte per byte con b936879: [integrità](../evidence/accesso-file-20261101/source-integrity.json).
- 88 regressioni pertinenti della base: 88 superate, zero skip/fallimenti/errori, Linux/Python 3.12.14. [Riepilogo e comando riproducibile](../evidence/accesso-file-20261101/baseline-tests.json), [log](../evidence/accesso-file-20261101/baseline-tests.log). Non sono test di una nuova add-on.
- Cinque osservazioni locali: Download soltanto file, parametri add-on respinti, target generale non ammesso, mapping voce ricerca assente, risposta breve classificata ambigua. [Esito](../evidence/accesso-file-20261101/baseline-observations.json), [riproduzione](../evidence/accesso-file-20261101/reproduce.py). Il guard applicativo è letto, non eseguito dalla prova.

Revisione iniziale: eliminati i presupposti «basta il manifest», «il binding esegue già», «il secondo procede già» e «open garantisce lettura». Ricontrollo mirato contro il codice. Dopo la precisazione dell'utente, eliminate dalla proposta scelte premature di schema/framework/numero moduli/processi; non erano implementate. Rimangono necessarie validazione dei parametri e policy applicata alle operazioni, perché richieste dal funzionamento desiderato.

**Prossimo passo:** prova Windows limitata del punto 1, poi percorso completo del punto 2 con la soluzione più semplice dimostrata. Nessuna nuova domanda sull'app campione, sulla struttura delle spunte o sul fatto che servano ricerca e lettura. Nessuna nuova build o modifica dati utente. Recupero diretto dal [registro versioni](../../Download/REGISTRO-VERSIONI.md).

## Fonti primarie ricontrollate

[SHGetKnownFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath), [GetFinalPathNameByHandleW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfinalpathnamebyhandlew), [Windows Search SQL/ADO](https://learn.microsoft.com/en-us/windows/win32/search/using-sql-and-aqs-to-query-the-index), [ShellExecute](https://learn.microsoft.com/en-us/windows/win32/shell/launch), [reparse point](https://learn.microsoft.com/en-us/windows/win32/fileio/reparse-point-operations) e [volumi montati](https://learn.microsoft.com/en-us/windows/win32/fileio/determining-whether-a-directory-is-a-volume-mount-point). Esempio originale [PowerShell/ADO Microsoft](https://devblogs.microsoft.com/scripting/hey-scripting-guy-weekend-scripter-querying-the-windows-search-index/), candidato per prova senza copiare codice.

Le fonti descrivono meccanismi disponibili; non sono prove dell'integrazione Python o del funzionamento sul Pavilion. La mappa Archify a86c2c9 rappresenta il nucleo successivo, non questi collegamenti ancora da costruire.
