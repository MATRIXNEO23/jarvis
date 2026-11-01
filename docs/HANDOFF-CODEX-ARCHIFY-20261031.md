# Handoff Jarvis → Codex — 2026-10-31

## Stato verificato
- Repository: MATRIXNEO23/jarvis, branch di distribuzione `main`.
- Archify v3.2.0 installato per Codex, solo come strumento di sviluppo in `.agents/skills/archify/`. La workflow `Install Archify skill for Codex (repository only)` run 41232507968 è PASS; verificato che `.agents/skills/archify/SKILL.md` è presente su `main`.
- Archify **non** è un add-on di Jarvis, non è un componente del runtime Windows e non corregge automaticamente bug.
- Due workflow recenti `Jarvis unit and GPT protocol checks` falliti: run 41230414187 (commit 1f7310f...) e 41230403859 (commit 8d439df...). Esaminare log, identificare cause, non indovinare.
- Workflow `Publish Jarvis timer audio fix ZIP to Download` run 41229495866 PASS; correzione nota: `winsound.SND_SYNC` non esiste, usare `SND_NODEFAULT` per WAV. Bip alternativo funzionante sul PC utente; WAV ancora da verificare sul PC dopo l'aggiornamento.
- Problema aperto: in conversazione normale Jarvis perde coerenza dopo 2-3 scambi. Le limitazioni note sono in `conversation_memory.py`, `conversation_router.py`, `jarvis_persona.py`, `jarvis.py`; verificare branch e versioni effettive prima di modificare. Le modifiche precedenti sul branch `feature/timer-settings-ui-20261031` non sono da considerare collaudate; due workflow falliti.
- Ultima richiesta: diagnosi architetturale con Archify, review del percorso voce/testo → memoria → prompt → modello esterno → risposta, e risoluzione dei workflow falliti. **Nessun nuovo add-on per questa correzione del nucleo conversazionale**.

## Vincoli del progetto
- Nessun costo aggiuntivo, nessuna API a consumo, nessun hosting a pagamento.
- Nuove funzionalità modulari `.jaddon` salvo correzioni tecniche del nucleo come questa.
- Preservare compatibilità, impostazioni, memoria/salvataggi e funzionalità.
- Microfono OFF/standby all'avvio; modalità di ascolto solo sotto controllo manuale.
- Hardware target: Windows 10 x64, HP Pavilion i3-2100, 10 GB RAM; evitare processi residenti superflui.
- Pubblicare pacchetti completi testati in `Download/`, aggiornare `Download/README.md` con link in cima solo dopo test PASS; non cancellare pacchetti precedenti.
- Prima di intervenire, verificare lo stato attuale di `main`, branch, diff e workflow; evitare sovrascritture e modifiche non richieste.

## Prossimo lavoro Codex
1. Leggere `.agents/skills/archify/SKILL.md` e documentazione necessaria. Usare Archify come strumento di sviluppo, non integrarlo nell'app.
2. Analizzare in sola lettura il codice e i log delle due run fallite; distinguere bug, regressioni e problemi CI.
3. Tracciare con prove da file/linee l'intero percorso della conversazione e la gestione del contesto; produrre mappa Archify validata e un breve rapporto.
4. Proporre una correzione minima e test multi-turno (riferimenti, cambio argomento, limiti e comandi); non aumentare indiscriminatamente il prompt.
5. Prima di modificare il codice, presentare risultati e piano all'utente per approvazione. Dopo approvazione, test e build review; pubblicare ZIP solo a verifiche superate.
6. Registrare commit, workflow, test e questioni aperte aggiornando questo handoff.

## Riferimenti
- Installazione: https://github.com/MATRIXNEO23/jarvis/actions/runs/41232507968
- Run fallite: https://github.com/MATRIXNEO23/jarvis/actions/runs/41230414187 e https://github.com/MATRIXNEO23/jarvis/actions/runs/41230403859
- Archify ufficiale: https://github.com/tt-a1i/archify


