# Numerazione progressiva delle build Jarvis

Richiesta di Alberto del 3 novembre 2026: ogni candidata pubblicata deve avere un numero progressivo semplice per riconoscere la versione e tornare indietro.

- Nomi pubblici: Jarvis-001.zip, Jarvis-002.zip, Jarvis-003.zip e così via. Tre cifre come minimo, senza azzerare il contatore dopo999.
- Registro autorevole: Download/BUILD-NUMBERS.json. Prima di confezionare/pubblicare, leggere latest_build e next_build correnti da main.
- Prima build numerata:001, alias con byte identici della candidata Continuità cec4536. Prossima pubblicazione:003;002 è pubblicata.
- Una build pubblicata non si sovrascrive, non si rinumera e il numero non si riutilizza, nemmeno se viene ritirata per un problema.
- Per ogni build registrare numero, nome ZIP/JSON, precedente, sorgenti, SHA256, dimensione, prove e stato del collaudo PC. La più recente resta in cima a Download e nel README principale; le precedenti restano scaricabili.
- Fonte/commit/data restano nei metadati. I nomi pubblici devono privilegiare il numero, evitando lunghe combinazioni di nomi/data/hash.
- La numerazione è comune alle candidate Jarvis: non creare contatori separati per contesto, voce, timer o altri moduli.
- Per tornare indietro usare la cartella della build precedente conservata. La numerazione non autorizza cancellazioni, sostituzioni di profili o migrazioni dei dati.
- La richiesta non autorizza build periodiche o nuove funzioni: si applica alle consegne autorizzate.

L'assegnazione001 non ricompila Jarvis: riusa esattamente lo stesso blob Git del pacchetto già verificato e mantiene il vecchio link. Chi ha già scaricato cec4536 possiede gli stessi file. VERSIONE.json interno mantiene la versione tecnica0.1.1-candidate e il source originario;001 è l'identificativo pubblico della consegna. Nelle future confezioni inserire anche build_number nei metadati VERSIONE.json e nel nome della cartella estratta.

I vecchi script/workflow possono ancora contenere nomi storici: prima di una nuova build adeguare il flusso al numero disponibile nel registro. La nuova regola di nomi non è un automatismo di compilazione.
