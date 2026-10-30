# Jarvis — Windows 10 (64 bit)

Assistente locale progettato per HP Pavilion i3-2100, 10 GB RAM, con obiettivo **zero costi aggiuntivi**. Sviluppo incrementale: non dichiarare funzionanti funzioni non testate.

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
- [x] Test unitari e sintassi **superati sui runner GitHub Actions Windows e Linux** ([esecuzione riuscita](https://github.com/MATRIXNEO23/jarvis/actions/runs/41084817158)). **Prova sul tuo Windows 10/i3-2100 ancora da effettuare**.

- [x] **Codice di integrazione GPT presente:** adapter Node `gpt_bridge.mjs` basato sul [DevKit ufficiale](https://github.com/openai/sign-in-with-chatgpt-devkit), client Python via pipe, cifratura DPAPI per utente Windows e installer su richiesta con SDK fissato a commit specifico.
- [x] **Interfaccia GPT:** Connetti ChatGPT, Scollega account, Chiedi a GPT, interruttore ON/OFF manuale; il tasto ON **non** equivale a una sessione OAuth connessa.
- [x] **Verifiche statiche e protocollo:** test Windows/Linux Python, sintassi Node e PowerShell su GitHub Actions.
- [ ] **Login OAuth e inferenza reale testati sul Pavilion:** serve eseguire `installa_gpt.bat`, autorizzare il proprio account dal browser e ottenere una vera risposta. Le capacità del piano non vengono presunte.
- [ ] **Pianificatore GPT -> strumenti locali:** ancora assente. Le risposte testuali GPT non avviano azioni sul computer.
- [ ] Comandi vocali, apprendimento procedure, TTS, tray, ricerca web, automazioni e packaging Windows.

## Uso della versione alpha

Con Python 3.11 e Tkinter: doppio clic su `avvia_jarvis.bat` oppure `py -3 jarvis.py`. Per testare: `py -3 -m unittest discover -s tests -v`.
- I comandi locali **non richiedono Node**.
- Per abilitare davvero il collegamento GPT: segui [docs/GPT_SETUP.md](docs/GPT_SETUP.md), installa Node 22.12+, lancia `installa_gpt.bat`, poi **Connetti ChatGPT** nella finestra.
- GPT resta **abilitato per scelta predefinita** ma richiede autenticazione. Non avviene alcuna richiesta AI senza comando esplicito.
- Il riconoscimento vocale **non è ancora implementato**; il microfono rimane spento.

Le impostazioni si salvano in `%LOCALAPPDATA%\\Jarvis\\settings.json`, non nella repository. Non committare credenziali, token o dati personali.

## Verifica richiesta prima di dichiarare GPT operativo

Il modulo implementa l'interfaccia del DevKit, ma **non è ancora stato verificato con un consenso reale e una risposta completata sull'account dell'utente**. Il test automatico controlla codice e protocollo, non l'autenticazione reale. Nessun fallback alle API a consumo. La disponibilità del piano e i limiti sono gestiti dal servizio OpenAI, non garantiti dall'interruttore. Per sicurezza le risposte GPT non vengono mai interpretate come comandi di Windows in questa fase.