## Fase 1 completata: correzione CI verificata
- Main iniziale: 2e10d52cb576dcbf7f000b4ada00e9ef08b0a1d1. La radice main contiene sorgenti storici (31 test locali PASS); sorgenti evoluti nel ramo feature/timer-settings-ui-20261031 e ZIP. PR #32 aperta verso feature/hud-reference-ui-20261031, nessun merge.
- Letti tutti gli 8 log delle run 41230403859 e 41230414187: unico errore test_second_brain.py:26, AssertionError 16 <= 8 falso. Il commit 8d439df ha ampliato memoria a 16/2400 senza aggiornare il test; 1f7310f eredita il problema.
- Richiesta successiva dell'utente autorizza il fix CI: commit faba67363e07ea478241fbe549c45474aab5144a sul ramo esistente, solo test. Verificati ordine, espulsione primi quattro dopo 20 inserimenti, 16 scambi, budget 2400/1050, ultimo scambio e clear. Nessun test disabilitato.
- Nuova run https://github.com/MATRIXNEO23/jarvis/actions/runs/41232983494 completed SUCCESS: Ubuntu Python 3.11.17 job 124630832484 e 3.12.15 job 124630832587: 373 test OK skipped=5 ciascuno; Windows Python 3.11.9 job 124630832597 e 3.12.10 job 124630832656: 373 test OK ciascuno. Sintassi Python/Node e PowerShell Windows PASS. Vecchie run restano fallite, superate dalla nuova verifica.
- Locale Python 3.12.14, Node 24.22.1: 373 test OK skipped=5; compileall, node --check, git diff --check PASS. Nessuno ZIP pubblicato; GPT/Pavilion non collaudati.

## Fase 2 completata con limite browser: Archify
- Mappa del commit evoluto 1f7310f67887dcc756646513151c90b3d12ac703: docs/architecture-20261031/jarvis.html. Non è la mappa dei sorgenti storici alla radice main.
- Commit HTML fa90dc640ff74b6d50cebfeffe4917ae78d92a05; candidato e6604fab75a332b88e9d79b81a19b971bfdc1663; ricevuta 189f2bd3022b9d39399aa3116f09ed823e074385.
- Archify validate/deliver/check PASS comprese fonti; browser-check SKIPPED per assenza Chrome/Chromium, finalize codice 2: non completamente PASS, nessuna ispezione visiva. Viewer fallback inglese, contenuto italiano. Archify solo sviluppo, nessuna dipendenza runtime.

## Fase 3: diagnosi e proposta, runtime in attesa di approvazione
- Rapporto docs/DIAGNOSI-ARCHIFY-DIALOGO-20261031.md, commit 231fc9dd1f96c95d6197417b7d55eeb59475ad28.
- Dimostrati: riduzione RAM a 860 e successivo limite <=850; permanente.recent SQLite ignorato dalla compattazione finale; cataloghi prima della memoria; troncamento prefissi; chiarimenti brevi dipendenti dalla domanda RAM. Sovrapposizione recenti progetto/RAM può duplicare il contesto.
- Riproduzione locale: 5 turni medi diventano 2, prompt 4896 caratteri; marcatore permanente.recent non passa al prompt. Nessuna richiesta a modelli esterni. Non dimostrata la causa di tutti gli episodi osservati sul PC.
- Bridge senza ID conversazione esplicito; comportamento interno SDK non verificato. ID Python correla richieste IPC, non conversazioni.
- Incongruenza preesistente: auto_listen=True e jarvis.py:3620–3622 possono attivare GPT_CONVERSATION all'avvio, in conflitto con standby richiesto. Non modificata dal fix test; da risolvere/verificare prima di distribuire.
- Piano minimo da approvare: un'unica selezione contesto entro 5000 caratteri, riserva memoria prima cataloghi opzionali, recupero permanente.recent a RAM vuota, dedup/isolamento e domanda pendente preservata. Test payload finale 6–10 turni, riferimenti, riavvio, cambio argomento/progetto, cataloghi pieni, limiti e nessun replay comandi. Poi CI completa, smoke IPC e collaudo GPT/microfono Windows 10 prima del pacchetto.
- La correzione autorizzata dei workflow è completata. Nessuna modifica del nucleo conversazionale prima dell'approvazione del piano.

## Nuova regola persistente richiesta dall'utente
- Registrare decisioni, motivazioni tecniche, prove ed esiti; promuovere solo soluzioni verificate. Escludere approcci falliti dalle soluzioni consigliate, conservando causa e lezione per evitare ricadute. Non cancellare prove diagnostiche, salvataggi o cronologia.
- Applicazione nelle istruzioni AGENTS.md e nel registro docs/DECISIONI-E-LEZIONI.md.

## Fase 4 completata — registro persistente di decisioni e lezioni
- Regola AGENTS.md presente su main (commit b2b28b2785b4b16c8d3c5f7e9f03a7ffc3c71abb) e sul ramo evoluto (bcf705869e0c9ff956bfb840feab1f3e1e6480a2).
- Registro docs/DECISIONI-E-LEZIONI.md presente su main (f5230f4550da0543a776c8450b37334a97efba8d) e sul ramo evoluto (d332c10aed102c671841f2e45fcee73939b15b83).
- Registrati soluzione CI verificata, aumento dei soli limiti scartato come soluzione sufficiente e limite del controllo browser Archify. Soluzioni fallite escluse dalle raccomandazioni; cause conservate per evitare di ripeterle.
- Questi ultimi commit modificano solo documentazione: nessuna nuova verifica runtime necessaria rispetto al fix test faba673 già verificato. Nessun pacchetto prodotto.

