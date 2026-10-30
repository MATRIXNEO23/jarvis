# Roadmap Jarvis — architettura GPT-first, controllo locale e funzionamento offline

> Stato: **sviluppo alpha locale** (Fase 1 iniziata; connessione GPT ancora assente). Questa roadmap descrive le funzionalità da realizzare; le caselle non completate **non** rappresentano funzioni disponibili. Aggiornamento: 30 ottobre 2026.

## Obiettivo

Realizzare un assistente Windows 10 x64 per HP Pavilion **Intel Core i3-2100, 10 GB di RAM, HDD e GPU datata**, che riceva richieste vocali e testuali in italiano, usi **ChatGPT per il ragionamento** quando autorizzato e disponibile, ed esegua operazioni controllate sul PC. Non dipendere da un grande modello AI locale: le funzioni di base devono funzionare **offline**.

**Requisito non negoziabile:** zero costi aggiuntivi. Nessuna chiave API a consumo, nessuna fatturazione automatica, nessun servizio a pagamento obbligatorio. Se il piano/permesso/quota ChatGPT non è utilizzabile, dichiararlo chiaramente e continuare con i comandi locali.

## Architettura prevista

```text
Voce (Vosk offline) / chat testuale / tasti
                  |
                  v
         Interfaccia Jarvis
       (tray, stato, consensi)
                  |
                  v
       Task Manager / Orchestratore
        |          |           |
        |          |           +--> memoria SQLite (task, procedure, journal)
        |          |
        |          +--> gateway GPT ufficiale (Sign in with ChatGPT)
        |                 interpretazione -> piano STRUTTURATO
        |                 risposta -> verifica locale -> eventuale revisione
        |
        +--> registro strumenti consentiti (capability registry)
                    |
                    +--> file e cartelle
                    +--> processi e applicazioni
                    +--> browser e ricerca pubblica
                    +--> diagnostica e progetti
                    +--> automazioni insegnate
                    |
                    v
              Policy/permessi -> backup -> esecuzione -> verifica -> audit
```

**Separazione delle responsabilità**
- **GPT = pianificatore/analista**, non processo con accesso illimitato a Windows. Ritorna piani strutturati; non shell libera eseguita direttamente.
- **Jarvis = esecutore locale**, applica controlli di validazione, limiti, conferme, timeout e controlli dei risultati.
- **Orchestratore = supervisore**, mantiene stati `queued / planned / needs_approval / running / verifying / completed / failed / cancelled`, checkpoint e ripresa dopo crash.
- **Offline = percorso indipendente**, nessun accesso GPT necessario per aprire programmi, controllare volume, cercare file, lanciare procedure già registrate o fare backup consentiti.

## Impostazioni già concordate (da non alterare automaticamente)

| Impostazione | Comportamento |
| --- | --- |
| Microfono all'avvio | **Spento**, sempre, anche dopo riavvio. |
| Modalità microfono | Standby / ascolto continuo / premi per parlare, selezionate **solo manualmente**. |
| Applicazioni pesanti | Non cambiano automaticamente la scelta dell'utente. |
| Collegamento GPT | **Abilitato di default**, con interruttore manuale ON/OFF e scelta salvata. |
| Timeout di inattività GPT | **Nessuno per ora**. Se autorizzato, il gateway resta disponibile finché non disattivato; non deve inviare richieste mentre inattivo. |
| Accesso ChatGPT | Necessita login, consenso e disponibilità reale del servizio/piano; «abilitato» non equivale a «connesso». |
| Voce | Scelta fra quelle effettivamente installate su Windows, test audio e velocità; preferenza salvata. |
| Risorse | Nessun modello pesante locale in standby. Caricamento modulare e monitoraggio del consumo. |
| Costi | Nessuna API a pagamento o fallback a consumo. |
| Memoria | Persistenza locale, controlli di privacy, backup e possibilità di correggere procedure. |

## Fasi, dipendenze e criteri di completamento

