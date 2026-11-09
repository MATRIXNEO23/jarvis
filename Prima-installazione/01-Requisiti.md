# 1. Componenti necessari

> Aggiornato per Lumi build 023. Solo Python è obbligatorio; il resto si installa solo per le funzioni che usi. Ordine consigliato nella [guida iniziale](README.md).

Le versioni sono quelle dichiarate dagli script o provate dalla CI del riferimento esaminato. Non sono un ordine di aggiornare componenti già funzionanti.

| Funzione | Componenti | Cosa fare |
|---|---|---|
| Programma, chat, comandi locali, timer, memoria, progetti, avatar | Python 3.11 o 3.12 a 64 bit con Tkinter | **Obbligatorio.** Installatore Python per Windows con pip, Tcl/Tk e launcher `py` (sezione sotto) |
| Modello locale (risposte senza Internet) | Motore KoboldCpp **già incluso** nello ZIP; un file `.gguf` (Gemma 2 2B, Qwen2.5 o Qwen3) | Scarica il modello una volta, poi ingranaggio → GPT e memoria → Configura Gemma locale → Sfoglia → Salva → riavvia Lumi |
| Voce che risponde: Paola, Serena | Motore Piper **già incluso** (cartella `voce_engine`) | Ingranaggio → Voce → «Scarica Paola/Serena» → scegli la voce |
| Voce che risponde: voci Windows | Windows PowerShell e SAPI con una voce installata | Già in Windows; scegli la voce nelle impostazioni |
| Voce che risponde: voci Edge (Isabella, Elsa, Diego, Giuseppe) | Pacchetto edge-tts 7.2.x, **Internet** (il testo va al servizio Microsoft) | Facoltativo: `installa_voce_edge.bat`, poi riavvia Lumi |
| Riconoscimento dal microfono | Vosk 0.3.45, sounddevice 0.5.3, modello italiano piccolo, microfono | Facoltativo: `installa_voce.bat` |
| Telegram | Account Telegram, API ID/hash personali, Telethon >=1.36 e <2 | Facoltativo: `installa_telegram.bat`, poi configurazione da Lumi ([guida](04-Telegram.md)) |
| Note vocali Telegram | Quanto sopra e FFmpeg con libopus nel PATH | [Guida Telegram](04-Telegram.md) |
| Trascrizione dei vocali ricevuti | Vosk e modello, FFmpeg | Componenti microfono più Telegram |
| Collegamento al GPT esterno | Node.js 22.12+ e npm; SDK fissato dallo script; account ChatGPT | Facoltativo: Node.js, poi `installa_gpt.bat` ([guida](02-GPT.md)) |
| Add-on | Gestore incluso e file .jaddon compatibile | Gestisci add-on |

Non servono un modello GPT locale, CUDA, hosting o un account API a consumo. Non serve installare separatamente SQLite: il programma usa sqlite3 di Python. Le dipendenze transitive di Vosk/Telethon sono gestite da pip; quelle SDK da npm. Non installare tutti i pacchetti Python possibili.

## Installare o controllare Python
1. Se Python 3.11/3.12 funziona già per Lumi/Jarvis, mantienilo.
2. Altrimenti usa [Python per Windows](https://www.python.org/downloads/windows/), scegliendo una versione 3.11/3.12 x64 compatibile con il pacchetto. La CI documentata ha usato anche 3.12.10: [pagina ufficiale e installatore Windows 64 bit](https://www.python.org/downloads/release/python-31210/). È una versione di riferimento, non la più recente patch di sicurezza.
3. Nell'installazione includi pip, Tcl/Tk e il launcher py. Non scegliere ARM64 né il pacchetto embeddable per questa procedura.
4. Apri Prompt dei comandi e verifica:

    py -3 --version
    py -3 -m tkinter

Il secondo comando deve aprire una piccola finestra dimostrativa: puoi chiuderla.
Gli script attuali usano py -3. Se questo seleziona un Python diverso da 3.11/3.12, fermati: installazione dei moduli e avvio devono usare lo stesso interprete. Non installare pacchetti alla cieca in un altro Python.

## Modello locale GGUF
Lumi non scarica modelli da solo. File consigliati per il Pavilion (CPU senza AVX2, 10 GB RAM), versione «instruct», quantizzazione Q4_K_M:
- Gemma 2 2B instruct (circa 1,7 GB);
- Qwen2.5 1.5B o 3B instruct;
- Qwen3 1.7B.

Pagine di riferimento: [bartowski/gemma-2-2b-it-GGUF](https://huggingface.co/bartowski/gemma-2-2b-it-GGUF), [Qwen/Qwen2.5-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF), [bartowski/Qwen_Qwen3-1.7B-GGUF](https://huggingface.co/bartowski/Qwen_Qwen3-1.7B-GGUF) (sono quelli usati nelle prove CI). Salva il file in una cartella fissa e selezionalo da Lumi. Dopo ogni cambio di modello, contesto o thread chiudi e riapri Lumi.

## Node.js
Solo per GPT. Scarica l'installatore Windows x64 della linea 22.x dal [sito ufficiale Node.js](https://nodejs.org/en/download/archive/), includendo npm e PATH. L'installer di Lumi richiede almeno 22.12; la CI usa 22.12. Riavvia il terminale dopo l'installazione e verifica:

    node --version
    npm --version

La presenza dei comandi non prova ancora il login GPT.

## Riferimenti locali
installa_gpt.ps1, installa_voce.bat, installa_telegram.bat, voice_control.py, telegram_voice.py e i workflow della base b936879; questi script di installazione sono identici anche nel riferimento successivo 5e61e53. Le istruzioni non installano nulla automaticamente.
