# Jarvis HUD — allineamento alla seconda immagine di riferimento

**Ramo sperimentale:** `feature/hud-reference-ui-20261031` (PR #31).
**Nessun merge sulla versione stabile.** Questo documento descrive modifiche grafiche, non nuove funzionalità applicative.

## Interventi

1. **Aspetto:** fondo quasi nero, cornici blu/ciano sottili, reattore e globo nello stile della seconda immagine. L'intensità del glow statico del reattore è stata ridotta per migliorare il contrasto di testo e contorni.
2. **Autodiagnosi:** il vecchio `ttk.Progressbar` bianco e il pulsante `Annulla` sempre visibile sono stati sostituiti da una striscia molto discreta con barra ciano su sfondo scuro e un piccolo comando `×`. La striscia compare **solo durante una diagnosi in esecuzione**; al termine scompare. Avvio, annullamento, timeout, progressi e risultati restano quelli esistenti.
3. **CPU/RAM/DISCO C/RETE:** le quattro schede in basso hanno identica larghezza mediante `grid_columnconfigure(..., uniform='telemetry')`, con pesi e padding uguali. I valori rimangono misure Windows reali, senza inventare percentuali o rete.
4. **Colori di stato:** blu/ciano permanente su anelli esterni, globo, cornici, barre e console. Soltanto il nucleo interno reagisce alla voce: arancione quando rileva parlato dell'utente, verde mentre Jarvis sta parlando, ciano in attesa. I cerchi esterni continuano a ruotare senza cambiare colore. Il raster decorativo rimane ciano e non richiede più tre texture per tre stati.
5. **Launcher:** solo `avvia_jarvis.bat`, il launcher unico più recente. Mantiene il profilo di prova isolato, i collegamenti GPT/Telegram esistenti e il modello Vosk locale in sola lettura. Non ricrea `AVVIA_TEST_TELEGRAM50.bat`.

## Compatibilità e collaudo

- Non sono stati modificati i contratti dei componenti GPT, voce, Telegram, documenti, progetti, add-on o memoria.
- L'analisi locale mantiene un comando di annullamento realmente collegato al `DiagnosticSession` e una progressione misurata, non fittizia.
- Il rendering resta Canvas Tk + standard library; niente browser, immagini di rete, API o nuovi costi.
- Test unitari regressivi per il nucleo/texture, proporzioni metriche, avvio singolo e diagnostic UI; test Windows/Linux GitHub Actions.
- Il confronto finale visivo e il microfono reale necessitano di un collaudo sul Pavilion Windows 10; non vengono dichiarati PASS senza tale prova.

## Avvio senza sovrascrivere

Chiudi il Jarvis già aperto, estrai la nuova ZIP in una cartella **nuova** e avvia `avvia_jarvis.bat`. Non usare due istanze collegate a Telegram contemporaneamente. Il profilo dati del test rimane sotto `%LOCALAPPDATA%\\Jarvis-Telegram50-Trial`; il programma attuale non viene sovrascritto.
