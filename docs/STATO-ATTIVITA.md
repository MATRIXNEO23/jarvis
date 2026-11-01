## Passo 2 in attesa Windows — richiesta senza nome
Sorgenti cd1ebddf566b99df6046a51c78e4e5370ff0c8dc, base 75b88ae. Implementato percorso «apri una cartella» → domanda nome/percorso → risposta → apertura/ricerca conservando azione e tipo. _pending esistente distingue nome mancante da scelta fra candidati; niente nuovo motore/memoria/modulo. Il raccordo GPT già presente conserva una richiesta esplicita incompleta, non usa la risposta del modello come autorizzazione. Nuovi test anche sul corpo effettivo del callback GPT con reply controllato. Numeri senza elenco, chat e nuovi comandi non diventano nomi ipotizzati; scadenza, revoca, annulla e scelta accodata/replay ricontrollati. Cinque prove nuove, esito ancora da acquisire su Windows run 41334831954. Nessuna build, prova Linux o navigazione Explorer personale.
Prossimo controllo unico: esito CI della run; se fallisce, correggere solo il difetto prima di incrementi dipendenti. Nessun elenco al TTS: nuova UI visuale dedicata ancora da fare. Dettagli [rapporto del passo 2](ACCESSO-FILE-PASSO2-CHIARIMENTO-20261101.md). Non unire a questo passo programmi, processi, browser o scansioni lunghe.

