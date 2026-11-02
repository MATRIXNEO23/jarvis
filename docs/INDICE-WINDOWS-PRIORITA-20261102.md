# Priorità indice Windows — diagnosi del 2 novembre 2026

Il requisito era già concordato: riusare Windows Search come prima fonte, senza un indicizzatore parallelo. Il chiarimento dell'utente non è una nuova richiesta di architettura.

Controllo del runtime 8066852/checkpoint b4ef5f0: file_access/service.py, _search_impl interroga self.index(query,root) nel ciclo delle radici, poi avvia sempre os.scandir sulla stessa radice, anche se l'indice ha risposto. Il limite tempo/voci della scansione può interrompere l'intero ciclo prima delle query indice sulle radici successive. file_access/windows.py usa realmente Windows Search (SYSTEMINDEX via Search.CollatorDSO, helper windows_search.ps1), ma la priorità globale non è rispettata pienamente.

Nelle ricerche locate, reason viene già valorizzato dal messaggio sulle registrazioni/collegamenti: reason = reason or note scarta quindi la nota dell'indice. La foto prova ricerca diretta parziale, non il motivo dell'esito dell'indice. Non affermare che WSearch fosse spento, guasto o senza risultati dal solo screenshot.

Rettifica della descrizione precedente: il fallback attuale non parte soltanto se Windows Search non risponde. I test indice live passati provano il provider, non questa scelta di orchestrazione. Le correzioni di dialogo 8066852 non modificano tale ciclo; lo ZIP precedente d06e233 mantiene lo stesso limite.

Proposta di prossimo intervento, non implementata: prima completare una fase indice per tutte le radici autorizzate, con deduplica/permessi/revoca e limiti espliciti; poi usare scansione diretta solo quando necessaria per aree non coperte o indice indisponibile, distinguendo assenza di risultati da indisponibilità/copertura ignota. Conservare stato e motivi dei provider separati dalla descrizione d'installazione, senza dedurli cercando parole nei messaggi. Nessun nuovo servizio o accesso oltre le spunte. Evitare che il budget di scansione impedisca query indice successive.

Accettazione Windows richiesta: indice positivo su più radici con budget diretto esaurito; assente/vuoto/timeout distinti; esclusioni/revoca; indice positivo senza scansione superflua; fallback parziale dichiarato e motivo visibile anche per locate. Nessun nuovo test eseguito per questa diagnosi statica, nessuna modifica runtime o build. Restano da definire/verificare la copertura effettiva e la politica del fallback, senza dichiarare l'indice completo dell'intero PC.