## Fase 5 — piano approvato e nucleo corretto, CI in attesa
- L'utente ha approvato esplicitamente con «Sì» dopo la conferma sul piano. Nessuna ulteriore autorizzazione necessaria per questa correzione.
- Commit a86c2c932af988b23916e8d4495025de5ee0a730 nel ramo esistente feature/timer-settings-ui-20261031; confronto controllato con d332c10: solo 13 file previsti, nessun pacchetto e nessun merge su main.
- Aggiunta raccolta locale conversation_context.py; rimossi tagli intermedi 860/850, recuperati recenti SQLite, selezione finale uniforme fino a 10 turni secondo budget, domanda finale preservata, dedup sovrapposizione, Unicode contato in unità UTF-16 come Node, cataloghi opzionali dopo riserva memoria.
- Timeout testo breve allineato alla voce a 180 secondi. Memoria resta descrittiva, validatori azioni invariati; nessun servizio/API aggiuntivo.
- Avvio in standby senza sovrascrivere modalità manuali; vecchia auto_listen conservata ma sospesa in UI; preparatore prova non forza più l'opzione a True. Nessuna migrazione schema o cancellazione dati.
- Locale: 386 test OK skipped=5 (Windows); 13 nuove regressioni inclusi callback reali fino alla chiamata client. compileall/node --check/diff --check PASS. Smoke Windows attivato sulla PR senza login o richieste al modello.
- Rapporto implementazione e lezioni sul ramo evoluto: docs/CORREZIONE-NUCLEO-DIALOGO-20261031.md e docs/DECISIONI-E-LEZIONI.md. Due difetti di prima implementazione trovati e corretti: conteggio Unicode e separatore domanda finale; conservarne i test.
- Esiti remoti da registrare nella prossima fase. Non dichiarare collaudo GPT/Pavilion; nessuno ZIP distribuibile prima dei controlli previsti.

## Fase 6 completata — CI e smoke verificati, consegna del nucleo
- Commit runtime/test a86c2c932af988b23916e8d4495025de5ee0a730, PR #32 sul ramo esistente. Nessun merge su main: qui restano catalogo e documentazione.
- Run unit https://github.com/MATRIXNEO23/jarvis/actions/runs/41236238213 completed SUCCESS. Log letti: Ubuntu 3.11.17 job 124640509613 e 3.12.15 job 124640509442, ciascuno 386 test OK skipped=5; Windows 3.11.9 job 124640509588 e 3.12.10 job 124640509685, ciascuno 386 test OK senza skip. Sintassi Python/Node e parser PowerShell PASS.
- Run smoke https://github.com/MATRIXNEO23/jarvis/actions/runs/41236238208 completed SUCCESS, job 124640509415. SDK import OK; protocollo reale bridge ready/status disconnected/shutdown verificato, senza login e senza richieste al modello.
- Archify aggiornato sul commit a86c2c9: docs/architecture-core-20261031/jarvis-core.html, candidato e ricevuta accanto. validate/deliver/check PASS; browser-check saltato perché Chrome/Chromium assente, finalize codice 2, nessuna verifica visiva. Questo limite riguarda la mappa, non la CI Jarvis.
- Implementazione, prove e limiti in docs/CORREZIONE-NUCLEO-DIALOGO-20261031.md; evidenze sintetiche in docs/VERIFICA-NUCLEO-DIALOGO-20261031.json; lezioni aggiornate in docs/DECISIONI-E-LEZIONI.md.
- Esito: correzione tecnica verificata automaticamente e pronta per collaudo reale. Non dimostrata ancora la qualità semantica delle risposte GPT sul Pavilion; vecchie informazioni già troncate non recuperabili. Budget limitato e dedup dei prefissi storici esplicitamente documentati.
- Nessun ZIP prodotto o pubblicato. Per distribuire resta il collaudo Windows 10 con account GPT, salvataggi/progetti, comandi e modalità microfono manuali. Non serve richiedere di nuovo approvazione per il piano già approvato; non dichiarare il collaudo reale senza prove.

## Chiusura e ripresa
- Documentazione/mappa/evidenze finali su main nel commit c814ee6ae0d8b3d4d1e84782b60eea14a9b34268; risultati riportati anche nel ramo evoluto con commit solo documentale 5e61e53fbb58ccb5d95b85671604cc5f365d6e04.
- PR #32 aggiornata per rappresentare timer e continuità; aperta, mergeable, nessun merge effettuato. I test verdi si riferiscono al codice di a86c2c9: 5e61e53 cambia soltanto documentazione.
- Prossimo collaudo reale: avviare il codice del ramo evoluto in cartella separata, verificare standby; collegare GPT; provare 6–10 scambi con due mete nominate, domanda e risposta breve, poi richiamo della scelta iniziale. Con Second Brain attivo riavviare e rispondere al chiarimento precedente; con memoria disattiva non aspettarsi ricordi dal disco. Cambiare progetto e verificare assenza di contaminazione. Controllare selezione manuale microfono, comandi locali e salvataggi. Annotare esito osservato senza attribuirgli risultati non misurati.


