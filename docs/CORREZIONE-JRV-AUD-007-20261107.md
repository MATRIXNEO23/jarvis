# JRV-AUD-007 — correzione verificata nei sorgenti in bozza

Jarvis scarta gli eventi vocali di una sessione precedente prima che possano produrre effetti nel consumer UI. Verificato su Windows CI; nessun nuovo pacchetto installabile, build, merge o modifica al Jarvis già presente sul PC.

Base `c9d1d29a085770744e1a1cc34fc7d5f2826ac35b`, bozza40. Source verificato `425bfc38c1232ca26c5d1939bda7f0f95b07c04e`, [bozza41](https://github.com/MATRIXNEO23/jarvis/pull/41), ramo `fix/jrv-aud-007-voice-generation-20261107`. Mantiene001–006 e il riproduttore007. [Specifica](superpowers/specs/2026-11-07-jrv-aud-007-design.md), [piano](superpowers/plans/2026-11-07-jrv-aud-007-fix.md), [evidenza](evidence/jrv-aud-007-fix-20261107.json).

## Problema e modifica

`VoiceController._report` controllava la generazione solo prima dell'enqueue e trasmetteva `(kind,value)`. La callback cambio modalità invalidava la sessione, ma `poll` reinterpretava un testo già accodato usando il modo attuale. Il problema è confermato dalla [verifica precedente](VERIFICA-JRV-AUD-007-20261107.md).

Modifica minima in due file esistenti:

- `voice_control.py:239-246`: `_report` invia `(kind,value,generation)`; `accepts_event(generation)` accetta soltanto interi esatti della sessione corrente con controller aperto e modo attivo. Il lock esistente protegge la verifica, senza coprire callback o dispatch UI.
- `jarvis.py:3244-3252`: prima degli handler, soltanto per `voice_text/voice_status`, rifiuta payload senza identità, tipo/lunghezza non validi o generazione scaduta. Anche log, campione vocale, telemetria e dettatura sono protetti. Gli handler e gli altri eventi non cambiano.

Nessuna coda parallela, svuotamento globale, dipendenza, timer, processo o migrazione dati. Unico produttore vocale verificato nel sorgente; non accettare le vecchie tuple senza identità, perché riaprirebbero il difetto. Correzione nel nucleo esistente, senza duplicarla in un add-on.

## Prove Windows

Comando: `python -m unittest discover -s tests -v`, Windows Server2022 x64.

| Fase | Source/run | Python e job | Risultato |
|---|---|---|---|
|Red originale|2632321 /42340988254|3.11.9/128308391527 e3.12.10/128308391854|723 test per job,9 fallimenti007,0 errori.|
|Red ampliato|887e3db /42342113095|3.11.9/128311857151|729 test/153.433s,24 fallimenti007 e1errore023: timeout15s fixture Explorer.|
|Red ampliato|887e3db /42342113095|3.12.10/128311857388|729 test/167.838s,24 fallimenti007,0 errori.|
|Green|425bfc3 /[42342496402](https://github.com/MATRIXNEO23/jarvis/actions/runs/42342496402)|3.11.9/128313038365|730 test/159.103s,0 fallimenti/errori/skip.|
|Green|425bfc3 /42342496402|3.12.10/128313038104|730 test/113.337s,0 fallimenti/errori/skip.|

Green al primo tentativo sulla candidata, senza retry. Tutti i14 metodi del riproduttore passano. I7 metodi originali mantengono le asserzioni della verifica Red.

Copertura: vecchi comandi locali ignorati in GPT/continuo/PTT; vecchie richieste modello ignorate in GPT/continuo; frase senza hotword non reinterpretata dopo cambio modo; avvisi scaduti senza effetti UI/log/campione/telemetria/dettatura; close revoca eventi in attesa; payload errato non ferma il successivo evento valido. Una frase nuova passa esattamente una volta; status ed errore corrente mantengono feedback e arresto dettatura; un risultato TTS tra frase vecchia e nuova resta elaborato.

Le tracce mostrano generazione1→3 con dispatcher locale/modello ora0, mentre il controllo corrente3→3 produce1comando locale; richiesta corrente al modello produce1avvio e0comandi locali. Sono confini controllati: non apertura effettiva di browser né invio a GPT.

Sintassi Python/JavaScript/PowerShell e probe nativo file superati in entrambi i job. Windows Search live3.12 superato con servizio ripristinato e fixture rimossa; il live3.11 non è previsto. Build, pacchetto estratto e pubblicazione saltati intenzionalmente.

## Review, lezioni e limiti

Review indipendente in sola lettura: nessun difetto runtime concreto o blocco residuo. Due lacune minori dei test recepite: dettatura attiva nel modo continuo realmente raggiungibile, più controllo positivo errore corrente con log/telemetria/disattivazione. Il Red ampliato iniziale aveva la fixture dettatura in GPT; non usarla come prova del percorso UI raggiungibile. Il Green usa continuo; i riproduttori originali restano invariati. Il nuovo test dell'errore corrente è caratterizzazione, non un ulteriore Red dichiarato. Il revisore non ha eseguito test.

Lezione: un controllo prima dell'enqueue non revoca messaggi già consegnati alla coda. Conservare l'identità e controllarla al consumo, prima di qualunque effetto. Non cancellare risultati estranei per scartare quelli vecchi.

Queue/controller/cambio modalità/loop dispatch reali; trascrizioni, audio startup e confini di azione/modello controllati. L'estrazione AST omette il preambolo esterno del poll sotto fixture aperta/documenti inattivi. Nessun microfono/Vosk acustico, account GPT/Telegram, inferenza GGUF o misurazione Windows10/i3/HDD/RAM/CPU reale. Nessun test funzionale Linux.

La correzione riguarda eventi ancora in attesa al controllo iniziale. Non dimostra revoca di un evento già in esecuzione durante dialoghi modali, cambi progetto o PTT release/press senza cambio modalità. Nessun comportamento nuovo per questi casi. Permessi, modalità/hotword, profili, cronologie e progetti conservati; nessuna configurazione utente modificata.

022 resta aperto e non riprodotto nel Green.023 resta aperto: timeout riprodotto nel Red ampliato3.11, poi stessa fixture passata nel Green senza modificarla; non è stato corretto da007. I documenti Red precedenti restano storici e la bozza40 resta il riproduttore; la correzione è nella41 dipendente, senza merge automatico.

Prossimo passo soltanto al successivo via: verificare se008, propagazione dei parametri Gemma salvati, è ancora riproducibile dopo005. Fermarsi qui; nessuna build automatica.
