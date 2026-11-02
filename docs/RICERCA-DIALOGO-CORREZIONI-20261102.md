## 2026-11-02 — percorso concreto della ricerca generica Netflix
Richiesta utente: capire perché «cerca Netflix» ha aperto il browser invece di cercare nel PC. Verificato il source del pacchetto pubblicato d06e233: file_access.parse_command riconosce ricerche con file/cartella o localizzazione installazione, non la frase generica. try_file_command, su parse None e senza parole file/cartella/deittici, chiama provider.reset(active_project_id) e ritorna False: può perdere lo stato strutturato della ricerca precedente prima dell'interpretazione. La modalità Conversazione GPT inoltra la frase al modello. Il validatore del vecchio source accetta browser.search/browser.open consentiti senza controllare se l'utente intendesse web; il dispatcher locale esegue. Nessuna query indice fa parte di quel ramo browser.
Il percorso è dimostrato dal codice per la frase esatta; trascrizione STT e risposta modello reali di quel tentativo non sono disponibili, quindi la specifica scelta del modello resta inferenza compatibile col riscontro, non log personale. Non attribuire l'apertura browser a Windows Search o al limite della scansione: questi riguardano un altro ramo.
Source correttivo 8066852 aggiunge già il guard sul browser con frase originale e domanda PC/Internet, verificato nei callback voce/testo in run 41367835278. Non basta a dichiarare conservazione universale del contesto di ricerca: va verificato il reset delle parafrasi e il raccordo a una richiesta locale già pendente, evitando sia reset prematuro sia riuso di permessi scaduti. Lacuna indice-prima separata e ancora non implementata; diagnosi INDICE-WINDOWS-PRIORITA-20261102.md.
Download/README riletto: ultimo ZIP ancora d06e233, non contiene correzioni 8066852. Nuova analisi statica, nessun test Windows ripetuto, nessuna modifica runtime o build da questa diagnosi.

# Ricerca file e continuità del dialogo — 2 novembre 2026

## Problemi osservati e limiti del riscontro
Foto del collaudo: nessun risultato nelle sole aree esaminate; fallback al limite tempo (652 elementi, 324 cartelle); raffinamento rifiutato localmente per contesto oltre limite. Riscontri aggiuntivi: «cerca Netflix» apre il browser; ricerca presentata come limitata ai Download; dopo domanda sull’oggetto si perde l’azione iniziale. Pacchetto proposto prima dei riscontri: d06e233; la foto non identifica da sola il nome ZIP né la trascrizione iniziale. La base PC confermata resta b936879.

## Cause verificate e scelta minima
- build_conversation_prompt aggiungeva riscontro file a persona, protocollo generale, catalogo core, grammatica file e stato dei moduli. Il solo catalogo add-on/memoria si adattava al budget: il prompt obbligatorio poteva già oltrepassare 5000. Rifiuto prima della chiamata GPT; non prova esaurimento quota Plus.
- La prima nuova prova a due turni ha dimostrato che il prompt generale poteva invece rientrare nel limite scartando il nome cercato e l'azione localizza. Ridotte ripetizioni del protocollo, preservando persona, schemi e vincoli, per conservare domanda/richiesta e catalogo.
- I gestori locali non trasformano «cerca Netflix» in ricerca web: solo frasi esplicite browser/internet sono comandi locali. La scelta del modello è un'inferenza dal percorso corrente, non una prova dell'audio personale.
- L'aiuto storico del nucleo dichiarava sempre solo Download; il dialogo di nome mancante conservava open/read ma non search.

## Modifiche
| File | Risultato |
|---|---|
| conversation_router.py | Raffinamento focalizzato sulle azioni file attive; protocollo generale compatto; browser.search/browser.open e vecchi web_search/open_browser diventano chiarimento se la richiesta di ricerca non specifica il web. Nessun marchio codificato. |
| jarvis.py | Il validatore riceve la frase originale anche al ritorno asincrono del modello. Chiarimento, voce e memoria usano lo stesso poll. |
| file_access/service.py | «Cercami un file/cartella» chiede nome e riprende search con ambito originario e permessi correnti, tramite request_target/answer_target esistenti. |
| local_engine.py | Aiuto coerente con cartelle autorizzate se Accesso file disponibile; fallback Download conservato se disattivo. |
| tests/test_conversation_router.py, tests/test_file_refinement.py | Budget pieno, stato runtime reale, raffinamento fino al risultato verificato, chiarimento browser in voce/testo, secondo turno con nome/domanda, ricerca fuori Download senza GPT. |

Nessun indice, servizio, modello, dipendenza o costo aggiunti. Nessuna scansione più ampia o autorizzazione implicita. Il limite tempo della scansione resta distinto e invariato. Per il generico «questo» il modello deve usare focus/memoria o chiedere l'oggetto: le prove controllate non dimostrano qualità semantica universale del modello reale.

## Prove e recupero
Prima run 41367413297/source 3d6a2be874edfa5bdbf4b3a89dae60a93b556281 fallita: 470 test, due failure. Una dimostrava perdita effettiva del contesto; l'altra era una soglia arbitraria sulla lunghezza del JSON runtime. live_capabilities può legittimamente eliminare la lista dei moduli per rispettare 850 caratteri; corretta la fixture con controllo contenuto/limite, mantenendo la prova separata del budget massimo.

Source corretto **806685275947cea4b933d20aa0317658d13b853c**, ramo **feature/fix-file-search-20261102**. [Run Windows 41367835278](https://github.com/MATRIXNEO23/jarvis/actions/runs/41367835278) SUCCESS: 471 test per job Python 3.11/3.12, zero failure/errori; sintassi e probe Windows PASS. [Evidenza](evidence/file-search-dialogue-20261102.json). Trascrizioni/risposte modello controllate e filesystem Windows effettivo; nessun test Linux, account/microfono personali o misura Pavilion.

ZIP esistente invariato, build/controllo archivio/publisher skipped. Nessuna nuova consegna installabile. Conservati dati, cronologia e pacchetti precedenti. Prossimo passo: una nuova build solo su richiesta esplicita, poi verifica archivio estratto e pubblicazione; sul PC verificare trascrizione, richiesta originale e risposta di chiarimento del pacchetto esatto. Non promuovere questi test di sorgente a collaudo PC.