## 2026-11-01 — Riscontro pratico dell'utente sul dialogo
- Alberto riferisce di aver appena conversato con Jarvis sul proprio PC: mantiene abbastanza il contesto ed è «molto migliorato».
- Stato: riscontro positivo riferito dall'utente durante uso reale; non osservato direttamente dall'agente. Supera la precedente assenza di feedback pratico, senza equivalere a collaudo completo.
- Versione/SHA installato, numero di scambi e payload non acquisiti: non attribuire causalmente il miglioramento al commit a86c2c9 senza verificarne la presenza sul PC.
- Restano da verificare riavvio e recupero SQLite, isolamento progetti, salvataggi/comandi e modalità manuali del microfono. Nessuna nuova build, merge o distribuzione eseguiti in questa fase; le CI citate sopra rimangono prove del codice testato.
- Richiesta successiva: valutare maggiore autonomia web con lettura pagine e browser automatico. Solo valutazione, nessuna implementazione autorizzata da questa domanda. Nuova funzionalità da progettare come .jaddon, con GPT esterno e zero costi aggiuntivi.

## 2026-11-01 — Pianificazione add-on web, diagnostica e memoria di sviluppo
- Requisiti e piano in docs/PIANO-ADDON-WEB-E-DIAGNOSTICA-20261101.md, creazione 04c8bf86c3f39158f6dd14b8cd9cb1125a541d3a; successivo aggiornamento aggiunge checkpoint e stato delle fasi. Solo documentazione.
- L'utente ha richiesto memoria di sviluppo nel repository, lettura obbligatoria prima di implementare, integrazione con ciò che esiste, piani per fasi e registrazione continua di scelte, prove, esiti e lezioni. Procedura AGENTS.md commit cf19eff734c7b85e81fa296f73b7b258d3aafc1c; registro aggiornato commit b955495008080940d63d78793a7f64fc6362e346.
- Add-on web on demand, GPT esterno decide e motore locale esegue; browser visibile; estensione Edge candidata, non validata. Cartella concordata Estensione-Edge. Navigazione e ricerca interna al sito, chiarimenti contestuali e confronto fonti; nessuna fonte obbligatoria dai soli esempi.
- Per ogni add-on: separazione file/configurazione, contenimento errori, versioni e recupero; UI semplice; «Ripristina impostazioni iniziali dell'add-on» distinto da «Torna alla versione precedente». Non alterare dati personali o altre funzioni.
- Diagnostica richiesta nella chat, con errore, fase e indicazione utile; dettagli limitati e autoverifiche finite nel programma, non scansioni continue.
- Verifica preliminare in sola lettura: gestore .jaddon descrittivo limitato, da progettare adattatore; diagnostica statica/passiva esistente, non prova operativa del browser. Evidenze/blob nel piano.
- Nessuna implementazione o test nuovo eseguito; nessuna misura RAM, nessuna build o distribuzione. Il valore 1–2 GB non è una misura. Non dichiarare estensione più leggera senza confronti.
- Prossimo passo: revisione del piano con l'utente; completare inventario tecnico prima di modificare codice, rispettando la richiesta di discutere prima di costruire.

## Chiarimento del ruolo dell'utente — 2026-11-01
- L'utente decide obiettivi, priorità e compromessi; non deve programmare. L'assistente svolge il lavoro tecnico autorizzato e guida eventuali operazioni manuali sul PC con passi semplici e brevi, uno alla volta.
- Evitare di trasferire all'utente scelte tecniche verificabili, ripetere domande già risolte o introdurre conferme per ogni micro-passaggio già autorizzato.
- Regola persistente AGENTS.md commit e3e09f6045fd741aa12dcd905651b7922ae4ff10; piano aggiornato commit 62a68c40143649c3dc0f5e6434eff1bf4c97449e; registro commit d90796af2ab3c05f79b1f80a495d7bc71ce19fd7.
- Solo documentazione modificata. Piano disponibile per revisione, nessuna implementazione web o prova funzionale avviata.

## Continuità tra argomenti — 2026-11-01
Indice docs/STATO-ATTIVITA.md creato nel commit d074634e96b584c1a1f339176ea22962108a357b. Leggerlo insieme a piano e registro quando l'utente riprende un argomento. Piano web già persistito, implementazione non avviata; ricordare stato e questioni aperte senza ricominciare la raccolta dei requisiti. Aggiornati AGENTS.md e lezioni con questa procedura. Nessuna modifica del programma o nuovo test.

