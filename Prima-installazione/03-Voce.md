# 3. Microfono e risposte vocali
Sono due funzioni separate: riconoscere ciò che dici e leggere la risposta a voce.

## Riconoscimento italiano
1. Chiudi Lumi.
2. Dalla cartella programma avvia installa_voce.bat.
3. Lo script installa Vosk 0.3.45 e sounddevice 0.5.3 nel Python usato da py -3.
4. Scarica il modello vosk-model-small-it-0.22. Verifica che esista:
   %LOCALAPPDATA%\Jarvis\models\vosk-model-small-it-0.22\am\final.mdl
5. Avvia Lumi con avvia_lumi.bat. Apri ingranaggio → Voce.
6. Seleziona manualmente Premi per parlare e prova una frase, per esempio «apri la calcolatrice». Controlla la trascrizione e il risultato.
7. Per parlare al GPT esterno, collega prima GPT e scegli Conversazione continua GPT. Standby spegne il microfono.

Il modello è usato localmente; la conversazione con GPT invia al modello esterno il testo riconosciuto.
**Versione base b936879:** l'avvio segue auto_listen; il preparatore del profilo Trial la imposta inizialmente attiva. Per spegnere l'ascolto scegli Standby; per non riattivarlo al prossimo avvio disabilita la preferenza di ascolto automatico nelle impostazioni. La migrazione una tantum del vecchio Trial è distinta dalla scelta manuale successiva.
**Ramo successivo a86c2c9/5e61e53:** impone invece standby all'avvio. Non confondere i comportamenti e non cambiare versione per questa differenza senza una scelta esplicita.
Il profilo Trial può riusare in sola lettura il modello del profilo base: non duplicarlo se è già completo.

Se il modello non si scarica, la [fonte del modello](https://alphacephei.com/vosk/models/vosk-model-small-it-0.22.zip) è quella usata dallo script. L'archivio va estratto mantenendo la cartella del modello nel percorso sopra. Una cartella incompleta non va sovrascritta senza averla identificata.

## Voce delle risposte (Lumi 023)
Tre tipi di voce, scegli nel menu Voce:
- **Paola, Serena (consigliate, offline)**: il motore Piper è già nella cartella `voce_engine` di Lumi. Ingranaggio → Voce → «Scarica Paola» o «Scarica Serena» (download dal repository con verifica), poi scegli «Piper: Paola/Serena» e premi «Prova voce». «Effetto digitale» regola il tocco olografico (0 = voce pulita). Se il motore non parte su questo PC, Lumi usa la voce di Windows e lo scrive.
- **Edge: Isabella, Elsa, Diego, Giuseppe (online)**: gratuite, molto naturali, ma serve Internet e il testo da leggere viene inviato al servizio di sintesi Microsoft. Una volta: chiudi Lumi, esegui `installa_voce_edge.bat`, riavvia Lumi, premi «Aggiorna voci» e scegli una voce «Edge:». Senza rete Lumi passa alla voce di Windows.
- **Voci di Windows**: sempre disponibili, nessuna installazione.

In tutti i casi la voce parte dalla prima frase pronta, non legge emoji e asterischi e la bocca dell'avatar segue l'audio.

### Voci di Windows
1. Apri ingranaggio → Voce.
2. Attiva Lumi risponde a voce.
3. Premi Aggiorna voci, scegli una voce disponibile e premi Prova voce.
4. Se non senti nulla, controlla volume, uscita audio e Mixer volume di Windows.
5. Una voce italiana come Microsoft Cosimo è utilizzabile solo se compare nell'elenco locale.

Non servono pyttsx3 o un modello vocale generativo per la sintesi attuale: viene usato Windows SAPI tramite PowerShell.
Se non compare una voce italiana, controlla i componenti vocali italiani nelle impostazioni lingua/voce di Windows e ricarica l'elenco in Jarvis; il nome esatto dipende dall'edizione e dai componenti installati.

## Errori distinguibili
- Modello italiano mancante: manca la cartella corretta o il file am\final.mdl.
- Componenti vocali mancanti: pacchetti Python assenti nell'interprete di Jarvis.
- Dispositivo non disponibile: controllare microfono predefinito e permesso di accesso al microfono per le app desktop nelle impostazioni privacy di Windows.
- Standby: scelta intenzionale, non guasto.
- Sintesi non disponibile: controllare voce Windows/PowerShell e uscita audio; è indipendente da Vosk.
