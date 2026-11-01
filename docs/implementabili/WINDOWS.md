# WINDOWS — File, cartelle e programmi scelti
Aggiornato: 2026-11-01. **Stato: requisiti raccolti e fattibilità preliminare; implementazione non autorizzata.** Base b936879a431370d206152be7b089baf587d15499. Priorità rispetto alle altre idee ancora da concordare.

## Criterio confermato dall'utente
Jarvis deve essere il più leggero possibile sul Pavilion i3-2100/10 GB/Windows 10. Prima verificare cosa esiste nel programma e cosa Windows mette già a disposizione; riusare queste capacità quando soddisfano i requisiti. Non è un divieto assoluto di nuove dipendenze: aggiungerle solo quando necessarie o giustificate da un vantaggio concreto, valutando peso, affidabilità, semplicità e manutenzione. La valutazione tecnica spetta all'assistente, senza chiedere all'utente di scegliere librerie/protocolli. Modulo logico .jaddon e dipendenza esterna sono cose distinte: un'add-on può usare solo funzioni Windows e componenti già presenti.

## Risultati richiesti
- Accedere a cartelle, navigarle, cercare un file e aprirlo; anche leggerne il contenuto e spiegarlo nei formati che saranno supportati e verificati.
- Cercare con nome parziale, prefisso, indizi e contesto, anche senza nome esatto: elencare candidati pertinenti e proseguire dalla scelta. Esempio richiesto: «trovami la cartella d'installazione di Minecraft», senza limitarsi al confronto del nome della cartella.
- Rispondere all'ora corrente leggendo l'orologio del PC; requisito espresso nella conversazione, da integrare nel catalogo e verificare.
- Nelle impostazioni scegliere i programmi avviabili; Netflix e WhatsApp sono esempi, non app già verificate sul PC.
- Richiesta precisa riconosciuta localmente senza GPT. Parafrasi/ambiguità interpretate dal GPT esterno se consentito e collegato, poi azione definita validata/eseguita localmente; chiarimento se necessario.
- Le funzioni nuove e i programmi configurati devono comparire nell'elenco aggiornato «cosa puoi fare?» con descrizione; distinguere disponibili e disattivati.

## Cosa esiste già — lettura della base esatta
- local_engine.py: apertura Blocco note, Calcolatrice, Esplora file, C:, Download e browser. _open_app usa subprocess.Popen senza shell; _find_download cerca per nome solo sotto Download, massimo 3000 file esaminati/20 risultati, senza seguire symlink. Non è una ricerca generale su tutto il PC e non apre il risultato selezionato.
- settings.py e punti pertinenti jarvis.py: impostazioni già presenti; nei file letti non esiste un catalogo configurabile di programmi scelti dall'utente. Non presentarlo come disponibile.
- capability_registry.py: catalogo descrittivo e binding locali espliciti. live_capabilities.py: disponibilità corrente e registrazione add-on; catalogo non concede esecuzione arbitraria. LocalEngine.available_commands contiene anche un elenco statico: allineare le fonti quando si aggiungono azioni, non aggiornare solo il testo del modello.
- Percorso voce/GPT e registro già presenti, da estendere e verificare: non ricostruire tutto né presumere che qualsiasi parafrasi sia già gestita.
Queste sono letture del codice, non prove eseguite su Windows.