## 2026-11-01 — Recupero unico e continuità per ogni modifica
- Creato RECUPERO.md, commit aa1bce7e0f56ce4ede2258fe5e6742f14ded4186. AGENTS.md aggiornato con lettura iniziale obbligatoria, recupero autonomo delle fonti e checkpoint per ogni modifica prima di chiudere il lavoro. Indice e lezioni collegati.
- L'utente richiede anche che l'assistente segnali incompatibilità e suggerisca alternative concrete; non limitarsi a eseguire richieste incoerenti e non trasferire scelte tecniche all'utente.
- Ambito verificato: creazione/aggiornamento documenti nel repository. Nessun test di nuova istanza, nessuna funzione runtime aggiunta. L'accesso al repository resta prerequisito della ripresa; una chat generica non legge questi file automaticamente.
- Punto di ripresa invariato: piano web documentato da rivedere, implementazione non avviata; requisiti e prove nei documenti collegati dall'indice.

## 2026-11-01 — Handoff aggiornato durante il lavoro
- Richiesta esplicita: l'utente non deve chiedere l'handoff; mantenerlo salvato anche per terminazioni improvvise.
- Procedura aggiunta a AGENTS.md e RECUPERO.md: prima di ogni modifica coerente salvare stato in corso e intervento previsto; subito dopo salvare risultato effettivo e verifiche pendenti; dopo i test aggiornare esito, prove e prossimo passo.
- Se resta uno stato in corso, la nuova sessione verifica diff, commit e file reali, senza assumere successo né assenza di cambiamenti. Nessuna garanzia su modifiche non ancora salvate.
- Stato attuale: completati questi aggiornamenti documentali; implementazione web non avviata, nessun nuovo test runtime. Prossimo passo: revisione del piano web già salvato e chiarimenti ancora aperti.

## 2026-11-01 — In corso: revisione preventiva finita e apprendimento dagli errori
- Richiesta: valutare progetto e criticità prima dell'implementazione, con controlli finiti e mirati; usare gli errori documentati per evitare ricadute.
- Intervento previsto: aggiornare AGENTS.md, piano web e DECISIONI-E-LEZIONI con revisione iniziale, ricontrollo delle sole correzioni e uso selettivo delle lezioni. Nessun codice applicativo da modificare.
- Verifica prevista: rilettura dei documenti aggiornati; nessun test runtime richiesto per queste sole modifiche testuali. Poi chiudere questo checkpoint con esito e prossimo passo.

## 2026-11-01 — Completata: procedura di revisione preventiva
- Aggiornati AGENTS.md (cebd5af94939c110e26fdb3af5ebb9aa85889cbf), piano web (a7d5ef3c14a843394a5cbfd3a01b3040bdfe19be) e registro (f0a30b5fd7b7f88d36c9a8ea9a0a10beda7cf9fa).
- Regola: una revisione iniziale prima del codice, correzione e ricontrollo mirato; blocchi residui espliciti, niente cicli globali infiniti. Dopo autorizzazione provare presto il percorso minimo completo.
- Errori da trasformare in lezioni pertinenti con evidenze e rimedi verificati; test di regressione solo quando significativo. Non promettere di trovare ogni errore prima dell'esecuzione.
- Solo documentazione modificata. Nessuna build o prova runtime. La revisione tecnica completa del piano web resta da eseguire; implementazione non avviata.

## 2026-11-01 — In corso: verifiche obbligatorie prima dell'installazione
- Precisazione dell'utente: tutto ciò che è verificabile nel repository deve essere controllato prima della consegna; sul PC restano solo prove dipendenti dall'ambiente reale. Non delegare all'utente il debug dei collegamenti di base.
- Modifica documentale prevista: esplicitare in AGENTS.md e piano web i controlli automatici e le condizioni per consegnare; aggiornare lezioni e chiudere il checkpoint. Nessuna implementazione web o nuovo test funzionale avviati.

## 2026-11-01 — Completata: regola dei test per add-on
- Richiesta chiarita: ogni add-on deve avere test automatici propri nel repository prima della prova sul PC. AGENTS.md commit eb1778680002cf24823031f2f9a5e7da4c0c5bb8, piano 2122eed746f0a706255c145dbbd400941ecf4c7a, lezioni 96f04540a3a0c367e95b5fab946e81d931525f5f.
- Requisiti: comportamento, contratti e integrazione dei componenti, errori/timeout, configurazione e recupero, regressioni pertinenti e prova del pacchetto. Distinguere componenti reali, simulazioni e controlli non eseguiti; non consegnare come pronto quando manca una prova obbligatoria.
- All'utente rimangono soltanto verifiche realmente dipendenti dal suo ambiente. Non delegargli debug riproducibile in sviluppo.
- Stato: modifica documentale completata. Nuovi test/add-on web non implementati, nessun nuovo test o workflow eseguito. Inventario della copertura delle add-on esistenti ancora da fare. Prossimo passo: revisione tecnica del piano web prima della realizzazione autorizzata.

