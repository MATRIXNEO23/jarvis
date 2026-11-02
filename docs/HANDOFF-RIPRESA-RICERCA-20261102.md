# Jarvis — handoff di pausa, 2 novembre 2026

## Stato e richiesta corrente
Alberto chiede di fermarsi, fare il punto e salvare continuità/handoff per riprendere le correzioni e arrivare alla prossima build. In questa chiusura si aggiornano soltanto i documenti: niente correzioni runtime, test ripetuti o nuova build. Alla riapertura recuperare questo punto, senza ricominciare l'analisi generale o richiedere decisioni già raccolte. La pausa resta attiva fino al successivo messaggio di ripresa; il riferimento alla prossima build indica l'obiettivo successivo, non un via a pubblicarla durante questa pausa.

## Riferimenti esatti
- Repository: MATRIXNEO23/jarvis.
- main prima di questo checkpoint documentale: ca474d32a0f7e8d618dbeac0b96cd528f7bbbf06.
- Ramo correttivo: feature/fix-file-search-20261102; testa riletta alla pausa: 445efe657e8bbac504d11ce71b10c7c110c3880d.
- Ultimo codice correttivo verificato: 806685275947cea4b933d20aa0317658d13b853c. Non confondere il codice operativo del ramo con la radice storica main.
- Run Windows: [41367835278](https://github.com/MATRIXNEO23/jarvis/actions/runs/41367835278), SUCCESS, 471 test per job Python 3.11/3.12. Sintassi e probe PASS; prova Windows Search live PASS nel job previsto. Build, verifica ZIP estratto e pubblicazione saltate.
- [Evidenza dettagliata](evidence/file-search-dialogue-20261102.json), [rapporto correzioni](RICERCA-DIALOGO-CORREZIONI-20261102.md), [diagnosi indice](INDICE-WINDOWS-PRIORITA-20261102.md).
- Ultimo ZIP nel Download/README riletto: Jarvis-Accesso-File-0.1.0-20261101-d06e233.zip, sorgenti d06e233a98e4ea5b4e99a9d296b9570ce0c92d86. NON contiene le correzioni 8066852.
- Base PC confermata precedente: Timer Audio Fix2, b936879a431370d206152be7b089baf587d15499. Preservare vecchi pacchetti e profili; il candidato Accesso file non è promosso a base confermata.

## Punto della situazione

| Problema | Stato effettivo | Resta da fare |
|---|---|---|
| Raffinamento GPT rifiutato per messaggio oltre limite | Prompt compatto corretto nei sorgenti 8066852 e verificato | Consegnarlo nel prossimo ZIP verificato; prova modello reale distinta |
| Risposta errata «solo Download» | Aiuto adeguato ad Accesso file attivo, test PASS | Collaudo del pacchetto esatto sul PC |
| «Cercami un file» → nome → perde l'azione | Ripresa search con nome/ambito originari verificata; memoria del prompt migliorata | Non estendere il risultato a ogni parafrasi: controllare reset prematuro |
| «Cerca Netflix» → browser | Guard sul browser con frase originale e chiarimento PC/Internet verificato nei callback voce/testo | Conservare anche l'intento locale già stabilito; non chiedere di nuovo l'ambito se già chiaro |
| Reset strutturato prima del modello | Percorso problematico identificato nel source pubblicato | Correzione mirata e regressioni ancora da fare |
| Priorità indice Windows | Provider reale esistente e già provato; orchestrazione indice-prima incompleta | Separare fase indice su tutte le radici dal fallback diretto e rendere visibili motivi/copertura |
| Nuovo ZIP | Non creato né pubblicato | Dopo correzioni e verifiche Windows, confezione/estratto/pubblicazione/download verificati nel perimetro della ripresa |

## Foto e significato dei messaggi
La foto allegata mostra «Ricerca parziale: raggiunto limite tempo della passata», 652 elementi esaminati, 324 cartelle lette, zero errori di lettura, zero fuori ambito/non verificabili, sottocartelle incluse e una radice selezionata. Non certifica la copertura completa né l'assenza del programma nel PC. Non rivela se Windows Search fosse spento, guasto o privo di risultati. Le registrazioni/collegamenti accessibili non hanno certificato l'installazione; eventuali cartelle omonime restano di ruolo non verificato.
«Raffinamento non avviato: la richiesta supera il limite di contesto GPT» è un rifiuto locale prima della richiesta al modello; non prova esaurimento del piano Plus. La foto non contiene trascrizione iniziale o identificazione certa dello ZIP installato. Non inventare log del tentativo.

## Diagnosi da conservare
1. Nel source d06e233, la frase generica «cerca Netflix» non corrisponde al parser file/programma. In try_file_command un parse None senza parole file/cartella/deittici può chiamare provider.reset(active_project_id), prima di inoltrare la frase a GPT. Il vecchio validatore può accettare browser.search/browser.open; quel ramo non interroga Windows Search. La scelta concreta del modello nel tentativo personale resta inferenza dal codice e dal riscontro, in assenza di log.
2. In file_access/service.py, _search_impl interroga l'indice per una radice e poi scansiona sempre quella stessa radice. Il limite della scansione può fermare il ciclo prima delle query indice sulle altre radici. In locate, reason già valorizzato può nascondere la nota dell'indice. Il successo del provider live non verifica questa orchestrazione.
3. Il primo ricontrollo 41367413297/source 3d6a2be fallì: perdita reale del nome/capacità nel prompt e soglia arbitraria della fixture sul JSON runtime. Superato da 8066852/run 41367835278. Non ripristinare il prompt precedente né ripetere quel tentativo senza nuovo motivo.

## Sequenza precisa alla ripresa
1. Leggere RECUPERO.md e AGENTS.md correnti, questo handoff, i due rapporti e le lezioni pertinenti. Verificare testa del ramo correttivo e diff rispetto a 8066852; riusare verifiche valide. Non sostituire main con una copia massiva dell'app.
2. Correggere il reset prematuro nel percorso esistente: conservare richiesta, azione, oggetto e ambito validi tra parafrasi e risposta breve; invalidare correttamente su annullamento, cambio progetto, scadenza o revoca. Riutilizzare memoria/provider/router; nessuna seconda funzione parallela.
3. Correggere _search_impl: interrogare prima l'indice per tutte le radici autorizzate, con deduplica e policy correnti. Poi fallback soltanto dove necessario, distinguendo indisponibilità, indice vuoto, copertura ignota/parziale e timeout. Un risultato vuoto non dimostra copertura completa. Il budget diretto non deve impedire query indice successive. Rendere osservabili provider e motivi anche per locate.
4. Eseguire prove significative soltanto Windows: dialogo locale già stabilito → frase generica; nome mancante → risposta → ricerca; PC/Internet soltanto se ambiguo; web esplicito; cambio progetto/revoca/annullamento e niente doppie esecuzioni; più radici con indice positivo e budget diretto esaurito; niente scansione superflua su copertura adeguata; fallback/errore/timeout separati. Aggiornare checkpoint dopo ogni incremento.
5. Dopo successo e nel perimetro della richiesta di ripresa/build, produrre candidato con soli file operativi, verificare archivio estratto e avvio/chiusura UI su Windows, manifest/hash/launcher unico e regressioni pertinenti dal pacchetto. Pubblicare in cima a Download preservando versioni precedenti, verificare download effettivo e corrispondenza al commit. Solo allora dichiarare consegnato. Non considerare una CI verde una nuova installazione sul PC.

## Vincoli invariati
Zero costi aggiuntivi, GPT esterno, priorità all'indice Windows esistente, nessun indicizzatore autonomo o SDK/browser nuovo senza necessità verificata. Accesso soltanto a cartelle autorizzate/spunte/esclusioni e permessi correnti. Preservare impostazioni, memoria, cronologia, salvataggi e controllo manuale microfono. Nuove funzioni come .jaddon; per queste correzioni migliorare i componenti esistenti. Elenchi nella finestra dedicata, niente lettura integrale in voce. Nessun nuovo test Linux; account/microfono e prestazioni Pavilion restano prove personali non eseguite qui.

## Richiamo breve per una nuova sessione
«Riprendi Jarvis da docs/HANDOFF-RIPRESA-RICERCA-20261102.md su main: completa reset del contesto e priorità Windows Search nel ramo feature/fix-file-search-20261102, poi verifiche Windows e prossima build secondo le autorizzazioni correnti. Conserva le correzioni 8066852 già verificate e tutti i dati.»
