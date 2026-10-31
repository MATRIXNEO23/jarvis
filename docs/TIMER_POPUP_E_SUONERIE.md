# Jarvis — Timer vocale con popup indipendente (31 ottobre 2026)

Ramo sperimentale: `feature/timer-popup-settings-20261031` (PR #33).
Questa build conserva tutte le funzionalità presenti nella precedente ZIP HUD.
**Nessun merge del codice su `main`.**

## Timer
- **Comandi vocali e scritti:** «timer», «timer dieci minuti», «Jarvis, metti un timer di cinque minuti», «imposta timer per un'ora e trenta minuti», «pausa timer», «riprendi timer», «stop timer», «resetta timer».
- Dire soltanto «timer» apre il piccolo popup senza avviare arbitrariamente il conto alla rovescia. Dire «timer dieci minuti» lo apre e avvia subito.
- Riconoscimento in modalità conversazione GPT senza wake word, e in ascolto continuo con le normali regole `Ehi Jarvis`. Il timer viene eseguito **localmente**, senza passare da GPT, senza API aggiuntive o costi.
- Il popup **non è incorporato nell'HUD principale**: finestra Tk indipendente, sfondo scuro blu/ciano, cifre digitali, Start, Pausa, Stop, Reset e campi manuali H/M/S. Una sola finestra/timer alla volta. Durata da 1 secondo a 23:59:59.
- Countdown basato su `time.monotonic()`, non sull'ora di sistema, con segnale di scadenza generato una sola volta.

## Impostazioni esistenti
Non viene creata una seconda finestra Impostazioni. L'ingranaggio continua ad aprire **quella già presente**, con i controlli preesistenti intatti. Sono state aggiunte intestazioni e una navigazione a otto destinazioni: Voce, Suonerie timer, Documenti, GPT, Memoria, Progetti, Telegram, Add-on. Il pulsante porta alla sezione nella pagina scorrevole senza cancellare o riposizionare la funzionalità.

In «Timer — suonerie e avvisi»: 4 suoni sintetizzati localmente tramite `winsound` su Windows, test in anteprima («Prova suono»), arresto («Ferma prova»), volume 0–100 e ripetizione facoltativa fino a Stop. Il volume è applicato al campione PCM generato dalla libreria standard, non al volume globale del sistema. Le preferenze rimangono nel file `settings.json`, con validazione e retrocompatibilità.

## Sicurezza / regressioni
- La finestra timer non gestisce file, shell, Telegram, GPT né il microfono.
- Tutti i vecchi comandi, bottoni e pannelli restano operativi; il launcher unico rimane `avvia_jarvis.bat`.
- L'audio di allarme non parte all'avvio di Jarvis, soltanto a scadenza o con la prova manuale.
- Chiudere il popup ferma il timer e l'allarme. Chiudere Jarvis ferma anche il popup.
- I suoni sono sintetici, non dipendono da WAV esterni.
- Richiesto collaudo manuale sul Pavilion Windows 10 per il reale output audio e per l'aspetto Tk; test Python/Node Windows e Ubuntu non equivalgono a test hardware.

## Collaudo
1. Chiudi la versione attuale di Jarvis; estrai la ZIP di test in una **nuova cartella**.
2. Usa soltanto `avvia_jarvis.bat`. Il profilo di prova resta isolato.
3. Pronuncia «timer dieci secondi», controlla finestra e scadenza.
4. Apri l'ingranaggio, scegli una suoneria e premi «Prova suono». Verifica volume e ripetizione.
5. Verifica che tutte le altre sezioni (GPT, Memoria, Progetti, Telegram, Add-on, documenti e voce) siano ancora presenti e utilizzabili.
