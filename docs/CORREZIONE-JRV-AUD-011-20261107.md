# JRV-AUD-011 — timeout GPT e annullamento per richiesta

Stato: candidata nei sorgenti in bozza, GreenWindows ancora da acquisire.
Base010 `e65b5ebfa01fe83b7c6ec605da7df836a66ae42e`, [bozza45](https://github.com/MATRIXNEO23/jarvis/pull/45), ramo `fix/jrv-aud-011-gpt-timeout-20261107`.
[Specifica](superpowers/specs/2026-11-07-jrv-aud-011-design.md), [piano](superpowers/plans/2026-11-07-jrv-aud-011-fix.md).

## Causa e intervento minimo

`jarvis.run_gpt` assegnava40s a typed_conversation mentre ask/conversation ricevevano180s. Le stesse domande brevi scritte attraverso submit_gpt passavano proprio dal canale40s. GPTClient scartava già pacchetti tardivi per ID, ma al timeout non chiedeva al figlio di annullare l'inferenza.

|Componente|Intervento|Prove necessarie|
|---|---|---|
|jarvis.py/run_gpt|typed_conversation nel ramo180s; account600/40s conservati|Callback reale e tempi virtuali39/41/179/181s per tutti3canali, busy/epoca e nessun retry|
|gpt_client.py/call,_cancel_request|Timeoutask invia cancel_request solo al medesimo processo ancora posseduto; IDcontrollo unico senza pending/start/attesa. Errori pipe mantengono timeout e distinguono annullamento noninviato|Timeout reale breve su pipe controllata, cambio/detachprocesso, pacchetti vecchi/ack non trasferiti alla chiamata nuova, stato pending pulito|
|gpt_bridge.mjs/execute,shutdown|AbortController per ask prima del primoawait; signal a listModels/streamResponse, checkdopo await, cleanupfinally. CancelIDvalido ignoto=false, invalidorifiutato, shutdownabortcontrollerattivi|BridgeNode reale contro SDKfinto: streamcontemporanei entrambiattivi, session/models/stream, abortignorato, cleanup/ID/shutdown|

Riutilizzo verificato nel SDK ufficiale fissato a0a36fefe, types.ts/StreamResponseOptions.signal, index.ts/listModels/streamResponse, responses.ts/AbortSignal. Nessuna nuova dipendenza/installazione, API a consumo, policy permessi, routing azioni/microfono/memoria o modifica credenziali. La cancellazione non è una nuova inferenza. L'helper non chiama start, non registra un'attesa di controllo, non riusaID; latepacket resta ignorato anche se l'annullamento non riesce.

## Red e review

Windows2022 x64, `python -m unittest discover -s tests -v`.

|Fase|Source/run|Python/job|Esito|
|---|---|---|---|
|Red1|7a7589f74316959738811e254cf277638fa8223c /42351877630|3.11.9/128341566504|809test,11failure+2errori,145.413s|
|Red1|stesso|3.12.10/128341566394|809test,11failure+2errori,113.026s|

Tutti gli errori/fallimenti nel nuovo modulo011: timeout40anziché180, nessuncomandocancel/AbortSignal, comandi sconosciuti e nessuna risposta di annullamento/shutdown entro il bound della fixture. Red1 aveva un'asserzioneID99 incoerente conIDvalido ignoto, rimossa nella review preventiva; non è la prova del bug timeout. Red2source `53d674eac36254801d87d8883e4a7f35dc75cfa2`, run42352051679, amplia19test/811totali e usa gate espliciti al posto di ritardi200ms. Esito:16failure,0errori entrambi;3.11.9/job128342078144157.782s,3.12.10/job128342078389143.552s. Tutti nel nuovo modulo011,022/023 non osservati.

Review preventiva recepita: unknownID coerenti; due stream entrambi bloccati prima del cancel; cambio/detachowner nel client; gate SDKsession/late rilasciati da status dopoack; wording annullamento inviato/noninviato epropagazioneUI. Ricontrollo senza blocchi fixture residui. Review runtime indipendente readonly: nessun blocco rilevato, nessun test eseguito dal revisore. Shutdown provato con SDKcooperativo, non garanzia di exit immediato di qualunque SDK.

## Prima candidata: errore shutdown e correzione mirata

Sourcec6949e28/run42352333419 fallita:3.11.9/job128342938450,811test130.180s,1errore shutdown attesa processo3s, dopoack/risposteabort già riuscite. Stesso errore su3.12.10/job128342938224,811test174.701s;0failure/1errore entrambi. Nessun timeout allargato o assert rimosso. SourceNode22.12 `lib/internal/readline/interface.js:1354` usa EventEmitter.on direttamente; `lib/events.js:1112,1196` iterator.return rimuove listener ma non chiude Interface. Fonti: https://github.com/nodejs/node/blob/v22.12.0/lib/events.js e https://github.com/nodejs/node/blob/v22.12.0/lib/internal/readline/interface.js .

Il vecchio smoke test chiude stdin dal parent, GPTClient.stop lo tiene aperto durante wait: il nuovo test ha esposto un caso reale. Aggiunto input.close() esplicito prima del break di shutdown, che pausa stdin lasciando finire pending/flush senza process.exit. Causa/soluzione riesaminate indipendentemente in sola lettura; nuova candidata da verificare, non semplice retry del source fallito.

## Limiti e recupero

Abort è best effort: il messaggio conferma invio del comando alla pipe, non arresto remoto/ackserver o rimborso token. GetSession e refreshcredenziali del SDK possono terminare il proprio lavoro prima di osservare il segnale; non interrompere forzatamente la persistenza OAuth. Se il SDK ignora abort, il bridge rifiuta successo tardivo quando ritorna; Python ignora comunque pacchetti del requestID scaduto. Lo shutdown può ancora richiedere l'escalation stop già esistente.

Tempi39/41/179/181s simulati nel trasporto dei callback: non attese di minuti o qualità GPT. Client/reader e Nodebridge reali, SDK inferenza/sessione esplicitamente simulati inLOCALAPPDATAtemporaneo. Nessun account, rete, token, DPAPI reale o Windows10/i3-HDD testato. Nessun test funzionaleLinux, build/ZIP/merge/release/config/dati/credenziali utente.022/023 separati. Prima di build: Greencompleto, client/bridge coordinati nello ZIP estratto e collaudo SDK/account autorizzato su target. Ramo/bozza reversibili, main e001–010 conservati.
