# JRV-AUD-006 — dipendenza nativa indipendente da artifact a scadenza

Goal: preparare la stessa DLL no-AVX2 da checkout pulita anche senza Actions artifact, senza compilare/pubblicare Jarvis o un nuovo motore. Base649d1a06477f66ba214fdcb392c28d7af5010613, ramo isolato e PR dipendente dalla38;001–005 conservate.

Fatti verificati: quattro workflow consumano native-engine-proof-not-installable/run41860087656. Artifact13339099748 oggi disponibile, expires_at2026-11-18T15:49:03Z. Non dichiarare la build già fallita: è confermata la dipendenza dalla futura scadenza. La stessa DLL esiste già nel Git del repository pubblico, archivio Download/Jarvis-Gemma-Carattere-e-Stile-61a95f8.zip al commit immutabilef147b1a5faa977e8e4aefe21c9799465a7a8e990. Archivio8.103.631 byte/SHA256c38806cf12574e7ae142a8eef2cebe2afec6244c92db0a195c507d6bade6041a; DLL19.010.560 byte/SHA256ac834f409855bd7e12a0f0c0ffc8601a663b036b2403d74af4b6b3d3afd49bba, identica alla prova nativa esistente.

Scelta: piccolo strumento di build tools/native_model/restore_engine.py e riferimento JSON fissano commit/percorso/dimensione/hash di archivio e DLL. Download pubblico raw dal commit, streaming limitato e hash prima di aprire ZIP; leggere solo il membro DLL atteso, staging e pubblicazione senza sovrascrivere file divergenti. Opzione archivio locale identico per ripristino offline. Riutilizzare checkout upstream già fissato e mantenere tutti i controlli hash esistenti. Nessun nuovo binario in Git, dipendenza Python o servizio.

Alternative: allungare retention sposta il problema; pubblicare una nuova release è fuori scopo; duplicare19MB di DLL non serve perché i byte sono già in Git; ricompilare C++ cambia potenzialmente l'hash e richiede un nuovo collaudo non autorizzato. Non usare main/latest come indirizzo variabile, non modificare i vecchi ZIP. La riproducibilità qui è recupero identico del componente, non compilazione C++ bit-per-bit.

- [ ] Red Windows della nuova capacità: destinazione vuota e nessun artifact/token Actions fornito; il baseline manca di acquisizione autonoma. Se il helper non esiste la destinazione resta vuota e l'asserzione sulla DLL fallisce, senza errori di import. È riproduzione di capacità mancante, non simulazione della cancellazione reale dell'artifact.
- [ ] Helper+manifest con soli moduli standard, verifiche dimensione/hash, ZIP senza estrazione generale, protezione file esistenti e cleanup temporanei; nessuna esecuzione nativa automatica nel helper.
- [ ] Aggiornare quattro consumer; Python disponibile prima dello strumento. Aggiungere percorsi manifest/workflow ai trigger della suite senza modificare guardie build/publisher.
- [ ] Test Windows: download reale dal commit senza artifact, hash originale, vecchio probe DLL (caricamento/export, nessuna inferenza); archivi corrotti/membro errato/hash errato/output preesistente e idempotenza con file temporanei; nessun test Linux.
- [ ] Review indipendente, suite3.11/3.12 e prove native esistenti; evidenza/continuità/mappa strumenti. Build completa/GGUF/Pavilion non eseguiti, dichiararli.

Review focus: nessun riferimento temporale residuo nei consumer; commit/hash immutabili; gestione errori rete/zip/troncamento; nessuna sovrascrittura dati o credenziale; verifiche esistenti e guardie build preservate. Recupero: ramo separato; runtime, download pubblicati e dati personali invariati.022/023 restano aperti.
