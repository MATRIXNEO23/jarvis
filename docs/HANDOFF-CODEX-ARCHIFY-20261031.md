# Handoff Jarvis → Codex — 2026-10-31

## Checkpoint vigente — struttura approvata e modularità persistente, 2026-11-01
Utente approva «dischi/cartelle selezionabili, sottocartelle incluse, eccezioni» prima delle scritture. Registrare come requisito confermato, non più soltanto proposta; dettagli tecnici/prove ancora da completare. Primo incremento generale in sola lettura, sistema protetto e diritti Windows rispettati; nessun via implicito a scritture/cancellazioni o modifiche ACL.
Regola esplicita per tutte le add-on: propria cartella, codice in file comprensibili divisi per responsabilità, evitare un singolo file di migliaia di righe. Esempi UI/policy-accesso/ricerca/configurazione da adattare al codice reale, nessun tetto righe inventato. LEGGIMI mappa compiti, test e import/pacchetto verificati dopo realizzazione. Riuso senza doppioni e niente migrazione automatica del nucleo.
AGENTS, scheda WINDOWS, STATO e lezioni aggiornati e riletti: quattro contenuti coincidenti ai salvataggi. **Stato:** documentazione/regole soltanto; nessun codice, file runtime spostato, nuovo test, benchmark o pacchetto. Base b936879 preservata. **Prossimo passo:** completare inventario/contratto e revisione mirata dell'accesso file generale con queste decisioni, prima del via al codice. Non chiedere una singola app campione come prerequisito; UI deve restare semplice e spiegazioni un punto alla volta.

## Checkpoint vigente — proposta selezione cartelle e fonti esistenti, 2026-11-01 pomeriggio
L'utente propone selezione con spunte di unità/cartelle/sottocartelle e chiede interfaccia semplice; dettagli ancora da discutere. Proposta in WINDOWS: radici selezionabili, ereditarietà, eccezioni espandibili, stato parziale e riepilogo chiaro; caricamento sottocartelle su espansione senza scansione completa. Primo incremento sola lettura, protezione sistema non superata dalla spunta. La spunta autorizza Jarvis ma non concede diritti Windows/ACL/UAC. addon_ui.py base letto: esiste pannello gestore, configuratore cartelle da realizzare senza duplicarlo.
Su richiesta cercate/aperti fonti primarie Everything Options/Exclude, Syncthing Ignoring Files e Microsoft Known Folders/WRP/SfcIsFileProtected. Tutti i riferimenti e limiti salvati: esempi per UI/regole, Windows per percorsi/protezioni; non installare quei programmi per le sole spunte, nessuna licenza/codice di riuso ancora selezionati. Filtri indice non sono controlli accesso; attributo system e risposta WRP negativa non classificano universalmente il sistema. Nessun database universale verificato. API Windows non provate sul PC.
Scheda WINDOWS, STATO e lezioni aggiornati/riletti, contenuti coincidenti; includono anche la precedente proposta UI. **Stato:** proposta e ricerca documentale soltanto, nessun codice, nuova UI, dipendenza, modifica permessi, test runtime/Windows, benchmark o pacchetto. Base b936879 preservata. **Prossimo passo:** spiegare riferimenti e proposta concreta all'utente, recepire correzioni e completare contratto/verifiche mirate prima dell'implementazione. Priorità resta accesso generale ai file, non una singola app campione.

## Checkpoint vigente — accesso generale e profilo Windows automatico, 2026-11-01 pomeriggio
La priorità precedente «app classiche/Store» è superata dall'utente: partire dall'accesso file/cartelle generale, non limitato a una sola app o Download. Esempi di programma sono campioni di collaudo, non prerequisiti: non chiedere ancora quale app per iniziare. Primo incremento accettato in sola lettura fuori dall'area di sistema; obiettivo futuro lettura/scrittura/cancellazione fuori dal sistema e sistema solo lettura. Confine e permessi reali da verificare; il «sì» al primo passo non approva Cestino o modifiche a dati concreti.
Nuova capacità come .jaddon nell'organizzazione add-on prevista, propria cartella/LEGGIMI e tutti i requisiti già raccolti: riuso senza doppioni, dialogo e catalogo, basso consumo, test, pacchetto essenziale, configurazione/recupero e console dipendenze. Non ridurre l'aderenza ai requisiti alla sola collocazione del file manifest.
Richiesta aggiunta: rilevare account/profilo Windows attivo e cartelle reali automaticamente; niente nomi/percorso ricostruiti dalla chat. Fonti Microsoft profilo/Known Folders lette e salvate nella scheda WINDOWS, inclusi reindirizzamenti e test da fare. Windows Search primo candidato con copertura/servizio verificabili, ricerca mirata dove necessario, non scansione continua né falsa assenza fuori dall'indice. Identificare app dal contesto o da evidenza reale, chiedere solo quando mancante.
Scheda WINDOWS, STATO e lezioni aggiornati; ultime tre riletture coincidono con i salvataggi e includono i requisiti precedenti sull'ambito generale. **Stato:** sola documentazione e verifica fonti; nessun codice, add-on, nuovo test runtime, pacchetto, benchmark o accesso al PC utente. Base b936879 e ZIP preservati, browser sospeso. **Prossimo passo:** progetto/contratto generale basato sui gestori esistenti e revisione mirata prima dell'implementazione; spiegare all'utente semplicemente senza restringere il prodotto a un'app campione.

