# JRV-AUD-008 — impostazioni Gemma applicate alla prossima richiesta

Correzione verificata nei sorgenti in bozza: dopo Salva, la prossima richiesta usa i nuovi parametri. I samplers cambiano senza ricaricare il GGUF; le impostazioni di caricamento causano una sostituzione serializzata. Nessun nuovo pacchetto installabile o aggiornamento del PC effettuato.

Base `b25f54ad34534b7446b0a4e12518634071c47049`/bozza41,001–007 conservate. Source verificato `b10453d5ddfda2155f4969dd8f1fa501cdcda8f9`, [bozza42](https://github.com/MATRIXNEO23/jarvis/pull/42), ramo `fix/jrv-aud-008-gemma-settings-20261107`. [Specifica](superpowers/specs/2026-11-07-jrv-aud-008-design.md), [piano](superpowers/plans/2026-11-07-jrv-aud-008-fix.md), [evidenza](evidence/jrv-aud-008-fix-20261107.json).

## Problema confermato e modifica

La sessione rileggeva la configurazione per prompt/budget ma preparava il motore soltanto alla prima richiesta. Adapter e bridge conservavano quindi i vecchi valori.005 applicava lo snapshot alla Prova generazione esplicita; non risolveva una normale domanda successiva al Salva. Esempi Red: contesto2048 invece di4096, output128 invece di64, un solo caricamento quando ne serviva un secondo. Nessun errore di fixture o ambiente nei due Red Windows.

| ID/stato | Componente | Correzione necessaria | Rischio di regressione e verifica |
|---|---|---|---|
|JRV-AUD-008, MEDIO, CONFERMATO; fix verificato in bozza|`native_conversation_session.py:86`, `_prepare` e flussi chat/isolato/picker/trial/stop|Passare un unico snapshot validato a prepare; confrontare tutti i valori di inferenza, escludendo soltanto il carattere già letto nel prompt. Cache valida solo dopo preparazione riuscita; revoca sicura anche dopo errori.|MEDIO: ownership005, budget e memoria002. Verificare snapshot durante Save/inferenza,3flussi, trial esplicito e recupero senza perdere storia.|
|Stessa008|`native_chat_adapter.py:13,53`, `prepare/stop`|Riutilizzare provider se i campi di caricamento coincidono; altrimenti validare/creare candidato prima di fermare il vecchio. Detach prima di abort per impedire riuso di provider fermato se abort solleva.|Verificare modello/thread/batch/context/DLL, file mancante, load/stop falliti e recupero.|
|Stessa008|`native_bridge.py:51`, `update_generation_settings`|Aggiornare max_output/temperatura/top-k/top-p/seed sotto lock, conservando modello e DLL effettivamente caricati.|Verificare5parametri senza reload; factory realmente trasformata con DLL bundled e percorso salvato vuoto.|

Salva continua a scrivere senza avviare caricamenti o inferenze. Cambiare soltanto carattere o samplers non ricarica il modello; modello/thread/batch/context e DLL interna sì, alla prossima richiesta e dopo la generazione in corso. La UI descrive questa tempistica. Schema di configurazione, consensi, microfono e memorie persistenti non cambiano. Nessun nuovo modulo, servizio, thread o dipendenza runtime.

## Test Windows e risultati

Comando: `python -m unittest discover -s tests -v`, Windows Server2022 x64.

| Fase | Source/run | Python e job | Risultato |
|---|---|---|---|
|Red1|6eaf7be /42343723225|3.11.9/128316811765|740 test,16 fallimenti008,0 errori,113.998s.|
|Red1|6eaf7be /42343723225|3.12.10/128316811896|740 test,16 fallimenti008,0 errori,113.969s.|
|Red2 ampliato|6c62ae9 /42343974322|3.11.9/128317587284|745 test,22 fallimenti008,0 errori,124.310s.|
|Red2 ampliato|6c62ae9 /42343974322|3.12.10/128317587390|745 test,22 fallimenti008,0 errori,135.665s.|
|Green|b10453d /[42344534309](https://github.com/MATRIXNEO23/jarvis/actions/runs/42344534309)|3.11.9/128319288492|747 test,0 fallimenti/errori/skip,119.191s.|
|Green|b10453d /42344534309|3.12.10/128319288706|747 test,0 fallimenti/errori/skip,114.697s.|

Green al tentativo1, senza retry. Passano i17nuovi metodi di `tests/test_native_settings_propagation.py` e i730test precedenti. Le firme prepare di due fixture sono allineate al keyword config; le precedenti asserzioni non sono state allentate.

Copertura: ogni sampler salvato raggiunge la prossima chat senza load/abort; ogni campo di caricamento causa il reload; Telegram isolato e picker aggiornano parametri o possono avviare il reload senza leggere/scrivere storia chat. Carattere aggiornato nel prompt senza reload. Save durante generazione non modifica quella in corso; richiesta in coda acquisisce i nuovi valori. Save tra validazione e prepare non altera lo snapshot della medesima richiesta. Valore UI non valido conserva i byte salvati; budget non valido/modello mancante/load fallito non producono inferenza o nuovo scambio. Recupero dopo load/stop falliti e Prova005 conservato.

Fixture: Tk e callback Salva, JSON atomico, sessione/adapter/factory/provider/bridge reali. ABI controllata registra parametri, carichi e sovrapposizioni, senza GGUF/DLL reali nei test008. Le trasformazioni UI/factory del builder sono eseguite soltanto su copie sorgenti temporanee; nessuna esecuzione del builder o generazione ZIP.

Sintassi Python/JavaScript/PowerShell e probe nativo file superati in entrambi i job. Windows Search live3.12 superato: servizio ripristinato e fixture rimossa. Live3.11 non previsto. Build, pacchetto estratto e pubblicazione saltati intenzionalmente. La suite ereditata conserva anche il probe006 di recupero/caricamento/export DLL di riferimento, senza inferenza GGUF: distinto dalla ABI controllata008.

## Review, limiti e continuità

Review indipendente con contesto nuovo, sola lettura: gap iniziali DLL/load failure/reload da isolato/picker coperti. Trovato un difetto concreto nella prima candidata prima del Green: dopo A valido→B mancante→errore→ripristinoA, Prova generazione saltava lo stop perché prepared era falso pur conservando providerA. Corretto usando sempre lo stop sicuro; test dedicato richiede reload, isolamento e successivo riuso. Ricontrollo mirato senza rilievi residui. Due nuove prove finali di gestione stato/recupero, aggiunte dopo Red2, sono verificate nel Green; non dichiarate come ulteriori Red eseguiti. Il revisore non ha eseguito test.

Lezione: rileggere un file non aggiorna un backend già caricato. Prompt/budget e motore devono usare lo stesso snapshot; separare i parametri dinamici da quelli che richiedono caricamento. Un errore può lasciare risorse possedute anche se prepared è falso: stop e prova esplicita devono gestire anche quel caso.

Nessun test funzionale Linux, account GPT/Telegram, audio/microfono, inferenza o qualità GGUF reale. Windows10/i3-2100/HDD, RAM/CPU e tempi reali non misurati. Il reload attende la richiesta corrente;010 (timeout/abort di una chiamata C bloccata) resta distinto.009 (dialogo Gemma nella memoria duratura) non è implementato da008: conservazione qui significa memoria RAM della sessione, con limiti e isolamento002 invariati.

022/023 non riprodotti nei run008 e restano aperti. Nessun build/ZIP/merge/release o modifica di dati/configurazioni dell'utente. Ultimo checkpoint documentale con runtime/test identici al source verde. Prossimo passo soltanto al via successivo: verificare009, rispettando opt-in memoria e isolamento dei progetti; fermarsi qui.
