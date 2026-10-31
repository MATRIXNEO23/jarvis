# JARVIS — nuova interfaccia HUD animata

**Stato:** implementazione sperimentale nel ramo `feature/animated-hud-interface`, PR draft #6. Prototipo Tkinter senza nuove dipendenze, successivo alle funzioni di Vosk, conversazione GPT, Second Brain e correzioni della voce. Il mockup cinematografico era un riferimento estetico: l'interfaccia reale privilegia animazioni leggere, leggibilità e interazione affidabile su un HP Pavilion i3-2100 con 10 GB di RAM.

## Layout

- **Sinistra — Console**: cronologia scorrevole di parole riconosciute (solo richieste gestite, non tutto il rumore o le dettature libere), domande dell'utente, risposte di Jarvis, risultati verificati delle azioni, documenti e messaggi di errore. Ogni riga ha orario e colore distinto. Campo di input e pulsanti per comandi locali, GPT e pianificatore restano accessibili.
- **Centro — reattore JARVIS**: scritta **JARVIS** sempre al centro. Cerchi concentrici, segmenti rotanti e un bagliore con animazioni continue. **Durante la riproduzione della voce SAPI** il nucleo cambia *gradualmente e leggermente* dal blu al turchese, soprattutto nelle aree centrali. Al termine torna lentamente blu. Non interpreta il silenzio o un cooldown del microfono come parlato: usa `OfflineSpeaker.is_speaking()`.
- **Destra — globo terrestre**: griglia olografica ortografica con meridiani che si muovono e punti rappresentativi delle terre emerse che ruotano lentamente. È un effetto grafico, non una mappa georeferenziata o un GPS. Non legge la posizione dell'utente.
- **Parte superiore**: stati reali del microfono, collegamento GPT e Second Brain; ingranaggio per aprire le impostazioni; pulsante di chiusura.
- **Parte inferiore**: dati reali su utilizzo memoria e disco C, quando disponibili, e orario di Windows. Non vengono mostrati finti valori CPU, rete o GPS.

## Impostazioni e comandi importanti

Le numerose impostazioni esistenti **non sono più visibili nella dashboard**. Si aprono soltanto premendo l'icona **⚙**, che mostra un pannello separato con scrollbar. La finestra principale resta attiva anche quando le impostazioni sono aperte. Si può chiudere il pannello senza uscire da Jarvis.

**Le scelte per i file non sono impostazioni**: quando Jarvis chiede di salvare/annullare la chiusura di un documento, i relativi pulsanti e «Scegli file...» appaiono direttamente accanto alla console; scompaiono dopo la decisione.

Il vecchio codice di controllo di microfono, GPT, dettatura e file non è stato sostituito né aggirato dal disegno. La modalità microfono parte **sempre in standby/off** e può essere cambiata **soltanto manualmente** dall'utente. Lo stato del centro reagisce a questi eventi ma **non modifica mai il loro funzionamento**. Le interfacce verso il modello e il catalogo autorizzato restano gli stessi.

## Prestazioni e limitazioni

L'animazione è realizzata in Python standard con Canvas di Tkinter, senza immagini 4K, video, Chromium, WebGL, OpenGL, modelli aggiuntivi, servizi esterni o dipendenze pip. Tick grafico circa ogni 110 ms (9 fps). Le metriche del disco/RAM vengono aggiornate ogni ~7 secondi e le etichette non cambiano se il valore è invariato. Se la finestra è minimizzata, il disegno non viene ricalcolato. La finestra iniziale è 1200×670, con dimensioni minime 940×580, e il pannello impostazioni è scrollabile.

**Questo non è un rendering fotorealistico identico al concept generato**: la forma del globo e i cerchi sono vettoriali e molto più leggeri. L'utente ha chiesto specificamente che l'effetto sia animato, non che rimanga una immagine statica.

## Installazione e verifiche

Scaricare `https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/animated-hud-interface.zip` ed estrarre **in una nuova cartella**, conservando il vecchio Jarvis e `%LOCALAPPDATA%\\Jarvis`. Chiudere la precedente istanza e avviare `avvia_jarvis.bat`. Nessuna nuova installazione se i componenti esistenti già funzionano.

Verificare sul Pavilion: standby all'avvio; console visibile; pulsante ⚙ apre tutte le impostazioni; selezionare manualmente la modalità GPT e TTS; fare rispondere Jarvis e controllare che il centro cambi **solo** mentre parla; verificare che il globo ruoti lentamente; chiedere un comando e osservare richiesta/risposta/operazione; aprire un nuovo file e provare pulsanti salva/annulla; chiudere senza blocchi. Confrontare carico CPU/memoria con la vecchia interfaccia e usare dati di prova non importanti.

**La CI Python/Node Windows/Linux conferma sintassi e test unitari, non collauda la grafica interattiva sul Pavilion.** La versione precedente resta intatta; nessun merge prima di una decisione separata dopo il test reale.
