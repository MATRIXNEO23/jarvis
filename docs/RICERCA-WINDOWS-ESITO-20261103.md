# Ricerca Windows — fattibilità e correzioni, 3 novembre 2026

## Risultato richiesto
Ricercare file/cartelle nelle aree autorizzate del PC corrente, mostrare risultati, permettere scelta e apertura mantenendo il riferimento. Minecraft e Netflix sono esempi, non requisiti da codificare per marchio. Impostazioni, dati e versioni precedenti vanno conservati; zero costi aggiuntivi.

## Cosa offre Windows e cosa fa già Jarvis
- Windows Search indicizza anche oggetti cartella, nelle posizioni incluse nella sua configurazione; SCOPE consente query su cartelle e sottocartelle. L'adapter reale di Jarvis è stato provato su Windows con creazione/ricerca/eliminazione di una cartella temporanea (run41604955975, passo nativo riuscito anche se allora la suite aveva failure del parser).
- Per trovare la directory di un programma il codice consulta anche Uninstall/InstallLocation/DisplayIcon, App Paths, destinazioni dei collegamenti Desktop/Start e pacchetti Store. Non è la stessa domanda di una ricerca per nome cartella. La documentazione App Paths descrive il percorso dell'eseguibile; i metadati disponibili non garantiscono directory dati/salvataggi di ogni launcher.
- Windows consente apertura di cartelle e documenti tramite ShellExecute e associazioni. Nel componente distribuito, però, i documenti vengono letti nell'anteprima interna di testo: apertura nel programma abituale è una scelta non ancora ricevuta. Il pannello della domanda è stato chiuso senza risposta; nessun consenso dedotto e nessuna nuova capacità aggiunta.

Fonti Microsoft consultate:
- https://learn.microsoft.com/en-us/windows/win32/search/-search-indexing-process-overview
- https://learn.microsoft.com/en-us/windows/win32/search/-search-sql-folderdepth
- https://learn.microsoft.com/en-us/windows/win32/shell/app-registration
- https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shellexecutea

## Difetti seguiti fino al punto responsabile
1. La richiesta «Cercami la cartella di Nome» diventava query «di Nome». Le quattro failure dei tre test su Windows erano corrette, non un limite del provider. Il parser ora elimina solo la preposizione iniziale dopo l'estrazione dello scope; nomi quotati e comandi d'installazione restano separati.
2. Il servizio alternava indice e scansione per ciascuna radice. Una prima scansione poteva esaurire il budget prima della query indice alla seconda radice. Ora interroga prima l'indice di tutte le radici autorizzate; risultati utili vengono mostrati senza scansione. Se non ci sono risultati utili, resta la scansione limitata esistente.
3. Nelle ricerche d'installazione la nota sulle registrazioni nascondeva il riscontro dell'indice. Ora entrambe le informazioni sono conservate. L'esito solo-indice dichiara copertura non necessariamente completa; non prova assenza globale.
4. Il revisore ha rilevato un avviso limite erroneo quando radici sovrapposte restituivano duplicati dopo i primi20. Prova aggiunta prima della correzione; vedere evidenza finale per esito.

## Ambito rimasto distinto
- R02: reset anticipato della ricerca prima del passaggio a GPT ancora aperto; R01 (consegna del riepilogo nel prompt) già verificato nel source c2964c7, non va scambiato per soluzione universale della continuità.
- R03: conferme operative senza ricevuta locale ancora aperte.
- «Macking Craft» e «Harris/Garris» riguardano trascrizione/richiamo vocale e non sono corretti dal parser file.
- Il limite di5000 unità UTF16 è imposto dal bridge di Jarvis: il messaggio troppo lungo viene respinto localmente, non dimostra quota Plus esaurita. Correzioni budget e R01 già presenti nei sorgenti precedenti, non nello ZIP d06e233.
- Windows Search può non coprire ogni cartella/unità. Nessuna promessa di indice completo del PC, di lettura universale o di individuazione certa delle directory interne di ogni applicazione.
- Timeout per query dell'adapter fino a8 secondi, chiamate per radice seriali: molte radici possono richiedere attesa. Worker/progress esistenti restano usati; prestazioni Pavilion non misurate.
- Nessuna nuova build, autenticazione o installazione sul PC dell'utente. Il vecchio ZIP resta invariato finché non viene richiesta e verificata una nuova consegna.

## Metodo e recupero
Applicate Systematic Debugging, Test-Driven Development, Writing Plans, Requesting Code Review e Verification Before Completion. Storia Red/Green e revisioni nel file evidence/windows-search-order-20261103.json e nel piano superpowers/plans/2026-11-03-windows-search.md. Prove su filesystem temporaneo Windows, query provider controllate per il servizio e probe nativo reale separato. Nessun test Linux o prova microfono/modello/account personali.

## Esito verificato del codice
Source 9df2229f05b94dbefd099f228151d042046f2701, [run41609193500](https://github.com/MATRIXNEO23/jarvis/actions/runs/41609193500) SUCCESS:500test per Python3.11/3.12, zero failure/errori. Sintassi/probe e indice Windows nativo PASS; servizio ripristinato e fixture rimossa. Revisore indipendente ha confermato la correzione dell'avviso sui duplicati, senza altri blocchi statici. I test sostituiscono il provider per esercitare in modo deterministico ordine e stati; il probe nativo separato usa l'adapter reale. Nessuna nuova build: le correzioni non sono nello ZIP ancora pubblicato.