### Fase 0 — Fondamenta e verifiche di base
- [x] Repository e configurazione iniziale.
- [x] Interfaccia iniziale e preferenza booleana GPT (ON di default), senza connessione reale.
- [ ] CI per lint, test automatici, distribuzione Windows x64, controllo dipendenze/licenze.
- [ ] Misure di riferimento su i3-2100: RAM e CPU idle, startup, HDD, latenza e gestione errori.
- [ ] Verificare una versione Python e librerie **effettivamente compatibili** con Windows 10.
- [ ] Gestire avvio ritardato opzionale e una sola istanza senza processi residui.

**Gate:** installer o pacchetto portabile avviabile su Windows 10 x64; microfono spento all'avvio e nessuna chiamata in rete inattesa.

### Fase 1 — Esecutore affidabile, senza GPT
- [x] **Primo sottoinsieme implementato:** apri alcune applicazioni predefinite, elenca/cerca file in Download, stato sistema, aiuto. Rimangono da realizzare lettura file selezionati, controllo processi, backup e URL verificati.
- [ ] Motore task completo: coda, progressi, annullamento e timeout. **Parziale già implementato:** risultato strutturato, errori, registro SQLite e thread UI per non bloccare la finestra.
- [ ] Livelli di permesso: lettura; scrittura reversibile; cancellazione/esecuzione rischiosa con **conferma esplicita**.
- [ ] Allowlist di directory e comandi, protezione delle credenziali, blocco esecuzione di shell arbitraria proposta da GPT.
- [ ] Backup prima delle modifiche e registro per rollback quando tecnicamente possibile.
- [ ] Test end-to-end, riavvii e operazioni negate su Windows 10. **Parziale già scritto:** unit test con directory temporanea, comandi vietati e symlink; esecuzione CI da verificare.

**Gate:** una richiesta testuale multi-passaggio viene eseguita e verificata **senza GPT**, nessuna operazione pericolosa parte senza approvazione.