## Funzioni Windows verificate nelle fonti Microsoft
- [ShellExecute/Ex](https://learn.microsoft.com/en-us/windows/win32/shell/launch): avvio applicazioni/apertura di file con il gestore associato. Riutilizzabile per aprire un risultato e l'app registrata.
- [Get-StartApps](https://learn.microsoft.com/en-us/powershell/module/startlayout/get-startapps): nomi e AppID delle app del menu Start dell'utente. Candidato per popolare la scelta programmi insieme a collegamenti/percorso selezionato, senza promettere inventario universale. Installazione effettiva e avvio di Netflix/WhatsApp da verificare sul PC.
- [Windows Search SQL](https://learn.microsoft.com/en-us/windows/win32/search/-search-sql-windowssearch-entry): interrogazione dell'indice già esistente, compatibile con Windows 10. [Copertura dell'indice](https://learn.microsoft.com/en-us/windows/win32/search/-search-3x-wds-included-in-index): non tutti i contenuti sono indicizzati; filtri/formati incidono sui risultati. Prima verificare servizio e cartelle realmente coperte, senza abilitare indicizzazione globale automaticamente. Alternativa da valutare: ricerca locale su richiesta nelle cartelle scelte con limiti, avanzamento e annullamento.
Non scelto ancora il collegamento tecnico definitivo fra Python e questi servizi. La disponibilità di un servizio Windows non equivale a integrazione già realizzata o a costo nullo.

## Proposta tecnica preliminare e ordine di difficoltà
1. Programmi selezionati nelle impostazioni e apertura file/cartelle note: percorso più circoscritto, candidato iniziale.
2. Ricerca per nome in cartelle concordate, scelta fra risultati e apertura: successiva, con lavoro su HDD limitato alla richiesta.
3. Lettura/spiegazione del contenuto richiesta: progettare per formati esplicitamente supportati; non promettere qualsiasi file. Ricerca e lettura sono attività distinte.
Nessun nuovo modello locale richiesto per le operazioni di apertura/ricerca per nome. Evitare scanner o processi residenti senza necessità; considerare anche il peso dei programmi che l'utente apre, distinto dal costo di Jarvis. Consumo aggiuntivo non misurato, nessuna promessa numerica.

## Questioni da discutere
Chiarito: entrambe le cose, ricerca/apertura e lettura/spiegazione. Non ripetere questa domanda. Restano da concordare ambito delle cartelle e formati iniziali; definire gestione degli omonimi. Avviare un'app è distinto dal controllarne tutte le funzioni interne.

## Prove da progettare prima della consegna
Voce/testo, comando preciso senza GPT e parafrasi col modello simulato/reale distinti; app scelta/disattiva/mancante, percorso cambiato, più risultati, permessi negati, ricerca annullata e catalogo coerente dopo modifiche. Non dichiarare una finestra aperta per il solo invio di un comando; definire osservazione/limiti di verifica. Regressioni pertinenti e pacchetto estratto; prova reale Windows e consumi Pavilion separati. Nessun nuovo test runtime o benchmark svolto in questa discussione.

## Recupero e prossimo passo
Base e ZIP funzionanti preservati: [registro versioni](../../Download/REGISTRO-VERSIONI.md). Quando esisterà una consegna collegare sorgenti, pacchetto/checksum, prove e ritorno versione senza perdita di dati. Ora definire percorso minimo, ambito di ricerca e formati sulla base dei requisiti chiariti; nessuna implementazione avviata.

## Ricerca per significato e indizi — precisazione 2026-11-01
**Requisito:** interpretare cosa vuole trovare l'utente, non richiedere un nome esatto. Windows Search è un candidato per recuperare risultati, non viene considerato da solo una soluzione già verificata di ricerca semantica universale.
**Strategia proposta, da verificare:** comandi precisi al percorso locale; descrizioni non risolte interpretate da GPT esterno consentito. Il motore raccoglie prove reali con ricerca Windows dove disponibile, nomi parziali/prefissi, proprietà e contesto; ricerche mirate nelle cartelle pertinenti dove l'indice non copre. Solo per i formati supportati e quando utile esamina il contenuto richiesto, con limiti di dimensione/tempo; non manda indiscriminatamente cartelle o file interi al modello. Nessun nuovo modello locale o indice semantico residente scelto.
**Esempio Minecraft:** verificare indizi da applicazioni/collegamenti e configurazione del launcher effettivamente presente per distinguere cartella programma, istanza/dati e salvataggi. Non fissare un percorso presunto, non assumere il launcher dalla memoria della chat. I candidati devono avere percorso esistente e motivazione osservabile; se più installazioni plausibili, chiarimento breve nel contesto.
**Risposta utile:** nome/percorso e ragione sintetica della corrispondenza; distinguere risultato verificato da candidato. «Non trovato nell'ambito esaminato» non significa che il file non esiste sul PC. Senza nome né indizi sufficienti chiedere un dato concreto (tipo, argomento, periodo o posizione) anziché inventare. Consumo ricerca da misurare: lavoro su richiesta, limiti, avanzamento/annullamento; nessuna scansione continua promessa o introdotta.
**Accettazione da aggiungere:** prefisso e sottostringa, descrizione senza nome, file in cartella pertinente con nome diverso, indice incompleto, launcher multipli, dati/programma distinti, nessun risultato e lettura del formato non supportato. Simulazioni e prove reali separate; nessun test eseguito in questa fase.

## Guida durante la discussione
L'utente richiede spiegazioni semplici e orientamento, un punto e una domanda alla volta. Presentare cosa esiste, cosa proponiamo e cosa resta da verificare; non comunicare solo «ho controllato». Lasciare terminare il discorso, non trasformare piccole pause in una domanda chiusa o nell'autorizzazione a procedere.

## Piano di lavoro proposto — prove prima delle dichiarazioni
Richiesto dall'utente il 2026-11-01. Stato: **piano da discutere, non implementazione avviata**. Ordine tecnico proposto, da allineare alle priorità dell'utente.

### 1. Inventario mirato e responsabilità delle funzioni
Sulla base preservata b936879 verificare azioni, gestori, impostazioni e test pertinenti: local_engine, capability_registry, live_capabilities, action_planner, voce/testo, moduli documenti e jarvis.py. Tabella da produrre: requisito → funzione esistente → limite dimostrato → modifica minima → test. Migliorare il componente già responsabile: niente secondo cercatore, lanciatore o lettore parallelo. Un nuovo componente .jaddon è giustificato solo per capacità nuova o necessità motivata, senza duplicare percorsi utente. La ricerca estesa deve evolvere quella esistente.
**Uscita:** punti di integrazione e lacune verificati nel codice, distinguendo presenti/da estendere/nuovi. Inventario iniziale presente sopra; moduli documenti e integrazione complessiva non ancora riesaminati per questo piano.

### 2. Scegliere e provare il collegamento Windows minimo
Dopo il via al lavoro tecnico preparare prova limitata in ambiente Windows disponibile: apertura di file/cartella nota con strumenti nativi, individuazione/avvio app di prova; per la ricerca controllare servizio Windows Search e risultati su campioni noti, inclusa cartella non indicizzata. Definire l'integrazione Python concreta solo dopo questa verifica; confronto mirato con alternative già disponibili se serve. Documentazione Microsoft già consultata, collegamento Jarvis non ancora provato.
**Uscita:** percorso reale verificato oppure errore/dipendenza/limite registrato. Se una prova fallisce, fermare il lavoro che ne dipende. Nessuna nuova dipendenza adottata per ipotesi e nessuna indicizzazione completa del disco attivata automaticamente.

### 3. Migliorare un percorso minimo completo
Dopo autorizzazione, primo incremento circoscritto proposto: apertura programma selezionato nelle impostazioni, da voce/testo all'azione locale e alla risposta, usando il gestore esistente esteso. Ora/data dal PC come azione locale circoscritta se scelta per il primo incremento. Configurazione persistente, disponibilità e «cosa puoi fare?» alimentati dalla stessa fonte, senza aggiungere liste parallele. Comandi precisi senza modello; frase non risolta al GPT esterno consentito; chiedere se ambiguo.
**Uscita:** app disponibile individuata correttamente, azione eseguita e riscontro con limiti dichiarati; disattivata/mancante gestita senza falso successo. La conferma di avvio Windows non è prova di tutte le funzioni interne dell'app.

### 4. Estendere ricerca e lettura esistenti per incrementi
Prima nomi parziali/prefissi in ambito concordato; poi descrizioni/indizi con candidati motivati e verifica locale, es. cartella Minecraft distinguendo installazione, dati e salvataggi. Infine lettura/spiegazione nei formati iniziali concordati, riusando prima i moduli documenti presenti. Per file senza nome esatto recuperare indizi reali: il modello non inventa percorsi e non trasforma un candidato in risultato verificato. Windows Search dove adatto, ricerca mirata dove necessario, senza scansioni continue.
**Uscita di ogni incremento:** prova con campioni controllati più casi di ambiguità, assenza risultati, limiti indice/permessi e formato non supportato. Lettura e spiegazione provate separatamente dall'apertura. Nessuna garanzia di trovare un file senza alcun indizio.

### 5. Verifica, consegna e ritorno alla versione precedente
Test automatici significativi sui componenti modificati e regressioni pertinenti: voce/testo, GPT simulato e reale distinti, nessuna doppia esecuzione, aggiornamento catalogo, ricerca annullata/timeout, dati preservati. Verificare pacchetto estratto e CI Windows disponibile; sul Pavilion account/app reali, usabilità e misura RAM/CPU/disco comparabile (inattivo, attività, fine). Conservare comando/ambiente/esito/limiti; saltato non equivale a riuscito.
**Uscita:** pacchetto persistente e checksum, sorgenti identificati e link Download verificato; prova PC collegata alla versione e all'ambito realmente testato prima di promuovere il nuovo riferimento funzionante. Fino ad allora mantenere la base confermata e il relativo ZIP.

### Punto di arresto del piano
Ora sono svolte soltanto letture mirate di codice/fonti e documentazione dei requisiti. Nessuna prova nuova di integrazione Windows, benchmark, implementazione o pacchetto. Prossimo passo: spiegare e discutere il piano con un esempio concreto; definire ambito cartelle e formati prima delle relative fasi. L'approvazione del criterio non equivale al via automatico a tutte le fasi.

## Organizzazione dei file richiesta dall'utente
Ogni nuova add-on/modulo aggiunto deve essere riconoscibile con una propria cartella e file pertinenti, così l'utente può ispezionarlo manualmente. Proposta indicativa: cartella dal nome chiaro, LEGGIMI.md iniziale, codice/risorse e test del componente; manifest e configurazione identificati nel LEGGIMI con percorso reale. La struttura esatta va verificata col gestore .jaddon esistente e col pacchetto; non è già implementata.
Nel LEGGIMI spiegare cosa fa il componente, file principali, configurazione/dati, dipendenze, test e recupero. Riutilizzare documentazione comune tramite link. Non copiare dati personali o configurazioni in due posti per ottenere una cartella apparentemente completa: il profilo dati esistente può avere una cartella dedicata, esplicitamente indicata. Durante la fase 1 verificare quali file siano già responsabilità del nucleo e quali siano davvero del componente. Migliorare funzioni esistenti senza duplicarle; un eventuale riordino del codice attuale richiede verifica di import, avvio, test e pacchetto. Nessun file runtime spostato in questa fase documentale.

## ZIP operativo essenziale e recupero del metodo
Requisito dell'utente: consegna con i soli file necessari per installare/configurare/usare Jarvis. Applicare la regola di selezione in AGENTS, controllando dipendenze reali, launcher, risorse e diagnostica; sorgenti .py/.mjs eseguiti direttamente sono file operativi. Guide/handoff/test/CI di sviluppo rimangono nella repository, salvo componenti realmente necessari al funzionamento distribuito. Testare lo ZIP estratto; preservare base e pacchetti storici.
**Riscontro sul publisher della base:** .github/workflows/publish-audit-zip.yml usa git ls-files, esclude soltanto i vecchi ZIP Download e richiede oltre 110 file. Include quindi materiale del repository non selezionato per necessità runtime. È evidenza dal codice, non una nuova compilazione; modifica del publisher da progettare per il prossimo pacchetto autorizzato, senza alterare lo ZIP confermato.
Ogni istanza con accesso repo deve recuperare AGENTS/RECUPERO/handoff e questa scheda prima del lavoro; niente garanzia di accesso o recupero automatico in una chat esterna. Nessuna ripacchettizzazione o cancellazione eseguita in questa discussione.

## Istruzioni essenziali e dipendenze mancanti nella console
Requisito aggiunto: ZIP con istruzioni d'installazione/configurazione essenziali e indicazione delle add-on/componenti da scaricare quando non distribuite. Jarvis deve segnalare in console il nome esatto del componente mancante, funzione bloccata, rimedio concreto e fonte di scaricamento verificata quando necessaria. Per file interni: percorso atteso e pacchetto da reinstallare. Distinguere mancanza da configurazione/permessi/versione incompatibile; dopo il rimedio ricontrollare senza scansioni continue.
**Lettura concreta b936879:** installa_telegram.bat installa Telethon>=1.36,<2 con pip e segnala FFmpeg nel PATH per note OGG/Opus. telegram_voice.py ha già missing_voice_dependencies per FFmpeg/SAPI e rilevatori Vosk per trascrizione. Migliorare/collegare questi controlli alla console, senza duplicarli. Nessuna prova d'esecuzione fatta ora; copertura unificata di tutte le dipendenze e link aggiornati ancora da verificare. I link concreti vanno ricavati dalle fonti ufficiali per versione/architettura compatibili quando si prepara la consegna, non inventati o dichiarati già configurati.
**Test da aggiungere al piano:** add-on/file/dipendenza assenti, versione errata, accesso negato, rimedio mostrato coerente e ricontrollo dopo ripristino. Assenza di componente opzionale non deve bloccare funzioni indipendenti. Nessun nuovo controllo implementato in questa fase.
