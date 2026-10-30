# Jarvis — Windows 10 (64 bit)

Assistente locale progettato per HP Pavilion i3-2100, 10 GB RAM, con obiettivo **zero costi aggiuntivi**. Sviluppo incrementale: non dichiarare funzionanti funzioni non testate.

## Download diretto per Windows

**[SCARICA JARVIS — ZIP COMPLETO (versione aggiornata)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/main.zip)**

[Cartella Download con istruzioni semplici](Download/README.md). Non serve cercare gli artifact di GitHub Actions: lo ZIP contiene tutta la repository e i file `installa_gpt.bat` e `avvia_jarvis.bat`. Versione **alpha**; il primo login e una risposta GPT sono stati provati sul Pavilion il 30/10/2026. Le altre funzioni richiedono collaudi specifici.

## Architettura e roadmap

La progettazione **GPT-first + esecutore locale controllato + funzioni offline** è descritta in [ROADMAP.md](ROADMAP.md). Include fasi, criteri di verifica, sicurezza, memoria e prestazioni per i3-2100.

## Preferenze confermate

- **ChatGPT abilitato per impostazione predefinita**. L'utente può disattivarlo e riattivarlo manualmente dalle impostazioni; la scelta viene salvata.
- **Nessun timeout di inattività GPT**: il servizio resta consentito fino alla disattivazione manuale o alla chiusura di Jarvis. Non significa che una sessione OAuth sia già autenticata.
- **Microfono sempre spento quando parte Jarvis**, anche dopo riavvio; attivazione solo manuale. GPT e microfono sono opzioni indipendenti.
- Quando sarà disponibile il riconoscimento vocale: modalità standby, ascolto continuo, premi-per-parlare. Non cambiare modalità senza comando esplicito.
- Processi e moduli opzionali vanno caricati solo quando necessari; niente demoni separati in avvio automatico.
- Niente API a consumo, crediti aggiuntivi, rinnovi automatici o chiavi inserite nel codice.

## Voce offline — prova separata in corso

La prima versione con riconoscimento vocale offline e' sul branch
[`feature/offline-voice-pavilion`](https://github.com/MATRIXNEO23/jarvis/tree/feature/offline-voice-pavilion)
e nella [pull request](https://github.com/MATRIXNEO23/jarvis/pull/1).
La versione `main` rimane invariata fino al collaudo.

Per provarla, scarica lo
[ZIP della versione voce](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/offline-voice-pavilion.zip),
estrailo **in una cartella nuova**, esegui una volta `installa_voce.bat`,
poi `avvia_jarvis.bat`. Guida: [voce offline](docs/VOCE_OFFLINE.md).
Il microfono e' spento a ogni avvio. Test reali del microfono sul Pavilion da fare.

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

## Primo test del pianificatore (dopo l'aggiornamento dello ZIP)

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
