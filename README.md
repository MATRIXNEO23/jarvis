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
- [x] Test unitari di base e workflow CI Windows/Linux inseriti; **esito della CI e prova su Windows 10 fisico ancora da verificare**.

- [ ] **Connessione Sign in with ChatGPT realmente funzionante e collaudata su Windows**. Abilitare GPT non equivale ad autenticarsi. Il componente OAuth va collegato al [DevKit ufficiale](https://github.com/openai/sign-in-with-chatgpt-devkit), con storage cifrato e test reale, prima di mostrare «Connesso».
- [ ] Comandi vocali, apprendimento procedure, TTS, tray, ricerca web, automazioni e packaging Windows.

## Esecuzione della sola interfaccia iniziale

Con Python 3.11 e Tkinter: `py -3 jarvis.py`. Per testare: `py -3 -m unittest discover -s tests -v`. Non è richiesta una installazione Node.js per usare i comandi locali della finestra: Node sarà necessario **solo** per il futuro collegamento Sign in with ChatGPT. Il collegamento GPT non è ancora pronto; l'interruttore salva soltanto la preferenza. Il microfono non è ancora implementato. La GUI non apre processi AI in background.

Le impostazioni si salvano in `%LOCALAPPDATA%\\Jarvis\\settings.json`, non nella repository. Non committare credenziali, token o dati personali.

## Prossimo modulo GPT

Integrare la libreria `@siwc/local` del DevKit ufficiale in un processo Node.js figlio del programma. Consentire avvio/stop manuale, riconnessione, refresh e logout; cifrare i token con protezione per utente Windows. Stato «connesso» solo dopo autentica e test richiesta completata. Nessun fallback alle API a consumo. La disponibilità del piano e i limiti sono gestiti dal servizio OpenAI, non sono garantiti dal toggle.
