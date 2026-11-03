# Navigazione Explorer — nomi visualizzati e riscontro PC, 3 novembre 2026

## Riscontro PC — navigazione Explorer in diversi casi riuscita, 3 novembre 2026
L'utente riferisce di navigare nella stessa finestra Explorer, entrare in Windows, Debug e varie altre cartelle: funzionamento positivo riferito, non nuovo test CI o conferma universale. Resta il caso «aprimi Programmi» con errore riferito in modo approssimativo (accesso negato/cartella non trovata); ipotizza un punto finale e segnala nomi poco pronunciabili. Il risultato del test contestuale della cartella già indicata non è ancora stabilito da questi comandi diretti.
Lettura statica della002/source6f48ad1: _explorer_target costruisce root/name, senza risolvere il nome visualizzato localizzato; lo Shell helper view restituisce percorso/handle/selezione, non mappa etichette→percorsi. «Programmi» può essere un'etichetta italiana di un percorso diverso (es. Program Files); sul PC ciò resta da verificare col messaggio esatto. Il ramo generico apri/aprimi conserva eventuale punteggiatura nel target. Policy.permits verifica le regole e la risoluzione del percorso, senza un divieto specifico per Programmi; l'errore riferito non dimostra da solo un divieto Windows reale.
Nessuna modifica runtime, nuova prova funzionale o build003.001/002 immutabili. Conservare l'esito positivo e separare l'eventuale correzione dei nomi Explorer dal collaudo del contesto della002.

## Punti sorgente verificati
- file_access/service.py, source6f48ad1: _explorer_context e _explorer_target (righe263–299), parse_command e ramo generico apri/aprimi (righe378–479).
- file_access/windows_shell.ps1: operazione view restituisce il percorso reale della cartella e gli elementi selezionati.
- file_access/policy.py: permits combina regole di autorizzazione e destinazione risolta.

Il riscontro PC specifico non è stato riprodotto su Windows in questa unità e non è stata acquisita la riga esatta dell'errore. Non presentare una deduzione dal codice come causa già dimostrata sul PC, né attribuire tutti gli errori al punto finale.