### Fase 2 — Collegamento GPT ufficiale con costo zero
- [ ] Integrare il [Sign in with ChatGPT DevKit](https://github.com/openai/sign-in-with-chatgpt-devkit) (`@siwc/local`), evitando soluzioni non ufficiali che automatizzano la UI di ChatGPT.
- [ ] Usare runtime Node >=22.12 solo per il gateway GPT, con dipendenze e licenze verificate; valutare impatto RAM/CPU sull'HP.
- [ ] Login browser con PKCE, callback localhost, validazione OIDC/scopes, token cifrati a riposo per utente Windows, refresh/riconnessione/logout e nessuna credenziale nei log o su GitHub.
- [ ] Interruttore GPT ON/OFF effettivo; **ON iniziale = permesso a usare il gateway, non accesso già autenticato**. OFF interrompe richieste e chiude la connessione/servizio.
- [ ] Se l'utente lascia GPT abilitato, mantenere il gateway disponibile senza timeout automatico; evitare richieste ripetitive e attività AI in background.
- [ ] Modelli: usare solo quelli disponibili all'account/sessione; distinguere `non installato / da autenticare / connesso / quota o permessi insufficienti / errore / disattivato`.
- [ ] Test reale (consenso + lista modelli + risposta completata + logout + riavvio). Vietato dichiarare «GPT funzionante» in assenza di test.
- [ ] **Nessun fallback automatico a chiavi API standard o crediti a consumo**, anche in caso di quote esaurite.

**Gate:** richiesta innocua completata tramite Sign in with ChatGPT su Windows 10 x64, consumo aggiuntivo assente, errori/quota comunicati con chiarezza, comando offline sempre disponibile.

### Fase 3 — Pianificazione assistita da GPT
- [ ] Parser intenzioni: comandi deterministici offline prima; GPT per compiti ambigui/complessi quando disponibile.
- [ ] Schema di piano `intent / steps / tool_id / arguments / expected_result / risk` con validazione rigorosa locale.
- [ ] Ciclo di verifica: GPT propone -> policy valida -> Jarvis esegue -> raccoglie esito -> GPT può ripianificare entro limiti.
- [ ] Limiti su numero passi, durata, directory, operazioni, rete; consenso quando la richiesta va oltre i permessi.
- [ ] Isolamento dei contenuti web/documenti da istruzioni operative (difesa da prompt injection).
- [ ] Test su casi pratici: «controlla la build Minecraft», «individua ZIP duplicati», «prepara backup progetto»; niente modifiche non autorizzate.

**Gate:** task con almeno 3 passi, esito verificato e log riproducibile; fallimento sicuro quando GPT non è disponibile.

### Fase 4 — Memoria persistente e apprendimento
- [ ] SQLite locale: preferenze, progetti, comandi, task, stato, journal/checkpoint e cronologia controllabile.
- [ ] «Insegna a Jarvis»: registra **azioni esplicite** e/o una procedura illustrata dall'utente; prima simulazione/anteprima, poi salvataggio.
- [ ] Modifica, rinomina, elimina, esporta/importa procedure, versioni, rollback e conferma per azioni rischiose.
- [ ] Ripresa dopo riavvio senza ripetere passi distruttivi; idempotenza e checkpoint.
- [ ] Osservazione di azioni sul desktop solo dopo consenso specifico; niente monitoraggio nascosto, password o dati sensibili registrati.

**Gate:** una procedura nuova viene insegnata, modificata, riavviata e rieseguita correttamente senza GPT.

### Fase 5 — Voce, interfaccia e web
- [ ] Riconoscimento offline Vosk in italiano, con gestione silenzio/rumore e wake word o push-to-talk.
- [ ] Modalità microfono manuali (standby / ascolto continuo / premi-per-parlare) e tray; **all'avvio sempre standby**.
- [ ] Sintesi vocale locale selezionabile (voci effettivamente disponibili, anteprima, velocità, volume).
- [ ] Ricerca web gratuita su richiesta, citazione URL/fonti, nessun web scraper sempre attivo; sintesi GPT solo se disponibile.
- [ ] Log e diagnostica esposti nella UI: CPU/RAM, latenza, microfono, stato GPT, task e permessi.
- [ ] Test con Minecraft o altro carico reale e degradazione controllata.

**Gate:** comando vocale locale completo con microfono attivato manualmente; nessun ascolto fuori dalla modalità selezionata.

### Fase 6 — Hardening e prima release testabile
- [ ] Test a freddo, riavvio, crash, perdita Internet, quota GPT terminata, permessi negati, file bloccati.
- [ ] Confronto prestazioni su i3-2100/10 GB: idle, ascolto, GPT abilitato, task parallelo a Minecraft.
- [ ] Packaging e script d'installazione che scaricano solo componenti necessari, con versioni/firme/hash verificabili.
- [ ] Manuale utente, troubleshooting, privacy locale, aggiornamenti non distruttivi.
- [ ] Release con numero versione, changelog, artefatti scaricabili e test realmente eseguiti.

**Gate:** workflow end-to-end provato su Windows 10 x64, nessun addebito, nessuna perdita dei dati, processi chiudibili completamente.

## Primo caso d'uso di riferimento

> «Jarvis, apri il progetto Minecraft, controlla gli errori dell'ultima compilazione e dimmi come correggerli».

1. Identifica la cartella del progetto **solo se configurata/autorizzata**.
2. Legge i log autorizzati, estrae l'errore, evita invio di segreti a GPT.
3. Se GPT è disponibile, chiede una diagnosi e un piano di correzione.
4. Mostra le modifiche previste e richiede conferma; salva backup.
5. Applica modifiche consentite, esegue test/compilazione nei limiti configurati.
6. Verifica output e registra nel journal cosa è riuscito e cosa no.
7. Se GPT è assente: offre i log e comandi locali, senza simulare una diagnosi GPT.

## Regole di qualità

- Distinguere sempre: **progettato**, **implementato**, **testato localmente**, **verificato sul Pavilion**.
- Ogni operazione riporta stato, esito, file toccati, eventuali permessi e passi di recupero.
- Nessun risultato inventato; nessuna azione compiuta «di nascosto».
- Modifica architetturale solo con test di regressione e senza distruggere dati dell'utente.
- Non introdurre nuove dipendenze sempre attive per risolvere una funzione occasionale.
- Quando si usa Sign in with ChatGPT, verificare sul dispositivo disponibilità effettiva del piano e dei permessi, senza presumere accesso ad altre chat o memorie dell'account.
