# JRV-AUD-014 — inventario limitato dei moduli runtime

Base018 `76e392f80eb7b1d1f43921f101eb1180cb54f76a`, con001–011 e018. L'utente autorizza correzioni mirate, preservando ciò che funzionava. Non autorizzati build, merge, nuove funzioni di indicizzazione o scansioni dei suoi documenti.

## Problema dimostrato e riuso

`self_diagnostics._source_list` visita soltanto i file diretti della radice e di tests. Le cartelle del runtime non entrano nell'AST di `inspect_jarvis/review_sources`: la diagnosi generale ignora Gemma, ricerca file, programmi e sveglia. Usare il motore statico esistente, senza importare/eseguire sorgenti o creare un secondo analizzatore.

Inventario Git letto dalla base:61Python nella radice,19local_model,5file_access,4program_apps,1sveglia;90Python runtime, più gli script. Non serve aumentare preventivamente i limiti140file/260000byte perfile. I test possono occupare soltanto lo spazio residuo, dopo il runtime.

## Contratto minimo

- Radice diretta invariata per estensioni `.py/.bat/.ps1/.mjs`; aggiungere ricorsione soltanto nelle cartelle runtime approvate `local_model`, `file_access`, `program_apps`, `sveglia`. Test per ultimi. Nessun generico rglob dell'installazione, drive o AppData.
- Escludere profili/dati espliciti (`data_root`), cache, cartelle nascoste, ambienti, upstream/native_engine/modelli e cartelle di dati note anche se annidate in un modulo. Non seguire link, junction o altri reparse point Windows. Se dati e codice coincidono, dichiarare inventario indisponibile/escluso anziché scansionare il profilo alla cieca.
- Conservare140file e260000byte; limitare anche le directory enumerate a140 per evitare attraversamenti illimitati di alberi vuoti. Dichiarare i limiti in modo visibile anche dopo molti errori di I/O. Ordinamento deterministico, runtime prima dei test. Errori di un modulo non impediscono di esaminare gli altri. Nessuna garanzia che tutti i file di installazioni arbitrarie rientrino nel limite.
- Riutilizzare AST e progressi già presenti; nessuna esecuzione/import/upload di sorgenti, nessun contenuto o literal privato nei messaggi. Le raccomandazioni restano segnali statici da valutare, non bug certificati.
- `review_sources` ricontrolla il contenimento fisico; `stat` deve rientrare nel blocco che gestisce errori di lettura. Un file sparito o diventato illeggibile fra inventario e review non deve interrompere la diagnosi.
- Non modificare grammatica dei comandi, selettore modulo semplice, microfono, permessi o richieste GPT. Questa correzione riguarda la diagnosi generale; un analizzatore universale multilinguaggio resta fuori ambito.

Rischi: copertura falsamente completa, lettura involontaria di dati, limiti e concorrenza con aggiornamenti del sorgente. Test soltanto Windows con cartelle temporanee, marker di codice che non deve essere eseguito, cartelle escluse e junction reali ove consentite. Nessuna garanzia di sandbox del filesystem contro sostituzioni concorrenti malevole; nessuna modifica di file da parte della diagnosi.
