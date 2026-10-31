# Roadmap Jarvis — architettura GPT-first, controllo locale e funzionamento offline

## Regola progettuale persistente — add-on (31/10/2026)

**Per le prossime funzionalità**, adottare come criterio predefinito l'architettura modulare degli **add-on `.jaddon`**: timer, cronometro e altri strumenti devono essere progettati come moduli indipendenti, installabili/attivabili/disattivabili dal gestore add-on. Prima di implementarli, verificare che l'infrastruttura esistente li supporti realmente; se richiedono estensioni al nucleo, limitarle a gateway/interfacce generiche e sicure, evitando integrazioni specifiche di ogni strumento direttamente nel programma principale. Nessun add-on non verificato può eseguire codice arbitrario. **Zero costi aggiuntivi, nessuna API a consumo**.

**Funzioni già esistenti:** non migrare automaticamente nulla. Prima di qualunque migrazione svolgere una valutazione esplicita di fattibilità, vantaggi, rischi, dipendenze, impatto su dati/impostazioni e regressioni. Valutare innanzitutto se sia preferibile **lasciare inalterate tutte le funzioni esistenti e applicare la regola solo alle successive**. Migrare soltanto dopo una decisione separata e un'approvazione esplicita dell'utente, con test e possibilità di ripristino.

**Stato della decisione:** regola salvata; nessuna conversione o modifica funzionale autorizzata adesso. Il timer attualmente integrato rimane com'è per il momento.

---


> Stato: **sviluppo alpha locale** (comandi locali e prima connessione GPT funzionanti; pianificatore con approvazione in prova). Questa roadmap descrive le funzionalità da realizzare; le caselle non completate **non** rappresentano funzioni disponibili. Aggiornamento: 30 ottobre 2026.

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
- [x] Implementato **adapter sperimentale** per il [Sign in with ChatGPT DevKit](https://github.com/openai/sign-in-with-chatgpt-devkit) (`@siwc/local`), senza browser automation non ufficiale. Richiede collaudo con account reale.
- [ ] Node >=22.12: installer su richiesta, commit SDK fissato e processo figlio isolato **implementati**; misurazione RAM/CPU sul Pavilion e verifica completa delle dipendenze ancora da effettuare.
- [ ] Login browser/PKCE/OIDC delegati all'SDK ufficiale e protezione DPAPI **implementati**, con primo collegamento reale riuscito sul Pavilion il 30/10/2026. Restano da verificare refresh, disconnessione, revoca e comportamento dopo riavvio.
- [x] Interruttore ON/OFF collegato al processo figlio e preferenza persistente; ON iniziale = **permesso di tentare il gateway**, non accesso già autenticato. Da testare con richiesta attiva durante la disattivazione.
- [x] Gateway avviato quando GPT è abilitato (e installato), senza timeout automatico; nessuna richiesta AI in background. Test CPU/RAM ancora da effettuare.
- [ ] Modelli da catalogo SDK, selezione prima voce disponibile e indicatori stato **implementati in alpha**; affinare errori quota e aggiungere scelta modello, quindi verificare su account reale.
- [ ] **Test reale parzialmente riuscito il 30/10/2026 sul Pavilion**: installazione SDK, stato connesso e prima risposta testuale confermati dall'utente. Restano test lista modelli, logout, riavvio, quote e prestazioni.
- [x] **Nessun fallback automatico a chiavi API standard o crediti a consumo** previsto nel codice; le richieste passano esclusivamente per SDK ufficiale dopo consenso.

**Gate:** richiesta innocua completata tramite Sign in with ChatGPT su Windows 10 x64, consumo aggiuntivo assente, errori/quota comunicati con chiarezza, comando offline sempre disponibile.

### Fase 3 — Pianificazione assistita da GPT
> **Stato 30/10/2026:** prima UI con pulsante «Pianifica attività», anteprima, approvazione e annullamento fra passi implementata e testata in CI Windows/Linux. Aggiunta protezione dei passi successivi se Jarvis viene chiuso o GPT viene disattivato/scollegato, con test di regressione verdi. Un comando locale già iniziato non può essere annullato forzatamente. Non ancora collaudata sul Pavilion; il pulsante «Chiedi a GPT» non esegue comandi.

- [ ] Parser intenzioni: comandi deterministici offline prima; GPT per compiti ambigui/complessi quando disponibile.
- [x] **Prima versione del piano a passi**: `intent / steps / tool_id / arguments` generati da GPT, convertiti localmente in azioni fisse con `description / risk / expected_result` e validazione rigorosa. Test automatici verdi, collaudo sul Pavilion da fare.
- [ ] Ciclo di verifica: GPT propone -> policy valida -> Jarvis esegue -> raccoglie esito -> GPT può ripianificare entro limiti.
- [ ] **Parziale:** massimo 5 passi, allowlist dei comandi locali già implementati, richieste GPT con timeout, sola consultazione Download e conferma esplicita prima di eseguire. Mancano ancora limiti temporali e permessi granulari per attività future.
- [ ] Isolamento dei contenuti web/documenti da istruzioni operative (difesa da prompt injection).
- [ ] Test di regressione del nuovo pianificatore esistenti (validazione, comandi vietati, file Download, apertura programmi); prove end-to-end reali e casi Minecraft/backup ancora da implementare.

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

### Fase 7 — App Android telecomando per Jarvis sul Pavilion
- [ ] **App Android leggera push-to-talk:** pulsante per parlare solo mentre premuto, conversazione testuale e risposta vocale sul telefono. Nessun modello IA pesante sul cellulare.
- [ ] **Bridge sul PC:** riceve la richiesta autenticata dal telefono, la consegna al motore Jarvis (locale o GPT quando autorizzato) e restituisce testo, esito e audio/risposta da pronunciare.
- [ ] **Uso in casa sulla LAN/Wi-Fi:** primo collegamento con associazione esplicita del telefono, autenticazione a dispositivo e trasporto cifrato quando possibile; nessuna apertura di porte pubbliche.
- [ ] **Accesso fuori casa opzionale:** soltanto attraverso una VPN privata/canale cifrato configurato e autorizzato dall'utente; nessun server o hosting a pagamento obbligatorio.
- [ ] **Controlli sicurezza:** conferme per azioni rischiose, stesso registro permessi del PC, revoca dispositivo, limite richieste, disconnessione e nessuna esposizione di credenziali ChatGPT al telefono.
- [ ] **Privacy e risorse:** microfono del telefono solo su azione volontaria; microfono del Pavilion sempre spento all'avvio; comunicazione locale senza servizi a consumo, gestione PC spento/non raggiungibile e disconnessioni.
- [ ] **Test reali:** invio richiesta Android → Pavilion, esecuzione autorizzata, risposta Android anche parlata, blocco di dispositivi non associati e recupero da rete assente.

**Gate:** da Android si preme per parlare, Jarvis sul Pavilion elabora la richiesta e risponde sul telefono, con autenticazione e senza esporre direttamente il PC a Internet. **Stato: solo pianificato; non implementato.**

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