## Checkpoint vigente — proposta dialogo/Windows pronta, 2026-11-01
Chiarimento dell'obiettivo salvato nella scheda WINDOWS, STATO e lezioni; tre file riletti e coincidenti ai salvataggi. Jarvis deve distinguere conversazione/azione/chiarimento col contesto, locale diretto per comandi precisi e GPT esterno per interpretazione necessaria, senza ripetere domande risolte. Risposta breve riprende attività pendente; niente azioni da semplici menzioni. Frasi personali «Insegna comando» sono opzione discussa, non il requisito centrale o una funzione già approvata. Requisiti di immediatezza e prove su dialoghi completi documentati.
Primo incremento scelto: app classiche/Store rilevate con Windows e selezionate nelle impostazioni, apertura corretta da voce/testo; ricerca file e lettura estese per fasi riusando gestori esistenti. Piano, cartelle chiare, ZIP operativo essenziale e console con rimedi precisi già salvati. Fonti Microsoft Cortana/WSR/Accesso vocale Windows 11 registrate, nessuna sostituzione automatica del riconoscimento esistente.
**Stato reale:** proposta e requisiti allineati/documentati; codice Jarvis invariato, nessuna nuova add-on, build, prova d'integrazione Windows o misura prestazionale. Base b936879 e pacchetti preservati; browser sospeso. Non presentare questa chiusura come implementazione funzionante. **Prossimo passo:** alla ripresa spiegare proposta/ambito e completare inventario/contratto/revisione mirata prima del via al codice. Utente chiede al termine soltanto «finito»; non avviare nuove attività da questa attesa.

## Checkpoint attuale — primo incremento programmi classici/Store, 2026-11-01
Utente sceglie di partire dall'apertura programmi con rilevamento classici/Store, spunte nelle impostazioni e app corretta da voce (esempio Netflix). Comportamento/piano e fonti Microsoft aggiunti in WINDOWS, stato e lezioni; tre file riletti, contenuti coincidenti. Documentazione Get-StartApps/AppsFolder, AUMID e ActivateApplication consultata: meccanismi nativi disponibili, non prova di integrazione Jarvis o delle app reali sul PC.
Elenco selezionabile unico con identità/avvio reale, stato rilevata distinto da prova apertura, catalogo coerente e interpretazione naturale. Proposta «Prova apertura» della voce selezionata; non aprire tutte le app durante inventario. Nessun ID/percorso Netflix hardcoded o sostituzione implicita con sito. Chiarire se ambigua; non promettere inventario universale di programmi non registrati.
**Stato:** requisiti e progetto preliminare soltanto; nessun codice, nuovo test runtime/Windows, benchmark o pacchetto. Base b936879 preservata, browser sospeso. **Prossimo passo:** spiegare il percorso con esempio concreto e completare inventario/contratto e revisione mirata sul gestore esistente prima del via al codice. L'utente vuole un percorso completo funzionante, non solo lista o pulsante: test voce/testo → selezione → azione → esito e riscontro PC separato.

