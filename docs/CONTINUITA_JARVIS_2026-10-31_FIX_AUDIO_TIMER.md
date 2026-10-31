# Continuità Jarvis — 31 ottobre 2026 — fix audio timer

## Stato alla chiusura conversazione
- L'utente ha segnalato che le voci delle suonerie erano visibili nelle Impostazioni, ma premendo **Prova** non si sentiva nulla e nemmeno alla scadenza del timer partiva il suono.
- Il timer precedente generava WAV PCM in memoria tramite `winsound.PlaySound`, senza un feedback UI affidabile sugli errori del backend audio; i vecchi test verificavano i dati WAV, non l'uscita audio reale.
- È stata preparata una correzione sul ramo `feature/timer-settings-ui-20261031`, collegato alla [PR #32](https://github.com/MATRIXNEO23/jarvis/pull/32). Modifiche rilevanti: `jarvis_timer.py`, `jarvis.py`, `settings.py`, test `test_jarvis_timer.py` e `test_settings.py`.
- Fix: prova riproduzione WAV da file temporaneo, fallback WAV in memoria, beep alternativo Windows, ulteriore segnale di sistema e messaggi di stato per **Prova** e scadenza; modalità **Bip alternativo** selezionabile nelle Impostazioni. I messaggi riportano l'esito della chiamata audio a Windows, **non** dimostrano che il suono sia udibile sugli altoparlanti.
- ZIP completo **pubblicato in cima** a `Download/README.md` sul ramo `main`, mantenendo le build vecchie:
  [Jarvis-Timer-Audio-Corretto-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/refs/heads/main/Download/Jarvis-Timer-Audio-Corretto-20261031.zip).
- Ultimo controllo CI durante la conversazione: test Linux superati, alcuni job Windows ancora in corso; non dare per conclusi tutti i job senza ricontrollare.
- **Prova sul PC reale ancora non eseguita** al termine della conversazione. L'utente ha detto: «Allora adesso la installo e provo». Non presumere installazione riuscita o audio funzionante.

## Ripresa esatta
Attendere che l'utente riferisca l'esito della prova, senza interromperlo né ripetere istruzioni già date. Ha chiesto espressamente silenzio mentre installa.
Se riferisce risultati, distinguere:
1. Cosa si sente premendo **Prova** nella versione corretta.
2. Cosa si sente premendo **Bip alternativo**.
3. Se, dopo 5 secondi di timer, suona l'allarme alla scadenza.
4. Se compare un errore/messaggio nella pagina Impostazioni o nel popup.
In caso di silenzio completo, considerare uscita audio/volume del mixer di Windows e raccogliere il testo esatto degli eventuali errori, senza affermare che la correzione sia riuscita.

## Vincoli di progetto da preservare
- Le **nuove funzionalità** di Jarvis vanno progettate come **add-on modulari `.jaddon`** dove fattibile; eventuale migrazione delle funzioni esistenti va valutata caso per caso, non automatica. Il fix audio sopra è una correzione della funzione esistente, non una migrazione ad add-on.
- Conservare la compatibilità con Windows 10 64 bit e il PC HP Pavilion i3-2100 / 10 GB RAM; niente nuove API a pagamento e avvio leggero.
- Microfono: modalità selezionata manualmente, mai cambiare automaticamente; all'avvio PC standby e microfono spento, come richiesta progettuale.
- Non sovrascrivere installazione precedente, impostazioni, progetti, Telegram o file personali per i test. Preferire estrazione in cartella nuova; preservare versioni precedenti.
- L'utente preferisce comunicazione essenziale e, quando sta eseguendo prove, **nessuna interruzione vocale**.

## Repository
- Repository: https://github.com/MATRIXNEO23/jarvis
- Ramo del fix: `feature/timer-settings-ui-20261031`
- PR: https://github.com/MATRIXNEO23/jarvis/pull/32
- Commit del packaging del fix: `a9d3d54e448bd0f830b216b740233cda7a6ab66f`.

Questo è un checkpoint della conversazione, non un collaudo dell'audio.
