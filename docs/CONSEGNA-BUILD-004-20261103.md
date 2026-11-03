# Jarvis004 — Programmi e app

Stato: candidata pubblicata e verificata su Windows, collaudo PC pendente. [Download](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-004.zip).

## Risultato

Avvio dei programmi classici e delle app pacchettizzate scelti dall’utente. Catalogo Windows filtrabile, consenso per app, aggiunta manuale .exe/.lnk, prova avvio e comando vocale personale. «Apri la posta», «avvia la posta» e «lancia la posta» possono richiamare la stessa app; nome originale resta utilizzabile. Comando preciso locale; interpretazione GPT esistente soltanto se necessaria e abilitata, con permessi verificati localmente. Ambiguità risolta con scelta contestuale, mai avvio casuale. Elenchi non pronunciati.

Add-on OFF all’installazione; nuove app non autorizzate. Nessuna nuova dipendenza/account, nessun servizio residente. Dati separati nel profilo esistente addon-data/programmi_app/programs.json. Non cancella programmi o preferenze. Non controlla le funzioni interne né chiude/disinstalla le app.

## Identità e provenienza

| Campo | Valore |
| --- | --- |
| Archivio | Jarvis-004.zip |
| Sorgenti confezionati | a1b93f34ff25bd9a972ed971a432af4984366f28 |
| Runtime app già verificato | 3c06c7172693add405a250bc9879aaef2abf59e1 |
| Source precedente con suite542 | 67ca39c4af21c91a12a6306b1ed967f6d83bbedd |
| Ramo recuperabile | build/jarvis-004 |
| Pubblicazione main | bd1905fbb83590111869704bf32086bf457c7127 |
| File / byte | 86 / 282968 |
| SHA-256 | 8589a789fecafd7918bdcf85cb81534ebd079b3531321a3e66042c0ff0a3c980 |
| Git blob ZIP | 5199bba974492f1c92d4f96d6c64043cb5aba747 |
| Versione interna | 0.1.4-candidate / build_number4 |
| Precedente | 003, conservata insieme a001/002 e baseb936879 |

Nessun runtime modificato durante la confezione: solo numero/versione,workflow e verificatore del pacchetto. Nuove suite app aggiunte al processo con cwd estratto: gateway,nativo,servizio,UI e integrazione voce/testo/GPT controllato. Le sole prove sono lette dalla repository, i moduli operativi vengono importati dal pacchetto.

## Verifiche riproducibili Windows

Comandi: python -m unittest discover -s tests -v; python tools/build_file_access.py dist; python tools/check_file_access_package.py dist/Jarvis-004.zip. Windows2022, [run41694455705](https://github.com/MATRIXNEO23/jarvis/actions/runs/41694455705).

| Verifica | Esito |
| --- | --- |
| Python3.11.9 / job126123443591,tentativo2 | 542 OK in65.683s,zero errori/fallimenti/skip |
| Python3.12.10 / job126121209198,tentativo1 riusato | 542 OK in91.793s,zero errori/fallimenti/skip |
| ZIP estratto / Python3.12 | 167 OK in35.306s,zero errori/fallimenti/skip |
| CRC,manifest/hash,contenuti,numero/cartella e launcher unico | PASS |
| Moduli program_apps e manifest apps.launch richiesti | PASS |
| Import dal cwd estratto,UI avvio/chiusura e bundled OFF | PASS |
| Ricostruzione con orologio diverso | Byte-identica PASS |
| Sintassi Python/Node/PowerShell,probe nativi e WindowsSearch live | PASS |
| Publisher126124432192 | PASS,HTTP/hash/byte/link e001/002/003 preservate |

Il primo job3.11/126121208961 ha riportato542 test con un errore: TimeoutExpired15s nella prima invocazione PowerShell del test Explorer test_real_powershell_explorer_selection_and_navigation_contract. Codice del test/helper invariato rispetto alle prove verdi precedenti;3.12 nello stesso run PASS. Rieseguito solo il job fallito sullo stesso SHA, senza allungare timeout o togliere asserzioni:542 PASS. Il timeout resta registrato, causa interna non osservata; ipotesi di lentezza transitoria del runner, nessuna patch runtime attribuita al retry.

Download pubblico riscaricato dal publisher su Windows:282968 byte e SHA256 coincidenti. Metadata/registro e blob Git riletti indipendentemente via API: coincidono. Registro latest4,next5,004 in cima a Download/README e README principale. Il publisher una tantum viene disabilitato dopo il successo; nessuna build periodica.

## Prima prova PC

1. Chiudere la precedente istanza di Jarvis,estrarre004 in una cartella nuova e avviare avvia_jarvis.bat.
2. Impostazioni > Gestisci add-on > Programmi e app > Configura > Aggiorna elenco.
3. Scegliere una sola app per la prova,spuntare Consenti avvio e assegnare una frase facoltativa; Salva.
4. Attivare Programmi e app nel gestore; provare il pulsante Prova avvio oppure «avvia» e il nome/richiamo scelto.

[Guida del componente](../Prima-installazione/Programmi-e-app.md). Ritorno alla precedente cartella003 senza cancellare il profilo o i nuovi dati; nessuna copia del solo manifest nella003.

## Limiti

Trascrizioni e trasporto GPT controllati nei test,non microfono/account/modello personali. Lancio .lnk reale con argomenti e attivazione API di Impostazioni verificati nel runner; API accettata non equivale a visibilità/contenuto della finestra osservati. AppStore terze,layout/DPI e prestazioni Pavilion restano prove PC. Nessuna promessa d’inventario universale o fusione di launcher diversi per solo nome. Limite20 della ricerca file,caso Programmi Explorer e rischi salva/chiudi precedenti non modificati da questa consegna. Nessuna promozione automatica a BASE-UTENTE.