## Checkpoint attuale — consegna essenziale e componenti mancanti, 2026-11-01
Metodo in AGENTS/RECUPERO da leggere da ogni istanza con accesso al repository; non garantisce accesso automatico in altre chat. Requisiti ZIP operativo e console salvati in AGENTS, scheda WINDOWS, STATO e lezioni; RECUPERO aggiornato. Riletture dei cinque documenti ZIP e dei quattro successivi aggiornamenti console: contenuti coincidenti ai salvataggi.
Publisher b936879 letto: seleziona git ls-files salvo ZIP Download, non una lista runtime. Prossime consegne autorizzate dovranno selezionare file necessari con dipendenze/risorse/launcher/installazione e istruzioni essenziali, includendo sorgenti direttamente eseguiti; lasciare strumenti/test/handoff di sviluppo nella repository. Verifica sul pacchetto estratto, base e ZIP storici preservati. Nessuna ripacchettizzazione o modifica workflow eseguita.
Nuovo requisito console: indicare add-on/file/dipendenza mancante con nome esatto, funzione interessata, rimedio locale o nome/link verificato per il download; per file interni percorso e pacchetto corretto. Distinguere mancante, incompatibile, non configurato e accesso negato; ricontrollo finito dopo il rimedio. Letti installa_telegram.bat e telegram_voice.py: Telethon installabile da script, rilevatori FFmpeg/SAPI/Vosk già presenti parzialmente; riusarli, niente duplicati o scanner continuo. Copertura console unificata e link di consegna non implementati/verificati ora.
**Stato:** soltanto piano/regole documentali; nessun codice, build, nuovo test runtime/Windows o benchmark. **Prossimo passo:** spiegare il piano semplicemente e definire primo incremento/ambito cartelle/formati prima del via al codice. Browser ancora sospeso; base b936879 invariata.

## Checkpoint corrente — piano Windows e organizzazione concordati, 2026-11-01
Requisiti precisati nella [scheda WINDOWS](implementabili/WINDOWS.md): ricerca/apertura e lettura/spiegazione entrambe richieste; nome parziale/prefisso o indizi/scopo, esempio cartella installazione Minecraft. Cercare evidenze locali e distinguere programma/dati/salvataggi; nessun percorso inventato o garanzia con zero indizi. Ambito cartelle/formati ancora da definire, non ripetere la domanda «anche lettura?».
Piano proposto in cinque fasi salvato: inventario responsabilità/limite/modifica/test, prova Windows minima, miglioramento percorso completo, ricerca/lettura per incrementi e verifiche/consegna/ritorno versione. Migliorare funzioni esistenti senza doppioni; add-on soltanto dove nuova o motivata, non per ricreare un'azione esistente. Riuso Windows/codice prima delle dipendenze nuove, valutazione tecnica a carico dell'assistente.
Richiesta organizzativa: propria cartella riconoscibile per nuove add-on/moduli, LEGGIMI con mappa di sorgenti/risorse/test e percorsi reali di manifest/configurazioni/dati. Struttura da verificare col gestore; non duplicare dati o migrare automaticamente codice esistente. Regole AGENTS, scheda, STATO e lezioni aggiornate e rilette: quattro contenuti identici ai salvataggi. Nessun file runtime spostato, codice, nuova add-on, suite, benchmark o pacchetto realizzato.
Guida semplice, un punto/domanda alla volta e spazio all'utente per terminare. **Prossimo passo:** spiegare il piano con esempio concreto, chiarire ambito cartelle/formati e delimitare il primo incremento prima dell'implementazione. La richiesta attuale autorizza pianificazione/documentazione, non avvio automatico del codice. Base b936879 e pacchetti preservati; browser resta sospeso.

## Checkpoint attuale — requisiti Windows e minimo peso, 2026-11-01
Scheda [WINDOWS](implementabili/WINDOWS.md) salvata con caratteristiche richieste, evidenze sorgenti b936879 e fonti Microsoft. Indice, STATO e lezioni aggiornati; quattro documenti riletti, contenuti coincidenti. Nessun codice/test runtime/pacchetto modificato o benchmark svolto.
Chiarimento dell'utente: usare prima funzioni Windows e codice già presenti se soddisfano il requisito; nuove dipendenze ammesse solo se giustificate. Valutazione di peso/affidabilità/manutenzione a carico dell'assistente. Add-on logica non equivale a nuova dipendenza. Funzioni richieste: file/cartelle, ricerca/apertura, programmi scelti nelle impostazioni, frase naturale con interpretazione GPT quando serve e elenco «cosa puoi fare?» aggiornato.
Fattibilità preliminare positiva, integrazione da progettare. Limiti attuali verificati: ricerca solo Download e programmi fissi; pannello programmi configurabili non presente nei file letti. Windows fornisce apertura e identificazione app/ricerca indicizzata, ma installazioni reali, copertura indice e consumi PC non verificati. Prossimo passo: discutere cosa intende per «verificare file» e dove cercare, poi definire percorso minimo. Nessun via al codice in questa richiesta; browser ancora sospeso.

