# Jarvis005 — preparazione e consegna, 4 novembre 2026

Alla richiesta «prosegui», dopo l’implementazione verificata e l’avviso che la004 non è aggiornata, si procede alla fase di preparazione, verifica Windows e pubblicazione della nuova candidata. Questa prosecuzione riguarda la005; non abilita build future su push ordinari.

Base: 14eeffc44055eb1a9dba936c57e10b6be155aa1f, derivata dai fix richiamoJarvis e memoria vuota verificati (558 test per Windows3.11/3.12). Ramo di confezione build/jarvis-005, nessun nuovo runtime o ulteriore snellimento prompt. Build immutabile progressiva005,004 e precedenti conservate; nessun componente Codex App Server o quotaHUD.

Confezione: aggiornati numero/versione/timestamp deterministico, identità nel verificatore e guida effettiva (riportava ancora003). Prove dal cwd ZIP estratto estese ai 12 casi richiamo, 4 casi memoria vuota e regressioni persona/router, senza import dal checkout del prodotto. Manifest/hash, solo file operativi, launcher unico, import e avvio/chiusura UI, riproducibilità con clock diverso. Suite Windows completa e probe prima della build; nessun test funzionale Linux.

Il collegamento GitHub non espone dispatch: si usa per questa consegna il trigger push del solo ramo build/jarvis-005. Publisher dipende dal successo di entrambi i job Windows, conserva le versioni, inserisce005 in cima a Download e riscarica il file pubblico controllando hash/byte e tutti i pacchetti001–004. Dopo la consegna disabilitare di nuovo trigger dedicato e publisher. Nessuna scrittura concorrente su main durante il publisher.

## CONSEGNATA — candidata005 verificata e pubblicata

[Scarica Jarvis-005.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-005.zip). Source **b202181d435cf4ee13ffb355265e1f1a9f995963**, [runWindows41749364482](https://github.com/MATRIXNEO23/jarvis/actions/runs/41749364482) SUCCESS; pubblicazione main **a9520b3e2d0ec680746710821a7adbbefcd1cd19**. ZIP **283598 byte**, **86 file**, SHA-256 **583bd55d1ef416b3781f6183d8ea6365f0b8761c6cf1fd614d652db832285728**.

558 test per Python3.11/job126310308264 (126.617s) e Python3.12/job126310308535 (71.776s), sintassi/probe nativo/indiceWindows live PASS. Dal cwd estratto: **213 test OK** in32.976s, manifest/hash/soli operativi/launcher unico/import/avvio e chiusura UI PASS; ricostruzione con clock diverso produce byte identici. Publisher/job126311593976 ha verificato byte/manifest, registrato005, pubblicato in cima a Download e riscaricato l’URL pubblico controllando hash/dimensioni e tutti i pacchetti001–004. Metadata remoti riletti e coincidenti. Registro latest5/next6; vecchie release inalterate.

Contiene solo le correzioni già verificate: nomeJarvis iniziale in ogni richiesta in GPT_CONVERSATION/CONTINUOUS, blocco ambiente prima di azioni/log/coda/GPT e omissione della memoria vuota quando allegata. Ricordi utili, personalità, catalogo e controlli manuali conservati; niente quotaHUD/AppServer o nuovi componenti. Nessuna misura della quota personale né promessa di risparmio percentuale.


## Collaudo sul PC

Chiudere la004 prima di avviare la005. Estrarre lo ZIP in una nuova cartella, senza sovrascrivere la004; avviare soltanto avvia_jarvis.bat. Profilo AccessoFile, dati, preferenze e autorizzazioni app restano gli stessi.

Prima prova locale a quota modello zero: con GPT spento e MIC acceso, dire «apri Netflix» (nessun avvio), poi «Jarvis, apri Netflix» (avvio della app già consentita). Non dare per scontato che questa prova acustica sia passata dai test sintetici; se il nome non viene riconosciuto serve il riscontro reale. Anche risposte e conferme richiedono il nome iniziale. Per la prova del solo nome, attendere il feedback «Dì Jarvis seguito…» prima di una frase senza richiamo: non deve autorizzarla.

Limiti: collaudo reale microfono/account/desktop/Pavilion ancora da fare; nessuna promessa di percentuale quota e nessuna barra quota installata. La riduzione del prompt vale solo quando il blocco vuoto era effettivamente allegato. Non promuovere005 a base utente senza riscontro.

Dopo consegna trigger push dedicato e publisher disabilitati nuovamente. Prossimo passo solo riscontro PC sul pacchetto esatto; non rigenerare lo stesso numero o avviare nuove build automaticamente.