## 2026-11-01 — In corso: ambito concordato e comandi vocali completi
- Richiesta: nessuna funzione extra a sorpresa; proporre eventuali estensioni prima di implementarle. Ogni add-on deve comprendere il percorso vocale completo, senza consegnare funzioni presenti ma non richiamabili da Jarvis.
- Modifica prevista solo documentale: precisare regole, piano e lezioni; verificare la presenza delle clausole, poi chiudere il checkpoint. Nessuna implementazione web o nuovo test in questa fase.

## 2026-11-01 — Completata: ambito e completezza vocale
- AGENTS.md 3e453b918283185fff4db857767cf670c8e95e00, piano 8cfe90dc5e39f91280a25360bf4dbd11e486c101, lezioni c2bf61f0f8af233d41ad885a3f6defaa4be12abc: niente nuove funzioni non concordate; proposte extra prima del codice.
- Ogni add-on include percorso comando vocale naturale → interpretazione GPT esterna/stato → capacità registrata → esecuzione locale → verifica → risposta. UI, esempi e capacità allineati; prove delle vie voce/testo e chiarimenti contestuali.
- Separare callback/trascrizione simulata, audio di prova e microfono/account reali. Non trasformare una prova simulata in collaudo completo.
- Solo documentazione aggiornata. Nessun nuovo test, build o implementazione web. Prossimo passo resta la revisione tecnica del piano web prima della realizzazione autorizzata.

## 2026-11-01 — In corso: linguaggio naturale ed elenco capacità aggiornato
- Precisazione: esempi vocali non sono formule obbligatorie; GPT esterno interpreta varianti e contesto. «Cosa puoi fare?» deve riflettere capacità installate, attive e disponibili.
- Aggiornamento solo documentale previsto in regole/piano/lezioni; nessuna implementazione o test avviati. Verifica prevista: presenza delle clausole e chiusura del checkpoint.

## 2026-11-01 — Completata: comandi naturali e catalogo
- Regole, piano e lezioni aggiornati: commit d26bb6eee24760b279b58e2c8f931e16bd5d0480, 93eadd7822dba06dd08b780fae0f9070282b017c, 828d6f401aafa98eec61ffa8e7a05aacb5c8d6eb.
- Parafrasi interpretate dal GPT esterno, senza formule obbligatorie; chiarimenti per dati mancanti. «Cosa puoi fare?» coerente con capacità davvero disponibili dopo ogni cambiamento delle add-on. Test esplicitati, non ancora realizzati.
- Solo documentazione. Nessun test runtime o implementazione web; prossimo passo: revisione tecnica del piano prima di realizzarlo.

## 2026-11-01 — In corso: sorgenti autorevoli e riuso della struttura
- Richiesta: codice completo sempre disponibile nel repository; nuove add-on integrate sul sistema esistente, senza ricostruirlo dalla chat.
- Verifica: ramo feature/timer-settings-ui-20261031 presente; inventario Git ricorsivo restituisce 167 voci, non troncato, con moduli Python, bridge, test e workflow. Riferimento evoluto 5e61e53fbb58ccb5d95b85671604cc5f365d6e04, coerente con handoff; non è una prova di build completa.
- Previsto: salvare un indice dei sorgenti e dei riferimenti architetturali, aggiungere regola a AGENTS/RECUPERO e lezioni. Nessun trasferimento massivo di sorgenti su main, merge o modifica runtime.

## 2026-11-01 — Completato: indice dei sorgenti e riferimenti
- Creato docs/INDICE-SORGENTI.md con inventario e punti di ingresso; riferimenti in AGENTS e RECUPERO aggiornati, lezioni registrate. Commit istruzioni 247757670b5b6146bffcdc4919fec6564017a5e1.
- Confermati ramo evoluto e presenza dei moduli/test/bridge/workflow; non verificata in questa fase la build completa o la copertura di ogni dipendenza. Radice main storica distinta dal ramo evoluto.
- Regola: sorgenti completi versionati e associati ai pacchetti; riuso dei moduli e mappa esistenti, aggiornati quando cambiano. Nessun merge, spostamento massivo di sorgenti o modifica runtime.
- Prossimo passo: revisione tecnica del piano web sui sorgenti evoluti, implementazione non avviata.

