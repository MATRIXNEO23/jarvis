# 1. Componenti necessari
Le versioni sono quelle dichiarate dagli script o provate dalla CI del riferimento esaminato. Non sono un ordine di aggiornare componenti già funzionanti.

| Funzione | Componenti | Installazione |
|---|---|---|
| Finestra, comandi locali, timer, memoria, progetti, diagnostica statica | Python 3.11 o 3.12 a 64 bit con Tkinter e libreria standard | Installatore Python per Windows con pip, Tcl/Tk e launcher py |
| Collegamento al GPT esterno | Node.js e npm; SDK locale fissato dallo script; account ChatGPT autorizzato | Node 22.12 minimo; linea 22.x compatibile con il riferimento CI; poi installa_gpt.bat |
| Riconoscimento dal microfono | Vosk 0.3.45, sounddevice 0.5.3, modello italiano piccolo, microfono funzionante | installa_voce.bat |
| Risposte a voce sul PC | Windows PowerShell, System.Speech/SAPI e una voce Windows installata | Normalmente già in Windows; selezione nelle impostazioni |
| Telegram | Account Telegram, API ID/hash personali, Telethon >=1.36 e <2 | installa_telegram.bat e configurazione account |
| Note vocali Telegram | Quanto sopra, SAPI e FFmpeg con encoder libopus nel PATH | Procedura Telegram |
| Trascrizione dei vocali ricevuti | Vosk e relativo modello, FFmpeg | Componenti voce più Telegram |
| Add-on descrittive attuali | Gestore incluso e file .jaddon compatibile | Gestisci add-on |
| Nuova navigazione web autonoma | In progettazione | Non installare ancora Playwright o estensioni per questa proposta |

Non servono un modello GPT locale, CUDA, hosting o un account API a consumo. Non serve installare separatamente SQLite: il programma usa sqlite3 di Python. Le dipendenze transitive di Vosk/Telethon sono gestite da pip; quelle SDK da npm. Non installare tutti i pacchetti Python possibili.

## Installare o controllare Python
1. Se Python 3.11/3.12 funziona già per Jarvis, mantienilo.
2. Altrimenti usa [Python per Windows](https://www.python.org/downloads/windows/), scegliendo una versione 3.11/3.12 x64 compatibile con il pacchetto. La CI documentata ha usato anche 3.12.10: [pagina ufficiale e installatore Windows 64 bit](https://www.python.org/downloads/release/python-31210/). È una versione di riferimento, non la più recente patch di sicurezza.
3. Nell'installazione includi pip, Tcl/Tk e il launcher py. Non scegliere ARM64 né il pacchetto embeddable per questa procedura.
4. Apri Prompt dei comandi e verifica:

    py -3 --version
    py -3 -m tkinter

Il secondo comando deve aprire una piccola finestra dimostrativa: puoi chiuderla.
Gli script attuali usano py -3. Se questo seleziona un Python diverso da 3.11/3.12, fermati: installazione dei moduli e avvio devono usare lo stesso interprete. Non installare pacchetti alla cieca in un altro Python.

## Node.js
Solo per GPT. Scarica l'installatore Windows x64 della linea 22.x dal [sito ufficiale Node.js](https://nodejs.org/en/download/archive/), includendo npm e PATH. L'installer Jarvis richiede almeno 22.12; la CI usa 22.12. Riavvia il terminale dopo l'installazione e verifica:

    node --version
    npm --version

La presenza dei comandi non prova ancora il login GPT.

## Riferimenti locali
installa_gpt.ps1, installa_voce.bat, installa_telegram.bat, voice_control.py, telegram_voice.py e i workflow del riferimento 5e61e53. Le istruzioni non installano nulla automaticamente.
