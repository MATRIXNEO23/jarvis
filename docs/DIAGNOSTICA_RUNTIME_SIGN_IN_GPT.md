# Jarvis — diagnosi coerente con Sign in with ChatGPT (31/10/2026)

## Cosa c'è davvero in Jarvis
- **Python locale**: interfaccia, Vosk, archivi, executor controllato e diagnostica.
- **GPT esterno**: accessibile esclusivamente tramite `gpt_client.py` → `gpt_bridge.mjs` → SDK Sign in with ChatGPT. Il modello non gira sul Pavilion e non legge direttamente i suoi file.
- **Consenso**: la scansione locale non contatta il modello. L'invio del rapporto ridotto al modello richiede conferma esplicita. La risposta GPT è solo un suggerimento; non esegue comandi e non modifica file.

## Nuove osservazioni locali in sola lettura
Alla conclusione dell'inventario e della verifica statica, `snapshot_runtime_evidence()` legge esclusivamente stati di componenti **già inizializzati**:
- SDK/Node/bridge disponibili, processo bridge in esecuzione e connessione precedentemente segnalata dall'interfaccia. Nessun nuovo login, ping, richiesta GPT o prova della qualità della connessione.
- Modalità microfono selezionata e `VoiceController.is_listening()`, che rileva lo stream reale. Standby e premi-per-parlare inattivo sono **stati normali**, non guasti. Non accende il microfono.
- Oggetto motore locale e presenza del suo archivio SQLite; oggetto memoria progetti e presenza dell'archivio. Presenza non equivale a corretto funzionamento.
- Contatori anonimi **in RAM** dei soli eventi di errore gestiti mentre l'istanza è aperta: GPT, voce, motore locale, documenti, journal progetti, scollegamento Telegram e diagnostica. Non registra il testo degli errori, file, comandi, messaggi o nomi di progetti. I contatori sono limitati a 99 per categoria e si azzerano al riavvio.

Il rapporto mostra osservazioni **insieme** alle euristiche sui sorgenti; le distingue esplicitamente da test end-to-end. Non sono stati letti log di sistema, database privati o documenti. Non si eseguono nuove azioni sul PC e non vengono installati modelli o servizi.

## Passaggio al GPT esterno
La funzione `diagnostic_handoff.py` inoltra, solo con consenso, i dati già limitati del controllo sorgenti, i precedenti conteggi anonimi delle operazioni e un nuovo blocco `observed_runtime`. I campi sono enumerazioni fisse (componente, stato, codice evento) e numeri, senza stringhe libere o percorsi, e vengono verificati con allowlist. Il prompt proibisce di confondere presenza di un componente e riuscita di una prova funzionale. Nessuna funzione di shell, automodifica o accesso al computer viene consegnata al GPT.

Il comando vocale e il pulsante continuano a effettuare **prima** la scansione locale. Al termine viene salvato anche lo snapshot runtime; una nuova diagnosi lo invalida. Annullamento, errore e timeout non autorizzano il riutilizzo di un vecchio snapshot. Il watchdog di 12/120 secondi continua a riguardare solo la GUI locale.

## Test e collaudo
I test automatici coprono separazione dei componenti, modalità standby non erroneamente classificata guasta, stream osservato/non osservato, bridge disconnesso, whitelist di dati esterni, consenso obbligatorio, etichette corrette e invalidazione.
**I test automatici NON possono convalidare il microfono e il sistema operativo del Pavilion né la risposta autentica dell'account GPT.**

Per il collaudo:
1. Non sostituire la build esistente. Chiudere tutte le istanze, fare un backup completo di `%LOCALAPPDATA%\Jarvis` ed estrarre il branch in una cartella differente.
2. Se Defender rileva il pacchetto, interrompere la prova; non creare esclusioni e non disattivare Defender. La precedente segnalazione `Trojan:Script/Wacatac.B!ml` è irrisolta.
3. Avviare `avvia_jarvis.bat`, senza abilitare automaticamente nuove modalità audio. Premere `⋯ → Autodiagnosi Jarvis`.
4. Verificare barra di avanzamento, rapporto sorgenti e sezione `Stato locale osservato`. In standby è normale leggere `voice_standby`; in ascolto continuo attivo la voce deve distinguere stream osservato/non confermato. Uno stato `ready` non certifica che ogni funzione sia stata collaudata.
5. Provare la richiesta vocale «Jarvis, fai un'autodiagnosi del tuo funzionamento e proponi eventuali fix». Controllare il testo trascritto nella console.
6. Prima dell'invio al GPT deve apparire una finestra di consenso. Scegliendo **No**, nulla deve partire; scegliendo **Sì**, GPT può commentare soltanto segnali anonimizzati. Se non connesso, il rapporto locale resta consultabile.
7. Provare Annulla, ripetizione e timeout; nessun rapporto precedente deve essere riutilizzato come nuovo.

## Stato integrazione
Ramo sperimentale separato. Nessun merge automatico, nessun costo/API aggiuntivi, nessun invio autonomo di dati. L'adozione richiede collaudo reale e decisione separata.
