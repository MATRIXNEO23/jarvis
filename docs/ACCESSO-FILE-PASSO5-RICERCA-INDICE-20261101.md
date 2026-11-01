# Ricerca vocale, passo 5A e indice locale per ogni PC — 2026-11-01

## Ripresa verificata
La precedente sintesi su main terminava al passo 4. Il ramo effettivo feature/file-access-20261101 contiene un passo successivo: 61deabcf9cdc5ead14561c37a26e52f4e2ddb1aa. Letti il checkpoint del ramo, diff dal passo 4, service.py, policy.py, windows.py e LEGGIMI; riletti i log effettivi della CI. Nessun lavoro di questa ripresa ha modificato il runtime.

## Passo 5A: esito acquisito, nessuna nuova build
[Run 41341801789](https://github.com/MATRIXNEO23/jarvis/actions/runs/41341801789), stesso SHA 61deabcf, completata SUCCESS. Entrambi i job Windows Server 2022:
- 124953209810, Python 3.12.10: 436 test in 48.587 s, OK.
- 124953210058, Python 3.11.9: 436 test in 48.171 s, OK.
Sintassi Python/Node/PowerShell e probe nativo PASS. Build candidato, verifica ZIP estratto, upload artifact e publisher SKIPPED. Nessun nuovo test Linux, installazione, pacchetto o benchmark Pavilion.
Il probe trova Known Folders e identità percorsi/volumi; index_available=false ed Explorer=none. Questo non prova l'indice Windows operativo o una finestra Explorer personale.

Ambito del passo: avanzamento nella finestra esistente tramite queue/poll, eventi con identità del lavoro, contatori e ragioni di interruzione distinti; controllo del budget/annullamento anche sulle voci escluse. Prove proprie comprendono UI Tk reale e callback effettivi con trascrizioni controllate. Non sono prove di microfono, STT, account GPT o carico sul Pavilion. Una chiamata Windows in corso può richiedere la sua conclusione/timeout prima di fermarsi.

## Requisito chiarito dall'utente
Jarvis deve rilevare sul PC in cui è installato le unità, cartelle e file effettivi e costruirsi un indice locale per cercare e aprire gli elementi via voce. Deve poter operare anche su un PC diverso dal Pavilion, con account, dischi, lettere e percorsi differenti; niente percorsi fissi o indice del primo PC considerato valido sul secondo.

L'obiettivo è l'intero PC accessibile nel perimetro consentito dalle spunte/esclusioni e dai permessi Windows. Non ridurlo alle sole cartelle personali note. Le zone non visitate, escluse o non accessibili vanno segnalate nella copertura, senza dichiarare una scansione universale. Indicizzazione non estende i formati attualmente leggibili/apribili dal componente.

## Review mirata e soluzione proposta
Fatti nel codice attuale:
- windows.drives rileva già unità locali/rimovibili; known_folder risolve il profilo corrente; volume_identity e AccessPolicy controllano identità e consenso. Riutilizzare questi adattatori.
- _search_impl consulta Windows Search e poi attraversa i nomi con os.scandir. Conserva soltanto le corrispondenze della query corrente e perde pila/cartella/iteratore alla fine.
- _report espone al massimo 20 risultati. Budget della passata: 5000 voci/10 secondi. Ripetere oggi la ricerca non equivale a riprenderla.
- Non esistono ancora un catalogo persistente completo per macchina, ripresa della scansione o aggiornamento incrementale dell'indice.
Queste sono osservazioni statiche sui sorgenti verificati, non un test del futuro indicizzatore.

Proposta coerente con il requisito: estendere il componente file_access esistente con una scansione progressiva riutilizzabile, che registri su disco nomi, percorsi e tipo degli elementi consentiti, indipendentemente dalla query pronunciata. Separare il limite delle righe mostrate dal lavoro di catalogazione; usare l'indice già raccolto durante la scansione, dichiarandone la copertura. Conservare avanzamento per pausa/ripresa senza ripartire sempre dall'inizio e aggiornare aggiunte/rimozioni/rinomine; controllare l'esistenza e la policy attuale prima di aprire un risultato. Sul nuovo PC creare un catalogo riferito a quel contesto, senza riutilizzare automaticamente identità e consensi di un altro dispositivo.
La prima scansione va progettata a carico contenuto, annullabile e recuperabile, senza riempire la RAM con tutto l'albero o aggiungere un servizio esterno per assunto. Le prestazioni vanno misurate, non promesse.

Windows Search resta una fonte già integrata: da solo non dimostra che tutto il PC sia catalogato. La documentazione Microsoft descrive ambiti/esclusioni e modalità Classic/Enhanced:
https://support.microsoft.com/en-us/windows/experience/performance-optimization/search-indexing-in-windows
https://support.microsoft.com/en-us/windows/privacy/windows-search-and-privacy
Python documenta os.scandir e la necessità di aggiornare i metadati divenuti vecchi:
https://docs.python.org/3.11/library/os.html#os.scandir
Non installato né adottato Everything. La scelta del formato dell'indice e della strategia di aggiornamento resta da concludere nella review, non è un risultato prestazionale verificato.

## Prossimo passo preciso
5A chiuso con le prove sopra; iniziare la review specifica 5B/indice autonomo, già richiesta dalla precedente istanza, prima del nuovo codice. Definire contratto minimo di persistenza, identità del PC/volume, ripresa dopo arresto, invalidazione per revoca, e raccordo con worker/coda e comandi voce senza bloccarli. Verificare come gestire una directory cambiata durante la pausa senza perdere file o duplicare risultati; un iteratore scandir non è un cursore persistente affidabile per un nuovo processo.
Accettazione Windows prevista: due contesti macchina/profilo/unità differenti controllati, indice inizialmente assente, scansione oltre una passata e ripresa dopo riavvio, query mentre l'indice è parziale, rinomina/rimozione/aggiunta, volume sostituito, accesso negato, esclusione/revoca, risultati vecchi e paging senza elenchi TTS. Simulare due contesti non equivale al collaudo di due PC reali.
Nessuna nuova autorizzazione per una dipendenza esterna è dedotta dalla richiesta concettuale. Nessuna build automatica. Base b936879 e pacchetti precedenti preservati.
