# Registro delle capacità vive — modello GPT esterno

**Stato:** sviluppo isolato in `feature/live-capability-registry-external-gpt` (PR draft #27). Non è un nuovo modello locale, non utilizza API OpenAI a consumo e non fornisce accesso diretto al filesystem del Pavilion a GPT.

## Architettura verificata
Jarvis disponeva già di `jarvis_commands.json` e `capability_registry.py`: il JSON **descrive**, mentre le associazioni Python compilate + il dispatcher + la verifica degli argomenti **autorizzano** l'esecuzione. `conversation_router.py` traduce risposte JSON del GPT e `gpt_bridge.mjs` invia prompt tramite lo SDK Sign in with ChatGPT (limite 5000 caratteri). Il modello esterno non scopre le capacità locali da solo.

Questo ramo introduce `live_capabilities.py`, che produce una fotografia per ogni nuova richiesta al GPT:
- identità e revisione del catalogo compilato;
- disponibilità del dialogo vocale Telegram dalla configurazione locale (credenziali presenti, contatti abilitati, Telethon, Windows SAPI/FFmpeg);
- risposte Telegram automatiche ON/OFF;
- solo **numero** dei contatti selezionati, non nomi/ID;
- stream del microfono realmente aperto, quando osservabile;
- WhatsApp dichiarato non implementato;
- capacità add-on registrate esplicitamente da un componente locale attendibile e loro stato disponibile/disattivato.

Ogni prompt nuovo include una revisione breve; nessun invio di API hash, credenziali, sessioni, chat, nomi, numeri di telefono, documenti o contenuti locali. Il catalogo conversazionale è compattato per rispettare il limite di 5000 caratteri senza perdere i comandi già autorizzati o la frase dell'utente.

## Telegram: proposta GPT non equivale a invio
Nuova azione compilata `telegram.voice.start` nel catalogo. Il modello può proporre soltanto `recipient` (nome detto dall'utente); il dispatcher locale riconsidera lo stato attuale prima di accettare la proposta, riconosce un contatto selezionato non ambiguo tramite ID e avvia il **dialogo locale** «Che messaggio?» → contenuto → «Confermo». Il modello non sceglie autonomamente contatti, non costruisce file audio, non riceve credenziali, non conferma l'invio e non determina una destinazione arbitraria. Le chiamate dirette già esistenti restano valide.

## Contratto futuro obbligatorio per gli add-on
Il semplice file manifest non rende un comando disponibile. Un add-on deve essere installato da un gestore locale affidabile, caricare un **handler realmente presente e approvato**, fornire una verifica di disponibilità e registrare il proprio ID con `LiveCapabilityRegistry.register(AddonBinding(...))`. Non sono ammessi nomi/ID arbitrari o handler non chiamabili.

**Eventi da gestire dal gestore degli add-on quando verrà introdotto:**
1. Installazione o abilitazione riuscita: verificare dipendenze, controllo/permessi e handler, quindi `register`. Il prossimo prompt GPT mostra lo stato attuale.
2. Disabilitazione, disinstallazione o crash: `unregister` o disponibilità `False` immediata. Nessun comando viene eseguito se il componente non è operativo.
3. Modifica di una opzione o revoca di permessi: la funzione `availability` viene richiamata alla prossima richiesta. Prima di qualsiasi futura esecuzione, il dispatcher deve ripetere la verifica su snapshot corrente.
4. Aggiornamento del **codice** add-on: richiede reinstallazione/caricamento controllato e nuova registrazione; non eseguire hot-reload arbitrario di file Python. Una versione o un handler cambiato non può conservare privilegi per inerzia.
5. Descrizione/azione aggiunta a un catalogo: l'impronta del catalogo cambia automaticamente, ma l'esecuzione resta vietata finché il dispatcher locale non ha la relativa associazione validata.

**Importante:** il registro di add-on in questa fase è un meccanismo di osservazione e di contratto. **Non esiste ancora in Jarvis un installatore generale di add-on che chiami automaticamente register/unregister, né un dispatcher di add-on eseguibile da GPT.** Gli add-on mostrati sono quindi indicati come informativi e *non invocabili via GPT*. Non considerare completata la funzione di installazione automatica finché non esisterà e non sarà stata collaudata questa integrazione.

## Prove prima di un'eventuale adozione
- Il catalogo cambia quando una spunta o la modalità Telegram cambia e quando un add-on viene registrato, disabilitato o revocato.
- Nessuna autorizzazione è conferita dal solo JSON o da una risposta del GPT; un'azione Telegram proposta quando il modulo è OFF deve essere rifiutata.
- L'assenza di contatti/FFmpeg/Telethon/sesssione non deve essere descritta come invio vocale disponibile.
- Il dialogo richiede il contenuto e la conferma dell'utente, senza riprovare su esito incerto.
- Zero divulgazione di nomi contatti o ID tramite stato capacità.
- Il prompt resta al massimo 5000 caratteri anche con 450 caratteri di richiesta.
- Regressione completa Windows/Ubuntu; **nessun invio reale** nei test CI.
- Ultimo gate: test sul Pavilion della nuova build e un reale invio Telegram a un contatto di prova consenziente.

Restano invariati backup, vecchie build e la decisione di **non unire sperimentazioni automaticamente**. WhatsApp resta sospeso.
