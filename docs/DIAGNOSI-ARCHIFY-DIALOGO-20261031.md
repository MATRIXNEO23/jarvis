# Diagnosi Jarvis con Archify — 31 ottobre 2026

## Identità e perimetro
- Main all'inizio: `2e10d52cb576dcbf7f000b4ada00e9ef08b0a1d1`, checkout pulito.
- Main contiene sorgenti storici alla radice e il catalogo Download: non coincide con l'app evoluta distribuita negli ZIP. La suite alla radice esegue solo 31 test, PASS locale.
- Sorgenti evoluti esaminati separatamente: `feature/timer-settings-ui-20261031`, commit `1f7310f67887dcc756646513151c90b3d12ac703`, PR #32 aperta verso `feature/hud-reference-ui-20261031`, non main. Nessun merge effettuato.
- Letti integralmente handoff e skill Archify. Nessuna installazione nell'app, nessuna richiesta a modelli esterni o API a consumo.
- La successiva richiesta dell'utente autorizza la correzione dei due workflow; la modifica del runtime conversazionale resta proposta da approvare.

## Fase 1: cause reali dei due fallimenti
Esaminati tutti gli otto log dei job (Linux/Windows, Python 3.11/3.12) delle run:
- [41230403859](https://github.com/MATRIXNEO23/jarvis/actions/runs/41230403859)
- [41230414187](https://github.com/MATRIXNEO23/jarvis/actions/runs/41230414187)

Tutti falliscono esclusivamente in `test_second_brain.ShortTermTests.test_limited_history_and_clear`:
`AssertionError: 16 not less than or equal to 8`, riga 26.
373 test per job; Linux salta 5 test Windows. Sintassi Python/Node PASS. Il controllo PowerShell non viene raggiunto su Windows.

Il commit 8d439df porta MAX_TURNS da 8 a 16 e MAX_CONTEXT da 1050 a 2400 senza aggiornare il contratto nel test; il successivo 1f7310f modifica solo jarvis_persona.py, perciò eredita il fallimento. Non è un errore infrastrutturale né la prova di un guasto GPT.

### Correzione CI autorizzata
Commit `faba67363e07ea478241fbe549c45474aab5144a` sul ramo esistente:
- verifica esplicita dei 16 scambi trattenuti;
- verifica dell'ordine e dell'espulsione dei primi quattro dopo 20 inserimenti;
- verifica del limite predefinito 2400 e del budget richiesto 1050;
- verifica che l'ultimo scambio resti presente e che clear cancelli la RAM.

Non sono stati disabilitati test né ridotta la capacità conversazionale. Nessun file runtime o YAML modificato.
373 test locali: OK, skipped=5. Python 3.12.14, Node 24.22.1; compileall, node --check e git diff --check PASS.
Nuova run: [41232983494](https://github.com/MATRIXNEO23/jarvis/actions/runs/41232983494). Esito finale registrato nell'handoff.

## Fase 2: mappa Archify
[Mappa HTML](architecture-20261031/jarvis.html). La mappa cita i sorgenti del commit 1f7310f, non la vecchia radice main. Interfaccia del visualizzatore con fallback inglese; contenuto italiano.

Flusso ricostruito: voce/testo → orchestrazione jarvis.py → RAM e richiamo locale → prompt e catalogo → GPTClient Python → pipe JSON → bridge Node / SDK → modello GPT esterno → coda risultati → validazione locale → risposta e memorizzazione dello scambio completato.

Fonti principali nel ramo evoluto:
- jarvis.py:541–563: scrittura RAM e memoria persistente, distinta per progetto.
- jarvis.py:616–680: composizione contesto, focus e richiamo.
- jarvis.py:1807–1834 e 2724–2754: ingresso voce/testo e scelta prompt.
- conversation_memory.py:48–82: troncamento e selezione dei turni.
- conversation_router.py:133–159: budget add-on e memoria.
- jarvis_persona.py:84–105, 147–204: compattazione finale.
- gpt_client.py:129–156: ID richiesta, pipe e timeout.
- gpt_bridge.mjs:140–153: scelta modello e streamResponse.
- jarvis.py:3275–3285 e 3390–3402: memorizzazione delle risposte.

Archify: validate, deliver e check PASS, compresa verifica delle fonti contro il commit. browser-check NON ESEGUITO: manca Chrome/Chromium locale. Finalize esce con codice 2; non è dichiarato interamente riuscito. Nessuna ispezione visiva. Ricevuta e candidato conservati insieme alla mappa.

## Fase 3: perdita di coerenza — prove e limiti

| Rilievo dimostrato | Effetto |
|---|---|
| jarvis.py:618 chiede solo 860 caratteri alla RAM, benché MAX_CONTEXT sia 2400 | L'aumento a 16 turni non assicura più contesto al modello |
| conversation_router.py:155–158 limita nuovamente a 850 o allo spazio residuo | Ulteriore selezione e troncamento; stato runtime/catalogo riducono lo spazio |
| compact_memory legge breve/recent al livello principale e permanente.related, ma ignora permanente.recent | Gli ultimi turni SQLite recuperati da SecondBrain non arrivano al prompt dopo riavvio |
| Il catalogo add-on occupa lo spazio prima della riserva per la memoria | Con cataloghi grandi la memoria può essere ulteriormente ridotta o omessa |
| RAM, SQLite e compattatore tagliano prefissi delle risposte | Una scelta o domanda finale può andare persa |
| handle_unanchored_short_reply, jarvis.py:1042–1050, dipende solo da last_question RAM | Una risposta breve dopo riavvio può essere intercettata prima del modello |
| Il percorso progetto concatena tre recenti persistenti alla RAM, jarvis.py:654–664 | Scambi sovrapposti possono duplicarsi e consumare budget |

Riproduzione locale senza modello: cinque turni con domanda di circa 250 caratteri e risposta di circa 290 diventano due nel primo contesto da 860 caratteri; nel prompt finale lungo 4896 caratteri restano due turni troncati. Inserendo un marcatore in permanente.recent, esso non compare nel prompt. Questo prova perdite nella pipeline, non la qualità di una risposta GPT reale.

Il bridge passa `streamResponse({model, input: prompt})`: nessun ID di conversazione o risposta precedente è passato esplicitamente da Jarvis. L'ID numerico Python correla richieste IPC, non identifica la conversazione GPT. Non è stato verificato lo stato interno dell'SDK: non si afferma che il servizio esterno sia necessariamente privo di stato.

Non dimostrati: causa esatta di ogni episodio sul Pavilion; effetti del modello selezionato; trascrizione Vosk; eventuali timeout effettivi. Mancano traccia anonimizzata di una sessione problematica e prova con account collegato.

Ulteriore incongruenza preesistente: settings.py usa auto_listen=True e jarvis.py:3620–3622 avvia GPT_CONVERSATION quando abilitato. È in conflitto con la regola standby all'avvio dell'handoff. Il fix CI non modifica queste impostazioni; la distribuzione va bloccata finché il requisito non è chiarito/collaudato e rispettato.

## Piano minimo del nucleo — da approvare prima dell'implementazione
1. Unificare la preparazione del contesto per testo e voce: una sola selezione entro il limite esistente di 5000 caratteri, con spazio riservato alla memoria prima dei cataloghi opzionali; catalogo locale e controlli esecutivi restano autorevoli.
2. Consumare anche permanente.recent come fallback quando la RAM è vuota, normalizzare e deduplicare gli scambi. Conservare isolamento progetto/Telegram e opt-in Second Brain.
3. Conservare esplicitamente domanda pendente e riferimenti essenziali, evitando che il solo taglio del prefisso elimini il chiarimento. Nessun riassunto generato, nuovo servizio o modello.
4. Test di regressione: 6–10 turni con riferimenti iniziali/intermedi, domanda in coda a risposta lunga, cambio argomento, riavvio con memoria attiva/disattiva, cambio progetto, duplicati RAM/SQLite, catalogo add-on pieno, caratteri Unicode/escaping, nessun replay di comandi e nessuna falsa ricevuta di successo. Verificare il payload finale effettivamente passato al client, non solo i singoli moduli.
5. Eseguire suite completa e sintassi su Linux/Windows e Python 3.11/3.12; smoke IPC senza credenziali; prova reale Windows 10 per GPT multi-turno, microfono manuale e avvio in standby. Separare PASS automatico da collaudo Pavilion.
6. Preparare e verificare un pacchetto solo dopo questi controlli: integrità, file necessari e provenienza del commit. Pubblicazione esclusivamente dopo esiti verificabili; nessuno ZIP prodotto in questa fase.

La correzione CI è limitata ai test. Non equivale alla correzione della continuità conversazionale né alla validazione di un nuovo pacchetto.