## Checkpoint corrente — schede progetto salvate, discussione prima del codice
2026-11-01: creati [indice implementabili](IMPLEMENTABILI.md), [modello](implementabili/MODELLO.md) e schede web, cronometro e promemoria. Le ultime due sono suggerimenti dell'assistente, non funzioni approvate. Browser resta sospeso senza priorità automatica: l'utente vuole prima discutere altre funzioni e definire ogni progetto.
Chiarimento esplicito: «prendere appunti» significa documentare caratteristiche e decisioni nella repository per il recupero dell'assistente, non sviluppare appunti vocali in Jarvis. Proposta errata ritirata, file APPUNTI.md eliminato nel commit 6fa1690b2041215c9e7076e9ff8d5ff05f6a4524 e riferimento tolto dall'indice. Cronologia Git conservata.
Collegati indice/schede da AGENTS, RECUPERO e STATO; lezione registrata. Riletti via API i nove file nuovi/aggiornati (escluso questo checkpoint): contenuti uguali a quelli salvati. Schede/modello presenti, riferimenti interni all'indice coerenti con i file creati. Nessun test runtime o nuova misura, codice/pacchetti/base b936879 invariati. La verifica è documentale, non una prova con una futura sessione.
**Prossimo passo:** discutere le funzioni desiderate con l'utente; salvare caratteristiche concordate, proposte, decisioni, prove e prossimo passo nella relativa scheda. Alla ripresa aprire indice e scheda, verificare fonti pertinenti. Nessuna implementazione autorizzata da questa richiesta; il precedente prossimo passo web è subordinato alla scelta di priorità.

## Checkpoint vigente — allineamento concreto completato il 2026-11-01
**Dopo «Continua»: audit chiuso e fermo prima del web.** Base confermata Jarvis-Timer-Audio-Fix2-20261031.zip, sorgenti b936879a431370d206152be7b089baf587d15499; 155 file identici, download diretto HTTP 200, hash/CRC PASS. Suite locale: 373 raccolti, 368 eseguiti con successo, 5 skip Windows/Tk, zero fallimenti/errori; sintassi Python/Node PASS. CI storica della base e publisher verificate; riferimenti nel [rapporto](VERIFICA-CONCRETA-BASE-20261101.md) e nel [registro](../Download/REGISTRO-VERSIONI.md).
Il nucleo successivo a86c2c9 e il suo standby non sono nello ZIP. Guide, indice, regole e piano distinguono le due versioni; mantenere la base e il comportamento scelti. Feedback PC riferito dall'utente, nessun nuovo collaudo hardware/account. La mappa Archify a86c2c9 resta riferimento del solo codice successivo, con limite browser già documentato.
Conservati aggiornamenti documentali concorrenti ed evidenze canoniche in docs/evidence/base-20261101; nessun duplicato di manifest o log. Controllati anche 20 ZIP, copertura gestore esistente e DDL dei due archivi. Nessuna modifica runtime/ZIP, installazione, migrazione, invio, cancellazione, merge di rami funzionali o nuova distribuzione.
File aggiornati in questa chiusura: istruzioni/recupero/stato, handoff/lezioni, rapporto, catalogo/registro Download, guida dati e JSON delle verifiche. Controlli finali dei collegamenti e dello scope registrati in package-checks.json. I vecchi stati «in corso» o «nome ZIP da confermare» sotto sono cronologia superata da questo checkpoint.
**Prossimo passo unico:** attendere il successivo via; poi completare fase 1 tecnica web sulla base b936879 (ricerca di soluzioni, confronto riuso/adattamento, contratto e test di accettazione), presentare il risultato prima del codice. Fasi 2–8 non avviate. Non chiedere nuovamente quale ZIP usa l'utente.

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

## 2026-11-01 — In corso: base funzionante indicata dall'utente
- Alberto conferma che l'ultima build che sta usando funziona bene per il momento e chiede di mantenerla come base da cui migliorare e a cui tornare in caso di regressioni.
- Registrare il riscontro come BASE-UTENTE-20261101; ambito: uso riferito, non prova universale. Associazione al nome ZIP/SHA installato ancora da confermare: in cima Download/README figura Jarvis-Timer-Audio-Fix2-20261031.zip, candidato da verificare con l'utente.
- Previsto: aggiornare registro/stato/lezioni, chiedere una sola conferma identificativa, nessuna build o ripristino.

