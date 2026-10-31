# Jarvis: prima versione comando vocale offline (alpha)

> **Nota aggiornata 31/10/2026:** questa guida documenta una fase precedente con microfono spento al lancio. Nel ramo di audit attuale è richiesta e configurata la **conversazione GPT con microfono attivo all'avvio**, purché Vosk e il dispositivo funzionino. Le modalità si possono sempre modificare manualmente; le sezioni sottostanti sono prove storiche.\n\n
Il microfono parte **sempre spento** a ogni apertura di Jarvis.
Il riconoscimento non richiede GPT, servizi cloud, chiavi API o account.
Il motore vocale non e' incluso automaticamente per non appesantire il Pavilion.

## Prima installazione (solo su richiesta)

1. Sul Pavilion, con Jarvis chiuso, avvia **`installa_voce.bat`** nella
   cartella della versione di prova. Non servono i diritti amministratore.
2. Lo script installa Vosk/SoundDevice per il Python disponibile e scarica
   il modello italiano piccolo (circa 48 MB) dalla fonte ufficiale:
   https://alphacephei.com/vosk/models/vosk-model-small-it-0.22.zip
   Il download avviene **solo** dopo l'avvio manuale dello script.
3. Il modello va automaticamente in
   `%LOCALAPPDATA%\Jarvis\models\vosk-model-small-it-0.22\`.
   L'installazione valida i percorsi nell'archivio ed evita di sovrascrivere
   un modello già presente. Connessione richiesta **solo per l'installazione**.
4. Avvia `avvia_jarvis.bat`. Il microfono resta spento fino alla scelta manuale.

Se il download non va a buon fine, puoi estrarre manualmente il file ZIP
ufficiale nella cartella `%LOCALAPPDATA%\Jarvis\models\`, verificando
che esista `vosk-model-small-it-0.22\am\final.mdl`.
Non eliminare la tua vecchia cartella Jarvis: prova la voce in una cartella separata.

## Modalità

- **Standby**: microfono spento; predefinito ad ogni avvio.
- **Premi per parlare**: seleziona la modalità, poi tieni premuto
  «Tieni premuto per parlare» e rilascia per terminare l'audio.
- **Ascolto continuo**: il microfono resta attivo fino a selezione manuale
  di un'altra modalità, chiusura di Jarvis o errore hardware.
  Non passa in standby automaticamente se apri Minecraft.

La voce riconosce offline solo alcuni comandi locali innocui già presenti,
per esempio «Jarvis, apri la calcolatrice» o «controlla la RAM».
I testi non riconosciuti come comandi sono mostrati e, se il campo è vuoto,
copiati nella casella testuale per revisione manuale. Non attivano GPT o
eseguono automaticamente file, script o comandi di shell.

Non vengono salvati audio né inviati a Internet. Le parole riconosciute
che diventano comandi locali sono registrate nella cronologia di Jarvis,
come gli stessi comandi scritti.

## Collaudo Pavilion

1. Avvia Jarvis: verifica «Microfono spento».
2. Seleziona «Premi per parlare» e tieni premuto il pulsante.
3. Pronuncia «Jarvis, apri la calcolatrice» e rilascia:
   dovrebbe aprirsi la calcolatrice.
4. Seleziona «Ascolto continuo», prova «stato sistema» e apri Minecraft.
   La modalità selezionata non deve cambiare da sola.
5. Seleziona «Standby»: il microfono deve smettere di acquisire audio.
6. Chiudi e riapri Jarvis: deve sempre partire in standby.

Il riconoscimento vocale reale, i dispositivi audio e il carico CPU/RAM
sono ancora da collaudare sul Pavilion. Errore o mancanza di modello
non devono impedire l'uso dei comandi testuali o di ChatGPT.
