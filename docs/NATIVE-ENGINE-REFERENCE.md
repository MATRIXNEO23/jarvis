# Riferimento persistente del motore nativo — JRV-AUD-006

I consumer della DLL usavano l'artifact13339099748 della run41860087656, con scadenza18 novembre2026 ore15:49:03UTC. L'artifact era ancora disponibile durante questa correzione: non è stato cancellato né dichiarato già scaduto.

La stessa DLL è già nel Git pubblico di MATRIXNEO23/jarvis. Il recupero usa lo ZIP esistente, non un nuovo binario o una nuova build:

- Commit archivio: `f147b1a5faa977e8e4aefe21c9799465a7a8e990`.
- File: `Download/Jarvis-Gemma-Carattere-e-Stile-61a95f8.zip`.
- Archivio:8.103.631 byte, SHA256 `c38806cf12574e7ae142a8eef2cebe2afec6244c92db0a195c507d6bade6041a`.
- DLL:19.010.560 byte, SHA256 `ac834f409855bd7e12a0f0c0ffc8601a663b036b2403d74af4b6b3d3afd49bba`.
- Sorgente upstream/provenienza: LostRuins/koboldcpp `7e0eb2dc4a23f1a0fc42a7660ad43be7a4b9e759`, build originale Jarvis run41860087656/source0b819a8c3f3a1911652b11811421da0c4f1e4f2e. [Prova precedente](evidence/native-engine-20261104.json).

Il file Python upstream normalizzato LF ha SHA256 `17e234e20c410e770858a58bfe5b3a84f15374e8ed462e2b884faeb653369d96`; il blob Git `7805cd49cd1f7a8f0101aba52721af7a771067af` coincide col contenuto upstream fissato. Se la cartella destinazione contiene koboldcpp.py, lo strumento verifica questa identità senza cambiare terminatori o contenuto.

## Mappa dei sorgenti

| File | Responsabilità |
|---|---|
| tools/native_model/engine-reference.json | Commit, nomi, dimensioni e hash immutabili. |
| tools/native_model/restore_engine.py | Download limitato da raw Git o archivio locale, doppio controllo hash, estrazione selettiva, staging e pubblicazione senza sovrascrittura. Solo preparazione build/CI. |
| tools/native_model/probe.py | Probe Windows già esistente: carica DLL e chiama export di sola osservazione, senza modello. |
| tests/test_native_engine_reference.py | Recupero reale con sorgente upstream fissato e probe DLL; fixture ZIP sintetiche per integrità, file esistenti e errori. |
| .github/workflows/gemma-windows-test-package.yml | Ripristina dipendenza prima dei vecchi controlli e della build, quando autorizzata. |
| .github/workflows/native-gemma.yml, native-bridge-real.yml, native-abort-real.yml | Stesso recupero al posto dell'artifact temporaneo; pin upstream e controlli esistenti conservati. |
| .github/workflows/tests.yml | Suite Windows, attivata anche da cambi al manifest/consumer; guardie build e publisher conservate. |

Questa utilità non appartiene al runtime Jarvis e non introduce add-on, servizi o dipendenze Python. L'indice generale canonico resta docs/INDICE-SORGENTI.md su main; questa pagina descrive il nuovo raccordo di build del ramo evoluto.

## Uso per sviluppo/CI

Da checkout di Jarvis, dopo il checkout upstream già previsto dai workflow:

```
python tools/native_model/restore_engine.py --destination upstream-kobold
```

Per riusare offline una copia **identica** dello ZIP fissato:

```
python tools/native_model/restore_engine.py --archive percorso/archivio.zip --destination upstream-kobold
```

Viene estratto solo il membro DLL atteso. Un file esistente diverso causa errore e resta intatto; un file identico viene riusato. Dati estratti e download restano temporanei fino alle verifiche. Nessun GGUF o modello viene scaricato, nessun server avviato, nessuna compilazione eseguita e nessun archivio applicativo prodotto dallo strumento.

Il recupero dipende dalla disponibilità del repository GitHub o di una copia locale verificata, senza la scadenza della retention Actions. Non è una prova di compilazione C++ bit-per-bit; conserva gli stessi byte verificati, la provenienza e i checkout sorgente/licenze già esistenti. La build completa e il collaudo Windows10/i3-2100 devono essere svolti separatamente prima di un rilascio, su autorizzazione.022/023 restano aperti.

## Verifica della correzione

Source `c0007689154efa574917ddb2ce23279ddf36c5f8`, [run42339214356](https://github.com/MATRIXNEO23/jarvis/actions/runs/42339214356) SUCCESS:716 test per Python3.11.9 e3.12.10 su Windows2022. Il nuovo recupero reale fornisce prima il sorgente upstream fissato, scarica lo ZIP immutabile senza artifact Actions, verifica i byte della DLL e la carica col probe esistente. Sette export disponibili e token iniziali0; nessuna generazione o modello. Otto nuove prove comprendono integrità/errori e conservazione dei file. [Evidenza](evidence/jrv-aud-006-20261107.json).

I quattro collegamenti ai workflow sono stati recensiti staticamente; l'action checkout, i workflow di inferenza e la build del pacchetto non sono stati eseguiti in questa fase. Nessun binario è stato ricompilato e nessun archivio applicativo è stato creato o pubblicato.
