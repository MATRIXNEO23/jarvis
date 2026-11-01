# Istruzioni persistenti — Jarvis

## Avvio e recupero automatico del contesto di sviluppo
All'avvio di una sessione con accesso a questo repository, prima di proporre o implementare lavoro leggere RECUPERO.md e seguirne l'ordine di lettura. Recuperare autonomamente handoff, indice, lezioni e piano pertinente senza chiedere all'utente di ricostruire la storia. Verificare lo stato con il codice corrente; non dichiarare recupero completo se le fonti non sono accessibili.

## Continuità a ogni modifica
Ogni modifica di codice/configurazione e ogni decisione che cambia il lavoro deve essere accompagnata da aggiornamento di handoff e stato attività prima di considerare il lavoro concluso. Raggruppare edit correlati in un checkpoint coerente prima del commit e aggiornare dopo test, fallimenti e prima di ogni pausa. Documentare le motivazioni tecniche e le lezioni pertinenti nel registro. Per scritture via API con commit per file, completare gli aggiornamenti in sequenza. Non serve un commit ricorsivo per annotare il proprio SHA: è recuperabile da Git.
Se una richiesta è incompatibile con il sistema, non eseguirla alla cieca: spiegare il conflitto dimostrato e proporre alternative concrete, distinguendo fatti da ipotesi. Non aggiungere funzionalità non richieste; lasciare all'utente obiettivi e compromessi.

## Decisioni, risultati ed errori
Dopo ogni fase significativa aggiornare docs/DECISIONI-E-LEZIONI.md e il documento di handoff con problema, decisione, motivazione tecnica sintetica, prove osservabili, commit, workflow, risultato e questioni aperte.

Promuovere a riferimento soltanto soluzioni verificate, indicando ambito e limiti del collaudo. Un test locale non prova il funzionamento del modello esterno o dell'hardware Windows.

Un approccio fallito va scartato dalle soluzioni raccomandate: indicare causa, prova del fallimento e condizione necessaria per rivalutarlo. Conservare una scheda diagnostica minima per non ripetere l'errore; non cancellare log utili, cronologia, pacchetti precedenti o dati utente. Una nuova prova può correggere una conclusione precedente: registrare il superamento senza riscrivere i fatti.

Non limitarsi a un elenco di comandi: spiegare il nesso tecnico tra problema, scelta e risultato con evidenze riproducibili. Distinguere fatti dimostrati, ipotesi e attività non eseguite. Non salvare credenziali o conversazioni personali nei registri.

## Vincoli
- Zero costi aggiuntivi e nessuna API a consumo.
- Archify è uno strumento di sviluppo, mai componente di Jarvis.
- Continuità conversazionale nel nucleo; nuove funzionalità come add-on salvo necessità motivate.
- Preservare impostazioni, salvataggi e controllo manuale microfono; standby all'avvio secondo handoff.
- Non pubblicare pacchetti difettosi o dichiarare test senza prove.
- Le modifiche del nucleo conversazionale proposte nel rapporto del 31 ottobre richiedono l'approvazione del piano già richiesta dall'utente. Il fix CI faba673 è autorizzato e verificato.

## Sorgenti e continuità
Main contiene il catalogo Download e sorgenti storici alla radice. Il ramo feature/timer-settings-ui-20261031 contiene l'app evoluta: verificare sempre SHA, ramo, diff e workflow prima di intervenire. Non sostituire in blocco la radice main per correggere un test.

Handoff autorevole: docs/HANDOFF-CODEX-ARCHIFY-20261031.md su main. Rapporto: docs/DIAGNOSI-ARCHIFY-DIALOGO-20261031.md su main.

## Procedura obbligatoria prima e durante ogni modifica
Richiesta dell'utente del 2026-11-01: la memoria di sviluppo risiede nel repository e deve essere consultata; il solo contesto della chat non basta.

