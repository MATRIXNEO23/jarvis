# JRV-AUD-010 — timeout e arresto cooperativo di Gemma

Stato: correzione verificata nei sorgenti in bozza con ABI controllata su Windows. Nessuna nuova build installabile. Source verificato `060999046d6b232b4d3c05243c53f53b2b39fbd6`.
Base009 `6e6b0813789adc87435995a663cabaa4d0d48f6b`; [bozza44](https://github.com/MATRIXNEO23/jarvis/pull/44), ramo `fix/jrv-aud-010-native-cancel-20261107`.
[Specifica](superpowers/specs/2026-11-07-jrv-aud-010-design.md), [piano](superpowers/plans/2026-11-07-jrv-aud-010-fix.md), [evidenza](evidence/jrv-aud-010-fix-20261107.json).

Problema dimostrato: timeout controllato solo dopo la chiamata C; stop attendeva il lock dell'inferenza prima di abortire; close GUI non fermava l'owner nativo e il getter poteva crearlo a chiusura iniziata.

Interventi mirati nei responsabili esistenti:

- `native_bridge.py`, load/generate/abort: Timer richiede abort alla deadline della generazione, con revoca e join prima del riuso. Check annullamento prima/dopo init/load e prima dell'ingresso C; errore di abort non diventa eccezione silenziosa del Timer. Timeout distinto da stop e risultato tardivo rifiutato. True/NaN/Inf non sono timeout validi.
- `native_chat_adapter.py`, prepare/call: riferimento provider stabile mentre stop lo detacha. Nessun nuovo provider caricato su C ancora attivo.
- `native_conversation_session.py`, entrypoint/commit/stop/close: revisione prima dell'attesa revoca attive/in coda e turni differiti; metadata lock breve separato dall'inferenza. Stop manda abort prima di attendere reset e permette recupero; close è terminale e non prende il lock inferenza. Prova esplicita usa reset privato, preservando reload005. Storia già accettata conservata.
- `jarvis.py`, get_gemma_session/close: lock solo sulla creazione e snapshot del proprietario, cancellazione fuori da quel lock; getter rifiuta dopo closing. Avviso generico se abort fallisce, poi chiusura degli altri servizi.
- `native_provider.py`: commento corretto sul percorso cooperativo già presente, logica invariata.

## Evidenze prima della correzione

Suite Windows2022 x64, `python -m unittest discover -s tests -v`; nessun test funzionale Linux.

|Fase|Source/run|Python/job|Esito|
|---|---|---|---|
|Red1|5b6ca6d485ef2f4ca9508a205a3eef6134a04f98 /42350310207|3.11.9/128336832048|784test,16failure,3errori,150.209s|
|Red1|stesso|3.12.10/128336832319|784test,16failure,3errori,132.052s|
|Red2|2a1e5ee92881c0f3130bc0c6e6fd9663ad8600ce /42350462062|3.11.9/128337282836|789test,21failure,3errori,127.965s|
|Red2|stesso|3.12.10/128337283043|789test,21failure,3errori,152.894s|

Tutti i fallimenti/errori appartengono ai nuovi controlli010. I3errori sono RuntimeError dalla risposta ABI simulata anziché ValueError per True/NaN/Inf accettati: difetto di validazione reale, non errore fixture.022/023 non osservati, restano aperti.

Review preventiva: fixture005 sostituiva threading.Thread globale, incompatibile con Timer reale; ora sostituisce soltanto namespace threading della UI generata. Assert esistenti preservati. Copertura aumentata a21test per stop con code, initialize, ABI che solleva dopo annullamento e join prima del reload.

Review runtime: corretti due difetti della prima candidata, riuso provider dopo detach e ingresso C dopo annullamento in Timer.start. Tre test deterministici aggiunti dopo Red2 (totale24nuovi/792attesi); non rivendicato un Red separato di questi tre. Ricontrollo indipendente mirato: nessun blocco residuo rilevato; nessuna esecuzione funzionale da parte del revisore.

## Green Windows

Source `060999046d6b232b4d3c05243c53f53b2b39fbd6`, [run42350951034](https://github.com/MATRIXNEO23/jarvis/actions/runs/42350951034) SUCCESS al tentativo1, senza retry.

|Python/job|Esito suite completa|
|---|---|
|3.11.9 /128338760673|792test,0failure/errori/skip,159.067s; tutti24nuovi test passati|
|3.12.10 /128338760391|792test,0failure/errori/skip,137.774s; tutti24nuovi test passati|

Sintassi Python/JavaScript/PowerShell e probe accesso file passati in entrambi. Searchlive3.12 passata con servizio ripristinato e fixture rimossa; non prevista su3.11. Build, estrazione pacchetto e pubblicazione skipped. Nessun022/023 riprodotto. Suite precedente768 conservata, assert non indeboliti; sola fixture threading005 confinata al namespace della UI generata.

Prove: deadline/stop durante ABI controllata, annullamento e timeout prima dell'ingresso C, eccezioni/abort falliti, load/initialize/prepare concorrenti, provider detach durante samplers, code di chat/prova/isolato/picker, backend che ignora abort, completamento watchdog prima del reload e callback vecchio durante generazione nuova. Verificati rifiuto turni differiti, storia già accettata conservata e recupero dopo stop/timeout. Callback get/close reali con servizi simulati.001–009 compresi nella suite; nessun collaudo reale del GGUF implicito.

Checkpoint finale solo documentazione/evidenze, runtime/test identici al sourceverde. Riferimenti di codice: native_bridge.py load26/abort57/generate76; native_conversation_session.py operation81/commit108/prepare121/stop267/close282; jarvis.py getter4184/close4432; adapter.prepare11/call36. Rischio residuo lifecycle/ABI alto per collaudo reale, nessuna garanzia assoluta di zero regressioni.

## Limiti e recupero

Abort è cooperativo, non una terminazione forzata o garanzia di deadline per C/load/processo. Se la DLL ignora abort, la chiamata mantiene il lock fino al ritorno; non si presenta il backend come già libero né si inizializza un secondo modello. La latenza dell'export abort stesso dipende dalla DLL. Non viene aggiunto un pulsante stop o cambiata la gestione del microfono. Nessun timeout globale su coda/load.

Prove con factory/provider/bridge e callback proprietario reali, inferenza controllata; finestre/servizi del callback close simulati. GGUF/DLL reale, chiusura effettiva processo, CPU/RAM e HDD sul Windows10/i3-2100 restano da verificare. Nessun costo/dipendenza nuovo; Timer limitato alla generazione, risorse e prestazioni sul target non misurate.

Nessuna modifica di schema o dati/configurazioni utente, nessun fallback/servizio online, build/ZIP/release/merge o aggiornamento PC. Main e001–009 preservati, ramo/bozza reversibili. Prima di build affidabile servono ancora modello reale, chiusura processo, pacchetto estratto e prova sul target; Green completo ottenuto come sopra. Problemi022/023 distinti.
