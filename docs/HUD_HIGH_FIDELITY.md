# JARVIS HUD — revisione high fidelity basata sul concept originale

**Ramo sperimentale:** `feature/high-fidelity-reference-hud`, [PR #10 draft](https://github.com/MATRIXNEO23/jarvis/pull/10), derivato dalla build con ascolto automatico, saluto vocale, dialogo continuo, Second Brain e correzioni Vosk. **La versione che hai già sul Pavilion rimane disponibile e non viene sovrascritta.**

## Obiettivo approvato

L'utente ha richiesto una somiglianza **molto più stretta** con il concept illustrato nella conversazione: non basta aggiungere forme circolari blu; servono un **reattore stratificato e luminoso**, un globo **molto più ricco di sfumature**, una console in stile chat con cornici al neon e quattro strumenti in basso. È accettato un **modesto aumento di peso grafico** rispetto al vecchio HUD, purché l'assistente rimanga utilizzabile sul Pavilion i3-2100 con 10 GB RAM, con priorità assoluta all'ascolto e alle funzioni.

## Implementazione

**Motore grafico ibrido, senza librerie aggiuntive.** Il nuovo `hud_raster.py` prepara in un **thread separato**, soltanto quando servono, immagini PNG compresse usando esclusivamente `math`, `zlib`, `struct` e `tkinter` della libreria standard. Il programma crea i `PhotoImage` soltanto sul thread Tk, e poi cambia i frame già pronti: non ricrea la Terra a ogni fotogramma.

Il reattore è composto da sette famiglie di archi concentrici più una serie di bagliori soffusi rasterizzati, per dare maggior profondità agli anelli. Ci sono tre versioni della luce: **ciano** mentre non parla nessuno, **arancione pulsante** quando viene rilevata la voce al microfono, **verde pulsante** mentre parla JARVIS. Il nome **JARVIS** rimane fisso al centro. L'illuminazione reagisce agli stessi stati audio reali precedentemente implementati, senza fingere che il microfono aperto equivalga a una voce rilevata.

La Terra usa ora una **superficie sferica rasterizzata**, con illuminazione atmosferica, continenti stilizzati ricavati dalle coste già presenti, sfumature dei terreni, luci urbane decorative e piccole rotazioni fra più pose, sotto gli archi orbitali e la griglia vettoriale già animati. **Non è una fotografia NASA**, non è una mappa di posizione dell'utente, né una fonte di dati geografici accurati. È un'immagine tecnica realizzata per assomigliare maggiormente al globo notturno del concept.

Il programma non scarica immagini o altri contenuti quando si avvia e non richiede Pillow, OpenGL, Chromium, GPU moderne o API a pagamento. **Se la preparazione delle immagini fallisce, continua a mostrare l'HUD vettoriale precedente** e non interrompe comandi, file o conversazione. Le texture sono generate in dimensioni quantizzate, per evitare decine di elaborazioni durante il ridimensionamento delle finestre.

### Console, cornici e pannelli

La console a sinistra mantiene le tre schede funzionanti **CONSOLE / ATTIVITÀ / SISTEMA**, i messaggi cronologici reali di TU/JARVIS/OPERAZIONE, gli orari e i colori per errori/conferme. È stata rivista con font Segoe UI, barra scura e un unico campo in basso, con **pulsante microfono reale** (commuta manualmente standby / Conversazione continua GPT) e freccia di invio. I comandi espliciti precedenti, compreso il pianificatore, sono ancora accessibili con **⋯**; nessun comando è stato eliminato.

Le cornici e gli strumenti inferiori hanno accenti ciano più luminosi e dettagli angolari. I quattro riquadri diventano **CPU, RAM, DISCO C, RETE**, più simili all'immagine. Nessun numero di esempio viene copiato dal concept:

- CPU e RAM arrivano da Windows;
- il disco C viene letto dal sistema;
- la rete è campionata **solo se disponibile** tramite la lettura locale di `netstat.exe -e` con argomenti fissi e senza shell, in un thread di sfondo; il traffico è mostrato in B/s o KB/s/MB/s reali;
- se il dato è assente compare **--**. Lo stato GPT rimane leggibile nell'intestazione e nel quadro di sistema.

## Costi, sicurezza e priorità

- Nessun costo aggiuntivo; nessun modello extra.
- L'illuminazione grafica non modifica mai microfono, modalità, GPT, salvataggi o autorizzazioni ai file.
- Il microfono segue la nuova regola scelta dall'utente: si attiva **quando apre JARVIS** in Conversazione continua GPT, a meno che abbia disattivato l'avvio dell'ascolto da ⚙. **Non** si aggiunge un avvio automatico di Windows.
- La generazione raster usa un thread separato e può comportare un piccolo picco iniziale CPU: va misurato sul Pavilion. Il resto delle animazioni usa immagini precalcolate e aggiornamenti moderati.
- Rimangono le scelte vocale: silenzio ciano, utente arancione, risposta verde, e il saluto iniziale legato all'ora locale.
- La versione usa il codice del ramo `feature/hud-speech-activity-auto-start` come base; la storia GPT e Second Brain restano separate dalle decorazioni.

## Prova sul Pavilion

1. Scarica la ZIP `https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/high-fidelity-reference-hud.zip`, estraila in **una cartella nuova** e avvia `avvia_jarvis.bat`. Non cancellare i vecchi Jarvis, il modello Vosk né `%LOCALAPPDATA%\\Jarvis`.
2. La grafica iniziale può mostrare per qualche istante gli anelli e il globo vettoriali; quando i PNG sono pronti devono comparire il bagliore più intenso e la superficie terrestre più dettagliata. Devono continuare a muoversi gli archi e la Terra.
3. Con microfono acceso ma in silenzio, controlla il nucleo ciano. Parla (arancione pulsante); lascia rispondere JARVIS (verde pulsante).
4. Prova le tre schede console, il nuovo campo di invio, il pulsante microfono, i comandi sotto ⋯, l'ingranaggio ⚙ e la conferma per i file.
5. Controlla che CPU/RAM/disco mostrino valori reali, e che il riquadro RETE mostri una velocità reale oppure -- quando non misurabile.
6. Confronta affiancando una foto della nuova finestra con il concept originario, specialmente **reattore, globo, spaziatura e pannelli**; verifica il carico CPU anche con altri programmi aperti.

La CI Windows/Linux verifica l'encoder PNG, la creazione delle texture, il caricamento in Tk, i limiti dimensionali, la logica del colore e il resto dei comandi. **Non è una prova fotografica di somiglianza:** la decisione se il risultato sia abbastanza vicino al concept dipende dalla verifica visiva sul Pavilion.

**Non fare merge automatico in main**: la nuova grafica resta sperimentale fino al confronto dell'utente e ad approvazione separata.
