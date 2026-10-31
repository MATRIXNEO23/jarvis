# Jarvis — Timer vocale e impostazioni riorganizzate (31 ottobre 2026)

## Timer
Il conto alla rovescia e' una finestra Tk separata dalla dashboard Jarvis.
Le cifre LED digitali mostrano `MM:SS` (oppure `HH:MM:SS` sopra un'ora).
Nella finestra, gli utenti possono inserire ore, minuti e secondi e
premere **START**, **PAUSA**, **STOP**, **RESET**.

Comandi locali disponibili:
- `timer`: apre la finestra per l'inserimento manuale;
- `timer 10 minuti` / `avvia timer da 10 minuti`: apre e avvia;
- `pausa timer`, `riprendi timer`, `stop timer`, `reset timer`;
- `quanto manca al timer`: mostra il tempo restante nel log di Jarvis.

Nella modalita' ascolto continuo e' necessario rivolgersi a Jarvis con
la wake-word gia' prevista. Il timer non usa ChatGPT o internet.

## Impostazioni
L'ingranaggio apre sempre **la stessa finestra Impostazioni**.
Le funzioni gia' presenti sono divise in categorie:
1. **Voce** — modalità microfono, dettatura, voci Windows e correzioni;
2. **GPT e memoria** — account ChatGPT e Second Brain;
3. **Progetti e servizi** — progetti, Telegram, add-on;
4. **Timer e allarmi** — suonerie locali, prova, volume, ripetizione e apertura timer.

Non sono stati eliminati pulsanti o handler delle impostazioni originali.
Le nuove preferenze `timer_sound`, `timer_volume` (0-100) e
`timer_repeat` vengono salvate insieme a quelle esistenti in
`settings.json`, e il profilo di prova resta isolato.

## Suoni
I cinque toni sono generati interamente in memoria come WAV PCM:
Bip digitale, Doppio bip, Allarme elettronico, Sirena, Avviso delicato.
Il volume regola realmente l'ampiezza del segnale.
La riproduzione usa `winsound` su Windows e un thread daemon;
nessun file modello, API, libreria o costo aggiuntivo.

## Collaudo
Eseguire `py -3 -m unittest discover -s tests -v` e
`py -3 -m compileall -q .`.
Sul Pavilion provare con il microfono e con le impostazioni originali:
`timer 1 minuto`, PAUSA / START, STOP / RESET,
suoneria PROVA e timer a scadenza con STOP.
Verificare anche accesso GPT, voce offline, Telegram, progetti e add-on.

La suite automatica non sostituisce il collaudo reale su Windows 10.
