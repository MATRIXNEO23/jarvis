# Jarvis: prima versione comando vocale offline (alpha)

Il microfono parte **sempre spento** a ogni apertura di Jarvis.
Il riconoscimento non richiede GPT, servizi cloud, chiavi API o account.
Il motore vocale non e' incluso automaticamente per non appesantire il Pavilion.

## Prima installazione (solo su richiesta)

1. Sul Pavilion, con Jarvis chiuso, avvia `installa_voce.bat`.
   Installa Vosk e SoundDevice per il Python 3 già presente.
2. Scarica il modello italiano leggero ufficiale (circa 48 MB):
   https://alphacephei.com/vosk/models/vosk-model-small-it-0.22.zip
3. Estrai la cartella `vosk-model-small-it-0.22` in:
   `%LOCALAPPDATA%\Jarvis\models\`
   Il file `am/final.mdl` deve quindi trovarsi dentro
   `%LOCALAPPDATA%\Jarvis\models\vosk-model-small-it-0.22\am\`.
4. Riavvia Jarvis con `avvia_jarvis.bat`. Il microfono e' ancora spento.

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
