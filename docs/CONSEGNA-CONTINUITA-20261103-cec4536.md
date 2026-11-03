# Consegna candidata Jarvis — Continuità e ricerca, 3 novembre 2026

[Scarica Jarvis-Continuita-20261103-cec4536.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Continuita-20261103-cec4536.zip)

## Versione e prove
- Sorgenti: [cec4536b0f5991cb900680ed05295245f4e04acb](https://github.com/MATRIXNEO23/jarvis/tree/cec4536b0f5991cb900680ed05295245f4e04acb), ramo build/continuita-20261103. Runtime1265360 e correzioni precedenti preservati.
- [Run Windows 41614085149](https://github.com/MATRIXNEO23/jarvis/actions/runs/41614085149) SUCCESS:505 test Python3.11.9 e505 Python3.12.10.
- Pacchetto estratto:130 test PASS, comprese le nuove prove di consegna contesto, domanda pendente, ordine indice, frasi di ricerca e correzioni vocali. Import, avvio/chiusura UI, manifest hash e launcher unico PASS.
- Probe nativi/sintassi e Windows Search live PASS; fixture e servizio Windows della CI ripristinati. Nessun nuovo test Linux.
- Publisher125844260648: archivio persistito senza sovrascrivere pacchetti precedenti, URL pubblico riscaricato su Windows, SHA256/dimensioni e prima voce Download/README/README principale verificati.
- 268298 byte,79 file. SHA256: d96e90657ad67399893ef5d89a7e250da5369b64a833fd596e4d718ad3687f07.
- Il Download precedente d06e233 e la base PC confermata b936879 restano disponibili. La candidata non è ancora promossa a base confermata.

## Ambito
Raccoglie le correzioni verificate di contesto tra servizio/callback/prompt, conservazione della domanda pendente, nomi naturali di ricerca e indice Windows prima del fallback. Nessuna nuova capacità di apertura file associata, nessuna nuova infrastruttura web o indice parallelo.

La build non certifica la continuità per qualsiasi dialogo. Le prove software usano trasporti GPT controllati; modello/account, microfono e prestazioni Pavilion restano collaudo personale. Restano aperti i rilievi della review, tra cui risposte libere del modello prive di conferma locale e il rischio statico di salvataggio seguito da chiusura documenti. Il LEGGIMI operativo segnala di evitare quest'ultima operazione su documenti importanti durante questo collaudo. Non dichiarare corretti tutti i difetti.

## Installazione e prossimo passo
1. Estrai in una cartella nuova e avvia soltanto avvia_jarvis.bat. Conserva la precedente cartella.
2. Il profilo Jarvis-AccessoFile-Trial esistente, dati e cartelle autorizzate sono mantenuti. Non cancellare i profili.
3. Dopo l'avvio provare contesto e ricerca, una prova guidata alla volta; soltanto dopo il riscontro procedere con altre implementazioni. Non rigenerare il pacchetto già consegnato senza un nuovo motivo.

Sono distribuiti solo file operativi e istruzioni essenziali; test, skill, workflow e continuità restano nel repository. Trigger push usato sul solo ramo di build per questa richiesta esplicita, quindi disattivato dopo il successo. Future build/pubblicazioni richiedono un nuovo via.
