# Ricerca locale e modello — incremento 6, 1 novembre 2026

## Risultato e autorizzazione
Richiesta utente «Procedi» dopo la chiusura del passo HUD. Locale per primo, modello già collegato soltanto per precisare una ricerca irrisolta, poi verifica locale. Nessun nuovo indice, modello, servizio o dipendenza. Nuovo comportamento nel componente Accesso file già esistente, senza nuovo comando o add-on parallelo. Nessuna build richiesta.

## Collegamenti effettivi
| Componente | Responsabilità |
|---|---|
| file_access/service.py | Riscontro vuoto strutturato, token e scadenza, richiesta originale, domanda/risposta di chiarimento, vincoli dell'azione, esecuzione e verifica locale |
| local_engine.py | Trasporto facoltativo del token al servizio, stesso registro degli esiti |
| conversation_router.py | Riscontri e obiettivo nel prompt con limite di 5000 caratteri; catalogo e validatore esistenti |
| jarvis.py | Callback voce/testo, esito locale, richiesta al GPT, gestione risultato/errore, azione locale nuovamente validata |
| tests/test_file_refinement.py | 13 nuove prove Windows del percorso e dei vincoli; risposte modello e trascrizioni controllate |
| file_access/LEGGIMI.md | Comportamento, preparazione e limiti per l'uso |

## Comportamento e confini
Una ricerca nominale riconosciuta localmente che trova risultati non interroga GPT. Se non trova risultati e non ci sono errori di lettura, il risultato può offrire un solo raffinamento. Le ricerche parziali mantengono la copertura dichiarata: non diventano prova dell'assenza del file nell'intero PC.
Il modello può cambiare solo l'indizio (query o target). Operazione, ambito, tipo file/cartella e richiesta di spiegazione restano vincoli locali; campi omessi vengono ripresi dalla richiesta originale, valori diversi rifiutati. La localizzazione di installazioni resta locate e non può diventare ricerca generale, apertura o comando browser. I percorsi vengono ancora verificati e filtrati dalla policy prima dell'azione.
Una domanda del modello conserva obiettivo e domanda; la successiva risposta dell'utente completa quel contesto, invece di diventare una ricerca isolata del solo nome pronunciato. Un secondo risultato vuoto non avvia un ciclo automatico. Replay, scadenza, annullamento, revoca, sostituzione e cambio di epoch vengono scartati. Nessuna estensione della ricerca per figlio Explorer mancante o accesso negato.
Le fasi riusano l'HUD verificato. Se GPT è spento, scollegato o occupato, resta visibile l'esito locale e il limite del raffinamento. Timeout e risposte invalide non producono azioni. Il token è metadato interno: non viene inoltrato come argomento SDK o lasciato al modello come permesso.

## Review e scelta minima
La causa era il consumo locale della frase prima del GPT, con _report che ritorna completed anche per zero elementi. Non era necessario un altro parser, database o bridge: listing trasporta il riscontro strutturato e lo stesso worker/poll completa il percorso. Non si riconoscono errori o assenze cercando parole nei messaggi. Il controllo viene ripetuto all'esecuzione locale per evitare che una proposta ancora in coda mantenga un permesso revocato.

## Prove, sorgenti e limiti
Runtime introdotto nel source 3f7fe6aad8638ad046f1dd3e34b2070876675694, correzione delle sole fixture nel source a279a4ee944c23a93545835ada740793055418fe. [Run 41345741998](https://github.com/MATRIXNEO23/jarvis/actions/runs/41345741998) SUCCESS: 455 test per job 3.11/3.12; sintassi, probe nativo e Windows Search live PASS; build/ZIP/publisher skipped. [Evidenza](evidence/file-refinement-20261101.json).
Prima run 41345558152 fallita: ciclo mancante nella fixture di un ramo poll con continue; costante STANDBY mancante nella nuova fixture voce; confronti testuali di Path DOS/lungo. Correzioni limitate alle prove: ciclo a un evento, stato reale e identità con os.path.samefile più unicità del risultato. Nessuna asserzione comportamentale eliminata e runtime invariato nel ricontrollo.
Le prove usano filesystem Windows reale, catalogo/risoluzione/servizio e callback/worker/poll effettivi, con avvio Explorer intercettato e risposte GPT/trascrizioni controllate. Non dimostrano riconoscimento audio, qualità del modello/account reale, desktop personale o consumi Pavilion. Una cartella candidata trovata non è automaticamente certificata come installazione: il servizio conserva la distinzione di ruolo già prevista.

## Parti non incluse e ripresa
Il bridge GPT non configura retrieval web leggibile dal modello; browser.search apre il browser e non equivale alla lettura di fonti. Nessuna navigazione web inventata, API a consumo o sostituzione del modello esterno. Copertura completa di ogni disco, continuazione persistente del fallback oltre una passata e indice autonomo restano questioni distinte: riusare Windows Search come priorità.
Dopo il verde: aggiornare esiti, indice sorgenti e guida moduli; mantenere build/ZIP/publisher disattivati. Una futura build richiede richiesta esplicita e verifica del pacchetto estratto; i test di questo incremento non sono una nuova consegna installabile.
