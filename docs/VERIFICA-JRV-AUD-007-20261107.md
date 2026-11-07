# JRV-AUD-007 — eventi vocali vecchi in coda

Verifica del 7 novembre 2026: **CONFERMATO, gravità ALTO** nel ramo evoluto con001–006. Questo passo aggiunge solo test e documentazione. Nessuna correzione al funzionamento, build o merge.

In parole semplici: Jarvis mette le frasi in una fila. Spegnere e riaccendere il microfono cambia sessione, ma una frase già nella fila perde l'indicazione della sessione originale. Quando arriva il suo turno, Jarvis può trattarla come nuova.

## Prova riproducibile

Base `7920c4d9c32049d49f848aef3af0006a037dfedf`; sorgente provato `2632321c258d9a20d44a7e6cbba8538476505412`; [bozza40](https://github.com/MATRIXNEO23/jarvis/pull/40), dipendente dalla39. Test: `tests/test_voice_queue_generation.py`, blob `30856c699fe4c797ab6e4b4567595f52ea712bf3`. [Evidenza strutturata](evidence/jrv-aud-007-20261107.json).

Comando CI: `python -m unittest discover -s tests -v`, Windows Server2022 x64, [run42340988254](https://github.com/MATRIXNEO23/jarvis/actions/runs/42340988254), conclusione **failure**.

| Python | Job | Test eseguiti | Fallimenti di comportamento | Errori fixture | Durata suite |
|---|---|---:|---:|---:|---:|
|3.11.9|128308391527|723|9|0|153.353s|
|3.12.10|128308391854|723|9|0|148.019s|

I9 fallimenti sono sottocasi di4 nuovi metodi; i3 nuovi metodi di controllo passano. Nessun altro test fallisce. Non è una suite verde e non dimostra una correzione: dimostra il problema.

Il test usa `_report` e `Queue` reali, la vera callback `change_voice_mode` e l'intero ciclo dequeue/dispatch di `poll`, compilati dal sorgente mediante AST. L'avvio del worker audio è sostituito; azioni e avvio conversazione sono osservatori senza effetti. Rimangono le guardie interne del ciclo. Sono esclusi soltanto scheduling e preambolo esterno, con applicazione aperta/documenti inattivi nella fixture.

| Scenario | Risultato osservato in entrambi i job |
|---|---|
|Comando locale accodato, OFF→ON|Una chiamata al dispatcher locale in GPT/continuo/PTT, sebbene la generazione originale sia scaduta. Esempio generazione1→3.|
|Richiesta modello accodata, OFF→ON|Una chiamata ad avvio conversazione in GPT/continuo, generazione1→3 oppure4→6.|
|Frase senza hotword in GPT, poi passaggio a continuo|Ignorata se consumata nel modo originale; inoltrata una volta al dispatcher locale dopo cambio modalità.|
|Avviso vocale accodato, OFF→ON|Lo stato precedente sostituisce il messaggio della sessione nuova in tutte e3 le modalità.|
|Restare in standby|Zero chiamate a comando locale/modello/file.|
|Produttore con generazione già scaduta|Non accoda più; il difetto riguarda gli eventi già accodati.|
|Frase corrente|Comando locale esattamente una volta in tutte e3 le modalità, modello zero. Richiesta modello corrente esattamente una volta in GPT/continuo, comando locale zero.|

## Causa, impatto e intervento futuro

| ID | Componente e righe | Evidenza | Impatto | Correzione candidata | Regressioni e test |
|---|---|---|---|---|---|
|JRV-AUD-007 — ALTO, CONFERMATO|`voice_control.py:175-190,234-241`, `VoiceController.set_mode/_is_current/_report`; `jarvis.py:2460,2807-2838,3244-3245,3371-3550`, `main/change_voice_mode/poll`|Il produttore controlla `_generation` ma accoda soltanto `(kind,value)`. La callback cambia generazione e svuota richieste conversazione, non identifica gli eventi vocali già accodati. Il consumer usa la modalità attuale senza verifica generazione;9 sottocasi Windows falliscono per questo comportamento.|Ingresso non voluto ai dispatcher locali/modello e stato UI errato. Le protezioni successive sulle singole azioni restano presenti; non è prova di esecuzione senza permessi.|Trasportare un'identità immutabile di sessione nell'evento vocale e verificarla nel consumer prima di stato, log, campione, dispatch o modello. Nessun nuovo servizio/add-on necessario.|Rischio MEDIO: formato notifiche condiviso, stato microfono, PTT/continuo/GPT e dettatura. Rendere verdi questi test; verificare gli altri tipi di evento, messaggi malformati, stato corrente e intera suite Windows.|

Correzione non applicata. Evitare uno svuotamento indiscriminato della coda condivisa: contiene anche risultati di altre operazioni. Conservare le regole attuali di hotword/modi, consensi, cronologie e configurazioni. Una futura correzione deve preservare comandi nuovi e disabilitazione manuale del microfono.

## Errori della verifica e limiti

Prima versione `e79b7f1`, run42340849694:722 test per job,5 fallimenti e6 errori perché mancava il mock UI `refresh_buttons`. Errore della fixture, non bug aggiuntivo di Jarvis. Corretto nel solo test con `29f442a`, run42340923269: job128308195955 osservato con722 test,9 fallimenti e0 errori. Versione finale2632321 aggiunge controlli positivi modello e frase senza hotword nel modo originale; la prova finale sopra supera questi limiti senza modificare il runtime.

Review indipendente in sola lettura: nessun blocco; lacuna minore del controllo positivo modello risolta e ricontrollata. Non ha eseguito test.

Sintassi Python/JavaScript superata su entrambi i job. PowerShell e probe nativo file saltati dopo il fallimento unitario, quindi non nuovamente verificati qui. Windows Search live3.12 superato; servizio ripristinato e fixture rimossa. Build, verifica pacchetto e pubblicazione saltate.

Nessun microfono/Vosk acustico, account GPT/Telegram, inferenza o programma desktop reale usato nella riproduzione007. Le chiamate osservate si fermano ai confini controllati: nessun consumo token o apertura reale dimostrati. Windows10/i3/HDD e frequenza del problema nell'uso reale non misurati. Non provati cambi progetto, PTT release/press nello stesso modo o interleaving durante dialoghi modali. Nessun test funzionale Linux.022/023 non riprodotti nel run finale e restano aperti; nessuna correzione dichiarata.

Prossimo passo, dopo il via dell'utente: correzione minima007 con questo riproduttore conservato, review e nuova suite Windows completa. Nessuna build automatica.
