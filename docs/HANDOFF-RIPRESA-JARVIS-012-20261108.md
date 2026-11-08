# Handoff di ripresa Jarvis — build 012
Data: 8 novembre 2026. Stato: pubblicazione completata; fermarsi in attesa del collaudo o di una nuova istruzione. Questo documento non autorizza altre modifiche o build.

## Repository e sorgenti
- Repository: MATRIXNEO23/jarvis.
- Ramo di lavoro: `fix/service-diagnostics-20261108`.
- Ultimo checkpoint prima di questo handoff: `402f1afcbe27ac66a7ca971ee77c582704bff9e5`.
- [PR58](https://github.com/MATRIXNEO23/jarvis/pull/58): draft, aperta, non integrata; base `fix/model-selection-session-20261108`.
- Main contiene il catalogo Download e sorgenti storici alla radice: non sostituire il ramo evoluto con main e non fare merge indiscriminati.
- Sorgente runtime verificato: `e29bc749196e97a10950d474548a92f48c181b5c`; checkout del pacchetto `5820b00623ec1632df86028c8bd9ac0341c5dc7d`.
- Prima di riprendere leggere AGENTS.md, questo handoff, STATO-ATTIVITA e la scheda tecnica pertinente. Verificare HEAD corrente: può avanzare rispetto a questi riferimenti.

## Pacchetto pubblicato
[Scarica Jarvis-012.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-012.zip).
Metadati: [Download/Jarvis-012.json](https://github.com/MATRIXNEO23/jarvis/blob/main/Download/Jarvis-012.json).
- 8.153.869 byte, 121 file di manifest.
- SHA256: `57c8fa161d36020207a46e2a6eee45f5fec8f0987546ae601e3abe1b6881c680`.
- Pubblicazione main: `f7a629b`; archivio pubblico scaricato e verificato.
- Registro: latest12/next13. 011 e versioni precedenti conservate.
- Publisher una tantum disattivato. Nessuna build automatica autorizzata da questo handoff.
- Estrarre in cartella nuova; preservare profilo e versione precedente.

## Funzioni/correzioni già consegnate
1. Scelta GPT/Gemma rispettata per voce, chat/PTT e Telegram. Consenso conversazionale GPT in RAM per la sessione; nessun passaggio silenzioso a Gemma per disconnessione GPT. Comandi locali prima dei modelli e cambio modello con sinonimi.
2. Gemma2 2B IT Q4_K_M: turni user/model separati; testo conversazionale accettato, azioni soggette a validazione.
3. M1: conteggio tramite tokenizer del motore sul prompt serializzato; budget fisico C-output-128; ultima coppia protetta o estratta localmente, storia/ricordi aggiunti entro600 token. Nessuna generazione aggiuntiva per riassumere.
4. M2: recupero recente dopo riavvio quando la RAM del contesto è vuota; massimo16 coppie per partizione e16384 caratteri per testo. Rispetto della memoria generale OFF, cancellazione e separazione progetti. Vecchi testi già troncati non ricostruibili.
5. Telegram: uscita da disconnessione terminale rilevata, evitando listener falsamente attivo; nessun replay/retry applicativo aggiunto.
6. 012: rapporto locale dei servizi con journal Telegram limitato a64 eventi RAM; comando voce/chat «Jarvis, diagnostica servizi». Pulsante in Impostazioni > Progetti e servizi > Apri diagnostica servizi. Aggiorna e Copia rapporto. Solo codici, conteggi e orari: niente nomi, ID, testi, credenziali o invii di prova. La vista non avvia modello, microfono o rete.
7. Corretto difetto della nuova diagnostica: una disconnessione dopo risposta vuota non viene più attribuita a una vecchia fase modello.

## Problema Telegram ancora aperto
Riscontro dell'utente sulla011: invio manuale funziona; messaggi da altro account/contatto spuntato non producono neppure «Ricevuto» in console.
La causa su quell'account NON è accertata né dichiarata risolta. La012 rende osservabile il punto di blocco: dipendenza, credenziali, connessione, autorizzazione, contatti, handler, aggiornamenti grezzi, filtri, acquisizione, modello, sintesi e invio.
Un handler registrato o un aggiornamento grezzo non certificano ricezione di un messaggio autorizzato. I codici sono osservazioni di fase, non spiegazioni di tutte le cause possibili. Non applicare altri fix soltanto su supposizioni.

## Prossimo passo
Sul PC dell'utente, avviare012, attivare le risposte automatiche già configurate, aprire la diagnostica e ricevere un NUOVO messaggio dall'altro account autorizzato. Premere Aggiorna, poi Copia rapporto e riportarlo nella chat.
Copiare prima di riavviare o sostituire il listener: il journal si azzera. Non chiedere API hash, sessioni o credenziali. Usare le evidenze per isolare la fase, poi test di riproduzione e correzione mirata.
L'utente ha chiesto espressamente di fermarsi dopo pubblicazione: non avviare ora nuovi interventi autonomi.

## Evidenze e limiti
- [Workflow012](https://github.com/MATRIXNEO23/jarvis/actions/runs/42457722089) SUCCESS:999 test su Windows/Python3.11 e3.12, e999 sullo ZIP estratto; avvio/chiusura UI, DLL, manifest e parità sorgenti verificati.
- [Diagnostica/Tk](https://github.com/MATRIXNEO23/jarvis/actions/runs/42457722164):12 test passati.
- [Listener Telegram](https://github.com/MATRIXNEO23/jarvis/actions/runs/42457722080):4 test passati.
- Review indipendente e recheck mirato completati; dettagli RED/GREEN e limiti in [DIAGNOSTICA-SERVIZI-ESITO-20261108.md](DIAGNOSTICA-SERVIZI-ESITO-20261108.md).
- Continuità M1/M2 e prova modello reale CI: [VERIFICA-CONTINUITA-GEMMA-20261108.md](VERIFICA-CONTINUITA-GEMMA-20261108.md).
- Prima correzione listener e limiti del sintomo: [TELEGRAM-RICEZIONE-20261108.md](TELEGRAM-RICEZIONE-20261108.md).
- Test funzionali soltanto Windows; rete/audio Telegram controllati, archivio temporaneo reale. Nessuna prova sull'account personale, sul microfono o sul Pavilion; nessuna garanzia di qualità/prestazioni universali. Non presentare i test CI come collaudo PC.

## Vincoli da conservare
Zero costi aggiuntivi; niente API a consumo. Riusare gestori esistenti senza comandi/esecutori duplicati. Preservare dati, impostazioni, profilo, versioni e controllo manuale del microfono. Nessuna modifica di avvio o selezione modello implicita. Nuove funzioni modulari secondo AGENTS, miglioramenti dei componenti esistenti nei loro responsabili. Help coerente. Errori/risultati documentati nel repo; test Windows prima della consegna. Nuove build solo su richiesta esplicita.
