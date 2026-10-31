# JARVIS HUD — versione più fedele al concept originale

**Ramo di sviluppo isolato:** `feature/hud-reference-redesign`, PR draft [#7](https://github.com/MATRIXNEO23/jarvis/pull/7). Basato sul ramo sperimentale animato precedente. Questa modifica nasce dal confronto tra la **foto dell'interfaccia realmente avviata** sul Pavilion e la **vecchia immagine di anteprima** inviata dall'utente il 31 ottobre 2026.

## Requisiti visivi confermati

L'immagine di riferimento mostra una console scura sulla sinistra con schede **CONSOLE / ATTIVITÀ / SISTEMA**, chat cronologica di comandi e risposte, un grande nucleo multilivello con testo **JARVIS**, un globo terrestre più complesso e quattro riquadri inferiori, tutto in un tema nero/blu ciano con cornici sottili ed elementi di illuminazione.

L'utente ha chiesto una modifica precisa allo **stato del nucleo**:

| Situazione reale | Colore nucleo | Animazione |
|---|---|---|
| Microfono chiuso e TTS inattivo | **Ciano** | Anelli in movimento lento, luce stabile |
| Stream di riconoscimento Vosk **davvero aperto** | **Arancione** | Pulsazione luminosa ripetuta, dal centro agli anelli |
| Voce offline SAPI **in riproduzione** | **Verde** | Pulsazione luminosa più rapida; ha precedenza sull'arancione |

Il centro deve **sempre** dire **JARVIS**. Non mettere «ASCOLTO» o «PARLO» dentro al cerchio: sono il colore e le pulsazioni a rappresentare l'attività. Lo stato viene riportato con parole anche fuori dal cerchio per accessibilità e in caso di monitor con colori alterati.

## Codice implementato

- `hud_reference.py`: nuovo renderer vettoriale del reattore con **7 fasce di archi segmentati**, una serie di anelli di contorno, reticolo e marcatori luminosi; luce centrale stratificata; globo terrestre con continenti stilizzati pieni, trama luminosa, punti urbani decorativi, meridiani, paralleli, orbite, motivo satellite e rotazione continua. Tutti gli elementi sono realizzati con **Tkinter Canvas standard**: nessuna dipendenza grafica esterna, API o GPU, nessun filmato statico spacciato per animazione.
- `animated_hud.py`: layout migliorato con console a tutta altezza e tre **schede funzionanti**. La console non perde i messaggi quando si cambia scheda: i filtri usano il meccanismo `elide` di Tk. Nella parte centrale e destra ci sono reattore e globo, sotto ci sono quattro riquadri con CPU, RAM, disco C e stato del collegamento GPT. I valori vengono letti dal sistema (CPU tramite GetSystemTimes su Windows, RAM e disco da Win32/std-lib); quando assenti si visualizza «--» senza numeri simulati. **GPT sostituisce la rete** nel quarto riquadro perché non è implementato un misuratore reale del traffico Internet.
- `voice_control.py`: `VoiceController.is_listening()` segnala soltanto il microfono realmente aperto per la generazione corrente. Se la modalità continua è selezionata ma Vosk non ha aperto il dispositivo, il nucleo non deve diventare arancione. La nuova funzione non abilita né disabilita il microfono.
- `jarvis.py`: cronologia visibile come timeline di chat con «TU», «JARVIS», «OPERAZIONE», «ERRORE» e orari; applicazione dei filtri a schede; il colore è collegato a `voice.is_listening()` e `speaker.is_speaking()`, non a un timer fittizio; la scelta della modalità microfono resta **manuale** e parte sempre in standby/off. Restano i comandi GPT, documenti, dettatura, Second Brain, pannello impostazioni ⚙ e pulsanti salva/annulla quando necessari.

### Prestazioni

Il loop Tk è circa ogni **110 ms**. Solo una parte degli archi luminosi viene animata, mentre i contorni statici restano disegnati. Terra e decorazioni geografiche sono aggiornate circa ogni **tre tick**; la rotazione terrestre è lenta (diversi minuti per un giro). CPU, RAM e disco vengono campionati ogni **5 secondi** anziché ad ogni frame. Non vengono mantenuti modelli grafici o pacchetti in RAM, né viene modificato l'audio per cambiare colori.

La preview originale è un'immagine cinematografica di altissima definizione; **Tkinter vettoriale non la riproduce pixel per pixel**. Questo ramo cerca di avvicinarne maggiormente composizione, colore, dettaglio e movimento restando compatibile con l'i3-2100/10GB.

### Cosa verificare sul Pavilion

1. Estrarre la ZIP di questo ramo in una **nuova cartella**, senza sovrascrivere quella funzionante o cancellare `%LOCALAPPDATA%\\Jarvis`, quindi eseguire `avvia_jarvis.bat`.
2. Verificare **ciano** appena aperto, quando microfono e sintesi vocale sono inattivi.
3. Aprire ⚙ e attivare manualmente la modalità di ascolto: quando Vosk apre il microfono, il nucleo deve diventare **arancione lampeggiante**. Se il microfono non si avvia davvero, non deve mostrare erroneamente arancione.
4. Attivare le risposte vocali e far parlare Jarvis: il nucleo deve lampeggiare **verde**, anche se il microfono resta attivo; a fine risposta torna arancione se il microfono è ancora aperto, altrimenti ciano.
5. Controllare la lenta rotazione della Terra e il disegno dei continenti. Usare CONSOLE / ATTIVITÀ / SISTEMA e verificare che nessuna riga venga cancellata cambiando scheda.
6. Controllare la console e l'esecuzione dei comandi locali/GPT; verificare il salvataggio sicuro dei documenti e tutte le impostazioni dietro ⚙.
7. Verificare la fluidità e il consumo CPU, anche con altri programmi aperti. Se diventa pesante, ridurre ulteriormente l'aggiornamento dei dettagli senza sacrificare l'ascolto scelto manualmente.

**Non integrare automaticamente:** i test CI controllano logica, sintassi e parte del rendering Tk su runner Windows; non sostituiscono l'ispezione visiva sul Pavilion e la separata decisione di adottare il nuovo stile.
