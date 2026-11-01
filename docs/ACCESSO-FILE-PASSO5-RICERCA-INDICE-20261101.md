# Ricerca vocale, passo 5A e indice locale per ogni PC — 2026-11-01

## Requisito confermato — modello esterno e Windows collaborano nella ricerca
L'utente chiarisce che la frase naturale, anche senza nome esatto di file/cartella, va interpretata dal GPT esterno e tradotta in una richiesta utile per il motore locale. Esempio: «dov'è installato Minecraft?» non deve richiedere il nome preciso della directory. Conoscenze del modello o fonti web possono suggerire identità, alias, ruoli e ambiti di ricerca; l'esistenza e il ruolo sul PC sono da verificare localmente. Non è una richiesta di sostituire Windows Search né di creare un secondo motore.

Percorso da completare riusando quello attuale:
1. Comando preciso e completo già riconosciuto: via locale diretta, senza GPT obbligatorio.
2. Richiesta non risolta, semantica o ambigua: GPT conserva l'obiettivo e propone una capacità/ricerca strutturata del catalogo, con termini o ambito utili; se manca un dato indispensabile chiede una sola precisazione contestuale.
3. Windows verifica registrazioni classiche/Store, indice e cartelle accessibili reali. Un percorso tipico o suggerito dal web non diventa un percorso osservato.
4. Risultato locale torna nello stesso contesto per scegliere/aprire/spiegare senza far ripetere la richiesta. Distinguere installazione, launcher, impostazioni, dati/salvataggi e cache; omonimi/profili differenti richiedono scelta. Nessun nuovo comando/formula da memorizzare, nessuna esecuzione di shell/testi scaricati.

Review statica già effettuata nel runtime 61deabcf (invariato nel successivo commit di test 9bec77c3):
- conversation_router.build_conversation_prompt e parse_conversation_intent descrivono/validano già azioni add-on; manifest AccessoFile.jaddon contiene cerca/localizza/apri/leggi. jarvis.py gestisce sia voce sia testo con lo stesso contratto, contesto e risultato file.
- file_access.windows.installed_locations consulta già registrazioni e Store; _search_impl usa indice/scansione e distingue candidati d'installazione non verificati.
- Manca una strategia verificata di raffinamento dopo una ricerca nominale vuota/non utile: una frase riconosciuta dal parser locale può essere consumata come ricerca letterale prima del GPT. Non basta aggiungere parole al prompt o un nuovo parser parallelo; progettare il ritorno dei riscontri locali al percorso esistente mantenendo un solo obiettivo e controlli.
- gpt_bridge.mjs chiama sdk.streamResponse con model e input; in questo codice non è configurata una capacità di navigazione web né un ciclo di tool retrieval. browser.search apre una ricerca nel browser: non dimostra che il modello ne legga i risultati. Prima di dichiarare la ricerca web disponibile al modello occorre verificarne supporto nel collegamento esistente e integrarla/collaudarla senza API a consumo o dipendenze non motivate. Non fingere una consultazione web.
- Non alterare priorità documenti/progetti/Telegram, profilo dati o modalità microfono per introdurre questo raccordo.

Accettazione da progettare/provare su Windows: parafrasi→azione registrata con argomenti pertinenti; richiesta su programma nota con nome della directory differente; indice vuoto→raffinamento contestuale senza loop; alias/percorsi suggeriti non esistenti rifiutati; dati di gioco non spacciati per installazione; chiarimento senza perdita obiettivo; modello/web indisponibili con limite dichiarato; nessuna doppia apertura, revoca/scadenza rispettate. Distinguere callback con reply controllato da modello/account/microfono e web reali.
Stato: requisito e lacune documentati, nessuna nuova funzione GPT/web implementata in questa precisazione. La prova nativa Windows Search 9bec77c31dce3bab5fb7c76d1e08d4d370893d42 è in run 41343194895: suite unit per entrambi i job completata con successo, prova indice live ancora in corso al controllo. Nessuna build.