## Passo 1 verificato — 2026-11-01
Sorgenti dcc4aebcee02bfb19862b2e215ee6be42aab6982, CI Windows [41333993279](https://github.com/MATRIXNEO23/jarvis/actions/runs/41333993279) SUCCESS: 409 test per job Python 3.11/3.12 (job 124929816594 e 124929816680), zero errori/fallimenti; sintassi e probe Windows PASS. Build, verifica ZIP estratto, upload artifact e publisher SKIPPED come richiesto. Nessun test Linux, nessuna nuova build.
Ambito verificato: nome esatto fra candidati di open/read pendente riprende la richiesta; omonimi chiedono numero, scelte vecchie o ripetute non riaprono; callback effettivo con trascrizione controllata e directory reali Windows. Avvio Explorer intercettato dal test: non prova della finestra/microfono/GPT personali. Primo fallimento sul confronto DOS/lungo superato usando identità reale della directory nel test; runtime invariato nel ricontrollo.
Passo chiuso e recuperabile. Requisito obbligatorio: nessun elenco lungo pronunciato, risultati in finestra dedicata scorrevole/selezionabile ancora da implementare. Prossimo passo breve da riprendere: completare la domanda di apertura senza elenco e il contesto relativo secondo il piano, poi finestra risultati; non accorpare programmi, processi e browser. Presentare risultati prima della decisione sulla build; nessuna richiesta automatica di build.


## Diagnosi e ricontrollo del primo passo
Prima esecuzione cf0c33c, run 41333821126: 409 test Windows, un solo fallimento nella nuova asserzione che confrontava forma lunga e alias DOS dello stesso percorso; il target della richiesta era corretto. Job 124929307811, AssertionError sul profilo lungo vs RUNNER~1. Correzione limitata al test: os.path.samefile verifica la directory effettiva invece del testo del percorso; nessuna modifica al runtime della correzione. Sorgenti successivi dcc4aebcee02bfb19862b2e215ee6be42aab6982, run 41333993279 ancora in attesa. Nessuna build. La verifica della run fallita non è presentata come successo.
Prossimo controllo unico: leggere l’esito della run del commit dcc4aeb; se verde registrare conteggi, zero errori e build/publisher skipped, poi chiudere questo passo senza passare automaticamente alla navigazione. Nessun nuovo test Linux.


Requisito obbligatorio ribadito: nessun elenco di file/cartelle/finestre/programmi/processi viene inviato alla sintesi vocale, indipendentemente dal numero di elementi. Voce per spiegazioni e domande brevi; risultati in finestra dedicata scorrevole/selezionabile (da implementare), con caricamento progressivo per elenchi grandi. La correzione già presente separa messaggio chat da spoken_message e non legge liste file; non dichiarare già presente la nuova finestra. Accettazione futura: lista molto grande non accoda nomi/percorsi TTS e lascia disponibili i comandi; spiegazioni richieste restano vocali.

## Checkpoint corrente — primo passo continuità, test Windows in attesa
Autorizzati da chiamata e «Continua» implementazione mirata e test, con risultati prima di decidere la build. Preferenza ribadita: passi brevi indicativamente 5 minuti, aggiornamenti entro un minuto; se CI supera il blocco, salvare attesa e prossimo controllo senza tenere aperta una lavorazione indefinita. Chiusura app già concordata anche per finestre aperte manualmente, purché autorizzate; non ripetere la domanda.
Primo incremento implementato in feature/file-access-20261101, sorgenti cf0c33c965f9ad5ed6706127aa97c93212db1255: nome esatto fra risultati di open/read pendente riprende la stessa azione, senza nuova ricerca. Riusa service/select e callback UI già presente, nessun modulo aggiuntivo. Nome duplicato richiede numero; scadenza, revoca, annullamento e sostituzione elenco non riutilizzano la vecchia azione; replay non riapre. Sei regressioni nuove con directory reali e callback effettivo controllato. Esito Windows ancora pendente, nessuna nuova build o test Linux. Dettagli e prossimo controllo in [rapporto del passo](ACCESSO-FILE-PASSO1-CONTINUITA-20261101.md). Restano distinti domanda GPT senza elenco, cartella Explorer corrente, UI risultati, ricerca lunga, programmi/processi/schede.

## Punto vigente — progetto rivisto e checkpoint di ripresa, 2026-11-01
Richieste confermate: partire dallo stato reale e requisiti del Pavilion, ottimizzare/semplificare, review prima del codice e test automatici prima delle prove manuali; aggiornare stato prima/dopo ogni unità e dopo ogni test. Le regole esistenti di handoff continuo restano operative.
Riferimento sorgenti verificato: feature/file-access-20261101 HEAD 87006ee4b7abf747512a54c684fff09f244d6696 (base PC b936879 preservata). [Progetto e review](PROPOSTA-FILE-PROGRAMMI-20261101.md), sezione iniziale: lacuna scelta per nome, azzeramento nel callback UI, differenza domanda GPT/azione pendente, scadenza/nuovi argomenti e singola esecuzione.
**Fase chiusa:** revisione statica iniziale del primo incremento, requisiti e matrice di accettazione conservati. **Non eseguiti:** implementazione, test runtime Windows/Linux, misura consumi, build e pubblicazione pacchetto. Workflow letto: Windows 3.11/3.12 per test; build solo dispatch esplicito.
**Prossimo passo preciso:** correzione del percorso richiesta di apertura → scelta ambigua → risposta col nome/numero → stessa apertura, riusando servizio e raccordi voce/testo; poi CI Windows prima di procedere alle fasi dipendenti. Non ricominciare inventario/base o ripetere domande risolte. Nuove build solo su richiesta esplicita.
Alla ripresa verificare checkpoint, ref e diff prima di agire: operazioni interrotte prima del salvataggio non sono garantite recuperabili.

## Punto vigente — studio continuità e navigazione semplice, 2026-11-01
Requisiti e piano aggiornati in [proposta FILE-PROGRAMMI](PROPOSTA-FILE-PROGRAMMI-20261101.md), sezione iniziale. Risolto il dubbio: chiusura normale anche di finestre aperte manualmente, soltanto per app consentite. Finestra risultati dedicata/silenziosa, cartella attiva e navigazione relativa, finestre/programmi/processi/schede, ricerca completa tracciabile e configurazioni AppData richieste; integrazioni ancora da verificare.
Studio statico del servizio esistente (service.py blob 2f4255589afc3dd6e08d8111421527b563549bbc): l'azione pendente viene ripresa da selezione numerica, manca equivalente per solo nome cartella. Resolver installazione separato e limitato. Compatibile col sintomo, non diagnosi del singolo payload/microfono sul PC.
Prossimo passo: progetto mirato e prove previste del flusso «apri → quale? → nome → apertura», riusando il servizio; poi cartella Explorer corrente. Nessuna nuova modifica runtime, suite o build in questo studio; build solo su richiesta esplicita. Le vecchie domande sulla chiusura sotto sono superate.

## Stato vigente — proposte e nessuna build automatica
L’utente ha fermato le build automatiche e chiede prima proposte per navigazione Explorer e programmi con spunte di apertura/chiusura. Workflow sorgente corretto nel commit 87006ee4b7abf747512a54c684fff09f244d6696: su push soltanto test Windows; archivio/pubblicazione solo con workflow_dispatch e build_candidate=true dopo richiesta esplicita. Nessuna nuova funzione di navigazione, ricerca contenuto o gestione programmi consegnata. Editing preliminare navigazione conservato come patch NON TESTATA, rimosso dal runtime. Leggere [proposta](PROPOSTA-FILE-PROGRAMMI-20261101.md) e [checkpoint](ACCESSO-FILE-CORREZIONI-20261101.md). Prossimo passo: discutere la proposta e chiarire se chiusura vale solo per finestre aperte da Jarvis o anche manualmente. Nessuna build da avviare.

# Stato attività Jarvis

## Ripresa verificata — nessun lavoro di build ancora in corso
Build candidata Accesso file 7298fb6 pubblicata; verifica live della run 41322290359: tre job completed/success, ZIP presente. Ripresa del contesto effettuata dalle fonti repository senza ricostruzione a memoria. Prossimo step: prova PC, iniziando soltanto dal download/estrazione in cartella nuova. Metodo aggiornato su richiesta: passi brevi con obiettivo, verifica e checkpoint persistente; niente nuova compilazione o modifica runtime da questa segnalazione. Base PC b936879 preservata.

## Stato vigente — primo incremento Accesso file consegnato come candidato Windows
Sorgenti esatti 7298fb632cd9b72386fd7a30f469b307ce7e6fa5; [ZIP candidato](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Accesso-File-0.1.0-20261101-7298fb6.zip), 249396 byte/78 file, SHA-256 72c6d57a9a258fe7c875cfdc8646bc4ddf5b75417aa748bb5d4d4b7ef3e96755. [CI Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/41322290359): 393 test per job Python 3.11/3.12, zero skip; 20 test dal pacchetto estratto, import e avvio/chiusura/rilascio directory PASS. Pubblicazione in Download e metadati remoti verificati, collegamento HTTP 200 con dimensione corretta.
[Rapporto](ACCESSO-FILE-RAPPORTO-20261101.md) e [metadati](evidence/accesso-file-build-20261101.json). Ramo sorgenti feature/file-access-20261101, runtime 7298fb632cd9b72386fd7a30f469b307ce7e6fa5; niente merge massivo su main e nessun cambio implicito del nucleo/microfono. Prossimo passo: l’utente configura una cartella e prova il candidato sul Pavilion, poi si registra versione e ambito verificato. Base confermata b936879 preservata; nessuna promozione senza prova PC. Indice non disponibile nel runner, fallback provato; GPT/microfono reali e consumi ancora da misurare. Le vecchie fasi in corso sotto sono cronologia.

## Attività vigente — implementazione fino alla build testabile, Windows soltanto
Autorizzazione utente acquisita. Sorgenti in feature/file-access-20261101 dalla base b936879; recuperare docs/ACCESSO-FILE-STATO.md di quel ramo. Probe Windows avviato con commit 7955efe/run 41319370085; integrazione e pacchetto ancora in corso, nessuna consegna nuova. Niente nuovi test Linux: richiesta esplicita salvata in AGENTS. Restano invariati zero costi extra, riuso Jarvis/Windows, add-on leggibile e versione PC preservata.

## Metodo vigente — documentazione sempre recuperabile dalla repository
Precisazione dell’utente incorporata in AGENTS/RECUPERO/handoff/lezioni: copie temporanee non sostituiscono conservazione remota di scelte, motivazioni, errori, prove, correzioni e prossimo passo. Nessuna fase dichiarata conclusa senza pubblicazione e verifica della relativa documentazione. Solo chiarimento del metodo; priorità accesso file e prova nativa Windows immutate.

Aggiornato il 2026-11-01 dopo «Procediamo col prossimo passo»: completati inventario/contratto e revisione iniziale accesso file; nessun runtime/ZIP nuovo. Cronologia e audit della base conservati sotto; il punto vigente è la sezione seguente.

## Punto vigente — accesso file, prossimo passo tecnico completato
Pubblicazione documentazione/evidenze su main completata nel commit b58ee03c5aef261fcdec45e0e3b8092cc80bd8ff, con ref e tre contenuti principali riletti e coincidenti, tree identico al locale; esplicitamente autorizzata dall’utente con «Certo che può pubblicare»; chiarita prima la differenza fra checkout temporaneo della sessione e repository GitHub. Non ripetere la richiesta di consenso. Nessuna modifica runtime autorizzata da questa pubblicazione. L’utente chiede domande brevi con opzioni quando resta un dubbio sostanziale; regola salvata in AGENTS.
[Contratto e revisione](implementabili/ACCESSO-FILE-CONTRATTO.md) collegati alla scheda WINDOWS e all'indice. Verificati i 14 sorgenti pertinenti della base b936879; 88 regressioni OK senza skip e 5 osservazioni locali riprodotte su Linux/Python 3.12.14. Non sono test di una nuova add-on o prove Windows. Rilevate le estensioni necessarie a gestore parametrico, dispatcher, policy unica e risposta breve contestuale; codice separato per responsabilità pianificato. Sistema di spunte approvato, scritture/cancellazioni escluse dal primo incremento.
Precisazione dell'utente incorporata: i suoi esempi descrivono la funzione finale; architettura semplice proposta dall'assistente. Riuso Jarvis/Windows, moduli soltanto per lacune reali; nessun nuovo schema/framework o numero di file fissato senza prova di necessità. Prossimo passo preciso: prova Windows circoscritta di profilo/volumi/percorsi reali e Search, poi primo percorso completo sulla base in ramo separato. Test di accettazione e limiti nel contratto. Nessuna installazione, nuova build o cambio del riferimento funzionante; browser sospeso. I successivi «prossimo passo corrente» e «primo incremento app» storici sono superati da questo punto.

## Punto di partenza certo
**BASE-UTENTE-20261101:** Jarvis-Timer-Audio-Fix2-20261031.zip, sorgenti b936879a431370d206152be7b089baf587d15499. L'utente conferma la build attualmente usata; l'audit ha verificato ZIP reale, 155 file contro sorgenti, riproduzione byte-identica e test inclusi.
[Registro con download/checksum](../Download/REGISTRO-VERSIONI.md) · [rapporto e log](VERIFICA-CONCRETA-BASE-20261101.md).

| Attività | Stato reale | Prova e prossimo passo |
|---|---|---|
| Audit della base | Completato | 373 test locali OK, 5 skip Windows; sintassi PASS; CI storica Windows/Linux riletta e codice coincidente |
| Identificazione sorgenti | Completata | Tutti i 155 file uguali a b936879; non al ramo successivo 5e61e53 |
| Guide e riferimenti | Allineamento alla base b936879 | [Prima-installazione](../Prima-installazione/README.md); separati avvio auto_listen della base e standby del ramo successivo |
| Metodo e recupero | Regole e checkpoint salvati | [AGENTS](../AGENTS.md), [RECUPERO](../RECUPERO.md), [handoff](HANDOFF-CODEX-ARCHIFY-20261031.md) |
| Ramo successivo a86c2c9/5e61e53 | Separato, non adottato automaticamente | Correzione nucleo e 386 test documentati, assenti dalla ZIP base |
| Add-on web: requisiti | Raccolti | [Piano](PIANO-ADDON-WEB-E-DIAGNOSTICA-20261101.md), voce naturale, ricerca e azione nel sito |
| Add-on web: progetto tecnico | Da completare sulla base b936879 | Contratto, ricerca/riuso, permessi, integrazione e revisione finita prima del codice |
| Add-on web: codice/test nuovi/pacchetto | Non iniziati | Nessuna nuova distribuzione |
| Diagnostica nuova/reset/ritorno versione/UI | Requisiti pianificati | Non confondere con funzioni già presenti nella base |
| Riordino operativo | Candidati e contraddizioni individuati | Nessun sorgente, launcher, pacchetto o dato cancellato |
| RAM/CPU target, nuovi login/audio/Windows | Non misurati/eseguiti dall'audit | Riscontro utente e CI hanno ambiti distinti |

## Decisioni preservate
Comando preciso locale senza GPT; interpretazione esterna quando necessaria e consentita; chiarimenti contestuali. Nessuna funzione extra non concordata. Utente decide risultati e non programma; assistente realizza il lavoro tecnico autorizzato. Add-on per Pavilion i3-2100/10 GB/Windows 10, caricamento a richiesta e test propri. Dati, compatibilità e controllo manuale microfono preservati. Consegna soltanto con pacchetto verificato e link funzionante in Download.

## Aggiornamento vigente — schede dei progetti
[Catalogo implementabili](IMPLEMENTABILI.md) e schede in implementabili/ creati per recuperare caratteristiche, decisioni, prove, dubbi e prossimo passo di ciascun progetto. Browser sospeso; discutere altre funzioni e concordare priorità prima del codice. Cronometro e promemoria sono proposte dell'assistente, non richieste approvate. Ritirata la proposta appunti vocali nata da un fraintendimento: l'utente chiedeva appunti di sviluppo nella repository. Nessuna modifica runtime, nuova build o test dell'app.

## Attività attuale — Windows, file e programmi
Requisiti dell'utente in [scheda WINDOWS](implementabili/WINDOWS.md): accesso/cartelle, ricerca/apertura file e programmi selezionabili nelle impostazioni, interpretazione naturale e catalogo aggiornato. Riusare Windows/codice esistente quando sufficiente; non è un divieto assoluto di dipendenze nuove, la scelta deve essere motivata da requisiti, consumo e affidabilità. Lettura sorgenti b936879 e documentazione Microsoft svolta, nessun test Windows/benchmark o implementazione. Chiarito dall'utente: ricerca/apertura e lettura/spiegazione entrambe richieste, con nomi parziali e ricerca per indizi/scopo (esempio cartella installazione Minecraft). Non basta cercare una cartella chiamata Minecraft; verificare fonti locali e distinguere candidati. Ambito cartelle e formati iniziali ancora da definire; nessun nuovo test/implementazione. Guida semplice, un punto/domanda alla volta.

## Piano Windows e vincolo contro i duplicati
Piano per fasi salvato nella scheda WINDOWS: inventario con responsabilità → prova minima Windows → miglioramento percorso completo → estensione ricerca/lettura esistenti → verifiche/consegna/recupero. Funzioni già presenti da migliorare nel loro componente, nessun doppione o nuova add-on automatica. Piano/documentazione soltanto; prove d'integrazione, codice e pacchetto non iniziati. Prossimo passo: discussione guidata del piano con esempio concreto, poi delimitare incrementi e autorizzazione.

## Organizzazione manualmente leggibile
Richiesta: nuove add-on/moduli con propria cartella dal nome chiaro e LEGGIMI che orienti fra codice, risorse, test, configurazione e dati reali. Pianificare/verificare compatibilità col gestore esistente; niente duplicati o spostamenti automatici dei moduli attuali. Requisito salvato in AGENTS e scheda WINDOWS; nessun file runtime riordinato.

## Metodo per le riprese e ZIP essenziale
AGENTS/RECUPERO aggiornati: ogni istanza con accesso repo deve leggere il metodo e la scheda, senza farlo ripetere all'utente. Nessuna garanzia di accesso automatico per chat esterne. Prossimi ZIP con soli file operativi/installazione/configurazione/istruzioni essenziali, inclusi sorgenti direttamente eseguiti. Test/handoff/CI e altro sviluppo restano repo; inclusioni motivate e test su ZIP estratto. Publisher b936879 esaminato: oggi include quasi tutto il Git, quindi selezione runtime ancora da implementare. Base/pacchetto confermati invariati.

## Componenti mancanti e istruzioni nella consegna
Richiesti avvisi nella console con nome esatto di add-on/file/dipendenza, funzione interessata e rimedio/script o nome/link verificato per scaricarla. File interni: percorso e pacchetto corretto. Rilevatori Telegram/FFmpeg/Vosk e installa_telegram.bat letti sulla base, da riusare; unificazione console/link non implementata o collaudata ora. Requisito in AGENTS e scheda WINDOWS; ZIP operativo con istruzioni essenziali, base invariata.

## Primo incremento scelto: applicazioni classiche e Store
L'utente sceglie avvio programmi: rilevamento Windows di classici e Store, spunte nelle impostazioni, frase naturale e apertura dell'app corretta (esempio Netflix). Specifica e fonti Microsoft nella scheda WINDOWS; rilevata distinta da avvio collaudato. No sostituzione silenziosa col sito web o promessa di trovare qualunque programma. Nessun codice o prova Windows eseguiti. Prossimo passo specifico: spiegare elenco/spunte/prova apertura e completare contratto/revisione sul gestore esistente prima dell'implementazione.

## Chiarimento vigente sul dialogo
L'utente conferma dialogo naturale: Jarvis deve distinguere conversazione, richiesta d'azione e dubbio, senza interpretare ogni frase come comando, chiedere ripetutamente o richiedere nomi/formule esatti. GPT esterno per interpretazione necessaria; locale diretto per comandi precisi. Conservare domanda pendente e risposte brevi. Frase personale «Insegna comando» solo opzione discussa, non sostituisce il requisito centrale. Criteri di prova e verifica Cortana/WSR/Windows 11 salvati nella scheda WINDOWS. Nessuna nuova implementazione/test runtime; chiesto chiarimento del funzionamento, non via al codice.

## Priorità vigente — accesso generale a file e cartelle
Aggiornamento pomeridiano: l'utente vuole partire dai file, non da una sola app campione. Funzione generale su cartelle accessibili fuori dal sistema, primo incremento in sola lettura; obiettivo più ampio RW/cancellazione fuori dal sistema e sistema solo lettura da progettare. Non richiedere nome di programma come prerequisito. Applicare tutti i requisiti .jaddon/cartella/riuso/dialogo/test/consegna/recupero, non duplicare la ricerca esistente. Dettagli e limiti in WINDOWS.md; nessun codice/test runtime/pacchetto. I precedenti «primo incremento app» sono superati per priorità, restano requisiti da riprendere.

## Profilo e ricerca automatici
Jarvis deve rilevare account/profilo Windows e percorsi reali delle cartelle note senza input manuale o nomi dedotti dalla chat; usare Windows Search dove disponibile e distinguere indice incompleto da file assente. Fonti Known Folders/profilo e criteri di prova aggiunti nella scheda WINDOWS. Nessun accesso reale al PC, implementazione o test nuovi.

## Proposta UI — cartelle consentite con spunte
L'utente suggerisce spunte per unità/cartelle, comprese sottocartelle; chiede semplicità. Proposta salvata in WINDOWS: selezione ampia con ereditarietà, eccezioni espandibili, riepilogo chiaro e caricamento su espansione. Primo incremento sola lettura; sistema protetto; spunte non cambiano permessi Windows. addon_ui.py base letto: configuratore non presente, da integrare nel gestore esistente. Dettagli ancora da discutere/validare; nessun codice o permesso modificato.

## Ricerca di riferimenti per selezione/esclusioni
Fonti primarie consultate e salvate nella scheda: Everything (Options/Exclude), Syncthing (regole ignore), Microsoft Known Folders e WRP/SfcIsFileProtected. Proposta: ispirazione per UI/policy, percorsi/protezioni dal Windows reale; nessuna installazione o copia dei due prodotti. Filtri indice non equivalgono al controllo accessi; nessun database universale verificato. Solo ricerca documentale, niente codice/test API sul PC.

## Decisione vigente — struttura approvata, codice per responsabilità
L'utente approva selezione dischi/cartelle con sottocartelle ed eccezioni per il primo incremento in sola lettura. Richiede tutte le add-on con propria cartella e codice ripartito in moduli comprensibili, evitando file monolitici di migliaia di righe; regola in AGENTS e scheda WINDOWS. Nessuna nuova build/codice/test runtime. Prossimo passo tecnico: completare contratto/inventario e revisione mirata, con questa struttura come requisito confermato; scritture/cancellazioni e dettagli non verificati non diventano automaticamente approvati.

## Prossimo passo corrente
Pubblicazione documentale chiusa e verificata; nessun consenso pendente. Passo tecnico successivo: prova nativa Windows limitata come descritta nel contratto ACCESSO-FILE, poi percorso minimo completo sul ramo b936879. Le scelte cartelle/eccezioni, priorità file e lettura sono già raccolte: non ricominciare la discussione né chiedere un'app campione. Browser resta sospeso.

## Prossimo passo precedente, subordinato alla scelta delle priorità
Attendere il successivo via dell'utente; poi leggere questi riferimenti e completare la revisione tecnica dell'add-on sulla base b936879 preservata. La revisione tecnica resta da completare, senza implementare finché non arriva il successivo via dell'utente. Non ripetere la ricerca della base o attribuire alla ZIP i 386 test successivi. Per ripristino usare il registro, non scansionare tutti i commit/artifact.

## 2026-11-01 — Riscontro PC Accesso file e correzioni in corso
Elenco/lettura funzionano nell’uso riferito, ma emersi difetti voce, numeri, tipo file/cartella e ricerca d’installazione/chiarimenti. Richiesta navigazione nelle sottocartelle e contesto Esplora file. [Checkpoint corrente](ACCESSO-FILE-CORREZIONI-20261101.md). Non promuovere 7298fb6 a base confermata. Run 41329991457 fallita e pubblicazione bloccata; correzione 755f988 in run Windows 41330559676. Nessun test Linux. Prossimo passo: verificare esito Windows, poi incremento installazione e navigazione nel servizio esistente. Base b936879 preservata.
