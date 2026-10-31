# JARVIS — sfondo cinematico più fedele alla reference

**Ramo di prova isolato:** `feature/high-fidelity-cinematic-background`, PR draft [#11](https://github.com/MATRIXNEO23/jarvis/pull/11). Deriva dal ramo `feature/high-fidelity-reference-hud`: tutte le funzionalità vocali, GPT, Second Brain, documenti e il reattore animato restano quelle già presenti.

## Feedback ricevuto sul Pavilion

Dopo aver avviato realmente la build high fidelity e aver mostrato una nuova fotografia, l'utente ha chiesto che **anche lo sfondo** fosse più simile all'immagine di anteprima approvata.

La fotografia mostra una griglia blu uniforme dietro al reattore e alla Terra. Nel preview originale, invece, **il fondo è quasi nero**, il blu è prevalentemente concentrato negli anelli e nel globo, e attorno si vedono circuiti e microelementi tecnici molto sottili e luminosi.

## Correzione implementata

- `hud_backdrop.py`: nuovo disegno Tkinter statico con 24 sottili bande molto scure (componenti RGB sempre inferiori a 18), circuiti angolari e asimmetrici, nodi ciano, scale tecniche e punti decorativi sparsi. Niente griglia quadrata regolare su tutta la schermata.
- `hud_reference.py`: reattore e globo chiamano il disegno dello sfondo appena ricostruiscono il Canvas. Immagini raster e animazioni esistenti restano sopra lo sfondo.
- `animated_hud.py`: tonalità scure della console e dei riquadri inferiori, più vicine al contrasto nero/ciano del concept.
- `jarvis.py`: il fondo della cronologia chat è stato scurito in modo coerente. I controlli non sono stati cambiati.
- `tests/test_hud_backdrop.py`: controlla il contrasto quasi nero, il numero limitato di tracciati (assenza di griglia fitta), il disegno deterministico, le dimensioni e gli input non validi.

### Prestazioni e priorità

Tutto il disegno del nuovo sfondo viene fatto **solo quando un Canvas viene inizializzato o ridimensionato**, non durante il tick di animazione da 110 ms. Nessun nuovo thread, servizio, libreria, download o costo; il renderer SVG, i modelli e le API non sono necessari.

**Colori del nucleo invariati:** ciano in silenzio anche col microfono attivo, arancione pulsante sulla voce dell'utente, verde pulsante sulla sintesi vocale di JARVIS. Rimangono testo JARVIS centrale, Terra animata, avvio conversazione continua GPT all'apertura dell'app con opt-out, saluto locale, personalità, Second Brain e approvazioni per i documenti.

## Test da fare sul Pavilion

Scaricare la ZIP `https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/high-fidelity-cinematic-background.zip` in **una cartella nuova**, chiudere la precedente istanza e lanciare `avvia_jarvis.bat`. Non eliminare la versione che funziona, la cartella del modello Vosk o `%LOCALAPPDATA%\\Jarvis`.

1. Confrontare il nuovo fondo con il concept: deve sembrare più nero, con circuiti e punti ciano leggeri e NON con la precedente griglia blu uniformemente ripetuta.
2. Verificare che il nucleo e il globo continuino a muoversi e siano chiaramente distinguibili dal fondo.
3. Verificare i colori del nucleo durante silenzio, parlato dell'utente e risposta.
4. Aprire ⚙, usare Console/Attività/Sistema, controllare la chat e le scelte sicure di salvataggio.
5. Provare anche Minecraft/altri programmi aperti e verificare che il microfono rimanga attivo e l'animazione sufficientemente fluida.

**La CI verifica il codice, non la fedeltà visiva sul monitor.** La nuova versione resta una prova isolata finché non viene confrontata con una foto reale sul Pavilion e approvata dall'utente.
