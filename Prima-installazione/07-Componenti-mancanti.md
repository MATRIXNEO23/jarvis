# 7. Componenti mancanti e messaggi
Questa pagina distingue ciò che il codice già rileva da ciò che è ancora da aggiungere. Non è una dichiarazione di diagnosi universale.

## Controlli già presenti nel riferimento
| Situazione | Dove rilevata | Indicazione/azione |
|---|---|---|
| Launcher Python py assente | avvia_jarvis.bat | Messaggio nella finestra di avvio; installare Python/launcher |
| SDK GPT assente | gpt_client.py e diagnostica runtime | «SDK GPT non installato»; eseguire installa_gpt.bat |
| Node assente | gpt_client.py e diagnostica | Node non trovato nel PATH |
| npm/Node troppo vecchio | installa_gpt.ps1 | Installazione interrotta con motivo |
| Bridge GPT assente o non attivo | diagnostica runtime | Stato del componente, non prova d'inferenza |
| Modello Vosk assente | voice_control.py | Modello italiano mancante |
| Vosk/sounddevice assenti | avvio ascolto | Componenti vocali mancanti, installa_voce.bat |
| Microfono in standby | diagnostica runtime | Stato intenzionale, non componente mancante |
| Telethon assente | configurazione e operazioni Telegram | Installare con installa_telegram.bat |
| FFmpeg assente | operazioni vocali Telegram | Mancanza segnalata; niente invio vocale |
| SAPI/sintesi/conversione fallita | operazione vocale | Errore della sintesi o conversione, non successo |
| Account Telegram/contatti assenti | pannello Telegram e controlli invio | Configurare account e selezionare contatti |
| Add-on non valida | gestore add-on | File ignorato/avviso, azione non abilitata |

Oggi questi segnali sono distribuiti fra console di avvio, stato del pannello, finestra errore e chat. Non tutti compaiono già uniformemente nella chat.
Se Python/Tkinter non permette l'avvio dell'interfaccia, Jarvis non può mostrare una chat: l'errore deve rimanere leggibile nel launcher.

## Comportamento richiesto da completare
Quando attivi/usI una funzione, la chat deve indicare componente assente, funzione bloccata e passo utile, senza inventare la causa. Le funzioni non interessate devono restare disponibili. Un modulo facoltativo disattivato non è un errore.

Formato proposto:
«Telegram: manca FFmpeg. Le note vocali non sono disponibili. Segui Prima-installazione/04-Telegram.md.»
È un esempio di messaggio desiderato, non una citazione garantita della UI attuale.

Distinguere assente, installato ma non configurato, account non connesso, errore operativo e verifica non eseguita. Non installare o cancellare componenti automaticamente per deduzione del modello.
Niente monitoraggio continuo pesante: controlli leggeri a richiesta/attivazione e prove finite quando richieste.

## Test da realizzare prima della consegna della diagnostica nuova
Simulare dipendenze assenti, interprete sbagliato, versione incompatibile, modello incompleto, account scollegato ed errore di conversione; verificare messaggio utile e nessun falso successo. Testare la coerenza fra prerequisiti documentati e quelli verificati dal programma.
Il collegamento con le add-on nuove segue lo stesso criterio. Questi nuovi test e l'unificazione dei messaggi non sono stati implementati creando la documentazione.