## 2026-11-01 — In corso: prima installazione completa e riordino verificato
- Richiesta: cartella unica per installazione da zero, componenti esterni, configurazione di ciascun modulo e reinstallazione; aggiornamento a ogni modulo nuovo. Jarvis deve indicare i componenti mancanti. Successive precisazioni: valutare a ogni aggiunta cosa è ancora necessario, non mantenere materiale superato confondibile; chiedere su ambiguità rilevanti senza inventare.
- Evidenze: letti script GPT/voce/Telegram, configurazione Telegram, percorsi dati e diagnostica; raccolti import di 60 moduli Python non-test del riferimento evoluto 5e61e53. Dipendenze dirette facoltative individuate: Vosk, sounddevice e Telethon; FFmpeg eseguibile per OGG/Opus, Node/npm e SDK fissato per GPT, SAPI/PowerShell Windows per TTS. Nessuna installazione eseguita.
- Contraddizioni reali: README/guida voce/LEGGIMI/echo launcher citano microfono ON, mentre codice corretto e preparatore avviano in standby; documentazione vecchia non va seguita alla cieca. Launcher usa profilo Trial, SDK/modello possono restare condivisi nel profilo base.
- Previsto: cartella Prima-installazione con guida iniziale, moduli, ripristino e diagnostica, più regole manutenzione/riordino; nessuna cancellazione di sorgenti o aggiunta di funzioni runtime durante questa fase.

## 2026-11-01 — In corso: completamento guide e criterio di consegna
- Create nove guide in Prima-installazione su main, da verificare nei riferimenti; nessuna build applicativa nuova. Ultimo commit guide 238be19be7ee0f1036b42aa7863219fc7962c71b.
- Nuova richiesta: non annunciare una funzione/add-on come implementata e installabile finché il pacchetto verificato non è pubblicato e linkato in Download/README.md con download funzionante. Prima riportare soltanto lo stato intermedio reale.
- Previsto: collegare le guide dall'ingresso principale, salvare regole su manutenzione/riordino/domande e consegna, verificare i file e chiudere il checkpoint. Nessun pacchetto o link Download fittizio da creare.

## 2026-11-01 — Completate guide e regole di consegna/risorse
- Nove guide in Prima-installazione: base, requisiti, GPT, voce, Telegram, moduli/add-on, reinstallazione, componenti mancanti e manutenzione. Fonti: script/codice del riferimento 5e61e53 e documentazione esterna indicata. README principale ora rimanda alla guida aggiornata.
- Verifica documentale: riletti tutti e nove i file, presenti e non vuoti; collegamenti locali fra guide risolti. Nessuna installazione Windows o test runtime svolti per queste modifiche; non equivalgono a certificazione della procedura sul Pavilion.
- Contraddizioni storiche inventariate; nessun sorgente/launcher/pacchetto eliminato. Unificazione messaggi componenti mancanti in chat resta da implementare, distinta dai controlli già presenti.
- Regole aggiornate: mantenere istruzioni di ogni modulo, verificare l'uso prima del riordino, chiedere su dubbi sostanziali, nessuna dichiarazione di funzione installabile prima di pacchetto verificato e link Download/README.md funzionante.
- Ulteriore requisito: ogni add-on progettata per Pavilion i3-2100/10 GB con poco consumo incrementale, caricamento a richiesta e misure comparabili; non spegnere microfono/servizi manuali. Commit regola 9a87cf1d08a387d5083b1e93acf7939394e3ea56, piano e9d3565dc233e9a7a64929eef3aafda0559b0791, lezioni fa98ef609165352baccb5843e311f15c9e024141.
- Stato reale: documentazione salvata; nessuna nuova build o add-on scaricabile pubblicata, nessun benchmark RAM. Prossimo passo resta revisione tecnica del piano web e dei punti d'integrazione, prima del codice.

## 2026-11-01 — In corso: scelta esplicita di instradamento ibrido
- L'utente conferma che un comando locale preciso non deve interrogare GPT. Le formulazioni ambigue/non riconosciute richiedono interpretazione del GPT esterno, che restituisce l'azione al motore; se resta dubbio, domanda contestuale e conferma breve.
- Rilettura sorgenti: jarvis.py 2894–2981 e 3038–3050, voice_control.py 45–85 nel riferimento evoluto. I gestori locali hanno precedenza; in Conversazione GPT esiste fallback, mentre altre modalità possono limitarsi a inserire il testo. Non interpretare questa preferenza come richiesta di mandare ogni comando a GPT o cambiare automaticamente modalità microfono.
- Previsto: aggiornare regole, piano e lezioni; nessun codice modificato o test eseguito. Poi chiudere checkpoint.

