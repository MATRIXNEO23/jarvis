# Scarica Jarvis per Windows 10 — HP Pavilion

**[NUOVA PROVA — JARVIS CON BROWSER, DETTATURA, «EHI JARVIS» E RISPOSTE A VOCE](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/voice-browser-dictation.zip)**

**AGGIORNAMENTO DETTATURA (30/10/2026):** il primo test reale sul Pavilion ha mostrato che Jarvis riconosceva le parole ma Windows rifiutava l'inserimento. La correzione modifica la struttura `SendInput` per Windows 64 bit e aggiunge test specifici: [CI Windows/Linux superata](https://github.com/MATRIXNEO23/jarvis/actions/runs/41129730526). **Da confermare nuovamente sul Pavilion.**

**Per avviare e fermare la dettatura completamente a voce:** seleziona **Ascolto continuo**, clicca nel campo di testo di Blocco note, quindi pronuncia **«Ehi Jarvis, attiva dettatura»**. Per interrompere di' **«Ehi Jarvis, disattiva dettatura»**. Una volta attiva, il parlato comune diventa testo senza ripetere «Jarvis». La modalità del microfono non cambia da sola.

**Per riprovare la correzione:** scarica di nuovo lo ZIP del **primo link**, estrailo in una **cartella nuova**, chiudi il Jarvis precedente e apri il nuovo `avvia_jarvis.bat`. **Non reinstallare Vosk** se già funziona. Non cancellare o sostituire le cartelle precedenti né `%LOCALAPPDATA%\\Jarvis`.

Il ramo di prova consente di aprire/cercare nel browser, dettare in un campo esterno, chiamare Jarvis con «Ehi Jarvis» durante l'ascolto continuo e **scegliere una voce Windows per le risposte parlate offline**. [Test automatici Windows/Linux superati](https://github.com/MATRIXNEO23/jarvis/actions/runs/41126671637); **collaudo reale sul Pavilion ancora necessario**. Non sostituisce per ora la versione vocale precedente. [Istruzioni risposte vocali](https://github.com/MATRIXNEO23/jarvis/blob/feature/voice-browser-dictation/docs/VOCE_RISPOSTE.md) · [Dettatura e browser](https://github.com/MATRIXNEO23/jarvis/blob/feature/voice-browser-dictation/docs/DETTATURA_BROWSER.md).

## SCARICA JARVIS — ZIP COMPLETO AGGIORNATO CON VOCE OFFLINE (VERSIONE DI PROVA)

**[PREMI QUI PER SCARICARE JARVIS CON LA VOCE](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/offline-voice-pavilion.zip)**

Questo link scarica lo ZIP del branch `feature/offline-voice-pavilion` con il comando vocale offline italiano e i file di installazione. **Non scaricare lo ZIP `main` se vuoi provare la voce.**

Il microfono **rimane spento a ogni avvio**. Puoi scegliere manualmente Standby, Premi per parlare e Ascolto continuo. Nessun passaggio automatico a standby per Minecraft o altri programmi.

### Installazione della versione con voce sul Pavilion

1. **Chiudi Jarvis** se e' aperto. Scarica lo ZIP dal pulsante qui sopra.
2. In Download di Windows, clic destro sullo ZIP e scegli **Estrai tutto** in **una cartella nuova**. Non cancellare o sovrascrivere la precedente cartella Jarvis.
3. Apri la cartella estratta `jarvis-feature-offline-voice-pavilion` (il nome puo' variare).
4. Fai doppio clic su **`installa_voce.bat`**: installa i moduli Vosk e SoundDevice e scarica il piccolo modello italiano ufficiale. Serve Internet soltanto per questa installazione; segui il testo nella finestra fino al completamento.
5. Fai doppio clic su **`avvia_jarvis.bat`**. Il microfono parte **spento**. Per la prima prova seleziona **Premi per parlare**, tieni premuto il pulsante e pronuncia «Jarvis, apri la calcolatrice».

Non devi reinstallare il collegamento GPT gia' installato nella cartella dei dati utente. Se l'installazione voce fallisce, il normale input testuale di Jarvis rimane utilizzabile. **Non cancellare i dati in `%LOCALAPPDATA%\Jarvis`.**

**Stato di verifica:** i test automatici Python/Node per Windows e Linux sono superati ([CI](https://github.com/MATRIXNEO23/jarvis/actions/runs/41099757267)). Il microfono fisico e le prestazioni sul tuo Pavilion non sono ancora collaudati; questa non e' una versione definitiva.

[Guida completa alla voce offline](https://github.com/MATRIXNEO23/jarvis/blob/feature/offline-voice-pavilion/docs/VOCE_OFFLINE.md) · [Codice e avanzamento della voce](https://github.com/MATRIXNEO23/jarvis/pull/1)

## Versione precedente senza voce

**[SCARICA JARVIS — ZIP PRINCIPALE (MAIN, SENZA VOCE)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/main.zip)**

Questa e' la versione gia' utilizzata per il pianificatore e i comandi testuali sul Pavilion. Mantienila finche' la prova del microfono non e' completata.

[Pagina principale del progetto](../README.md)
