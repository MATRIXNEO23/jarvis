# WhatsApp per Jarvis — backlog sospeso / non implementato

**Stato al 31 ottobre 2026:** proposta funzionale concordata, **rinviata**. Priorità immediata: migliorare Telegram secondo le prossime indicazioni dell'utente. Questa pagina è una nota di continuità, non un incarico a creare codice, attivare servizi o avviare workflow.

## Obiettivo futuro
Aggiungere WhatsApp come canale opzionale di messaggistica a Jarvis, per poter ricevere, leggere e inviare messaggi e, quando esplicitamente abilitato, rispondere automaticamente ai contatti autorizzati. Jarvis mantiene l'architettura attuale: motore locale leggero per impostazioni, controllo, gestione eventi e operazioni; GPT esterno **solo tramite Sign in with ChatGPT** per la generazione di risposte. Nessun modello AI locale aggiuntivo o API GPT a consumo.

## Interfaccia prevista: Impostazioni > WhatsApp
- **Interruttore generale WhatsApp ON/OFF**, con priorità assoluta sulle autorizzazioni dei contatti. OFF: nessuna lettura, risposta o invio; configurazioni conservate senza cancellazioni.
- **Elenco contatti configurati** con un interruttore ON/OFF *indipendente* per ogni contatto. OFF: nessuna interazione di Jarvis con quel contatto; gli altri restano gestibili se l'interruttore generale è ON.
- **Pulsante «+ Aggiungi contatto»**: acquisisce almeno nome e numero WhatsApp con prefisso internazionale; convalida il numero e permette la configurazione delle autorizzazioni. Il contatto viene gestito localmente e non è automaticamente autorizzato all'accesso a messaggi storici.
- Per ogni contatto abilitato, tre permessi distinti: **Leggi**, **Rispondi automaticamente**, **Invia messaggi**. Se «Leggi» è OFF, non si può abilitare «Rispondi automaticamente». L'utente decide se abilitarli e può revocarli.
- Possibilità futura di modificare dati, permessi e stato senza perdere l'elenco. Impostazioni **persistenti** e revocabili.
- **Anteprima UI mostrata in chat era illustrativa** e non ha creato/salvato contatti nel programma.

## Vincoli non negoziabili
1. **Zero costi aggiuntivi**, zero addebiti automatici: se una operazione può essere fatturata o il budget gratuito è esaurito, bloccare prima di eseguire, non inviare. Non assumere come certa una quota di 1.000 messaggi gratis al mese o una tariffa senza verifica ufficiale aggiornata.
2. Non presumere che WhatsApp Cloud API/Business consenta di importare la rubrica del **WhatsApp personale**, leggere tutte le chat preesistenti o avviare chiamate personali automatizzate. La fattibilità e i permessi dipendono dalla modalità di collegamento da scegliere successivamente; nessun provider è stato ancora approvato.
3. Non automatizzare un account personale tramite strumenti non ufficiali prima di valutarne affidabilità, conformità e rischio di blocco. Preferire soluzioni ufficiali, sostenibili e compatibili con le richieste.
4. Isolamento forte: nessun messaggio di contatto non autorizzato, nessuna lettura di archivi personali/progetti Telegram/altre chat; inviare a GPT esterno solo il contesto strettamente necessario per un contatto abilitato, nell'ambito dei permessi.
5. L'utente deve poter spegnere tutto immediatamente e revocare singoli contatti; nessuna attivazione automatica al solo inserimento di un numero.
6. Soluzione leggera per HP Pavilion i3-2100, 10 GB RAM, Windows 10. Evitare browser pesanti in background quando possibile.
7. Nessun merge, installazione, account Business, servizio, codice, workflow o consumo avviato in questa fase.

## Richiesta separata, NON ancora approvata per implementazione
In precedenza l'utente ha considerato anche un sistema sveglia che **chiama davvero** suo figlio a un'ora impostata. Questa funzionalità è diversa dalla messaggistica e **non va data per possibile gratuitamente via WhatsApp API**; richiede studio a parte della modalità di chiamata e del consenso, senza confonderla con l'invio di note vocali.

## Priorità e ripresa
**Adesso lavorare su Telegram, non su WhatsApp.** Attendere gli specifici miglioramenti Telegram richiesti dall'utente, senza inventarli. Solo su nuova autorizzazione, recuperare questa nota, verificare capacità e prezzi ufficiali attuali, scegliere un'architettura coerente e pianificare un'implementazione isolata/testabile. Nessun cambiamento WhatsApp in questa operazione.
