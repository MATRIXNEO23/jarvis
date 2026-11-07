# Voce offline — guida operativa

Il riconoscimento usa Vosk e il microfono del PC; la sintesi usa le voci Windows SAPI. La configurazione delle risposte vocali è separata dalla modalità del microfono. Nessun account è necessario per queste due funzioni locali.

## Installazione facoltativa

1. Chiudi Jarvis e avvia [installa_voce.bat](../installa_voce.bat) dalla cartella estratta. Lo script installa Vosk0.3.45/SoundDevice0.5.3 e richiama [installa_modello_voce.py](../installa_modello_voce.py). Non viene eseguito automaticamente da Jarvis.
2. Il modello italiano piccolo viene scaricato dalla fonte ufficiale: https://alphacephei.com/vosk/models/vosk-model-small-it-0.22.zip. Rete necessaria solo per questa installazione; non serve aggiungere un servizio a pagamento.
3. Percorso standard: `%LOCALAPPDATA%\Jarvis\models\vosk-model-small-it-0.22\`. I profili di prova possono leggere il modello già presente senza spostarlo. Per configurazioni personalizzate controlla il percorso indicato nell'errore.
4. Riavvia Jarvis e scegli la modalità desiderata. L'installer non modifica la preferenza di avvio del microfono.

Se manca il modello, verifica che nella cartella indicata esista `am\final.mdl`. In caso di download fallito puoi estrarre manualmente il modello ufficiale in quella posizione; conserva eventuali cartelle precedenti e dati prima di intervenire. Errori di dispositivo richiedono di controllare il microfono in Windows e riprovare la modalità, senza cancellare il profilo.

## Ascolto e avvio

- **Standby:** microfono spento.
- **Premi per parlare:** ascolta mentre tieni premuto il pulsante.
- **Ascolto continuo:** con dettatura disattivata puoi parlare direttamente. La dettatura in altre finestre richiede attivazione manuale; quando è attiva, il richiamo Jarvis distingue i comandi dal testo dettato.
- **Hey Jarvis:** inizia ogni richiesta con Jarvis nella stessa frase, per esempio «Jarvis, apri la calcolatrice». Le altre frasi vengono ignorate. I comandi locali mantengono la priorità; GPT richiede abilitazione, collegamento e permessi. Il solo nome non apre una finestra libera per la frase successiva.

All'apertura vale la preferenza di ascolto automatico salvata. I valori di prima installazione possono abilitarlo; non è corretto promettere Standby a ogni avvio. Una configurazione esistente illeggibile usa invece l'avvio prudente descritto in [Recupero impostazioni](RECUPERO-IMPOSTAZIONI.md). Jarvis non aggiunge con questa funzione un avvio automatico con Windows.

Gli elenchi dei file rimangono visuali; non vengono letti integralmente. I risultati vocali dipendono dalle preferenze TTS e dalle voci installate. Le impostazioni e i dati appartengono al profilo attivo: non sostituire quello dell'altra installazione.

## Prova sul PC

Controlla apertura/chiusura del microfono, richiamo, comando locale innocuo, risposta SAPI e assenza di eco che riattivi una richiesta. Verifica anche Standby e riavvio con la tua preferenza salvata. Qualità audio e consumo sul PC richiedono questa prova reale; i test con trascrizioni controllate non la sostituiscono.

La documentazione storica precedente è conservata nel [commit di riferimento](https://github.com/MATRIXNEO23/jarvis/blob/605c7056a1320523bb2a177fc95acbadb70a6159/docs/VOCE_OFFLINE.md). Questa guida accompagna i sorgenti corretti; non aggiorna da sola i pacchetti già pubblicati.