1. Prima di implementare leggere queste istruzioni, l'handoff autorevole, docs/DECISIONI-E-LEZIONI.md e il piano pertinente. Verificare ramo, SHA, diff, file effettivi e prove disponibili; i documenti possono essere superati. In caso di divergenza annotarla e verificarla, senza inventare lo stato.
2. Esaminare ciò che esiste già e i punti di integrazione: nucleo, capacità, altre add-on, impostazioni, memoria, microfono e modello esterno. Non creare un duplicato di una funzione senza una necessità dimostrata.
3. Preparare un piano per fasi con obiettivo, interventi, dipendenze, test significativi, risultato atteso e procedura di recupero. Segnalare ipotesi, dati mancanti e possibili modifiche del nucleo. Per l'add-on web l'utente ha chiesto di discutere prima di creare: non avviare l'implementazione finché non autorizzata.
4. Procedere per fasi controllate. Dopo un fallimento non proseguire con attività che dipendono dal risultato fallito. Conservare riproduzione, causa dimostrata oppure ipotesi esplicita, correzione e prova successiva.
5. Aggiornare piano, handoff e registro dopo ogni fase significativa e prima di interrompere il lavoro: stato proposto/in corso/verificato/fallito/non eseguito, file interessati, motivazione tecnica sintetica, risultati attesi e osservati, comando e ambiente di prova, commit/workflow, limiti e prossimo passo preciso.
6. Riutilizzare soluzioni riuscite solo nell'ambito verificato. Escludere quelle fallite dalle raccomandazioni, conservando una nota minima su errore e lezione. Registrare perché una nuova prova supera una vecchia conclusione. Salvare motivazioni tecniche ed evidenze riproducibili, non un flusso di ragionamento privato.
7. Nessuna dichiarazione di successo senza prova; distinguere test simulati, osservazioni passive, test reali e riscontri riferiti dall'utente. Un aggiornamento documentale non equivale a implementazione o test dell'app.

## Regole add-on e piano web
Per questa e le future add-on pianificare cartella e configurazione separate, compatibilità, contenimento degli errori, versioni precedenti e recupero senza perdita di dati. Le cartelle da sole non isolano i guasti. Migrazione dei componenti esistenti soltanto dopo valutazione.
UI semplice e coerente in Impostazioni > Add-on: nome, descrizione, Attivo/Disattivato, stato, Configura; opzioni meno usate distinte. Azioni separate «Ripristina impostazioni iniziali dell'add-on» e «Torna alla versione precedente», con effetti espliciti e dati utente preservati.
Errori visibili nella chat con fase e azione utile; dettagli tecnici consultabili senza credenziali o conversazioni private. Valutare autoverifiche finite nel programma, senza analisi continua o promesse di diagnosi universale.
Piano attuale: docs/PIANO-ADDON-WEB-E-DIAGNOSTICA-20261101.md. GPT resta esterno; add-on web su richiesta, priorità al basso consumo aggiuntivo. Estensione Edge proposta, cartella finale concordata Estensione-Edge; tecnologia e prestazioni ancora da validare.

## Collaborazione con l'utente
L'utente decide risultati desiderati, priorità e compromessi; lo sviluppo è responsabilità dell'assistente. Non richiedere all'utente di programmare, progettare protocolli o scegliere dettagli tecnici che si possono verificare autonomamente. Proporre soluzioni motivate e svolgere analisi, implementazione autorizzata, test, pacchettizzazione e aggiornamento documenti. Per operazioni inevitabili sul PC dell'utente dare istruzioni brevi, una alla volta, e spiegare cosa osservare. Per rispettare la preferenza di accessibilità comunicativa espressa, usare poche scelte concrete, linguaggio semplice e riepiloghi brevi; evitare domande ripetute o richieste di conferma per ogni dettaglio. La conferma del piano richiesta per l'add-on web non va estesa a ogni micro-passaggio del piano già autorizzato.

## Continuità tra argomenti
Prima di riprendere un'attività consultare docs/STATO-ATTIVITA.md e i documenti collegati, poi verificarli rispetto alle fonti correnti. Quando si cambia argomento, lasciare per quello sospeso obiettivo, requisiti confermati, decisioni, fase, prove, dubbi e prossimo passo. Alla richiesta «torniamo a...» recuperare quei dati senza ricominciare o ripetere domande risolte. Non equiparare una proposta salvata a un'approvazione o un'implementazione. L'indice orienta, non sostituisce la lettura delle fonti.

## Handoff continuo anche in caso di interruzione
Non attendere una richiesta «fammi l'handoff» o la fine del turno. Prima di ogni unità coerente di modifica salvare nell'handoff attività in corso, punto di partenza, file previsti e prossimo controllo; subito dopo salvarne esito, file effettivi e test ancora da eseguire. Aggiornare di nuovo dopo i test e le correzioni. Preferire checkpoint piccoli e codice/documentazione nello stesso commit dove possibile; una serie di edit strettamente correlati costituisce una sola unità, non un salvataggio per ogni carattere. Se si interrompe fra scritture, la sessione seguente deve confrontare il checkpoint in corso con diff, commit e file reali prima di proseguire. Non promettere copertura di modifiche non ancora salvate o interruzioni durante una scrittura.

