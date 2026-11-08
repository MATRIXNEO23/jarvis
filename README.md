**Nuova candidata Windows: [Jarvis 011](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-011.zip)** — verificata su Windows, collaudo PC pendente.

**Nuova candidata Windows: [Jarvis 010](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-010.zip)** — verificata su Windows, collaudo PC pendente.

**Nuova candidata Windows: [Jarvis 009](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-009.zip)** — verificata su Windows, collaudo PC pendente.

**Nuova candidata Windows: [Jarvis 008](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-008.zip)** — verificata su Windows, collaudo PC pendente.

> **Ultima candidata: [Jarvis007](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-007.zip)** — timer scritto, aiuto locale e tasti rapidi. [Consegna](docs/CONSEGNA-JARVIS-007-20261107.md), [handoff](docs/HANDOFF-JARVIS-007-20261107.md). Collaudo PC pendente; vecchie versioni conservate.

> **Nuova candidata Windows: [Jarvis 006](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-006.zip)** — correzioni audit con Gemma; [prove e istruzioni](docs/CONSEGNA-JARVIS-006-20261107.md). Collaudo sul PC ancora da fare. Versioni precedenti conservate.

> **Versioni e sorgenti:** consulta il [registro autorevole](Download/REGISTRO-VERSIONI.md). La radice di main contiene sorgenti storici e il catalogo dei pacchetti; non coincide con il runtime Gemma distribuito. Il registro distingue pacchetti pubblicati, sorgenti esatti e correzioni ancora in bozza. Le sezioni sottostanti sono cronologia, non un'indicazione univoca dell'ultima versione.

> **Installazione e configurazione aggiornate:** parti da [Prima-installazione/README.md](Prima-installazione/README.md). Per riprendere lo sviluppo leggi [RECUPERO.md](RECUPERO.md) e [l’indice dei sorgenti](docs/INDICE-SORGENTI.md). Le sezioni sottostanti contengono anche aggiornamenti storici: non identificano tutte la versione attuale. 

**Serie numerata storica: [Jarvis 005](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-005.zip)** — richiamo Jarvis obbligatorio e prompt senza memoria vuota; collaudo PC pendente. [Versioni precedenti](Download/REGISTRO-VERSIONI.md).


# Jarvis — Windows 10 (64 bit)

