# Gemma nativa — checkpoint configurazione (2026-11-04)

## Evidenza verificata
- Run 41866803511: SUCCESS su Windows 2022, inferenza Gemma 2 2B Q4_K_M tramite DLL CPU senza launcher/server. La correzione UTF-8 è nel commit 24a3587.
- Il test non misura parità di velocità con KoboldCpp sul Pavilion i3-2100, né prova l'integrazione nell'interfaccia Jarvis.
- local_model/runtime.py è ancora un contratto incompleto e i suoi test precedenti si riferiscono al percorso eseguibile/server. Non sostituirlo implicitamente.

## Scelta e modifica
- Creato local_model/native_config.py: impostazioni native persistenti e validate, con scrittura atomica e protezione del file precedente quando i parametri sono invalidi.
- Creati tests/test_native_model_config.py e workflow Windows native-config.yml.
- Parametri: DLL, GGUF, threads, batch_threads, context_size, max_output, temperature, top_k, top_p, seed.
- La configurazione non avvia il modello, non modifica le preferenze correnti di Jarvis e non richiede download/API.

## Stato e prossimo passo
- Modifica pubblicata nel ramo feature/gemma-local-20261104. Esito CI da verificare prima di dichiarare superati i test.
- Implementare un adattatore DLL isolato e arrestabile, con timeout, errori sicuri e controllo della concorrenza; prima ispezionare API native e lifetime reali della libreria fissata.
- Collegare al ModelService solo dopo prova Windows di almeno due turni, regressioni e verifica delle impostazioni.
- Prestazioni e stabilità sul Pavilion: NON VERIFICATE. Nessuna build installabile pubblicata.

## Diagnosi CI e correzione 2026-11-04
- Run 41868898297 FAILED: 3/4 test superati; test_reject_bad_parameters falliva perché il test forniva la sequenza letterale \\x00 anziché un vero carattere NUL. Corretto il fixture con chr(0), commit b511486.
- Run 41868856559 FAILED: workflow preesistente local-model, 8 fallimenti nel contratto legacy di local_model/runtime.py ancora incompleto. Non è una regressione dimostrata della configurazione nativa e non è stato disabilitato o modificato.
- Attendere esito della nuova CI Windows prima di dichiarare verificata la configurazione; poi affrontare il contratto legacy separatamente, decidendo se mantenerlo o migrare con test.
