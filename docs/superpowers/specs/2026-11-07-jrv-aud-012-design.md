# JRV-AUD-012 — sorgenti verificati uguali a quelli del pacchetto

Base021/022 verificata `8626d193ef33ddc141f9c1ef1bce3decb0388185`. Nessuna build/ZIP autorizzata: si correggono sorgenti e procedura futura, senza generare un pacchetto dell'app.

Il builder modifica native_ui.py e native_factory.py dopo la suite principale: introduce Prova generazione e fallback DLL bundled con trasformazioni testuali; il launcher cambia profilo per la distribuzione isolata. Eliminare soltanto le trasformazioni Python, trasferendo nei due moduli l'implementazione già esistente nel pacchetto. Testare direttamente quella versione, aggiornando i due helper test che oggi applicano le trasformazioni. Nessun nuovo comportamento nel pacchetto, modello autoavviato, cambio di profilo del launcher sorgente o migrazione dati.

Il futuro workflow registra hash dei file Python/MJS/PS1 tracciati prima del builder e li ricontrolla dopo: deve fallire se il builder altera uno script verificato. Deve fermarsi anche sul primo comando Python fallito, senza lasciarlo coprire dal successivo. Il launcher conserva il profilo isolato Gemma nel pacchetto; non spostare i dati di chi avvia i sorgenti dal profilo AccessoFile.

Prove Windows senza build: builder fermato deliberatamente prima dello ZIP per assenza dei file nativi, writer ZIP vietato tramite stub; controllare byte Python invariati. Eseguire il vero blocco PowerShell del workflow in repository Git temporaneo con solo comando python sostituito da stub: accetta file invariati, rifiuta mutazione e fallimento builder. Prova/factory direttamente dai sorgenti con ABI controllata. Nessuna DLL/GGUF o ZIP dell'app prodotto, test funzionali soltanto Windows. Gli hash e l'estrazione di una build vera rimangono da verificare quando autorizzata.
