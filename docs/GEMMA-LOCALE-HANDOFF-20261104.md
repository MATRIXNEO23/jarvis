## Diagnosi coda — runner alternativo anch’esso in coda

Run minima41863698315 su windows-2025 e prova Gemma41862178113 su windows-2022 risultano entrambe QUEUED agli ultimi controlli, nessun nuovo esito runtime. Il problema osservato non è limitato alla singola etichetta2022; non dimostrata causa generale/billing/outage. Consultato stato pubblico GitHub ma dati non sufficienti ad attribuire la coda a un incidente. Non avviare ulteriori job o cambiare motore per tentativi. Prossima verifica: esito di queste due run già inviate. Compilazione DLL e ABI verdi restano prove valide nel loro ambito; inferenza, UI e prestazioni non verificate.

## Diagnosi finita della coda Windows

Dopo nuovo «procedi», run41862178113 resta QUEUED/job126686686231 senza step; nessuna causa dimostrata. Nuovo esperimento minimo windows-runner-probe.yml su windows-2025: stampa OS, nessun checkout/modello/compilazione. Scopo distinguere disponibilità pool2022 da un problema più ampio, non considerare un esito runner come test motore. Non cambiare backend o aggirare gate di verifica per la coda.

## Prosecuzione autorizzata — criterio di confronto fissato

L’utente richiede ancora prosecuzione autonoma con skill e domande solo necessarie. Stato run41862178113/job126686686231 ricontrollato: QUEUED, nessuno step avviato. Non è un fallimento del modello; causa della coda non accertata. Nessuna nuova compilazione o inferenza sostitutiva avviata. [Protocollo confronto Kobo](GEMMA-CONFRONTO-KOBO-20261104.md): GGUF/impostazioni identici, misure separate cold/warm/TTFT/token-s, cache e output comparabili, incertezza non promossa a PASS. Nessuna misura Pavilion acquisita. Prossima dipendenza resta esito prova Gemma reale; non pubblicare la006.

## Prova Gemma reale in coda — prossimo controllo

Run41862178113/job126686686231 sul source220241d07041c12a055295b11a71adc4aba08645, ultimo stato QUEUED (nessuna generazione osservata). Non ricompilare la DLL già verde; il workflow scarica artifact13339099748 della run41860087656 e verifica SHA256. Esito ABI130 PASS resta distinto da inferenza. Leggere log di questo job, correggere solo cause dimostrate, poi implementare binding/add-on e raccordo console. Non richiedere di nuovo approvazione ai passi autorizzati.

## Motore nativo compilato e caricato — prova successiva Gemma in preparazione

Run41860087656/job126679185318 SUCCESS: DLL19010560byte SHA256ac834f409855bd7e12a0f0c0ffc8601a663b036b2403d74af4b6b3d3afd49bba, export e contatore iniziale reali PASS. Anche duplicata41860458509 SUCCESS. Non sono inferenze. Prossima unità tools/probe_native_gemma.py usa mapping Python upstream fissato e DLL direttamente, mai main/server. Download CI pubblico bartowski/gemma-2-2b-it-Q4_K_M.gguf con revisione/hash dalla metadata publisher; nessun account, peso non redistribuito. Identità col GGUF dell’utente NON verificata. Due richieste con un solo load, report risultati/tempi; non è benchmark Pavilion o raccordo Jarvis. Workflow native-gemma.yml da verificare.

## ABI verificata, compilazione motore in attesa — prossimo passo preciso

Source0c57701d29dab9aa7bcdb24270ae07609ce36eda, run41860720969/job126681442160 SUCCESS:130 dimensioni/offset coincidono tra ctypes upstream ed header C++ compilato Windows; nessuna inferenza. Primo errore fixture conservato sotto. Evidenza native-engine-20261104.json. Compilazione DLL run41860087656/job126679185318 ancora IN_PROGRESS all’ultimo controllo; run41860458509 duplicata dallo stesso trigger ampio, non è una nuova variante del motore. Non avviare altre compilazioni finché non letto questo esito.

Ripresa: leggere esito/log native build e probe, distinguere un verde compilazione da caricamento DLL. Poi binding nativo dalla revisione fissata, confronto default upstream, prova Gemma residente e misure stesse impostazioni; solo dopo raccordo console e consegna. Non riprendere subprocess Kobo esterno o dichiarare raggiunte le prestazioni. Nuova UI/impostazioni e006 non presenti. Sviluppo e pubblicazione checkpoint già autorizzati; nessuna nuova domanda sui requisiti confermati.

