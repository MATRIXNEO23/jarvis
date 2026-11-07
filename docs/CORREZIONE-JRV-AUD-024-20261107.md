# JRV-AUD-024 — timer scritto e durate in lettere

Correzione verificata nei sorgenti, non ancora distribuita. [PR55](https://github.com/MATRIXNEO23/jarvis/pull/55), source `f4fbf74e8e0f918cf67c2a879cba92f512b9d16e`. [Run Windows42418024579](https://github.com/MATRIXNEO23/jarvis/actions/runs/42418024579). La006 pubblicata resta invariata.

## Causa e intervento

`jarvis.py:send_console_input` ammetteva `try_timer_command` solo se il testo era riconosciuto come sveglia: «imposta timer6minuti» saltava il comando e arrivava al modello configurato. «avvia un timer» incontrava inoltre il filtro di avvio programmi. Il gate comune ora viene dopo file e prima del guard programmi, rispettando precedenze documenti e progetti pendenti. Invio/Invia mantiene la conversazione Gemma per richieste non operative.

`jarvis_timer.py:parse_timer_command` riconosceva cifre e qualsiasi menzione della parola timer. Ampliare quel comportamento a tutta la console avrebbe introdotto azioni per «non impostare timer6» o «spiegami un timer da6minuti». Ora si riconoscono interamente i comandi espliciti/controlli supportati; le menzioni negate o conversazionali non avviano/fermano il timer. Riutilizzata la mappa italiana già presente0–59, con un/una per unità; import differito per non creare un ciclo con Sveglia. «sei minuti» diventa360secondi, «due ore e trenta minuti»9000.

`sveglia/service.py:next_alarm` accetta «sette e trenta di mattina/del mattino»:07:30 di oggi o domani se già passato, e rifiuta ore pomeridiane qualificate come mattina. Consensi/add-on, impostazioni, file e cronologie preservati. Nessuna dipendenza o nuovo modello.

## Prove ed errori conservati

Red iniziale42417048902:914test/job,3failure comportamentali e2errori di fixture (Mock alarm non stringa, re assente). Secondo Red42417313290:918test/job,1failure e13errori nelle nuove fixture config-model per Path/re mancanti; non sono errori dell'app. Candidata928ebb9f/run42417636927:918test/job,0failure1error nella sola fixture Explorer esistente che non dichiarava try_timer_command; i7nuovi metodi passavano. Completato solo quel collaboratore nella fixture, assert originali conservati e runtime immutato.

Green finale: [{"id": 128540219645, "python": "3.12.10", "tests": 918, "seconds": 169.013, "failures": 0, "errors": 0, "skipped": 0}, {"id": 128540219761, "python": "3.11.9", "tests": 918, "seconds": 169.798, "failures": 0, "errors": 0, "skipped": 0}]. Sintassi/probe/Searchlive3.12 verificati nel workflow, servizio/fixture ripristinati. Review indipendente readonly e ricontrolli completati, nessun blocco residuo. [Evidenza completa](evidence/jrv-aud-024-fix-20261107.json).

Test tengono reali i callback console/timer e parser; modello, popup timer e alarm.arm sono confini controllati, configurazione/modello in directory temporanee. Verificati avvio360 una volta, controlli, timer senza durata, assenza dispatch modello per i comandi, fallback Gemma per richieste non operative, precedenze e rollover mattina. Nessun test acustico, GGUF reale o Windows10 fisico. Avvisi Tk delle vecchie fixture Mock restano visibili nei log; nessun errore soppresso.

## Stato e prossima consegna

Nessuna nuova build o pubblicazione,006 e profili personali non cambiati. Il pulsante esplicito Prova Gemma locale resta una prova del modello; corretti Invio/Invia della console. Per usare il fix sul PC serve un successivo pacchetto autorizzato e verificato dall'estratto; non attribuire questi918test al vecchio ZIP006.016 e023 restano aperti come prima. La nuova validazione del parser limita le frasi operative ai comandi riconosciuti: eventuali ulteriori sinonimi sono incrementi mirati, non una promessa di comprensione universale.
