# Jarvis — Recupero automatico di Blocco note chiuso manualmente

## Problema reale

L'utente ha salvato un documento e ha chiuso autonomamente la finestra di Blocco note. Una successiva richiesta di creare un **nuovo documento di testo** riceve «esiste già un documento aperto», perché il gestore documenti e il dialogo UI potrebbero conservare la vecchia sessione in memoria.

## Comportamento richiesto

Quando si chiede di creare un documento, Jarvis deve controllare l'esistenza dell'**originale Blocco note aperto da Jarvis** (PID + HWND). Se è davvero chiuso, deve liberare il riferimento e la precedente conferma di salvataggio/chiusura, poi aprire un altro documento.

Se la finestra è **ancora aperta** oppure Windows non è in grado di verificarne la presenza, Jarvis NON deve inventare che sia chiusa: lascia intatti la sessione e l'eventuale testo non salvato. Anche un titolo cambiato con «Salva con nome» non è una prova che il documento sia chiuso.

## Implementazione

- `notepad_controller.py`: `session_state(note)` distingue `closed`, `open`, `uncertain`; solo process termination, sparizione dell'HWND originale o suo riutilizzo da un PID diverso identificano la chiusura certa. Nessun intervento su finestre esterne.
- `managed_documents.py`: `forget_if_closed()` abbandona la sessione **solo** quando lo stato è `closed`; `open_blank()` e `compose(target=new_notepad)` rivalidano prima di rifiutare il nuovo documento.
- `document_recovery.py`: ripristina insieme stato del documento e dialogo di conferma, dopo chiusura certa, senza alcuna cancellazione di file.
- `jarvis.py`: riconcilia il dialogo e le variabili UI in ingresso a chat, voce e operazioni documenti; polling economico e limitato (ogni 1,5 secondi) se la sessione è aperta. Un GPT in corso su un documento chiuso non ottiene autorizzazioni a usare quello nuovo.

## Test

CI Python 3.11/3.12 su Windows e Ubuntu; test unitari su:
- nuovo Blocco note dopo chiusura manuale del precedente;
- nuovo testo dopo chiusura del precedente;
- un titolo cambiato/non leggibile non provoca perdita della sessione;
- consenso al salvataggio del vecchio documento non resta attivo;
- un ID vecchio non può salvare/modificare il nuovo documento;
- PID riutilizzato per un'altra finestra non deve essere scambiato per il documento precedente.

**Il collaudo reale sul Pavilion non è stato eseguito** (l'utente aveva deciso di rinviare il collaudo generale). Per test futuri: backup completo `%LOCALAPPDATA%\Jarvis`, avvio di una sola istanza, aprire documento con Jarvis, scrivere e salvare, chiuderlo manualmente, chiedere «crea un nuovo documento di testo», verificare che se ne apra uno nuovo e che il file precedente resti invariato.

## Sicurezza

Il precedente allarme Microsoft Defender `Trojan:Script/Wacatac.B!ml` sul pacchetto di Jarvis è ancora irrisolto. Test unitari e CI non lo escludono; non disattivare antivirus, non impostare eccezioni e non forzare l'esecuzione del file bloccato.