## Diagnosi ABI — fixture corretta

Run41860458889/job126680509056 fallita prima del confronto: expose.h usa std::string e std::vector, include mancanti nella translation unit della prova. Non è mismatch ABI o difetto motore. Correzione minima include string/vector prima di expose.h; nuovo ingresso tools/check_native_abi.py per separare trigger ABI dalla costosa compilazione DLL. Vecchio tools/native_model/check_abi.py resta storico e non è più chiamato dal workflow ABI. Nuova verifica Windows da leggere.

## Prova Windows avviata

Source0b819a8c3f3a1911652b11811421da0c4f1e4f2e, run41860087656/job126679185318: compilazione DLL upstream in corso. Compilatore installato; non dichiarare PASS prima del probe. Mappa impostazioni in GEMMA-IMPOSTAZIONI-20261104.md. Preparato check_abi.py per confrontare strutture ctypes upstream con sizeof/offsetof C++ dello stesso header: da eseguire su Windows prima di chiamare load_model/generate dal nuovo binding. Nessun peso o account personale usato.

## Prova motore incorporato in corso — checkpoint corrente

Requisiti più recenti: prestazioni almeno Kobo e tutte le impostazioni utili configurabili. Prima prova su backend nativo della stessa versione, non wrapper exe. [Decisione e percorso verificabile](GEMMA-MOTORE-NATIVO-20261104.md). Workflow native-model.yml e tools/native_model/probe.py: compilazione/caricamento DLL Windows da eseguire, nessuna006. Il percorso subprocess/HTTP precedente resta scartato per la consegna.

## Correzione architetturale dell’utente — 4 novembre 2026

Requisito prevalente: incorporare nell’add-on di Jarvis il motore e le funzioni utili che consentono a KoboldCpp di eseguire Gemma, senza installazione/configurazione esterna di KoboldCpp. Stessa console, controllo CPU/RAM/thread/contesto, modello residente. L’utente descrive il lavoro come reverse engineering: prima analisi e riuso dei sorgenti pubblici e delle librerie, non reimplementazione cieca degli algoritmi. Prestazioni pari a Kobo sono un obiettivo da misurare sul Pavilion, non un risultato garantito.

L’adattatore subprocess che richiede un koboldcpp.exe scelto dall’utente NON soddisfa questo requisito e non va distribuito come soluzione finale. local_model/runtime.py e client.py operativi sono bozze locali non pubblicate né verificate; remoto a83f533 contiene soltanto lo stub del contratto configurazione. Broker con nove test Windows rimane riutilizzabile; i test command-line sul vecchio approccio non attestano il nuovo motore incorporato.

Fonti primarie consultate: https://github.com/LostRuins/koboldcpp (sorgenti e componenti/licenze), https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md e ggml/CMakeLists.txt (librerie native e configurazione CPU). Valutare libreria interna KoboldCpp contro llama.cpp nativo riusabile tramite binding, preservando formato Gemma2, cache e opzioni effettive. Non scegliere dal solo nome della libreria. Verificare AVX senza AVX2/FMA/F16C e altre istruzioni non disponibili sullo i3-2100; compilazione Windows e prova di caricamento/inferenza necessarie. Non affermare parità di prestazioni dal riuso dello stesso antenato del motore.

Prossimo passo: inventario funzioni necessarie e confronto tecnico dei due riusi, versione sorgente e licenze fissate, piccola prova Windows del backend incorporabile prima del raccordo GUI. Non proseguire il wrapper HTTP/Kobold esterno come consegna finale. Nessun motore nuovo già integrato, nessuna006. Le sezioni precedenti sono storia e sono superate dove incompatibili.

# Gemma locale — checkpoint in corso, 4 novembre 2026

Autorizzazione: utente richiede pianificazione e installazione/integrazione per lo scopo; chiarisce motore tipo Kobold integrato come add-on, CPU/RAM configurabili, modello residente, unica console Jarvis. Online interruttore e conferma per ogni inferenza. Non chiedere di nuovo queste decisioni.

Base verificata via Git: build/jarvis-005,7203fef3357cb880161d20dd5304ccee92a0c0bb. Nuovo ramo feature/gemma-local-20261104. Nessuna modifica delle copie locali precedenti release-work/voice-work e dati utente. Main radice storica non usata. Letti RECUPERO, AGENTS correnti main, indice sorgenti, handoff/lezioni e implementazioni mirate. Ramo005 ha documenti storici con intestazione004: sorgente/005 verificati separatamente.