## In corso — prova positiva Windows Search prima di aggiungere componenti
Via esplicito dell'utente: proseguire, massima integrazione Windows, rendere semplici a voce funzioni già offerte dal sistema. Base source 61deabcf; main af82d9427b9549fcb6aad6acb09dc2a3c44c544d. Osservazione dimostrata nei log dei job 124953209810/124953210058: WSearch Stopped/Disabled. Il precedente verde non copre una query positiva nativa.
Unità limitata: nuovo probe di sviluppo tools/probe_windows_search_live.py e passo CI Windows 3.12 in .github/workflows/tests.yml; riusare indexed_candidates e gli adattatori attuali, nessuna modifica al runtime distribuito. Nel SOLO runner CI abilitare temporaneamente WSearch, poi ripristinare stato/startup in finally; fixture in cartella Documenti risolta da Windows. Provare query senza risultato, nuovo file effettivamente indicizzato, scope diverso, rinomina e cancellazione osservate nell'indice con attesa limitata. Fallimento o indice non disponibile NON sono successo o skip equivalente. Nessuna espansione di scope, Reset/Reindex globale o nuovo indicizzatore.
Prossimo controllo: CI Windows del commit sorgente; preservare prove di fallback quando WSearch è spento, build/ZIP/publisher disattivati. Se ambiente non indicizza la fixture, diagnosticare separatamente copertura e query prima di introdurre altre soluzioni. Prove sul Pavilion/microfono/account restano distinte.

## Decisione vigente — prima Windows Search, indice proprio solo se necessario
Precisazione successiva dell'utente: la funzione richiesta è una ricerca affidabile integrata col Windows corrente, semplice e senza duplicati. Preferire l'indice Windows se soddisfa i requisiti; NON è obbligatorio costruirne uno di Jarvis. Questa decisione supera le formulazioni sotto che impongono un catalogo autonomo per macchina. Restano validi i risultati desiderati: adattamento al PC, dischi/unità accessibili, novità, persistenza dopo aggiornamento e copertura dichiarata.

Verifica effettiva sul source 61deabcf: file_access/windows_search.ps1 usa ADODB.Connection con Provider=Search.CollatorDSO e interroga SYSTEMINDEX con SCOPE della radice consentita e filtro System.FileName LIKE; input JSON su stdin, TOP 50, timeout. windows.indexed_candidates lo chiama già; _search_impl lo consulta e integra con scansione diretta. Il lavoro da fare è migliorare/verificare questo percorso, non aggiungere un secondo raccordo Windows o assumere necessaria una nuova banca dati.
Microsoft documenta modalità Classic/Enhanced e posizioni incluse/escluse: Windows non garantisce che tutti i file di ogni unità siano già nell'indice. Fonte corrente:
https://support.microsoft.com/en-us/windows/experience/performance-optimization/search-indexing-in-windows
https://support.microsoft.com/en-us/windows/privacy/windows-search-and-privacy
La pagina Win32 sulle esclusioni dei rimovibili contiene note specifiche Vista/7: NON usarla per proclamare un divieto universale attuale su ogni disco USB Windows 10/11.

Prossimo passo sostitutivo: prova Windows mirata di disponibilità/provider, interrogazione positiva su contenuti temporanei realmente indicizzati e distinzione fra vuoto, non indicizzato, indice in aggiornamento ed errore; leggere configurazione/copertura prima di cambiare il sistema. Verificare paging, query e latenza sul raccordo esistente; il TOP 50 del provider e le 20 righe del servizio non dimostrano assenza di altri risultati. Sulle zone/periferiche non coperte usare/migliorare il fallback già presente con continuazione recuperabile; valutare persistenza aggiuntiva solo per una lacuna dimostrata, mantenendo un solo percorso operativo.
La CI 41341801789 aveva index_available=false: prova il fallback e gli altri controlli, NON un'interrogazione positiva dell'indice nativo. Indice di Windows è gestito dal sistema e non va ricreato per aggiornare Jarvis; eventuale checkpoint del fallback resta nei dati persistenti del profilo. Nessun indice proprio implementato, nessuna installazione, cambio di configurazione Windows o nuova build eseguiti.

