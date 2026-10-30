# Jarvis — Windows 10 (64 bit)

Assistente locale progettato per HP Pavilion i3-2100, 10 GB RAM, con obiettivo **zero costi aggiuntivi**. Sviluppo incrementale: non dichiarare funzionanti funzioni non testate.

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
- [ ] **Connessione Sign in with ChatGPT realmente funzionante e collaudata su Windows**. Abilitare GPT non equivale ad autenticarsi. Il componente OAuth va collegato al [DevKit ufficiale](https://github.com/openai/sign-in-with-chatgpt-devkit), con storage cifrato e test reale, prima di mostrare «Connesso».
- [ ] Comandi vocali, apprendimento procedure, TTS, tray, ricerca web, automazioni e packaging Windows.

## Esecuzione della sola interfaccia iniziale

Con Python 3 e Tkinter: `py -3 jarvis.py`. Non è richiesta una installazione Node.js per aprire questa finestra: Node sarà necessario **solo** per il futuro collegamento Sign in with ChatGPT. L'interfaccia mostra chiaramente che il collegamento non è ancora pronto; non apre processi fittizi.

Le impostazioni si salvano in `%LOCALAPPDATA%\\Jarvis\\settings.json`, non nella repository. Non committare credenziali, token o dati personali.

## Prossimo modulo GPT

Integrare la libreria `@siwc/local` del DevKit ufficiale in un processo Node.js figlio del programma. Consentire avvio/stop manuale, riconnessione, refresh e logout; cifrare i token con protezione per utente Windows. Stato «connesso» solo dopo autentica e test richiesta completata. Nessun fallback alle API a consumo. La disponibilità del piano e i limiti sono gestiti dal servizio OpenAI, non sono garantiti dal toggle.