**Continuità del progetto:** [stato, branch e punto di ripresa (30/10/2026)](docs/CONTINUITA_JARVIS.md). Il problema del test di ricerca web è stato corretto. I test automatici della nuova versione con browser, dettatura, «Ehi Jarvis» e risposte vocali hanno superato [Windows e Linux](https://github.com/MATRIXNEO23/jarvis/actions/runs/41126671637). **Le nuove funzioni non sono ancora state provate sul Pavilion**; la versione vocale precedente resta disponibile.

Assistente locale progettato per HP Pavilion i3-2100, 10 GB RAM, con obiettivo **zero costi aggiuntivi**. Sviluppo incrementale: non dichiarare funzionanti funzioni non testate.

## Nuovo ramo di prova: progetti indipendenti, orbite e Telegram vocale

**[Scarica JARVIS — progetti e Telegram (ZIP)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/project-memory-orbits-telegram.zip)**.

Include l'HUD nero cinematico e il reattore colorato, più **pallini orbitanti interattivi** per i progetti attivi e le notifiche Telegram, un gestore di **memorie separate per progetto con ricerca SQLite FTS5 e CONTINUITA.md persistente**, e una personalità più sintetica e ironica. Telegram è un'integrazione facoltativa per **un solo contatto privato** con risposte come **note vocali SAPI/OGG**, tramite Telethon e FFmpeg gratuiti; interruttore inizialmente OFF, autenticazione e scelta del contatto esplicitamente autorizzate, sessione cifrata con DPAPI. Non accede ad altri contatti né condivide automaticamente i ricordi di altri progetti.

**Non è una versione già collaudata sul Pavilion**: aprire in una nuova cartella. [Guida installazione, funzionamento, limiti e controlli](https://github.com/MATRIXNEO23/jarvis/blob/feature/project-memory-orbits-telegram/docs/PROJECT_MEMORY_TELEGRAM.md) · [PR draft #12](https://github.com/MATRIXNEO23/jarvis/pull/12).

## Ultimo aggiornamento visivo: sfondo cinematico più fedele al preview

**[Scarica JARVIS HUD con sfondo nero e circuiti discreti — ZIP](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/high-fidelity-cinematic-background.zip)**.

Dopo il test reale dell'HUD High Fidelity sul Pavilion, l'utente ha chiesto uno sfondo più vicino all'immagine originale: il ramo di prova ora rimpiazza la griglia blu uniforme dietro reattore e Terra con **nero-blu quasi assoluto, piste elettroniche sottili e punti ciano molto discreti**. Anche console e pannelli inferiori sono più scuri. Nessuna nuova libreria, API o costo; lo sfondo viene ridisegnato solo se la finestra è creata o ridimensionata.

**Non perde le funzioni** di ascolto automatico GPT, saluto orario, Second Brain, dialogo, comandi e approvazione dei file. [Guida e test sul Pavilion](https://github.com/MATRIXNEO23/jarvis/blob/feature/high-fidelity-cinematic-background/docs/HUD_CINEMATIC_BACKGROUND.md) · [PR draft #11](https://github.com/MATRIXNEO23/jarvis/pull/11). Estrai in una cartella diversa dalla versione che già funziona; collaudo visivo da eseguire.

## Ultima interfaccia di prova: JARVIS high fidelity

**[Scarica JARVIS HUD più fedele al concept originale (ZIP)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/high-fidelity-reference-hud.zip)**.

L'interfaccia sperimentale è stata rielaborata con **illuminazione rasterizzata, nuovi bagliori nel reattore**, un globo terrestre con continenti e luci più ricchi, cornici hi-tech più marcate, una console chat a piena altezza e strumenti **CPU / RAM / DISCO C / RETE** con valori reali o --. Il pulsante microfono e la freccia di invio sono visibili nel campo principale; le funzioni aggiuntive restano dietro **⋯**.

Il codice genera gli elementi PNG pesanti **una sola volta in un worker**, e anima quelli precalcolati per non sovraccaricare continuamente l'i3-2100. Non aggiunge API, librerie grafiche o costi. Rimangono l'ascolto automatico all'apertura dell'app, il saluto vocale, il dialogo GPT, il Second Brain e il cerchio **ciano nel silenzio / arancione quando parli / verde quando parla Jarvis**.

**Branch isolato:** questa non è una sostituzione della versione funzionante. Estrarre in una cartella nuova, confrontare realmente sul Pavilion con l'immagine di riferimento e approvare separatamente l'eventuale integrazione. [Guida](https://github.com/MATRIXNEO23/jarvis/blob/feature/high-fidelity-reference-hud/docs/HUD_HIGH_FIDELITY.md) · [PR #10](https://github.com/MATRIXNEO23/jarvis/pull/10).

## Nuova prova: JARVIS ascolta già all'apertura e saluta

**[Scarica la ZIP con microfono continuo, saluto vocale e nucleo reattivo](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/hud-speech-activity-auto-start.zip)**.

Aggiornamento sperimentale successivo al dialogo continuo: **microfono attivo quando apri JARVIS**, in modalità Conversazione continua GPT senza parola di attivazione, con saluto di apertura basato sull'orario locale. Il cerchio centrale è **ciano con microfono aperto ma in silenzio**, **arancione pulsante solo quando rileva la voce** e **verde pulsante mentre JARVIS risponde**. Se vuoi tornare allo standby iniziale, disattiva l'impostazione di avvio automatico in ⚙; la scelta rimane salvata per le successive aperture dell'app. Non aggiunge JARVIS all'avvio automatico di Windows.

[Guida, privacy e limiti](https://github.com/MATRIXNEO23/jarvis/blob/feature/hud-speech-activity-auto-start/docs/HUD_VOICE_ACTIVITY.md) · [CI Windows/Linux SUCCESS](https://github.com/MATRIXNEO23/jarvis/actions/runs/41151683977) · [PR #9 draft](https://github.com/MATRIXNEO23/jarvis/pull/9). **Da collaudare fisicamente sul Pavilion prima di qualunque merge.** Non sostituire la versione precedente: estrai il nuovo ZIP in una cartella separata.

## Ultima prova sperimentale: JARVIS con dialogo continuo e personalità

**[Scarica la ZIP con JARVIS conversazionale e HUD rinnovato](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/dialogue-continuity-personality.zip)**.

La nuova versione mantiene il reattore ciano/arancione/verde e la Terra animata, ma corregge due limiti del dialogo: il contesto breve che si svuotava se una risposta era troppo lunga e le frasi che venivano scartate mentre GPT elaborava. Ora JARVIS conserva i turni recenti in RAM e accoda fino a tre frasi in elaborazione, mantenendo come unica richiesta corrente l'ultima frase pronunciata. Usa inoltre una personalità coerente, italiana, competente e leggermente ironica; non scambia ricordi passati per autorizzazioni a nuove operazioni.

[Guida e limiti](https://github.com/MATRIXNEO23/jarvis/blob/feature/dialogue-continuity-personality/docs/DIALOGO_CONTINUO.md) · [Test Windows/Linux PASS](https://github.com/MATRIXNEO23/jarvis/actions/runs/41150861417) · [PR draft #8](https://github.com/MATRIXNEO23/jarvis/pull/8).

**Non integrare automaticamente:** l'efficacia va testata sul Pavilion in modalità Conversazione continua GPT, usando una nuova cartella per la ZIP. La memoria breve funziona anche senza attivare il Second Brain permanente. Nessun nuovo modello o servizio a pagamento.

## Ultimo concept JARVIS HUD — versione sperimentale

**[ZIP con reattore JARVIS e Terra animata più vicini al preview](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/hud-reference-redesign.zip)**.

Dopo il confronto fra la foto della prima interfaccia avviata e il concept originale, è stato implementato il nuovo design: console chat con schede realmente selezionabili, cerchio centrale con più dettagli e scritta **JARVIS** costante, Terra più ricca di continenti e luci, indicatori CPU/RAM/disco/GPT basati su dati reali. Il nucleo resta **ciano in inattività, lampeggia arancione quando Vosk sta ascoltando e verde durante la risposta vocale SAPI**. Il microfono resta in standby fino alla selezione manuale; le impostazioni si aprono tramite ⚙. Nessuna nuova dipendenza grafica o API a pagamento.

**Non sostituisce la versione già in uso**: scaricare ed estrarre in una cartella differente. Test automatici Windows/Linux superati, collaudo grafico e carico CPU sul Pavilion ancora necessario. [Specifiche aggiornate](https://github.com/MATRIXNEO23/jarvis/blob/feature/hud-reference-redesign/docs/HUD_REFERENCE_V2.md), [PR #7](https://github.com/MATRIXNEO23/jarvis/pull/7).

## Nuovo ramo di prova: memoria Second Brain di Lia

**[ZIP Jarvis con Second Brain locale e conversazione GPT](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/conversation-short-memory.zip)**.

Lia ora può utilizzare gli ultimi scambi per interpretare i messaggi successivi e, dopo **attivazione manuale del Second Brain**, archiviare conversazioni brevi e risultati di azioni locali realmente concluse in un database SQLite del PC, consultabile anche dopo il riavvio. Il nuovo ramo include il catalogo dei comandi e la gestione di Blocco note, ma resta isolato dalla versione funzionante. [Documentazione dettagliata](https://github.com/MATRIXNEO23/jarvis/blob/feature/conversation-short-memory/docs/SECOND_BRAIN.md) · [PR sperimentale #4](https://github.com/MATRIXNEO23/jarvis/pull/4).

**Non include ancora lettura/invio email**: prepara soltanto la registrazione futura di ricevute verificabili. Memoria persistente disattivata per impostazione predefinita, cancellabile manualmente; niente nuovi costi/API e microfono sempre spento all'avvio. Non sostituire la vecchia versione prima dei test sul Pavilion.

## Ultimo sviluppo sperimentale: interpretazione dei comandi

**[Scarica Jarvis con conversazione GPT e catalogo dei comandi](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/gpt-conversazione-documenti.zip)**.

Nel ramo di prova è disponibile un catalogo dichiarativo `jarvis_commands.json`: GPT consulta la lista delle azioni realmente implementate per identificare il comando anche quando la frase è diversa, ad esempio «mi chiudi Blocco note?» → `notepad.close`, oppure «aprimi il disco C» → `explorer.drive_c`. Le operazioni vengono eseguite da adapter Python verificati, **non** da comandi creati liberamente dal modello. [Documentazione del catalogo](https://github.com/MATRIXNEO23/jarvis/blob/feature/gpt-conversazione-documenti/docs/CATALOGO_COMANDI.md).

Questa è una **versione sperimentale**: conservare la vecchia installazione, usare un'altra cartella per la prova sul Pavilion. Il microfono parte spento e la modalità Conversazione continua GPT richiede selezione manuale e collegamento ChatGPT già disponibile. Nessuna nuova API a pagamento. Il catalogo non implica che ogni applicazione Windows sia automaticamente supportata.

## Download diretto per Windows

**[NUOVA PROVA — JARVIS CON DETTATURA, BROWSER, «EHI JARVIS» E RISPOSTE VOCALI OFFLINE](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/voice-browser-dictation.zip)**

Il ramo sperimentale aggiunge dettatura nelle altre finestre, apertura e ricerca nel browser, chiamata «Ehi Jarvis» per i comandi in ascolto continuo e **voci Windows selezionabili per risposte parlate gratuite/offline**. **Test automatici verdi; collaudo fisico ancora da fare. Non sostituisce per ora la versione già verificata.** [Dare una voce a Jarvis](https://github.com/MATRIXNEO23/jarvis/blob/feature/voice-browser-dictation/docs/VOCE_RISPOSTE.md) · [Dettatura e browser](https://github.com/MATRIXNEO23/jarvis/blob/feature/voice-browser-dictation/docs/DETTATURA_BROWSER.md).

**[SCARICA JARVIS — ZIP COMPLETO AGGIORNATO CON VOCE OFFLINE (PROVA)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/offline-voice-pavilion.zip)**

Questa e' la **versione di prova con voce italiana offline**. Il codice e' nel branch `feature/offline-voice-pavilion`, separato dal ramo stabile `main`. I test automatici Windows/Linux sono superati; **il microfono reale sul Pavilion non e' ancora stato collaudato**. Scarica lo ZIP, estrailo in **una cartella nuova**, avvia **`installa_voce.bat`** (installazione facoltativa dei moduli vocali e del modello italiano), poi **`avvia_jarvis.bat`**. **All'avvio il microfono e' spento** e le modalita' si selezionano solo manualmente.

**[SCARICA JARVIS — ZIP PRECEDENTE SENZA VOCE (MAIN)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/main.zip)**

[Cartella Download con istruzioni semplici](Download/README.md) · [Guida alla voce offline](https://github.com/MATRIXNEO23/jarvis/blob/feature/offline-voice-pavilion/docs/VOCE_OFFLINE.md) · [Verifica CI voce](https://github.com/MATRIXNEO23/jarvis/actions/runs/41099757267). Non serve cercare gli artifact di GitHub Actions. La versione e' ancora **alpha**, non un installer Windows autonomo; ChatGPT e pianificatore sono stati provati sul Pavilion, mentre la voce richiede collaudo.

## Architettura e roadmap

La progettazione **GPT-first + esecutore locale controllato + funzioni offline** è descritta in [ROADMAP.md](ROADMAP.md). Include fasi, criteri di verifica, sicurezza, memoria e prestazioni per i3-2100.

## Preferenze confermate

- **ChatGPT abilitato per impostazione predefinita**. L'utente può disattivarlo e riattivarlo manualmente dalle impostazioni; la scelta viene salvata.
- **Nessun timeout di inattività GPT**: il servizio resta consentito fino alla disattivazione manuale o alla chiusura di Jarvis. Non significa che una sessione OAuth sia già autenticata.
- **Microfono sempre spento quando parte Jarvis**, anche dopo riavvio; attivazione solo manuale. GPT e microfono sono opzioni indipendenti.
- Quando sarà disponibile il riconoscimento vocale: modalità standby, ascolto continuo, premi-per-parlare. Non cambiare modalità senza comando esplicito.
- Processi e moduli opzionali vanno caricati solo quando necessari; niente demoni separati in avvio automatico.
- Niente API a consumo, crediti aggiuntivi, rinnovi automatici o chiavi inserite nel codice.

## Stato di questa prima base

- [x] Interfaccia minimale delle impostazioni e salvataggio locale.
- [x] Interruttore GPT acceso di default e spento/riacceso manualmente, con stato persistente.
- [x] Microfono impostato su standby ad ogni lancio.
- [x] Motore locale a comandi consentiti, con registro attività SQLite (`local_engine.py`). Comandi supportati: `aiuto`, `stato sistema`, `mostra download`, `cerca file NOME` (ricerca limitata a Download), `apri blocco note`, `apri calcolatrice`, `apri esplora file`, `apri download`, `ultimi comandi`. Nessun comando shell arbitrario.
- [x] Campo comandi testuale integrato nella finestra, con lavoro su thread separato per non bloccare la GUI.
- [x] Test unitari e sintassi **superati sui runner GitHub Actions Windows e Linux** ([esecuzione riuscita](https://github.com/MATRIXNEO23/jarvis/actions/runs/41084817158)). **Primo avvio e prima risposta GPT confermati dall'utente sul Pavilion il 30/10/2026; collaudo delle altre funzioni ancora necessario**.

- [x] **Codice di integrazione GPT presente:** adapter Node `gpt_bridge.mjs` basato sul [DevKit ufficiale](https://github.com/openai/sign-in-with-chatgpt-devkit), client Python via pipe, cifratura DPAPI per utente Windows e installer su richiesta con SDK fissato a commit specifico.
- [x] **Interfaccia GPT:** Connetti ChatGPT, Scollega account, Chiedi a GPT, interruttore ON/OFF manuale; il tasto ON **non** equivale a una sessione OAuth connessa.
- [x] **Verifiche statiche e protocollo:** test Windows/Linux Python, sintassi Node e PowerShell; [smoke test Windows del kit GPT e del dialogo con il processo superato](https://github.com/MATRIXNEO23/jarvis/actions/runs/41087321055). Questo **non** verifica un login reale al piano ChatGPT.
- [x] **Primo login e risposta GPT sul Pavilion (30/10/2026):** l'utente ha confermato SDK installato, stato «connesso» e risposta pertinente ricevuta. Restano da testare riavvio, riconnessione, quote e consumi.
- [x] **Prima versione pianificatore GPT -> strumenti locali:** pulsante «Pianifica attività», proposta di massimo 5 passi con rigida lista di strumenti consentiti, anteprima, approvazione esplicita, annullamento fra passi e test CI. **Non ancora provato sul Pavilion**. Le risposte al pulsante «Chiedi a GPT» continuano a essere solo testo. Correzione successiva: arresto ai confini dei passi quando Jarvis viene chiuso, GPT disattivato/scollegato o l'autorizzazione revocata; test automatici Windows/Linux [verificati](https://github.com/MATRIXNEO23/jarvis/actions/runs/41096466572). Un passo gia iniziato non viene forzatamente interrotto.
- [ ] Comandi vocali, apprendimento procedure, TTS, tray, ricerca web, automazioni e packaging Windows.

## Primo test del pianificatore (versione precedente senza voce)

1. Chiudi Jarvis se è aperto. Scarica nuovamente lo ZIP dal link in cima alla pagina, poi estrailo **in una cartella nuova** (non sovrascrivere o eliminare i dati in `%LOCALAPPDATA%\\Jarvis`).
2. Apri la nuova cartella `jarvis-main` e avvia `avvia_jarvis.bat`. L'SDK già installato nella cartella runtime utente non va reinstallato, a meno che non compaia un errore.
3. Verifica che GPT sia connesso. Premi **Pianifica attività**, quindi scrivi, per esempio: `Apri la calcolatrice e controlla quanta RAM ho disponibile`.
4. Esamina l'anteprima. Premi **Approva ed esegui** solo se i passi corrispondono a ciò che desideri. Puoi usare **Annulla** per scartare il piano prima dell'esecuzione.
5. Il programma non elimina, scrive o modifica file e non esegue comandi shell attraverso questo pianificatore. Sono supportati solo i comandi già implementati dall'esecutore locale.
6. Per provare l'arresto: approva un piano innocuo di più passi e premi «Annulla», oppure disattiva GPT o chiudi Jarvis durante l'esecuzione. Verifica che non partano passi successivi. La singola operazione già iniziata può terminare prima che il blocco abbia effetto.

## Uso della versione alpha

Con Python 3.12 (presente sul Pavilion) e Tkinter: doppio clic su `avvia_jarvis.bat` oppure `py -3 jarvis.py`. Per testare: `py -3 -m unittest discover -s tests -v`.
- I comandi locali **non richiedono Node**.
- Per abilitare davvero il collegamento GPT: segui [docs/GPT_SETUP.md](docs/GPT_SETUP.md), installa Node 22.12+, lancia `installa_gpt.bat`, poi **Connetti ChatGPT** nella finestra.
- GPT resta **abilitato per scelta predefinita** ma richiede autenticazione. Non avviene alcuna richiesta AI senza comando esplicito.
- Il riconoscimento vocale **non è ancora implementato**; il microfono rimane spento.

Le impostazioni si salvano in `%LOCALAPPDATA%\\Jarvis\\settings.json`, non nella repository. Non committare credenziali, token o dati personali.

## Verifica richiesta prima di dichiarare GPT operativo

Il **primo login e la prima risposta GPT sono stati confermati dall'utente sul Pavilion il 30/10/2026**. Il test automatico controlla codice e protocollo, mentre prove approfondite di rinnovo sessione, logout e quote restano da completare. Nessun fallback alle API a consumo. La disponibilità del piano e i limiti sono gestiti dal servizio OpenAI, non garantiti dall'interruttore. Per sicurezza le risposte GPT non vengono mai interpretate come comandi di Windows in questa fase.
