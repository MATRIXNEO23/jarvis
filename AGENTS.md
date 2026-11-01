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
