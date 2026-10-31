# JARVIS — microfono continuo, cerchio reattivo alla voce e saluto

**Stato:** prova isolata nel ramo `feature/hud-speech-activity-auto-start`, [PR #9 (draft)](https://github.com/MATRIXNEO23/jarvis/pull/9). Il ramo discende dalla versione con dialogo continuo, personalità e HUD più vicino al preview. **Non modifica né sostituisce automaticamente la versione già funzionante sul Pavilion.**

## Ultimo feedback dell'utente

L'utente ha precisato che **la modalità di ascolto non deve corrispondere al colore arancione**. Il microfono deve poter rimanere acceso sempre, ma il cerchio centrale deve reagire alla **voce realmente rilevata**.

| Condizione | Colore del cerchio | Aspetto |
|---|---|---|
| Microfono spento oppure aperto, ma l'utente tace | Ciano | Animazione normale, luce stabile |
| L'utente parla nel microfono | Arancione | Pulsazione luminosa ripetuta |
| JARVIS risponde con la voce Windows SAPI | Verde | Pulsazione luminosa più rapida, prioritaria rispetto all'arancione |

Il nome **JARVIS** resta sempre fisso al centro. La scritta ASCOLTO non deve ricomparire nel nucleo.

### Distinzione tecnica

- `VoiceController.is_listening()` indica che il **flusso audio del microfono è davvero aperto**.
- `VoiceController.is_user_speaking()` indica invece che **l'energia del segnale vocale rilevata recentemente supera la soglia**. Il modulo `speech_activity.py` usa soltanto i campioni PCM 16-bit/16kHz che Vosk legge già, senza un secondo modello, API o registrazioni.
- `OfflineSpeaker.is_speaking()` indica che JARVIS sta effettivamente parlando con SAPI. Ha precedenza nell'indicatore del cerchio; durante la voce dell'assistente, il microfono continua a rimanere aperto, ma l'audio del computer viene ignorato dal riconoscitore e non può far lampeggiare arancione.
- La rilevazione è **approssimativa e basata sull'energia**, non è un identificatore della persona: rumori o altre voci forti potrebbero attivare momentaneamente l'arancione. Il riconoscimento linguistico e i comandi rimangono separati e protetti da Vosk, GPT e dall'esecutore autorizzato.

## Nuovo comportamento all'apertura dell'app

**L'utente ha modificato esplicitamente la regola precedente**, chiedendo che aprendo JARVIS il microfono parta già attivo e sia sempre in ascolto.

- Quando **si apre l'app Jarvis**, l'interruttore **«Avvia Jarvis già in Conversazione continua GPT (microfono attivo)»** è **attivo per impostazione predefinita**, anche per chi proviene da un file di configurazione precedente.
- Circa un attimo dopo aver creato la finestra, Jarvis imposta `GPT_CONVERSATION` e avvia in thread il modello Vosk, senza necessità di pronunciare «Ehi Jarvis».
- Il microfono **non si attiva al semplice avvio di Windows**: questo aggiornamento NON aggiunge alcun programma alla cartella Esecuzione automatica, al Registro o alle attività pianificate.
- La modalità resta attiva mentre l'app è aperta, anche se ci sono programmi pesanti; nessuna transizione automatica verso Standby. L'utente mantiene tutti i controlli di Standby, Premi per parlare, Ascolto continuo con wake word e Conversazione continua GPT.
- Se l'utente disattiva la casella in ⚙, Jarvis **dal prossimo avvio** tornerà inizialmente in Standby; la scelta non cambia senza consenso il microfono della sessione corrente. La preferenza è salvata localmente in `settings.json` come `auto_listen`.
- Se il microfono/Vosk non è disponibile, la modalità selezionata non inventa uno stato di ascolto: il cerchio rimane ciano e gli indicatori mostrano che il flusso non si è aperto. Jarvis non tenta di installare niente né forza riavvii di programmi.
- GPT ha bisogno del normale collegamento e del consenso già in uso; microfono acceso non significa che GPT sia sempre connesso. Le frasi che arrivano a GPT seguono la stessa logica di esecuzione sicura del catalogo.

## Saluto di apertura, in stile JARVIS

`startup_greeting.py` usa **l'orario locale di Windows** senza rete:
- 00–04: «Buonanotte, signore. Come posso esserle utile?»
- 05–11: «Buongiorno, signore. Come posso esserle utile?»
- 12–17: «Buon pomeriggio, signore. Come posso esserle utile?»
- 18–23: «Buonasera, signore. Come posso esserle utile?»

Il saluto appare una volta nella console; viene pronunciato tramite la voce SAPI locale quando le risposte vocali sono abilitate. La modalità GPT continua, come nella versione precedente, abilita la voce quando viene selezionata. La sintesi vocale non richiede GPT né API a consumo. Non viene inviata come richiesta al modello e non diventa un comando Vosk.

## Prova consigliata sul Pavilion

1. Chiudere la vecchia istanza e scaricare [la ZIP di questo ramo](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/hud-speech-activity-auto-start.zip) in **una cartella nuova**; non cancellare la versione precedente, il modello Vosk o il profilo `%LOCALAPPDATA%\\Jarvis`.
2. Avviare `avvia_jarvis.bat`: il microfono deve attivarsi automaticamente **all'apertura dell'app**, senza avviare automaticamente Jarvis con Windows.
3. Durante il saluto il reattore deve lampeggiare **verde**; dopo il saluto, se nessuno parla, deve essere **ciano**, benché il microfono sia ancora acceso.
4. Pronunciare una frase: deve diventare **arancione pulsante** soltanto mentre l'utente parla, poi tornare ciano dopo una breve coda di circa mezzo secondo. Quando JARVIS risponde deve essere verde.
5. Aprire ⚙ e mettere il microfono in Standby: deve chiudersi e il centro rimanere ciano. Selezionare di nuovo Conversazione continua GPT: deve riaprirsi e restare attivo finché lo si desidera.
6. Disattivare l'interruttore «Avvia Jarvis già in Conversazione continua GPT», chiudere e riaprire l'app: deve partire in Standby; riattivarlo e riprovare l'avvio.
7. Provare dialogo continuo, Second Brain, comandi ed eventuale salvataggio file con documenti fittizi. Verificare l'assenza di rallentamenti anomali sull'i3-2100 e che la voce di JARVIS non causi falsi lampeggi arancioni.

I test automatici possono verificare filtri, stati e logica del saluto; non possono dimostrare che il microfono reale rilevi correttamente ogni voce, né misurare la qualità grafica o il consumo del Pavilion. **Nessuna adozione o merge automatico dopo la sola CI.**
