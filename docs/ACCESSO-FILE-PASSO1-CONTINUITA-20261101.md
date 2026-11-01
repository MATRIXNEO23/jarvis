
Requisito obbligatorio ribadito: nessun elenco di file/cartelle/finestre/programmi/processi viene inviato alla sintesi vocale, indipendentemente dal numero di elementi. Voce per spiegazioni e domande brevi; risultati in finestra dedicata scorrevole/selezionabile (da implementare), con caricamento progressivo per elenchi grandi. La correzione già presente separa messaggio chat da spoken_message e non legge liste file; non dichiarare già presente la nuova finestra. Accettazione futura: lista molto grande non accoda nomi/percorsi TTS e lascia disponibili i comandi; spiegazioni richieste restano vocali.

# Passo 1 — risposta col nome e richiesta pendente

Stato: implementato; CI Windows in attesa. Sorgenti cf0c33c965f9ad5ed6706127aa97c93212db1255, base del passo 87006ee4, base PC b936879 preservata.

Problema dimostrato staticamente: select riprendeva _pending per numero; il nome arrivava al callback come nuovo testo e poteva azzerare il contesto. Correzione minima nel servizio esistente: riconoscere il nome esatto normalizzato soltanto tra i candidati della richiesta pendente, poi riusare select. Il parser viene già chiamato prima del reset UI: nessuna modifica a jarvis.py necessaria per questo caso. Identità dell’elenco lega la scelta accodata ai risultati originali; consumo una sola volta; tipo e opzione spiegazione conservati. Nomi duplicati richiedono numero. Nessuna app o percorso inventato.

File: file_access/service.py, file_access/LEGGIMI.md, tests/test_file_access.py, docs/ACCESSO-FILE-STATO.md. Sei prove nuove: callback reale → nome → una sola apertura senza ricerca; omonimi poi numero; risposta su elenco sostituito; scadenza/annulla/progetto/permessi/disattivazione; tipo corretto/nessuna ipotesi su nomi estranei; lettura con spiegazione mantenuta. Finestra/Popen simulati, file e directory temporanei reali in Windows; non prova del microfono o della visibilità Explorer personale.

CI 41333821126: python -m unittest discover -s tests -v e controlli sintassi/probe del workflow su Windows 2022/Python 3.11 e 3.12. Nessuna esecuzione Linux. Generazione ZIP, estrazione/publisher devono restare skipped perché è un push e non dispatch build. Esito non ancora acquisito: non dichiarare passo verificato o pronto da installare.

Prossimo controllo: leggere solo stato/job della run associata al commit; se fallisce, diagnosi circoscritta prima delle fasi dipendenti. Se passa, registrare conteggi/esito/limiti e proporre il prossimo passo breve: domanda senza candidati e/o cartella corrente secondo il piano, senza build automatica. Navigazione/nuova UI/ricerca lunga/programmi/processi/schede non implementati da questo passo.