Documenti: GEMMA-LOCALE-SPEC-20261104.md e superpowers/plans/2026-11-04-gemma-locale.md. Piano riesaminato prima del codice. Adattatore progettato per riuso delle azioni già presenti; niente framework/servizi a pagamento. Accuratezza Gemma non dimostrata in generale; precisazione successiva utente: richiesta esplicita di apertura immediata, proposta indiretta da chiarire. Test soltanto Windows.

Stato: pianificazione pronta; Task1 e2 da iniziare con test e stub comportamentale. Nessun test nuovo eseguito, nessun modello reale chiamato da questo ambiente, nessun pacchetto006 creato. Prima modifica prevista local_model/* e test; pubblicare red Windows, poi implementare. Mancata clonazione iniziale risolta: clone completo gemma-work disponibile; jarvis/.git precedente era incompleto e non usato.

Task1/2 RED pronto: stub ModelService.call non esegue richieste; sei test di comportamento chiedono routing/consenso e devono fallire su asserzioni osservabili, non import. Workflow Windows local-model.yml separato, nessuna build. Scelta utente: apertura esplicita immediata se autorizzata; indiretta da chiarire.

## Blocco prima del RED Windows

La revisione automatica ha rifiutato git push: destinazione pubblica e autorizzazione alla pubblicazione non considerata esplicita. Non aggirare il rifiuto con GitHub API o altri trasporti. Nessun test Windows nuovo eseguito; il RED è atteso, non osservato. Non continuare implementazione dipendente dal test fino al via alla pubblicazione e al riscontro CI. Il tool create_branch, già chiamato prima di ricevere il rifiuto, ha creato feature/gemma-local-20261104 dalla005 senza questi file; non considerarlo checkpoint pubblicato. Nessuna build/pacchetto006.

Modifica da approvare: piano, specifica, handoff, rimandi nei tre documenti di continuità, stub innocuo ModelService.call (nessun processo/inferenza), sei test Windows e workflow dedicato; nessun peso, binario, credenziale, log personale. Un commit locale e i suoi edit successivi sono presenti; verificare diff prima di riprendere. App005 e dati non modificati. File di revisione GEMMA-PROPOSTA.patch nel checkout, creato da git diff della base005. La pubblicazione serve prima ai test e alla continuità, non installa nulla sul PC.

## Autorizzazione e primo RED osservato

L’utente ha risposto «Consento» alla pubblicazione di piano/test nel ramo pubblico. Superato il blocco di autorizzazione. Git CLI privo di credenziali; pubblicazione tramite connettore GitHub autorizzato, commit0e1f36af97b59617dc4114eedf94993035436ce8. Run Windows41841632108/job126614440423: sei test, sei fallimenti di asserzione, zero errori/skip. Stub non eseguiva inferenze: RED del contratto, non regressione della005.

Prima implementazione isolata del broker in local_model/service.py: locale prioritario, interruttore online, consenso callback per ogni inferenza, origine Telegram distinta, revoca risultati al cambio configurazione. Aggiunti tre casi revoca/consenso monouso/spegnimento durante attesa. Nessun raccordo UI/runtime ancora realizzato. Prossima verifica Windows nove test; poi runtime Kobold, consenso UI non modale e collegamenti console. Nessuna006, nessuna misura Gemma reale.

## Primo componente verificato, non ancora integrato

Source a47c63a79b3865f655e24aef2530469c58988628, Windows run41841843739/job126615172345:9 test PASS, zero errori/fallimenti. Trasporti locali/online sostituiti, nessuna inferenza reale. Evidenza docs/evidence/gemma-routing-20261104.json. Suite globale/GUI/Gemma/Kobold/account non eseguiti. Non dichiarare add-on installabile. Prossimo passo: runtime/client locali con startup CPU loopback e timeout, poi UI consenso non modale e raccordo console/voce/Telegram. Autorizzazioni di sviluppo già date: non richiedere nuovamente il via per questi passi.

## Runtime CPU — nuova unità in corso

Utente: «Procedi». Prima del codice operativo, quattro test configurazione/command-line/persistenza/corruzione e stub LocalConfig. Windows RED da osservare; nessun test Linux. File local_model/runtime.py e tests/test_local_model_runtime.py, workflow focalizzato esteso. Segue implementazione runtime e client su loopback, senza cambiare ancora la console.