## 2026-11-01 — Completata: decisione ibrida locale/GPT
- Regola in AGENTS.md fed120f5abeeb1c2e039d92fc4f57482f2f34595, piano 38a25509e2badeb87273a68275a1e3fd7c65e339, lezioni edd9126892b89beb86a7a568b8fe9d1a2acf72cc.
- Comando preciso riconosciuto localmente senza modello; richieste non risolte interpretate da GPT esterno con motore esecutore e chiarimenti contestuali. Nessun obbligo di interrogare GPT per ogni frase; preservare modalità manuali e connessione consentita.
- Nessun codice, nuovo test o pacchetto. Prossimo passo: revisione tecnica del piano e comportamento nelle modalità prima dell'implementazione autorizzata.

## 2026-11-01 — In corso: allineamento finale e arresto prima del codice
- Richiesta: completare l'allineamento del metodo e dei documenti, salvare un punto di ripresa pulito e fermarsi prima di implementare la nuova add-on.
- Controllo documentale: individuate formulazioni generiche sul passaggio GPT da precisare con la scelta ibrida finale; vecchia clausola di approvazione del nucleo superata dal piano già approvato e dalla correzione documentata. La politica di riuso/ricerca web va esplicitata.
- Previsto: correggere queste formulazioni, rendere univoci stato delle fasi e prossimo passo in piano/STATO/RECUPERO, registrare esito. Nessun codice, pacchetto o test runtime in questo allineamento.

## 2026-11-01 — In corso: catalogo persistente dei punti di ripristino
- L'utente precisa: decisioni tecniche tracciabili, riferimento funzionante dopo test automatici e prova PC, ZIP completo persistente in repository e recupero senza cercare fra artifact/commit.
- Verifica Download: 20 ZIP già versionati nel repository, più README. Presenza/file SHA osservati via API, non collaudo dei contenuti. Nessuno viene promosso automaticamente a versione stabile; il feedback dialogo sul PC non identifica ancora uno ZIP/SHA esatto.
- Previsto: registro in Download collegato all'indice, con stati/prove/limiti e procedura di recupero; aggiornare metodo e punto di arresto. Rimane il fermo prima dell'implementazione web.

## 2026-11-01 — Chiusura verificata: metodo allineato, recupero indicizzato, fermo prima del codice
- Allineamento documentale completato: corrette formulazioni conflittuali sul GPT e la clausola storica del nucleo già approvato; esplicitato confronto di soluzioni esistenti prima dello sviluppo nuovo. Commit iniziali dell'allineamento: AGENTS 377fcf77434d5c2fa6fd7d92f50dfeb2cb9510f6, piano 2705ca124fbe890b4dd3790d28fedd91479720fe, recupero 943b4ff237acba11961a3c2357b96a7040d10c12, stato f0623eceacba49173072ed0bcfcf32076a5bd49f; successivi aggiornamenti collegano il registro versioni.
- Registro Download/REGISTRO-VERSIONI.md creato nel commit 2e1785f050c47ad3cea9507c09d19110f6d953c1 e collegato in Download/README.md; contiene inventario di 20 ZIP con percorsi immutabili, byte e Git blob SHA. Confronto con directory Download al commit bb94afa1865fe0315021f783736be3cb77c4af84: tutti e 20 corrispondono. Questo prova presenza e riferimenti, non download/estrazione o funzionamento PC.
- Riletti AGENTS, RECUPERO, STATO-ATTIVITA, piano, registro versioni e Download/README: verificati percorso ibrido, clausola approvazione aggiornata, ricerca/riuso, fermo prima del codice, fasi pendenti e collegamento del registro. Esiti documentali tutti positivi. Nessuna nuova prova runtime o con nuova istanza.
- Decisioni tracciabili con fatti/fonti, alternative, motivazione tecnica sintetica, test/esito/limiti, commit e collegamento alla versione. I problemi vanno ricercati dai riferimenti puntuali, non ricostruendo l'intero progetto o il ragionamento privato.
- Nessun punto «funzionante al 100%» inventato: feedback PC sul dialogo positivo ma ZIP/SHA ancora non identificato. CI precedente distinta dai pacchetti precedenti. Le versioni future saranno promosse solo dopo prove automatiche e riscontro PC collegati al pacchetto esatto e all'ambito provato.
- Stato finale: metodo e documenti allineati; requisiti web raccolti; fase 1 tecnica parzialmente svolta e sospesa, revisione completa/contratto ancora da concludere; fasi 2–8 da fare. Nuova add-on non implementata, nessuna nuova build/ZIP, misura RAM, installazione, cancellazione di sorgenti, merge o ripristino.
- Prossimo passo unico: attendere la ripresa richiesta dall'utente, leggere indice e piano e completare la revisione tecnica web; non avviare codice o pubblicazione finché l'utente non darà il successivo via. Se chiede una versione precedente, leggere prima il registro e chiedere solo se il riferimento resta ambiguo.
