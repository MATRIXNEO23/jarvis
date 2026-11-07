# JRV-AUD-021 — chiusura del solo helper vocale posseduto

Base019 verificata `e059883a1e446ca71452a2358920b4af02001b69`. L'utente autorizza correzioni mirate preservando il funzionamento; niente build/dati personali o gestione di processi estranei.

## Causa dimostrata

OfflineSpeaker.close imposta l'evento e svuota la coda, ma il runner predefinito usa subprocess.run senza conservare il processo attivo. Il chunk SAPI in corso può continuare fino alla sua fine o al timeout90s. Il thread è daemon: la chiusura UI non certifica uscita del figlio.

## Contratto minimo

Il runner Windows predefinito per la voce conserva il Popen dell'helper creato da Jarvis. Pubblicazione/rimozione del riferimento e chiusura sincronizzate con un lock breve; chiusura prima della pubblicazione rifiuta l'invio del testo e ritira il figlio appena creato. close resta terminale/idempotente, svuota la coda e richiede termine solo a quel Popen, mai per nome/PID generico. Nessun taskkill, processo Explorer o applicazione utente. Il timeout communicate resta90s; la pulizia conserva l'errore primario anche se Windows rifiuta kill. Come per Popen/run, non è un hard deadline del cleanup quando il sistema rifiuta la terminazione: il worker può attendere l'uscita effettiva, mentre close sulla UI non la attende.

Popen/communicate, attese e termine fuori dal lock. La UI non aspetta la fine naturale di un chunk o l'intero timeout90s. Il worker libera riferimenti/pipe in finally; errore di cancellazione non maschera errori attivi o interrompe le altre fasi di chiusura dell'app. Non dichiarare is_speaking=False prima dell'effettiva uscita dal runner; mantenere cooldown/anti-eco, limiti coda/chunk/testo e JSON su stdin con comando fisso/cwd SystemRoot.

Runner personalizzati a due argomenti (payload, timeout keyword) restano compatibili; un callable iniettato non cooperativo non viene terminato forzatamente. installed_voices conserva il percorso finito esistente. Non aggiungere un nuovo comando mute/stop o cambiare checkbox/microfono; questa correzione riguarda close.

## Prove e limiti

Windows2022/Python3.11/3.12, processi figli Python temporanei al posto dell'helper SAPI per controllare avvio, lettura JSON, blocco e uscita. Popen reale, pipe reali, nessun suono/account. Coprire processo attivo, coda/chunk successivi, close prima di pubblicazione, doppia close/figlio già uscito, timeout/errore e cleanup, runner custom e anti-eco. Spie su argv/cwd e processo estraneo separato per provare che non viene toccato. Nessuna promessa di misura della latenza su Windows10/i3/HDD o audio reale; nessuna esecuzione funzionale Linux.