## Revisione preventiva finita e apprendimento dagli errori
Prima del codice preparare il progetto e rivederlo con i dati reali: requisiti, integrazione con ciò che esiste, dipendenze/compatibilità, risorse, stati di errore, recupero e test di accettazione. Consultare solo le lezioni pertinenti al cambiamento. Segnalare problemi dimostrati, ipotesi e prove mancanti; correggere il progetto prima di implementare.
Ciclo ordinario: una revisione iniziale e un ricontrollo mirato delle sole correzioni. Se resta una criticità bloccante, documentarla e proporre una scelta o una prova di fattibilità limitata prima di proseguire; non ripetere revisioni globali all'infinito e non far passare un blocco per rispetto del limite. Nuovi dati o variazioni di ambito possono giustificare una nuova revisione, esplicitandone il motivo.
Dopo autorizzazione costruire e verificare prima il percorso minimo completo e poi aggiungere le parti successive: non attendere la build finale per scoprire che i componenti non comunicano. Eseguire i test pertinenti; ripeterli/ampliarli solo per modifiche, fallimenti o dubbi irrisolti. La revisione del progetto non garantisce l'assenza di errori runtime.
Per un errore reale registrare sintomo, riproduzione, evidenza, causa dimostrata o ipotesi, soluzione verificata, ambito/limiti e regola preventiva. Quando utile aggiungere un test di regressione significativo o un controllo mirato; non creare test che rispecchiano banalmente il codice o ripetono altri test senza beneficio. Una soluzione non verificata resta proposta. Prima di un lavoro simile applicare la lezione pertinente, senza rileggere o ricontrollare ogni volta tutto il progetto.

## Test automatici per ogni add-on prima della consegna
Ogni nuova add-on deve includere test automatici propri, significativi e riproducibili nel repository, integrati nei controlli di progetto prima della prova sul PC utente. Verificare comportamento e integrazione reale dove possibile: contratto/registro capacità, dialogo col nucleo e con eventuale estensione, gestione errori e timeout, disattivazione, configurazione e recupero. Test simulati e test con componenti reali vanno distinti.
Eseguire i controlli applicabili nel repository/CI disponibile prima della consegna, compresa la suite pertinente di regressione Jarvis e la verifica del pacchetto estratto. Non considerare riuscito un controllo obbligatorio saltato o non disponibile: documentare il blocco e non presentare il pacchetto come pronto. Non delegare all'utente debug di collegamenti o errori che sono riproducibili in sviluppo.
Sul Pavilion restano verifiche dipendenti dall'ambiente personale (account reale, dispositivi, browser installato, prestazioni e usabilità). I test automatici riducono i guasti, non garantiscono assenza di ogni bug. Per le add-on esistenti inventariare prima copertura e lacune; non dichiarare che abbiano già tutti questi test.

## Ambito concordato e completezza vocale delle add-on
Limitarsi all'obiettivo concordato. Presentare eventuali funzioni extra come proposte prima di implementarle; non introdurle di propria iniziativa né farle comparire a sorpresa nella build. Distinguere una nuova funzione di prodotto dai dettagli tecnici necessari a realizzare quanto già autorizzato; non chiedere conferma per ogni dettaglio ordinario.
Ogni add-on deve essere progettata come percorso completo: frase naturale al microfono → trascrizione → interpretazione GPT esterna con stato dell'attività → capacità/azione registrata e disponibile → esecuzione locale → verifica dell'effetto → risposta comprensibile. Prima della consegna verificare anche voce e testo, esempi dei comandi, varianti pertinenti, chiarimenti brevi e comportamento attivo/disattivo. Non dichiarare completa una funzione solo perché il suo pulsante o modulo funziona.
Aggiornare registro delle capacità, catalogo/esempi dei comandi e UI coerentemente con ciò che è realmente disponibile. Un add-on disattivato non deve essere presentato come utilizzabile; una richiesta valida non deve finire in «comando mancante» per un collegamento dimenticato. Il modello esterno resta responsabile dell'interpretazione; i validatori locali controllano le azioni definite.
Separare prove dei callback con trascrizione simulata, prove del riconoscimento con campioni audio quando disponibili e prova del microfono/account reali sul PC. Non attribuire a una simulazione copertura del microfono reale. Le prove riproducibili restano responsabilità dello sviluppo.

## Linguaggio naturale e risposta sulle capacità
Gli esempi dei comandi sono suggerimenti, non formule obbligatorie. La richiesta vocale deve essere interpretata semanticamente dal GPT esterno con il contesto; evitare che un mancato abbinamento letterale locale impedisca al modello di interpretare una richiesta supportata. Chiedere chiarimenti quando mancano dati necessari o l'intento resta ambiguo, senza inventare dettagli. Mantenere controlli locali sulle azioni e non ampliare le capacità in base alla sola formulazione.
«Cosa puoi fare?» e la lista dei comandi devono usare la stessa fonte delle capacità realmente disponibili, aggiornata dopo installazione, aggiornamento, attivazione, disattivazione e rimozione delle add-on. Distinguere installato da attivo e utilizzabile; non promettere funzioni mancanti. Testare parafrasi equivalenti, richieste incomplete, chiarimenti e coerenza dell'elenco con lo stato effettivo.