## Persistenza fra interruzioni, riavvii e aggiornamenti — requisito confermato
L'utente richiede che l'arresto conservi ciò che è già stato catalogato e il punto raggiunto. La continuazione deve funzionare anche dopo chiusura/riavvio di Jarvis. Installare una nuova versione non deve cancellare indice o avanzamento né obbligare a rifare la scansione iniziale.
Indice e checkpoint devono vivere nei dati persistenti del profilo Jarvis già previsto (addon-data/accesso_file), separati dalla directory del codice/distribuzione. Riutilizzare la risoluzione del profilo attivo e le regole di migrazione esistenti; non creare una cartella dati concorrente né cambiare automaticamente profilo a ogni aggiornamento.
Salvare progressivamente con scritture coerenti/atomiche: alla pausa richiesta rendere durevole il progresso accettato; in caso di arresto improvviso riprendere dall'ultimo checkpoint valido, dichiarando che la porzione non ancora consolidata può richiedere un ricontrollo. Non promettere recupero di una scrittura mai completata o ripresa dal medesimo offset se una directory è cambiata nel frattempo. Conservare le voci già validate e riprendere il lavoro residuo senza ricatalogare tutto da zero.
Un aggiornamento dello schema dell'indice deve avere migrazione conservativa e recupero; niente ricostruzione silenziosa integrale per il solo cambio versione. Su una macchina nuova creare invece il suo catalogo; non confondere aggiornamento del programma sullo stesso PC con trasferimento su un altro PC.
Prove Windows richieste prima della consegna: pausa/riapertura con stesso profilo, installazione aggiornata in un'altra cartella ma medesimi dati, checkpoint interrotto/non valido con recupero, cambiamenti dei file durante la pausa e unità scollegata/ricollegata. Restano prove progettate, NON eseguite. Nessuna modifica runtime o build in questa precisazione.

## Aggiornamento incrementale e unità collegate — requisito confermato
Alberto precisa che Jarvis deve rilevare i dischi/percorsi realmente presenti (C:, D: e unità esterne collegate) e creare autonomamente il catalogo; non serve chiedere se iniziare da C/D o dalle periferiche. A una scansione successiva deve riconoscere ciò che è già catalogato e aggiornare le novità, senza ricostruire ogni volta tutto l'indice.

Contratto minimo da progettare nel componente esistente:
- Prima scansione: registrare nomi, percorsi, tipo e metadati necessari al confronto delle voci accessibili/consentite; conservare lo stato per macchina e identità dei volumi, non per la sola lettera.
- Scansioni successive: riutilizzare le voci invariate e inserire/aggiornare quelle nuove o cambiate. Rilevare spostamenti, rinomine ed eliminazioni senza dover rileggere il contenuto di tutti i file. Modalità concreta di rilevamento cambiamenti ancora da verificare: cercare le novità può richiedere di enumerare/confrontare i metadati delle cartelle; non promettere di scansionare fisicamente soltanto file nuovi senza un meccanismo che li segnali.
- Unità rimossa: segnare il volume non disponibile; non trattare tutti i suoi file come cancellati. Alla riconnessione confrontare la stessa identità anche se la lettera è cambiata. Un disco diverso con la vecchia lettera non eredita catalogo/consenso.
- Eliminazioni: eliminare o invalidare una voce del catalogo solo con evidenza di assenza nel perimetro verificato; scansione interrotta, errore di lettura e disco scollegato non provano la cancellazione.
- Prima di aprire un risultato: ricontrollare presenza e permessi attuali. Indice parziale/in aggiornamento deve dichiarare la copertura e consentire la ricerca sui dati disponibili. Nessuna modifica ai file catalogati.

