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
