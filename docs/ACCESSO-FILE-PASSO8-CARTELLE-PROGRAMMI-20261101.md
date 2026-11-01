# Cartella del programma: risoluzione locale — 1 novembre 2026

## Obiettivo e scelta
L'utente vuole trovare la cartella giusta del programma senza conoscerne il nome tecnico o il percorso, adattandosi al profilo/PC corrente. Gli esempi su Minecraft e il suggerimento web descrivono l'obiettivo, non impongono un'architettura. Riutilizzare le fonti Windows e il modello esterno solo dove serve; web rimane un aiuto eventuale.
La review sul source a279a4e/checkpoint dd9654e mostrava già Uninstall/Store, indice Windows, policy e raffinamento GPT. Mancavano App Paths, destinazioni dei collegamenti Desktop/Start e template del profilo con sottopercorso. Aggiunte nei componenti responsabili, senza indice, servizio, framework o add-on parallelo.

## Cambiamenti effettivi
| Componente | Modifica |
|---|---|
| file_access/windows.py | program_location valida un target locale; installed_locations consulta anche App Paths e shortcut; user_path_hint risolve APPDATA/LOCALAPPDATA/USERPROFILE con Known Folders |
| file_access/windows_shell.ps1 | Lettura dei .lnk esistenti in Desktop/Start utente/comuni, senza avviarli o salvarli; Store indipendente, così il suo errore non scarta i collegamenti |
| file_access/service.py | Varianti naturali di localizzazione, template portabili, identità esatta prima di nomi soltanto simili, raggruppamento coerente delle fonti |
| conversation_router.py | Indica al modello i template utente supportati e la risoluzione locale del profilo |
| file_access/AccessoFile.jaddon | Aggiorna la descrizione dell'azione localizza esistente; stesso ID e gestore |
| tests/test_program_locations.py | 11 nuove prove Windows native e dei raccordi, con esiti verificabili |
| file_access/LEGGIMI.md | Esempi, confini e nessuna dipendenza aggiuntiva |

## Percorso operativo
«Dove è installato Nome» e «trovami la cartella del programma Nome» usano locate. La fonte può essere il nome leggibile di un collegamento che punta a una directory/eseguibile di nome differente: il motore legge il target reale, verifica file locale e policy, poi mostra la cartella. L'indice non è obbligatorio quando queste fonti risolvono la richiesta.
«Apri cartella 1» riusa selezione e verifiche già esistenti. Un nome esatto fra programmi simili conserva solo quell'identità; più identità non risolte producono una domanda breve e mantengono locate. Le nuove frasi incomplete restano al percorso di interpretazione/chiarimento, senza cercare “installato” come nome.
Il modello può proporre %APPDATA%\\Nome, %LOCALAPPDATA%\\Nome o %USERPROFILE%\\Nome per target/scope delle azioni che li accettano: Windows ricava la base del profilo corrente, quindi il servizio controlla presenza e permessi. Non ci sono percorsi di Minecraft o nomi utente codificati. I template non estendono il perimetro consentito né cambiano i vincoli della richiesta.

## Confini e semplicità
App Paths/Uninstall sono letti soltanto da HKCU/HKLM nelle viste 32/64 bit; nessuna registrazione modificata dal runtime. Gli unici dati modificati nel registro durante i test sono chiavi HKCU temporanee, rimosse dal cleanup.
Il helper Shell è quello esistente, finito e con timeout; non viene avviato un servizio residente. Ricerca link limitata a 2000 voci e 40 candidati, risultati complessivi limitati come prima; reparse point non attraversati. Sono indizi disponibili, non un inventario completo.
Non vengono eseguiti collegamenti, eseguibili o argomenti. WorkingDirectory non viene scambiata per directory di installazione. Target mancanti, reti, comandi, icone non eseguibili e host generici (per esempio javaw per un gioco) non vengono certificati come cartelle del programma. Un launcher che avvia un altro gioco può richiedere un chiarimento o altre evidenze: non si deduce la directory del gioco dalla sola directory del launcher. Resta la distinzione già dichiarata fra percorso candidato, directory dell'eseguibile e ruolo d'installazione.
Percorsi con virgole non vengono troncati; DisplayIcon perde soltanto il suffisso numerico dell'indice. I percorsi sono canonizzati e ricontrollati dalla policy attuale.

## Fonti tecniche primarie
- [Microsoft: Application Registration](https://learn.microsoft.com/en-us/windows/win32/shell/app-registration), App Paths e significato del valore predefinito rispetto a Path.
- [Microsoft: Shell Links](https://learn.microsoft.com/en-us/windows/win32/shell/links), target, WorkingDirectory e argomenti come informazioni distinte.
- Adapter Known Folders e policy esistenti nel repository, già coperti dai probe Windows. Questa modifica non ricostruisce l'indice Windows.

## Sorgenti e cronologia delle prove
Runtime introdotto in d02e9c9580ddf15dd0dd9b384561d7b30969c246. Run 41348798109: 466 test, un fallimento del vecchio test Store che confrontava il percorso DOS con quello lungo; tutte le 11 nuove prove passate.
Correzione solo test in 7384a71c73b2d269ee0712a6f41febff491ea4a7: os.path.samefile, nome della fonte, unicità e reale esclusione della cartella privata. Run 41349085946 successiva PASS. Ricontrollo mirato del parser nel source d379368c0c9ebaee93816fa2ea739bae5cf5b0f0 per evitare che una frase incompleta ricerchi la parola “installato”; due nuove asserzioni nelle prove esistenti.
[Run 41349291815](https://github.com/MATRIXNEO23/jarvis/actions/runs/41349291815) SUCCESS: 466 test per job Python 3.11/3.12, sintassi/probe/indice Windows live PASS; build/ZIP/publisher skipped. [Evidenza](evidence/program-locations-20261101.json).

## Copertura e limiti
Prova principale: .lnk creato/letto dalla COM Windows reale, nome app differente da directory/exe, ingresso voce con trascrizione controllata, risultato giusto per identità del filesystem e apertura della cartella una sola volta (Popen intercettato), senza GPT o scansione per nome.
Altre prove: due radici profilo controllate, App Paths HKCU reale, template modello per due profili, identità simili e chiarimento, nomi con virgole, host/rete/target assenti, revoca e policy. I profili simulati non sono due PC reali; gli eseguibili fixture non vengono eseguiti.
Non sono prove del microfono/STT audio, qualità del modello/account reale, desktop personale, prestazioni Pavilion o riconoscimento universale di ogni gioco/launcher. Se non basta l'evidenza, va presentato il limite o chiesto un chiarimento, non inventata una posizione.

## Ripresa e consegna
Passo locale da chiudere solo dopo il verde della run del source finale. Aggiornare handoff, evidenza, guida e catalogo. Nessuna build automatica o nuova consegna installabile; per un futuro pacchetto esplicitamente richiesto verificare ZIP estratto e percorsi prima della consegna. La ricerca web e la sua eventuale integrazione non sono prerequisiti per questo percorso locale.