Il rilevatore esistente windows.drives copre unità fisse/rimovibili che Windows espone come dischi locali. Rete e telefoni/MTP non sono già collaudati: inventariare i tipi rilevati e i supporti reali prima di dichiarare supporto di qualunque periferica. Non introdurre una funzione generale di gestione periferiche estranea all'indicizzazione.
Stato: requisito e contratto preliminare salvati; indice incrementale NON ancora implementato. Nessun nuovo codice, test runtime o pacchetto in questo aggiornamento. Ripresa/annullamento dell'indicizzazione restano necessari al contratto, non una funzione separata da far scegliere all'utente.

## Controllo cronologia per evitare duplicati
Confronto API b936879a431370d206152be7b089baf587d15499...61deabcf9cdc5ead14561c37a26e52f4e2ddb1aa: 29 commit, elenco completo non troncato. Letti diff aggregato e sorgenti correnti interessati; l'elenco dei commit da solo non prova ogni funzione. Già presenti: servizio/policy/gestore add-on, rilevamento profilo/unità, fonte Windows Search con scansione diretta, ricerca installazioni classiche/Store, scelte vocali numero/nome e tipo, richieste pendenti, contesto Explorer, finestra risultati e avanzamento/cancel. Da aggiungere nel componente esistente: catalogo persistente locale, confronto fra scansioni e continuazione/paginazione oltre i limiti; niente nuovo servizio parallelo. Build solo su richiesta.

| Commit | Cambiamento registrato |
|---|---|
| 7955efee | feat: prepare native Windows file access feasibility checks |
| 4f04df40 | feat: integrate scoped read-only file access and Windows regression suite |
| 0e6c95c8 | fix: normalize Windows short names and preserve pending file choices |
| cb28d233 | fix: accept fresh requests after activation and verify packaged Windows runtime |
| 63bfd048 | build: finalize Windows candidate verification and persistent Download publication |
| c20e6cf5 | fix: prioritize user folders within approved whole-drive searches |
| 7298fb63 | fix: release installation directory when native Windows helper outlives the window |
| c9faa11d | docs: close Windows candidate handoff with verified package, tests and rollback |
| 83fc6d0f | fix: keep file lists silent and preserve numbered file or folder intent |
| 755f9884 | fix: accept folder listing without article and repair callback test fixture |
| 950f655a | fix: preserve installation search goals and query native Store identities |
| 87006ee4 | docs: pause runtime work for proposals and require explicit manual candidate builds |
| cf0c33c9 | fix: resume pending file actions from an exact result name |
| dcc4aebc | test: compare real Windows directory identity in pending choice check |
| 75b88ae1 | docs: close first continuity step with Windows results and no build |
| cd1ebddf | fix: retain file action while asking for a missing target |
| f66d2694 | docs: record verified missing-target step and next bounded task |
| 2e388d7a | feat: resolve Explorer context for relative file navigation |
| 9e4d09b5 | test: normalize Explorer fixture array and retain native error identifiers |
| d4991313 | test: model selected Explorer items as FolderItem objects |
| 41d132e8 | fix: route console folder navigation before implicit project requests |
| e61346b2 | fix: retain pending project dialog priority at the console gate |
| ba7fe5b2 | test: provide project dialog state to legacy console callback fixture |
| fb993295 | docs: record verified Explorer navigation and next visual-results step |
| 22c8e8d9 | feat: display file results in one selectable window with concise chat |
| d6721801 | feat: make visual result selection fully usable by voice without clicks |
| 26da95d9 | fix: keep incomplete requests ahead of spoken result references |
| 07cbee04 | docs: record voice-first visual results and Windows acceptance |
| 61deabcf | feat: show scoped search progress and precise coverage without spoken lists |

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
