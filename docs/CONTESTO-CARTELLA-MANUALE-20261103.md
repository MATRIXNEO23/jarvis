# Contesto della cartella fornita in dialogo — 3 novembre 2026

## Riscontro e ambito
L'utente mostra in una schermata la sequenza cartella fornita manualmente → Jarvis propone apertura o elenco → «elenca il contenuto» → Jarvis chiede di nuovo quale cartella. È visibile un progetto selezionato. Il difetto conversazionale è osservato sul PC; il suo prompt di rete esatto non è stato registrato qui.

La correzione precedente R02 proteggeva le domande pendenti del motore locale. Un percorso fornito soltanto nel dialogo può non generare focus.file_results, quindi non attivava la stessa prenotazione del budget del prompt. L'ordine del compattatore poteva inoltre sacrificare l'ultimo scambio ai vecchi progressi del progetto. Non attribuire questo episodio al limite20 e non correggerlo con una grammatica dedicata a Minecraft.

## Riproduzione Windows
Base f2e76c46312f5edfb38fdb79c12dcc1569b61851, runtime applicativo uguale a001.
Tre nuovi metodi in tests/test_file_context_delivery.py:
1. Cartella fornita dall'utente, nessun risultato locale, domanda sull'operazione e risposta «elenca il contenuto»; due percorsi portabili diversi.
2. Memoria e progetto SQLite reali, ultimo scambio inserito col callback effettivo, precedenti progressi presenti, nessun risultato locale.
3. Riferimento conversazionale generico, senza dipendere da nomi di file.

Red valido:04b295d0a57d53fdb7913858c5cd7a09b69e2865, [run41619941313](https://github.com/MATRIXNEO23/jarvis/actions/runs/41619941313), job125862812213/Python3.11.9 e125862812693/Python3.12.10.508 test,4 fallimenti nei3 nuovi metodi,0 errori per job. I percorsi sono presenti nel contesto grezzo del callback ma mancano nel prompt finale senza risultati locali; nella variante col progetto il percorso arriva ma sparisce l'identità del progetto. Anche il soggetto dello scambio generico viene perso. Sono difetti riprodotti della consegna del contesto, non una riproduzione della risposta del modello reale sul PC.

Una prima preparazione della fixture confrontava un percorso grezzo col JSON serializzato: corretto il solo confronto per decodifica/escaping, senza modificare il prodotto, prima di accettare il Red. Non usare i fallimenti della versione preliminare27fb894 come diagnosi del runtime.

## Correzione e Green
Runtime [dc78bb9e7fd835f93a8cb8d65e50f7c9848b7d16](https://github.com/MATRIXNEO23/jarvis/tree/dc78bb9e7fd835f93a8cb8d65e50f7c9848b7d16):
- conversation_router.py: prenota il budget del contesto compattato valido per domanda/scambio/progetto anche senza file_results, prima degli esempi opzionali add-on.
- jarvis_persona.py: preserva l'ultimo scambio prima dei vecchi progressi; i progressi mantengono lo spazio per un prefisso utile dei risultati attuali.
- Nessuna variazione di azioni, validatori, permessi, ricerca o limite tecnico complessivo del bridge.

[Run41620441158](https://github.com/MATRIXNEO23/jarvis/actions/runs/41620441158) SUCCESS:
- job125864485582/Python3.11.9:508 test OK,79.111s.
- job125864486111/Python3.12.10:508 test OK,68.254s.
- Sintassi Python/Node/PowerShell, probe nativo e Windows Search live PASS. Build/ZIP/publisher SKIPPED.

Le prove usano servizio/policy/filesystem temporaneo Windows, memoria SQLite, callback e costruttore del prompt reali. Nessuna chiamata al modello/account o prova microfono/desktop personale.

## Revisione e limiti
Revisione indipendente in sola lettura sul diff esatto f2e76c4…dc78bb9: nessun blocco concreto nelle modifiche; confermati budget UTF16 e validatori invariati. Il revisore non ha eseguito test e non sostituisce il Green Windows letto separatamente.

Resta il limite preesistente dei prefissi: percorsi lunghi o riferimenti posti tardi in una frase possono ancora essere troncati. Le nuove fixture usano riferimenti brevi. Non dichiarare risolta la continuità per dialoghi arbitrari, progetti molto lunghi o qualsiasi formulazione del modello.

## Stato della consegna
001 resta invariata e non contiene il fix. Nessuna002 pubblicata; prossimo numero002 secondo Download/BUILD-NUMBERS.json. La nuova candidata, quando autorizzata, deve includere e verificare queste prove dal pacchetto estratto prima del riscontro PC. Altri rilievi della review e limite20 restano distinti. Nessuna nuova implementazione da avviare al posto del problema di contesto.
