# Jarvis Telegram — memoria breve e cronologia limitata

Stato: implementazione sperimentale nel ramo feature/telegram-bounded-history-50, **non integrata in main**. Nessuna modifica a WhatsApp.

## Regole approvate

- Jarvis si presenta una sola volta per contatto, usando un indicatore persistente che non dipende dai 50 messaggi.
- Contesto della risposta automatica: esattamente gli ultimi 4 eventi precedenti, ricevuti o inviati, dello stesso contatto. Nessuna ricerca storica e nessun riassunto GPT.
- Archivio SQLite: massimo 50 messaggi/eventi per contatto (ricevuti e inviati insieme). Il 51° elimina il più vecchio nella stessa transazione di inserimento.
- Il testo locale è conservato fino a 4096 caratteri per messaggio. Al GPT arrivano fino a 155 caratteri per ciascuno dei quattro eventi.
- La memoria Telegram non viene più duplicata nella tabella generale messages.
- Nessuna cancellazione di progetti, conversazioni di altri contatti, configurazioni, credenziali, autorizzazioni, promemoria da riferire o stato della presentazione.

## Impostazioni

Da Impostazioni → Telegram → Gestisci contatti Telegram, accanto a un contatto autorizzato:

- **Apri conversazione**: genera su richiesta un file di testo UTF-8 nella cartella locale telegram_conversations/contatto_ID.txt e lo apre. Il file contiene solo i messaggi registrati da Jarvis, ancora conservati; non recupera l'intera chat del servizio Telegram. Ogni nuova apertura aggiorna il file.
- **Cancella cronologia**: richiede conferma, elimina gli eventi di quel contatto e il file TXT esportato, lasciando invariati contatti e promemoria pendenti. Se il file è aperto e bloccato, la cancellazione si interrompe senza eliminare la cronologia.
- I messaggi successivi alla cancellazione sono nuovamente registrati.

## Migrazione e rollback

La prima apertura con dati Telegram preesistenti crea una copia SQLite consistente nella stessa cartella, chiamata jarvis_workspaces.pre-telegram-50.sqlite3. Il backup è fisso, non cresce con i nuovi messaggi.

Solo dopo il backup, in una transazione SQLite, il nuovo codice identifica i contatti già presentati, conserva i 50 eventi più recenti e rimuove le vecchie coppie duplicate dalla tabella generale. Il backup rimane disponibile per un ripristino controllato.

Quando si cancella la cronologia di un contatto, le sue informazioni vengono cancellate anche da tale backup, quando esiste, senza eliminare i dati di altri contatti o progetti.

Non eseguire il vecchio Jarvis sullo stesso database dopo la migrazione senza ripristinare coerentemente una copia del database. Non distribuire questa build prima di test su una copia dei dati locali e di una verifica end-to-end Windows 10.

## Collaudo richiesto

1. Test offline del limite di 50, memoria degli ultimi 4, isolamento dei contatti, backup, migrazione, riavvio, introduzione e pulizia selettiva.
2. Regressione degli invii vocali, controllo autorizzazioni e deduplicazione dei messaggi.
3. Collaudo su Windows 10 con database di prova.
4. Eventuale messaggio Telegram reale soltanto a un contatto consenziente, con autorizzazione esplicita dell'utente.

Nessun merge o aggiornamento automatico della versione esistente.