## 2026-11-01 — Riscontro della base salvato, identificazione ZIP pendente
- BASE-UTENTE-20261101 registrata come build attuale funzionante nell'uso riferito dall'utente. Registro aggiornato commit cae5e5d16fae3c9b300c53de987afb6b83764daa; stato e lezioni coerenti.
- Resta una sola conferma identificativa: il pacchetto usato è Jarvis-Timer-Audio-Fix2-20261031.zip, quello in cima a Download? Non associare il candidato o a86c2c9 senza riscontro.
- Preservare la base e ripartire dal suo codice verificato nelle prossime aggiunte. Nessun codice, nuovo test, pacchetto o ripristino in questa fase; fermo prima dell'implementazione mantenuto.

## 2026-11-01 — In corso: identificazione della base confermata
- L'utente chiarisce che la build funzionante è il primo file scaricabile in cima a Download/README.md.
- Riletto il catalogo: primo ZIP Jarvis-Timer-Audio-Fix2-20261031.zip. Metadati directory verificati: 406653 byte, Git blob SHA 6aa9e6f9eb040dc7390b4edb55c9ae175bd4e512, uguali al riferimento immutabile inventariato.
- Aggiornare il puntatore BASE-UTENTE-20261101 con nome esatto e conferma PC; nessuna domanda identificativa ulteriore necessaria. Commit sorgente interno della ZIP ancora da associare prima di modificarne il codice; non attribuire automaticamente a86c2c9.

## 2026-11-01 — In corso: verifica concreta autorizzata della base
- L'utente richiede di pianificare e avviare le verifiche concrete per allineare i dati, senza deduzioni inventate. Piano in docs/VERIFICA-CONCRETA-BASE-20261101.md.
- ZIP reale acquisito: 406653 byte, blob 6aa9e6f9eb040dc7390b4edb55c9ae175bd4e512, SHA-256 c37270265918c63ddb3a9cf6a2c0982d468dd1af83a1af330c5af1dfb20f9352. CRC/percorso/estrazione: PASS, 155 voci. Baseline utente identificata; confronto sorgenti e test inclusi prossimi.
- Nessun codice modificato né add-on iniziata; questo audit è autorizzato, la successiva implementazione resta sospesa.

## 2026-11-01 — Ripresa audit concreto dopo «Continua»
- Punto verificato: main c6f0170497f8b2c0b4511950bd722e681cef02b6; lette istruzioni e fonti di recupero correnti. Le vecchie copie locali con modifiche non salvate restano separate e non sono la base.
- Unità in corso: confrontare i byte dello ZIP confermato con la storia sorgente; eseguire suite inclusa e sintassi disponibili; verificare guide, mappa e riferimenti. Annotare difetti senza correggere il runtime durante questo audit.
- File previsti: rapporto VERIFICA-CONCRETA-BASE, evidenze sintetiche/log di test, registro versioni, indice sorgenti, stato, recupero, piano, lezioni e questo handoff. Nessuna nuova add-on, build, installazione o modifica dei dati utente.
- Arresto richiesto: allineamento del metodo e dei dati reali; presentare esito e limiti, fermarsi prima del codice web. Il precedente prossimo passo generico «revisione web» è subordinato alla chiusura di questo audit.

## 2026-11-01 — Audit fasi 1–3 verificato, allineamento documenti in corso
- Download diretto HTTP 200, 406653 byte e SHA-256 c37270265918c63ddb3a9cf6a2c0982d468dd1af83a1af330c5af1dfb20f9352; byte identici allo ZIP versionato. CRC e percorsi PASS.
- Tutti i 155 file dell'archivio coincidono con b936879a431370d206152be7b089baf587d15499. Conferma indipendente dal log del job 124620508446, run 41229495866 SUCCESS: SOURCE_COMMIT, FILES, ZIP_BYTES e SHA256 corrispondono.
- Sullo ZIP estratto: Python 3.12.14, Linux; 373 test, OK, 5 skip Windows/Tk; compileall e node --check (Node 24.22.1) PASS. La prova locale non copre login, audio, microfono o Windows reale.
- Rispetto al ramo 5e61e53: 145 file identici, 10 modificati e 5 aggiunti; correzione a86c2c9 assente dallo ZIP. Baseline avvia il microfono secondo auto_listen; codice successivo impone standby. Nessun cambio runtime autorizzato in questo audit.
- Restano aggiornamento dei documenti e controllo finale dei riferimenti. Nessuna implementazione web o nuova distribuzione.
