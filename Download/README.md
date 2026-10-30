# Download di Jarvis per Windows 10

## [SCARICA JARVIS — ZIP COMPLETO AGGIORNATO](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/main.zip)

Il collegamento qui sopra scarica **tutti i file attuali del ramo principale** della repository, direttamente da GitHub. Non occorre aprire **Actions**, cercare un **artifact**, avere un account GitHub o scaricare i file uno alla volta.

> **Versione alpha per prove.** Il collegamento ChatGPT tramite account non è ancora stato collaudato sul Pavilion; la voce non è ancora implementata. Non è un programma Windows autonomo pronto da installare con un unico setup.

### Sul PC

1. Termina l'installazione di **Node.js 22.12 o successivo** e assicurati che **Python 3.12** sia disponibile.
2. Premi il link **SCARICA JARVIS** qui sopra. Il browser salva uno ZIP, in genere nella cartella **Download** di Windows.
3. Fai clic destro sullo ZIP scaricato e scegli **Estrai tutto**. Apri la cartella estratta `jarvis-main`.
4. **Prima installazione GPT:** fai doppio clic su `installa_gpt.bat` (occorre Internet). Lo script scarica e compila il DevKit locale OpenAI, senza API a consumo.
5. Avvia Jarvis con `avvia_jarvis.bat` dalla **stessa** cartella estratta.
6. Nella finestra Jarvis usa i comandi locali oppure **Connetti ChatGPT**, che apre il browser ufficiale per effettuare l'accesso con il tuo consenso.

### Cosa serve scaricare separatamente

- [Python per Windows](https://www.python.org/downloads/windows/) — già presente sul Pavilion secondo la verifica effettuata con Python 3.12.
- [Node.js, sito ufficiale](https://nodejs.org/) — serve a GPT; lascia installati npm e Add to PATH. Gli strumenti di compilazione facoltativi non sono richiesti.
- Il kit **Sign in with ChatGPT** viene scaricato dal file `installa_gpt.bat`: **non va cercato negli artifact**.
- Moduli vocali Vosk/TTS: **non installarli ancora**; la funzione voce non è pronta.

**Aggiornamenti:** torna su questo stesso link per scaricare il ZIP aggiornato. Estrai le nuove versioni in una cartella separata; non cancellare i dati salvati in `%LOCALAPPDATA%\Jarvis`.

[Documentazione dettagliata GPT](../docs/GPT_SETUP.md) · [Pagina principale del progetto](../README.md)
